# PRD Template

Use this template to produce the PRD draft after the interview. Replace
all `[placeholders]` with interview responses. Mark unresolved parked
items with `⚠️ GAP: [description]`. Do not omit sections — if a section
has no content, write "None identified" or the appropriate gap marker.

---

```
# [Feature title]

**Linear / ADO reference:** [issue ID and link]
**Component Specification:** [link to child page — add after creating it]
**Status:** Draft
**Author:** [PM name]
**Date:** [ISO date]

---

## 1. Overview

### Problem statement
[One to two sentences. Why does this feature need to exist?]

### Who benefits
[User roles, client types, or workflows that benefit]

### Expected outcome
[Business or product outcome — what improves as a result]

### Background
[Client driver, internal decision, or compliance requirement.
Any related features this extends or depends on.]

---

## 2. Functional requirements

[Numbered list. Each requirement is a testable predicate.
No vague language. Each requirement has a REQ-N identifier.]

REQ-1: [requirement]
REQ-2: [requirement]
...

---

## 3. Acceptance criteria

[Per requirement or grouped. Each AC is pass/fail testable.]

**REQ-1:** [AC]
**REQ-2:** [AC]
...

---

## 4. Screen inventory

[Every affected or new page and screen. Include the mockup file path
for each. This is what prd-completeness-check uses to verify D4.]

| Screen name | Page / location | New or modified | Mockup path |
|---|---|---|---|
| [name] | [page] | [New / Modified] | [repo path] |
...

---

## 5. User flows

[Step-by-step description of each user flow identified in P2.
One subsection per flow.]

### Flow 1: [name]
1. [step]
2. [step]
...

### Flow 2: [name] (if applicable)
...

---

## 6. Permissions and roles

[Which roles can access this feature, and what can each role do?
What do users without the required role see?]

| Role | Access | Notes |
|---|---|---|
| [role] | [full / read-only / hidden] | [any conditions] |
...

---

## 7. Edge, empty, and error states

[Functional-area level. Component-level states are in the Component
Specification child page.]

### [Functional area name]

**Empty state:**
[What renders when there is no data]

**Error states:**
- API / stored procedure failure: [what the user sees]
- Validation failure: [what the user sees]
- Timeout: [what the user sees]
- [Any Profitability-specific error, e.g. ProcessID not found]: [what the user sees]

**Boundary conditions:**
- [Field name]: [min/max, and behaviour at boundary]
...

Repeat for each functional area.

---

## 8. Data and calculations

[Any calculations or data operations not captured in requirements.
For Profitability: name Adjusted_GL fields, ProcessIDs, stored procedures,
and views involved. State what is read and what is written.]

### Data reads
| Source | Field(s) / SP | Used for |
|---|---|---|
| [Adjusted_GL / SP / view] | [field or SP name] | [purpose] |
...

### Data writes
| Target | Field(s) / SP | Triggered by |
|---|---|---|
| [table / SP] | [field or SP name] | [user action or event] |
...

### Background processes (if applicable)
[Description, trigger condition, failure behaviour]

---

## 9. Out of scope

[Explicit list. Every item names a specific capability, integration,
or behaviour that is NOT included in this feature.]

The following are explicitly excluded from this feature:

- [item]
- [item]
...

**Data boundary:**
[If this feature touches Adjusted_GL, GLAllocationLog, or any shared
stored procedure: what it reads, what it writes, and what it does not
touch.]

**Pyramid Analytics / IMDB:**
[Explicitly state whether Pyramid model updates are in or out of scope.
Default: out of scope unless confirmed otherwise.]

---

## 10. Open items / gaps

[List of all parked questions that were not resolved during the interview.
Each item must be resolved before prd-completeness-check is run.]

⚠️ GAP: [question / decision outstanding]
⚠️ GAP: [question / decision outstanding]
...

[If no gaps: "None — all items resolved during interview."]
```
