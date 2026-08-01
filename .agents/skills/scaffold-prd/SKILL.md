---
name: scaffold-prd
description: Guide for scaffolding Product Requirements Documents (PRD) in the HRIS project to ensure consistency between Backend and Frontend teams.
---

# Scaffolding PRD (Product Requirements Document)

When the user asks to create or brainstorm a requirement document, PRD, or specifications for a new module/feature, you MUST follow this format and convention.

**CRITICAL RULE - NO TECHNICAL JARGON:**
The PRD is written strictly for Product Managers, Business Analysts, and QA. Do NOT use technical jargon such as `JWT`, `Bcrypt`, `Middleware`, `HTTP status codes` (e.g., `200 OK`, `401 Unauthorized`), `JSON structures`, or internal database constraints. Describe behaviors purely in terms of Business Flows, User Actions, and Product Rules. All technical implementation details MUST be deferred to the TRD.

## 1. Directory & Naming Convention
- **One file per module (bounded context).** DO NOT put multiple modules in a single monolithic file. Each module gets its own `.md`, mirroring the domain-first code layout.
- **Location:** All PRD documents MUST be saved in the `PRD/` directory inside `hris-docs`.
- **Naming Convention:** Use lowercase with hyphens (e.g., `employee.md`, `attendance-tracking.md`).
- **Do not** use `PRD/` for technical specs. Technical Requirements Documents (TRD) belong in `TRD/BE/` or `TRD/FE/`.
- **Index maintenance (MANDATORY):** Every time a PRD is created or its status/version changes, you MUST update `PRD/README.md` (module table + dependency graph). The index is the single "see everything at a glance" entry point. After editing any `depends_on`/`consumed_by`, run `python3 scripts/check-prd-deps.py` from the `hris-docs` root and fix every `FAIL` it reports before considering the edit done (`WARN` for modules with no local PRD file yet is expected and fine).
- **Shared concepts:** Cross-module terminology or concepts (e.g., "Working Day", holiday calendar) live in `PRD/_shared/glossary.md`. Modules **reference** the glossary — never copy-paste shared rules into individual PRDs.
- **Module boundary heuristic:** A cross-cutting concern that will be consumed by *many* future bounded contexts (e.g., authorization/roles, audit trail, notifications) gets its **own** PRD/module — do not fold it into the nearest existing module just because it's convenient right now (e.g., RBAC belongs in its own PRD, not bolted onto User just because User owns the account table). Loose coupling in docs mirrors loose coupling in code.
- **Ground truth before writing (MANDATORY for already-implemented modules):** If the module already has code (`internal/<module>/`), you MUST read the real `domain`/`application`/`adapter`/`transport` files before writing or updating a single line of the PRD. Never infer behavior from function/file names alone. Acceptance Criteria and Constraints must reflect what the code *actually does*, not what it's assumed to do.
- **Legacy migration hygiene (MANDATORY when migrating a PRD from `hris-backend/docs/PRD/`):** Ground in the real code (previous bullet), but do NOT carry over sections that are actually TRD content disguised as PRD content — literal endpoint paths (`GET /workforce/departments/tree`), JSON shapes, or "Catatan untuk FE" blocks listing routes. That belongs in `TRD/FE/`, not here (see root rule "Pemisahan Konteks"). Translate the underlying business rule instead of copy-pasting the technical note. Also don't blindly carry the legacy document's version number or "Approved" status forward — re-grounding in `hris-docs` format starts the version/status fresh (see §1a) unless the content is verified unchanged.
- **Master data vs. workflow module (module boundary heuristic, cont'd):** When a feature area has both a *reference/configuration* concept and a *transactional/approval* concept, split them into two PRDs even before the transactional one is built — the reference data usually has consumers beyond just its own workflow module (e.g. Payroll also reads it). Precedent in this workspace: `employment-status.md` (master data) is separate from the future `employee.md`-adjacent onboarding flow; `leave-type.md` (master data) is separate from the future `leave.md` (request/approval workflow); `work-shift.md` (master data) is separate from the future `attendance.md` (clock-in/out workflow). The workflow module's PRD, once written, adds `depends_on: [<master-data>@x.y.z]` pointing back.

## 1a. Mandatory Frontmatter Header
Every PRD file MUST begin with a YAML frontmatter block for versioning and traceability:

```yaml
---
module: Payroll
version: 1.0.0          # SemVer — bump on every business-rule change
status: Draft           # Draft | In Review | Approved | Deprecated
owner: <name>
updated: 2026-07-22 14:35:07   # yyyy-MM-dd HH:mm:ss, Asia/Jakarta timezone, down to the second (not date-only)
depends_on: [attendance@1.2, leave@1.0]   # empty [] if none
---
```

Bump `version` (SemVer) and refresh `updated` (full timestamp, not just the date) whenever the PRD content changes, and reflect it in the README index. Concrete bump criteria:
- **PATCH** (1.0.0→1.0.1): wording clarification, typo fix — no change in contract meaning.
- **MINOR** (1.0.0→1.1.0): new scope/feature added that's backward-compatible — existing consumers aren't broken.
- **MAJOR** (1.0.0→2.0.0): breaking change to a contract another module references via `depends_on` (field removed/renamed, business rule reversed, etc.).

**`@planned` vs. a real version number in `depends_on`/`consumed_by` (MANDATORY distinction):** This tag is a **product/scope** signal, never an implementation-status one — whether the target module has code in `internal/<module>/` is irrelevant here (that belongs in `product-vision.md` §5.1's "Status kode" column and each PRD's own "Ringkasan Gap", not in this tag).
- Use **`@planned`** only when either: (a) the target module has **no PRD file at all** yet (nothing to pin a version to — e.g. `payroll@planned`, `attendance@planned`), or (b) the dependency is still roadmap-level intent that this PRD's own content has **not yet** turned into a concrete field/rule (e.g. `organization.md` says `bank@planned` because its own §7 Data Schema has no bank-account column yet — the day that column is added to Organization's scope, the tag becomes real).
- Use the **real version** (`@1.0.0`, etc.) the moment the target PRD exists AND this PRD's own content already commits to something concrete from it — a named field, a named contract (e.g. any PRD whose §5 says "filter dienforce lewat `scope.FromContext`" is concretely committing to `rbac.md`'s contract and must write `rbac@1.0.0`, not `rbac@planned`, even before `internal/rbac/` has a single line of Go code).
- When in doubt: ask "does *this PRD's own text* name a specific field/behavior from the target?" — yes = real version; no (or target has no PRD) = `planned`.

