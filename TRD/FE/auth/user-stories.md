# TRD Extension: User Stories (Frontend Auth)

Dokumen ini memecah arsitektur FE menjadi tiket-tiket kerja yang siap dieksekusi, dengan pembagian fase *Slicing* dan *Integration*.

## FASE 1: SLICING [UI & Mocking]
- **Task:** Buat kerangka UI statis (`HTML/CSS`) untuk halaman Login di `src/routes/login/+page.svelte`.
- **Task:** Pasang dan konfigurasi `sveltekit-superforms` dan Zod untuk input `email` dan `password` beserta pesan *error*-nya.
- **Task:** Buat *state management* global menggunakan Svelte 5 Runes (`$state`).
- **Task:** Bangun `AuthMockRepository` (Port/Adapter) untuk meretur simulasi sukses (data dummy token) atau simulasi gagal. Pastikan disuntikkan ke komponen dengan flag lokal `useMock = true`.
- **Task:** Bangun *Route Guard* di `+layout.ts` (uji dengan *mock data*).

## FASE 2: INTEGRATION [Koneksi API Backend Asli]
- **Task:** Balik flag *Dependency Injection* menjadi `useMock = false`.
- **Task:** Buat `AuthApiRepository` yang benar-benar memanggil `fetch()` ke URL BE sesuai panduan di file Swagger.
- **Task:** Implementasikan *HTTP Interceptor* di sisi Svelte untuk merotasi *refresh token* jika menerima error 401.
