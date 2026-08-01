# Infrastructure - Organization Module

## 1. Database Seeding & Migration
- **Tidak ada Seeder wajib.** Berbeda dari Bank/Wilayah (data referensi publik yang harus tersedia sejak awal), Company & Branch adalah data transaksional milik masing-masing pelanggan (grup usaha) — didaftarkan manual oleh Owner/Group Admin saat onboarding, bukan diisi otomatis saat *deployment*.
- **Urutan migrasi (WAJIB diperhatikan):** migrasi tabel `companies`/`branches` **harus** dijalankan lebih dulu, sebelum migrasi modul mana pun yang mendeklarasikan FK ke `company_id`/`branch_id` (Workforce Structure, Employee, Employment Status) — modul-modul itu saat ini menjalankan FK secara *staged* (kolom ada, constraint fisik menyusul) persis karena urutan ini (`scoping-convention.md` §4).
- Migrasi index partial (`idx_companies_npwp`, `(company_id, code)` pada `branches`, `(company_id) WHERE is_main=true`) wajib satu paket dengan migrasi `CREATE TABLE`, bukan migrasi terpisah belakangan — mencegah window tanpa constraint di produksi.

## 2. Caching Strategy
- **Tidak ada HTTP caching** pada endpoint manapun di modul ini. Berbeda dari Bank/Wilayah (Global Master, aman di-cache agresif lintas seluruh pengguna), data Company/Branch bersifat transaksional (bisa diubah kapan saja oleh Admin) dan terikat ke pelanggan tertentu — meng-cache berisiko menampilkan data kantor pusat/status aktif yang sudah usang.

## 3. Performance Notes
- **Pencarian (`ILIKE '%...%'`) sengaja tanpa index `pg_trgm`.** Volume `companies`/`branches` kecil (puluhan-ratusan baris per grup usaha, bukan tabel operasional volume tinggi seperti Attendance) — *full scan* diterima di rilis ini. Revisit index trigram kalau data tumbuh signifikan (lihat `tech-spec.md` §3.5 catatan performa asal).
- **Nested `branches` di `GET /companies`** menambah satu query batch (`WHERE company_id IN (...)`) per permintaan list — bukan N+1, tapi tetap query tambahan yang harus diperhitungkan saat estimasi beban (`decision-log.md` ADR-006).

## 4. Secrets & External Integration
Tidak ada. Modul ini murni internal (tanpa API key, tanpa integrasi pihak ketiga).
