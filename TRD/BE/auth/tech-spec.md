---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26 13:17:00
references_prd: https://github.com/bagusyanuar/hris-docs/blob/main/PRD/auth.md
---

# TRD Backend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **Ringkasan:** Implementasi gerbang otentikasi (login) dan *refresh token rotation* yang akan melindungi seluruh ekosistem backend HRIS. Modul ini tidak mengelola entitas tabel mandiri, melainkan mengonsumsi entitas User.

## 2. Kontrak API (Endpoints)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Endpoint untuk memvalidasi kredensial dan menerbitkan JWT *Token Pair*. |
| POST | `/api/v1/auth/refresh` | Endpoint untuk memperbarui *access token* yang *expired* menggunakan *refresh token* dari *cookie*. |

### 2.1 Endpoint Detail: `POST /api/v1/auth/login`
- **Request Payload:**
  ```json
  {
    "email": "user@company.com",
    "password": "mySecurePassword123"
  }
  ```
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
  *(Catatan: `refresh_token` disertakan di header `Set-Cookie` secara otomatis).*
- **Error Codes:** 
  - `400 Bad Request` (Invalid JSON)
  - `422 Unprocessable Entity` (Validation failed)
  - `401 Unauthorized` (Invalid credentials / Inactive account)

### 2.2 Endpoint Detail: `POST /api/v1/auth/refresh`
- **Request Payload:** Kosong (token diambil dari `Cookie: refresh_token=...`).
- **Response Payload (200 OK):** Sama persis dengan respons login di atas. *Cookie* baru juga akan di-*set* untuk me-rotasi *refresh token*.
- **Error Codes:** `401 Unauthorized` (Refresh token missing or invalid)

## 3. Desain Arsitektur DDD

### 3.1 Domain Layer
- **Entity/Abstraksi:** `TokenPair` (struct penyimpan Access & Refresh Token), `TokenClaims` (payload token).
- **Abstraksi (Interface):** `TokenGenerator` — Kontrak untuk men-*generate* JWT tanpa terikat implementasi fisik.

### 3.2 Application Layer
- **Use Cases / Service:**
  - `Login(ctx, email, password)`: Melakukan validasi *password* (Bcrypt) via `user.Repository`, **memverifikasi status pengguna (active)**, lalu memanggil `TokenGenerator`.
  - `Refresh(ctx, refreshToken)`: Memvalidasi *refresh token*, mengekstrak klaim, lalu men-*generate* token *pair* baru.

### 3.3 Adapter Layer
- **Token Adapter:** `jwt.go` (Implementasi dari interface `TokenGenerator` menggunakan HMAC `HS256`).
- **Handlers:** `handler.go` untuk *parsing* HTTP request dari Gofiber dan menyusun Cookie *HttpOnly*.

## 4. Referensi Skema Database (DBML)
- **File DBML:** Tidak ada spesifik untuk Auth.
- **Tabel Utama:** Modul ini berinteraksi langsung (baca-saja) ke tabel `users` (diambil melalui domain User). Pengecekan krusial ada di field `users.status`.

## 5. Keamanan & Multi-Tenant Scoping
- **Token Delivery:**
  - `access_token` dikirimkan secara terbuka (di memori sisi klien).
  - `refresh_token` dikirimkan via *Cookie* dengan atribut `HttpOnly=true`, `Secure=true`, dan `SameSite=Strict`.
- **Hiding Error Detail:** Kesalahan validasi *password* atau email tidak terdaftar akan dilempar secara seragam sebagai `401 Invalid credentials` untuk menghindari serangan *User Enumeration*.
