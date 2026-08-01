---
module: RBAC
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [auth@1.0.1, user@1.0.1, organization@1.0.1]
consumed_by: [employment-status@1.0.1, employee@1.0.1, workforce-structure@1.0.1, leave-type@1.0.1, work-shift@1.0.1, payroll@planned, attendance@planned, leave@planned]
---

# Product Requirements: RBAC Module (Role-Based Access Control)

> **Catatan grounding:** Modul ini **belum ada kode sama sekali** (`internal/rbac/` belum dibuat). PRD ini rancangan awal (Docs & Design First) — sebelumnya cuma disebut sebagai baris di [product-vision.md](product-vision.md) §5.2 dan diasumsikan lewat kontrak `scope.FromContext` di beberapa PRD lain ([organization.md](organization.md) §5, [employment-status.md](employment-status.md) §5). Dokumen ini yang pertama kali mendefinisikan modul ini secara utuh.

---

## 1. Tujuan & Dampak (The "Why")

Setiap modul operasional (Organization, Employee, Employment Status, dan seterusnya) butuh jawaban atas dua pertanyaan yang sama persis di titik yang sama: **"Siapa user ini, boleh ngapain aja, dan datanya PT/cabang mana aja yang boleh dia lihat/ubah?"** Tanpa modul terpusat, tiap modul akan menulis ulang logika ini sendiri-sendiri — rawan inkonsisten (satu modul lupa filter PT, modul lain aturannya beda) dan sulit diaudit karena aturan akses tersebar di banyak tempat.

Modul RBAC menyediakan jawaban tunggal untuk seluruh sistem: siapa boleh melakukan aksi apa (**role & permission**), dan data PT/cabang mana yang boleh diakses (**cakupan**). Modul lain tinggal *konsumsi* keputusan ini, tidak perlu menghitung ulang. Ini juga yang menggantikan `role` yang saat ini masih *hardcoded* di modul Auth (lihat [auth.md](auth.md) §3).

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pengelolaan daftar **Role** (peran) — mis. Owner/Group Admin, Admin Perusahaan, Admin Cabang, Karyawan (ESS) — berlaku seluruh grup usaha (lihat §5 klasifikasi scoping).
- Pengelolaan daftar **Permission** (izin aksi per modul) — Lihat/Baca, Buat, Ubah, Nonaktifkan/Hapus, dan aksi khusus lain (mis. Setujui) per modul operasional.
- Penetapan kombinasi Permission ke tiap Role (matriks izin).
- Penetapan **Role + cakupan PT/cabang** ke tiap akun pengguna — satu akun bisa punya lebih dari satu penetapan (mis. jadi Admin Cabang di PT A, sekaligus cuma boleh Lihat di PT B).
- Penyediaan kontrak baca terpusat ("apa saja PT/cabang yang boleh diakses user ini, dan izin apa saja yang dia punya") untuk dikonsumsi seluruh modul operasional lain.
- Validasi pemilihan PT/cabang aktif oleh user (*workspace switcher*, lihat `product-vision.md` §2) — wajib berada dalam cakupan yang sudah ditetapkan untuknya, ditolak kalau di luar itu.

**Out-of-Scope (TIDAK Dikerjakan di modul ini, untuk saat ini):**
- **Izin di level data spesifik (field-level / row-level permission custom)** — modul ini bekerja di level "boleh akses modul X aksi Y", bukan "boleh lihat kolom gaji tapi bukan kolom bonus".
- **Delegasi/approval hierarki berjenjang** (mis. atasan menyetujui izin bawahannya secara berantai) — itu tanggung jawab modul operasional masing-masing (mis. Leave), RBAC cuma menjawab "boleh approve atau tidak", bukan alur approval-nya.
- **Audit trail perubahan role/permission** — jejak siapa-ubah-apa jadi tanggung jawab modul Audit Trail (rencana mendatang, lihat `product-vision.md` §5.2), bukan bagian inti RBAC.
- **Single Sign-On / identitas eksternal** — tetap tanggung jawab Auth, RBAC cuma bicara otorisasi setelah identitas terverifikasi.
- **Role kustom per-PT** (PT A dan PT B punya definisi Role yang beda-beda) — daftar Role bersifat global/seragam seluruh grup usaha di rilis ini (lihat §5).

---

## 3. User Roles & Permissions

| Role | Kelola Role & Permission | Kelola Penetapan Role ke User | Lihat Penetapan Miliknya Sendiri |
|------|---------------------------|-------------------------------|-----------------------------------|
| Owner / Superadmin | ✅ | ✅ (semua PT) | ✅ |
| Admin Perusahaan (Company Admin) | ❌ | ✅ (hanya untuk user di PT-nya sendiri) | ✅ |
| Role lain (Branch Admin, ESS, dst.) | ❌ | ❌ | ✅ (lihat izin miliknya sendiri saja) |

