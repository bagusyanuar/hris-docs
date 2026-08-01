---
module: Leave Type
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [organization@1.0.1, rbac@1.0.1]
consumed_by: [leave@planned]
---

# Product Requirements: Leave Type Module

> **Catatan grounding:** Modul ini adalah fitur baru (belum ada implementasi kode sama sekali). Ini adalah Master Data pertama dari domain Cuti (Leave/Time-off) — mendefinisikan **jenis-jenis cuti** (mis. Cuti Tahunan, Cuti Sakit, Cuti Melahirkan) beserta aturan dasarnya. Modul ini **tidak** menangani pengajuan cuti karyawan, sisa saldo cuti (leave balance), atau alur approval — itu tanggung jawab modul **Leave** (Pengajuan Cuti) yang direncanakan menyusul dan akan mengonsumsi data dari modul ini.

---

## 1. Tujuan & Dampak (The "Why")

Setiap perusahaan (PT) dalam grup usaha punya kebijakan cuti yang berbeda-beda — jumlah jenis cuti, apakah dibayar atau tidak, apakah butuh lampiran (mis. surat dokter untuk cuti sakit), dan apakah sisa cuti tahun ini bisa dibawa ke tahun depan. Tanpa Master Data ini, aturan-aturan tersebut berisiko tertanam sebagai daftar tetap di dalam kode, sehingga setiap PT baru atau perubahan kebijakan cuti butuh rilis ulang aplikasi.

Modul Leave Type menjadikan jenis cuti sebagai data yang dikelola sendiri oleh masing-masing PT, sehingga:
- Tiap PT bisa mendefinisikan jenis cuti sesuai kebijakan internalnya sendiri, tanpa menunggu rilis aplikasi baru.
- Aturan kelayakan (berbayar/tidak, butuh lampiran, minimal jarak pengajuan, batas carry-forward) tercatat sebagai data terstruktur, bukan logika tersembunyi di kode — mudah diaudit HR dan mudah disesuaikan bila kebijakan berubah.
- Modul Leave (Pengajuan Cuti) di masa depan bisa membaca aturan ini sebagai satu sumber kebenaran saat memvalidasi pengajuan cuti karyawan, bukan menerka dari nama jenis cutinya.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pengelolaan daftar Jenis Cuti per perusahaan (PT): tambah, ubah, nonaktifkan.
- Tiap Jenis Cuti membawa aturan dasar: apakah cuti dibayar (paid/unpaid), jatah hari default per tahun, apakah butuh lampiran/dokumen pendukung, apakah sisa jatah bisa dibawa ke tahun berikutnya (carry-forward) beserta batas maksimalnya, minimal jarak hari pengajuan sebelum tanggal cuti, dan pembatasan berdasarkan jenis kelamin (mis. Cuti Melahirkan khusus karyawan perempuan).
- Penyediaan daftar ini sebagai pilihan (dropdown) saat karyawan/HR mengajukan cuti (dikonsumsi oleh modul Leave di masa depan).

**Out-of-Scope (TIDAK di modul ini):**
- **Pengajuan cuti karyawan (leave request) & alur approval** — itu tanggung jawab modul Leave (Pengajuan Cuti), rencana mendatang.
- **Perhitungan & penyimpanan sisa saldo cuti (leave balance) per karyawan** — modul ini hanya menyimpan *aturan* (jatah default, batas carry-forward), bukan angka saldo aktual milik tiap karyawan.
- **Kalender hari libur/hari kerja** yang dipakai untuk menghitung jumlah hari cuti efektif — itu konsep terpisah (lihat catatan di §5, dikonsumsi bukan dimiliki modul ini).
- **Keterkaitan otomatis dengan Employment Status** (mis. hanya Karyawan Tetap yang berhak Cuti Tahunan) — flag `has_leave_entitlement` sudah ada di modul Employment Status, tapi logika pemetaan "status kepegawaian mana berhak jenis cuti apa" adalah tanggung jawab modul Leave saat memvalidasi pengajuan, bukan modul ini.
- **Migrasi otomatis lintas-PT** — tiap PT memulai dengan daftar dasar hasil *seeding*, tidak ada mekanisme "copy" otomatis dari PT lain.

---

## 3. User Roles & Permissions

