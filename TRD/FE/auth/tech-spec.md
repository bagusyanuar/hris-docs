---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26
references_prd: https://github.com/bagusyanuar/hris-docs/blob/main/PRD/auth.md
---

# TRD Frontend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **Fokus Frontend:** Menerjemahkan alur bisnis otentikasi menjadi antarmuka UI Svelte 5 yang reaktif, validasi formulir sisi klien, serta membangun *Interceptor* jaringan untuk perpanjangan token secara *seamless* di latar belakang.

## 2. Tech Stack Svelte 5
- **Framework:** SvelteKit (dikonfigurasi sebagai SPA murni dengan `ssr = false`).
- **State Management:** Svelte 5 Runes (`$state()`, `$derived()`) untuk memori sesi in-browser.
- **Form Validation:** `sveltekit-superforms` dengan resolver Zod.
- **Styling:** Vanilla CSS (berdasarkan keputusan awal proyek).

## 3. Desain Komponen UI
- `src/routes/login/+page.svelte`: Halaman utama login. Menampilkan input email dan password, serta *toast/alert* jika gagal. 
- Komponen harus memiliki *loading state* (tombol berputar/disabled) untuk menghindari *double-submission*.

## 4. Client-Side Validation (Superforms/Zod)
Skema Zod akan menduplikasi logika dari PRD:
- `email`: `z.string().email("Format email tidak valid")`
- `password`: `z.string().min(8).regex(/.../, "Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial")`
Validasi ini langsung tampil di bawah kolom input secara *real-time*.

## 5. State Management & SPA Route Guard
- Setelah token (JWT `access_token`) didapatkan, ia disimpan ke dalam *global store* yang menggunakan Svelte 5 `$state()`. **Dilarang** menyimpannya di `localStorage`!
- Fungsi `load()` pada `src/routes/(app)/+layout.ts` bertindak sebagai penjaga gerbang (Route Guard). Jika variabel memori token kosong, fungsi ini akan langsung melempar aksi `redirect(302, '/login')`.

## 6. HTTP Interceptor & Refresh Token
Sistem Svelte akan dibekali *wrapper* `fetch` yang menangkap respons error jaringan:
- Jika merima status `401 Unauthorized`, *interceptor* akan menahan *request* UI yang gagal.
- Secara diam-diam, FE menembak `POST /api/v1/auth/refresh`.
- Jika berhasil, *access_token* diperbarui di memori, dan *request* asli diulang (*retry*).

## 7. Data Mocking (Clean Architecture & DI)
Untuk memampukan tim FE bekerja (slicing) meskipun API BE belum jadi:
- **Mock Repository:** Dibuat sebuah `AuthMockRepository` yang mengembalikan Promise palsu setelah jeda `setTimeout()`.
- **Flagging (useMock):** Di level *Dependency Injection Container* khusus domain Auth, disediakan flag lokal `const useMock = true`. Jika true, komponen Usecase/UI akan diinjeksi dengan `AuthMockRepository`. Jika false, menggunakan `AuthApiRepository` asli. Menggunakan `.env` global secara tegas dilarang agar tidak merusak modul lain.
