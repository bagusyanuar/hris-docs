# Infrastructure & Tooling: Auth Frontend

Dokumen infrastruktur pendukung spesifik untuk pengembangan Frontend modul Auth.

## 1. Konfigurasi Dependency Injection (Mocking)

Agar tim Frontend (Svelte) bisa berlari mengimplementasikan alur "Perpanjangan Sesi" tanpa menunggu API Backend, proyek menerapkan arsitektur *Dependency Injection* murni tanpa membebani *browser* dengan *Service Worker* pihak ketiga.

- **Domain-Level Flag:** Disediakan *flag* lokal `useMock` di dalam *Dependency Injection Container* (Context/Factory) khusus untuk modul Auth. Variabel global `.env` secara tegas tidak digunakan agar tidak berdampak ke modul/domain lain.
- **Dependency Injection:** Jika *flag* lokal tersebut bernilai `true`, kelas `AuthMockRepository` akan disuntikkan ke dalam *Use Case* komponen. Jika `false`, akan menggunakan kelas API aslinya.
- **Simulasi Interceptor (Rotasi Token) di Level Kode:**
  - `AuthMockRepository` akan di-*hardcode* untuk sengaja me-*return* *Promise reject* `401 Unauthorized` pada simulasi panggil API pertama.
  - Penolakan *Promise* ini akan ditangkap otomatis oleh fungsi *Interceptor*, yang kemudian men- *trigger* pemanggilan fungsi `refresh()` pada repositori yang sama.
  - Seluruh alur kompleks ini beroperasi murni di JavaScript *runtime* tanpa satu pun *request* yang bocor ke *network tab*.

## 2. CI/CD Static Adapter

Karena *Decision Log* menetapkan aplikasi berjalan sebagai SPA murni tanpa *Node server* (`ssr=false`), maka proses kompilasi infrastruktur akan berjalan seperti ini:

- **Build Command:** `vite build` akan membuahkan sebuah folder `build/` yang hanya berisi *File Statis* (`.html`, `.js`, `.css`, gambar).
- **Deployment:** Folder statis tersebut disalin (misalnya via *GitHub Actions*) langsung ke penyimpanan statis infrastruktur seperti AWS S3 Bucket, Nginx Web Server, atau Cloudflare Pages.
- **Konsekuensi Fallback:** Konfigurasi infrastruktur (misalnya Nginx) WAJIB mengarahkan seluruh rute 404 kembali ke `index.html` (SPAs fallback), agar SvelteKit Client Router bisa mengambil alih dan mengecek memori otorisasi pengguna (`+layout.ts`).
