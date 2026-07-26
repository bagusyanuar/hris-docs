# Infrastructure: Auth Module (Backend)

Dokumen ini menjelaskan interaksi arsitektur infrastruktur eksternal yang berhubungan dengan fungsi otentikasi.

## 1. Konektivitas Database
- **Primary Database:** PostgreSQL
- **Pola Akses:** Modul Auth melakukan operasi **BACA SAJA (Read-Only)** terhadap tabel `users`. Ia tidak pernah melakukan `INSERT`, `UPDATE`, atau `DELETE`.

## 2. Manajemen Key Kriptografi (Secrets)
- JWT ditandatangani menggunakan algoritma HMAC SHA-256 (`HS256`).
- Kunci penandatangan (*Signing Key / Secret*) **TIDAK BOLEH** di-*hardcode* di dalam basis kode.
- Kunci harus diekstrak dari **Environment Variable** (`JWT_SECRET`) saat aplikasi dimuat menggunakan *Viper*.
- Jika *secret* ini berubah/diganti di *environment server*, maka **seluruh** *access token* dan *refresh token* yang sedang beredar di pengguna akan seketika dianggap tidak valid (otomatis *force logout* masal).

## 3. Topologi Cache / Redis (Future-Proofing)
- **Saat Ini:** Tidak ada penyimpanan *state* di Redis (Murni Stateless JWT).
- **Rencana Skalabilitas:** Jika di masa depan sistem mewajibkan fitur **Force Logout** (pembatalan token sebelum expired), maka infrastruktur Redis akan ditambahkan sebagai lapis filter (Token Blacklist / Denylist).
