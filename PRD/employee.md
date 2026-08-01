---
module: Employee
version: 1.0.1
status: Draft
owner: bagusyanuar
updated: 2026-08-01 23:00:00
depends_on: [auth@1.0.1, user@1.0.1, organization@1.0.1, workforce-structure@1.0.1, employment-status@1.0.1, bank@1.0.0, region@1.0.0, rbac@1.0.1]
consumed_by: [leave@planned, payroll@planned, attendance@planned, performance@planned]
---

# Product Requirements: Employee Module

> **Catatan grounding:** Dokumen ini migrasi dari `hris-backend/docs/PRD/employee.md` (v2.3.1), sekaligus regrounding total ke kode nyata (`internal/employee/` — domain-first, sudah lengkap domain/application/adapter/transport) dan ke tiga modul Master Data yang landing belakangan: [employment-status.md](employment-status.md), [bank.md](bank.md), [region.md](region.md). Versi di sini di-reset mengikuti konvensi penomoran `hris-docs` (bukan lanjutan v2.3.1 legacy), selaras modul lain yang sudah dimigrasi. Sebagian besar gap yang tercatat di dokumen legacy (layout domain-first, offboarding, riwayat kontrak, dokumen wajib) **sudah ditutup** di kode — gap yang tersisa dicatat eksplisit di Ringkasan Gap.

Modul **Employee** mengelola **data induk (master data) karyawan** sebagai Single Source of Truth kepegawaian — identitas kerja, biodata, kontak, alamat, rekening bank, pendidikan, dokumen, riwayat kontrak, riwayat penempatan, dan data keluarga/tanggungan. Modul ini adalah fondasi bagi seluruh modul operasional turunan (Attendance, Cuti, Payroll, Performance).

---

## 1. Tujuan & Dampak (The "Why")

Menyediakan satu sumber data karyawan yang akurat dan real-time, menggantikan pencatatan manual/Excel. Dampak yang dikejar:

- Pembaruan data karyawan real-time, pencarian profil dari hitungan menit menjadi hitungan detik.
- Fondasi data yang solid dan sadar-cakupan (per-PT, per-cabang) bagi modul operasional turunan.
- Onboarding karyawan baru terstruktur lewat formulir bertahap (simpan per langkah) supaya input panjang tidak hilang di tengah jalan.
- Riwayat karier karyawan (mutasi, promosi, perpanjangan kontrak) tersimpan sebagai jejak audit, bukan ditimpa begitu saja — dibutuhkan Payroll untuk menghitung gaji sesuai posisi pada periode tertentu, dan Performance untuk melihat jejak karier.

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- Data inti kepegawaian (`Employee`): kode karyawan internal, penempatan Jabatan (Job Position), **jenis hubungan kerja** yang dirujuk dari Master Data Status Kepegawaian, dan **status aktif** (lifecycle) — dua sumbu terpisah, lihat §5 — beserta tanggal bergabung.
- **Riwayat kontrak kerja** (1:N): tiap periode/perpanjangan kontrak berjangka direkam terpisah (bukan menimpa), termasuk dokumen kontrak bertanda tangan.
- **Riwayat penempatan** (1:N): setiap perpindahan jabatan, mutasi, atau pindah cabang induk direkam sebagai satu baris riwayat baru bertanggal efektif, bukan menimpa data lama.
- Biodata sipil (`PersonalData`): nama, nomor identitas, jenis kelamin, status pernikahan, status PTKP, agama, **avatar/foto profil**, **nomor NPWP**, **nomor BPJS Kesehatan**, **nomor BPJS Ketenagakerjaan**.
- Kontak (`Contact`: surel + telepon) dan rekening bank untuk transfer gaji, dengan nama bank dirujuk dari Master Data Bank (bukan diketik bebas).
- **Alamat terstruktur** (1:N): alamat sesuai identitas dan alamat domisili terpisah — mencakup kasus pekerja kos/rantau yang domisili berbeda dari identitas — dengan wilayah (provinsi/kota/kecamatan/kelurahan) dirujuk dari Master Data Wilayah.
- **Data keluarga/tanggungan** (1:N): nama, hubungan keluarga, dan nomor identitas anggota keluarga yang jadi tanggungan (dipakai validasi status PTKP dan pendaftaran tanggungan BPJS Kesehatan) — termasuk penanda **kontak darurat**.
- Riwayat pendidikan dan dokumen digital (URL unggahan identitas/ijazah/dll.).
- **Simpan bertahap** saat onboarding (buat data inti dulu, sub-data menyusul per langkah).
- **Offboarding** (Resign/PHK): ubah status menjadi tidak aktif, isi tanggal berhenti, blokir akses masuk (koordinasi ke modul Akun Pengguna). Data hanya dinonaktifkan, tidak dihapus permanen.
- **Reaktivasi**: karyawan yang pernah keluar lalu bergabung kembali diaktifkan ulang dari data lama, bukan didaftarkan sebagai orang baru.
- **Daftar karyawan** dengan halaman bertahap, pencarian, dan urutan.
- **Lihat profil sendiri**: karyawan bisa melihat profil dirinya sendiri.

