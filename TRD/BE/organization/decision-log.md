# Decision Log (ADR) - Organization Module

## ADR-001: Company & Branch sebagai Dua Kolom Scope Terpisah (`company_id` + `branch_id`)
- **Konteks:** Kewajiban legal (pajak, BPJS) melekat ke badan hukum (PT), sementara jam kerja/shift/UMR melekat ke lokasi fisik (cabang). Kalau digabung jadi satu dimensi (mis. hanya `branch_id`, company diturunkan dari branch), query lintas-cabang dalam satu PT (mis. laporan payroll konsolidasi per PT) butuh JOIN tambahan di setiap tempat, dan entity yang company-scoped-tapi-bukan-lokasi-spesifik (mis. Department) jadi terpaksa nempel ke satu cabang secara salah kaprah.
- **Keputusan:** Dua kolom scope independen: `company_id` (wajib di semua entity operasional) + `branch_id` (wajib hanya untuk entity yang benar-benar lokasi-spesifik). Lihat klasifikasi kelas di `scoping-convention.md` §1.
- **Alasan:** Entity company-owned-tapi-bukan-lokasi-spesifik (Department, Job Title) tidak perlu `branch_id` sama sekali — hemat kolom, hindari ambiguitas "cabang mana" untuk data yang bisnisnya memang per-PT.

## ADR-002: Row-Level Scoping (Shared DB + Kolom), Bukan Schema/DB-per-Tenant
- **Konteks:** Multi-PT bisa diisolasi dengan tiga pendekatan: (a) DB terpisah per PT, (b) schema Postgres terpisah per PT, (c) shared table + kolom `company_id`. Opsi (a)/(b) memberi isolasi lebih kuat tapi migration/maintenance overhead naik linear dengan jumlah PT, dan query konsolidasi lintas-PT (kebutuhan Owner) jadi butuh cross-database query yang jauh lebih mahal.
- **Keputusan:** Shared database + kolom `company_id`/`branch_id` row-level. Isolasi ditegakkan di query boundary (aplikasi), bukan di level infrastruktur DB.
- **Alasan:** Enforcement isolasi jadi tanggung jawab kode (RBAC middleware + `scope.FromContext` di setiap repository read) — bukan otomatis dijamin DB. Kalau suatu saat ada tuntutan regulasi yang butuh isolasi fisik penuh (jarang), perlu migrasi arsitektur terpisah — bukan default sekarang.

## ADR-003: Branch adalah Aggregate Root Sendiri, Bukan Child Entity Company
- **Konteks:** Kalau Branch dimodelkan sebagai child collection yang selalu dimuat bersama Company (mis. `Company.Branches []Branch`), setiap load Company jadi query mahal + risiko N+1 ketika Company punya puluhan cabang. Operasi Branch (create/update/delete satu cabang) juga tidak seharusnya butuh memuat ulang seluruh Company.
- **Keputusan:** Branch = aggregate root independen dengan `CompanyID` sebagai foreign key referensi (bukan embedded slice). `BranchRepository` terpisah dari `CompanyRepository`.
- **Alasan:** Trade-off: konsistensi antar aggregate (mis. "Company tidak boleh dihapus kalau masih punya Branch aktif") jadi tanggung jawab Application Service, bukan otomatis dijamin satu aggregate boundary. Untuk scope 2.0.0 aturan itu belum diimplementasikan (PRD Skenario 5) — ditandai sebagai gap eksplisit, bukan silent decision.

