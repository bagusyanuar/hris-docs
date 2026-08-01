# Data Dictionary - Region Module

## 1. Naming & Formatting
Sistem menggunakan `administrative_code` untuk merepresentasikan Kode Wilayah Administrasi Pemerintahan (Kemendagri). Format kode dipastikan bersih dari karakter titik (`.`) saat masuk ke sistem agar penelusuran konsisten.

- **Provinces:** 2 digit string (e.g., `"32"` untuk Jawa Barat).
- **Cities:** 4 digit string (e.g., `"3273"` untuk Kota Bandung).
- **Districts:** 6 digit string (e.g., `"327305"` untuk Kecamatan Cicendo).
- **Sub-districts:** 10 digit string (e.g., `"3273051001"` untuk Kelurahan Arjuna).

## 2. Enums & Lifecycles
Tidak ada siklus (lifecycles) maupun enumerasi status (`active/inactive`) untuk modul wilayah pada iterasi ini. Data dioperasikan secara *hard-delete* apabila terjadi pembaruan langsung dari *Seeder*.

## 3. Error Mappings
- `ErrProvinceNotFound`: Dikembalikan ketika UUID `province_id` tidak eksis. Di-*translate* di layer HTTP menjadi `404 Not Found`.
- `ErrCityNotFound`: Dikembalikan ketika UUID `city_id` tidak eksis.
- `ErrMissingParentID`: Dikembalikan di layer HTTP (`400 Bad Request`) apabila parameter URL seperti `province_id` lupa dikirimkan oleh klien.
