# Data Dictionary: Auth Backend

Dokumen ini mendefinisikan standar tipe data, validasi, dan *magic strings* yang digunakan dalam implementasi kode *Golang* untuk modul Auth.

## 1. Pemetaan Field `status` (Tabel `users`)

Modul Auth menjadi penjaga gawang pertama terhadap lifecycle entitas User. Berdasarkan PRD, hanya `status` tertentu yang boleh login:

| Enum (String) | Lolos Login? | Keterangan |
|---------------|--------------|------------|
| `active`      | ✅ Ya         | Karyawan aktif yang sah. |
| `inactive`    | ❌ Tidak      | Akun dibekukan sementara. |
| `suspended`   | ❌ Tidak      | Terlibat kasus hukum / pelanggaran. |
| `offboarded`  | ❌ Tidak      | Karyawan sudah resign. |

**Aturan Kode:** Pengecekan ini harus di- *hardcode* logikanya di `LoginUseCase`. 

## 2. Format Error Messages (Skenario 6 PRD)

Backend WAJIB mengembalikan JSON spesifik jika payload `POST /api/v1/auth/login` tidak sesuai standar:

| Kasus Kegagalan | HTTP Status | Pesan (JSON Response) |
|-----------------|-------------|-----------------------|
| Email bukan format `@` yang valid | `422 Unprocessable Entity` | `"Format email tidak valid"` |
| Password < 8 karakter | `422 Unprocessable Entity` | `"Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial"` |
| Password tidak ada huruf kapital | `422 Unprocessable Entity` | *"Sda"* |
| Password tidak ada angka | `422 Unprocessable Entity` | *"Sda"* |
| Password tidak ada simbol khusus | `422 Unprocessable Entity` | *"Sda"* |

## 3. JWT Claims Dictionary

Berikut adalah struktur JSON resmi yang di-*encode* ke dalam token JWT (bersama standar klaim RFC):

| Key | Tipe Data Golang | Deskripsi |
|-----|------------------|-----------|
| `sub` | `uuid` | (Subject) Alias untuk `user_id` dari tabel `users`. |
| `role` | `string` | Hak akses, saat ini di-*hardcode* `"employee"`. |
| `type` | `string` | Tipe token, bernilai `"access"` atau `"refresh"`. |
| `exp` | `int64` | Waktu kadaluwarsa (Unix epoch). |
| `iat` | `int64` | Waktu diterbitkan (Unix epoch). |
