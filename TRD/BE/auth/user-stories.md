# User Stories (Backend): Auth Module

Dokumen ini mendetailkan skenario penggunaan spesifik (*Use Cases*) dari perspektif sistem backend untuk modul otentikasi.

## 1. Otentikasi Kredensial
- **Sebagai** pengguna terdaftar,
- **Saya ingin** API backend dapat memvalidasi kombinasi *email* dan *password* saya,
- **Sehingga** saya mendapatkan *access token* dan *refresh token* jika kredensial saya benar.
- **Kondisi Batas (Edge Case):** Jika format email tidak valid (bukan email), API harus segera menolak dengan `422 Unprocessable Entity` sebelum kueri ke *database*.

## 2. Pengecekan Status Aktif
- **Sebagai** administrator (via sistem),
- **Saya ingin** backend secara otomatis memblokir akses login bagi akun yang berstatus `inactive` atau `suspended`,
- **Sehingga** mantan karyawan yang di-*offboard* tidak bisa mengakses sistem meskipun mereka masih ingat *password* mereka.

## 3. Rotasi Refresh Token
- **Sebagai** pengguna dengan sesi aktif,
- **Saya ingin** backend memberikan *refresh token* baru setiap kali saya menggunakan *refresh token* lama saya,
- **Sehingga** masa aktif sesi saya diperpanjang dengan aman tanpa perlu mengetik ulang *password*.

## 4. Keamanan Akses Token
- **Sebagai** arsitek keamanan,
- **Saya ingin** API tidak pernah menyimpan atau menerima *access token* melalui parameter URL (hanya via *Authorization header*),
- **Sehingga** token tidak bocor di *log* server.
