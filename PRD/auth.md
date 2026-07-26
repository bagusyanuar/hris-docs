---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26 13:17:00
depends_on: [user@1.0.0]
consumed_by: [employee@1.0.0, organization@1.0.0]
---

# Product Requirements: Auth Module

> **Catatan grounding:** Modul ini sudah terimplementasi di backend. PRD ini adalah standardisasi dokumentasi bisnis dari arsitektur *existing* agar selaras dengan aturan *Control Plane* `hris-docs`.

---

## 1. Tujuan & Dampak (The "Why")

Menyediakan satu pintu masuk (*Single Point of Entry*) otentikasi untuk seluruh sistem HRIS, menggantikan kebutuhan tiap modul membuat mekanisme login sendiri-sendiri. Modul ini menjamin hanya pengguna dengan kredensial valid dan akun aktif yang bisa mengakses API, sekaligus menjadi lapisan pertahanan pertama (*perimeter security*) sebelum *request* menyentuh domain bisnis lain (seperti Employee, Organization, dll).

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Login menggunakan `email` + `password` (dicocokkan dengan hash `bcrypt` di tabel `users`).
- Penerbitan token pasangan (*Token Pair*): `access_token` (umur pendek, dikirim via JSON response) dan `refresh_token` (umur panjang, diset via **HttpOnly Secure Cookie**).
- Endpoint refresh token dengan pola **rotation** (tiap refresh berhasil, refresh token lama diganti baru).
- Middleware `AuthProtected` untuk memvalidasi `access_token` (`Authorization: Bearer <token>`) pada endpoint yang butuh proteksi, dan menyisipkan `userID` + `role` ke context request.
- Validasi status akun (`users.status`) — akun yang tidak `active` (misalnya `inactive`, `suspended`) **wajib** ditolak saat login, meskipun kredensial benar. Ini adalah kontrak yang dijanjikan ke modul Employee (offboarding memblokir akses login).

**Out-of-Scope (TIDAK di modul ini):**
- **Registrasi akun baru (Sign Up)** — pembuatan baris data di `users` adalah tanggung jawab proses onboarding Employee, bukan ranah Auth.
- **RBAC granular / permission matrix** — token membawa klaim `role`, tapi otorisasi spesifik berbasis role (misal: "hanya HR Manager boleh akses endpoint X") belum diimplementasikan.
- **Logout server-side / token revocation** — karena token bersifat *stateless JWT* tanpa token store/blacklist, tidak ada mekanisme pembatalan token sebelum masa berlakunya habis. Endpoint logout (jika ada) hanya menghapus cookie di sisi *client*.
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
- **Given** pengguna dengan akun `status = active` memasukkan email dan password yang benar.
- **When** request `POST /api/v1/auth/login` dikirim.
- **Then** sistem merespon `200 OK` berisi `access_token`, `expires_in`, `token_type`, dan menyisipkan `refresh_token` sebagai cookie `HttpOnly`, `Secure`, `SameSite=Strict`.

**Skenario 2: Login Gagal — Kredensial Salah**
- **Given** email tidak terdaftar, atau email terdaftar tapi password salah.
- **When** request login dikirim.
- **Then** sistem merespon `401 Unauthorized` dengan pesan generik *"Invalid credentials"* (tidak membedakan pesan antara email salah atau password salah untuk mencegah *user enumeration*).

**Skenario 3: Login Ditolak — Akun Tidak Aktif**
- **Given** akun dengan kredensial benar tapi `status != active` (mis. offboard).
- **When** request login dikirim.
- **Then** sistem menolak dengan `401 Unauthorized`, tanpa menerbitkan token.
- *Catatan implementasi:* Pengecekan status saat ini masih menjadi *gap* di backend (`application/auth/service.go` belum mengecek `u.Status()`). **Ini harus segera ditutup** karena merupakan kontrak dengan PRD Employee.

**Skenario 4: Refresh Token Rotation**
- **Given** client memiliki `refresh_token` valid di cookie.
- **When** request `POST /api/v1/auth/refresh` dikirim.
- **Then** sistem menerbitkan `access_token` baru dan `refresh_token` baru (merotasi/mengganti cookie lama).

**Skenario 5: Perlindungan Endpoint (Middleware)**
- **Given** request ke endpoint terproteksi dikirim tanpa token, ATAU dengan token yang kedaluwarsa/invalid.
- **When** request tersebut menyentuh server.
- **Then** sistem merespon `401 Unauthorized`, dan request tidak diteruskan ke *handler* bisnis.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design:** Domain Layer Auth hanya menangani abstraksi token (`TokenGenerator`, `TokenPair`). Verifikasi user dilakukan di Application Layer dengan memanggil `user.Repository` (jangan mem-bypass kueri langsung ke DB).
- **Hybrid Token Storage (Frontend Constraint):** `access_token` dikirim via JSON body (FE menyimpannya di *memory*, BUKAN *localStorage* untuk cegah XSS), sedangkan `refresh_token` **wajib** dikirim sebagai HttpOnly Secure Cookie.
- **Stateless JWT:** Token ditandatangani menggunakan rahasia `HS256`. Tidak ada token store di database.
- **Keamanan Hashing:** Kata sandi wajib dibandingkan menggunakan fungsi *Bcrypt* (`bcrypt.CompareHashAndPassword`).

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **[User @1.0.0]** — Modul Auth mengonsumsi `user.Repository` (terutama `FindByEmail` dan `FindByID`) untuk memverifikasi `id`, `password` (hash), dan `status` dari tabel `users`.

**Consumed by:**
- **[Employee @1.0.0]** — Mengandalkan mekanisme blokir login Auth saat proses *offboarding* (Kriteria Penerimaan Skenario 3).
- **[Semua Modul Terproteksi]** — Organisasi, Employee, dan semua API masa depan bergantung mutlak pada *middleware* `AuthProtected`.

---

## 7. Data Schema & Business Rules (Database Map)

Auth **tidak memiliki tabel fisik sendiri** — modul ini merupakan konsumen mutlak dari tabel `users` (milik Modul User) dan berperan sebagai penerbit JWT stateless yang tidak disimpan ke *database*.

### 7.1. `users` (Dikonsumsi dari Modul User)
Berikut adalah properti entitas User yang diawasi ketat oleh proses otentikasi:

| Field | Aturan Bisnis |
| :-- | :-- |
| `id` | Dimasukkan sebagai Klaim `user_id` di dalam payload JWT. |
| `email` | Bersifat **unique**. Menjadi kredensial utama saat proses *login*. |
| `password` | Berbentuk hash `bcrypt`, wajib dicocokkan sebelum token diterbitkan. |
| `status` | Gerbang masuk. Hanya pengguna berstatus `active` yang lolos verifikasi. |

### 7.2. Struktur JWT Payload (Bukan Tabel Fisik)
Data yang disisipkan ke dalam token (klaim):

| Field | Tipe | Keterangan |
| :-- | :-- | :-- |
| `user_id` | string | ID unik dari tabel `users`. |
| `role` | string | Saat ini *hardcoded* `"employee"`. |
| `type` | string | Nilainya `"access"` atau `"refresh"` untuk mencegah penyalahgunaan tipe token. |
| `exp` | timestamp | Masa kedaluwarsa token. |

---

## 8. Ringkasan Gap (Kondisi Kode vs PRD Target)

| Area | Status kode backend sekarang | Target perbaikan |
|------|------------------------------|------------------|
| Validasi Akun Aktif | `application/auth/service.go` hanya memverifikasi *password*, tidak mempedulikan field `status`. | Wajib menolak login jika `status != active` sesuai dengan Skenario 3. |
