# Infrastructure - Region Module

## 1. Database Seeding & Migration
Karena ini adalah modul *Reference Data*, *developer* backend diwajibkan menyertakan mekanisme *Seeder* (misal: mengeksekusi file `.sql` dump atau mem-*parsing* file `.csv` master BPS/Kemendagri). Tabel-tabel `region` harus sudah otomatis terisi setelah eksekusi perintah migrasi (misal: `make migrate-up`).

## 2. Caching Strategy
Modul ini adalah kandidat terbaik untuk agresivitas *caching*.
- **HTTP Layer:** Response harus menyertakan header `Cache-Control: public, max-age=86400`.
- **Gateway Layer (Opsional):** Jika HRIS menggunakan Kong/Nginx Ingress, rute `/api/v1/references/*` bisa diatur untuk merespons langsung dari Edge Server.
- **In-Memory Go (Opsional):** Mengingat ukurannya (ribuan kelurahan, ratusan kota) tidak terlalu bengkak, *Repository layer* diperbolehkan menggunakan *in-memory cache library* (seperti `Ristretto` atau *map* dengan RWMutex) jika frekuensi *hit* dari DB PostgreSQL dianggap terlalu tinggi.
