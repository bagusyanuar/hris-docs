# Data Dictionary & Error Mapping: Auth Frontend

Dokumen ini memetakan kode dari Backend menuju antarmuka visual (Svelte) yang dijanjikan dalam PRD.

## 1. Validasi Regular Expression (Regex) Klien

Untuk mengurangi lalu lintas jaringan ke API sesuai *Skenario 6 PRD*, Zod Schema pada SvelteKit Form (*Superforms*) akan menerapkan regex ketat berikut sebelum tombol *submit* bekerja:

| Input Field | Pattern Regex | Pesan Peringatan Klien |
|-------------|---------------|------------------------|
| `email` | `z.string().email()` | `"Format email tidak valid"` |
| `password` | `/^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])(?=.{8,})/` | `"Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial"` |

## 2. Pemetaan API Response ke UI Toast (Alert)

Berdasarkan *API Contract* di TRD Backend, komponen *Notification/Toast* di Frontend harus menafsirkan *error code* sebagai berikut:

| HTTP Status API | Isi Pesan API | Output Visual di Layar Klien |
|-----------------|---------------|------------------------------|
| `200 OK` | (Token) | (Tidak ada alert, *Redirect* ke `/dashboard`) |
| `422 Unprocessable` | "Format email tidak valid" | Tulisan merah berkedip di *bawah* kolom input email. |
| `401 Unauthorized` | "Kredensial tidak valid" | Toast merah melayang di pojok layar: *"Email atau sandi salah"* |
| `401 Unauthorized` | "Akun tidak aktif" | Modal besar/Toast kuning peringatan: *"Akun Anda telah dinonaktifkan. Hubungi HR."* |
| `500 Server Error` | - | Toast darurat: *"Gangguan server internal. Coba beberapa saat lagi."* |
