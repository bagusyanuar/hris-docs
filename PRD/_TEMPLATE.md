---
module: [Nama Modul]
version: [Versi (e.g., 1.0.0)]
status: [Draft / In Review / Approved]
owner: [Nama Owner]
updated: [YYYY-MM-DD HH:MM:SS]
depends_on: [module_a@1.0.0, module_b@2.0.0]
consumed_by: [module_c@planned, module_d@planned]
---

# Product Requirements: [Nama Modul] Module

> **Catatan grounding:** (Opsional) Penjelasan status modul saat ini (misalnya apakah ini fitur baru, migrasi, atau penambahan fitur di modul lama).

---

## 1. Tujuan & Dampak (The "Why")

Deskripsi singkat tentang mengapa modul ini dibuat, masalah apa yang diselesaikan, dan apa dampaknya (misalnya "Sebagai Single Source of Truth...", "Mempercepat proses...").

---

## 2. Scope & Out-of-Scope (Batasan Tegas)

**In-Scope (Dikerjakan):**
- [Fitur atau entitas utama yang dikerjakan]
- [Hal penting yang masuk cakupan rilis ini]

**Out-of-Scope (TIDAK di modul ini):**
- [Fitur terkait yang mungkin diasumsikan orang masuk ke sini, padahal bukan]
- [Fitur yang ditunda ke rilis berikutnya]

---

## 3. User Roles & Permissions

Tabel hak akses dasar untuk modul ini (sesuaikan kolom jika perlu).

| Role | Read | Create | Update | Delete / Offboard |
|------|------|--------|--------|-------------------|
| Superadmin / Admin | ✅ | ✅ | ✅ | ✅ |
| Karyawan (ESS) | ✅ (hanya milik sendiri) | ❌ | ❌ | ❌ |

- **Catatan tambahan:** Aturan spesifik terkait role (misal: "Hanya Admin yang bisa mengakses fitur X").

---

## 4. Kriteria Penerimaan (Acceptance Criteria)

Gunakan format *Given, When, Then* untuk memperjelas skenario pengujian.

**Skenario 1: [Nama Skenario]**
- **Given** [Kondisi awal, misal: "HR sedang mengisi biodata"]
- **When** [Aksi pengguna, misal: "memasukkan data yang sudah ada"]
- **Then** [Hasil yang diharapkan, misal: "sistem menolak dengan HTTP 409"]
- *Catatan implementasi:* [Opsional: Catatan khusus untuk developer jika ada gap antara kode sekarang dan target]

**Skenario 2: [Nama Skenario]**
- **Given** ...
- **When** ...
- **Then** ...

---

## 5. Technical & Architectural Constraints

Panduan tingkat tinggi untuk *engineering*.
- **Domain-Driven Design (domain-first):** Target modul hidup di mana, aturan pemanggilan lintas-domain.
- **Multi-Entity Scoping:** Aturan `company_id` dan `branch_id`.
- **Persistensi / Database:** Aturan khusus mengenai insert/update/delete (misal: "Soft delete only", "Wajib transaksi").
- **UI (Frontend):** Aturan UX khusus (misal: "Wajib Wizard/Multi-step form").

---

## 6. Dependencies (Ketergantungan)

*(Penjelasan lebih rinci dari frontmatter)*

**Depends on:**
- **[Modul A @versi]** — Alasan bergantung pada modul ini (misal: butuh data User ID).
- **[Modul B @versi]** — ...

**Consumed by:**
- **[Modul C]** — Mereka membutuhkan endpoint/data dari modul ini untuk proses X.

**External integrations:**
- **[Sistem Eksternal]** — Misal: MinIO (S3) untuk file upload, Payment Gateway, SMTP, dll.

---

## 7. Data Schema & Business Rules (Database Map)

Penjelasan entitas dan tabel utama beserta atribut kunci dan aturan bisnis spesifiknya (Bisa digabung dengan snapshot tabel).

### 7.1. [Nama Entitas/Tabel Utama]
- **Aturan Bisnis:** Penjelasan kolom mandatory, format khusus, enum yang diizinkan.

| id | [kolom_1] | [kolom_2] | created_at |
| :-- | :-- | :-- | :-- |
| `uuid` | `value` | `value` | `timestamp` |

### 7.2. [Nama Child Entity] — [1:1 / 1:N]
- **Aturan Bisnis:** Aturan relasinya.

| parent_id | [kolom_1] |
| :-- | :-- |
| `uuid` | `value` |

---

## Ringkasan Gap (kondisi kode vs PRD target) - (Opsional untuk Fitur Migrasi)

| Area | Status kode sekarang | Gap |
|------|----------------------|-----|
| [Contoh Area] | [Kondisi sekarang] | [Target perubahan] |
