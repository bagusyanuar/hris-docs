# User Stories & Engineering Tasks - Organization Module

File ini digunakan untuk membuat sub-task di *GitHub Issues*.

## Task 1: Scaffolding Domain & Entity
- Buat entitas `Company` di `internal/organization/domain/company.go` — konstruktor `NewCompany` men-generate UUID, validasi `code`/`legal_name` wajib.
- Buat entitas `Branch` di `internal/organization/domain/branch.go` — konstruktor `NewBranch` mewajibkan `companyID` non-kosong.
- Definisikan sentinel error: `ErrCompanyNotFound`, `ErrCompanyNPWPDuplicate`, `ErrBranchNotFound`, `ErrBranchCodeDuplicate`, `ErrBranchCompanyMismatch`, `ErrInvalidInput`.
- Definisikan `TxManager` abstraction (unit-of-work) di `internal/organization/domain/tx_manager.go`.

## Task 2: Database Migration
- Buat migrasi SQL (`UP`/`DOWN`) untuk tabel `companies` & `branches` sesuai [tech-spec.md](tech-spec.md) §3.4.
- Partial unique index `companies.npwp` (`WHERE npwp IS NOT NULL AND deleted_at IS NULL`).
- Partial unique index `branches (company_id, code)` dan `branches (company_id) WHERE is_main = true` (keduanya `WHERE deleted_at IS NULL`).

## Task 3: Postgres Repository Implementation
- Implementasikan `CompanyRepository` & `BranchRepository` di `internal/organization/adapter/postgres.go` — `Create`/`Update` pakai method biasa (bukan `Save()`, selaras `persistence-convention.md`).
- Implementasikan `FindAll` (Company) dengan `pkg/pagination`, `search` match `legal_name ILIKE %search%` ATAU `EXISTS` subquery ke branch yang cocok (bukan `JOIN`, hindari duplikasi row — [decision-log.md](decision-log.md) ADR-006).
- Implementasikan `FindAllByCompanyIDs` (Branch, batch tanpa paginasi) untuk kebutuhan nested `branches` di List Company.
- Implementasikan `DemoteMainBranch(ctx, companyID)` — `UPDATE branches SET is_main=false WHERE company_id=? AND is_main=true`.
- Implementasikan `GormTxManager` (implementasi `TxManager` domain).

## Task 4: Application Use Case & HTTP Delivery
- Buat `CreateCompany`, `GetCompany`, `ListCompanies` (embed nested branches lewat batch query), `UpdateCompany`, `DeleteCompany` di `internal/organization/application/service.go`.
- Buat `CreateBranch` — bungkus cek duplikasi kode + demote main branch lama + insert dalam satu `TxManager.Do` ([decision-log.md](decision-log.md) ADR-004).
- Buat `GetBranch`, `ListBranchesByCompany`, `UpdateBranch` (logic demote sama seperti create), `DeleteBranch`.
- Buat `CompanyHandler` & `BranchHandler` di `internal/organization/transport/http/` dengan rute sesuai [tech-spec.md](tech-spec.md) §3.2.

## Task 5: Dependency Injection & Documentation
- *Wiring* modul `organization` ke `internal/di/wire.go`, ekspos Application Service untuk di-inject modul Workforce Structure, Employee, Employment Status.
- Ekspor *Swagger Specs* (YAML) ke `docs/api/swagger/organization.yaml` dan koleksi *Bruno* ke `docs/api/bruno/Organization/`.
- Sinkronkan `hris-docs/API_CONTRACTS/` setelah endpoint selesai dibangun.

## Task 6: Unit Test Domain Logic
- Table-driven test `company_test.go` — cover constructor happy path & validasi `ErrInvalidInput` saat `code`/`legal_name` kosong.
- Table-driven test `branch_test.go` — cover constructor happy path & validasi `ErrInvalidInput` saat `companyID`/`code`/`name` kosong.
