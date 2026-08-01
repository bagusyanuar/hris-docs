# User Stories & Engineering Tasks - Region Module

File ini dapat digunakan sebagai referensi untuk membuat sub-task di *GitHub Issues* / Jira.

## Task 1: Scaffolding Domain & Entities
- Buat entitas `Province`, `City`, `District`, `SubDistrict` di `internal/region/domain/`.
- Tuliskan antarmuka (interface) `RegionRepository` yang membungkus semua operasi keempat entitas tersebut (atau pisahkan per entitas jika file terlalu besar).

## Task 2: Database Migration & Seeder
- Buat file migrasi SQL (`UP` dan `DOWN`) untuk 4 tabel hirarki wilayah.
- Buat file seeder berbasis `.sql` atau programmatic Go untuk memasukkan kode Kemendagri awal (bisa diunduh dari dataset publik) ke tabel yang baru dibuat.

## Task 3: Postgres Repository Implementation
- Implementasikan metode pencarian wilayah (`FindAll`, `FindByParentID`) pada `internal/region/adapter/postgres/`.
- Integrasikan dengan modul `pkg/pagination` untuk menyeragamkan format paging dan standar keamanan sorting/search.

## Task 4: Application Use Cases & HTTP Delivery
- Susun *Use Cases* di `internal/region/application/`.
- Buat HTTP Handlers di `internal/region/adapter/http/` dengan mematuhi konvensi *prefix* API: `/api/v1/references/`.
- Terapkan HTTP Caching Header.

## Task 5: Dependency Injection & Documentation
- Hubungkan seluruh komponen menggunakan `Wire` dan daftarkan ke *router* utama.
- Buat *Swagger Specs* YAML di `docs/api/swagger/region.yaml`.
- Tambahkan koleksi Bruno di `docs/api/bruno/References/Region/`.
