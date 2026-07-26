# TRD Extension: Decision Log (Backend Auth)

Dokumen ini mencatat keputusan arsitektural (ADR) mengapa teknologi atau pola tertentu dipilih.

## ADR-001: Penggunaan Stateless JWT
- **Konteks:** Perlu mekanisme otentikasi yang ringan dan skalabel untuk seluruh API.
- **Keputusan:** Menggunakan **Stateless JWT (JSON Web Token)** daripada *Session ID* berbasis *database* (seperti Redis).
- **Alasan:** Menghindari *bottleneck* I/O pada *database* saat pengecekan hak akses di setiap *request* (*Access Control*).

## ADR-002: Refresh Token Rotation di HttpOnly Cookie
- **Konteks:** Token JWT panjang (misal 30 hari) berbahaya jika dicuri via XSS.
- **Keputusan:** *Access token* berumur pendek (misal 15 menit) dikirim di JSON, sedangkan *refresh token* berumur panjang dikirim murni via `HttpOnly` Cookie.
- **Alasan:** Melindungi token jangka panjang dari eksploitasi JavaScript pihak ketiga di browser (XSS).

## ADR-003: Swagger sebagai Single Source of Truth
- **Konteks:** Dokumentasi API (JSON payload) di Markdown cepat kedaluwarsa.
- **Keputusan:** Tim BE wajib mengekspor Swagger dan menyimpannya di `API_CONTRACTS/` repositori `hris-docs`. TRD hanya memuat tautan Swagger.
- **Alasan:** Mencegah *stale documentation* (dokumen basi) yang dapat mengganggu integrasi tim FE.
