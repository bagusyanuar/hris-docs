# User Stories & Engineering Tasks - Bank Module

File ini digunakan untuk membuat sub-task di *GitHub Issues*.

## Task 1: Scaffolding Domain & Entity
- Buat entitas `Bank` di `internal/bank/domain/bank.go`.
- Definisikan *interface* repository untuk `FindAll` (dengan dukungan parameter `search`).

## Task 2: Database Migration & Seeder
- Buat migrasi SQL (`UP` dan `DOWN`) untuk tabel `banks`.
- Buat file *seeder* yang minimal memasukkan 10-20 bank terbesar di Indonesia (BCA, Mandiri, BNI, BRI, BSI, CIMB Niaga, dll) beserta *bank code* mereka.

## Task 3: Postgres Repository Implementation
- Implementasikan pembacaan data bank di `internal/bank/adapter/postgres/bank_repo.go`.
- Integrasikan dengan `pkg/pagination` agar mendukung fitur pencarian nama bank (*search*).

## Task 4: Application Use Case & HTTP Delivery
- Buat `GetBanksUseCase` di `internal/bank/application/`.
- Buat `BankHandler` di `internal/bank/adapter/http/` dengan rute `/api/v1/references/banks`.
- Tambahkan *HTTP Caching Header*.

## Task 5: Dependency Injection & Documentation
- *Wiring* modul bank ke *router* utama.
- Ekspor *Swagger Specs* (YAML) dan koleksi *Bruno*.
