---
module: <Nama Modul>
version: 1.0.0
status: Draft           # Draft | In Review | Approved | Deprecated
owner: <Nama Arsitek/BE Lead>
updated: <YYYY-MM-DD HH:MM:SS>
references_prd: <URL absolut GitHub ke file PRD>
---

# TRD Backend: <Nama Modul>

## 1. Referensi PRD & Ruang Lingkup
- **PRD:** [Link PRD](file:///...)
- **Versi PRD:** v<X.Y.Z>
- **Ringkasan:** <Penjelasan singkat modul ini dalam konteks backend>

## 2. Kontrak API (Endpoints)
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/v1/...` | ... |
| POST | `/api/v1/...` | ... |

### 2.1 Endpoint Detail: `POST /api/v1/...`
- **Request Payload:**
  ```json
  {}
  ```
- **Response Payload:**
  ```json
  {}
  ```
- **Error Codes:** 400, 401, 500

## 3. Desain Arsitektur DDD
### 3.1 Domain Layer
- **Entity:** ...
- **Business Rules:** ...

### 3.2 Application Layer
- **Use Cases:** ...

### 3.3 Adapter Layer
- **Repositories:** ...
- **Handlers:** ...

## 4. Referensi Skema Database (DBML)
- **File DBML:** [Link DBML](file:///...)
- **Tabel Utama:** ...

## 5. Keamanan & Multi-Tenant Scoping
- **RBAC:** Role apa saja yang diizinkan mengakses endpoint di modul ini?
- **Scope Filter:** Bagaimana `company_id` atau `branch_id` diterapkan di *query* database?
