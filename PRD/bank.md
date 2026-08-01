---
module: Bank
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-08-01 19:15:00
depends_on: []
consumed_by: [employee@1.0.0, organization@planned, payroll@planned]
---

# Product Requirements: Bank Module

> **Catatan grounding:** Modul ini belum terimplementasi di kode (`internal/bank` belum ada). PRD ini adalah rancangan awal (Docs & Design First) sebelum implementasi backend dimulai.

---

## 1. Tujuan & Dampak (The "Why")

Setiap kali karyawan atau perusahaan perlu mendaftarkan rekening bank (misalnya untuk pencairan gaji), sistem butuh daftar bank yang akurat dan konsisten — bukan input teks bebas yang rawan salah ketik nama bank. Modul Bank menyediakan satu daftar referensi bank yang bisa dipakai berulang oleh fitur pendaftaran rekening gaji karyawan (Payroll) maupun pencatatan rekening perusahaan, sehingga data rekening di seluruh sistem konsisten dan siap diintegrasikan dengan proses pencairan dana (*disbursement*) di masa depan.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Penyediaan daftar bank yang beroperasi di Indonesia (dan internasional bila diperlukan) sebagai pilihan (dropdown) di formulir mana pun yang membutuhkan data bank.
- Pencarian bank berdasarkan nama atau kode.
- Penandaan status aktif/tidak aktif suatu bank (mengantisipasi bank tutup atau merger).

**Out-of-Scope (TIDAK di modul ini):**
- **Validasi nomor rekening secara real-time** ke pihak bank (*Account Validation API* / Payment Gateway) — modul ini hanya menyediakan daftar identitas bank, bukan verifikasi nomor rekening.
- **Proses pencairan dana (*disbursement*)** — itu tanggung jawab modul Payroll di masa depan.
- **Pengelolaan data lewat antarmuka Admin biasa oleh HR** — data bank dikelola murni lewat *Seeder* saat *deployment* atau oleh Superadmin, bukan operasional harian HR per-PT.

---

## 3. User Roles & Permissions

| Role | Read | Create | Update | Nonaktifkan |
|------|------|--------|--------|-------------|
| Superadmin | ✅ | ✅ | ✅ | ✅ |
| Admin Perusahaan (HR) | ✅ (hanya melihat, untuk dropdown) | ❌ | ❌ | ❌ |
| Karyawan (ESS) | ✅ (hanya melihat, untuk dropdown) | ❌ | ❌ | ❌ |

- **Catatan tambahan:** Modul ini bersifat *read-only* bagi seluruh pengguna operasional (HR maupun Karyawan). Penambahan/perubahan data bank murni jalur teknis (*Seeder*) atau kewenangan Superadmin, bukan alur bisnis harian.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Menampilkan Daftar Bank Aktif**
- **Given** pengguna sedang mengisi formulir yang membutuhkan pemilihan bank (misalnya pendaftaran rekening gaji karyawan).
- **When** pengguna membuka pilihan (dropdown) Bank.
- **Then** sistem menampilkan seluruh bank berstatus aktif, tanpa dibatasi berdasarkan perusahaan (PT) atau cabang mana pun.

**Skenario 2: Pencarian Bank**
- **Given** pengguna mengetik kata kunci nama atau kode bank pada kolom pencarian.
- **When** pencarian dijalankan.
- **Then** sistem hanya menampilkan bank yang nama atau kodenya cocok dengan kata kunci tersebut.

**Skenario 3: Bank Tutup/Merger Dinonaktifkan**
- **Given** sebuah bank sudah tutup atau merger dengan bank lain (misalnya kasus Bank Syariah Indonesia hasil merger beberapa bank syariah).
- **When** Superadmin menonaktifkan entitas bank tersebut.
- **Then** bank tersebut tidak lagi muncul di pilihan dropdown untuk pendaftaran rekening baru, tetapi data karyawan yang sudah lebih dulu memakai bank tersebut (rekening lama) tetap tersimpan dan valid tanpa error.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Entitas Bank ditempatkan di domain tersendiri `internal/bank` (dapat digabung ke domain besar `internal/reference` bila disepakati di masa depan).
- **Multi-Entity Scoping (MANDATORY):** Diklasifikasikan sebagai **Global Master** (tanpa `company_id`/`branch_id`) — **justifikasi eksplisit** sesuai `scoping-convention.md` §1: identitas bank (kode BI/RTGS, SWIFT code) adalah fakta nasional/internasional yang identik untuk seluruh PT dalam grup usaha, bukan kebijakan yang berbeda per perusahaan.
- **Persistensi / Database:** Tidak ada penghapusan permanen (*hard delete*) — bank yang tutup/merger hanya diberi tanda tidak aktif, supaya data rekening karyawan lama yang mengacu ke bank tersebut tidak rusak.
- **UI (Frontend):** Cukup komponen dropdown dengan pencarian (*searchable select*), tanpa kebutuhan halaman pengelolaan CRUD khusus untuk HR.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- Tidak ada. Modul ini berdiri sendiri (*standalone reference data*).

**Consumed by:**
- **Employee @1.0.0** — pendaftaran rekening gaji karyawan mereferensikan entitas Bank ini.
- **Organization (rencana mendatang)** — pencatatan rekening perusahaan (jika ada) akan mereferensikan entitas Bank yang sama; belum ada kolom terkait di skema Organization saat ini (PRD Organization §7.1).
- **Payroll (rencana mendatang)** — proses pencairan gaji akan membaca identitas bank tujuan transfer dari modul ini.

**External integrations:** Tidak ada saat ini. Kolom `swift_code` disiapkan sebagai bekal integrasi *Payment Gateway*/*Disbursement* di masa depan, belum ada koneksi aktif ke pihak ketiga manapun.

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Bank
- **Aturan Bisnis:** `bank_code` (Kode BI/RTGS) unik, opsional untuk bank yang belum punya kode nasional. `swift_code` opsional, dipakai khusus untuk transfer internasional. `is_active=false` menyembunyikan bank dari pilihan baru tanpa menghapus data historis.

| id | name | bank_code | swift_code | is_active |
| :-- | :-- | :-- | :-- | :-- |
| `bank-1` | Bank Central Asia (BCA) | `014` | `CENAIDJA` | `true` |
| `bank-2` | Bank Mandiri | `008` | `BMRIIDJA` | `true` |
