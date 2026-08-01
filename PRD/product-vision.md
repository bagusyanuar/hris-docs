---
doc_type: Product Vision (Global PRD / North Star)
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-08-01 18:00:00
scope: platform-wide          # bukan PRD per-bounded-context; ini payung semua modul (Docs, Backend, Frontend)
---

# HRIS — Global PRD (Product Vision / North Star)

> **Catatan grounding:** Dokumen ini adalah migrasi + generalisasi dari `hris-backend/docs/PRD/product-vision.md` (v1.0.0). Versi asli berjudul "HRIS Backend" dan sebagian isinya (§4) mencampur prinsip platform-wide dengan prinsip teknis backend-spesifik. Versi ini memisahkan keduanya secara eksplisit, supaya dokumen ini benar jadi payung untuk **Docs, Backend, dan Frontend** sekaligus, bukan cuma backend.

Dokumen ini adalah **payung** di atas semua PRD per-modul. Fungsinya menetapkan *arah produk* (GOALS), *model deployment*, dan *aksioma lintas-platform* yang **tidak boleh dilanggar** oleh PRD modul manapun ataupun kode di ketiga repository (`hris-docs`, `hris-backend`, `hris-frontend`). Kalau ada konflik antara PRD modul dan dokumen ini, dokumen ini yang menang (atau dokumen ini yang direvisi lebih dulu secara sadar).

> Beda peran dokumen:
> - **Global PRD (ini)** = arah & aksioma seluruh platform (Docs + Backend + Frontend).
> - **PRD modul** (`organization.md`, `employee.md`, `employment-status.md`, …) = WHAT/WHY per bounded context.
> - **tech-spec / decision-log** (di `TRD/BE/` dan `TRD/FE/`) = HOW teknis per modul, per sisi (backend/frontend).

---

## 1. Visi Produk (North Star)

> **Satu platform HRIS untuk satu grup usaha (holding) yang menaungi beberapa PT, masing-masing dengan banyak cabang — dikelola satu owner, dari satu login, dengan visibilitas konsolidasi penuh atas seluruh grup.**

Sistem ini melayani **enterprise skala menengah–besar** dengan struktur kompleks (multi-PT, multi-cabang, multi-departemen) dan jumlah karyawan yang bertumbuh. Arsitektur DDD di backend dipilih supaya tiap domain bisa berkembang mandiri, bahkan diekstrak jadi service terpisah nanti; di frontend, struktur berbasis komponen Svelte 5 dipilih supaya tiap modul UI bisa dikembangkan selaras batas bounded-context yang sama.

---

## 2. Model Bisnis & Deployment (AKSIOMA — mengunci semua desain, semua sisi)

Keputusan paling fundamental yang menyetir seluruh arsitektur, berlaku sama untuk Backend maupun Frontend:

| Aspek | Keputusan | Konsekuensi |
|-------|-----------|-------------|
| **Model** | **Group / Holding, single-owner** | Satu instalasi = satu grup usaha milik satu owner. |
| **BUKAN** | **BUKAN multi-tenant SaaS** | Tidak dijual ke banyak klien tak-saling-kenal. Tidak ada lapis `Tenant`, tidak ada onboarding self-service, tidak ada billing per-tenant, tidak ada sub-domain per-tenant — **dan di sisi UI**, tidak ada halaman "pilih tenant"/billing plan, yang ada cukup *workspace switcher* Company/Branch di sidebar. |
| **Legal entity** | **Banyak `Company` (PT)** di bawah satu owner | Tiap PT punya NPWP/BPJS/payroll sendiri. Owner lihat konsolidasi lintas PT. |
| **Lokasi** | **Banyak `Branch` (cabang)** per Company | Operasional (absensi/shift/UMR) di-scope per cabang. |
| **Isolasi data** | **Shared DB + row-level scoping** (`company_id` / `branch_id`) | Cukup untuk group tunggal. TIDAK pakai schema-per-tenant / DB-per-tenant kecuali ada tuntutan regulasi nyata. |

