---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26
references_prd: https://github.com/bagusyanuar/hris-docs/blob/main/PRD/auth.md
---

# TRD Backend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **Penerjemahan Bisnis ke Teknis:** Menerjemahkan kebutuhan "Penciptaan sesi aman" dan "Perpanjangan masa aktif sesi" menjadi arsitektur otentikasi berbasis **Stateless JWT** dengan pengamanan **HttpOnly Secure Cookie**.

## 2. API Contracts
| Method | Endpoint | Business Intent |
|--------|----------|-----------------|
| POST | `/api/v1/auth/login` | Memvalidasi kredensial pengguna dan menerbitkan JWT Token Pair jika berhasil. |
| POST | `/api/v1/auth/refresh` | Merotasi access token secara otomatis di latar belakang untuk memperpanjang sesi. |

> **Catatan API Contract:** Detail skema *Request/Response* JSON, tipe data, aturan validasi ketat, dan daftar lengkap *HTTP Status Code* dikelola sepenuhnya melalui *Swagger/OpenAPI*. 
> Tim BE **wajib** mengekspor file `swagger.json` (atau `.yaml`) dan menyimpannya ke folder `hris-docs/API_CONTRACTS/` segera setelah pengembangan *endpoint* selesai dibangun.

*(Catatan: `refresh_token` tidak dikirim di JSON body, melainkan diset eksklusif via header jaringan `Set-Cookie` oleh Backend).*

## 3. Desain Arsitektur DDD

### 3.1 Domain Layer
- **Entitas:** Modul ini beroperasi murni sebagai pemroses (tidak ada entitas Auth mandiri).
- **Abstraksi (Interface):** `TokenGenerator` (Kontrak penciptaan JWT).

### 3.2 Application Layer
- **Use Cases:**
  - `LoginUseCase(email, password)`: Memanggil `user.Repository` (`FindByEmail`). Melakukan komparasi *hash* via **Bcrypt**. Memverifikasi `status == active`. Memanggil `TokenGenerator`.
  - `RefreshUseCase(cookieToken)`: Memvalidasi *refresh token*, mengekstrak *user_id*, lalu menerbitkan siklus token baru.

### 3.3 Adapter Layer
- **Middleware:** `AuthMiddleware` — Menginspeksi header `Authorization: Bearer <token>`, memvalidasi *signature* `HS256`, dan menyuntikkan `user_id` ke *request context*.
- **Handlers:** Menyusun respons dan mengeset atribut `HttpOnly=true`, `Secure=true`, `SameSite=Strict` pada Cookie.

## 4. Referensi Skema Database
- Modul ini **hanya mengonsumsi (Read-Only)** dari tabel `users` (dikelola oleh modul User).
- Modul melakukan pencarian berdasarkan `users.email` (unik).

## 5. Security & Multi-Tenant Scoping
- Sesi pengguna tidak disimpan di *database* fisik (Stateless JWT).
- Bahaya pencurian sesi (XSS) diatasi dengan merantai *refresh token* ke dalam ranah *HttpOnly Cookie* yang tidak bisa diakses JavaScript.
