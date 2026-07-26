# Data Dictionary: Auth Module (Backend)

Modul Auth tidak memiliki tabel mandiri, namun memiliki kamus data virtual (konstanta/enum) dan ketergantungan erat pada kamus dari tabel `users`.

## 1. Status Pengguna (User Status)
Diambil dari tabel `users` (dikelola oleh Modul User). Modul Auth secara ketat menggunakan kamus nilai berikut untuk mengevaluasi gerbang *login*:

| Status / Value | Klasifikasi Login | Tindakan Auth |
|----------------|-------------------|---------------|
| `active`       | Lolos (Pass)      | Cek *password*. Jika cocok, terbitkan JWT. |
| `inactive`     | Gagal (Reject)    | Tolak seketika dengan `401 Unauthorized`. |
| `suspended`    | Gagal (Reject)    | Tolak seketika dengan `401 Unauthorized`. |

## 2. Struktur Payload JWT (Klaim)
Standar penamaan *key* di dalam JSON Web Token:

| Key | Tipe Data | Deskripsi & Validasi |
|-----|-----------|----------------------|
| `user_id` | string (UUID) | Identitas utama yang akan di-*inject* ke *Request Context*. |
| `role` | string | Role pengguna (sementara *hardcoded* "employee"). |
| `type` | string (enum) | Wajib bernilai `"access"` atau `"refresh"`. |
| `exp` | integer | Epoch Unix timestamp batas kedaluwarsa. |

## 3. Pesan Error Standar (Magic Strings)
Dilarang mem-*bypass* pesan ini untuk menghindari *Information Leak*.

- `ErrInvalidCredentials`: *"Invalid credentials"* (Dipakai jika email tidak ketemu ATAU *password* salah).
- `ErrTokenExpired`: *"Invalid or expired token"* (Dipakai jika JWT melewati masa `exp`).
