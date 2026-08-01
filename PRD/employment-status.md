---
module: Employment Status
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [organization@1.0.1, rbac@1.0.1]
consumed_by: [employee@1.0.1, leave@planned, payroll@planned]
---

# Product Requirements: Employment Status Module

> **Catatan grounding:** Modul ini adalah pemisahan dari konsep "status kepegawaian" yang saat ini masih *hardcoded* sebagai daftar tetap (`PERMANENT`, `CONTRACT`, `PROBATION`, `INTERN`, `DAILY_WORKER`) pada field `employment_type` milik Employee (lihat PRD Employee §5 — bukan field `status` lifecycle aktif/nonaktif, dua hal itu berbeda dan sudah dipisah sebelumnya). PRD ini mengangkat daftar tersebut menjadi Master Data mandiri yang bisa dikelola tanpa perlu merilis ulang aplikasi.

---

## 1. Tujuan & Dampak (The "Why")

Saat ini, jenis hubungan kerja karyawan (Tetap/Kontrak/Probation/Magang/Harian) adalah daftar tetap yang dipatok dalam kode program. Setiap kali sebuah PT dalam grup usaha butuh jenis hubungan kerja baru (misalnya "Outsource" atau "Freelance"), atau butuh mengubah aturan batas waktu kontrak, perubahan itu **wajib lewat rilis ulang aplikasi**.

Modul Employment Status memindahkan daftar ini menjadi data yang dikelola sendiri oleh masing-masing perusahaan (PT), sehingga:
- Tiap PT bisa punya jenis hubungan kerja sendiri sesuai kebutuhan bisnisnya, tanpa menunggu rilis aplikasi baru.
- Aturan kepatuhan (seperti batas maksimal masa kontrak) tercatat sebagai data, bukan angka yang ditulis ulang di dalam kode, sehingga mudah diaudit dan disesuaikan bila ada perubahan aturan.
- Modul lain di masa depan (Cuti, Payroll) bisa membaca hak-hak yang melekat pada suatu jenis hubungan kerja (misalnya apakah berhak cuti tahunan, apakah berhak pesangon) dari satu sumber yang sama, bukan menerka-nerka dari nama statusnya.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Pengelolaan daftar Status Kepegawaian (jenis hubungan kerja) per perusahaan (PT): tambah, ubah, nonaktifkan.
- Setiap Status Kepegawaian membawa aturan bisnis: apakah wajib punya periode kontrak, apakah wajib mengisi tanggal akhir masa percobaan, apakah berhak cuti tahunan, apakah berhak pesangon/kompensasi saat berhenti, dan batas maksimal durasi (bila ada).
- Penyediaan daftar ini sebagai pilihan (dropdown) saat HR mengisi data karyawan.
- Validasi batas maksimal durasi terhadap riwayat kontrak karyawan (mencegah pelanggaran ketentuan ketenagakerjaan seperti batas maksimal kontrak berjangka).

**Out-of-Scope (TIDAK di modul ini):**
- **Field `status` (lifecycle Aktif/Nonaktif/Cuti/Suspend) milik Employee** — itu tetap daftar tetap terpisah, bukan bagian modul ini (lihat catatan grounding).
- **Perhitungan nominal pesangon/uang kompensasi** — modul ini hanya menyimpan *hak* (berhak/tidak), rumus dan nominal adalah tanggung jawab modul Payroll (rencana mendatang).
- **Perhitungan hak cuti (jumlah hari, dsb.)** — modul ini hanya menyimpan *hak* (berhak/tidak), aturan jumlah hari adalah tanggung jawab modul Cuti (rencana mendatang).
- **Migrasi otomatis lintas-PT** — tiap PT memulai dengan daftar dasar hasil *seeding*, tapi tidak ada mekanisme "copy" otomatis kalau PT baru mau meniru daftar PT lain (dilakukan manual oleh HR PT tersebut).

---

## 3. User Roles & Permissions

| Role | Read | Create | Update | Nonaktifkan |
|------|------|--------|--------|-------------|
| Superadmin / Owner Group Usaha | ✅ (semua PT) | ✅ (semua PT) | ✅ (semua PT) | ✅ (semua PT) |
| Admin Perusahaan (HR PT ybs.) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) | ✅ (hanya PT sendiri) |
| Karyawan (ESS) | ❌ (tidak mengelola; hanya melihat nama status miliknya sendiri lewat profil Employee) | ❌ | ❌ | ❌ |

