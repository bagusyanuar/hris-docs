# Decision Log (ADR) - Employment Status Module

## ADR-001: Master Data Company-Owned, Bukan Global Reference
- **Konteks:** Bank & Wilayah (`internal/bank`, `internal/region`) adalah Master Data global (tanpa `company_id`) karena datanya identik untuk semua PT. Employment Status secara nama terlihat mirip (kandidat dropdown, jarang berubah) — apakah ikut pola global yang sama?
- **Keputusan:** **Company-owned** (`company_id` NOT NULL). Setiap PT punya daftar status kepegawaian sendiri, bisa berbeda satu sama lain.
- **Alasan:** Bank/Wilayah datanya identik secara faktual di dunia nyata (BCA tetap BCA untuk semua PT). Jenis hubungan kerja **bukan** fakta universal — tiap PT dalam grup usaha bisa punya kebijakan berbeda (anak usaha jasa outsourcing butuh tipe "Outsource" yang tak relevan buat PT lain), dan batas durasi kontrak (`max_duration_months`) bisa jadi kebijakan internal PT (selama tidak melanggar batas maksimal hukum) bukan angka tunggal berlaku sama rata. Memilih "Global master" di sini akan memaksa satu daftar untuk seluruh grup usaha, bertentangan dengan aksioma multi-PT di `scoping-convention.md` §1 yang menyatakan "Global master" harus dijustifikasi eksplisit, bukan default.

## ADR-002: Endpoint di Bawah `/api/v1/employment-statuses`, Bukan `/api/v1/references/*`
- **Konteks:** `api-naming-convention.md` mengelompokkan endpoint dropdown murni ke `/api/v1/references/*` (publik/semua authenticated user, cache agresif). Employment Status secara fungsi memang jadi dropdown di form Employee — apakah masuk kategori ini?
- **Keputusan:** Ditempatkan sebagai **Business Domain Route** (`/api/v1/employment-statuses`), bukan Reference Route.
- **Alasan:** Kriteria Reference Route mensyaratkan data "rarely changes" dan **tidak dibatasi role tertentu**. Karena modul ini punya operasi tulis (create/update/deactivate) yang dibatasi ketat ke Admin Perusahaan/Superadmin per-PT (bukan semua authenticated user), dan datanya bisa berubah relatif sering di awal pemakaian tiap PT (nge-setup daftar sendiri), ini tidak memenuhi kriteria caching agresif lintas-PT yang jadi alasan utama kategori Reference Route. `GET` list tetap dipakai untuk dropdown, tapi scoping per-`company_id` membuatnya tidak bisa di-cache generik seperti Bank/Wilayah.

## ADR-003: Flag Boolean (`requires_contract_period`, dst.), Bukan Field Enum Bebas
- **Konteks:** Aturan bisnis seperti "wajib punya periode kontrak" atau "wajib tanggal akhir probation" bisa saja tetap dicek dengan membandingkan `code == "CONTRACT"` di kode Employee, tanpa nambah kolom flag baru.
- **Keputusan:** Aturan bisnis disimpan sebagai kolom boolean eksplisit (`requires_contract_period`, `requires_probation_end_date`, `has_leave_entitlement`, `has_severance_pay`) di tabel `employment_statuses`, bukan hardcode perbandingan `code` di kode Employee/Leave/Payroll.
- **Alasan:** Kalau logic tetap `if code == "CONTRACT"`, menambah status kepegawaian baru (mis. "Outsource" di ADR-001) tetap butuh ubah kode setiap kali (persis masalah yang mau dihilangkan modul ini). Dengan flag eksplisit, admin PT bisa mendefinisikan tipe baru dan langsung menentukan perilakunya lewat data, tanpa developer ikut campur.

## ADR-004: Validasi Batas Durasi Kontrak Ada di Employment Status, Bukan di Employee
- **Konteks:** `ValidateContractDurationUseCase` (jumlahkan durasi `EmployeeContract` vs `max_duration_months`) bisa diletakkan di domain Employee (pemilik `EmployeeContract`) atau di domain Employment Status (pemilik aturan batasnya).
- **Keputusan:** Diletakkan sebagai Application Service milik **Employment Status**, diekspos ke Employee lewat pemanggilan Service (bukan Employee query tabel `employment_statuses` langsung).
- **Alasan:** Selaras `coding-convention.md` §4 (cross-domain lewat Application Service) — kalau logic ini taruh di Employee, Employee harus tahu detail struktur `employment_statuses` (leaky abstraction). Dengan pola ini, kalau aturan batas berubah (mis. nambah pengecualian tertentu), cukup ubah di satu domain pemilik aturan, Employee tetap hanya memanggil use case tanpa tahu detail internalnya.
