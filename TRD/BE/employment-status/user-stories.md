# User Stories & Engineering Tasks - Employment Status Module

File ini digunakan untuk membuat sub-task di *GitHub Issues*.

## Task 1: Scaffolding Domain & Entity
- Buat entitas `EmploymentStatus` di `internal/employmentstatus/domain/employment_status.go` — konstruktor generate UUID bila kosong, validasi `code`/`name` tidak kosong.
- Definisikan sentinel error: `ErrEmploymentStatusNotFound`, `ErrEmploymentStatusCodeDuplicate`, `ErrEmploymentStatusCompanyMismatch`, `ErrContractDurationExceeded`.
- Definisikan *interface* repository: `Create`, `Update`, `FindByID`, `FindAll` (dengan `company_id`, `search`, paginasi), `SumContractDurationMonths` (dipakai validasi durasi).

## Task 2: Database Migration & Seeder
- Buat migrasi SQL (`UP`/`DOWN`) untuk tabel `employment_statuses` (kolom & index sesuai [tech-spec.md](tech-spec.md) §3.4).
- Buat migrasi terpisah untuk `employees`: tambah kolom `employment_status_id` (nullable dulu di migrasi ini, NOT NULL di migrasi berikutnya setelah backfill selesai — hindari downtime lock).
- Buat *seeder* 5 baris standar (`PERMANENT`/`CONTRACT`/`PROBATION`/`INTERN`/`DAILY_WORKER`) untuk tiap `company_id` yang sudah ada di database saat migrasi dijalankan.
- Buat skrip backfill: isi `employees.employment_status_id` berdasarkan pencocokan `employment_type` lama (per baris) ke `code` + `company_id` hasil seeding di atas.
- Migrasi lanjutan: set `employment_status_id` jadi NOT NULL, lalu `DROP COLUMN employment_type`.

## Task 3: Postgres Repository Implementation
- Implementasikan `internal/employmentstatus/adapter/postgres.go` — `Create`/`Update` pakai `Create()`/`Updates()` biasa (bukan `Save()`, selaras `persistence-convention.md`), unique violation `(company_id, code)` dipetakan ke `ErrEmploymentStatusCodeDuplicate`.
- `FindAll` integrasi `pkg/pagination` (`SortMap`: `code`, `name`, `sort_order`, `created_at`; `SearchClause("code", "name")`), filter `company_id` dari `scope.FromContext` WAJIB di-chain sebelum `pagination.Query[T]`.
- `SumContractDurationMonths` — query agregat total durasi periode `EmployeeContract` existing milik satu `employee_id` + `employment_status_id`.

## Task 4: Application Use Case & HTTP Delivery
- Buat `CreateEmploymentStatusUseCase`, `UpdateEmploymentStatusUseCase`, `DeactivateEmploymentStatusUseCase`, `GetEmploymentStatusesUseCase`, `GetEmploymentStatusByIDUseCase` di `internal/employmentstatus/application/`.
- Buat `ValidateContractDurationUseCase` — diekspos sebagai Application Service untuk dipanggil domain Employee (bukan endpoint HTTP), lihat [decision-log.md](decision-log.md) ADR-004.
- Buat `EmploymentStatusHandler` di `internal/employmentstatus/adapter/http/` dengan rute sesuai [tech-spec.md](tech-spec.md) §3.2. Validasi input pakai `pkg/validator` (422 untuk field wajib kosong).
- Handler baca header `X-Company-Id`, validasi subset dari `scope.FromContext` sebelum dipakai filter (`scoping-convention.md` §3.1).

## Task 5: Integrasi ke Employee
- Ubah `internal/employee/domain/entity.go`: field `EmploymentType` (string enum) → `EmploymentStatusID` (string, FK).
- Employee Application Service memanggil `ValidateContractDurationUseCase` (Task 4) saat create/extend `EmployeeContract`, dan membaca `requires_probation_end_date` untuk mewajibkan `probation_end_date` (PRD Skenario 6).
- Update DTO Employee (request/response) — response nested `{id, name}` untuk `employment_status` sesuai `preload-convention.md` (bukan flat `employment_status_name`).

## Task 6: Dependency Injection & Documentation
- *Wiring* modul `employmentstatus` ke `internal/di/wire.go`, inject Application Service ke modul Employee (bukan repository langsung).
- Ekspor *Swagger Specs* (YAML) ke `docs/api/swagger/employment_status.yaml` dan koleksi *Bruno* ke `docs/api/bruno/EmploymentStatus/`. Update juga Swagger `employee.yaml` untuk field yang berubah.
- Sinkronkan `hris-docs/API_CONTRACTS/` setelah endpoint selesai dibangun.
