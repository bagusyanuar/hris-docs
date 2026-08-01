# Decision Log (ADR) - Bank Module

## ADR-001: Penggunaan UUID vs Bank Code sebagai Primary Key
- **Konteks:** Setiap bank memiliki kode unik nasional (misal: 014 untuk BCA). Apakah menggunakan kode tersebut sebagai *Primary Key*?
- **Keputusan:** Tetap menggunakan **UUID (Surrogate Key)** sebagai `id` utama. Kode nasional disimpan di kolom `bank_code`.
- **Alasan:** Terkadang bank merger (contoh Bank Syariah Indonesia) yang menyebabkan pergantian entitas atau kode. Menggunakan UUID mencegah perlunya melakukan *update* ke seluruh tabel `payroll` yang sudah menunjuk ke bank tersebut. Kode BI dapat diubah tanpa merusak integritas *Foreign Key*.

## ADR-002: Pemisahan Modul Bank
- **Konteks:** Di mana meletakkan entitas Bank?
- **Keputusan:** Di modul **`internal/bank`**.
- **Alasan:** Memisahkan *concern* agar mudah dirawat. Modul ini di masa depan mungkin berkembang tidak hanya sekadar *dropdown*, melainkan integrasi dengan *Payment Gateway* untuk validasi nomor rekening (Account Validation API).
