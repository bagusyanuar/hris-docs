---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26 20:30:00
references_prd: https://github.com/bagusyanuar/hris-docs/blob/main/PRD/auth.md
---

# TRD Backend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **Penerjemahan Bisnis ke Teknis:** Sesuai arahan PRD untuk menciptakan *"Penciptaan sesi pengguna yang aman"* dan *"Perpanjangan masa aktif sesi otomatis"*, TRD ini memetakan alur bisnis tersebut menjadi arsitektur otentikasi berbasis **Stateless JWT** dengan pola *Refresh Token Rotation* menggunakan pengamanan **HttpOnly Secure Cookie**.

## 2. Kontrak API (Endpoints)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Endpoint untuk memvalidasi kredensial (menggunakan algoritma `Bcrypt`) dan menerbitkan JWT *Token Pair*. (Menerjemahkan *PRD Skenario 1*). |
| POST | `/api/v1/auth/refresh` | Endpoint untuk merotasi *access token* dan *refresh token*. (Menerjemahkan *PRD Skenario 4: Perpanjangan Sesi Otomatis*). |

### 2.1 Endpoint Detail: `POST /api/v1/auth/login`
- **Request Payload:**
  ```json
  {
    "email": "user@company.com",
    "password": "mySecurePassword123!"
  }
  ```
- **Request Payload Validation & Error Messages (422 Unprocessable Entity):**
  *(Menerjemahkan aturan ketat dari PRD Skenario 6)*
  - `email`: `required`, `email` format. -> *(Pesan error mutlak: "Format email tidak valid")*
  - `password`: `required`, `min:8`, wajib 1 huruf kapital, 1 angka, 1 karakter khusus. -> *(Pesan error mutlak: "Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial")*
- **Response Payload (200 OK):**
  ```json
  {
    "code": 200,
    "message": "Login successful",
    "data": {
      "access_token": "eyJhbGciOi...",
      "expires_in": 3600,
      "token_type": "Bearer"
    }
  }
  ```
  *(Catatan Teknis: Sesuai Non-Functional Requirements PRD, `refresh_token` tidak dikirim di payload JSON, melainkan diset via header jaringan `Set-Cookie`).*
- **Error Codes:** 
  - `401 Unauthorized` (Pesan: *"Kredensial tidak valid"*) — untuk gagal kredensial.
  - `401 Unauthorized` (Pesan: *"Akun tidak aktif"*) — jika `users.status != active` (Menerjemahkan *PRD Skenario 3*).

### 2.2 Endpoint Detail: `POST /api/v1/auth/refresh`
- **Request Payload:** Kosong. Backend membaca `refresh_token` dari *Cookie* secara otomatis.
- **Response Payload (200 OK):** Menerbitkan `access_token` baru di JSON, dan menimpa *Cookie* yang lama dengan `refresh_token` yang baru (Mekanisme Rotasi/Perpanjangan Sesi).

## 3. Desain Arsitektur DDD

Modul ini diimplementasikan menggunakan tumpukan teknologi **Golang DDD**:

### 3.1 Domain Layer
- **Entitas:** Modul ini beroperasi murni sebagai pemroses (tidak ada tabel Auth mandiri).
- **Abstraksi (Interface):** `TokenGenerator` (Kontrak penciptaan bukti digital/JWT).

### 3.2 Application Layer
- **Use Cases:**
  - `LoginUseCase(email, password)`: Memanggil `user.Repository` untuk mencari profil berdasarkan email. Melakukan *hashing* komparasi via pustaka kriptografi **Bcrypt**. Mengecek secara tegas apakah `status == active` (menerjemahkan gerbang masuk *PRD Skenario 3*). Memanggil `TokenGenerator`.
  - `RefreshUseCase(cookieToken)`: Memvalidasi *refresh token*, mengekstrak entitas identitas, lalu menerbitkan siklus token baru.

### 3.3 Adapter Layer
- **Middleware:** `AuthMiddleware` — Menginspeksi header `Authorization: Bearer <token>`, memvalidasi *signature* rahasia JWT (`HS256`), dan menyuntikkan klaim identitas (`user_id`) ke dalam *request context* (Menerjemahkan amanat PRD: *"Pengecekan hak akses terpusat"*).
- **Handlers:** Gofiber HTTP *handler* bertugas menyusun Cookie dengan atribut tingkat keamanan tertinggi (`HttpOnly=true`, `Secure=true`, `SameSite=Strict`).

## 4. Referensi Skema Database
- Modul ini **hanya mengonsumsi (Read-Only)** data dari tabel `users` (dikelola oleh modul User).
- *Constraint* yang dijaga ketat adalah `users.email` (bersifat unik) dan `users.password` (disimpan dalam bentuk *Hash Bcrypt*, menerjemahkan larangan *plain-text* di PRD).

## 5. Security & Multi-Tenant Scoping
- Sesuai dengan "Non-Functional Requirements" di PRD, sesi pengguna tidak disimpan di *database* fisik (Arsitektur Stateless JWT).
- Bahaya pencurian sesi (pencurian data via celah XSS antarmuka) diatasi dengan merantai *refresh token* ke dalam ranah *HttpOnly Cookie* yang mustahil diakses oleh *script* JavaScript jahat dari klien.
