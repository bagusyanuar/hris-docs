# Data Dictionary - Organization Module

## 1. Naming & Formatting
- **code (Company):** Bebas format singkat (contoh: `"PTA"`, `"PTB"`), dipakai sebagai identitas ringkas internal — bukan identitas legal (itu peran `legal_name`/`npwp`). Maks 20 karakter.
- **legal_name:** Nama badan hukum resmi sesuai akta (contoh: `"PT Alpha Nusantara"`). Maks 150 karakter.
- **npwp:** Format standar `NN.NNN.NNN.N-NNN.NNN` (15 digit NPWP Indonesia). Opsional — kosong diperbolehkan, tidak divalidasi format ketat di rilis ini (validasi format detail belum diimplementasikan, hanya unique constraint saat terisi).
- **code (Branch):** Bebas format singkat (contoh: `"JKT"`, `"SBY"`), unik hanya dalam lingkup satu Company (dua Company boleh sama-sama punya kode `"JKT"`). Maks 20 karakter.
- **city:** Nama kota bebas teks, tidak direlasikan ke Master Data Wilayah di rilis ini (lihat Ringkasan Gap PRD Employee §5 soal rencana relasi wilayah di masa depan).

## 2. Enums & Lifecycles
- `is_active` (Company & Branch, boolean): `true` = beroperasi normal. `false` = dinonaktifkan (soft delete secara bisnis) — dipakai bersamaan dengan `deleted_at` terisi. Tidak ada state ketiga.
- `deleted_at` (nullable timestamp): Penanda soft delete teknis. `NULL` = record hidup. Terisi = "terhapus" tapi tetap ada secara fisik di database (wajib, demi integritas riwayat Payroll/Attendance/Employee yang merujuknya — PRD Skenario 7).
- `is_main` (Branch, boolean): `true` = kantor pusat (head office) Company tersebut. Invariant: **tepat satu** `is_main=true` per `company_id` pada waktu mana pun. Transisi antar Branch terjadi lewat *auto-demote* (lihat `decision-log.md` ADR-004) — bukan dua langkah manual set/unset terpisah.

## 3. Error Mappings
| Sentinel Error (Domain) | Pemicu | HTTP Status |
|---|---|---|
| `ErrInvalidInput` | Field wajib kosong saat constructor domain dipanggil (`code`/`legal_name` untuk Company; `companyID`/`code`/`name` untuk Branch). | `422 Unprocessable Entity` |
| `ErrCompanyNotFound` | `FindByID` Company tidak menemukan baris (termasuk saat dirujuk dari alur Branch, mis. `companyId` di path tidak valid). | `404 Not Found` |
| `ErrCompanyNPWPDuplicate` | Insert/update `npwp` yang sudah dipakai Company lain (hanya berlaku saat `npwp` diisi — dua `NULL` tidak konflik). | `409 Conflict` |
| `ErrBranchNotFound` | `FindByID` Branch tidak menemukan baris. | `404 Not Found` |
| `ErrBranchCodeDuplicate` | Insert/update `code` Branch yang sudah ada di `company_id` yang sama. | `409 Conflict` |
| `ErrBranchCompanyMismatch` | Dicadangkan untuk fase mendatang — dipakai modul lain (mis. Employee) saat validasi `branch_id` yang dirujuk ternyata bukan milik `company_id` yang bersangkutan. Belum dipicu dari dalam modul Organization sendiri di rilis ini. | `422 Unprocessable Entity` |
