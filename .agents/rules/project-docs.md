# Dokumen Proyek (Requirements & Technical)

Workspace `hris-docs` adalah **Control Plane** proyek. Ada tiga pilar dokumen utama yang wajib dirancang dan disimpan di sini secara permanen sebelum eksekusi kode dilakukan:

## 1. Product Requirements Document (PRD) (Fase Bisnis)
- Jika *user* meminta rancangan fitur, *requirement*, atau alur bisnis (bukan implementasi teknis murni), gunakan format PRD.
- **WAJIB** disimpan di folder `PRD/` (contoh: `PRD/employee.md`).
- Format penulisan wajib mematuhi template `PRD/_TEMPLATE.md` dan menggunakan *skill* `scaffold-prd`.
- **Prinsip**: PRD hanya memuat WHAT dan WHY, tidak membahas HOW (jangan bahas arsitektur kode, jenis validasi Svelte, atau relasi SQL fisik di sini).

## 2. Dokumen Teknis & Arsitektur (Fase Desain)
Setelah PRD disetujui, spesifikasi teknis (HOW) dijabarkan secara terpisah untuk Backend (BE) dan Frontend (FE). Dokumen-dokumen ini nantinya akan dipublikasikan sebagai GitHub Issues untuk dikerjakan oleh masing-masing tim/agen.

### A. TRD BE (`TRD/BE/<domain_name>/`)
- Disimpan di sub-folder per domain, misalnya `TRD/BE/employee/tech-spec.md`.
- Membahas arsitektur DDD, kontrak API, *sequence diagram* logika bisnis, penanganan error, dan *decision log* (ADR).
- **Tingkat Kelengkapan:** 
  - **Simpel**: Cukup skema DBML & ringkasan kontrak API.
  - **Sedang**: `tech-spec.md` (arsitektur inti + API terperinci).
  - **Kompleks**: `tech-spec.md` + `user-stories.md` + `decision-log.md`.

### B. TRD FE (`TRD/FE/<domain_name>/`)
- Disimpan di sub-folder per domain, misalnya `TRD/FE/employee/ui-architecture.md`.
- Membahas desain komponen UI Svelte, *state management* (penggunaan Runes Svelte 5), *mock-up* data untuk pengembangan paralel, serta strategi *client-side validation* dan *error handling*.

### C. Dokumen Pendukung (Opsional)
Berlaku untuk **kedua sisi (TRD BE maupun FE)**. Dibuat jika modul yang didesain memiliki kompleksitas tinggi. Dokumen ini dapat disimpan di sub-folder domain masing-masing (contoh: `TRD/BE/employee/data-dictionary.md` atau `TRD/FE/employee/infrastructure.md`):
- **`data-dictionary.md`**: Berisi *whitelist enum*, kamus status (lifecycle data), dan standar *magic string*. Di BE ini menjadi acuan validasi & tipe DB, sementara di FE menjadi acuan *dropdown options* & *state mapping*.
- **`infrastructure.md`**: Penjelasan interaksi dengan infrastruktur eksternal/pihak ketiga. Di BE contohnya: arsitektur *bucket* MinIO atau Redis. Di FE contohnya: integrasi CDN khusus, WebSockets, atau konfigurasi SDK eksternal spesifik domain.

## 3. Database Markup (DBML)
- Skema database relasional **WAJIB** ditulis dalam format DBML (`.dbml`).
- Disimpan di folder `TRD/BE/databases/` (contoh: `TRD/BE/databases/employee.dbml`).
- DBML adalah **sumber tunggal** migrasi SQL dan perancangan *database* di tim BE. Data *dummy* tabel di PRD **tidak** menggantikan struktur DBML. 
- Gunakan *skill* `scaffold-dbml` untuk menerjemahkan bab "Data Schema" di PRD menjadi DBML fisik yang presisi.