> **Kalau suatu hari model berubah jadi SaaS** — itu perubahan MAJOR pada dokumen ini, wajib tambah lapis `Tenant` di atas `Company`, review ulang strategi isolasi data, dan review ulang seluruh alur UI yang berasumsi "satu grup usaha". Jangan diam-diam menyelundupkan asumsi SaaS ke modul manapun (backend maupun frontend).

---

## 3. Hierarki Struktural Global (Kanonik)

Semua modul — di ketiga repository — WAJIB mengacu ke hierarki ini. Company/Branch didefinisikan di [organization.md](organization.md); Department/Job Position di `workforce-structure.md` (saat ini masih di `hris-backend/docs/PRD/workforce-structure.md`, migrasi ke `hris-docs` menyusul); Employee di `employee.md` (idem); Employment Status per PT di [employment-status.md](employment-status.md).

```text
Group / Holding (implisit = 1 instalasi aplikasi, 1 owner)
  └── Company (PT / badan hukum)        ← company_id  · NPWP, BPJS, payroll, pajak   [Organization]
        └── Branch (cabang / lokasi)    ← branch_id   · absensi, shift, UMR, libur   [Organization]
              └── Department            ← struktur unit kerja (tree)                 [Workforce Structure]
                    └── Job Position    ← "kursi" (Department × Job Title)           [Workforce Structure]
                          └── Employee  ← menduduki posisi; wajib company_id + branch_id  [Employee]
                                └── Employment Status ← jenis hubungan kerja per-PT  [Employment Status]
```

**Dua dimensi scoping wajib** (jangan digabung jadi satu kolom):
- `company_id` → dimensi **legal** (payroll, pajak, kontrak). Non-nullable di semua entity operasional.
- `branch_id` → dimensi **lokasi** (operasional harian). Non-nullable di Employee & transaksi operasional.

---

## 4. Prinsip Arsitektur

### 4.1. Prinsip Lintas-Platform (Non-Negotiable — Docs, Backend, Frontend)
1. **Loose coupling di dokumen & kode** — modul merujuk field/section modul lain (+ versi), bukan copy-paste aturan. Konsep lintas-modul naik ke `PRD/_shared/glossary.md`.
2. **Concern lintas-modul = modul sendiri** — RBAC, audit trail, notifikasi TIDAK ditempel ke modul terdekat. Masing-masing PRD sendiri (berlaku untuk PRD, TRD/BE, dan TRD/FE-nya sekaligus).
3. **Dua dimensi scoping (`company_id`/`branch_id`) sejak baris pertama** — kolom non-nullable dari migrasi awal di backend, dan wajib direfleksikan di frontend sebagai *active scope* (`X-Company-Id`/`X-Branch-Id`, lihat `scoping-convention.md` §3.1) — bukan sekadar detail backend yang disembunyikan dari UI.
4. **Payroll/pajak selalu per-Company** — tidak ada agregasi lintas PT dalam satu slip/laporan pajak. Konsolidasi hanya di layer reporting Owner.
5. **Docs & Design First atau Prototyping-Driven** — tiap fitur lewat salah satu dari dua *workflow* resmi (lihat root `CLAUDE.md` §2A), tidak ada kode ditulis tanpa PRD/TRD yang menyertainya, baik ditulis duluan (top-down) maupun disusulkan dari hasil *slicing* UI (bottom-up).

### 4.2. Prinsip Spesifik Backend
1. **DDD domain-first** — tiap bounded context = satu folder utuh di `internal/`, siap diekstrak jadi service. Lihat `hris-backend/.agents/rules/architecture.md`.
2. **Cross-domain via Application Service** (sinkron, Wire DI) — bukan inject repository modul lain, bukan message broker (untuk sekarang). Lihat `coding-convention.md` §4.
3. **Bukan GORM `AutoMigrate` di produksi** — skema via SQL migration + DBML, `hris-docs/TRD/BE/<modul>/` sebagai sumber DDL.

> Prinsip spesifik Frontend (Svelte 5, Runes, konvensi komponen) diatur di `hris-frontend/.agents/AGENTS.md` — tidak diulang di sini, sesuai prinsip §4.1 poin 1 (loose coupling di dokumen).

