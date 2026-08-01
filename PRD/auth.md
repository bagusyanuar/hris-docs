---
module: Auth
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [user@1.0.1]
consumed_by: [employee@1.0.1, organization@1.0.1, rbac@1.0.1]
---

# Product Requirements: Auth Module

> **Catatan grounding:** Modul ini sudah terimplementasi di backend. PRD ini adalah standardisasi dokumentasi bisnis dari arsitektur *existing* agar selaras dengan aturan *Control Plane* `hris-docs`.

---

## 1. Tujuan & Dampak (The "Why")

Menyediakan satu pintu masuk (*Single Point of Entry*) otentikasi untuk seluruh sistem HRIS, menggantikan kebutuhan tiap modul membuat mekanisme login sendiri-sendiri. Modul ini menjamin hanya pengguna dengan kredensial valid dan akun aktif yang bisa mengakses API, sekaligus menjadi lapisan pertahanan pertama (*perimeter security*) sebelum *request* menyentuh domain bisnis lain (seperti Employee, Organization, dll).

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Hak akses (Login) menggunakan kombinasi `email` dan `password` yang dikelola secara aman oleh sistem.
- Penciptaan sesi pengguna (*User Session*) setelah berhasil masuk.
- Perpanjangan masa aktif sesi secara otomatis selama pengguna masih aktif menggunakan sistem.
- Pengecekan hak akses terpusat (*Access Control*) untuk melindungi seluruh halaman dan data internal HRIS dari pengguna tanpa izin.
- Validasi status akun — akun yang tidak berstatus aktif (misalnya *inactive*, *suspended*) **wajib** ditolak saat login, meskipun kredensial yang dimasukkan benar. (Ini adalah kontrak operasional yang menjamin mantan pegawai tidak bisa mengakses sistem setelah proses offboarding).

**Out-of-Scope (TIDAK di modul ini):**
- **Registrasi akun baru (Sign Up)** — pembuatan baris data di `users` adalah tanggung jawab proses onboarding Employee, bukan ranah Auth.
- **Otorisasi spesifik (RBAC/Permission Matrix)** — Hak akses khusus per fitur (misal: "hanya HR Manager boleh melihat gaji") belum ditangani di tahap ini, hanya identifikasi peran (*role*).
- **Pembatalan Sesi Jarak Jauh (Remote Logout)** — Saat ini, sistem belum memiliki kemampuan untuk memutus sesi secara paksa dari server sebelum waktu sesi habis (kecuali lewat penghapusan data di perangkat pengguna).
- **Reset password / lupa password** — belum ada alur email verifikasi.
- **Account lockout / brute-force protection** — belum ada pembatasan batas percobaan login (Rate Limiting).
- **Multi-Factor Authentication (MFA) & Social Login (SSO)**.

---

## 3. User Roles & Permissions

Modul Auth **tidak** mendefinisikan role bisnis sendiri — ia hanya bertindak sebagai **pembawa** (carrier) klaim `role` yang sumber datanya dari modul lain (saat ini *hardcoded* `"employee"` sampai fitur RBAC matang).

| Role | Keterangan Akses Otentikasi |
|------|-----------------------------|
| **Pengguna Aktif** | Selama `status = active` dan kredensial valid, berhak mendapat `access_token` dan `refresh_token`. |
| **Pengguna Nonaktif** | Pengguna berstatus *suspended/inactive* akan **ditolak** login sepenuhnya tanpa pengecualian role. |

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Login Berhasil**
- **Given** pengguna dengan akun berstatus aktif memasukkan kredensial (email dan password) yang benar.
- **When** pengguna menekan tombol Masuk (Login).
- **Then** sistem memberikan hak akses, menciptakan sesi aktif, dan mengarahkan pengguna ke halaman *Dashboard* utama.

**Skenario 2: Login Gagal — Kredensial Salah**
- **Given** email tidak terdaftar, ATAU email terdaftar tetapi password salah.
- **When** pengguna mencoba masuk.
- **Then** sistem menolak akses dan menampilkan pesan umum *"Kredensial tidak valid"* (tidak memberi petunjuk spesifik apakah email atau sandi yang salah, demi keamanan).

**Skenario 3: Login Ditolak — Akun Tidak Aktif**
- **Given** akun pengguna sudah tidak aktif (misal: pegawai telah *offboard*), tetapi memasukkan kredensial yang benar.
- **When** pengguna mencoba masuk.
- **Then** sistem menolak akses, tidak memberikan sesi, dan menampilkan pesan penolakan.
- *Catatan implementasi:* Pengecekan status saat ini masih menjadi *gap* di kode existing. Ini harus segera ditutup karena merupakan kontrak fungsional dengan modul Employee.

