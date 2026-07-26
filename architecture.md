# Arsitektur Global & Tech Stack Sistem HRIS

Dokumen ini adalah ringkasan arsitektur tingkat tinggi (*High-Level Architecture*) yang menggerakkan seluruh ekosistem aplikasi HRIS kita. Setiap *engineer* atau perancang dokumen di **hris-docs** harus memahami batasan teknologi ini sebelum menyusun spesifikasi teknis (TRD).

---

## 1. Topologi Repositori & Pemisahan Fokus

Ekosistem HRIS kita beroperasi secara terdistribusi di tiga *workspace* (repositori) utama:
- **`hris-docs`**: *Control Plane*. Menyimpan PRD (Bisnis) dan TRD (Desain Teknis) untuk menjaga *Single Source of Truth*.
- **`hris-backend`**: Repositori kode murni untuk *server-side logic* dan interaksi *database*.
- **`hris-frontend`**: Repositori kode murni untuk *client-side logic* dan interaksi antarmuka pengguna (UI/UX).

Kesepakatan interaksi (Kontrak):
> Frontend dan Backend berjalan secara terpisah (*headless*) dan **hanya** berkomunikasi melalui RESTful API berformat JSON.

---

## 2. Tech Stack Backend (`hris-backend`)
Tim Backend menggunakan tumpukan teknologi (berbasis `go.mod` *existing*) yang memprioritaskan arsitektur terstruktur (DDD) dan performa tinggi.

- **Bahasa**: Golang (v1.26+)
- **Arsitektur Kode**: Domain-Driven Design (DDD). Dibagi menjadi *layer*: Domain, Application, Adapter, Transport.
- **Web Framework**: Gofiber (v3) untuk *routing* dan HTTP *handling*.
- **Database ORM & Driver**: GORM dengan PostgreSQL.
- **Dependency Injection**: Google Wire (`github.com/google/wire`).
- **Autentikasi**: JWT (`golang-jwt/jwt/v5`).
- **Validasi Data**: Go-Playground Validator.
- **Manajemen Konfigurasi**: Viper.
- **Logging**: Uber Zap (Terstruktur).
- **Primary Key**: UUID (di-*generate* di level aplikasi/Go, bukan DB).

---

## 3. Tech Stack Frontend (`hris-frontend`)
Tim Frontend menggunakan tumpukan teknologi modern (berbasis `package.json` *existing*) yang memprioritaskan reaktivitas tingkat tinggi dan *type-safety*.

- **Framework Inti**: Svelte 5 (menggunakan *Runes* untuk *state management*) dan SvelteKit (App Router & SSR/SSG).
- **Bahasa**: TypeScript (`typescript-eslint`).
- **Styling**: Tailwind CSS v4.
- **Komponen UI**: Bits-UI (Headless UI).
- **Form & Validasi**: SvelteKit-Superforms dipadukan dengan **Zod** untuk validasi skema.
- **Manajemen Data / Fetching**: 
  - TanStack Query (`@tanstack/svelte-query`) untuk *caching* dan siklus asinkronus (Loading/Error/Success).
  - Axios untuk HTTP *client*.
- **Tabel Data**: TanStack Table v8.
- **Testing & Storybook**: 
  - Vitest (Unit Test) & Playwright (E2E Test).
  - Storybook (Komponen UI terisolasi).

---

## 4. Panduan Desain (Untuk Agen & Perancang Dokumen)

Mengingat *stack* di atas sangat spesifik, setiap merancang TRD di `hris-docs/TRD/`, patuhi aturan ini:
1. **Frontend**: Saat merancang UI, manfaatkan *Zod* di TRD untuk kriteria *client-side validation*. Manfaatkan *Tanstack Query* untuk mengelola state transisi pemuatan data. 
2. **Backend**: Saat merancang API, sadari bahwa *payload* JSON akan divalidasi dengan sangat ketat (Zod di FE, Validator di BE). Struktur DBML harus merepresentasikan tabel fisik PostgreSQL yang tangguh.
