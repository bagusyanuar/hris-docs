# Technical Requirements Document (TRD) - Organization Module

## 3.1. PRD Reference
Implementasi ini mengacu pada PRD: [organization.md](../../../PRD/organization.md) versi 2.0.0. Modul sudah terimplementasi di `internal/organization/` (lihat catatan grounding PRD).

## 3.2. API Contracts
Base path `/api/v1`. Branch di-nested di bawah Company untuk pembuatan & listing (butuh konteks Company induk), tapi flat untuk aksi per-record (get/update/delete satu Branch tidak perlu tahu `companyId` lewat URL lagi).

1. `POST /api/v1/companies` — Mendaftarkan Company (PT) baru.
2. `GET /api/v1/companies` — Daftar Company, mendukung paginasi, `?search=` (cocok nama badan hukum ATAU nama salah satu Branch miliknya), dan menyertakan daftar Branch (nested) tiap Company dalam satu respons (PRD Skenario 6).
3. `GET /api/v1/companies/{id}` — Detail satu Company.
4. `PUT /api/v1/companies/{id}` — Mengubah data Company.
5. `DELETE /api/v1/companies/{id}` — Menonaktifkan (soft delete) Company. Tidak cascade ke Branch anak (PRD Skenario 5, gap tercatat).
6. `POST /api/v1/companies/{companyId}/branches` — Mendaftarkan Branch baru di bawah Company tersebut. `is_main=true` memicu pencabutan status kantor pusat Branch lama secara otomatis (PRD Skenario 4).
7. `GET /api/v1/companies/{companyId}/branches` — Daftar Branch milik satu Company, dengan paginasi.
8. `GET /api/v1/branches/{id}` — Detail satu Branch.
9. `PUT /api/v1/branches/{id}` — Mengubah data Branch (termasuk toggle `is_main`, efek sama seperti create).
10. `DELETE /api/v1/branches/{id}` — Menonaktifkan (soft delete) Branch.

> **Catatan API Contract:** Detail skema *Request/Response* JSON, tipe data, dan daftar lengkap *HTTP Status Code* dikelola sepenuhnya melalui *Swagger/OpenAPI*. Tim BE **wajib** mengekspor file `swagger.json` dan menyimpannya ke folder `hris-docs/API_CONTRACTS/` segera setelah *endpoint* selesai dibangun.

## 3.3. DDD Architecture Design
Bounded context `internal/organization/` berisi **dua aggregate root independen** — Branch mereferensikan Company lewat `CompanyID` (foreign key), bukan sub-koleksi yang selalu dimuat bersama Company (lihat [decision-log.md](decision-log.md) ADR-003).

- **Domain Layer:**
  - Entitas: `Company` (legal root, tanpa kolom scope), `Branch` (location root, `CompanyID` wajib).
  - Constructor `NewCompany`/`NewBranch` men-generate UUID (selaras `uuid-generation.md`) dan validasi field wajib.
  - Sentinel errors: `ErrCompanyNotFound`, `ErrCompanyNPWPDuplicate`, `ErrBranchNotFound`, `ErrBranchCodeDuplicate`, `ErrBranchCompanyMismatch`, `ErrInvalidInput`.
  - `TxManager` (unit-of-work abstraction) — dipakai untuk operasi yang wajib atomik (lihat §3.3 Application Layer).
- **Application Layer (Use Cases):**
  - `CreateCompany`, `GetCompany`, `ListCompanies` (embed nested `branches` lewat batch query, bukan N+1 — [decision-log.md](decision-log.md) ADR-006), `UpdateCompany`, `DeleteCompany`.
  - `CreateBranch` — validasi `companyId` ada, cek duplikasi `code` dalam company yang sama, **demote otomatis** main branch lama bila `is_main=true`, semua dalam satu `TxManager.Do` ([decision-log.md](decision-log.md) ADR-004).
  - `GetBranch`, `ListBranchesByCompany`, `UpdateBranch` (logic demote sama seperti create), `DeleteBranch`.
- **Adapter Layer:**
  - `postgres`: `CompanyRepository` + `BranchRepository` implementasi, `GormTxManager` implementasi `TxManager`.
  - `http`: `CompanyHandler` + `BranchHandler` merespons rute REST di atas.
- **Dependency Injection:** Dikelola `google/wire`. Modul lain (Workforce Structure, Employee, Employment Status) inject `organization/application.Service` (Application Service), **bukan** repository langsung, sesuai `coding-convention.md` §4.

## 3.4. Database Schema Reference
- `companies`:
  - `id` (uuid, PK)
  - `code` (varchar(20), not null)
  - `legal_name` (varchar(150), not null)
  - `npwp` (varchar(25), nullable — partial unique index `WHERE npwp IS NOT NULL AND deleted_at IS NULL`, lihat [decision-log.md](decision-log.md) ADR-005)
  - `bpjs_no` (varchar(50), nullable)
  - `is_active` (boolean, not null, default `true`)
  - `deleted_at` (timestamp, nullable — soft delete)
- `branches`:
  - `id` (uuid, PK)
  - `company_id` (uuid, FK → `companies.id`, not null, index)
  - `code` (varchar(20), not null — partial unique `(company_id, code)` WHERE `deleted_at IS NULL`)
  - `name` (varchar(150), not null)
  - `city` (varchar(100), nullable)
  - `is_main` (boolean, not null, default `false` — partial unique `(company_id)` WHERE `is_main = true AND deleted_at IS NULL`, jaring pengaman terakhir di level DB untuk PRD Skenario 4)
  - `is_active` (boolean, not null, default `true`)
  - `deleted_at` (timestamp, nullable — soft delete)

## 3.5. Security & Multi-Tenant Scoping
`Company` = **Legal root** (tanpa kolom scope, dia sendiri adalah akar hierarki). `Branch` = **Company-owned** (`company_id` NOT NULL). Semua endpoint wajib lolos `AuthProtected` (JWT). Operasi tulis (`POST`/`PUT`/`DELETE`) idealnya dibatasi role `OWNER`/`GROUP_ADMIN`, namun penegakan granular per role **staged** menunggu modul RBAC landing — untuk saat ini seluruh request berjalan mode Owner (tanpa filter tambahan), sesuai `scoping-convention.md` §4. Repository `FindAll`/`FindAllByCompany` sudah membaca `scope.FromContext(ctx)` sesuai kontrak (signature dipaku sekarang), meski isinya masih kosong sampai RBAC menyala.
