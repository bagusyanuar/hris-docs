---
module: Region
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-08-01 19:15:00
depends_on: []
consumed_by: [employee@1.0.0, organization@planned]
---

# Product Requirements: Region Module (Master Data Wilayah)

> **Catatan grounding:** Modul ini belum terimplementasi di kode (`internal/region` belum ada). PRD ini adalah rancangan awal (Docs & Design First) sebelum implementasi backend dimulai.

---

## 1. Tujuan & Dampak (The "Why")

Data alamat (provinsi, kota/kabupaten, kecamatan, kelurahan/desa) dibutuhkan di banyak tempat — formulir data karyawan, alamat domisili sesuai KTP, lokasi cabang kantor, hingga pelaporan pajak. Kalau data ini diketik bebas oleh pengguna, rawan salah ketik dan tidak konsisten (nama wilayah yang sama bisa ditulis berbeda-beda). Modul Region menyediakan satu daftar referensi wilayah administratif Indonesia yang akurat, berjenjang (hierarkis), dan konsisten untuk dipakai seluruh sistem, sehingga integritas data lokasi terjamin dan proses pelaporan resmi (pajak, BPJS) bisa langsung memakai kode wilayah standar pemerintah.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Struktur data administratif berjenjang: **Provinsi → Kota/Kabupaten → Kecamatan → Kelurahan/Desa**.
- Penyediaan data wilayah lengkap se-Indonesia sejak awal *deployment*, bersumber dari data resmi pemerintah (BPS/Kemendagri).
- Dropdown berjenjang (*cascading dropdown*) di sisi Frontend — memilih provinsi akan menyaring pilihan kota, lalu kecamatan, lalu kelurahan.

**Out-of-Scope (TIDAK di modul ini):**
- **Halaman pengelolaan (CRUD) wilayah untuk Admin HR** — tidak dibutuhkan antarmuka tambah/ubah/hapus provinsi/kota satu per satu oleh HR. Perubahan data (misalnya akibat pemekaran wilayah oleh pemerintah pusat) di-*maintain* secara teknis lewat *Database Seeder* oleh tim IT.
- **Data wilayah internasional** — rilis pertama ini hanya mencakup struktur administratif Indonesia.

---

## 3. User Roles & Permissions

| Role | Read | Create / Update / Delete |
|------|------|---------------------------|
| Superadmin | ✅ | ❌ (tidak ada, lihat catatan) |
| Admin Perusahaan (HR) | ✅ (untuk dropdown alamat/cabang) | ❌ |
| Karyawan (ESS) | ✅ (untuk dropdown alamat pribadi) | ❌ |

- **Catatan tambahan:** Tidak ada role aplikasi mana pun (termasuk Superadmin) yang punya kewenangan tambah/ubah/hapus data wilayah lewat antarmuka — ini kebutuhan yang sangat jarang terjadi (hanya saat ada pemekaran wilayah resmi) dan ditangani lewat proses teknis (*Database Seeder*) oleh tim IT, bukan fitur aplikasi.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Pemilihan Wilayah Berjenjang (Cascading)**
- **Given** pengguna sedang mengisi formulir yang membutuhkan alamat lengkap.
- **When** pengguna memilih sebuah Provinsi.
- **Then** sistem menyaring dan menampilkan hanya Kota/Kabupaten yang berada di provinsi tersebut pada dropdown berikutnya, dan proses yang sama berlanjut hingga tingkat Kelurahan/Desa.

**Skenario 2: Data Tersedia Lengkap Sejak Awal**
- **Given** sistem baru selesai di-*deploy* untuk pertama kali.
- **When** pengguna membuka formulir yang membutuhkan data wilayah.
- **Then** seluruh data wilayah administratif Indonesia (Provinsi hingga Kelurahan/Desa) sudah tersedia tanpa perlu entri manual satu per satu oleh pengguna.