| Role | Read | Create | Update | Nonaktifkan |
|------|------|--------|--------|-------------|
| Superadmin / Owner Group Usaha | ✅ (semua PT) | ✅ (semua PT) | ✅ (semua PT) | ✅ (semua PT) |
| Admin Perusahaan (HR PT ybs.) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) |
| Karyawan (ESS) | ✅ (hanya daftar jenis cuti aktif miliknya, sebagai pilihan saat mengajukan cuti) | ❌ | ❌ | ❌ |

- **Catatan tambahan:** Tidak ada penghapusan permanen (*hard delete*) — jenis cuti yang sudah pernah dipakai dalam pengajuan cuti karyawan hanya bisa dinonaktifkan, tidak dihapus, supaya riwayat pengajuan cuti lama tidak rusak.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: HR Menambah Jenis Cuti Baru**
- **Given** Admin Perusahaan PT A membutuhkan jenis cuti baru yang belum ada di daftar standar (misalnya "Cuti Ibadah Haji").
- **When** Admin mengisi kode, nama, dan aturan dasar (berbayar/tidak, jatah hari default) jenis cuti baru lalu menyimpan.
- **Then** sistem menyimpan jenis cuti tersebut khusus untuk PT A, langsung tersedia sebagai pilihan saat karyawan PT A mengajukan cuti, dan **tidak muncul** di PT lain.

**Skenario 2: Kode Jenis Cuti Duplikat dalam PT yang Sama**
- **Given** PT A sudah memiliki jenis cuti dengan kode tertentu (misalnya "ANNUAL").
- **When** Admin PT A mencoba membuat jenis cuti baru dengan kode yang sama persis.
- **Then** sistem menolak penyimpanan dan menampilkan pesan *"Kode jenis cuti ini sudah digunakan di perusahaan Anda"*.

**Skenario 3: Menonaktifkan Jenis Cuti yang Masih Punya Riwayat Pengajuan**
- **Given** ada karyawan yang pernah mengajukan cuti dengan jenis "Cuti Sakit".
- **When** Admin menonaktifkan jenis cuti "Cuti Sakit".
- **Then** sistem tetap mengizinkan penonaktifan (riwayat pengajuan lama tidak terganggu/tidak error), tetapi "Cuti Sakit" hilang dari pilihan dropdown untuk pengajuan **baru**.
- *Catatan implementasi:* validasi "masih punya riwayat pengajuan" ini bergantung pada modul Leave (rencana mendatang) yang belum ada — sampai modul Leave dibangun, penonaktifan berjalan tanpa pengecekan riwayat karena riwayatnya sendiri belum eksis.

**Skenario 4: Jenis Cuti Wajib Sesuai Perusahaan Karyawan (Scoping)**
- **Given** karyawan PT A sedang membuka daftar pilihan jenis cuti.
- **When** sistem menampilkan daftar jenis cuti.
- **Then** sistem hanya menampilkan jenis cuti milik PT A; jika ada upaya memaksakan ID jenis cuti milik PT lain (misalnya lewat manipulasi request), sistem menolak dengan pesan ketidakcocokan perusahaan.

**Skenario 5: Konfigurasi Carry-Forward Tidak Konsisten**
- **Given** Admin mengisi jenis cuti baru dengan `is_carry_forward = false`.
- **When** Admin juga mengisi angka pada `max_carry_forward_days` (misalnya 5 hari).
- **Then** sistem menolak penyimpanan dan menampilkan pesan *"Batas hari carry-forward hanya bisa diisi jika carry-forward diaktifkan"*.

