---
module: <Nama Modul>
version: 1.0.0
status: Draft           # Draft | In Review | Approved | Deprecated
owner: <Nama Arsitek/FE Lead>
updated: <YYYY-MM-DD HH:MM:SS>
references_prd: <Link ke file PRD>
references_trd_be: <Link ke TRD BE - opsional>
references_design: <Link Figma / UI Design (tulis "-" jika belum ada)>
---

# TRD Frontend: <Nama Modul>

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [Link PRD](file:///...)
- **Versi PRD:** v<X.Y.Z>
- **TRD BE (API):** [Link TRD BE](file:///...)
- **Ringkasan:** <Penjelasan singkat modul ini dalam konteks antarmuka pengguna>

## 2. Pemetaan Rute (Routing & Layouts)
| URL Path | Komponen Halaman (Page) | Layout Pembungkus |
|----------|-------------------------|-------------------|
| `/employee` | `EmployeePage.svelte` | `MainLayout.svelte` |

## 3. Arsitektur Komponen Svelte
Pecah antarmuka menjadi komponen-komponen reaktif.
- **`<EmployeeTable />`**: Komponen presentasional (Dumb).
  - **Props**: `data`, `isLoading`
  - **Events**: `on:edit`, `on:delete`
- **`<EmployeeForm />`**: Komponen pengambil data (Smart).
  - **State ($state)**: `formData`, `errors`

## 4. State Management & Reaktivitas
- **Global State:** (Gunakan Svelte 5 Runes `$state` yang di-export dari file `.svelte.js/ts`).
- **Data Fetching:** Bagaimana status *Loading*, *Error*, dan *Success* di-handle saat memanggil API BE?

## 5. Client-Side Validation
- **Field Aturan:** (misal: validasi email, panjang password)
- **Error Display:** (bagaimana error ditampilkan ke user)
