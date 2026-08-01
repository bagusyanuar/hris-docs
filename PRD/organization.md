---
module: Organization
version: 2.0.0
status: Draft
owner: bagusyanuar
updated: 2026-08-01 17:00:00
depends_on: []
consumed_by: [workforce-structure@1.0.0, employee@1.0.0, employment-status@1.0.0, rbac@planned, payroll@planned, attendance@planned]
---

# Product Requirements: Organization Module

> **Catatan grounding:** Modul ini sudah terimplementasi di backend (`internal/organization/`). PRD ini adalah standardisasi dokumentasi bisnis dari arsitektur *existing* agar selaras dengan aturan *Control Plane* `hris-docs` — sekaligus migrasi dari dokumen legacy `hris-backend/docs/PRD/organization.md` (v2.0.0, breaking scope change dari versi 1.x yang dulu juga mencakup Department/Job Title/Job Position — konsep itu sudah dipindah ke modul **Workforce Structure**, di luar cakupan PRD ini).

---

## 1. Tujuan & Dampak (The "Why")

Satu grup usaha (holding) bisa membawahi banyak PT (badan hukum terpisah), dan tiap PT bisa punya banyak cabang/lokasi fisik. Modul Organization menyediakan fondasi dua entitas dasar ini — **Company** (PT) dan **Branch** (cabang) — sehingga satu aplikasi bisa menaungi seluruh grup usaha dengan satu login, tanpa perlu instalasi/deploy terpisah per PT.

Masalah yang diselesaikan:
- **Pemisahan legal vs lokasi.** Kewajiban legal seperti pajak dan BPJS melekat ke badan hukum (Company/PT), sementara operasional harian seperti jam kerja dan absensi melekat ke lokasi (Branch/cabang). Keduanya konsep berbeda yang butuh direpresentasikan sebagai dua entitas terpisah, bukan digabung jadi satu.
- **Isolasi data antar-PT & antar-cabang.** HR di cabang A semestinya tidak melihat data cabang B; HR di PT-X semestinya tidak melihat PT-Y. Pemilik grup usaha (Owner) tetap bisa melihat semuanya.
- **Fondasi konsolidasi.** Owner butuh melihat gambaran gabungan lintas PT/cabang, sementara tiap PT tetap punya pembukuan sendiri-sendiri.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pendaftaran dan pengelolaan **Company** (PT/badan hukum): kode internal, nama badan hukum, NPWP, nomor registrasi BPJS, status aktif.
- Pendaftaran dan pengelolaan **Branch** (cabang/lokasi): kode cabang, nama, kota, penanda kantor pusat (*main branch*), status aktif — setiap Branch wajib menempel ke satu Company.
- Penetapan satu Branch sebagai kantor pusat (*head office*) per Company.
- Pencarian gabungan: menemukan Company berdasarkan nama badan hukumnya sendiri, **atau** berdasarkan nama salah satu cabangnya.
- Penyediaan dua dimensi (`Company`, `Branch`) sebagai fondasi pemilahan data untuk seluruh modul operasional lain (Workforce Structure, Employee, Employment Status, dst).

**Out-of-Scope (TIDAK di modul ini):**
- **Department, Job Title, Job Position** — sudah dipindah ke modul **Workforce Structure**, bukan bagian modul ini lagi sejak versi 2.0.0.
- **Penegakan hak akses (RBAC) berbasis Company/Branch** — modul ini hanya menyediakan *dimensi* datanya (kolom identitas PT/cabang); penegakan siapa-boleh-lihat-apa adalah tanggung jawab modul **RBAC** (rencana mendatang).
- **Perhitungan pajak/BPJS/payroll per-PT** — tanggung jawab modul Payroll (rencana mendatang).
- **Pengaturan shift/jam kerja/kalender libur per-cabang** — tanggung jawab modul Attendance/Leave (rencana mendatang).
- **Riwayat perpindahan karyawan antar-cabang/PT** — tanggung jawab modul Employee di fase lanjutan.
- **Penghapusan Company beserta seluruh Branch anaknya secara berantai (cascade)** — saat ini menghapus Company **tidak** otomatis ikut menghapus Branch di bawahnya (lihat §4 Skenario 5 dan Ringkasan Gap).

---

## 3. User Roles & Permissions