**Skenario 3: Pembaruan Akibat Pemekaran Wilayah**
- **Given** pemerintah pusat menerbitkan kebijakan pemekaran wilayah (kode administrasi suatu daerah berubah atau daerah baru terbentuk).
- **When** tim IT memperbarui data wilayah lewat proses teknis.
- **Then** data karyawan/cabang yang sudah mereferensikan wilayah lama tetap valid (karena mengacu ke identitas internal sistem, bukan kode pemerintah yang bisa berubah), sementara kode administrasi wilayah tersebut diperbarui mengikuti aturan terbaru.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Seluruh entitas wilayah (`Province`, `City`, `District`, `SubDistrict`) disatukan dalam satu domain `internal/region`.
- **Multi-Entity Scoping (MANDATORY):** Diklasifikasikan sebagai **Global Master** (tanpa `company_id`/`branch_id`) — **justifikasi eksplisit** sesuai `scoping-convention.md` §1: wilayah administratif Indonesia identik dan berlaku sama untuk seluruh PT dalam grup usaha, tidak ada variasi kebijakan per perusahaan.
- **Identitas Data:** Primary Key **wajib** memakai *Surrogate Key* (UUID), **bukan** Kode Wilayah Administrasi Pemerintahan (Kemendagri) — kode Kemendagri disimpan terpisah di kolom `administrative_code` (unik). Ini mencegah masalah integritas data saat terjadi pemekaran wilayah yang mengubah kode resmi (Skenario 3).
- **Persistensi / Database:** *Read-heavy* — hampir tidak ada operasi tulis di operasional harian aplikasi (hanya lewat Seeder teknis).
- **UI (Frontend):** Wajib pola dropdown berjenjang (*cascading select*) yang mengambil data anak berdasarkan `parent_id` dari pilihan sebelumnya, dioptimalkan untuk respons cepat.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- Tidak ada. Modul ini berdiri sendiri (*standalone reference data*), bersumber dari data resmi pemerintah (BPS/Kemendagri) lewat proses Seeder.

**Consumed by:**
- **Employee @1.0.0** — data alamat domisili/KTP karyawan mereferensikan wilayah dari modul ini.
- **Organization (rencana mendatang)** — lokasi cabang (Branch) akan mereferensikan wilayah dari modul ini; kolom `city` pada Branch saat ini masih teks bebas (PRD Organization §7.2).

**External integrations:** Tidak ada koneksi langsung — data bersumber dari BPS/Kemendagri namun dimasukkan lewat *Database Seeder* saat *deployment*, bukan pemanggilan API pihak ketiga secara *real-time*.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Province (Provinsi)
- **Aturan Bisnis:** `administrative_code` (2 digit, sesuai kode Kemendagri) unik. `id` (UUID) tetap jadi acuan relasi, bukan `administrative_code`.

| id | administrative_code | name |
| :-- | :-- | :-- |
| `prov-1` | `32` | Jawa Barat |

### 7.2. City (Kota/Kabupaten) — 1:N dari Province
- **Aturan Bisnis:** `administrative_code` (4 digit) unik, wajib punya `province_id` yang valid.

| id | province_id | administrative_code | name |
| :-- | :-- | :-- | :-- |
| `city-1` | `prov-1` | `3273` | Kota Bandung |

### 7.3. District (Kecamatan) — 1:N dari City
- **Aturan Bisnis:** `administrative_code` (6 digit) unik, wajib punya `city_id` yang valid.

| id | city_id | administrative_code | name |
| :-- | :-- | :-- | :-- |
| `dist-1` | `city-1` | `327305` | Sukajadi |

### 7.4. Sub-district (Kelurahan/Desa) — 1:N dari District
- **Aturan Bisnis:** `administrative_code` (10 digit) unik, wajib punya `district_id` yang valid. `postal_code` opsional.

| id | district_id | administrative_code | name | postal_code |
| :-- | :-- | :-- | :-- | :-- |
| `sub-1` | `dist-1` | `3273051001` | Sukagalih | `40163` |
