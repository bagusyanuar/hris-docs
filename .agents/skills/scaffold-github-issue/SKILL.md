---
name: scaffold-github-issue
description: Guide for generating actionable GitHub Issue payloads based on TRD and PRD documents.
---

# Scaffolding GitHub Issues

When the user asks to generate a GitHub Issue (or execution task) based on a PRD or TRD, you MUST follow these guidelines. This skill translates documentation into an actionable checklist for engineers.

**Language Requirement:** Although these instructions are in English, the actual GitHub Issue content you generate MUST be written in Indonesian.

## 1. Input Requirements
Before generating the issue, you MUST read the corresponding TRD (Technical Requirements Document) and PRD (Product Requirements Document). 
- If targeting Backend, read `TRD/BE/...`
- If targeting Frontend, read `TRD/FE/...`
- Always cross-reference with the PRD for Acceptance Criteria.

## 2. Issue Output Format (Backend vs Frontend)
Your output must be a Markdown block that the user can directly copy-paste into GitHub's "New Issue" body.

### A. Backend Issues
For Backend requests, generate **ONE** comprehensive issue.
- **Title Pattern:** `[BE] - <Module Name>: <Feature/Task Name>`
- **Execution Checklist:** Break down by DB Migration, Domain layer, Application layer (Use Cases), Adapter (Handlers), and writing Unit Tests.

### B. Frontend Issues (SPLIT: Slicing & Integration)
For Frontend requests, you MUST generate **TWO SEPARATE** Markdown blocks representing two distinct sequential issues.

**Issue 1: Slicing Phase**
- **Title Pattern:** `[FE Slicing] - <Module Name>: <Feature/Task Name>`
- **Objective:** Focus entirely on UI development, layout, and mocking.
- **Execution Checklist MUST Include:** 
  - Creation of UI Components and Layouts.
  - Form validation (e.g., Zod, Superforms).
  - State Management (Svelte 5 Runes).
  - **Dependency Injection Mocking:** Implementation of the mock repository (`MockRepository`) and enforcing the `useMock = true` local flag. Do NOT mention MSW.

**Issue 2: Integration Phase**
- **Title Pattern:** `[FE Integration] - <Module Name>: <Feature/Task Name>`
- **Objective:** Focus entirely on connecting the UI to the real Backend API.
- **Execution Checklist MUST Include:**
  - Flipping the DI container flag to `useMock = false`.
  - Implementation of the real API repository (`ApiRepository`) using `fetch`.
  - Handling real network errors and API Interceptor logic (e.g., 401 token rotations).
  - The UI (HTML/CSS) should NOT be modified in this ticket.
- **API Contract References:** The AI MUST instruct the engineer to read the `swagger.json` located in `hris-docs/API_CONTRACTS/` or open the staging Swagger UI link to determine the exact payload structures before writing the `ApiRepository`.

## 3. Mandatory Sections for ALL Issues
Every issue body (whether BE, FE Slicing, or FE Integration) MUST contain:
1. **🎯 Objective:** 1-2 sentence summary of what to build.
2. **📚 References:** Clickable Markdown links to PRD, TRD Main, TRD Extensions (user-stories, decision-log, etc.) pointing to the `hris-docs` repository.
3. **🛠️ Execution Checklist:** Granular `- [ ]` actionable checkboxes as described above.
4. **✅ Acceptance Criteria:** The exact GIVEN-WHEN-THEN rules extracted from the PRD.
5. **🛑 Technical Constraints:** Strict rules from the TRD (e.g., "Must use UUID", "ssr=false", "useMock flag").

## 4. Workflow Rule (Default: Chat Output)
By default, do NOT save the issue text as a file in the repository. Output the Markdown payload directly in the chat so the user can copy it to the GitHub UI.

## 5. Automation Rule (Execution via GitHub CLI)
If the user explicitly asks to "create" or "update" the issue automatically:
1. **Check for Token:** Read the `hris-docs/.env` file. If `GH_TOKEN` is `ghp_your_personal_access_token_here` or empty, ask the user to fill it in first.
2. **Execute Create (Backend):**
   ```bash
   export GH_TOKEN=$(grep GH_TOKEN hris-docs/.env | cut -d '=' -f2)
   cd hris-backend
   gh issue create --title "[Title]" --body "[Markdown Body]"
   ```
3. **Execute Create (Frontend - Two Steps):** You must run the command twice, once for Slicing and once for Integration.
   ```bash
   export GH_TOKEN=$(grep GH_TOKEN hris-docs/.env | cut -d '=' -f2)
   cd hris-frontend
   gh issue create --title "[FE Slicing]..." --body "[Slicing Body]"
   gh issue create --title "[FE Integration]..." --body "[Integration Body]"
   ```
