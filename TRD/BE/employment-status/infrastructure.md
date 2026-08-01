# Infrastructure - Employment Status Module

## 1. Database Seeding & Migration
- Seeder awal (satu kali, saat migrasi modul ini pertama kali dijalankan) mengisi 5 baris standar (`PERMANENT`/`CONTRACT`/`PROBATION`/`INTERN`/`DAILY_WORKER`) untuk **setiap `company_id` yang sudah ada** di tabel `companies` saat itu — lihat [user-stories.md](user-stories.md) Task 2 untuk urutan migrasi & backfill `employees.employment_type` → `employment_status_id`.
- **Seeding untuk PT baru (pasca-migrasi awal):** karena modul Organization (pembuatan Company baru) masih *staged* (belum ada di kode, lihat `scoping-convention.md` §4), pemicu otomatis "saat Company baru dibuat, seed 5 baris default untuk company itu" **belum bisa diimplementasikan sebagai event/hook lintas-modul sekarang**. Untuk sementara, pembuatan Company baru (manual oleh Superadmin) **wajib** diikuti pemanggilan manual `CreateEmploymentStatusUseCase` 5 kali (atau skrip seeder terpisah) — dicatat sebagai *technical debt* yang harus ditutup lewat Application Service call synchronous begitu modul Organization landing (Company creation memanggil Employment Status Application Service untuk auto-seed, bukan lewat Message Broker — selaras `coding-convention.md` §4 yang saat ini masih synchronous antar-modul).

## 2. Caching Strategy
- **Tidak memakai HTTP caching agresif** seperti modul Bank/Wilayah. Karena data ini di-scope per `company_id` (bukan identik lintas-PT) dan punya operasi tulis yang relatif sering di awal pemakaian tiap PT, `Cache-Control: public, max-age=...` **tidak** dipasang di endpoint `GET /api/v1/employment-statuses` — cukup mengandalkan index database `(company_id, code)` untuk kecepatan query, mengingat volume baris per PT sangat kecil (puluhan, bukan ribuan).

## 3. Secrets & External Integration
Tidak ada. Modul ini murni internal (tanpa API key, tanpa integrasi pihak ketiga).