**Out-of-Scope (TIDAK di modul ini):**
- Perhitungan gaji, tunjangan, pajak penghasilan, iuran BPJS — tanggung jawab **Payroll**.
- Jam masuk/pulang, jadwal shift, pengajuan cuti — tanggung jawab **Attendance / Cuti**.
- Registrasi akun, pemulihan kata sandi, manajemen hak akses tingkat sistem — tanggung jawab **Akun Pengguna / RBAC**.
- Karyawan mengubah data dirinya sendiri beserta alur persetujuannya — fase berikutnya, belum masuk rilis ini.
- Rekrutmen / pelacakan pelamar kerja — tanggung jawab modul **Rekrutmen** (rencana mendatang).
- Pembuatan kode karyawan otomatis berpola — untuk rilis ini diinput manual oleh HR.
- **Rotasi/penempatan operasional harian lintas cabang** (mis. karyawan bertugas di cabang berbeda tiap hari) — tanggung jawab **Attendance & Penjadwalan** (rencana mendatang). Data induk karyawan hanya menyimpan **cabang induk** (tunggal). Jadwal harian per-shift adalah catatan bertanggal milik Attendance, bukan atribut data induk karyawan.
- **Penentuan cabang saat hadir kerja** (di cabang mana kehadiran tercatat hari itu) — tanggung jawab **Attendance** (rencana mendatang), bukan dari cabang induk Employee.
- **Biometrik** (pendaftaran maupun verifikasi kehadiran: pengenalan wajah/sidik jari) — modul/PRD **terpisah** (rencana mendatang), **BUKAN** sub-data Employee, karena data biometrik termasuk data pribadi spesifik yang butuh persetujuan eksplisit, enkripsi, dan kebijakan retensi tersendiri.
- **Multi-cabang struktural permanen** (karyawan resmi memegang dua cabang atau lebih dalam jangka panjang, mis. area manager) — ditunda sampai ada kebutuhan bisnis nyata.
- **Penegakan batas kuota jabatan saat penempatan** (menolak penempatan kalau kuota jabatan penuh) — keputusan kuotanya milik [workforce-structure.md](workforce-structure.md), penegakannya jadi tanggung jawab modul ini + RBAC, tercatat sebagai gap (lihat Ringkasan Gap).

---

## 3. User Roles & Permissions

| Role | Read | Create | Update | Offboard |
|------|------|--------|--------|----------|
| Superadmin / HR Manager | ✅ semua karyawan (dalam cakupan PT/cabang miliknya) | ✅ | ✅ | ✅ |
| Karyawan (ESS) | ✅ **profil diri sendiri saja** | ❌ | ❌ (belum ada di rilis ini) | ❌ |

- **Rilis ini:** karyawan **tidak** boleh mengubah data sendiri. Semua perubahan lewat permintaan manual ke HR. Alur persetujuan swalayan belum masuk rilis ini.
- **Penegakan cakupan:** HR Manager hanya melihat/mengubah karyawan dalam cakupan PT/cabang miliknya (lihat [rbac.md](rbac.md) §5). Owner/Admin Grup = cakupan kosong = semua PT dan cabang.

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