## 2. Mandatory PRD Structure (The 6 Pillars)
An Enterprise-Grade PRD must act as a single source of truth for Business, QA, and Engineering. Every PRD MUST contain the following 6 core sections:

### 2.1. Tujuan & Dampak (The "Why")
Explain *why* this module is being built. What business problem does it solve?
*Example: "Mempercepat proses input data dari 10 menit menjadi 2 menit."*

### 2.2. Scope & Out-of-Scope (Batasan Tegas)
Clearly define what is being built and, critically, what is **NOT** being built right now to prevent feature creep.

### 2.3. User Roles & Permissions
Define who will use this feature and their access levels (e.g., Superadmin, HR Manager, Regular Employee). Detail what each role can Read, Write, or Approve.

### 2.4. Kriteria Penerimaan (Acceptance Criteria)
The strict definition of "Done" to prevent debates between QA and Engineering. Use the **Given-When-Then** format to ensure boundaries are black-and-white and easily convertible into unit tests.

**Implementation gap flagging (MANDATORY):** If, while grounding the PRD in real code (see §1 "Ground truth before writing"), you find the code does **not** actually do what a scenario requires — or does not fulfill a contract another module's PRD already promised depends on it — write the scenario as the *intended/required* behavior anyway, then add a `*Catatan implementasi:*` line directly under it stating what the code currently does instead and that it's a gap to close. Never silently omit the scenario, and never mark it done just because "that's what the code happens to do."