| Role | Cakupan Company | Cakupan Branch | Baca | Tulis |
|------|-----------------|-----------------|------|-------|
| Owner / Group Admin | Semua PT | Semua cabang | ✅ | ✅ |
| Admin Perusahaan (HR PT-X) | 1 PT | Semua cabang PT-X | ✅ (PT-X saja) | ✅ (PT-X saja) |
| Admin Cabang (HR cabang) | 1 PT | 1 cabang | ✅ (cabang sendiri) | ✅ (cabang sendiri) |
| Karyawan (ESS) | PT sendiri | Cabang sendiri | ✅ (identitas PT/cabang sendiri saja) | ❌ |

- **Catatan tambahan:** Detail penegakan akses (siapa benar-benar dibatasi lihat apa) adalah tanggung jawab PRD **RBAC** — modul ini baru menyediakan kolom kepemilikan datanya. Sampai RBAC selesai dibangun, seluruh operasi berjalan dalam mode "Owner" (tanpa pembatasan tambahan).

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Company Unik per NPWP (Bila Diisi)**
- **Given** sudah ada Company dengan NPWP tertentu terdaftar.
- **When** ada percobaan mendaftarkan Company baru dengan NPWP yang sama persis.
- **Then** sistem menolak dan menampilkan pesan bahwa NPWP tersebut sudah terdaftar.
- **Catatan:** NPWP bersifat opsional saat pendaftaran awal — dua Company yang sama-sama belum mengisi NPWP **tidak** dianggap konflik satu sama lain.

**Skenario 2: Branch Wajib Menempel ke Company yang Valid**
- **Given** seseorang mencoba mendaftarkan Branch baru.
- **When** Company tujuan yang dirujuk tidak ditemukan/tidak valid.
- **Then** sistem menolak pendaftaran Branch tersebut — tidak boleh ada Branch yang berdiri sendiri tanpa Company induk yang jelas.

**Skenario 3: Kode Branch Unik dalam Satu Company**
- **Given** sebuah Company sudah memiliki Branch dengan kode tertentu.
- **When** ada percobaan mendaftarkan Branch baru dengan kode yang sama persis **di Company yang sama**.
- **Then** sistem menolak dan menampilkan pesan kode cabang sudah digunakan. Kode yang sama tetap **boleh** dipakai di Company yang berbeda.

**Skenario 4: Satu Company Hanya Punya Satu Kantor Pusat**
- **Given** sebuah Company sudah punya satu Branch yang ditandai sebagai kantor pusat (*main branch*).
- **When** Admin menandai Branch lain di Company yang sama sebagai kantor pusat baru.
- **Then** sistem otomatis mencabut status kantor pusat dari Branch lama dan memindahkannya ke Branch yang baru ditandai — Admin **tidak perlu** melakukan dua langkah manual (cabut dulu, baru pasang), dan pada saat mana pun hanya ada tepat satu kantor pusat aktif per Company.

**Skenario 5: Company Dinonaktifkan/Dihapus Tidak Menghapus Branch Anaknya**
- **Given** sebuah Company memiliki beberapa Branch aktif.
- **When** Company tersebut dihapus (dinonaktifkan).
- **Then** Branch-branch di bawahnya **tetap ada** dan tidak ikut terhapus — ini adalah batasan yang disengaja pada rilis saat ini (lihat Ringkasan Gap), bukan pengecualian sistem.
- *Catatan implementasi:* belum ada validasi "tolak hapus Company kalau masih punya Branch aktif" — gap yang perlu dipertimbangkan di iterasi berikutnya bila kebutuhan bisnis muncul.

**Skenario 6: Menemukan Company Lewat Nama Cabangnya**
- **Given** seorang Admin hanya ingat nama salah satu cabang, bukan nama badan hukum lengkap PT-nya.
- **When** Admin mencari menggunakan nama cabang tersebut di daftar Company.
- **Then** sistem tetap menemukan Company yang dimaksud, dan menampilkan **seluruh** daftar cabang milik Company itu (bukan cuma cabang yang cocok dengan pencarian).

**Skenario 7: Data Historis Tidak Rusak Saat Dihapus**
- **Given** sebuah Company atau Branch dihapus.
- **When** ada modul lain (Payroll, Attendance, dst.) yang masih merujuk riwayat data lama milik Company/Branch tersebut.
- **Then** riwayat tersebut tetap utuh dan bisa diakses — penghapusan bersifat "nonaktif" (dapat dipulihkan/ditelusuri), bukan penghapusan permanen yang menghilangkan jejak data.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Company & Branch hidup di `internal/organization/` sebagai dua aggregate root independen (Branch bukan sub-koleksi Company, hanya mereferensikan Company lewat ID) — Department/Job Title/Job Position berada di modul terpisah `internal/workforce/`.
- **Multi-Entity Scoping (MANDATORY):**
  - **Company** = **Legal root** — tidak punya kolom scope (dirinya sendiri adalah scope tertinggi/akar hierarki).
  - **Branch** = **Company-owned** (`company_id` NOT NULL) — setiap Branch wajib menempel ke satu Company yang pasti, tanpa pengecualian.
