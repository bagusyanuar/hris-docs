# TRD Extension: Infrastructure (Frontend Auth)

Dokumen infrastruktur pendukung spesifik untuk pengembangan Frontend modul Auth.

## 1. Konfigurasi Dependency Injection (Mocking)

Agar tim Frontend (Svelte) bisa berlari mengimplementasikan alur "Perpanjangan Sesi" tanpa menunggu API Backend, proyek menerapkan arsitektur *Dependency Injection* murni.

- **Domain-Level Flag:** Disediakan *flag* lokal `useMock` di dalam *Dependency Injection Container* (Context/Factory) khusus untuk modul Auth. Variabel global `.env` secara tegas tidak digunakan agar tidak berdampak ke modul/domain lain.
- **Dependency Injection:** Jika *flag* lokal tersebut bernilai `true`, kelas `AuthMockRepository` akan disuntikkan ke dalam *Use Case* komponen. Jika `false`, akan menggunakan kelas API aslinya.
- **Simulasi Interceptor (Rotasi Token) di Level Kode:**
  - `AuthMockRepository` akan di-*hardcode* untuk sengaja me-*return* *Promise reject* `401 Unauthorized` pada simulasi panggil API pertama.
  - Penolakan *Promise* ini akan ditangkap otomatis oleh fungsi *Interceptor*, yang kemudian men- *trigger* pemanggilan fungsi `refresh()` pada repositori yang sama.

## 2. CI/CD Static Adapter
Karena aplikasi berjalan sebagai SPA murni (`ssr=false`):
- **Build Command:** `vite build` akan membuahkan sebuah folder `build/` (hanya `.html`, `.js`, `.css`).
- Konfigurasi Web Server (Nginx / S3) **WAJIB** mengarahkan seluruh rute `404 Not Found` kembali ke `index.html` (Fallback SPA). Hal ini krusial agar SvelteKit Client Router bisa mengambil alih dan menjalankan skrip *Route Guard* di `+layout.ts`.

## 3. Swagger API Contracts
- Tim FE diwajibkan untuk meninjau struktur JSON asli API Backend melalui file `swagger.json`.
- File *swagger* ini tersentralisasi di dalam direktori `hris-docs/API_CONTRACTS/` milik tim. Pastikan memeriksa URL tersebut untuk membangun *Data Mapper* di `AuthApiRepository` saat tahap integrasi.
