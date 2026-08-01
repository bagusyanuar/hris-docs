---
module: Work Shift
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [organization@1.0.1, rbac@1.0.1]
consumed_by: [attendance@planned]
---

# Product Requirements: Work Shift Module

> **Catatan grounding:** Modul ini adalah fitur baru (belum ada implementasi kode sama sekali). Ini adalah Master Data pertama dari domain Attendance & Time Tracking — mendefinisikan **pola jam kerja (shift)** yang berlaku di tiap cabang. PRD [organization.md](organization.md) §2 sudah secara eksplisit menyatakan "Pengaturan shift/jam kerja per-cabang" bukan tanggung jawab modul Organization, melainkan modul ini. Modul ini **tidak** menangani absensi aktual karyawan (jam datang/pulang, keterlambatan real-time) atau penjadwalan/roster — itu tanggung jawab modul **Attendance** yang direncanakan menyusul dan akan mengonsumsi data dari modul ini.

---

## 1. Tujuan & Dampak (The "Why")

Tiap cabang (Branch) dalam satu PT bisa punya pola jam kerja berbeda-beda — kantor pusat kerja 08:00–17:00, gudang punya shift pagi/siang/malam bergilir, toko retail buka lebih larut. Tanpa Master Data ini, pola jam kerja berisiko tertanam sebagai angka tetap di dalam kode, sehingga penambahan cabang baru atau perubahan pola shift butuh rilis ulang aplikasi.

Modul Work Shift menjadikan pola jam kerja sebagai data yang dikelola sendiri oleh masing-masing cabang, sehingga:
- Tiap cabang bisa mendefinisikan shift sesuai kebutuhan operasionalnya sendiri, tanpa menunggu rilis aplikasi baru.
- Aturan jam kerja (jam mulai, jam selesai, shift lintas hari/malam, toleransi keterlambatan, durasi istirahat) tercatat sebagai data terstruktur, bukan logika tersembunyi di kode — mudah diaudit HR dan mudah disesuaikan bila kebijakan berubah.
- Modul Attendance di masa depan bisa membaca definisi shift ini sebagai satu sumber kebenaran saat menghitung keterlambatan, lembur, dan kepatuhan jam kerja karyawan.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pengelolaan daftar Shift Kerja per cabang (Branch): tambah, ubah, nonaktifkan.
- Tiap Shift membawa aturan dasar: kode, nama, jam mulai, jam selesai, apakah shift lintas hari (overnight, mis. shift malam 22:00–06:00), durasi istirahat, dan toleransi keterlambatan (grace period) sebelum dianggap terlambat.
- Penyediaan daftar ini sebagai pilihan (dropdown) saat HR menetapkan/mengubah shift kerja karyawan (dikonsumsi oleh modul Attendance di masa depan).

**Out-of-Scope (TIDAK di modul ini):**
- **Absensi aktual karyawan** (jam datang/pulang, status hadir/terlambat/alpha per hari) — itu tanggung jawab modul Attendance, rencana mendatang.
- **Penjadwalan/roster shift bergilir per karyawan per tanggal** (mis. karyawan X shift pagi tanggal 1–5, shift malam tanggal 6–10) — modul ini hanya menyimpan *definisi* pola shift, bukan jadwal penugasan harian. Roster adalah tanggung jawab modul Attendance.
- **Perhitungan lembur (overtime) dan nominalnya** — modul ini hanya menyediakan jam selesai shift sebagai referensi batas normal; perhitungan durasi lembur dan nominalnya adalah tanggung jawab modul Attendance/Payroll.
- **Kalender hari libur nasional/cuti bersama** — konsep terpisah, tidak dimiliki modul ini (lihat catatan §5).
- **Migrasi otomatis lintas-cabang** — tiap cabang memulai dengan daftar dasar hasil *seeding*, tidak ada mekanisme "copy" otomatis dari cabang lain.

---

## 3. User Roles & Permissions

