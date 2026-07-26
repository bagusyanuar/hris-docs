---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26 20:30:00
references_prd: https://github.com/bagusyanuar/hris-docs/blob/main/PRD/auth.md
references_trd_be: https://github.com/bagusyanuar/hris-docs/blob/main/TRD/BE/auth/tech-spec.md
---

# TRD Frontend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **Mode Rendering:** **SPA (ssr=false)** menggunakan `adapter-static`.
- **Penerjemahan Bisnis ke Teknis:** Sesuai arahan PRD untuk menciptakan antarmuka yang mengelola *"Sesi Pengguna Secara Aman"* tanpa membocorkan data ke pihak ketiga, TRD ini mendesain *state management* dengan **Svelte 5 Runes** dan pengamanan rute secara murni di klien (*Client-Side Route Guards*).

## 2. Pemetaan Rute (Routing & Layouts)

| URL Path | Tipe Akses | Konteks Layout | Penerjemahan Bisnis |
|----------|------------|----------------|---------------------|
| `/login` | Public | *Blank/Auth Layout* | Pintu gerbang utama. Me-redirect *user* yang sudah bersesi aktif ke *Dashboard*. |

## 3. Persyaratan Interaksi UI (UI Behavior)

Berdasarkan *Skenario 1* dan *Skenario 6* pada PRD:
- **Penanganan Form:** Komponen UI Login harus mengikat form input Email dan Password ke *Superforms* untuk reaktivitas *state* dan validasi sisi klien.
- **Loading State:** Tombol "Masuk" (Submit) wajib memiliki *state* `disabled` dan `loading` saat proses pemanggilan API Login berlangsung, guna mencegah *double-submit*.
- **Notifikasi Error (Toast/Alert):** Jika gagal login (kredensial salah / akun non-aktif), UI harus menangkap *response API 401* dan menampilkannya sebagai pesan merah (*"Kredensial tidak valid"* / *"Akun tidak aktif"*).

## 4. State Management & Reaktivitas (Svelte 5)

Menerjemahkan fitur *"Penciptaan Sesi Pengguna"* (Skenario 1 PRD):
- Menggunakan **Svelte 5 Runes** (`$state`, `$derived`).
- Pasca login sukses (API merespon `200 OK`), `access_token` yang didapat dari *response payload* tidak boleh disimpan di `localStorage` (menerjemahkan Non-Functional Requirement pencegahan XSS). Token wajib disimpan ke dalam *global in-memory state* (`authStore.svelte.ts`).
- Cookie `refresh_token` tidak perlu dipedulikan oleh kode Svelte karena *browser* akan menanganinya otomatis (HttpOnly).

## 5. Client-Side Validation

Mengimplementasikan *Skenario 6* PRD secara harafiah di FE sebelum menekan *Backend* untuk menghemat proses jaringan. Dibungkus dalam skema **Zod**:

- **Field Email:**
  - `z.string().email({ message: "Format email tidak valid" })`.
- **Field Password:**
  - Panjang minimal 8 karakter, wajib memiliki 1 huruf kapital, 1 angka, dan 1 karakter spesial.
  - Implementasi regex: `z.string().min(8).regex(/.../, { message: "Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial" })`.

## 6. API Client & Interceptors (Mekanisme Perpanjangan Otomatis)

Menerjemahkan *"Perpanjangan masa aktif sesi secara otomatis"* (Skenario 4 PRD):
- Aplikasi FE akan memiliki sebuah fungsi *Wrapper* / *Interceptor* pada fungsi `fetch()`.
- Jika sebuah *request API* bisnis ditolak dengan `401 Unauthorized` (karena *access_token* kadaluwarsa):
  1. *Interceptor* menahan request tersebut secara *background*.
  2. *Interceptor* diam-diam memanggil endpoint `POST /api/v1/auth/refresh`.
  3. Jika berhasil (200 OK), *access_token* di `authStore` diperbarui, dan *request* yang sempat tertahan di-*retry* secara otomatis.
  4. Pengguna sama sekali tidak merasakan putusnya koneksi. Jika gagal *refresh*, barulah pengguna dilempar (*redirect*) paksa ke `/login`.

## 7. SPA Route Protection (Pengamanan Halaman)

Menerjemahkan *"Pengecekan hak akses terpusat"* (Skenario 5 PRD) dalam konteks SPA murni:
- Karena `ssr=false`, kita tidak menggunakan `hooks.server.ts`.
- **Client-Side Guard:** Logika diletakkan pada fungsi `load()` di dalam `src/routes/(app)/+layout.ts`.
- Fungsi `load()` akan mengecek apakah state in-memory `access_token` eksis. Jika tidak eksis, *SvelteKit* akan melempar kode `redirect(302, '/login')` di *browser*.

## 8. Data Mocking (Tahap Development)

Untuk memampukan tim FE bekerja saat BE belum ada, proyek ini menggunakan **Clean Architecture (Dependency Injection)** alih-alih alat eksternal seperti MSW:
- **Mock Repository:** Tim FE wajib membuat *interface* (Port) untuk fungsi API. Akan ada dua implementasi: `AuthApiRepository` (memanggil HTTP asli ke Backend) dan `AuthMockRepository` (mengembalikan Promise statis/dummy dengan jeda waktu simulasi).
- **Domain-Level Flagging (useMock):** Pemilihan repositori dikendalikan secara manual (di-*hardcode*) di level *Dependency Injection Container* khusus untuk domain Auth. Kita **tidak** menggunakan variabel `.env` global, agar modul Auth bisa menggunakan *mock data* sementara modul lain yang API-nya sudah rampung (misal modul Karyawan) bisa memanggil API asli secara bersamaan.
