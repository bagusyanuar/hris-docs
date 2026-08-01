# Technical Requirements Document (TRD) - Region Module

## 3.1. PRD Reference
Implementasi ini mengacu pada PRD: [reference_data_wilayah.md](../../../PRD/reference_data_wilayah.md).

## 3.2. API Contracts
Berikut adalah daftar *endpoint* yang diekspos oleh modul ini. Tujuannya adalah melayani kebutuhan *dropdown* UI di sisi *client*.

1. `GET /api/v1/references/provinces` (Mendapatkan semua daftar provinsi)
2. `GET /api/v1/references/cities?province_id={uuid}` (Mendapatkan kota berdasarkan provinsi)
3. `GET /api/v1/references/districts?city_id={uuid}` (Mendapatkan kecamatan berdasarkan kota)
4. `GET /api/v1/references/sub-districts?district_id={uuid}` (Mendapatkan kelurahan berdasarkan kecamatan)

> **Catatan API Contract:** Detail skema *Request/Response* JSON, tipe data, dan daftar lengkap *HTTP Status Code* dikelola sepenuhnya melalui *Swagger/OpenAPI*. Tim BE **wajib** mengekspor file `swagger.json` dan menyimpannya ke folder `hris-docs/API_CONTRACTS/` segera setelah *endpoint* selesai dibangun.

## 3.3. DDD Architecture Design
Seluruh entitas disatukan dalam domain **`internal/region`**.

- **Domain Layer:** 
  - Entitas: `Province`, `City`, `District`, `SubDistrict`. Aturan bisnis: *Read-only*, menggunakan UUID sebagai *Primary Key*, dan `administrative_code` sebagai *Unique Constraint*.
- **Application Layer (Use Cases):**
  - `GetProvincesUseCase`, `GetCitiesByProvinceUseCase`, `GetDistrictsByCityUseCase`, `GetSubDistrictsByDistrictUseCase`.
- **Adapter Layer:**
  - `postgres` (Repository Interfaces Implementation): `ProvinceRepository`, `CityRepository`, dst. Menggunakan `pkg/pagination`.
  - `http` (Delivery): `RegionHandler` memetakan *request* ke *Application layer*.
- **Dependency Injection:** Dikelola menggunakan `google/wire`.

## 3.4. Database Schema Reference
Tabel-tabel relasional (hirarkis) dari entitas wilayah.
- `provinces`: id (uuid), administrative_code (unique), name.
- `cities`: id (uuid), province_id (uuid, FK), administrative_code (unique), name.
- `districts`: id (uuid), city_id (uuid, FK), administrative_code (unique), name.
- `sub_districts`: id (uuid), district_id (uuid, FK), administrative_code (unique), name, postal_code.

*(Skema detail menggunakan format DBML dapat di-*generate* secara terpisah).*

## 3.5. Security & Multi-Tenant Scoping
Karena modul `region` bersifat *Master Data Reference*, modul ini **dikecualikan** dari filter `company_id` dan `branch_id`. Data bersifat global. *Endpoint* dibatasi menggunakan *Auth Middleware* standar (membutuhkan valid JWT Token), tanpa limitasi *Role-Based Access Control* (RBAC) agar semua karyawan bisa mengambil data ini.