**Skenario 1: Validasi Duplikasi Nomor Identitas**
- **Given** HR sedang mengisi biodata karyawan.
- **When** memasukkan nomor identitas (KTP) yang sudah dipakai karyawan lain yang masih aktif.
- **Then** sistem menolak simpan dan menampilkan pesan bahwa nomor identitas sudah terdaftar pada karyawan lain.
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 2: Karyawan Rehire Wajib Direaktivasi, Bukan Didaftar Baru**
- **Given** nomor identitas yang diinput cocok dengan karyawan lama yang statusnya sudah nonaktif (pernah resign/diberhentikan).
- **When** HR mencoba mendaftarkan sebagai karyawan baru.
- **Then** sistem menolak pendaftaran baru dan menyarankan opsi reaktivasi dari data karyawan lama tersebut — nomor identitas bersifat unik seumur hidup per individu, bukan per periode kerja.
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 3: Offboarding (Resign / PHK)**
- **Given** profil karyawan berstatus aktif.
- **When** HR memproses resign/nonaktifkan.
- **Then** status berubah menjadi tidak aktif, tanggal berhenti terisi, akses masuk diblokir (koordinasi ke Akun Pengguna), data **tidak** dihapus fisik — hanya diarsipkan.
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 4: Aturan Rekening Bank Utama**
- **Given** HR melengkapi data rekening bank karyawan.
- **When** menyimpan daftar rekening.
- **Then** sistem mewajibkan **tepat satu** rekening ditandai sebagai utama — Payroll butuh satu tujuan transfer yang pasti.
- *Catatan implementasi:* kode saat ini baru menegakkan **minimal satu** utama (multi-utama masih lolos) — gap yang perlu ditutup jadi "tepat satu".

**Skenario 5: Cakupan Multi-Entitas (Isolasi PT/Cabang)**
- **Given** HR cabang A dengan cakupan PT-1/Cabang-A.
- **When** meminta daftar karyawan atau membuka detail karyawan Cabang B.
- **Then** daftar hanya berisi karyawan PT-1/Cabang-A; akses ke karyawan Cabang B ditolak atau tidak muncul di daftar.
- *Catatan implementasi:* kolom cakupan (PT/cabang) sudah ada di data & query; penegakan penuh menunggu RBAC selesai dibangun (mode Owner tanpa batasan sampai saat itu).

**Skenario 6: Daftar Karyawan Berhalaman dengan Pencarian**
- **Given** ada banyak karyawan.
- **When** HR membuka daftar karyawan dengan kata kunci pencarian dan urutan tertentu.
- **Then** sistem mengembalikan hasil berhalaman yang cocok dengan kode karyawan **atau** nama lengkap; urutan yang tidak dikenal otomatis jatuh ke urutan bawaan tanpa menampilkan galat.
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 7: Jabatan Wajib Terisi dan Valid**
- **Given** HR membuat atau menempatkan karyawan.
- **When** jabatan (Job Position) kosong atau tidak ditemukan di Workforce Structure.
- **Then** pembuatan/penempatan ditolak.
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 8: Status Kepegawaian Wajib Milik PT yang Sama**
- **Given** HR memilih jenis hubungan kerja (Status Kepegawaian) untuk karyawan.
- **When** Status Kepegawaian yang dipilih ternyata milik PT lain, bukan PT tempat karyawan itu bekerja.
- **Then** sistem menolak — Status Kepegawaian bersifat per-PT (lihat [employment-status.md](employment-status.md) §5), tidak boleh disilangkan.
- *Catatan implementasi:* **belum ada** — kode saat ini masih memakai daftar tetap (bukan rujukan ke Master Data Status Kepegawaian). Gap besar, lihat Ringkasan Gap.

