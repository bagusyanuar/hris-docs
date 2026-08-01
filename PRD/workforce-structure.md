---
module: Workforce Structure
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [organization@1.0.1, rbac@1.0.1]
consumed_by: [employee@1.0.0]
---

# Product Requirements: Workforce Structure Module

> **Catatan grounding:** Modul ini sudah terimplementasi penuh di backend (`internal/workforce/` — lengkap domain, application, adapter, transport). Dokumen ini migrasi dari `hris-backend/docs/PRD/workforce-structure.md` (v1.2.0, berstatus Approved di sana), sekaligus regrounding total ke kode nyata — sebagian besar gap yang tercatat di dokumen legacy (Department belum punya `company_id`, kode belum dipindah dari `internal/domain/organization/`) **sudah ditutup**, jadi statusnya di sini dikembalikan ke Draft (bukan warisan Approved) sampai format hris-docs ini direview ulang.

Modul **Workforce Structure** mengatur bagan organisasi internal sebuah perusahaan: unit kerja (**Department**), pangkat/grade (**Job Title**), dan jabatan aktual (**Job Position**) beserta jalur pelaporan & kuota jumlah pegawai. Ini kerangka "kursi" yang nanti diduduki karyawan — dipisah tegas dari modul Organization yang cuma mengurus legal/lokasi (Company/Branch, lihat [organization.md](organization.md)).

---

## 1. Tujuan & Dampak (The "Why")

Menyediakan kerangka organisasi berbasis **jabatan** (bukan berbasis **orang**) yang stabil: jalur pelaporan tidak rusak saat ada pergantian pegawai, jumlah kuota per jabatan terkontrol, dan standar gaji/grade konsisten lintas departemen. Tanpa ini, penempatan karyawan jadi asal-asalan dan bagan organisasi tidak bisa diaudit.

Kenapa berbasis jabatan, bukan berbasis orang: struktur & "kursi" dibentuk dulu (Department → Job Title → Job Position), baru karyawan menempatinya. Konsekuensinya:
- **Struktur independen dari orangnya** — manajer resign, jalur pelaporan bawahannya tidak ikut rusak (karena lapor ke *jabatan*, bukan ke *orang tertentu*).
- **Kuota/anggaran jumlah pegawai terkelola** — bisa membatasi berapa orang boleh menempati satu jabatan.
- **Standarisasi gaji (grade)** — Job Title terpisah dari Department menjamin keadilan gaji lintas departemen untuk jabatan setara.
- Trade-off yang disadari: setup awal lebih berat (harus bentuk Department → Job Title → gabungkan jadi Job Position dulu, baru karyawan bisa ditempatkan) — kurang cocok untuk organisasi sangat kecil yang satu orang merangkap banyak peran, tapi sesuai target enterprise skala menengah-besar (lihat `product-vision.md` §1).

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pengelolaan **Department** (unit kerja/divisi) dengan hierarki bertingkat (Department bisa punya Department induk).
- Pengelolaan **Job Title** (master pangkat/grade) — independen dari Department, tapi tetap milik satu PT.
- Pengelolaan **Job Position** (jabatan aktual) — kombinasi satu Department + satu Job Title, punya penanda "lapor ke jabatan mana" dan kuota jumlah pegawai.
- Penyajian struktur Department dan Job Position secara utuh sekaligus (bukan per halaman) untuk kebutuhan tampilan bagan organisasi dan tabel bertingkat (*nested*).

**Out-of-Scope (TIDAK di modul ini):**
- **Penempatan karyawan ke Job Position** (siapa menduduki jabatan apa) — tanggung jawab modul **Employee**. Modul ini hanya menyediakan "kursi"-nya, bukan siapa yang duduk.
- **Company/Branch** (legal/lokasi) — tanggung jawab modul **Organization**.
- **Perhitungan gaji** dari grade Job Title — tanggung jawab modul **Payroll** (rencana mendatang).
- **Penegakan batas kuota saat karyawan ditempatkan** (menolak penempatan kalau kuota penuh) — keputusan kuotanya ada di sini, tapi *penegakannya* saat assign jadi tanggung jawab modul Employee/RBAC.
- **Struktur berbeda per cabang** — Department/Job Title/Job Position berlaku untuk seluruh PT (lihat §5), bukan per cabang.

---

## 3. User Roles & Permissions

| Role | Baca | Tulis |
|------|------|-------|
| Owner / Admin Perusahaan | ✅ struktur PT-nya (Owner: semua PT) | ✅ |
| HR Manager | ✅ | ✅ (dalam PT-nya sendiri) |
| Karyawan (ESS) | ✅ (lihat bagan organisasi) | ❌ |

- **Catatan tambahan:** Pembatasan akses berdasarkan PT (`company_id`) adalah tanggung jawab modul **RBAC** — modul ini menyediakan kolom kepemilikan datanya (lihat §5), penegakan siapa-boleh-lihat-apa dilakukan RBAC.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Hierarki Department Valid**
- **Given** Department baru menunjuk Department induk yang berada di PT yang sama.
- **When** Department disimpan.
- **Then** sistem menyimpannya sebagai anak dari Department induk tersebut. Kalau tidak menunjuk induk sama sekali, Department tersebut jadi akar (root) bagan organisasi PT itu.