- **Persistensi / Database:** **Soft delete only** — Company/Branch yang "dihapus" wajib tetap tersimpan (ditandai nonaktif/terhapus-lunak), demi menjaga integritas riwayat Payroll/Attendance/Employee yang sudah pernah merujuknya. Dilarang penghapusan permanen.
- **Isolasi Data:** Satu basis data bersama dengan kolom identitas kepemilikan (`company_id` pada entity turunannya), bukan basis data terpisah per PT — supaya laporan konsolidasi lintas-PT untuk Owner tetap efisien.
- **UI (Frontend):** Halaman daftar Company menampilkan cabang-cabangnya secara langsung (tidak perlu berpindah halaman/permintaan kedua untuk melihat daftar cabang suatu PT).

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- Tidak ada. Company & Branch adalah akar hierarki data — modul paling dasar dalam struktur multi-PT/multi-cabang.

**Consumed by:**
- **Workforce Structure @1.0.0** — Department dan struktur jabatan mengonsumsi `company_id` untuk cakupan datanya.
- **Employee @1.0.0** — data karyawan wajib terikat ke satu Company dan satu Branch (home branch).
- **Employment Status @1.0.0** — status kepegawaian dikelola per Company, mengonsumsi `company_id` dari modul ini (lihat PRD Employment Status §5).
- **RBAC (rencana mendatang)** — penegakan hak akses akan memakai dua dimensi `company_id`/`branch_id` yang disediakan modul ini.
- **Payroll (rencana mendatang)** — perhitungan pajak/BPJS dikelompokkan per Company.
- **Attendance/Leave (rencana mendatang)** — pengaturan jam kerja/kalender libur dikelompokkan per Branch.

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Company — PT / Badan Hukum
- **Aturan Bisnis:** `code` dan `legal_name` wajib diisi. `npwp` opsional — kalau diisi, wajib unik lintas seluruh Company *(Pesan error: "NPWP sudah terdaftar")*. `bpjs_no` opsional, belum divalidasi format khusus di rilis ini. `is_active=false` menandakan Company tidak lagi beroperasi (soft delete), riwayat data anaknya tetap utuh.

| id | code | legal_name | npwp | bpjs_no | is_active |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `co-1` | PTA | PT Alpha Nusantara | `01.234.567.8-901.000` | `JKN-0001` | `true` |
| `co-2` | PTB | PT Beta Sejahtera | `null` | `null` | `true` |

### 7.2. Branch — Cabang/Lokasi — 1:N dari Company
- **Aturan Bisnis:** `company_id` wajib merujuk Company yang valid dan aktif. `code` wajib unik **dalam satu Company** (boleh sama di Company berbeda) *(Pesan error: "Kode cabang sudah digunakan di perusahaan ini")*. `is_main=true` menandai kantor pusat — tepat satu per Company, penetapan Branch baru sebagai kantor pusat otomatis mencabut status dari Branch lama (Skenario 4).

| id | company_id | code | name | city | is_main | is_active |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `br-1` | `co-1` | JKT | Kantor Pusat Jakarta | Jakarta | `true` | `true` |
| `br-2` | `co-1` | SBY | Cabang Surabaya | Surabaya | `false` | `true` |
| `br-3` | `co-2` | BDG | Kantor Pusat Bandung | Bandung | `true` | `true` |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Hapus Company beserta Branch anak | Menghapus Company tidak memvalidasi/menghentikan proses meski masih ada Branch aktif di bawahnya (Skenario 5). | Belum ada keputusan bisnis final — didokumentasikan sebagai batasan yang disengaja, direvisit bila kebutuhan bisnis muncul. |
| Penegakan akses (RBAC) | Filter `company_id`/`branch_id` di query baca sudah disiapkan strukturnya, tapi berjalan tanpa pembatasan tambahan (mode Owner) karena modul RBAC belum ada. | Menunggu PRD & implementasi modul RBAC (rencana mendatang). |
