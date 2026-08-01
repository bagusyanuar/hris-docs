---
module: User
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: []
consumed_by: [auth@1.0.1, employee@1.0.0, rbac@1.0.1]
---

# Product Requirements: User Module

> **Catatan grounding:** Modul ini sudah terimplementasi sebagian di backend (`internal/user/` — baru layer `domain` dan `adapter`, belum ada `application`/`transport`). Dokumen ini adalah migrasi + standardisasi format dari `hris-backend/docs/PRD/user.md` (v1.0.0) agar selaras aturan *Control Plane* `hris-docs` — isi bisnis inti dipertahankan, ditambah klasifikasi scoping eksplisit (§5) dan `consumed_by` di frontmatter yang belum ada di dokumen legacy.

---

## 1. Tujuan & Dampak (The "Why")

Menjadi sumber tunggal (*Single Source of Truth*) identitas akun sistem — pasangan `email` + kata sandi + status — yang dipakai modul Auth untuk otentikasi dan modul lain untuk gerbang akses. Tanpa modul ini dipisah dari Employee, data karyawan (person) dan data akun login (credential) akan tercampur, padahal keduanya punya siklus hidup berbeda (misalnya akun bisa dinonaktifkan sementara tanpa menghapus data kepegawaian, atau ada akun sistem yang bukan karyawan seperti akun Superadmin).

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Entity akun: `email` (unik), kata sandi (tersimpan terenkripsi), `status` (`active` / `inactive` / `suspended`).
- Pembuatan akun **otomatis** saat proses onboarding Employee disetujui (proses sistem-ke-sistem, bukan formulir pendaftaran terbuka) — memenuhi kontrak yang dijanjikan PRD Employee §6 ("Karyawan wajib memiliki akun/`user_id`", masih di `hris-backend/docs/PRD/employee.md`, belum dimigrasi).
- Perubahan status akun (`active` ↔ `suspended` ↔ `inactive`), dipicu oleh proses dari modul lain (misal offboarding Employee → `inactive`) atau tindakan Admin langsung.
- Penyediaan kontrak baca (cari akun berdasarkan email, cari akun berdasarkan id) untuk dikonsumsi modul Auth.
- Penyimpanan kata sandi **wajib** dalam bentuk terenkripsi satu-arah, tidak pernah teks biasa, di titik manapun proses pembuatan/ubah kata sandi terjadi.

**Out-of-Scope (TIDAK Dikerjakan di modul ini, untuk saat ini):**
- **Pendaftaran mandiri / registrasi publik** — akun hanya dibuat lewat proses sistem (Employee onboarding) atau Admin, bukan formulir publik.
- **RBAC / matriks hak akses** — `role` adalah tanggung jawab bersama Auth + modul Access Control masa depan, bukan atribut inti User.
- **Reset kata sandi via email (lupa password)** — belum ada integrasi email/notifikasi.
- **Ganti kata sandi mandiri oleh pemilik akun** — belum ada fitur ini; saat ini kata sandi hanya bisa diatur ulang lewat proses teknis (skrip seed) atau Admin manual.
- **Audit log percobaan login** — kalau dibutuhkan, jadi tanggung jawab domain Auth atau modul Security terpisah, bukan bagian inti User.
- **Multiple email / login berbasis nomor telepon**, **akun tanpa email (username-only)**.

---

## 3. User Roles & Permissions

| Role | Keterangan Akses |
|------|-------------------|
| Superadmin / HR Admin | Berhak membuat akun sistem di luar jalur Employee onboarding (misal akun admin), mengubah `status` akun manapun (nonaktifkan/aktifkan kembali), tapi **tidak** boleh melihat kata sandi (nilai terenkripsi tidak pernah diekspos ke response API manapun). |
| Sistem (internal, dipicu modul lain) | Modul Employee memicu pembuatan akun otomatis saat onboarding disetujui, dan memicu perubahan status ke `inactive` saat offboarding. Ini bukan aksi manusia langsung, tapi panggilan antar-modul lewat lapisan Application Service masing-masing (bukan akses data langsung lintas modul). |
| Pemilik akun (User biasa) | Untuk saat ini **tidak** ada hak akses langsung ke modul ini (tidak bisa ubah profil/kata sandi sendiri) — hanya jadi subjek yang datanya dikonsumsi Auth saat login. |

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Pembuatan Akun Otomatis saat Onboarding**
- **Given** HR Admin menyetujui data karyawan baru di modul Employee.
- **When** proses onboarding selesai.
- **Then** sistem membuat satu akun baru berstatus `active`, dengan kata sandi awal/sementara (tersimpan terenkripsi), dan mengaitkan akun tersebut ke data karyawan yang bersangkutan.
- *Catatan implementasi:* **belum ada** di kode saat ini — alur pemicu dari modul Employee ke modul User ini belum pernah dipanggil, meskipun field penghubung (`user_id`) sudah ada di sisi entity Employee. Ini gap yang harus ditutup agar kontrak PRD Employee §6 benar-benar terpenuhi, bukan cuma asumsi di dokumen.

**Skenario 2: Duplikasi Email Ditolak**
- **Given** email yang akan dipakai untuk membuat akun sudah terpakai akun lain yang masih aktif.
- **When** proses pembuatan akun dijalankan.
- **Then** sistem menolak, tidak membuat baris baru, dan menampilkan pesan bahwa email tersebut sudah terdaftar.

**Skenario 3: Offboarding Menonaktifkan Akun**
- **Given** karyawan diproses resign/PHK di modul Employee.
- **When** proses offboarding selesai.
- **Then** status akun terkait berubah jadi `inactive`, dan sejak saat itu login lewat modul Auth ditolak (lihat [auth.md](auth.md) §4 Skenario 3).

