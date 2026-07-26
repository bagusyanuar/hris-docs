# Architecture Decision Record (ADR): Auth Backend

## 1. Penggunaan Stateless JWT (Mengeliminasi Redis)
- **Konteks:** PRD mengharuskan kita mengelola sesi pengguna, namun mensyaratkan arsitektur tanpa jejak untuk efisiensi (*Stateless*).
- **Keputusan:** Kita menggunakan JSON Web Token (JWT) yang di-*sign* dengan `HS256`. Token tidak disimpan sama sekali di dalam database (baik PostgreSQL maupun Redis).
- **Alasan:** 
  1. *Cost-efficiency*: Tidak perlu memelihara *cluster* Redis hanya untuk menampung data sesi.
  2. *Scalability*: Fiber API bisa di- *scale horizontal* (tambah *pod*) tanpa perlu pusing sinkronisasi state.
- **Konsekuensi:** Kita kehilangan kemampuan *Server-Side Token Revocation* (Logout paksa jarak jauh sebelum token *expired*). PRD sudah secara eksplisit menyetujui batasan (Out-of-Scope) ini.

## 2. Pengamanan Refresh Token via HttpOnly Cookie
- **Konteks:** Menjawab amanat PRD *"Mekanisme penyimpanan sesi harus kebal dari pencurian data XSS"*.
- **Keputusan:** `access_token` berumur sangat pendek (misal: 15 menit) diserahkan ke *memory* klien, namun `refresh_token` berumur panjang (misal: 7 hari) WAJIB dititipkan ke *browser* menggunakan HTTP Header `Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict`.
- **Alasan:** 
  1. `HttpOnly` memastikan script berbahaya (seperti XSS) tidak bisa mengakses nilai token.
  2. Ini adalah standar keamanan tertinggi untuk arsitektur SPA yang berinteraksi dengan API REST.
- **Konsekuensi:** Tim Frontend tidak akan pernah bisa membaca (maupun menyentuh) *refresh token* tersebut via JavaScript. Klien harus bergantung penuh pada *browser* untuk menyertakan cookie setiap kali memanggil endpoint `/refresh`.

## 3. Penyatuan Pesan Error 401
- **Konteks:** Serangan *User Enumeration* sering memanfaatkan kelemahan API yang membocorkan status apakah suatu email terdaftar atau tidak (misal membedakan pesan "Email tidak ditemukan" dan "Sandi salah").
- **Keputusan:** Apapun skenario kegagalan login (baik email tidak ada, maupun sandi meleset), API wajib merespon dengan `401 Unauthorized` dengan pesan statis: `"Kredensial tidak valid"`.
