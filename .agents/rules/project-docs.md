# Project Documentation Rules (Requirements & Technical)

The `hris-docs` workspace serves as the **Control Plane** of the project. There are three main document pillars that MUST be designed and permanently stored here before any code execution takes place.

**CRITICAL LANGUAGE REQUIREMENT:** Although these rules and associated AI skills are written in English for optimal LLM comprehension, **ALL generated output documents (PRD, TRD, DBML, and TRD Extensions) MUST be written in Indonesian.**

## 1. Product Requirements Document (PRD) (Business Phase)
- If the user requests feature designs, requirements, or business flows (not pure technical implementations), use the PRD format.
- **MUST** be saved in the `PRD/` folder (e.g., `PRD/employee.md`).
- Formatting MUST adhere to the `PRD/_TEMPLATE.md` template and utilize the `scaffold-prd` skill.
- **Core Principle:** PRDs ONLY contain the WHAT and WHY. Do NOT discuss the HOW (no code architecture, Svelte validation types, or physical SQL relationships should be present here).

## 2. Technical & Architecture Documents (Design Phase)
After a PRD is approved, the technical specifications (the HOW) are detailed separately for Backend (BE) and Frontend (FE). These documents will eventually be published as GitHub Issues to be executed by their respective teams/agents.

### A. TRD BE (`TRD/BE/<domain_name>/`)
- Saved in a sub-folder per domain, e.g., `TRD/BE/employee/tech-spec.md`.
- Discusses DDD architecture, API contracts, business logic sequence diagrams, error handling, and decision logs (ADR).
- **Completeness Levels:**
  - **Simple**: DBML schema & brief API contract summary.
  - **Medium**: `tech-spec.md` (core architecture + detailed API).
  - **Complex**: `tech-spec.md` + the 4 extension files.

### B. TRD FE (`TRD/FE/<domain_name>/`)
- Saved in a sub-folder per domain, e.g., `TRD/FE/employee/tech-spec.md`.
- Discusses Svelte UI component design, state management (using Svelte 5 Runes), data mock-ups for parallel development, client-side validation strategies, and error handling.

### C. Supporting Documents (TRD Extensions)
Applicable to **both sides (TRD BE and FE)**. Created when the designed module has high complexity. These documents are stored alongside `tech-spec.md` in their respective domain sub-folders:
- **`user-stories.md`**: Breaks down the specifications from `tech-spec.md` into actionable engineering tasks (tickets).
- **`decision-log.md`**: Records Architecture Decision Records (ADR) that answer "WHY" a specific technology or pattern was chosen (e.g., why SSR is disabled, why Redis is not used).
- **`data-dictionary.md`**: Contains enum whitelists, status dictionaries (lifecycle data), magic string standards, and precise Error Message Mappings (e.g., 401/422).
- **`infrastructure.md`**: Explains interactions with the environment or external infrastructure (e.g., Secret Keys, Cookie configurations, Dependency Injection/Mocking flags, S3/Redis integrations).

## 3. Database Markup (DBML)
- Relational database schemas **MUST** be written in DBML format (`.dbml`).
- Saved in the `TRD/BE/databases/` folder (e.g., `TRD/BE/databases/employee.dbml`).
- DBML is the **single source of truth** for SQL migrations and database design in the BE team. Dummy table data in the PRD does **NOT** replace the physical DBML structure.
- Use the `scaffold-dbml` skill to precisely translate the "Data Schema" chapter of the PRD into physical DBML.