- **Catatan tambahan:** Tidak ada penghapusan permanen (*hard delete*) — status kepegawaian yang sudah pernah dipakai karyawan hanya bisa dinonaktifkan, tidak dihapus, supaya riwayat karyawan lama tidak rusak.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: HR Menambah Jenis Status Kepegawaian Baru**
- **Given** Admin Perusahaan PT A membutuhkan jenis hubungan kerja baru yang belum ada di daftar standar (misalnya "Outsource").
- **When** Admin mengisi kode dan nama status kepegawaian baru lalu menyimpan.
- **Then** sistem menyimpan status baru tersebut khusus untuk PT A, langsung tersedia sebagai pilihan saat mengisi data karyawan PT A, dan **tidak muncul** di PT lain.

**Skenario 2: Kode Status Kepegawaian Duplikat dalam PT yang Sama**
- **Given** PT A sudah memiliki status kepegawaian dengan kode tertentu (misalnya "CONTRACT").
- **When** Admin PT A mencoba membuat status kepegawaian baru dengan kode yang sama persis.
- **Then** sistem menolak penyimpanan dan menampilkan pesan *"Kode status kepegawaian ini sudah digunakan di perusahaan Anda"*.

**Skenario 3: Menonaktifkan Status Kepegawaian yang Masih Dipakai Karyawan Aktif**
- **Given** ada karyawan aktif yang sedang memakai status kepegawaian "Magang".
- **When** Admin menonaktifkan status "Magang".
- **Then** sistem tetap mengizinkan penonaktifan (karyawan yang sudah memakainya tidak terganggu/tidak error), tetapi status "Magang" hilang dari pilihan dropdown untuk karyawan **baru**.

**Skenario 4: Batas Maksimal Durasi Terlampaui**
- **Given** status kepegawaian "Kontrak" dikonfigurasi punya batas maksimal durasi 60 bulan (sesuai ketentuan ketenagakerjaan yang berlaku untuk perjanjian kerja waktu tertentu).
- **When** HR memperpanjang atau membuat periode kontrak baru untuk seorang karyawan sehingga akumulasi total durasi kontraknya melebihi 60 bulan.
- **Then** sistem menolak penyimpanan dan menampilkan peringatan bahwa batas maksimal durasi untuk status kepegawaian tersebut telah terlampaui.
- *Catatan implementasi:* **belum ada** di kode existing — saat ini batas 60 bulan (bila dicek sama sekali) berupa angka tertanam di kode, bukan dibaca dari data. Ini gap yang harus ditutup modul ini.

**Skenario 5: Status Kepegawaian Wajib Sesuai Perusahaan Karyawan (Scoping)**
- **Given** Admin PT A sedang mengisi/mengubah data karyawan miliknya.
- **When** Admin memilih status kepegawaian dari daftar.
- **Then** sistem hanya menampilkan status kepegawaian milik PT A; jika ada upaya memaksakan ID status kepegawaian milik PT lain (misalnya lewat manipulasi request), sistem menolak dengan pesan ketidakcocokan perusahaan.

**Skenario 6: Validasi Tanggal Akhir Masa Percobaan**
- **Given** status kepegawaian yang dipilih (misalnya "Probation") dikonfigurasi mewajibkan tanggal akhir masa percobaan.
- **When** HR menyimpan data karyawan dengan status tersebut tanpa mengisi tanggal akhir masa percobaan.
- **Then** sistem menolak penyimpanan dan meminta tanggal akhir masa percobaan diisi.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Modul ini hidup di domain baru `internal/employmentstatus` (terpisah dari `internal/employee`, dikonsumsi Employee lewat Application Service, bukan akses tabel langsung — selaras larangan akses lintas-domain).
- **Multi-Entity Scoping (MANDATORY):** Diklasifikasikan sebagai **Company-owned** (`company_id` NOT NULL, tanpa `branch_id` — status kepegawaian berlaku di seluruh cabang dalam satu PT, bukan spesifik satu cabang). **Bukan** "Global master" seperti Bank/Wilayah, karena tiap PT dalam grup usaha berpotensi punya kebijakan jenis hubungan kerja berbeda (justifikasi eksplisit sesuai `scoping-convention.md` §1 — default entity baru adalah Company-owned, "Global master" harus dijustifikasi, bukan dipilih karena kebetulan mirip Bank). Filter scope dienforce lewat `scope.FromContext` pada setiap query baca/tulis.
- **Persistensi / Database:** **Soft delete tidak relevan** — modul ini tidak pernah hapus data, hanya nonaktifkan (`is_active=false`). Perubahan koleksi status kepegawaian per PT bukan operasi "ganti seluruh koleksi", jadi tiap baris dikelola individual (create/update biasa), bukan pola delete-recreate batch.
- **Integritas Data:** Status kepegawaian yang diassign ke seorang karyawan **wajib** berasal dari `company_id` yang sama dengan karyawan tersebut — pelanggaran ditolak tegas (selaras aturan kecocokan `branch_id`/`company_id` yang sudah berlaku di modul Employee).
- **UI (Frontend):** Halaman pengelolaan Status Kepegawaian cukup form sederhana (bukan wizard) karena hanya 1 entity datar, tanpa sub-entity.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Organization @1.0.1** — sumber `company_id` (Company) untuk scope kepemilikan data. Fisik *foreign key* ke tabel `companies` mengikuti jadwal staged yang sama dengan modul Employee (`scoping-convention.md` §4) — kolom & aturan scope dipaku sekarang, penegakan penuh menyusul saat modul Organization selesai dibangun.
- **RBAC @1.0.1** — filter `company_id` di §5 ("Filter scope dienforce lewat `scope.FromContext`") disediakan oleh modul ini (lihat [rbac.md](rbac.md) §5); sampai RBAC diimplementasikan, penegakan berjalan default kosong (mode Owner).

