# User Stories: Auth Module (Frontend)

Dokumen ini memecah spesifikasi teknis dari `tech-spec.md` menjadi tiket kerja untuk tim Svelte Frontend.

## 1. Komponen Antarmuka (Form Login)
- **Sebagai** pengguna,
- **Saya ingin** melihat halaman form dengan *input* email dan password,
- **Sehingga** saya bisa memasukkan data profil saya untuk masuk ke sistem.
- **Kriteria Penerimaan (AC):**
  - Pembuatan rute `/login`.
  - Integrasikan library Zod dengan *Superforms* untuk form validation di klien.
  - Implementasikan validasi wajib: email format, dan pola kekuatan password sesuai regex.

## 2. Reaktivitas Mutasi API & Loading State
- **Sebagai** pengguna yang tak sabaran,
- **Saya ingin** tombol login menampilkan status *"Loading..."* setelah saya klik,
- **Sehingga** saya tidak menekan tombol itu berkali-kali.
- **Kriteria Penerimaan (AC):**
  - Implementasikan *Svelte Query Mutation*.
  - *Bind state `isPending`* dari Query ke komponen *Button submit*.
  - Tangkap error `401`/`422` dan terjemahkan menjadi notifikasi/Toast bewarna merah.

## 3. Penyimpanan Global State (Runes)
- **Sebagai** sistem SPA,
- **Saya ingin** menyimpan status bahwa pengguna telah *login* ke memori global,
- **Sehingga** seluruh komponen di halaman *Dashboard* tahu siapa pengguna tersebut.
- **Kriteria Penerimaan (AC):**
  - Buat `authStore.svelte.ts` dengan variabel `$state` `currentUser` dan `accessToken`.
  - Jangan simpan token ini ke `localStorage` (hanya di memori *Runtime* JS).

## 4. Mekanisme Refresh Token (Background)
- **Sebagai** karyawan yang bekerja berjam-jam,
- **Saya ingin** sesi saya tetap menyala otomatis,
- **Sehingga** saya tidak perlu login ulang di tengah presentasi.
- **Kriteria Penerimaan (AC):**
  - Buat fungsi pembungkus *fetch API (Interceptor)*.
  - Jaring *error response* `401`. Tahan antrean *request* aslinya.
  - Panggil endpoint `/refresh` secara asinkron.
  - *Retry request* asli jika refresh sukses.
  - *Redirect* ke `/login` jika refresh ditolak.
