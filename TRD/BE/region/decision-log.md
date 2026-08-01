# Decision Log (ADR) - Region Module

Dokumen ini mencatat keputusan-keputusan arsitektural (*Architectural Decision Records*) yang diambil pada fase desain.

## ADR-001: UUID vs Natural Key untuk Primary Key
- **Konteks:** Setiap wilayah memiliki kode resmi (Kemendagri/BPS). Apakah menggunakan kode tersebut sebagai *Primary Key* atau membuat UUID buatan sistem?
- **Keputusan:** Menggunakan **UUID (Surrogate Key)** sebagai `id` utama. Kode Kemendagri dipindah ke kolom unik `administrative_code`.
- **Alasan:** Terkadang pemerintah merilis aturan pemekaran wilayah yang memaksa perubahan pada kode administratif. Menggunakan UUID menghindari bahaya *Cascading Update* secara ekstensif pada miliaran baris *foreign key* (misal: log absensi, alamat karyawan, cabang kantor) di database HRIS. 

## ADR-002: Konsolidasi Entitas dalam Satu Bounded Context
- **Konteks:** Apakah memisahkan modul Provinsi, Kota, dan Kecamatan menjadi mikro-domain tersendiri (`internal/province`, `internal/city`)?
- **Keputusan:** Tidak. Digabungkan menjadi satu *Bounded Context* tunggal di `internal/region`.
- **Alasan:** Menghindari *Entity = Domain Fallacy*. Entitas-entitas ini memiliki *business cohesion* yang sama persis (hanya data hirarki referensi belaka). Memecahnya hanya akan membuat *Tight Coupling* dan repetisi kode konfigurasi antar modul.