### 2.5. Technical & Architectural Constraints
Define the engineering rules for this module.
- **Backend:** DDD isolation rules, strict typing, or soft-delete mandates.
- **Frontend:** Form structure (e.g., Wizard/Multi-step), UI constraints, data masking, or client-side validations.
- **Multi-Entity Scoping (MANDATORY):** klasifikasikan tiap entity modul ini sesuai [scoping-convention.md](../../../hris-backend/.agents/rules/scoping-convention.md) §1 dan nyatakan eksplisit di PRD — **Company-owned** (`company_id`, default), **Company+Location** (`company_id`+`branch_id`), atau **Global master** (tanpa scope, wajib justifikasi). Nyatakan juga siapa yang enforce filter (RBAC via `scope.FromContext`). Kolom scope harus muncul di §3 Data Schema entity yang bersangkutan. Jangan bikin PRD entity operasional tanpa keputusan scope-nya.

### 2.6. Dependencies (Ketergantungan)
Make coupling explicit and versioned. Two directions are MANDATORY:
- **Depends on** — modules this one consumes, with version. State *which field/output* is consumed and **reference** the source PRD section instead of restating its rules. *Example: "Payroll consumes `total_work_hours` from Attendance PRD §4.2 (v1.2)."*
- **Consumed by** — modules that depend on this one (reverse edge). Keeps the impact radius visible when this PRD changes.
- **External integrations** — 3rd-party APIs, SSO, Payment Gateways.

> Principle: loose coupling in docs, same as in code. Never duplicate a parent module's business rule; link to it. If a rule is truly shared, promote it to `PRD/_shared/glossary.md`.

## 3. Data Schema & Business Rules
After the 6 core pillars, provide the logical breakdown of the data models (Entities):
- **Header:** `## [Entity Name]`
- **Aturan Bisnis & Validasi:** Unique constraints, relations, format validations, AND the explicit **Error Messages** expected to be shown to the user when validation fails.
- **Sample Data:** A Markdown table illustrating what the data looks like. Columns should reflect the actual fields (e.g., `id`, `name`, `status`, `created_at`). This helps Frontend developers mock the UI.

## 4. Updating an Existing PRD
When the user references an existing PRD and asks for a change/new feature, follow this sequence — don't skip straight to editing:
1. **Brainstorm first.** Align on the scope of the change with the user before rewriting anything.
2. **Re-ground in real code** if the module is implemented (see §1) — the code may have moved since the PRD was last written.
3. Edit only the relevant sections. Don't delete still-valid history unless it's genuinely deprecated.
4. **Bump `version`** per the SemVer criteria in §1a, and refresh `updated`.
5. **Sync `PRD/README.md`** — registry row (version/status/updated) and dependency graph if an edge changed.
6. **Ripple-check dependents (MANDATORY):** run `python3 scripts/check-prd-deps.py` — any version bump (PATCH included) makes every dependent's pinned pointer stale and shows up as `FAIL`. For a MAJOR (breaking) bump, treat each `FAIL` as a real re-verify: open the dependent PRD and confirm the section it references still says what it thinks it says before bumping its pointer. For PATCH/MINOR, the underlying meaning didn't change, so just bump the pointer to match — no re-verify needed.
7. If the module has a TRD (`tech-spec.md`/`decision-log.md`) (Sedang/Kompleks tier), sync any technical-decision change there too — PRD stays WHAT/WHY, TRD stays HOW, never blend them.
8. **Commit atomically** with a `docs:` prefix, separate from any `feat:`/`fix:` code commit ([commit-convention.md](../../../hris-backend/.agents/rules/commit-convention.md)).