---

## 5. Peta Modul & Roadmap

### 5.1. Modul Fondasi
| Modul | Peran | Status kode | PRD di `hris-docs` |
|-------|-------|-------------|---------------------|
| **Auth** | autentikasi & access control dasar | ada | [auth.md](auth.md) |
| **User** | akun pengguna sistem | ada | belum dimigrasi |
| **Organization** | legal & lokasi: Company (PT), Branch | ada | [organization.md](organization.md) |
| **Workforce Structure** | struktur internal: Department, Job Title, Job Position | ada | belum dimigrasi (`hris-backend/docs/PRD/workforce-structure.md`) |
| **Employee** | data & profil karyawan, sudah punya `company_id`/`branch_id` | ada | belum dimigrasi (`hris-backend/docs/PRD/employee.md`) |
| **Employment Status** | status kepegawaian sebagai master data per-PT | **Draft, belum ada kode** | [employment-status.md](employment-status.md) |

### 5.2. Concern Lintas-Modul (jadi modul/PRD sendiri)
| Modul | Peran | Kenapa dipisah |
|-------|-------|-----------------|
| **RBAC** | enforce scoping `company_id`/`branch_id` + role/permission | dikonsumsi SEMUA modul; fondasi access-control |
| **Audit Trail** (rencana mendatang) | jejak siapa-ubah-apa-kapan lintas modul | requirement enterprise |
| **Notification** (rencana mendatang) | email/push lintas modul | dikonsumsi banyak modul |

### 5.3. Modul HRIS Inti (arah pengembangan, belum PRD)
Attendance & Time Tracking · Leave/Time-off · **Payroll & Compensation** · Performance Management · Recruitment & Onboarding.

> Semua modul di §5.3 WAJIB lewat proses PRD/Tech-Spec penuh (Docs & Design First atau Prototyping-Driven, §4.1 poin 5) sebelum diimplementasi. Payroll & Attendance = tier **Kompleks** (kalkulasi berlapis/state machine).

### 5.4. Master Data Pendukung
Bank ([bank.md](bank.md)) dan Wilayah ([region.md](region.md)) — Global Master, dikonsumsi lintas modul (Employee, Organization, Payroll rencana mendatang) tanpa scope `company_id`.

---

## 6. Non-Goals (Batas Tegas — mencegah scope creep, semua sisi)

- ❌ **BUKAN SaaS multi-tenant.** Tidak melayani banyak owner/klien tak-saling-kenal. Tidak ada lapis Tenant, billing, self-service onboarding — di kode maupun di UI.
- ❌ **Bukan** konsolidasi payroll lintas-PT dalam satu perhitungan pajak. Tiap PT tutup buku sendiri.
- ❌ **Bukan** schema-per-tenant / DB-per-tenant (sampai ada tuntutan regulasi nyata).
- ❌ **Bukan** message broker / event-driven antar-modul untuk sekarang (sinkron via Application Service).
- ❌ **Bukan** GORM `AutoMigrate` di produksi — skema via SQL migration + DBML.

---

## 7. Metrik Sukses (indikatif — dipertajam per modul)

- Owner bisa lihat **konsolidasi lintas-PT** (jumlah karyawan, headcount) dari satu dashboard.
- Data satu cabang/PT **tidak bocor** ke cabang/PT lain (enforced RBAC) — 0 insiden kebocoran lintas-scope.
- Tambah PT/cabang/jenis status kepegawaian baru **tanpa deploy ulang** aplikasi — cukup master data.
- Tiap PT bisa jalankan payroll/pajak **independen** tanpa saling ganggu.

---

## 8. Referensi

- Index PRD: [README.md](README.md)
- Glossary lintas-modul: `PRD/_shared/glossary.md` (belum dibuat)
- Rules arsitektur & konvensi Backend: `hris-backend/.agents/rules/`
- Rules arsitektur & konvensi Frontend: `hris-frontend/.agents/AGENTS.md`
- Aturan koordinasi lintas-workspace: root `CLAUDE.md`
- PRD fondasi multi-entity: [organization.md](organization.md)