**Skenario 4: Kata Sandi Selalu Tersimpan Terenkripsi**
- **Given** proses apapun yang menyimpan/mengubah kata sandi (pembuatan akun, reset manual).
- **When** nilai kata sandi disimpan.
- **Then** nilai yang tersimpan **wajib** hasil enkripsi satu-arah yang kuat, tidak pernah nilai teks biasa dari input asli.

**Skenario 5: Pencarian Akun Tidak Ditemukan**
- **Given** pencarian akun berdasarkan email atau id yang tidak ada (atau sudah dihapus-lunak).
- **When** pencarian dijalankan.
- **Then** sistem memberi tahu secara eksplisit bahwa akun tidak ditemukan (bukan diam-diam mengembalikan kosong tanpa penjelasan).
- *Catatan implementasi:* kontrak ini **sudah** terimplementasi dengan benar di kode saat ini.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Entity `User` hidup di `internal/user/domain/`, pure business logic tanpa detail penyimpanan — pertahankan pemisahan ini. Representasi database terpisah di `internal/user/adapter/models/` dengan mapper konversi dua arah.
- **Multi-Entity Scoping (MANDATORY) — Pengecualian Eksplisit:** `User` **tidak** punya kolom `company_id`/`branch_id`, dan ini **disengaja**, bukan default malas. Pencarian akun (berdasarkan email, saat login) **wajib** bisa jalan sebelum sistem tahu PT/cabang mana yang bersangkutan — konteks Company/Branch baru diketahui **setelah** login berhasil, lewat data Employee yang terhubung ke akun tersebut. Menambahkan `company_id` di modul ini akan merusak alur pencarian saat login. Ini beda alasan dari "Global Master" (Bank/Region — datanya identik lintas PT); `User` justru data per-individu, cuma kebetulan sama-sama tidak boleh terikat scope PT/cabang di titik pencarian awal.
- **Gap Pembuatan ID:** Konvensi project mewajibkan entity auto-generate ID unik sendiri kalau belum diisi. Konstruktor `User` saat ini justru **menolak** kalau id kosong — tidak konsisten dengan pola modul lain (Employee, Organization). Wajib diperbaiki saat fitur pembuatan akun (Skenario 1) diimplementasikan.
- **Persistensi:** Kontrak baca (cari berdasarkan email/id) sudah ada; kontrak tulis baru mencakup ubah status. Method pembuatan akun yang akan ditambahkan wajib menerjemahkan pelanggaran keunikan email jadi pesan yang jelas ke pemanggil (Skenario 2), bukan membocorkan detail teknis penyimpanan data.
- **Komunikasi Lintas Modul:** Pemicu dari Employee ke User (pembuatan akun, perubahan status) wajib lewat lapisan Application Service modul User, bukan akses langsung ke data internalnya dari modul Employee.
- **Penghapusan Data:** Hapus-lunak, konsisten dengan pola Employee — jangan hapus permanen akun (jejak audit login harus tetap bisa ditelusuri).

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- Tidak ada. User adalah root/foundational context — tidak butuh data modul lain untuk berfungsi.

**Consumed by:**
- **Auth @1.0.1** — mencari akun berdasarkan email/id, dan membaca `status` sebagai gerbang login (lihat [auth.md](auth.md) §6).
- **Employee (belum dimigrasi ke `hris-docs`)** — Employee butuh User untuk pembuatan akun saat onboarding dan menonaktifkan akun saat offboarding. Arah panggilan: Employee memanggil User, bukan sebaliknya.
- **RBAC @1.0.1** — penetapan Role ke user mengikat ke identitas akun dari modul ini (lihat [rbac.md](rbac.md) §7.4).

**External integrations:** Tidak ada saat ini. Kalau nanti ada alur lupa kata sandi, akan butuh integrasi email/notifikasi (di luar cakupan dokumen ini).

---

## 7. Data Schema & Business Rules

### 7.1. User (Akun Sistem)
- **Aturan Bisnis:** `email` wajib unik. `status` hanya boleh salah satu dari `active`, `inactive`, `suspended`. Kata sandi tidak pernah diekspos di response API manapun. Satu email = satu akun; satu akun bisa dipakai lintas konteks (milik Employee ATAU akun non-employee seperti Superadmin).

| id | email | status | created_at |
| :-- | :-- | :-- | :-- |
| `usr-1` | `admin@hris.local` | `active` | `2026-01-10 08:00:00` |
| `usr-2` | `employee@hris.local` | `active` | `2026-01-10 08:00:00` |
| `usr-3` | `resigned.user@hris.local` | `inactive` | `2025-11-02 09:15:00` |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Pembuatan akun otomatis saat onboarding | Belum pernah dipanggil dari modul Employee, meski field penghubung sudah ada di entity Employee. | Perlu diimplementasi agar kontrak PRD Employee §6 benar-benar terpenuhi (Skenario 1). |
| Auto-generate id saat kosong | Konstruktor `User` menolak input kalau id kosong, beda dari pola modul lain. | Selaraskan dengan pola Employee/Organization saat fitur pembuatan akun dibangun. |
| Method pembuatan akun di kontrak data | Kontrak baca-tulis saat ini baru: cari berdasarkan email, cari berdasarkan id, ubah status. Belum ada method pembuatan akun baru. | Tambah saat Skenario 1 diimplementasi, ikut aturan penerjemahan error keunikan email (Skenario 2). |
