# Data Dictionary - Employment Status Module

## 1. Naming & Formatting
- **code:** Ditulis `UPPER_SNAKE_CASE` (contoh: `"CONTRACT"`, `"DAILY_WORKER"`), konsisten dengan enum lama yang digantikan. Unik per `(company_id, code)`, **bukan** unik global — dua PT boleh sama-sama punya kode `"CONTRACT"`.
- **name:** Label tampil bebas format (bisa di-reword HR sesuai bahasa internal PT, contoh: `"Karyawan Kontrak"` atau `"PKWT"`), tidak divalidasi format khusus selain wajib tidak kosong.
- **max_duration_months:** Integer bulat bulan, bukan hari/tahun. `null` = tanpa batas (dipakai `PERMANENT`/`INTERN`/`DAILY_WORKER`). Terisi = ada batas kumulatif (mis. `60` untuk `CONTRACT` sesuai ketentuan ketenagakerjaan berlaku, `3` untuk `PROBATION`).

## 2. Enums & Lifecycles
- `is_active` (boolean): `true` berarti status ini bisa dipilih untuk karyawan **baru**. `false` berarti sudah dinonaktifkan HR — karyawan existing yang sudah memakainya **tidak** terdampak/tidak error, hanya hilang dari pilihan dropdown. Tidak ada state ketiga (tidak ada "archived"/"deleted") — hanya dua nilai boolean ini.
- `requires_contract_period` (boolean): `true` mewajibkan Employee punya minimal satu baris `EmployeeContract` saat status ini dipilih (dicek di Application Layer Employee, bukan constraint DB).
- `requires_probation_end_date` (boolean): `true` mewajibkan kolom `Employee.probation_end_date` terisi (non-null) saat status ini dipilih.
- `has_leave_entitlement` / `has_severance_pay` (boolean): murni flag data untuk dikonsumsi modul Cuti/Payroll di masa depan — **tidak ada logic apa pun** yang mengeksekusi berdasarkan flag ini di dalam modul Employment Status sendiri maupun Employee saat ini (modul konsumennya belum ada).

## 3. Error Mappings
| Sentinel Error (Domain) | Pemicu | HTTP Status |
|---|---|---|
| `ErrEmploymentStatusNotFound` | `FindByID` tidak menemukan baris (atau ditemukan tapi beda `company_id` — diperlakukan sama seperti tidak ditemukan, bukan 403, untuk hindari kebocoran informasi eksistensi data PT lain). | `404 Not Found` |
| `ErrEmploymentStatusCodeDuplicate` | Insert/update `code` yang sudah ada di `company_id` yang sama (unique violation `(company_id, code)`). | `409 Conflict` |
| `ErrEmploymentStatusCompanyMismatch` | Operasi tulis eksplisit menyebutkan `company_id` yang berbeda dari active scope (`X-Company-Id`) — beda dari kasus not-found di atas karena ini terjadi saat validasi *sebelum* query DB (mis. payload request memuat `company_id` yang tidak cocok header). | `403 Forbidden` |
| `ErrContractDurationExceeded` | `ValidateContractDurationUseCase` menghitung akumulasi durasi kontrak baru melebihi `max_duration_months` milik `employment_status_id` terkait. | `409 Conflict` |
