# TRD Extension: Data Dictionary (Backend Auth)

Dokumen ini berisi standar pesan *error* dan *magic strings* yang digunakan dalam modul.

## 1. Magic Strings / Enums
- `Authorization: Bearer <token>`: Format standar header HTTP untuk *access token*.
- `HttpOnly`, `Secure`, `SameSite=Strict`: Atribut wajib untuk pengaturan Cookie `refresh_token`.
- `active`: Status pengguna (dari modul Employee/User) yang menjadi syarat mutlak kelulusan *login*.

## 2. Error Message Mappings (Sesuai PRD)
Backend **wajib** mengembalikan pesan *error* ini secara presisi pada JSON respons:

- **422 Unprocessable Entity:**
  - Jika email salah format: `"Format email tidak valid"`
  - Jika password gagal validasi kompleksitas (min 8, huruf kapital, angka, simbol): `"Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial"`
- **401 Unauthorized:**
  - Jika email/password salah: `"Kredensial tidak valid"`
  - Jika `status != active`: `"Akun tidak aktif"`