**Skenario 9: Batas Durasi Kontrak Mengikuti Aturan Master Data**
- **Given** karyawan dengan Status Kepegawaian yang punya batas durasi maksimal (mis. kontrak berjangka) sudah punya riwayat kontrak sebelumnya.
- **When** HR menambah periode kontrak baru yang membuat total durasi kumulatif melewati batas maksimal yang tercatat di Status Kepegawaian tersebut.
- **Then** sistem memberi peringatan ke HR (bukan menolak paksa — keputusan akhir tetap di HR/legal, sistem hanya mengingatkan risiko kepatuhan). Batas durasi dibaca dari data Status Kepegawaian, bukan angka tetap dalam kode.
- *Catatan implementasi:* **belum ada** — batas durasi kumulatif masih dihitung terhadap angka tetap dalam kode, belum membaca dari Master Data Status Kepegawaian. Gap, menunggu Skenario 8 selesai.

**Skenario 10: Dokumen Wajib Onboarding**
- **Given** HR menyelesaikan langkah dokumen saat onboarding.
- **When** menyelesaikan langkah tersebut tanpa dokumen identitas (KTP) atau NPWP terunggah.
- **Then** sistem menolak menyelesaikan langkah tersebut (dokumen lain tetap opsional).
- *Catatan implementasi:* sudah berjalan di kode.

**Skenario 11: Riwayat Penempatan Tercatat, Bukan Ditimpa**
- **Given** karyawan sedang menduduki suatu jabatan/cabang induk.
- **When** HR memproses mutasi, promosi, atau pindah cabang induk.
- **Then** sistem mencatat satu baris riwayat penempatan baru dengan tanggal efektif, tanpa menghapus riwayat penempatan sebelumnya — data penempatan aktif di profil karyawan mengikuti riwayat yang paling baru.
- *Catatan implementasi:* **belum ada** — penempatan jabatan saat ini menimpa data lama tanpa jejak riwayat. Gap, lihat Ringkasan Gap.

**Skenario 12: Mutasi Antar-PT Dilarang, Antar-Cabang dalam Satu PT Diizinkan**
- **Given** HR memproses mutasi cabang induk karyawan.
- **When** cabang tujuan ternyata milik PT yang berbeda dari PT karyawan tersebut.
- **Then** sistem menolak — mutasi cabang hanya diizinkan dalam PT yang sama; pindah PT adalah proses offboarding + onboarding baru, bukan mutasi.
- *Catatan implementasi:* **belum ada**, menyatu dengan Skenario 11.

**Skenario 13: Tepat Satu Kontak Darurat**
- **Given** HR melengkapi data keluarga/tanggungan karyawan.
- **When** menyimpan daftar anggota keluarga.
- **Then** sistem mewajibkan **tepat satu** anggota keluarga ditandai sebagai kontak darurat — situasi mendesak butuh satu nomor yang pasti dihubungi, bukan ambigu di antara beberapa.
- *Catatan implementasi:* **belum ada** — data keluarga/tanggungan belum ada di kode sama sekali. Gap, lihat Ringkasan Gap.

**Skenario 14: Alamat Identitas dan Domisili Tersimpan Terpisah**
- **Given** HR mengisi alamat karyawan dan menandai "domisili sama dengan identitas".
- **When** data disimpan.
- **Then** sistem tetap menyimpan dua baris data (identitas dan domisili) dengan nilai yang disalin — tidak ada kolom penanda "sama" yang bisa membuat data tidak sinkron di kemudian hari.
- *Catatan implementasi:* sudah berjalan di kode.

---

## 5. Technical & Architectural Constraints

