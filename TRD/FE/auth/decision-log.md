# Architecture Decision Record (ADR) - Frontend Auth

## ADR-001: Penggunaan TanStack Query untuk Autentikasi
- **Status:** Diterima (Accepted)
- **Konteks:** Pemanggilan API Login membutuhkan manajemen *state* asinkron (Loading, Error, Success). Mengatur variabel boolean *loading* secara manual dengan `$state` Svelte akan menghasilkan kode piringan (*boilerplate*).
- **Keputusan:** Menggunakan `createMutation` dari **TanStack Svelte Query** untuk memanggil API `/api/v1/auth/login`.
- **Konsekuensi:** 
  - Penanganan transisi antarmuka (*loading/error*) sangat rapi dan otomatis.
  - Berpotensi *over-engineering* jika hanya untuk satu *endpoint*, namun sangat *worth-it* karena akan menjadi standar arsitektur standar ke depannya.

## ADR-002: Penyimpanan Access Token di Memori Global
- **Status:** Diterima (Accepted)
- **Konteks:** Sistem Frontend (Svelte) menerima `access_token` via *JSON body* dari Backend. Token ini perlu dikirim ke header `Authorization` setiap *request* berikutnya. Jika disimpan di `localStorage`, rentan dicuri lewat celah XSS.
- **Keputusan:** Token akan disimpan di memori *runtime* aplikasi (menggunakan Svelte 5 `$state` global yang di-eksport, misal di `src/lib/stores/auth.svelte.js`).
- **Konsekuensi:** Token aman dari XSS. Namun, jika pengguna me-*refresh* tab browser secara manual (F5), *memory* akan hilang. Solusinya: SvelteKit harus me-*mount* ulang token baru dengan memanggil API `/api/v1/auth/refresh` (yang akan membaca *cookie*) pada fungsi siklus hidup awal (misal di root `+layout.ts`).
