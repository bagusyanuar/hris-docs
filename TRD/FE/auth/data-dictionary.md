# TRD Extension: Data Dictionary (Frontend Auth)

Dokumen ini memuat konstanta, *magic strings*, dan pemetaan *error* yang penting untuk antarmuka.

## 1. Zod Validation Error Messages
Sesuai dengan Skenario 6 di PRD, berikut adalah *string* pesan mutlak yang **wajib** tampil secara *real-time* (Sisi Klien):
- Email tidak punya lambang `@` -> `"Format email tidak valid"`
- Password lemah -> `"Password minimal 8 karakter, wajib mengandung huruf kapital, angka, dan karakter spesial"`

## 2. API Error Message Mapping
Jika API mengembalikan kegagalan (dari respon Backend Swagger), UI harus menampilkannya dengan rapi di komponen Toast/Alert merah:
- `422` atau `401` dengan pesan *"Kredensial tidak valid"* -> Tampilkan peringatan gagal login yang umum (jangan tunjukkan field mana yang salah).
- `401` dengan pesan *"Akun tidak aktif"* -> Tampilkan pesan bahwa akun di- *suspend*.

## 3. Konstanta Mock
- `MOCK_DELAY_MS = 1500`: Jeda waktu statis (1.5 detik) yang digunakan oleh `AuthMockRepository` untuk menyimulasikan kecepatan jaringan riil (memberi ruang bagi tombol *Loading* UI untuk berputar).
