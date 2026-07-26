# User Stories: Auth Module (Backend)

Dokumen ini memecah spesifikasi teknis dari `tech-spec.md` menjadi tiket kerja (*actionable tasks*) untuk tim Golang Backend.

## 1. Setup Infrastruktur JWT
- **Sebagai** Backend Engineer,
- **Saya ingin** mengimplementasikan fungsi kriptografi `HS256` untuk men-generate JWT (Access & Refresh),
- **Sehingga** sistem dapat menerbitkan token yang kebal dari pemalsuan.
- **Kriteria Penerimaan (AC):**
  - Buat interface `TokenGenerator`.
  - Buat implementasinya di layer *Adapter* menggunakan *library* standar JWT.
  - Membutuhkan kunci rahasia dari *environment variable*.

## 2. Endpoint Login & Validasi Bcrypt
- **Sebagai** pengguna yang sah,
- **Saya ingin** API `/api/v1/auth/login` memvalidasi kredensial email dan password saya,
- **Sehingga** saya bisa mendapatkan sesi (*Token Pair*).
- **Kriteria Penerimaan (AC):**
  - Harus menerapkan validasi Payload (Format Email, dan Regex Password).
  - Melempar `422 Unprocessable Entity` jika payload tidak valid (sesuai *Data Dictionary*).
  - Harus mengecek kecocokan *password* menggunakan `bcrypt.CompareHashAndPassword`.
  - Wajib menolak *user* dengan pesan "Akun tidak aktif" jika field DB `status != active`.
  - Merespon dengan `200 OK`, JSON berisi `access_token`, dan Header `Set-Cookie` berisi `refresh_token` (*HttpOnly, Secure*).

## 3. Auth Middleware
- **Sebagai** sistem keamanan internal,
- **Saya ingin** sebuah *Middleware* fiber yang mampu membaca header `Authorization: Bearer <token>`,
- **Sehingga** saya bisa melarang pengguna tak dikenal masuk ke endpoint internal.
- **Kriteria Penerimaan (AC):**
  - Parsing token dan validasi *signature*.
  - Menyuntikkan klaim `user_id` ke dalam Fiber Context.
  - Melempar `401 Unauthorized` jika token kadaluwarsa atau hilang.

## 4. Endpoint Refresh Token
- **Sebagai** pengguna,
- **Saya ingin** sesi saya diperpanjang otomatis di belakang layar,
- **Sehingga** saya tidak perlu login ulang berulang kali.
- **Kriteria Penerimaan (AC):**
  - Buat endpoint `/api/v1/auth/refresh`.
  - Baca nilai `refresh_token` khusus dari *Cookie*.
  - Jika valid, terbitkan JSON berisi `access_token` baru, dan timpa Cookie lama dengan `refresh_token` yang baru (Rotasi).
