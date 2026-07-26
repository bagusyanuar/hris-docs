# HRIS Docs - Business Specifications & PRD Guidelines

Dokumen ini adalah index aturan untuk workspace `hris-docs`. Semua agen dan product manager/developer yang berkontribusi pada penulisan spesifikasi bisnis harus mematuhi aturan ini.

## Project Overview

Workspace `hris-docs` adalah **Control Plane & Single Source of Truth** untuk proyek ini. Segala bentuk perencanaan, baik itu visi produk, Product Requirements Document (PRD), alur bisnis, maupun **desain arsitektur teknikal (BE & FE)** WAJIB didokumentasikan di sini sebelum dieksekusi di repositori kode.

## Daftar Aturan (Rules)

1. **Docs First**: Setiap pengembangan fitur baru WAJIB diawali dengan pembuatan/pembaruan PRD di dalam folder `PRD/`.
2. **Standardisasi Format PRD**: Penulisan PRD harus mematuhi format baku yang sudah disediakan (lihat template di `PRD/_TEMPLATE.md`). PRD harus memuat 6 pilar utama: Tujuan & Dampak, Scope & Out-of-Scope, User Roles, Kriteria Penerimaan (Given-When-Then), Technical Constraints, dan Dependencies.
3. **Pemisahan Konteks**: Jangan mencampurkan urusan teknis seperti query SQL, struktur JSON API, atau nama komponen Svelte ke dalam PRD bisnis.

## Referensi Lain
- Aturan Dokumentasi: [`rules/project-docs.md`](rules/project-docs.md) — panduan penyusunan dokumen PRD dan Teknis.
- Skills: [`skills/`](skills/) — instruksi pembuatan dokumen, contoh: `scaffold-prd`, `scaffold-trd-be`, `scaffold-trd-fe`.
