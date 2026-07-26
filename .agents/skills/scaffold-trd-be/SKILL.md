---
name: scaffold-trd-be
description: Guide for scaffolding Technical Requirements Documents (TRD) for the Backend (BE) to ensure architectural consistency with Go DDD.
---

# Scaffolding TRD Backend (Technical Requirements Document)

When the user asks to generate a TRD (or technical specs) for the Backend based on a PRD, you MUST follow these guidelines.

**Language Requirement:** Although these instructions are in English, the actual TRD content you generate MUST be written in Indonesian.

## 1. Directory & Context
- **Location:** All BE TRDs MUST be saved in `TRD/BE/<domain_name>/` (e.g., `TRD/BE/employee/tech-spec.md`).
- **Source of Truth:** A TRD BE must always reference an existing PRD. You must read the approved PRD first before writing the TRD. Do not invent new business flows that do not exist in the PRD.

## 2. Tech Stack & Architecture Constraints
**CRITICAL ROLE: TRANSLATING BUSINESS TO TECH**
Because the PRD is written strictly in business language without technical jargon, it is YOUR JOB as the TRD generator to infer and map those business intents into concrete backend technical implementations. (e.g., Translate "Secure User Session" into `JWT` & `Bcrypt`, translate "Access Control" into `Auth Middleware`, etc.).

The Backend uses **Golang** with **Domain-Driven Design (DDD)**. Your TRD must reflect this:
- **Architecture Layers:** Design must be divided into Domain (Entities/Interfaces), Application (Use Cases/Services), and Adapter (Repository/Delivery).
- **Primary Keys:** UUID generation must happen in the Domain/Adapter layer (in Go code), not via database auto-generation.
- **Relational DB:** The backend uses PostgreSQL. Avoid soft-deletes unless the PRD explicitly requires it.
- **Dependency Injection:** Mention the use of `Wire` where relevant.
- **Pagination & Scoping:** Use the standard `pkg/pagination` and enforce `company_id`/`branch_id` scope filters at the query builder level.

## 3. Mandatory Structure of TRD BE
A `tech-spec.md` file for BE must contain:

### 3.1. PRD Reference
Link to the PRD file and specify the version being implemented.

### 3.2. API Contracts
Design the RESTful endpoints to be exposed (URL, HTTP Method, Request JSON, Response JSON, HTTP Status Codes). You MUST explicitly define **Request Payload Validation** rules and the exact **Error Messages** (e.g., for 422 status codes) to ensure alignment with the PRD. This is the BE's promise to the FE.

### 3.3. DDD Architecture Design
- **Domain Layer:** What entities are created? What are their business rules?
- **Application Layer:** List of Use Cases (e.g., `CreateEmployeeUseCase`).
- **Adapter Layer:** Interfaces for Repositories and Handlers/Controllers.

### 3.4. Database Schema Reference
Detail the planned table structures and relationships. If requested by the user, execute the `scaffold-dbml` skill to create the `.dbml` file in `TRD/BE/databases/`.

### 3.5. Security & Multi-Tenant Scoping
Explain how RBAC and scope filters (`company_id`, `branch_id`) will be enforced at the database query level.

## 4. TRD Extensions (For Complex Modules)
If the module is complex and requires supporting documentation, you MUST also generate the 4 extension files in the same directory alongside `tech-spec.md`:
- `user-stories.md`: Breakdown of engineering tasks based on the `tech-spec.md`.
- `decision-log.md`: Architectural decisions and justifications (ADR).
- `data-dictionary.md`: Enums, status lifecycles, and exact error message mappings.
- `infrastructure.md`: Environment variables, secrets, and system-level integrations.
