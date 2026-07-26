# Infrastructure & Deployment: Auth Backend

Dokumen ini menjelaskan integrasi eksternal dan kebutuhan tingkat sistem (*system-level requirements*) untuk modul Auth.

## 1. Secret Management (Kunci Kriptografi)

Modul otentikasi membutuhkan manajemen rahasia infrastruktur yang ketat. Kunci (*Key*) yang digunakan untuk menandatangani algoritma `HS256` JWT tidak boleh di- *hardcode* dalam repositori (baik dalam bentuk *plaintext* maupun `.env.example`).

- **Variabel Server:** `JWT_SECRET_KEY`
- **Tipe Integrasi:** Docker Environment Variable / Kubernetes Secrets.
- **Kriteria Kunci:** String acak (Base64 atau alfanumerik panjang) minimal 256-bit (32 karakter).
- **Prosedur Pembaruan (Key Rotation):** Jika kunci ini diganti di level infrastruktur server (misal karena dugaan peretasan), maka **seluruh token pengguna** yang sedang *login* saat itu di seluruh dunia akan mendadak ter-invalidasi secara massal dan semua *user* dipaksa *login* ulang.

## 2. Ketiadaan Ekosistem Caching (Redis)

Sesuai keputusan di *Decision Log*, infrastruktur **tidak perlu menyiapkan instance Redis** khusus untuk modul Auth. 
- *Server* Go murni bersifat komputasional (*hashing* & verifikasi JWT). 
- Jika trafik login naik tajam, penambahan kapasitas hanya butuh menaikkan replika kontainer (Docker) Go, tanpa pusing memikirkan hambatan di memori terpusat.

## 3. Konfigurasi Domain untuk Cookie (CORS)

Karena kita menggunakan strategi perpanjangan sesi via *Cookie*, tim infrastruktur/DevOps wajib mengatur domain:
- Konfigurasi `SameSite=Strict` pada Cookie JWT mengharuskan Frontend (Aplikasi Svelte) dan Backend (API Golang) berada di payung TLD/Subdomain yang saling mengizinkan, atau dikelola melalui aturan konfigurasi *reverse proxy* (contoh: Nginx/Traefik).
- Jika beroperasi beda domain secara ekstrem (misal Frontend di `app.com`, Backend di `api.org`), konfigurasi Cookie harus diturunkan minimal menjadi `SameSite=None` dengan SSL mutlak, yang mana bukan kondisi ideal berdasarkan PRD keamanan.
