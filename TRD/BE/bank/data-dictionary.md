# Data Dictionary - Bank Module

## 1. Naming & Formatting
- **bank_code:** Disimpan murni sebagai angka/string numerik (contoh: `"014"` untuk BCA).
- **swift_code:** Menggunakan standar 8 atau 11 karakter alfanumerik kapital (contoh: `"CENAIDJA"`).
- **name:** Ditulis menggunakan standar kapitalisasi penulisan nama perusahaan/brand (contoh: `"Bank Mandiri"`).

## 2. Enums & Lifecycles
- `is_active` (boolean): `true` menandakan bank tersebut masih beroperasi dan bisa dipilih oleh karyawan baru. `false` menandakan bank telah tutup atau merger (karyawan lama yang masih menggunakan bank ini secara historis tidak akan *error*, tetapi karyawan baru tidak bisa memilih bank ini dari *dropdown*).

## 3. Error Mappings
- `ErrBankNotFound`: Dikembalikan ketika operasi mencari spesifik UUID bank gagal. Di-*translate* di layer HTTP menjadi `404 Not Found`.
