# Technical Requirements Document (TRD) - Bank Module

## 3.1. PRD Reference
Implementasi ini mengacu pada PRD: [bank.md](../../../PRD/bank.md).

## 3.2. API Contracts
Berikut adalah daftar *endpoint* yang diekspos oleh modul ini untuk kebutuhan *dropdown* UI di sisi *client*.

1. `GET /api/v1/references/banks` (Mendapatkan semua daftar bank, mendukung pencarian via *query param* `?search=`)

> **Catatan API Contract:** Detail skema *Request/Response* JSON, tipe data, dan daftar lengkap *HTTP Status Code* dikelola sepenuhnya melalui *Swagger/OpenAPI*. Tim BE **wajib** mengekspor file `swagger.json` dan menyimpannya ke folder `hris-docs/API_CONTRACTS/` segera setelah *endpoint* selesai dibangun.

## 3.3. DDD Architecture Design
Entitas bank ditempatkan di dalam domain tersendiri yaitu **`internal/bank`** (atau bisa digabung dalam domain besar `internal/reference` jika disepakati di masa depan).

- **Domain Layer:** 
  - Entitas: `Bank`.
  - Atribut: `id` (UUID), `name`, `bank_code`, `swift_code`, `is_active`.
- **Application Layer (Use Cases):**
  - `GetBanksUseCase` (Menangani pengambilan daftar bank dengan fitur pencarian dan paginasi).
- **Adapter Layer:**
  - `postgres`: Implementasi `BankRepository`.
  - `http`: `BankHandler` merespons ke rute REST API.
- **Dependency Injection:** Dikelola menggunakan `google/wire`.

## 3.4. Database Schema Reference
Tabel relasional untuk Bank.
- `banks`: 
  - `id` (uuid, PK)
  - `name` (varchar, not null)
  - `bank_code` (varchar, unique, nullable) - Kode BI/RTGS
  - `swift_code` (varchar, nullable)
  - `is_active` (boolean, default true)

## 3.5. Security & Multi-Tenant Scoping
Karena modul `bank` bersifat *Master Data Reference*, modul ini **dikecualikan** dari filter `company_id` dan `branch_id`. Data bersifat global. *Endpoint* dibatasi menggunakan *Auth Middleware* standar, tanpa limitasi *Role-Based Access Control* (RBAC) agar semua karyawan bisa memilih bank untuk rekening gajinya.
