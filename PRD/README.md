# PRD Index

Daftar seluruh Product Requirements Document di `hris-docs`. Selalu update tabel ini saat PRD baru dibuat atau versi/status berubah (`scaffold-prd` §1, mandatory).

## Global

| Dokumen | Versi | Status | Terakhir Update |
|---|---|---|---|
| [product-vision.md](product-vision.md) | 1.0.0 | Draft | 2026-08-01 22:30:00 |

## Modul

| Modul | Versi | Status | Depends On | Consumed By | Terakhir Update |
|---|---|---|---|---|---|
| [user.md](user.md) | 1.0.1 | Draft | — | auth@1.0.1, employee@1.0.0, rbac@1.0.1 | 2026-08-01 23:00:00 |
| [auth.md](auth.md) | 1.0.1 | Draft | user@1.0.1 | employee@1.0.0, organization@1.0.1, rbac@1.0.1 | 2026-08-01 23:00:00 |
| [organization.md](organization.md) | 1.0.1 | Draft | auth@1.0.1, bank@planned, region@planned | workforce-structure@1.0.1, employee@1.0.0, employment-status@1.0.1, rbac@1.0.1, leave-type@1.0.1, work-shift@1.0.1, payroll@planned, attendance@planned | 2026-08-01 23:00:00 |
| [workforce-structure.md](workforce-structure.md) | 1.0.1 | Draft | organization@1.0.1, rbac@1.0.1 | employee@1.0.0 | 2026-08-01 23:00:00 |
| [employment-status.md](employment-status.md) | 1.0.1 | Draft | organization@1.0.1, rbac@1.0.1 | employee@1.0.0, leave@planned, payroll@planned | 2026-08-01 23:00:00 |
| [bank.md](bank.md) | 1.0.0 | Draft | — | employee@1.0.0, organization@planned, payroll@planned | 2026-08-01 19:15:00 |
| [region.md](region.md) | 1.0.0 | Draft | — | employee@1.0.0, organization@planned | 2026-08-01 19:15:00 |
| [rbac.md](rbac.md) | 1.0.1 | Draft | auth@1.0.1, user@1.0.1, organization@1.0.1 | employment-status@1.0.1, employee@1.0.0, workforce-structure@1.0.1, leave-type@1.0.1, work-shift@1.0.1, payroll@planned, attendance@planned, leave@planned | 2026-08-01 23:00:00 |
| [leave-type.md](leave-type.md) | 1.0.1 | Draft | organization@1.0.1, rbac@1.0.1 | leave@planned | 2026-08-01 23:00:00 |
| [work-shift.md](work-shift.md) | 1.0.1 | Draft | organization@1.0.1, rbac@1.0.1 | attendance@planned | 2026-08-01 23:00:00 |

> **Belum dimigrasi ke `hris-docs`** (masih di `hris-backend/docs/PRD/`): `employee.md`. Lihat [product-vision.md](product-vision.md) §5.1.

## Dependency Graph

```mermaid
graph TD
    Organization --> WorkforceStructure["Workforce Structure"]
    Organization --> Employee
    Organization --> EmploymentStatus["Employment Status"]
    User --> Auth
    Auth --> Employee
    Auth --> Organization
    Bank --> Employee
    Bank --> Organization
    Wilayah --> Employee
    Wilayah --> Organization
    EmploymentStatus --> Leave["Leave (planned)"]
    EmploymentStatus --> Payroll["Payroll (planned)"]
    Auth --> RBAC
    User --> RBAC
    Organization --> RBAC
    RBAC --> EmploymentStatus
    RBAC --> WorkforceStructure
    WorkforceStructure --> Employee
    Organization --> LeaveType["Leave Type"]
    RBAC --> LeaveType
    LeaveType --> Leave
    Organization --> WorkShift["Work Shift"]
    RBAC --> WorkShift
    WorkShift --> Attendance["Attendance (planned)"]
```

## Ringkasan Gap

| Item | Kondisi |
|---|---|
| PRD `employee` | Masih di `hris-backend/docs/PRD/`, belum dipindah ke `hris-docs` — migrasi menyusul (pola sama seperti `organization.md`). |
| `PRD/_shared/glossary.md` | Belum dibuat — belum ada istilah lintas-modul yang cukup mendesak diangkat. |
