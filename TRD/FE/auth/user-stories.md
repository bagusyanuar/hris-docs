# User Stories (Frontend): Auth Module

Dokumen ini mendetailkan skenario penggunaan antarmuka dari perspektif pengguna (*End-User*) untuk modul otentikasi.

## 1. Alur Login Lancar
- **Sebagai** pengguna aplikasi,
- **Saya ingin** melihat peringatan instan (merah) jika format email saya salah *sebelum* saya menekan tombol masuk,
- **Sehingga** saya tidak perlu membuang waktu menunggu respons *loading* dari server untuk kesalahan ketik sepele.

## 2. Pengalaman Loading (*Feedback Loop*)
- **Sebagai** pengguna aplikasi,
- **Saya ingin** tombol masuk berubah menjadi *spinner* (memutar) atau teks "Memproses..." saat saya menekannya,
- **Sehingga** saya tahu sistem sedang bekerja dan saya tidak akan mengklik tombol masuk berkali-kali.

## 3. Penanganan Gagal Login
- **Sebagai** pengguna aplikasi yang lupa kata sandinya,
- **Saya ingin** sistem menampilkan pesan kesalahan merah yang jelas di bawah form (misal: "Kredensial tidak valid"),
- **Sehingga** saya tahu bahwa saya harus mengetik ulang *password* atau email saya.

## 4. Keamanan Sesi (*Invisible Security*)
- **Sebagai** pengguna aplikasi,
- **Saya ingin** tidak pernah berurusan dengan token atau masa aktif teknis,
- **Sehingga** sesi saya tetap menyala secara gaib (*auto-refresh* di *background*) selama saya rutin menggunakan aplikasi dalam 7 hari terakhir.