**Consumed by:**
- **Employee @1.0.0** — field `employment_type` pada Employee (PRD Employee §5) berubah dari daftar tetap menjadi referensi ke modul ini (`employment_status_id`). Employee juga mengonsumsi flag `requires_contract_period` dan `requires_probation_end_date` untuk validasi pengisian data karyawan.
- **Leave (rencana mendatang)** — akan membaca flag `has_leave_entitlement` untuk menentukan kelayakan cuti tahunan tanpa perlu menduplikasi aturan berdasarkan nama status.
- **Payroll (rencana mendatang)** — akan membaca flag `has_severance_pay` untuk menentukan apakah proses offboarding memicu perhitungan pesangon/kompensasi (rumus & nominal tetap tanggung jawab Payroll, modul ini hanya menyediakan hak/tidaknya).

**External integrations:** Tidak ada.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Employment Status
- **Aturan Bisnis:** `code` wajib unik **per perusahaan** (bukan unik global — dua PT boleh punya kode yang sama persis, mis. dua-duanya punya "CONTRACT"). *(Pesan error: "Kode status kepegawaian ini sudah digunakan di perusahaan Anda")*. `name` wajib diisi untuk tampilan dropdown. `max_duration_months` opsional — kosong berarti tidak ada batas waktu (dipakai untuk status kepegawaian permanen/tetap). `is_active=false` menyembunyikan status dari pilihan karyawan baru tanpa mengganggu karyawan yang sudah memakainya.

| id | company_id | code | name | is_active | requires_contract_period | requires_probation_end_date | has_leave_entitlement | has_severance_pay | max_duration_months | sort_order |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `es-1` | `co-1` | PERMANENT | Karyawan Tetap | `true` | `false` | `false` | `true` | `true` | `null` | 1 |
| `es-2` | `co-1` | CONTRACT | Karyawan Kontrak | `true` | `true` | `false` | `true` | `true` | 60 | 2 |
| `es-3` | `co-1` | PROBATION | Masa Percobaan | `true` | `true` | `true` | `false` | `false` | 3 | 3 |
| `es-4` | `co-1` | INTERN | Magang | `true` | `false` | `false` | `false` | `false` | `null` | 4 |
| `es-5` | `co-1` | DAILY_WORKER | Harian Lepas | `true` | `false` | `false` | `false` | `false` | `null` | 5 |

### 7.2. Perubahan pada Employee — 1:N (referensi)
- **Aturan Bisnis:** Kolom `employment_type` (daftar tetap) pada Employee digantikan oleh `employment_status_id` (referensi ke tabel di atas). Wajib diisi. Wajib satu `company_id` dengan karyawan yang bersangkutan *(Pesan error: "Status kepegawaian tidak sesuai dengan perusahaan karyawan")*. Bila status kepegawaian terpilih punya `requires_probation_end_date=true`, kolom `probation_end_date` pada Employee menjadi wajib diisi.

| employee_id | employment_status_id (baru, gantikan employment_type lama) |
| :-- | :-- |
| `emp-1` | `es-1` |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Daftar jenis hubungan kerja | `employment_type` di Employee adalah daftar tetap tertanam di kode (`PERMANENT`/`CONTRACT`/`PROBATION`/`INTERN`/`DAILY_WORKER`), sama untuk seluruh PT. | Pindah jadi tabel Master Data per-PT (`employment_status_id`), bisa dikelola tanpa rilis ulang aplikasi. |
| Batas maksimal durasi kontrak | Bila ada pengecekan batas kontrak berjangka, angkanya tertanam di kode. | Baca dari kolom `max_duration_months` per status kepegawaian. |
| Hak cuti & pesangon | Belum ada penanda eksplisit di data — logic (kalau ada) menerka dari nama status. | Tersimpan eksplisit sebagai `has_leave_entitlement`/`has_severance_pay`, siap dikonsumsi modul Cuti/Payroll di masa depan. |