**Skenario 4: Perpanjangan Sesi Otomatis**
- **Given** pengguna sedang menggunakan sistem dan memiliki sesi latar belakang yang masih aktif.
- **When** sesi utama hampir habis masa berlakunya.
- **Then** sistem akan secara otomatis memperbarui sesi tersebut tanpa mengganggu aktivitas pengguna di layar.

**Skenario 5: Perlindungan Halaman (Access Control)**
- **Given** pengguna (atau pihak tak dikenal) mencoba mengakses halaman atau fitur internal HRIS tanpa memiliki sesi yang sah (belum login atau sesi telah habis).
- **When** sistem menerima permintaan akses tersebut.
- **Then** sistem langsung memblokir akses dan mengarahkan paksa pengguna kembali ke halaman Login.

**Skenario 6: Login Ditolak — Validasi Format Input Gagal**
- **Given** pengguna mencoba masuk.
- **When** format email tidak sesuai standar ATAU password tidak memenuhi kebijakan minimum keamanan (minimal 8 karakter, mengandung 1 huruf kapital, 1 angka, dan 1 karakter spesial).
- **Then** sistem menolak akses dan langsung menampilkan pesan peringatan spesifik kepada pengguna mengenai kesalahan format tersebut (sebelum mencocokkan data lebih jauh).
---

## 5. Non-Functional Requirements (Keamanan & Performa)

- **Keamanan Sandi:** Kata sandi pengguna tidak boleh disimpan dalam bentuk teks biasa (*plain-text*) di dalam penyimpanan data manapun. Sistem harus menggunakan algoritma perlindungan searah yang kuat.
- **Manajemen Sesi:** Mekanisme penyimpanan sesi di perangkat pengguna harus kebal dari pencurian data lewat celah keamanan antarmuka (misal: *Cross-Site Scripting* / XSS).
- **Arsitektur Tanpa Jejak (Stateless):** Sistem tidak memerlukan tempat penyimpanan sesi terpusat di *database*, melainkan menggunakan bukti digital yang dapat diverifikasi secara independen oleh sistem.

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **[User @1.0.1]** — Modul Auth mengonsumsi `user.Repository` (terutama `FindByEmail` dan `FindByID`) untuk memverifikasi `id`, `password` (hash), dan `status` dari tabel `users`.

**Consumed by:**
- **[Employee @1.0.0]** — Mengandalkan mekanisme blokir login Auth saat proses *offboarding* (Kriteria Penerimaan Skenario 3).
- **[Semua Modul Terproteksi]** — Organisasi, Employee, dan semua API masa depan bergantung mutlak pada *middleware* `AuthProtected`.
- **[RBAC @1.0.1]** — RBAC berjalan setelah identitas user diverifikasi Auth, mengasumsikan `user_id` yang sudah tervalidasi dari lapisan ini (lihat [rbac.md](rbac.md) §6).

---

## 7. Data Schema & Business Rules

Auth **tidak memiliki tabel entitas sendiri** — modul ini merupakan konsumen mutlak dari profil Pengguna (milik Modul User) dan hanya berperan sebagai penerbit akses masuk.

### 7.1. Konsumsi Entitas Pengguna
Berikut adalah data pengguna yang diperiksa secara ketat oleh sistem saat proses masuk:

| Field | Aturan Bisnis |
| :-- | :-- |
| `id` | Menjadi penanda identitas unik pengguna pada sesi yang diterbitkan. |
| `email` | Bersifat **unik**. Wajib berformat *email* yang sah. *(Pesan error: "Format email tidak valid")*. Menjadi kredensial utama yang diinput pengguna. |
| `password` | Dijaga kerahasiaannya. **Validasi Pembuatan Sandi:** Wajib minimal 8 karakter, mengandung minimal 1 huruf kapital, 1 angka, dan 1 karakter spesial. *(Pesan error: "Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial")*. |
| `status` | Gerbang mutlak. Hanya pengguna berstatus `active` yang diizinkan untuk melewati verifikasi akses. |

---

## 8. Ringkasan Gap (Kondisi Kode vs PRD Target)

| Area | Status kode backend sekarang | Target perbaikan |
|------|------------------------------|------------------|
| Validasi Akun Aktif | `application/auth/service.go` hanya memverifikasi *password*, tidak mempedulikan field `status`. | Wajib menolak login jika `status != active` sesuai dengan Skenario 3. |