- **Catatan tambahan:** Modul ini sendiri adalah modul akses-tertinggi — kesalahan konfigurasi di sini berdampak ke semua modul lain, jadi pengelolaan Role/Permission dasar dikunci hanya untuk Owner/Superadmin. Admin Perusahaan boleh menetapkan Role yang **sudah ada** ke user di PT-nya (mis. menaikkan seorang Admin Cabang), tapi tidak boleh membuat Role atau Permission baru.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Superadmin Menetapkan Role & Cakupan ke Akun**
- **Given** Superadmin ingin memberi seorang user akses ke sistem.
- **When** Superadmin memilih satu Role untuk user tersebut, dan (opsional) membatasi cakupannya ke satu PT tertentu, atau satu PT + satu cabang tertentu.
- **Then** sistem menyimpan penetapan tersebut — sejak saat itu user hanya bisa melakukan aksi sesuai izin Role-nya, pada data PT/cabang sesuai cakupan yang ditetapkan.

**Skenario 2: Penetapan Tanpa Batasan PT = Akses Seluruh Grup**
- **Given** Superadmin menetapkan Role ke user **tanpa** memilih PT tertentu (dikosongkan, bukan memilih "semua").
- **When** user tersebut menggunakan sistem.
- **Then** user tersebut punya akses ke seluruh PT dan cabang dalam grup usaha, selama Role-nya mengizinkan aksi yang dilakukan.

**Skenario 3: Memilih PT/Cabang di Luar Cakupan Ditolak**
- **Given** seorang user hanya ditetapkan cakupan ke PT A.
- **When** user tersebut mencoba beralih bekerja di konteks PT B lewat pemilihan PT/cabang aktif di aplikasi.
- **Then** sistem menolak permintaan tersebut dan menampilkan pesan bahwa user tidak punya akses ke PT yang dipilih.

**Skenario 4: Aksi Ditolak Kalau Role Tidak Punya Izinnya**
- **Given** Role milik seorang user hanya punya izin "Lihat" pada suatu modul, tanpa izin "Ubah".
- **When** user tersebut mencoba mengubah data di modul tersebut.
- **Then** sistem menolak aksi tersebut — meskipun user berada dalam cakupan PT/cabang yang benar, izin aksinya yang tidak mencukupi.

**Skenario 5: Pencabutan Role Menghentikan Akses**
- **Given** seorang user sebelumnya punya penetapan Role tertentu.
- **When** Superadmin/Admin Perusahaan mencabut penetapan tersebut.
- **Then** user kehilangan seluruh izin yang datang dari penetapan itu pada penggunaan sistem berikutnya.
- *Catatan implementasi:* modul ini seluruhnya rancangan baru, belum ada kode — termasuk keputusan apakah pencabutan berlaku instan pada sesi yang sedang aktif atau baru berlaku setelah user membuka sesi baru. Ini gap desain yang wajib diputuskan saat modul mulai diimplementasikan, bukan diasumsikan diam-diam salah satu caranya.

**Skenario 6: Cakupan Cabang Wajib Konsisten dengan PT-nya**
- **Given** Superadmin menetapkan cakupan berupa satu cabang spesifik ke seorang user.
- **When** cabang yang dipilih ternyata bukan milik PT yang juga ditetapkan (atau PT-nya belum diisi sama sekali).
- **Then** sistem menolak penetapan tersebut dan meminta PT diisi/dicocokkan dulu sebelum cabang bisa dipilih (selaras aturan kecocokan `company_id`/`branch_id` yang sudah berlaku di modul lain, mis. [organization.md](organization.md) §3 Skenario 3).

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Modul baru `internal/rbac/` (rancangan — belum ada kode). Bertindak sebagai lapisan yang dipanggil lewat middleware, dijalankan setelah identitas user diverifikasi oleh Auth (`AuthProtected`) dan sebelum request menyentuh domain bisnis modul lain.
- **Multi-Entity Scoping (MANDATORY):**
  - **Role** dan **Permission** = **Global Master** — satu daftar berlaku identik seluruh grup usaha (tanpa `company_id`), karena definisi peran/izin bukan kebijakan yang berbeda per-PT di rilis ini (lihat §2 Out-of-Scope — role kustom per-PT ditunda).
  - **Penetapan Role ke User** (§7.4) = kelas tersendiri, **bukan** "Company-owned" biasa — kolom `company_id`/`branch_id`-nya **NULLABLE**, karena baris ini justru yang **mendefinisikan** cakupan akses seorang user, bukan yang di-filter oleh cakupan siapa pun. `company_id` kosong berarti akses seluruh PT (Skenario 2); `branch_id` kosong berarti akses seluruh cabang dalam `company_id` terkait.
