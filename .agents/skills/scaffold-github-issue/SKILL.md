---
name: scaffold-github-issue
description: Guide for generating actionable GitHub Issue payloads based on TRD and PRD documents, using Event-Driven (Just-in-Time) workflow.
---

# Scaffolding GitHub Issues

When the user asks to generate a GitHub Issue (or execution task) based on a PRD or TRD, you MUST follow these guidelines. This skill translates documentation into an actionable checklist for engineers.

**Language Requirement:** Although these instructions are in English, the actual GitHub Issue content you generate MUST be written in Indonesian.

## 1. Input Requirements & Execution Modes
You must ask the user which phase they are triggering, or infer it from their request. 
There are **TWO MODES** of issue generation:

### MODE 1: Initial Phase (Start of Project)
Triggered when the PRD/TRD is just created. The Backend API does not exist yet.
- **Read:** `TRD/BE/...` and `TRD/FE/...` and `PRD/...`.
- **Action:** Generate exactly **TWO** issues:
  1. `[BE]` Issue.
  2. `[FE Slicing]` Issue.
- **Do NOT** generate the FE Integration issue in this mode.

### MODE 2: Integration Phase (Backend is Done)
Triggered when the user states that the Backend is ready and the Swagger contract has been pushed.
- **Read:** `TRD/FE/...` and the specific Swagger file `hris-docs/API_CONTRACTS/<module>.json`.
- **Action:** Generate exactly **ONE** issue:
  1. `[FE Integration]` Issue.
- **AI Intelligence Requirement:** You MUST analyze the `swagger.json` payload structure. If the Backend's JSON keys differ from what a typical Frontend interface would expect (or differ from the Mock), you MUST include explicit **Data Mapper Instructions** in the issue body. (e.g., *"Petunjuk Integrasi: Field 'full_name' dari BE harus di-map ke 'name' di AuthApiRepository"*).

## 2. Issue Output Format

### A. Backend Issue (Mode 1)
- **Title Pattern:** `[BE] - <Module Name>: <Feature/Task Name>`
- **Execution Checklist:** Break down by DB Migration, Domain layer, Application layer (Use Cases), Adapter (Handlers), and writing Unit Tests.

### B. FE Slicing Issue (Mode 1)
- **Title Pattern:** `[FE Slicing] - <Module Name>: <Feature/Task Name>`
- **Objective:** Focus entirely on UI development, layout, and mocking.
- **Execution Checklist MUST Include:** 
  - Creation of UI Components and Layouts.
  - Form validation (e.g., Zod, Superforms).
  - State Management (Svelte 5 Runes).
  - **Dependency Injection Mocking:** Implementation of the mock repository (`MockRepository`) and enforcing the `useMock = true` local flag. Do NOT mention MSW.

### C. FE Integration Issue (Mode 2)
- **Title Pattern:** `[FE Integration] - <Module Name>: <Feature/Task Name>`
- **Objective:** Connect the UI to the real Backend API.
- **Execution Checklist MUST Include:**
  - Flipping the DI container flag to `useMock = false`.
  - Implementation of the real API repository (`ApiRepository`) using `fetch`.
  - Handling network errors and API Interceptor logic.
  - **AI Data Mapping Insight:** The specific discrepancies you found between Swagger and UI that the engineer must map.
  - The UI (HTML/CSS) should NOT be modified in this ticket.

## 3. Mandatory Sections for ALL Issues
Every issue body MUST contain:
1. **🎯 Objective:** 1-2 sentence summary.
2. **📚 References:** Clickable Markdown links to PRD, TRD Main, and API_CONTRACTS (if applicable).
3. **🛠️ Execution Checklist:** Granular `- [ ]` actionable checkboxes.
4. **✅ Acceptance Criteria:** Exact GIVEN-WHEN-THEN rules from the PRD.
5. **🛑 Technical Constraints:** Strict rules from the TRD (e.g., "Must use UUID", "ssr=false", "useMock flag").

## 4. Automation Rule (Execution via GitHub CLI)
If the user explicitly asks to "create" or "update" the issue automatically:

1. **Temporary Files Rule:** You MUST create the temporary Markdown body files (`temp_be.md`, `temp_slicing.md`, etc.) **inside the `hris-docs` workspace**.
2. **Check for Token:** Read `hris-docs/.env`. If `GH_TOKEN` is missing, ask the user.

**Script for Mode 1 (Initial Phase):**
```bash
export GH_TOKEN=$(grep GH_TOKEN hris-docs/.env | cut -d '=' -f2)

# Create BE Issue
cd hris-backend
gh issue create --title "[BE]..." --body-file ../hris-docs/temp_be.md

# Create FE Slicing Issue
cd ../hris-frontend
gh issue create --title "[FE Slicing]..." --body-file ../hris-docs/temp_slicing.md

# Cleanup
rm ../hris-docs/temp_be.md ../hris-docs/temp_slicing.md
```

**Script for Mode 2 (Integration Phase):**
```bash
export GH_TOKEN=$(grep GH_TOKEN hris-docs/.env | cut -d '=' -f2)

# Create FE Integration Issue
cd hris-frontend
gh issue create --title "[FE Integration]..." --body-file ../hris-docs/temp_integration.md

# Cleanup
rm ../hris-docs/temp_integration.md
```
