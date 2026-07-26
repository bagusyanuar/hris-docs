# Data Dictionary: Auth Module (Frontend)

Berikut adalah translasi atau perlakuan data yang dilakukan oleh Svelte Frontend saat menerima respons dari Backend.

## 1. Zod Validation Schema (UI Dictionary)
Batas kaku (kamus validasi) yang diatur di sisi form SvelteKit-Superforms:

| Field UI | Tipe Skema Zod | Keterangan Pesan Error Jika Dilanggar |
|----------|----------------|---------------------------------------|
| `email` | `z.string().email()` | "Format email tidak valid" |
| `password` | `z.string().min(8)` | "Kata sandi minimal 8 karakter" |

## 2. Pemetaan State Otentikasi (Svelte Runes)
Sistem FE akan menyimpan status pengguna (*current user*) secara global:

| Variabel Global Svelte | Tipe Data Asumsi | Sumber Data |
|------------------------|------------------|-------------|
| `currentUser.isAuthenticated` | boolean | Hasil evaluasi keberadaan token. |
| `currentUser.id` | string (UUID) | Di-ekstrak dari `payload.user_id` di dalam token JWT. |
| `currentUser.role` | string | Di-ekstrak dari `payload.role` di dalam token JWT. |

## 3. Kamus Error Lemparan Backend
Pemetaan khusus dari pesan *error* HTTP 401 ke teks yang ramah UX di layar.
- Jika HTTP 401 merespon pesan apapun dari Backend $\rightarrow$ Tampilkan: *"Email atau kata sandi yang Anda masukkan salah, atau akun Anda dinonaktifkan."* (Digeneralisasi demi alasan UX dan privasi).