## ADR-004: `is_main` Branch — Demote Otomatis, Bukan Tolak (Reject)
- **Konteks:** PRD Skenario 4 sengaja menyerahkan pilihan "pindahkan status vs tolak" ke tech-spec. Dari sisi UX, "tolak dengan error" berarti Admin harus manual: (1) cabut status main branch lama, (2) baru set main branch baru — dua request terpisah dengan window race (sempat tidak ada main branch sama sekali, atau race dua request paralel bikin dua main branch sekaligus).
- **Keputusan:** Demote otomatis. Saat create/update Branch dengan `is_main=true`, dalam satu `TxManager.Do`: (1) `DemoteMainBranch(companyID)` — set `is_main=false` untuk main branch lama di company yang sama, (2) simpan branch baru/ubah dengan `is_main=true`. Partial unique index `idx_branches_company_main` di DB tetap jadi jaring pengaman terakhir kalau ada bug di application layer yang lewatkan step demote.
- **Alasan:** Admin tidak perlu dua langkah manual. Trade-off: aksi "pindahkan kantor pusat" jadi efek samping implisit dari update biasa (tidak ada endpoint terpisah `PATCH /branches/{id}/set-main`) — didokumentasikan di sini supaya FE tahu efek sampingnya saat toggle `is_main`.

## ADR-005: `npwp` & `bpjs_no` Nullable (Bukan NOT NULL) di Scope Awal
- **Konteks:** PRD §7.1 mendeskripsikan `npwp`/`bpjs_no` sebagai bagian data legal Company, tapi belum ada modul konsumen (Payroll) yang benar-benar butuh nilainya sekarang — mewajibkan `NOT NULL` di awal berarti tim harus punya data NPWP/BPJS valid untuk *setiap* PT sebelum bisa input Company sama sekali, padahal onboarding PT baru sering data itu menyusul belakangan.
- **Keputusan:** Kolom nullable, unique constraint tetap ada (partial index `WHERE npwp IS NOT NULL`, aman untuk multi-NULL) — bukan penghapusan field.
- **Alasan:** Validasi "npwp wajib diisi" (kalau suatu saat dibutuhkan Payroll) jadi tanggung jawab modul consumer atau validasi tambahan di masa depan, bukan constraint DB. `ErrCompanyNPWPDuplicate` (PRD Skenario 1) tetap berlaku HANYA ketika `npwp` diisi (dua Company boleh sama-sama `npwp = NULL`).

## ADR-006: Nested `branches` di `GET /companies` — Batch Query Manual, Bukan GORM `Preload`
- **Konteks:** FE butuh menampilkan Company beserta daftar Branch-nya sekaligus di satu halaman (list view), tanpa round-trip kedua per row. ADR-003 sudah menetapkan Branch sebagai aggregate root terpisah justru untuk menghindari pola "selalu ikut ke-load bareng Company" yang berisiko N+1 — kebutuhan UI ini sekilas kontradiksi ADR-003, jadi perlu didokumentasikan eksplisit kenapa aggregate boundary TIDAK diubah.
- **Keputusan:**
  1. Nested `branches` di respons `GET /companies` adalah **komposisi read-model di Application Layer**, bukan perubahan aggregate — `BranchRepository` tetap terpisah dari `CompanyRepository`, tidak ada foreign-key embed di domain entity `Company`.
  2. Diambil lewat method `BranchRepository.FindAllByCompanyIDs(ctx, companyIDs []string)` — satu query `WHERE company_id IN (...)` atas seluruh company di halaman itu (bukan loop per company/N+1), lalu di-group manual per `company_id` di Application Layer.
  3. **Bukan** GORM `Preload` meski secara mekanisme sama-sama batch query di balik layar — alasannya bukan performa (sama), tapi kontrol: `Preload` butuh association field (`Company.Branches []BranchModel`) nempel di GORM model, yang bikin adapter model "tahu" relasi lintas aggregate (menyimpang dari ADR-003), dan sulit disisipi filter `scope.FromContext` custom nanti saat RBAC landing dibanding query manual yang eksplisit di adapter.
  4. Saat `search` cocok dengan nama branch (bukan `legal_name`), `branches` yang di-embed tetap FULL LIST milik company itu — TIDAK difilter cuma yang cocok. `search` cuma menentukan company mana yang lolos filter, bukan menyaring isi nested-nya.
- **Alasan:** `GET /companies` selalu menjalankan satu query tambahan (branch batch) per request list, walau FE kadang tidak butuh data branch-nya (trade-off diterima, volume data kecil). Kalau nanti butuh skip branch, pertimbangkan parameter opsional (`?include=branches`) saat itu — belum dibutuhkan sekarang (YAGNI).
