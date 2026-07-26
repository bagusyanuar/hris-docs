# Architecture Decision Record (ADR) - Backend Auth

## ADR-001: Penggunaan Stateless JWT vs Stateful Session
- **Status:** Diterima (Accepted)
- **Konteks:** Sistem butuh otentikasi. Stateful session (simpan di Redis/DB) menjamin kontrol pembatalan (revocation) instan, tapi memperlambat performa karena tiap *request* harus kueri ke *cache*.
- **Keputusan:** Menggunakan **Stateless JWT** (HS256).
- **Konsekuensi:** 
  - **Positif:** Peningkatan performa drastis karena validasi (verifikasi *signature*) terjadi murni secara matematis di *Application layer* tanpa kueri I/O.
  - **Negatif:** Token tidak bisa di-*revoke* secara manual sebelum kedaluwarsa. Umur *access_token* harus dibuat pendek (1 jam) untuk mitigasi.

## ADR-002: Penyimpanan Refresh Token di HttpOnly Cookie
- **Status:** Diterima (Accepted)
- **Konteks:** *Refresh token* berumur panjang (misal 7 hari). Jika diletakkan di *body JSON*, *frontend* harus menyimpannya di `localStorage`, yang rentan dicuri lewat serangan *Cross-Site Scripting* (XSS).
- **Keputusan:** API login/refresh akan langsung menyuntikkan *refresh token* via header `Set-Cookie` dengan atribut `HttpOnly`, `Secure`, dan `SameSite=Strict`.
- **Konsekuensi:** Token ini benar-benar tidak bisa diakses oleh *JavaScript frontend*. Mencegah pencurian XSS secara mutlak. Backend harus siap membaca `Cookie` dari header *request*.