**Skenario 6: Pembatasan Berdasarkan Jenis Kelamin**
- **Given** Admin membuat jenis cuti "Cuti Melahirkan" dan mengisi pembatasan jenis kelamin `FEMALE`.
- **When** jenis cuti ini ditampilkan sebagai pilihan untuk karyawan laki-laki saat mengajukan cuti (dikonsumsi modul Leave).
- **Then** jenis cuti "Cuti Melahirkan" **tidak muncul** di daftar pilihan karyawan laki-laki tersebut.
- *Catatan implementasi:* enforcement penyaringan ini dieksekusi oleh modul Leave (rencana mendatang) saat menyusun daftar pilihan; modul ini hanya bertanggung jawab menyimpan flag pembatasannya dengan benar.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Modul ini hidup di domain baru `internal/leavetype` (terpisah dari `internal/leave` yang akan dibangun kemudian untuk pengajuan cuti), dikonsumsi modul lain lewat Application Service, bukan akses tabel langsung.
- **Multi-Entity Scoping (MANDATORY):** Diklasifikasikan sebagai **Company-owned** (`company_id` NOT NULL, tanpa `branch_id`) sesuai `scoping-convention.md` §1 — kebijakan jenis cuti berlaku untuk seluruh cabang dalam satu PT, bukan spesifik satu cabang, selaras keputusan yang sama pada modul Employment Status. Filter scope dienforce lewat `scope.FromContext` pada setiap query baca/tulis.
- **Persistensi / Database:** **Soft delete tidak relevan** — modul ini tidak pernah hapus data, hanya nonaktifkan (`is_active=false`). Tiap baris dikelola individual (create/update biasa), bukan pola delete-recreate batch.
- **Integritas Data:** Validasi konsistensi konfigurasi wajib dilakukan di level aplikasi, bukan hanya UI — kombinasi `is_carry_forward=false` dengan `max_carry_forward_days` terisi WAJIB ditolak (lihat Skenario 5).
- **Kalender kerja:** Modul ini **tidak memiliki** konsep hari kerja/hari libur. Bila perhitungan jumlah hari cuti efektif nanti butuh mengecualikan akhir pekan/hari libur nasional, itu adalah tanggung jawab modul Leave saat memproses pengajuan, bukan bagian dari data jenis cuti di modul ini.
- **UI (Frontend):** Halaman pengelolaan Jenis Cuti cukup form sederhana (bukan wizard) karena hanya 1 entity datar tanpa sub-entity.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Organization @1.0.1** — sumber `company_id` (Company) untuk scope kepemilikan data. Fisik *foreign key* ke tabel `companies` mengikuti jadwal staged yang sama dengan modul lain (`scoping-convention.md` §4) — kolom & aturan scope dipaku sekarang, penegakan penuh menyusul saat modul Organization selesai dibangun.
- **RBAC @1.0.1** — filter `company_id` di §5 disediakan oleh modul ini (lihat [rbac.md](rbac.md) §5); sampai RBAC diimplementasikan, penegakan berjalan default kosong (mode Owner).

**Consumed by:**
- **Leave / Pengajuan Cuti (rencana mendatang)** — akan membaca seluruh daftar Jenis Cuti aktif milik PT karyawan sebagai pilihan pengajuan, serta membaca flag `is_paid`, `default_quota_days`, `requires_attachment`, `is_carry_forward`, `max_carry_forward_days`, `min_advance_notice_days`, dan `gender_restriction` untuk validasi pengajuan cuti dan perhitungan saldo cuti karyawan.

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Leave Type
- **Aturan Bisnis:** `code` wajib unik **per perusahaan** (bukan unik global — dua PT boleh punya kode yang sama persis, mis. dua-duanya punya "ANNUAL"). *(Pesan error: "Kode jenis cuti ini sudah digunakan di perusahaan Anda")*. `name` wajib diisi untuk tampilan dropdown. `default_quota_days` opsional — kosong berarti tidak ada jatah tetap (mis. cuti tanpa dibayar/unpaid leave yang tidak dibatasi kuota tahunan tertentu, atau kuota diatur manual per kasus). `max_carry_forward_days` **wajib kosong** bila `is_carry_forward=false` *(Pesan error: "Batas hari carry-forward hanya bisa diisi jika carry-forward diaktifkan")*. `gender_restriction` opsional — nilai yang diizinkan: `ALL`, `MALE`, `FEMALE` (default `ALL`). `is_active=false` menyembunyikan jenis cuti dari pilihan pengajuan baru tanpa mengganggu riwayat yang sudah memakainya.

| id | company_id | code | name | is_active | is_paid | default_quota_days | requires_attachment | is_carry_forward | max_carry_forward_days | min_advance_notice_days | gender_restriction | sort_order |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `lt-1` | `co-1` | ANNUAL | Cuti Tahunan | `true` | `true` | 12 | `false` | `true` | 6 | 3 | `ALL` | 1 |
| `lt-2` | `co-1` | SICK | Cuti Sakit | `true` | `true` | `null` | `true` | `false` | `null` | 0 | `ALL` | 2 |
| `lt-3` | `co-1` | MATERNITY | Cuti Melahirkan | `true` | `true` | 90 | `true` | `false` | `null` | 30 | `FEMALE` | 3 |
| `lt-4` | `co-1` | UNPAID | Cuti Tanpa Dibayar | `true` | `false` | `null` | `false` | `false` | `null` | 7 | `ALL` | 4 |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Jenis cuti | Belum ada implementasi sama sekali (fitur baru). | Buat Master Data baru `internal/leavetype` sesuai §7. |
