# Infrastructure - Bank Module

## 1. Database Seeding & Migration
Sama halnya dengan wilayah, *developer* diwajibkan menyertakan skrip *Seeder* untuk mengisi tabel `banks` dengan daftar bank umum yang terdaftar di OJK/BI. Tabel ini harus sudah ada isinya ketika aplikasi HRIS di-deploy.

## 2. Caching Strategy
- **HTTP Layer:** Response pada endpoint `GET /api/v1/references/banks` harus menyertakan header `Cache-Control: public, max-age=86400` (cache 1 hari).
- **Search Query Caching:** Jika ada pencarian via `?search=`, *query* tersebut cukup di-*cache* oleh Edge Server atau in-memory jika *traffic* tinggi, karena daftar bank jarang sekali berubah.
