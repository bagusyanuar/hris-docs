# Product Requirements Document (PRD): Master Data Wilayah (Geographical Reference Data)

## 1. Overview
Modul Master Data Wilayah bertujuan untuk menyediakan data referensi geografis yang akurat, konsisten, dan terstruktur (hierarkis) untuk seluruh ekosistem HRIS. Data ini akan digunakan secara luas di berbagai form, seperti pendaftaran karyawan, pengisian alamat domisili/KTP, manajemen lokasi cabang kantor, hingga pelaporan perpajakan.
Secara arsitektural, seluruh entitas ini akan dipusatkan ke dalam satu domain khusus yaitu **`internal/region`**.

## 2. Tujuan & Lingkup
- Menyediakan struktur data administratif berjenjang: **Provinsi -> Kota/Kabupaten -> Kecamatan -> Kelurahan/Desa**.
- Memastikan integritas dan keseragaman data lokasi di seluruh sistem dengan menggunakan ID referensi yang pasti (menghindari kesalahan ketik dari input teks bebas/manual).
- Memberikan endpoint API yang efisien dan cepat (mendukung implementasi caching) agar frontend dapat menyajikan *cascading dropdown* (dropdown berjenjang) dengan *user experience* yang optimal.

## 3. User Stories
- **Sebagai Developer/Sistem:** Saat inisialisasi awal (Deployment), saya dapat menjalankan *Database Seeder* untuk memasukkan seluruh data wilayah Indonesia secara otomatis dari sumber data yang valid (seperti BPS), agar sistem siap digunakan tanpa entri manual.
- **Sebagai Karyawan / HR Admin:** Saat mengisi formulir yang membutuhkan alamat lengkap, saya dapat memilih "Provinsi", yang kemudian secara otomatis akan menyaring (filter) pilihan pada *dropdown* "Kota/Kabupaten" sesuai dengan provinsi yang saya pilih, dan berlanjut hingga tingkat Kelurahan.
- **Sebagai Frontend Developer:** Saya membutuhkan *endpoint* API yang terstruktur untuk mengambil daftar provinsi, serta daftar kota, kecamatan, dan kelurahan berdasarkan *parent_id*-nya dengan waktu respons yang sangat cepat.

## 4. Kebutuhan Data (Data Requirements)
Untuk mencegah isu pembaruan data jika terjadi pemekaran wilayah, sistem **wajib menggunakan Surrogate Key (UUID)** sebagai *Primary Key* (`id`), dan menyimpan **Kode Wilayah Administrasi Pemerintahan (Kemendagri)** pada kolom `administrative_code` (Unique).

Struktur hierarki wilayah (Relational Database):
- **Provinces (Provinsi)**: 
  - `id` (UUID, Primary Key)
  - `administrative_code` (String, 2 digit, Unique, ex: "32")
  - `name` (String)
- **Cities (Kota/Kabupaten)**: 
  - `id` (UUID, Primary Key)
  - `province_id` (UUID, Relasi ke Provinces)
  - `administrative_code` (String, 4 digit, Unique, ex: "3273")
  - `name` (String)
- **Districts (Kecamatan)**: 
  - `id` (UUID, Primary Key)
  - `city_id` (UUID, Relasi ke Cities)
  - `administrative_code` (String, 6 digit, Unique, ex: "327305")
  - `name` (String)
- **Sub-districts (Kelurahan/Desa)**: 
  - `id` (UUID, Primary Key)
  - `district_id` (UUID, Relasi ke Districts)
  - `administrative_code` (String, 10 digit, Unique, ex: "3273051001")
  - `name` (String)
  - `postal_code` (String, opsional, Kode Pos)

*Keuntungan menggunakan Kode Kemendagri sebagai ID:*
1. Data pasti unik (tidak ada duplikasi nama wilayah yang membingungkan).
2. Dari ID saja kita sudah tahu hierarkinya (misal kelurahan berawalan `3273` pasti ada di dalam kota `3273`).
3. Saat lapor pajak atau BPJS karyawan, kodenya sudah standar nasional.

*Catatan: Seluruh entitas ini bersifat "Read-Heavy". Proses Create/Update/Delete (CUD) hampir tidak pernah terjadi di operasional harian, kecuali ada kebijakan pemekaran wilayah dari pemerintah pusat.*

## 5. Flow & Interaksi (Cascading Selection)
Alur interaksi pada sisi Frontend (misal pada form Alamat):
1. UI memuat *dropdown* Provinsi dengan melakukan *fetch* ke `GET /api/v1/references/provinces`.
2. Pengguna memilih Provinsi (misal: ID `32` - Jawa Barat).
3. UI mengaktifkan *dropdown* Kota/Kabupaten dan melakukan *fetch* ke `GET /api/v1/references/cities?province_id=32`.
4. Pengguna memilih Kota.
5. Alur yang sama berulang untuk Kecamatan (`GET /api/v1/references/districts?city_id={id}`) dan Kelurahan.

## 6. Di Luar Cakupan (Out of Scope)
- **UI CRUD Wilayah untuk Admin:** Tidak perlu dibuatkan halaman antarmuka (UI) khusus bagi Admin HR untuk menambah, mengubah, atau menghapus data provinsi/kota satu per satu. Perubahan data ini di-*maintain* secara teknis via *Database Seeder* oleh tim IT.
- **Data Internasional:** Pada iterasi rilis pertama ini, struktur hirarki wilayah dioptimalkan secara khusus hanya untuk format wilayah administratif negara Indonesia.
