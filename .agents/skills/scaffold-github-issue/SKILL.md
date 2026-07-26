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

## 2. Issue Output Format
Your output must be a Markdown block that the user can directly copy-paste into GitHub's "New Issue" body.

### Issue Title
The title must be descriptive and follow this pattern:
`[FE] or [BE] - <Module Name>: <Feature/Task Name>`
*(Example: `[BE] - Employee: Create CRUD Endpoints for Master Employee`)*

### Issue Body
The issue body MUST contain the following sections:

#### 1. 🎯 Objective
A brief 1-2 sentence summary of what the engineer needs to build, referencing the PRD goal.

#### 2. 📚 References
Links to the documents the engineer MUST read before coding:
- **PRD:** `[Link to PRD in hris-docs]`
- **TRD:** `[Link to TRD in hris-docs]`
- **Figma/Design:** `[Link to Figma]` (if FE)

#### 3. 🛠️ Execution Checklist
Break down the TRD into granular, actionable checkboxes (`- [ ]`). This is the most critical part. 
- **For BE:** Break down by DB Migration, Domain layer, Application layer (Use Cases), Adapter (Handlers), and writing Unit Tests.
- **For FE:** Break down by Types/Interfaces creation, State/Runes setup, API Service setup, UI Component building, and Validation.

#### 4. ✅ Acceptance Criteria (Definition of Done)
Extract the exact GIVEN-WHEN-THEN acceptance criteria from the PRD that apply to this specific engineering task.

#### 5. 🛑 Technical Constraints
Summarize any strict rules from the TRD (e.g., "Must use UUID", "Must enforce company_id scope", "Must use Svelte Runes").

## 3. Workflow Rule
Do NOT save the issue text as a file in the repository unless explicitly asked. Your primary job is to output the Markdown payload directly in the chat so the user can copy it to the GitHub UI.
