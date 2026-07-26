# TRD Extension: Decision Log (Frontend Auth)

Dokumen ini mencatat keputusan arsitektural (ADR) mengapa teknologi atau pola tertentu dipilih di FE.

## ADR-001: Aplikasi SPA Murni (ssr=false)
- **Konteks:** SvelteKit menawarkan mode *Server-Side Rendering* (SSR) yang bertenaga, tapi butuh *server* Node.js untuk berjalan.
- **Keputusan:** Fitur SSR dimatikan sepenuhnya (`export const ssr = false` di layout root).
- **Alasan:** HRIS adalah aplikasi internal yang tidak membutuhkan SEO (Search Engine Optimization). Menjadikannya SPA (Static Site) membuatnya sangat ringan dan bisa di-*deploy* ke CDN statis seperti S3 / Cloudflare Pages.

## ADR-002: Token Disimpan di In-Memory State (Runes)
- **Konteks:** *Access token* (JWT) perlu disimpan di sisi *client* untuk dikirim di setiap *request*.
- **Keputusan:** Token murni disimpan dalam variabel RAM (*Runes state*). Dilarang keras menyimpannya di `localStorage` atau `sessionStorage`.
- **Alasan:** Keamanan. Menyimpan di memori browser melumpuhkan potensi eksploitasi kode jahat (XSS) secara total, sambil mengandalkan HttpOnly Cookie untuk rotasi jangka panjang.

## ADR-003: DI Mocking vs MSW
- **Konteks:** Tim FE butuh men-*develop* UI sebelum API BE siap.
- **Keputusan:** Menggunakan *Dependency Injection Container* dengan repositori Mock, membuang MSW.
- **Alasan:** Clean Architecture membuat kode FE modular, *strongly-typed*, dan *immune* terhadap perubahan JSON API BE di masa depan. Flag `useMock` di level domain tidak akan mengganggu tim lain.