| Role | Read | Create | Update | Nonaktifkan |
|------|------|--------|--------|-------------|
| Superadmin / Owner Group Usaha | ✅ (semua PT & cabang) | ✅ (semua PT & cabang) | ✅ (semua PT & cabang) | ✅ (semua PT & cabang) |
| Admin Perusahaan (HR PT ybs.) | ✅ (semua cabang milik PT sendiri) | ✅ (semua cabang milik PT sendiri) | ✅ (semua cabang milik PT sendiri) | ✅ (semua cabang milik PT sendiri) |
| Admin Cabang (HR/Supervisor cabang ybs.) | ✅ (hanya cabang sendiri) | ✅ (hanya cabang sendiri) | ✅ (hanya cabang sendiri) | ✅ (hanya cabang sendiri) |
| Karyawan (ESS) | ✅ (hanya melihat shift miliknya sendiri lewat profil) | ❌ | ❌ | ❌ |

- **Catatan tambahan:** Tidak ada penghapusan permanen (*hard delete*) — shift yang sudah pernah dipakai dalam riwayat absensi karyawan hanya bisa dinonaktifkan, tidak dihapus, supaya riwayat absensi lama tidak rusak.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: HR Menambah Shift Baru**
- **Given** Admin Cabang membutuhkan pola shift baru yang belum ada di daftar (misalnya "Shift Malam").
- **When** Admin mengisi kode, nama, jam mulai (22:00), jam selesai (06:00), menandai shift ini lintas hari, lalu menyimpan.
- **Then** sistem menyimpan shift tersebut khusus untuk cabang ybs., langsung tersedia sebagai pilihan saat menetapkan shift karyawan cabang tersebut, dan **tidak muncul** di cabang lain.

**Skenario 2: Kode Shift Duplikat dalam Cabang yang Sama**
- **Given** cabang tertentu sudah memiliki shift dengan kode tertentu (misalnya "PAGI").
- **When** Admin mencoba membuat shift baru dengan kode yang sama persis di cabang yang sama.
- **Then** sistem menolak penyimpanan dan menampilkan pesan *"Kode shift ini sudah digunakan di cabang Anda"*.

**Skenario 3: Jam Selesai Lebih Awal dari Jam Mulai Tanpa Ditandai Lintas Hari**
- **Given** Admin mengisi jam mulai 08:00 dan jam selesai 06:00 pada shift baru.
- **When** Admin menyimpan tanpa menandai shift ini sebagai lintas hari (overnight).
- **Then** sistem menolak penyimpanan dan menampilkan pesan *"Jam selesai lebih awal dari jam mulai — tandai sebagai shift lintas hari jika ini shift malam"*.

**Skenario 4: Menonaktifkan Shift yang Masih Dipakai Karyawan Aktif**
- **Given** ada karyawan aktif yang sedang memakai shift "Shift Pagi".
- **When** Admin menonaktifkan shift "Shift Pagi".
- **Then** sistem tetap mengizinkan penonaktifan (karyawan yang sudah memakainya tidak terganggu/tidak error), tetapi "Shift Pagi" hilang dari pilihan dropdown untuk penetapan shift **baru**.

**Skenario 5: Shift Wajib Sesuai Cabang Karyawan (Scoping)**
- **Given** Admin sedang menetapkan shift untuk karyawan yang bekerja di Cabang B milik PT A.
- **When** Admin memilih shift dari daftar.
- **Then** sistem hanya menampilkan shift milik Cabang B; jika ada upaya memaksakan ID shift milik cabang lain (termasuk cabang lain dalam PT yang sama), sistem menolak dengan pesan ketidakcocokan cabang.

