# TRD Extension: User Stories (Backend Auth)

Dokumen ini memecah arsitektur `tech-spec.md` menjadi tiket-tiket kerja yang siap dieksekusi.

## 1. Persiapan Infrastruktur Otentikasi
- **Task:** Konfigurasi environment variables untuk rahasia JWT (e.g., `JWT_SECRET`, `JWT_EXPIRES_IN`).
- **Task:** Pembuatan *interface* `TokenGenerator` di Domain Layer dan implementasinya menggunakan library JWT resmi Golang di Adapter Layer.
- **Task:** Implementasi komparasi *password* menggunakan library **Bcrypt**.

## 2. Implementasi Endpoint Login
- **Task:** Buat `LoginUseCase` di Application Layer yang mengonsumsi `user.Repository`. Wajib memverifikasi bahwa akun berstatus `active`!
- **Task:** Buat REST Handler untuk `POST /api/v1/auth/login`. Tangani *payload validation* sesuai Swagger.
- **Task:** Handler wajib mengeset `refresh_token` ke dalam *HttpOnly Cookie*.

## 3. Implementasi Endpoint Refresh Token
- **Task:** Buat `RefreshUseCase` yang bertugas memvalidasi *refresh token* lama dan menerbitkan *Token Pair* baru.
- **Task:** Buat REST Handler untuk `POST /api/v1/auth/refresh` yang membaca *Cookie*, bukan JSON body.

## 4. Middleware & Pengamanan
- **Task:** Buat `AuthMiddleware` yang mengekstraksi `Bearer Token` dari header, memverifikasi klaim, dan meneruskannya ke *handler* berikutnya.

## 5. Dokumentasi API
- **Task:** Tambahkan anotasi Swagger pada seluruh *endpoint* Auth (Login & Refresh).
- **Task:** *Generate* `swagger.json` dan *push* ke `hris-docs/API_CONTRACTS/auth.json`.