- **Domain-Driven Design (domain-first):** Modul hidup di `internal/employee/` sebagai satu bounded context utuh (domain/application/adapter/transport). Akses ke tabel modul lain **dilarang** langsung — lintas-domain wajib lewat Application Service (Akun Pengguna, Organization, Workforce Structure, dan setelah Skenario 8/Skenario 9 ditutup: Employment Status; setelah Skenario 4/§7.5 ditutup: Bank; setelah §7.4 ditutup: Region).
- **Multi-Entity Scoping (WAJIB):**
  - `Employee` diklasifikasikan **Company + Location bound** — wajib PT **dan** cabang, keduanya tidak boleh kosong.
  - **Cabang di sini = cabang induk (tunggal).** Identitas struktural dan pusat biaya payroll/pajak — wajib satu nilai pasti. **Bukan** tempat mencatat rotasi kerja harian lintas cabang (itu catatan bertanggal milik Attendance).
  - Perpindahan cabang induk hanya lewat proses mutasi resmi (Skenario 11/12), tidak lewat pengeditan langsung.
  - Sub-data (Biodata, Kontak, Alamat, Bank, Pendidikan, Dokumen, Riwayat Kontrak, Riwayat Penempatan, Keluarga) adalah turunan dari `Employee` — cakupan PT/cabang diturunkan dari induknya, tidak diduplikasi.
  - Integritas silang: cabang yang dipilih wajib milik PT yang sama dengan karyawan; ketidakcocokan ditolak.
  - Penegakan cakupan bertahap sampai RBAC selesai dibangun (lihat Skenario 5) — kolom dan struktur data sudah dipastikan sadar-cakupan sejak sekarang.
- **Status Kepegawaian — dua sumbu terpisah (WAJIB):**
  - **Jenis hubungan kerja** (per PT, dirujuk dari [employment-status.md](employment-status.md)) — nilainya beserta aturan bisnisnya (wajib punya riwayat kontrak, wajib punya tanggal akhir masa percobaan, batas durasi) dikelola sebagai data, bukan daftar tetap dalam kode (lihat Skenario 8/9).
  - **Status aktif** (lifecycle: aktif/tidak aktif/cuti/ditangguhkan) tetap daftar tetap terpisah — dua konsep ini tidak boleh digabung jadi satu kolom.
  - Tanggal akhir masa percobaan hanya terisi kalau Status Kepegawaian yang dipilih memang mewajibkannya (dibaca dari master, bukan dicek berdasarkan nama status).
- **Riwayat Kontrak (WAJIB entity riwayat, bukan dua kolom datar):**
  - Direkam per periode (tanggal mulai, tanggal akhir, nomor kontrak, dokumen bertanda tangan) — tidak menimpa data lama.
  - Hanya relevan untuk Status Kepegawaian yang mewajibkan riwayat kontrak (dibaca dari master); yang tidak mewajibkan tidak wajib punya baris di sini.
- **Riwayat Penempatan (WAJIB entity riwayat, entity baru):**
  - Setiap perubahan jabatan atau cabang induk direkam sebagai baris baru bertanggal efektif — tidak menimpa riwayat lama (selaras Skenario 11).
  - Tanggal efektif tidak boleh mendahului tanggal bergabung karyawan.
  - Data penempatan aktif pada profil karyawan adalah cerminan dari baris riwayat penempatan yang paling baru — bukan sumber kebenaran independen.
- **Dokumen — daftar tipe terbatas:**
  - Tipe dokumen mengikuti daftar baku (identitas, kartu keluarga, NPWP, ijazah, sertifikat, kontrak kerja, BPJS Kesehatan, BPJS Ketenagakerjaan, SKCK, dan sejenisnya) — mencegah data sampah, memudahkan tampilan slot unggah sesuai tipe.
  - Wajib minimum saat onboarding: identitas (KTP) dan NPWP (lihat Skenario 10). Dokumen lain opsional.
  - Tanggal kedaluwarsa opsional — sebagian dokumen memang kedaluwarsa (mis. SKCK). Pengingat kedaluwarsa adalah tanggung jawab modul Notifikasi (rencana mendatang), bukan modul ini.
  - Penyimpanan berkas bersifat privat (tidak bisa diakses publik langsung) — beda kelas sensitivitas dari avatar (§ Avatar), karena dokumen berisi data pribadi sensitif.
- **Data Keluarga/Tanggungan (entity baru):**
  - Menyimpan nama, hubungan keluarga, nomor identitas (opsional), dan penanda kontak darurat.
  - Tepat satu anggota wajib ditandai kontak darurat (Skenario 13) — bukan wajib-ada-tanggungan (karyawan lajang tanpa tanggungan tetap valid, tapi tetap perlu satu kontak darurat, boleh diri sendiri/kerabat non-tanggungan).