**Skenario 6: Toleransi Keterlambatan Dipakai Modul Attendance**
- **Given** shift "Shift Pagi" dikonfigurasi dengan toleransi keterlambatan 15 menit dari jam mulai 08:00.
- **When** karyawan mencatat kehadiran pukul 08:10 (masih dalam modul Attendance, rencana mendatang).
- **Then** sistem menandai kehadiran tersebut sebagai tepat waktu, bukan terlambat, karena masih dalam batas toleransi.
- *Catatan implementasi:* **belum ada** — logika pencatatan kehadiran & penandaan terlambat adalah bagian modul Attendance yang belum dibangun. Modul ini hanya menyediakan kolom `late_tolerance_minutes` sebagai sumber aturan untuk dikonsumsi modul tersebut.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Modul ini hidup di domain baru `internal/workshift` (terpisah dari `internal/attendance` yang akan dibangun kemudian untuk pencatatan kehadiran), dikonsumsi modul lain lewat Application Service, bukan akses tabel langsung.
- **Multi-Entity Scoping (MANDATORY):** Diklasifikasikan sebagai **Company + Location bound** (`company_id` **dan** `branch_id` NOT NULL) sesuai `scoping-convention.md` §1 — **berbeda** dari Employment Status/Leave Type yang Company-owned, karena [organization.md](organization.md) §2 dan [product-vision.md](product-vision.md) §Struktur Organisasi eksplisit menyatakan shift/jam kerja adalah data **per-cabang**, bukan berlaku seragam se-PT. Filter scope dienforce lewat `scope.FromContext` pada setiap query baca/tulis; `branch_id` yang dipilih wajib milik `company_id` yang sama (tolak dengan `ErrBranchCompanyMismatch`).
- **Persistensi / Database:** **Soft delete tidak relevan** — modul ini tidak pernah hapus data, hanya nonaktifkan (`is_active=false`). Tiap baris dikelola individual (create/update biasa), bukan pola delete-recreate batch.
- **Integritas Data:** Validasi `end_time` vs `start_time` wajib dilakukan di level aplikasi, bukan hanya UI — `end_time` lebih awal dari `start_time` HANYA diizinkan bila `is_overnight=true` (lihat Skenario 3).
- **Kalender kerja:** Modul ini **tidak memiliki** konsep hari kerja/hari libur (mis. shift berlaku hari apa saja dalam seminggu, atau pengecualian hari libur nasional). Itu konsep terpisah yang, bila dibutuhkan, menjadi tanggung jawab modul Attendance saat menyusun roster.
- **UI (Frontend):** Halaman pengelolaan Shift cukup form sederhana (bukan wizard) karena hanya 1 entity datar tanpa sub-entity. Input jam mulai/selesai wajib pakai time-picker, bukan free-text.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Organization @1.0.1** — sumber `company_id` dan `branch_id` (Company & Branch) untuk scope kepemilikan data. Fisik *foreign key* ke tabel `companies`/`branches` mengikuti jadwal staged yang sama dengan modul lain (`scoping-convention.md` §4) — kolom & aturan scope dipaku sekarang, penegakan penuh menyusul saat modul Organization selesai dibangun.
- **RBAC @1.0.1** — filter `company_id`/`branch_id` di §5 disediakan oleh modul ini (lihat [rbac.md](rbac.md) §5); sampai RBAC diimplementasikan, penegakan berjalan default kosong (mode Owner).

**Consumed by:**
- **Attendance (rencana mendatang)** — akan membaca daftar Shift aktif milik cabang karyawan untuk penetapan shift, serta membaca `start_time`, `end_time`, `is_overnight`, `break_duration_minutes`, dan `late_tolerance_minutes` untuk perhitungan keterlambatan dan jam kerja efektif.

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Work Shift
- **Aturan Bisnis:** `code` wajib unik **per cabang** (bukan unik global maupun unik per-PT — dua cabang dalam PT yang sama boleh punya kode yang sama persis, mis. dua-duanya punya "PAGI"). *(Pesan error: "Kode shift ini sudah digunakan di cabang Anda")*. `name` wajib diisi untuk tampilan dropdown. `end_time` lebih awal dari `start_time` hanya sah bila `is_overnight=true` *(Pesan error: "Jam selesai lebih awal dari jam mulai — tandai sebagai shift lintas hari jika ini shift malam")*. `late_tolerance_minutes` default 0 bila tidak diisi. `is_active=false` menyembunyikan shift dari pilihan penetapan baru tanpa mengganggu karyawan yang sudah memakainya.

| id | company_id | branch_id | code | name | start_time | end_time | is_overnight | break_duration_minutes | late_tolerance_minutes | is_active | sort_order |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `ws-1` | `co-1` | `br-1` | REGULER | Non-Shift / Reguler | 08:00 | 17:00 | `false` | 60 | 15 | `true` | 1 |
| `ws-2` | `co-1` | `br-1` | PAGI | Shift Pagi | 06:00 | 14:00 | `false` | 30 | 10 | `true` | 2 |
| `ws-3` | `co-1` | `br-1` | SIANG | Shift Siang | 14:00 | 22:00 | `false` | 30 | 10 | `true` | 3 |
| `ws-4` | `co-1` | `br-1` | MALAM | Shift Malam | 22:00 | 06:00 | `true` | 30 | 10 | `true` | 4 |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Shift kerja | Belum ada implementasi sama sekali (fitur baru). | Buat Master Data baru `internal/workshift` sesuai §7. |
