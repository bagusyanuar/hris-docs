# Architecture Decision Record (ADR): Auth Frontend

## 1. Mematikan SSR (Server-Side Rendering) `ssr=false`
- **Konteks:** Ekosistem SvelteKit secara *default* menggunakan kapabilitas Node.js Server untuk me-render HTML awal (*Isomorphic rendering*). Namun aplikasi HRIS adalah *dashboard* tertutup.
- **Keputusan:** Kita mematikan SSR secara eksplisit dengan flag `export const ssr = false;` di root `+layout.ts` dan menggunakan `@sveltejs/adapter-static`. 
- **Alasan:** 
  1. Menghemat biaya operasional arsitektur (tidak butuh *Node server*, cukup ditaruh di CDN/S3).
  2. Mencegah kerumitan manajemen state Auth antara *Server Svelte* dan *Client Browser*.
- **Konsekuensi:** Fitur *Route Guard* tidak bisa menggunakan *middleware* server `hooks.server.ts`. Perlindungan halaman harus dilakukan 100% murni di dalam browser (mengecek *state Runes* di dalam SvelteKit Client Router).

## 2. In-Memory State untuk Access Token (Bukan LocalStorage)
- **Konteks:** PRD mengharuskan perlindungan level maksimal atas bahaya pencurian sesi lewat serangan *Cross-Site Scripting (XSS)*.
- **Keputusan:** Data sensitif `access_token` hanya disimpan dalam variabel memori RAM browser lewat *Runes* (misal `$state accessToken`). Kita dengan sengaja **menolak** menyimpannya ke `window.localStorage` atau `sessionStorage`.
- **Alasan:** Segala hal di `localStorage` sangat mudah di-*scrape* oleh skrip ekstensi atau *malware* pihak ketiga. Di sisi lain, memori JS *runtime* sulit diakses dari luar konteks eksekusi spesifiknya. (Sementara itu, `refresh_token` sudah aman dari JS karena dikawal `HttpOnly`).
- **Konsekuensi:** Jika pengguna me-refresh (*F5*) *browser*, Svelte State akan ter- *reset* (hilang). Interceptor 401 harus secara proaktif sadar akan hal ini, dan harus mendeteksi: "Jika API butuh akses tapi state memori kosong, panggil endpoint `/refresh` di belakang layar untuk menukar *Cookie* menjadi `access_token` memori baru".