- **Nomor Statutory (bagian dari Biodata):**
  - Nomor NPWP, BPJS Kesehatan, BPJS Ketenagakerjaan disimpan sebagai nomor terstruktur — beda dari berkas dokumennya (§ Dokumen) yang menyimpan salinan filenya. Payroll butuh nomornya, bukan berkasnya, untuk perhitungan.
  - Ketiganya opsional saat onboarding (bisa menyusul), tidak termasuk dokumen wajib minimum (Skenario 10).
- **Persistensi / Database:**
  - Rekening bank dan pendidikan: ganti-seluruh koleksi dalam satu transaksi (hapus lalu buat ulang) karena tidak punya kunci alami.
  - Alamat dan dokumen: punya kunci alami (karyawan + tipe) — perbarui per tipe, unggah ulang satu tipe tidak menghapus tipe lain yang sudah ada.
  - Riwayat kontrak dan riwayat penempatan: **hanya tambah**, tidak pernah dihapus/dibuat ulang — tiap periode/perpindahan adalah baris baru.
  - Data keluarga: ganti-seluruh koleksi dalam satu transaksi, sama seperti rekening bank/pendidikan.
  - Tidak ada penghapusan permanen data karyawan — hanya diarsipkan (Skenario 3).
- **Avatar:** foto profil disimpan terpisah dari berkas dokumen (kelas sensitivitas beda — avatar sekadar tampilan, bukan dokumen legal). Unggahan baru menimpa foto lama, bukan menumpuk berkas baru. Diakses lewat tautan sementara, bukan tautan publik permanen. Opsional — belum tentu semua karyawan mengunggah avatar.
- **UI (Frontend):** Formulir pembuatan **wajib** berbentuk wizard bertahap dengan simpan per langkah (Data Inti → Biodata → Kontak → Rekening → Pendidikan/Dokumen → Keluarga) ke setiap langkah tersendiri, mencegah input panjang hilang saat gagal/dimuat ulang. Dropdown pemilihan Status Kepegawaian, Bank, dan Wilayah wajib mengambil pilihannya dari modul masing-masing (bukan input teks bebas). Dropdown Wilayah wajib **berjenjang** (pilih provinsi menyaring pilihan kota, dan seterusnya).

---

## 6. Dependencies (Ketergantungan)

**Depends on:**
- **Akun Pengguna (User) @1.0.1** — pembuatan karyawan bergantung akun pengguna; karyawan wajib punya akun terkait. Offboarding memicu perubahan status akun (koordinasi lewat Application Service).
- **Auth @1.0.1** — pemblokiran akses masuk saat offboarding dikoordinasikan lewat modul ini.
- **Organization @1.0.1** — sumber PT dan Cabang untuk cakupan data (lihat [organization.md](organization.md)).
- **Workforce Structure @1.0.1** — sumber Jabatan (Job Position) untuk penempatan karyawan (Skenario 7, Skenario 11).
- **Employment Status @1.0.1** — sumber daftar Status Kepegawaian per-PT beserta aturan bisnisnya (Skenario 8, Skenario 9) — lihat [employment-status.md](employment-status.md) §4.
- **Bank @1.0.0** — sumber daftar bank untuk pilihan rekening karyawan (§7.5) — lihat [bank.md](bank.md).
- **Region @1.0.0** — sumber daftar wilayah administratif untuk alamat karyawan (§7.4) — lihat [region.md](region.md).
- **RBAC @1.0.1** — penegakan cakupan PT/cabang pada daftar dan detail karyawan (Skenario 5) — lihat [rbac.md](rbac.md) §5; sampai RBAC diimplementasikan, penegakan berjalan default kosong (mode Owner).

**Consumed by:** Cuti, Payroll, Attendance, Performance (semua rencana mendatang) — mereka mereferensikan identitas karyawan dan menurunkan cakupan PT/cabang dari sini.

**External integrations:** penyimpanan berkas untuk dokumen dan avatar — modul ini menyimpan tautan/kunci berkas saja, bukan menangani unggah biner secara langsung. Penyimpanan dokumen dan avatar dipisah menurut kelas sensitivitas (§5).