**Skenario 2: Department Wajib Milik PT yang Valid**
- **Given** pembuatan Department baru merujuk `company_id` yang tidak ditemukan/tidak valid.
- **When** Department disimpan.
- **Then** sistem menolak — Department tidak boleh berdiri tanpa PT induk yang jelas (selaras [organization.md](organization.md) §4).

**Skenario 3: Kode Department Unik dalam Satu PT**
- **Given** sebuah PT sudah memiliki Department dengan kode tertentu.
- **When** ada percobaan membuat/mengubah Department lain di PT yang sama jadi kode yang sama persis.
- **Then** sistem menolak dan menampilkan pesan kode sudah dipakai. Kode yang sama tetap boleh dipakai di PT berbeda.

**Skenario 4: Department Induk Wajib Satu PT dengan Anaknya**
- **Given** sebuah Department akan diarahkan menjadi anak dari Department lain.
- **When** Department induk yang dipilih ternyata milik PT berbeda.
- **Then** sistem menolak penetapan tersebut.

**Skenario 5: Job Title Milik Satu PT, Kode Unik dalam PT Itu**
- **Given** sebuah PT sudah memiliki Job Title dengan kode tertentu.
- **When** ada percobaan membuat/mengubah Job Title lain di PT yang sama jadi kode yang sama persis.
- **Then** sistem menolak dan menampilkan pesan kode sudah dipakai. Job Title milik satu PT saja, tidak dibagi lintas PT (tiap PT punya daftar grade sendiri).

**Skenario 6: Job Position Wajib Department & Job Title dari PT yang Sama**
- **Given** pembuatan Job Position merujuk satu Department dan satu Job Title.
- **When** Department dan Job Title yang dirujuk ternyata milik PT yang berbeda satu sama lain.
- **Then** sistem menolak — satu Job Position tidak boleh menggabungkan Department dan Job Title dari dua PT berbeda.

**Skenario 7: Jalur Pelaporan Tidak Lintas PT**
- **Given** sebuah Job Position diarahkan untuk lapor ke Job Position lain (atasan).
- **When** Job Position atasan yang dipilih ternyata milik PT berbeda.
- **Then** sistem menolak — jalur pelaporan wajib berada dalam satu PT yang sama.

**Skenario 8: Jalur Pelaporan & Hierarki Anti-Siklus**
- **Given** penetapan Department induk atau jalur pelaporan Job Position akan membentuk lingkaran (mis. A melapor ke B, B melapor balik ke A).
- **When** penetapan tersebut disimpan.
- **Then** sistem menolak — hierarki dan jalur pelaporan wajib berbentuk pohon, tidak boleh membentuk lingkaran.

**Skenario 9: Kuota Jumlah Pegawai Punya Nilai Default**
- **Given** Job Position baru dibuat tanpa mengisi kuota jumlah pegawai, atau mengisi dengan angka kurang dari 1.
- **When** Job Position disimpan.
- **Then** sistem otomatis menetapkan kuota menjadi 1 (bukan menolak penyimpanan) — Admin bisa membuat Job Position dulu, menyesuaikan kuota belakangan.

