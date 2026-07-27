# HRIS Docs (Control Plane & Single Source of Truth)

Selamat datang di repositori dokumentasi sentral untuk sistem **HRIS (Human Resource Information System)**. Repositori ini bertindak sebagai **Control Plane** yang mengatur seluruh alur bisnis dan desain teknis proyek sebelum implementasi kode dilakukan.

## 🌟 Fungsi & Filosofi

Repositori kode utama kita (`hris-backend` dan `hris-frontend`) adalah ruang lingkup implementasi murni (*headless*). Oleh karena itu, **segala jenis perancangan, baik itu perancangan bisnis maupun perancangan arsitektur teknis perangkat lunak, dipusatkan di sini (`hris-docs`)**.

Dengan pendekatan ini:
1. **Transparansi Tinggi:** Tim Bisnis (PM), QA, dan Engineer bisa melihat rancangan sistem secara utuh dari satu tempat.
2. **Standardisasi:** Semua spesifikasi teknis (seperti kontrak API dan skema database) disepakati di sini sebelum *engineer* menulis baris kode pertama.
3. **Pemisahan Konteks:** Mencegah repositori kode menjadi "kotor" oleh dokumen-dokumen perancangan yang terus berubah.

## 📂 Struktur Repositori

```text
hris-docs/
├── PRD/                 # Product Requirements Document (Spesifikasi Bisnis & Alur)
├── TRD/                 # Technical Requirements Document (Spesifikasi Teknis)
│   ├── BE/              # TRD untuk Backend (Kontrak API, DBML, dsb)
│   └── FE/              # TRD untuk Frontend (State, Komponen UI, dsb)
├── .agents/             # Konfigurasi AI Agents (Rules, Skills, Workflow)
├── architecture.md      # Ringkasan Tech Stack Global & Komunikasi Sistem
└── README.md            # Anda berada di sini
```

## 🔄 Alur Kerja (Workflow)

Pengembangan fitur baru **wajib** mengikuti siklus berikut:

1. **Fase Bisnis (Rancang PRD):**
   Product Manager merumuskan fitur baru ke dalam dokumen PRD dan menyimpannya di `PRD/`. Dokumen ini difokuskan pada *WHAT* (apa yang dibuat) dan *WHY* (kenapa dibuat), lengkap dengan Kriteria Penerimaan (Acceptance Criteria).
   
2. **Fase Desain (Rancang TRD):**
   Setelah PRD disetujui, System Architect atau tim Engineer menjabarkannya menjadi dokumen teknis (TRD) di folder `TRD/BE/` dan `TRD/FE/`. Fase ini berfokus pada *HOW* (bagaimana cara membuatnya secara teknis), termasuk mendesain skema database (DBML) dan kontrak API.
   
3. **Fase Eksekusi (GitHub Issues):**
   Dokumen TRD yang sudah selesai dipublikasikan/dijadikan referensi pada GitHub Issue di repositori masing-masing (`hris-backend` atau `hris-frontend`). Engineer kemudian mengeksekusi *issue* tersebut menjadi kode yang nyata.

### Pola Integrasi API (Consumer-Driven Contracts)
Untuk pengembangan API, sangat disarankan menggunakan pendekatan **Consumer-Driven Contracts (CDC)** atau *Frontend-First API Design*.
- **Konsep:** Tim Frontend (FE) menentukan bentuk/struktur JSON (*request/response*) yang paling optimal untuk UI mereka terlebih dahulu. Tim Backend (BE) kemudian membangun *endpoint* untuk memenuhi kontrak tersebut. Ini mencegah *over-fetching* dan memastikan API tepat sasaran.
- **Tempat Distribusi Kontrak:** FE merumuskan format kontrak (bisa menggunakan *Markdown*, *JSON*, atau *OpenAPI/Swagger YAML*) dan menyimpannya ke dalam folder **`API_CONTRACTS/`** di repositori ini.
- **Handover ke Backend:** Saat menerbitkan *GitHub Issue* untuk tim BE, lampirkan URL/link menuju file spesifik di dalam folder `API_CONTRACTS/` tersebut. Kontrak ini akan menjadi *Acceptance Criteria* kelulusan tugas bagi tim BE.
## 📝 Aturan Revisi Dokumen (PRD vs TRD)

Seringkali saat fase eksekusi (*coding*), ditemukan ketidaksesuaian atau kebutuhan untuk merubah desain. Berikut adalah aturan main (*Rules of Thumb*) kapan harus merevisi dokumen:

**✅ Cukup Update TRD Saja (PRD Tidak Perlu Diubah):**
- Perubahan **murni bersifat teknis** dan tidak mengubah aturan bisnis, Kriteria Penerimaan (*Acceptance Criteria*), atau *User Journey*.
- *Contoh:* Perubahan struktur/payload JSON dari endpoint (misal merubah *flat list* menjadi *tree/nested* agar FE lebih mudah *render*), perubahan tipe data (misal `Integer` menjadi `UUID`), perubahan arsitektur komponen UI, atau optimasi performa *query* database.
- *Action:* Update dokumen spesifikasi di `TRD/BE` atau `TRD/FE` dan tambahkan catatan perubahan di file `decision-log.md` pada modul terkait agar *engineer* lain mengetahui alasan perubahannya.

**❌ WAJIB Update PRD Terlebih Dahulu:**
- Perubahan **berdampak pada alur bisnis**, penambahan/pengurangan fitur, atau mengubah *Acceptance Criteria* yang sudah disepakati di awal.
- *Contoh:* Menambahkan tombol "Login with Google" pada halaman otentikasi, mengubah hak akses (*Role*) untuk aksi tertentu, atau menambah langkah *step* pada sebuah proses persetujuan (Approval).
- *Action:* Lapor/revisi dokumen di folder `PRD/` terlebih dahulu untuk menyesuaikan *scope* bisnis. Setelah disetujui, barulah update dokumen `TRD` untuk merancang teknis implementasi dari penambahan tersebut.

## 🛠️ Tech Stack & Arsitektur

Tim kita menggunakan *stack* yang sangat modern (*Golang, Svelte 5, Tailwind v4, dll*). Untuk panduan arsitektur global dan daftar *tech stack* lengkap, silakan baca file **[`architecture.md`](architecture.md)**.

## 🤖 Bantuan AI Agent

Repositori ini telah dibekali dengan kecerdasan buatan (*AI Agents Configuration*). Jika Anda menggunakan AI Assistant yang mendukung framework `.agents` (seperti Google Antigravity), Anda bisa langsung menggunakan *skill* yang tersedia, seperti:
- Men-generate draf PRD yang sesuai standar perusahaan.
- Mendesain otomatis TRD Backend (termasuk DBML) berdasarkan file PRD.
- Merancang otomatis arsitektur komponen Svelte (TRD Frontend) berdasarkan file PRD.

Lihat selengkapnya di [Aturan Agen](.agents/AGENTS.md).
