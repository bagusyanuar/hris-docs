---
module: Auth
version: 1.0.0
status: Draft
owner: bagusyanuar
updated: 2026-07-26 13:17:00
references_prd: ../../../PRD/auth.md
references_trd_be: ../../BE/auth/tech-spec.md
references_design: -
---

# TRD Frontend: Auth Module

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [PRD/auth.md](../../../PRD/auth.md)
- **Versi PRD:** v1.0.0
- **TRD BE (API):** [BE/auth/tech-spec.md](../../BE/auth/tech-spec.md)
- **Ringkasan:** Rancang bangun *interface* otentikasi bagi pengguna (Halaman Login). Modul ini menangani form *input* kredensial, validasi klien, pemanggilan API *Login*, dan pengamanan akses halaman terproteksi di sisi Frontend (Svelte 5).

## 2. Pemetaan Rute (Routing & Layouts)

SvelteKit akan dikonfigurasi dengan *route* spesifik untuk otentikasi.

| URL Path | Komponen Halaman (Page) | Layout Pembungkus | Keterangan |
|----------|-------------------------|-------------------|------------|
| `/login` | `src/routes/login/+page.svelte` | `AuthLayout.svelte` | Halaman utama login. *Layout* ini tidak memiliki *sidebar/navbar* utama. |

## 3. Arsitektur Komponen Svelte

Memanfaatkan Bits-UI dan Tailwind v4. Komponen akan difokuskan untuk form interaktif.

- **`<LoginForm />`**: Komponen pengambil data (Smart).
  - **Dependencies**: Terhubung ke *Superforms* dan *Zod* schema.
  - **State ($state)**: Terikat penuh ke fungsionalitas SvelteKit-Superforms untuk reaktivitas *field* (Email & Password).
  - **Behavior**: Menangani siklus *Submit* ke API via *TanStack Query Mutation*.
- **`<AuthAlert />`**: Komponen presentasional (Dumb).
  - **Props**: `type` ("error"|"success"), `message`.
  - **Behavior**: Menampilkan notifikasi kegagalan login (misal: "Invalid credentials").

## 4. State Management & Reaktivitas

- **Form State:** Dikelola menggunakan *SvelteKit-Superforms*. Setiap ketikan *user* akan dievaluasi *Zod*.
- **Data Fetching (API Call):** Memanggil *endpoint* `POST /api/v1/auth/login` menggunakan *TanStack Svelte Query* (`createMutation`). UI akan bereaksi secara asinkron (tombol berubah *disabled*/*loading* saat API berproses).
- **Global Auth State:** Setelah berhasil, `access_token` yang diterima akan diekstrak *payload*-nya (untuk mendapat *role* dan `user_id`), lalu disimpan di memori global Svelte 5 (misalnya dalam `authStore.svelte.js` yang mengekspor `$state` `currentUser`). Cookie `refresh_token` otomatis ditangani oleh *browser*.

## 5. Client-Side Validation

Validasi awal dilakukan sebelum *request* dikirim ke Backend guna mengurangi beban server. Akan dibungkus dalam skema *Zod*.

- **Field Email:**
  - Wajib diisi.
  - Wajib berformat *email* valid (`z.string().email()`).
- **Field Password:**
  - Wajib diisi.
  - Panjang minimal 8 karakter (`z.string().min(8)`).
- **Error Display:** Pesan *error* warna merah akan langsung muncul di bawah masing-masing kolom input sesaat setelah pengguna berinteraksi (*on-blur* atau saat ditekan *submit*).