- **Enforcement Terpusat:** RBAC **wajib** mengisi kontrak `scope.FromContext(ctx)` yang sudah didefinisikan di `scoping-convention.md` §3 — modul lain membaca dari situ, bukan query tabel RBAC secara langsung (selaras prinsip cross-domain via Application Service, bukan akses repository modul lain).
- **Validasi PT/Cabang Aktif:** Saat user memilih PT/cabang aktif di aplikasi (dikirim lewat `X-Company-Id`/`X-Branch-Id`, lihat `scoping-convention.md` §3.1), RBAC **wajib** memvalidasi nilai tersebut adalah subset dari cakupan yang sudah ditetapkan untuk user itu (Skenario 3) — tidak pernah dipercaya mentah dari sisi client.
- **UI (Frontend):** Tiga permukaan berbeda — (1) halaman kelola Role & matriks Permission (checklist modul × aksi), (2) halaman penetapan Role+cakupan per user, (3) *workspace switcher* di sidebar yang cuma menampilkan pilihan PT/cabang sesuai cakupan user yang sedang login (bukan seluruh daftar PT/cabang yang ada di sistem).

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Auth @1.0.0** — RBAC berjalan setelah identitas user diverifikasi oleh Auth; mengasumsikan identitas (`user_id`) yang sudah tervalidasi dari lapisan Auth, tidak melakukan verifikasi kredensial sendiri (lihat [auth.md](auth.md) §6 "Semua Modul Terproteksi").
- **User @1.0.0** — penetapan Role mengikat ke identitas akun dari modul ini (lihat [user.md](user.md) §7.1).
- **Organization @1.0.0** — dimensi `company_id`/`branch_id` yang jadi isi cakupan penetapan Role berasal dari modul ini (lihat [organization.md](organization.md) §7).

**Consumed by:**
- **Employment Status @1.0.0, Workforce Structure @1.0.0, Leave Type @1.0.0, Work Shift @1.0.0** — PRD masing-masing sudah menyatakan eksplisit filter scope dienforce lewat `scope.FromContext` yang disediakan modul ini (lihat §5 tiap PRD terkait).
- **Employee @1.0.0** — PRD-nya (legacy, `hris-backend/docs/PRD/employee.md`) sudah menyatakan pembatasan akses HR Manager lewat `scope.FromContext(ctx)` (§ Multi-Entity Scoping).
- **Payroll, Attendance, Leave (rencana mendatang)** — belum ada PRD sama sekali; begitu digarap, otomatis ikut pola scope yang sama seperti modul operasional lain.

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Role
- **Aturan Bisnis:** `code` wajib unik (mis. `SUPERADMIN`, `COMPANY_ADMIN`, `BRANCH_ADMIN`, `EMPLOYEE_ESS`). Global — satu daftar berlaku seluruh grup usaha (lihat §5). `is_system_default=true` menandai Role bawaan yang tidak boleh dihapus (mis. `SUPERADMIN`), mencegah sistem kehilangan akses admin sama sekali.

| id | code | name | is_system_default |
| :-- | :-- | :-- | :-- |
| `role-1` | SUPERADMIN | Owner / Group Admin | `true` |
| `role-2` | COMPANY_ADMIN | Admin Perusahaan | `true` |
| `role-3` | BRANCH_ADMIN | Admin Cabang | `true` |
| `role-4` | EMPLOYEE_ESS | Karyawan (ESS) | `true` |

### 7.2. Permission
- **Aturan Bisnis:** Satu baris = satu kombinasi modul + aksi yang bisa diberikan ke Role (mis. `organization` + `read`). Daftar ini bertambah mengikuti modul yang tersedia di sistem — bukan diisi manual satu-satu oleh Admin, tapi terdaftar otomatis tiap kali modul baru dibangun.

| id | module | action | description |
| :-- | :-- | :-- | :-- |
| `perm-1` | organization | read | Melihat data Company/Branch |
| `perm-2` | organization | create | Mendaftarkan Company/Branch baru |
| `perm-3` | employment-status | update | Mengubah status kepegawaian |

### 7.3. Role Permission — N:N antara Role dan Permission
- **Aturan Bisnis:** Satu Role bisa punya banyak Permission, satu Permission bisa dipakai banyak Role. Kombinasi `role_id`+`permission_id` wajib unik (tidak boleh dobel).

| role_id | permission_id |
| :-- | :-- |
| `role-2` | `perm-1` |
| `role-2` | `perm-2` |

### 7.4. Penetapan Role ke User — 1:N dari User
- **Aturan Bisnis:** `company_id` **nullable** (kosong = akses seluruh PT, Skenario 2), `branch_id` **nullable** (kosong = akses seluruh cabang dalam `company_id` terkait). `branch_id` yang diisi wajib milik `company_id` yang sama pada baris tersebut (Skenario 6) *(Pesan error: "Cabang yang dipilih bukan milik perusahaan yang ditetapkan")*. Satu user boleh punya lebih dari satu baris (Role/cakupan berbeda-beda per PT).

| id | user_id | role_id | company_id | branch_id |
| :-- | :-- | :-- | :-- | :-- |
| `grant-1` | `usr-1` | `role-1` | `null` | `null` |
| `grant-2` | `usr-2` | `role-2` | `co-1` | `null` |
| `grant-3` | `usr-3` | `role-3` | `co-1` | `br-2` |
