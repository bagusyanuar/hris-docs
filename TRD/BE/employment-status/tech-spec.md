# Technical Requirements Document (TRD) - Employment Status Module

## 3.1. PRD Reference
Implementasi ini mengacu pada PRD: [employment-status.md](../../../PRD/employment-status.md) versi 1.0.0.

## 3.2. API Contracts
Endpoint dikelompokkan mengikuti [api-naming-convention.md](../../../../hris-backend/.agents/rules/api-naming-convention.md) — karena scope-nya per-company (bukan lookup identik lintas-PT seperti Bank), endpoint ditempatkan sebagai *Business Domain Route* (`/api/v1/employment-statuses`), bukan `/api/v1/references/*`, meski tujuan utamanya tetap dropdown. Alasan lengkap ada di [decision-log.md](decision-log.md) ADR-002.

1. `GET /api/v1/employment-statuses` — Mengambil daftar status kepegawaian milik perusahaan aktif (`X-Company-Id`), mendukung pencarian (`?search=`) dan paginasi. Dipakai untuk mengisi dropdown form Employee dan halaman pengelolaan Admin.
2. `POST /api/v1/employment-statuses` — Membuat status kepegawaian baru untuk perusahaan aktif. Hanya Admin Perusahaan/Superadmin.
3. `GET /api/v1/employment-statuses/{id}` — Mengambil detail satu status kepegawaian (dipakai layar edit).
4. `PUT /api/v1/employment-statuses/{id}` — Mengubah atribut status kepegawaian (nama, flag-flag bisnis, `max_duration_months`, `sort_order`).
5. `PATCH /api/v1/employment-statuses/{id}/deactivate` — Menonaktifkan status kepegawaian (`is_active=false`). Endpoint terpisah dari `PUT` biasa karena ini operasi bisnis bermakna khusus (bukan update field generik), selaras semantik Skenario 3 PRD.

> **Catatan API Contract:** Detail skema *Request/Response* JSON, tipe data, dan daftar lengkap *HTTP Status Code* dikelola sepenuhnya melalui *Swagger/OpenAPI*. Tim BE **wajib** mengekspor file `swagger.json` dan menyimpannya ke folder `hris-docs/API_CONTRACTS/` segera setelah *endpoint* selesai dibangun.

## 3.3. DDD Architecture Design
Domain baru **`internal/employmentstatus`**, dikonsumsi modul lain (Employee, dan nanti Leave/Payroll) lewat Application Service — dilarang akses tabel `employment_statuses` langsung dari domain lain.

- **Domain Layer:**
  - Entitas: `EmploymentStatus`.
  - Atribut: `id` (UUID), `company_id`, `code`, `name`, `is_active`, `requires_contract_period`, `requires_probation_end_date`, `has_leave_entitlement`, `has_severance_pay`, `max_duration_months` (`*int`, nullable), `sort_order`.
  - Constructor `NewEmploymentStatus(...)` men-generate UUID bila kosong (selaras `uuid-generation.md`) dan memvalidasi `code`/`name` tidak kosong.
  - Sentinel errors: `ErrEmploymentStatusNotFound`, `ErrEmploymentStatusCodeDuplicate`, `ErrEmploymentStatusCompanyMismatch`.
- **Application Layer (Use Cases):**
  - `CreateEmploymentStatusUseCase` — validasi `code` unik per `company_id`, panggil constructor domain, simpan.
  - `UpdateEmploymentStatusUseCase` — validasi entity ditemukan & sesuai scope company aktif sebelum update.
  - `DeactivateEmploymentStatusUseCase` — set `is_active=false`; **tidak** memblokir meski masih dipakai karyawan aktif (PRD Skenario 3).
  - `GetEmploymentStatusesUseCase` — list dengan paginasi + search (`pkg/pagination`), filter `company_id` dari `scope.FromContext`.
  - `ValidateContractDurationUseCase` (dikonsumsi Employee saat create/extend `EmployeeContract`) — jumlahkan durasi seluruh periode kontrak existing + kontrak baru milik satu karyawan untuk `employment_status_id` yang sama, tolak (`ErrContractDurationExceeded`) bila melebihi `max_duration_months` (nullable = tanpa batas, selalu lolos). Ini adalah Application Service yang diekspos ke domain Employee, bukan endpoint HTTP tersendiri (PRD Skenario 4).
- **Adapter Layer:**
  - `postgres`: Implementasi `EmploymentStatusRepository`. `FindAll` pakai whitelist `SortMap` (`code`, `name`, `sort_order`, `created_at`) dan `SearchClause("code", "name")` sesuai `pagination-convention.md` §3.
  - `http`: `EmploymentStatusHandler` merespons rute REST di atas.
- **Dependency Injection:** Dikelola menggunakan `google/wire`, di-inject sebagai Application Service ke domain Employee (untuk `ValidateContractDurationUseCase` dan resolusi `requires_probation_end_date`).

## 3.4. Database Schema Reference
Tabel relasional untuk Employment Status.
- `employment_statuses`:
  - `id` (uuid, PK)
  - `company_id` (uuid, FK → `companies.id`, not null) — fisik FK staged sampai modul Organization landing (`scoping-convention.md` §4), kolom & validasi scope tetap dipaku sekarang.
  - `code` (varchar, not null)
  - `name` (varchar, not null)
  - `is_active` (boolean, not null, default `true`)
  - `requires_contract_period` (boolean, not null, default `false`)
  - `requires_probation_end_date` (boolean, not null, default `false`)
  - `has_leave_entitlement` (boolean, not null, default `true`)
  - `has_severance_pay` (boolean, not null, default `true`)
  - `max_duration_months` (int, nullable)
  - `sort_order` (int, not null, default `0`)
  - Index unik: `(company_id, code)`.
  - Index: `(company_id)` untuk filter scope pada `List`.

Perubahan pada tabel `employees` (existing):
- Kolom `employment_type` (varchar enum) **dihapus**, digantikan `employment_status_id` (uuid, FK → `employment_statuses.id`, not null).
- Migrasi data: seed 5 baris standar (`PERMANENT`/`CONTRACT`/`PROBATION`/`INTERN`/`DAILY_WORKER`) per `company_id` existing terlebih dahulu, baru backfill `employees.employment_status_id` dari nilai `employment_type` lama (match by `code` + `company_id`), sebelum kolom lama di-drop pada migrasi terpisah.

## 3.5. Security & Multi-Tenant Scoping
`employment_statuses` diklasifikasikan **Company-owned** (`company_id` NOT NULL, tanpa `branch_id`) — bukan *Global Master Reference* seperti Bank/Wilayah. Semua query `FindAll`/`FindByID` di Adapter Layer **wajib** membaca `scope.FromContext(ctx)` dan inject filter `company_id`, konsisten dengan pola `internal/organization` dan `internal/workforce`. Endpoint tulis (`POST`/`PUT`/`PATCH`) memvalidasi entity yang diakses berada dalam `company_id` yang diizinkan sebelum eksekusi — mismatch ditolak `ErrEmploymentStatusCompanyMismatch` (403), bukan diam-diam di-filter. Active scope diambil dari header `X-Company-Id` sesuai `scoping-convention.md` §3.1, divalidasi subset dari `scope.FromContext` sebelum dipakai.
