# TRD Extension: Infrastructure (Backend Auth)

Dokumen ini memuat daftar *environment variables* dan infrastruktur eksternal yang dibutuhkan modul.

## 1. Environment Variables (.env)
Modul Auth sangat bergantung pada rahasia kriptografi. Variabel berikut wajib disediakan di *server*:
- `JWT_SECRET`: Kunci rahasia untuk menandatangani JWT (algoritma `HS256`).
- `JWT_ACCESS_EXPIRES_IN`: Umur access token (misal: `15m`).
- `JWT_REFRESH_EXPIRES_IN`: Umur refresh token (misal: `7d`).

## 2. Swagger API Contracts
- Tim BE tidak mendefinisikan API di TRD. Spesifikasi JSON mutlak di-*generate* melalui anotasi Swagger (e.g. `swaggo/swag`).
- Hasil *generate* berupa file `swagger.json` **WAJIB** di- *commit* ke direktori `hris-docs/API_CONTRACTS/auth.json`.
- Dokumentasi ini juga bisa diakses secara *live* melalui Docker Container Swagger UI (biasanya `http://localhost:8080/swagger` pada lingkungan pengembangan lokal).