**Skenario 10: Data yang Masih Dipakai Tidak Boleh Dihapus Sembarangan**
- **Given** sebuah Department masih punya Department anak yang aktif, atau sebuah Department/Job Title masih dipakai oleh Job Position yang aktif.
- **When** Department/Job Title tersebut dihapus.
- **Then** sistem **seharusnya** menolak penghapusan tersebut, supaya tidak ada Department anak atau Job Position yang jadi "yatim" (menunjuk ke data yang sudah tidak ada).
- *Catatan implementasi:* **belum ada** di kode saat ini — penghapusan Department/Job Title/Job Position saat ini tidak mengecek dependensi sama sekali, sehingga data yang masih dipakai anak/relasi lain tetap bisa dihapus. Gap yang perlu ditutup, pola sama seperti gap serupa yang sudah didokumentasikan di [organization.md](organization.md) Ringkasan Gap (Company/Branch).

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Ketiga entity hidup di `internal/workforce/` sebagai satu bounded context, masing-masing (`Department`, `JobTitle`, `JobPosition`) punya repository sendiri — bukan digabung jadi satu aggregate. Deteksi siklus (Skenario 8) pakai satu implementasi yang dipakai bersama oleh Department maupun Job Position, bukan logika terpisah per entity.
- **Multi-Entity Scoping (MANDATORY):** Ketiga entity — **Company-owned** (`company_id` NOT NULL, **tanpa** `branch_id`) — struktur organisasi berlaku untuk seluruh PT, bukan per cabang, selaras `scoping-convention.md` §1. `company_id` pada Job Position **tidak diisi manual oleh pengguna** — otomatis mengikuti `company_id` milik Department yang dipilih, supaya filter kepemilikan data tetap konsisten di ketiga entity tanpa perlu menelusuri relasi tiap kali dibaca.
- **Cross-Domain Communication:** Validasi `company_id` ke modul Organization (Skenario 2) wajib lewat Application Service Organization, bukan akses langsung ke datanya.
- **Penegakan Akses (RBAC):** Filter berdasarkan PT pada daftar Department/Job Title/Job Position disediakan lewat kontrak scope terpusat (lihat [rbac.md](rbac.md) §5) — sampai RBAC selesai dibangun, filter tersebut berjalan default tanpa pembatasan tambahan (mode Owner), sama seperti modul lain yang sudah dimigrasi.
- **Persistensi / Database:** Hapus bersifat lunak (data tidak hilang permanen) — tapi lihat gap Skenario 10, saat ini belum ada validasi yang mencegah penghapusan data yang masih dipakai relasi lain.
- **UI (Frontend):** Form pembuatan Job Position butuh pilihan Department dan Job Title, serta pencarian jabatan atasan (jalur pelaporan) dari daftar Job Position yang sudah ada. Tampilan bagan organisasi dan tabel Department bertingkat (*nested*, bisa dibuka-tutup) butuh seluruh data diambil sekaligus (bukan per halaman) — supaya struktur induk-anak tidak terpotong saat sebagian data ada di halaman lain.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Organization @1.0.1** — `company_id` yang dipakai Department/Job Title divalidasi ke Company yang benar-benar ada dan aktif sebelum data disimpan (lihat [organization.md](organization.md) §4).
- **RBAC @1.0.1** — filter kepemilikan PT pada daftar Department/Job Title/Job Position disediakan modul ini (lihat [rbac.md](rbac.md) §5); sampai RBAC diimplementasikan, penegakan berjalan default kosong (mode Owner).

**Consumed by:**
- **Employee @1.0.0** — karyawan menempati satu Job Position; mengonsumsi identitas Job Position, jalur pelaporannya, dan kuota jumlah pegawai untuk penempatan.

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Department
- **Aturan Bisnis:** Wajib milik satu PT (`company_id`). `code` wajib unik **dalam satu PT** *(Pesan error: "Kode departemen sudah digunakan di perusahaan ini")*. Department tanpa induk (`parent_id` kosong) jadi akar bagan organisasi. Department induk wajib PT yang sama dengan anaknya (Skenario 4), dan hierarkinya wajib bebas lingkaran (Skenario 8).

| id | company_id | code | name | parent_id | is_active |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `dept-1` | `co-1` | DIR | Direksi | `null` | `true` |
| `dept-2` | `co-1` | TI | Divisi Teknologi Informasi | `dept-1` | `true` |
| `dept-3` | `co-1` | DEV | Departemen Pengembangan | `dept-2` | `true` |

### 7.2. Job Title
- **Aturan Bisnis:** Wajib milik satu PT (`company_id`) — tiap PT punya daftar grade sendiri, tidak dibagi lintas PT. `code` wajib unik **dalam satu PT** *(Pesan error: "Kode jenjang jabatan sudah digunakan di perusahaan ini")*. `grade_level` makin tinggi berarti pangkat makin tinggi, dipakai untuk urutan tampilan dan standar gaji (rumus/nominal jadi tanggung jawab modul Payroll).

| id | company_id | code | name | grade_level | is_active |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `title-1` | `co-1` | DIR | Direktur | `10` | `true` |
| `title-2` | `co-1` | MGR | Manajer | `7` | `true` |
| `title-3` | `co-1` | STF | Staf | `3` | `true` |

### 7.3. Job Position
- **Aturan Bisnis:** Kombinasi tepat satu Department + satu Job Title, keduanya wajib dari PT yang sama (Skenario 6). `company_id` otomatis mengikuti Department, tidak diisi manual (§5). Jalur pelaporan (`reports_to_id`, opsional — kosong berarti posisi puncak) wajib menunjuk Job Position di PT yang sama (Skenario 7) dan bebas lingkaran (Skenario 8). `headcount_quota` (kuota jumlah pegawai) default `1` kalau tidak diisi atau diisi kurang dari 1 (Skenario 9).

| id | company_id | name | department_id | job_title_id | reports_to_id | headcount_quota | is_active |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `pos-1` | `co-1` | Direktur Utama | `dept-1` | `title-1` | `null` | `1` | `true` |
| `pos-2` | `co-1` | Manajer Pengembangan | `dept-3` | `title-2` | `pos-1` | `3` | `true` |
| `pos-3` | `co-1` | Staf Programmer | `dept-3` | `title-3` | `pos-2` | `10` | `true` |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Hapus data yang masih dipakai relasi lain | Penghapusan Department/Job Title/Job Position tidak mengecek dependensi sama sekali (Skenario 10). | Perlu validasi tolak-hapus kalau Department masih punya anak aktif, atau Department/Job Title masih dipakai Job Position aktif. |