---

## 7. Data Schema & Business Rules (Database Map)

### 7.1. Employee (Data Inti Pekerjaan)
- **Aturan Bisnis:** wajib Jabatan (Workforce Structure) dan tanggal bergabung. Kode karyawan unik, diinput manual HR. PT dan Cabang wajib terisi, Cabang wajib se-PT. Status Kepegawaian dirujuk dari Master Data (Skenario 8) — bukan daftar tetap. Status aktif (lifecycle) terpisah dari Status Kepegawaian. Tanggal akhir masa percobaan hanya terisi kalau Status Kepegawaian bersangkutan mewajibkannya.

| id | company_id | branch_id | user_id | employee_code | job_position_id | employment_status | status | probation_end_date | join_date | resign_date |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `emp-1` | `co-1` | `br-1` | `usr-1` | HR-001 | `pos-1` | Karyawan Tetap | Aktif | `null` | 2020-01-01 | `null` |

### 7.2. Personal Data (Biodata) — 1:1
- **Aturan Bisnis:** nomor identitas unik seumur hidup per individu (Skenario 2). Status PTKP wajib (dipakai Payroll). Avatar opsional. Nomor NPWP/BPJS opsional saat onboarding, bisa menyusul (§5).

| employee_id | full_name | ktp_number | gender | marital_status | ptkp_status | religion | npwp_number | bpjs_kesehatan_number | bpjs_ketenagakerjaan_number | avatar_url |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `emp-1` | Budi Santoso | 3171000000000001 | Laki-laki | Menikah | K/1 | Islam | 09.123.456.7-012.000 | 0001234567890 | 12AB34567890 | `(tautan avatar)` |

### 7.3. Contact — 1:1
- **Aturan Bisnis:** surel dan nomor telepon pribadi. Alamat tidak disimpan di sini — lihat §7.4.

| employee_id | personal_email | phone_number |
| :-- | :-- | :-- |
| `emp-1` | budi@mail.com | 08123456789 |

### 7.4. Address (Alamat Terstruktur) — 1:N
- **Aturan Bisnis:** dua tipe — sesuai identitas dan domisili (Skenario 14). Wilayah (provinsi/kota/kecamatan/kelurahan) dirujuk dari Master Data Wilayah ([region.md](region.md)), bukan diketik bebas — nama jalan/RT/RW/kode pos tetap teks bebas.

| employee_id | address_type | street | rt | rw | village_id | district_id | city_id | province_id | postal_code |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `emp-1` | Identitas | Jl. Melati No.1 | 003 | 005 | `vil-1` | `dist-1` | `city-1` | `prov-1` | 10160 |
| `emp-1` | Domisili | Kos Mawar Kamar 4 | 001 | 002 | `vil-2` | `dist-2` | `city-2` | `prov-1` | 12790 |

### 7.5. Bank Account — 1:N
- **Aturan Bisnis:** nama bank dirujuk dari Master Data Bank ([bank.md](bank.md)), bukan diketik bebas. Wajib **tepat satu** rekening utama (Skenario 4) — dipakai Payroll sebagai tujuan transfer.

| employee_id | bank_id | account_number | account_holder_name | is_primary |
| :-- | :-- | :-- | :-- | :-- |
| `emp-1` | `bank-bca` | 1234567890 | Budi Santoso | true |

### 7.6. Education — 1:N (opsional saat onboarding)

| employee_id | level | institution_name | major | start_year | end_year | score |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `emp-1` | S1 | Universitas Indonesia | Sistem Informasi | 2010 | 2014 | 3.50 |

### 7.7. Document — 1:N (identitas dan NPWP wajib onboarding, sisanya opsional)
- **Aturan Bisnis:** tipe dokumen mengikuti daftar baku (§5). Tanggal kedaluwarsa opsional.

| employee_id | document_type | document_url | expiry_date |
| :-- | :-- | :-- | :-- |
| `emp-1` | Identitas (KTP) | `(tautan dokumen)` | `null` |
| `emp-1` | NPWP | `(tautan dokumen)` | `null` |
| `emp-1` | SKCK | `(tautan dokumen)` | 2026-12-01 |

