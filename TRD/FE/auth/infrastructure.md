# Infrastructure: Auth Module (Frontend)

Dokumen ini menjelaskan integrasi dan perilaku infrastruktur lapisan klien yang terkait dengan fungsi otentikasi.

## 1. SvelteKit SSR (Server-Side Rendering) vs Browser
- Proses penangkapan JWT Payload dilakukan secara *hybrid*.
- Jika pengguna pertama kali membuka aplikasi, fitur SSR SvelteKit (via fungsi `load` di `+layout.server.ts` atau *hooks*) **belum bisa** membaca *access token* karena itu disimpan di memori klien.
- SSR hanya bisa membaca *cookie* `refresh_token`. SvelteKit harus dikonfigurasikan agar mampu meminta rotasi token *di sisi server* untuk melakukan rehidrasi (*rehydration*) akses login sebelum halaman dirender.

## 2. Interaksi HTTP Client (Axios / Fetch)
- Komponen Svelte tidak pernah menyentuh fungsi `fetch` murni secara langsung.
- Semua *request* jaringan FE dialirkan melalui `Axios Interceptor`.
- **Interceptor Request:** Mengambil token dari memori `$state` dan menempelkannya ke `Authorization: Bearer ...` secara otomatis.
- **Interceptor Response:** Jika API mengembalikan HTTP `401 Expired`, FE secara diam-diam (*silent*) akan menembak `/api/v1/auth/refresh` lalu mengulang kembali *request* awal yang terputus tersebut.

## 3. Cookie Storage (Infrastruktur Browser)
- Frontend **tidak diizinkan** melakukan injeksi `document.cookie`.
- Frontend sepenuhnya bergantung pada mekanisme respons infrastruktur *Browser* modern (Chrome/Safari) yang akan menyimpan secara otomatis header `Set-Cookie` dari Backend, selama atribut CORS API di-*set* mengizinkan `credentials: include`.