### 7.8. Employee Contract (Riwayat Kontrak) — 1:N
- **Aturan Bisnis:** tiap periode/perpanjangan = satu baris baru, tidak menimpa baris lama. Batas durasi kumulatif dibaca dari batas maksimal Status Kepegawaian bersangkutan (Skenario 9), bukan angka tetap. Hanya relevan untuk Status Kepegawaian yang mewajibkan riwayat kontrak.

| id | employee_id | contract_number | employment_status | start_date | end_date | document_url | status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `ctr-1` | `emp-1` | PKWT/2024/001 | Karyawan Kontrak | 2024-01-01 | 2025-01-01 | `(tautan dokumen)` | Berakhir |
| `ctr-2` | `emp-1` | PKWT/2025/014 | Karyawan Kontrak | 2025-01-01 | 2026-01-01 | `(tautan dokumen)` | Aktif |

### 7.9. Employee Assignment (Riwayat Penempatan) — 1:N — **Entity Baru**
- **Aturan Bisnis:** tiap perpindahan jabatan/cabang induk = satu baris baru, tidak menimpa (Skenario 11). Tanggal efektif tidak boleh mendahului tanggal bergabung karyawan. Cabang tujuan wajib se-PT dengan karyawan (Skenario 12) — pindah PT bukan mutasi, melainkan offboarding + onboarding baru.

| id | employee_id | job_position_id | branch_id | effective_date | reason |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `asg-1` | `emp-1` | `pos-3` | `br-1` | 2020-01-01 | Penempatan awal |
| `asg-2` | `emp-1` | `pos-2` | `br-1` | 2023-06-01 | Promosi |

### 7.10. Employee Family (Data Keluarga/Tanggungan) — 1:N — **Entity Baru**
- **Aturan Bisnis:** wajib **tepat satu** anggota ditandai kontak darurat (Skenario 13). Nomor identitas opsional (anak di bawah umur belum tentu punya).

| employee_id | full_name | relationship | ktp_number | is_emergency_contact |
| :-- | :-- | :-- | :-- | :-- |
| `emp-1` | Siti Aminah | Istri | 3171000000000099 | true |
| `emp-1` | Ahmad Fauzi | Anak | `null` | false |

---

## Ringkasan Gap (kondisi kode vs PRD target)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| Rekening bank utama | minimal satu utama ditegakkan, multi-utama masih lolos | tegakkan tepat satu utama (Skenario 4) |
| Cakupan PT/Cabang | kolom dan query sudah sadar-cakupan | penegakan penuh menunggu RBAC selesai dibangun (Skenario 5) |
| Status Kepegawaian | daftar tetap dalam kode | ganti jadi rujukan ke Master Data Status Kepegawaian per-PT (Skenario 8) — menunggu modul Employment Status punya kode |
| Batas durasi kontrak | angka tetap dalam kode | baca dari batas maksimal Status Kepegawaian (Skenario 9) — menyatu dengan gap di atas |
| Riwayat penempatan | penempatan jabatan menimpa data lama, tanpa jejak riwayat | tambah entity riwayat penempatan append-only (Skenario 11, 12) |
| Data keluarga/tanggungan | belum ada entity sama sekali | tambah entity + validasi tepat satu kontak darurat (Skenario 13) |
| Nomor NPWP/BPJS di Biodata | belum ada kolom, baru tersimpan sebagai berkas dokumen | tambah kolom nomor terstruktur di Biodata (§7.2) |
| Rekening bank sebagai teks bebas | `bank_name` teks bebas | ganti jadi rujukan ke Master Data Bank (§7.5) — menunggu modul Bank punya kode |
| Alamat wilayah sebagai teks bebas | kolom wilayah teks bebas | ganti jadi rujukan ke Master Data Wilayah (§7.4) — menunggu modul Region punya kode |
| Penegakan kuota jabatan | belum ada | tolak penempatan kalau kuota Job Position penuh (lihat [workforce-structure.md](workforce-structure.md) Skenario 9) |
