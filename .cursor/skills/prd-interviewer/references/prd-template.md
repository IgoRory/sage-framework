# PRD Template -- Profitability Domain

Reference for prd-interviewer. Use this structure when generating the PRD
draft from the interview answer record. Every section heading and subsection
must appear in the output, even if the content is a TODO placeholder.

---

## PRD structure

The PRD is generated as a markdown file at `.sage/prds/[FEATURE_ID]/prd.md` with this exact structure:

---

# [Feature title]

**Linear issue:** [issue ID]
**Status:** Draft
**Author:** [PM name]
**Date:** [ISO date]
**Completeness score:** Not yet assessed

---

## 1. Feature overview

[2-3 sentences from Q1.2. Must answer: what does this feature do, who
uses it, and what can they do after it exists that they could not before.
Do not use vague qualifiers. Derive from Q1.1 and Q1.2 answers.]

---

## 2. Primary change type

[List the change types selected in Q1.3. One per line.]
- [ ] New user-facing screen or UI change
- [ ] Change to how calculations are performed
- [ ] Change to how costs or income are allocated
- [ ] Change to reporting or BI output
- [ ] Configuration or administration change
- [ ] Data model or schema change

---

## 3. Affected area

[From Q1.4. Name the specific area of the product, referencing codebase
components by name where confirmed in the interview.]

---

## 4. User roles

[From Q1.5. List each role that will interact with this feature.]

---

## 5. Requirements

[One requirement per line. Each must be a testable predicate -- a specific
condition and a specific outcome. No vague qualifiers. Derive from the
acceptance criteria in Q4.1 and the scenario descriptions throughout the
interview.

Format each requirement as:
"When [condition], [subject] [must/must not] [outcome]."

Examples:
- "When ProcessID = 1001 and the instrument type is Loan, the
  FTP_NetInterestIncome measure must equal the sum of
  FTP_GrossInterestIncome minus FTP_FundingCost for all instruments
  in the portfolio."
- "When usp_CalculateFTP returns -3, the system must display the message
  'Allocation blocked: instrument not initialised' in the status panel
  within 200ms."

If a requirement is parked (PM could not answer), write:
"TODO: [topic of parked question Q[N].[N]]"
]

---

## 6. Calculation logic (include only if Q1.3 includes b)

### 6.1 Affected measures
[From Q2.1. List each measure by exact name from vw_BI_AllInstruments.]

### 6.2 Affected stored procedures
[From Q2.2. List each procedure by exact name.]

### 6.3 Current behaviour
[From Q2.3. Describe current behaviour in predicate form. If parked: TODO.]

### 6.4 New behaviour
[From Q2.3. Describe new behaviour in predicate form. If parked: TODO.]

### 6.5 FTP and revision date changes
[From Q2.4. If not applicable: "No change to FTP revision date handling."]

### 6.6 Return code handling
[From Q2.5. For each relevant return code (-1 through -8), state the
required behaviour. If not applicable: "No change to return code handling."]

### 6.7 Instrument flag behaviour
[From Q2.6. If not applicable: "No change to instrument flag handling."]

---

## 7. Allocation methodology (include only if Q1.3 includes c)

### 7.1 Allocation type
[From Q3.1.]

### 7.2 Current methodology
[From Q3.2. In predicate form. If parked: TODO.]

### 7.3 New methodology
[From Q3.2. In predicate form. If parked: TODO.]

### 7.4 Allocation driver
[From Q3.4. Name the specific driver.]

### 7.5 GLAllocationLog changes
[From Q3.5. If not applicable: "No change to GLAllocationLog."]

### 7.6 Exclusions
[From Q3.6. If none: "No exclusions."]

---

## 8. Acceptance criteria

Generate ACs from **four sources**. Each AC must be agent-evaluable
(explicit input, explicit action/condition, explicit measurable output).
No vague qualifiers. Format:
"Given [precondition], when [action], then [measurable outcome]."

Use categorised IDs to trace AC provenance:

### 8.1 Requirement ACs (AC-REQ-NNN)

One AC per requirement from Section 5. Derive from Q4.1, Q4.2, and the
requirements list. Each requirement must have at least one AC.

AC-REQ-001: Given [precondition], when [action], then [outcome].
AC-REQ-002: ...

[If a requirement is deferred: "TODO: [DI-ID] -- [topic]"]

### 8.2 Edge-case ACs (AC-EC-NNN)

One AC per edge case documented in Section 11. Each edge case becomes a
testable scenario. Cross-reference the edge case condition.

AC-EC-001: Given [precondition], when [edge condition], then [outcome].
  Edge case: "[condition text from Section 11]"
AC-EC-002: ...

### 8.3 UI state ACs (AC-UI-NNN)

One AC per non-trivial state transition identified in the component
specification (Section 5b / component-spec.md). Cover state entries,
state exits, and inter-component impacts.

AC-UI-001: Given [component] is in [state A], when [trigger], then
  [component] transitions to [state B] and [observable effect].
  Component: [component name]
AC-UI-002: ...

[If no UI components: "Not applicable -- no UI components in scope."]

### 8.4 Error/empty/loading ACs (AC-ERR-NNN)

One AC per error path, empty state, and loading state identified in
Q5b.7-Q5b.9 and Section 6 (failure and recovery edge cases).

AC-ERR-001: Given [data condition], when [action], then [error behaviour].
  Recovery: [user recovery path]
AC-ERR-002: ...

[If no error states applicable: "Not applicable -- backend-only feature."]

### 8.5 Performance requirements
[From Q4.3. If none: "No performance requirements specified."]

### 8.6 Test scope
[From Q4.4. Name specific test files in scope.]

### 8.7 AC coverage summary

| Category | Count | Tier minimum | Status |
|----------|-------|-------------|--------|
| AC-REQ | [N] | [from tier] | [Met/Below] |
| AC-EC | [N] | [from tier] | [Met/Below] |
| AC-UI + AC-ERR | [N] | [from tier] | [Met/Below] |
| **Total** | **[N]** | **[from tier]** | |

If any category is below tier minimum, derive additional ACs from
under-covered areas before finalising the PRD.

---

## 9. Scope boundaries

### In scope
[Derive from the full interview -- everything confirmed as in scope.]

### Out of scope
[From Q5a.1 and Q5a.2. At minimum one explicit item. If the PM provided
none, write: "TODO: Product Manager to confirm explicit out-of-scope items
before completeness check."]

### Downstream impact
[From Q5a.3. Name specific reports, Dataverse entities, or exports that
must not be affected.]

### Dataverse boundary
[From Q5a.4. State explicitly whether this feature crosses the Dataverse
boundary and if so, which entities are read or written.]

---

## 10. UI and UX (include only if Q1.3 includes a or UI files found in recon)

### Screen inventory
[List each new or modified screen. Format:
| Screen name | New / Modified | Purpose | Layout description |
|-------------|---------------|---------|-------------------|
| [name] | [New/Modified] | [one sentence] | [top-to-bottom component placement and spatial relationships] |
]

### Navigation
[From Q5b.4. What triggers navigation to each screen.]

### Component specification
[This section states that the component specification is maintained in
a separate file. Write:
"Component specifications for all new and modified UI components are
documented in the companion Component Specification file.

See: [component-spec.md](./component-spec.md)

The component specification covers: [list component names]."
]

---

## 11. Edge cases and constraints

[From Section 6. Format each with a cross-reference to its corresponding
acceptance criterion in Section 8.2:

"[Condition]: [required behaviour]. → AC-EC-[N]"

Each edge case must have a corresponding AC-EC entry in Section 8.2 that
makes it testable. The cross-reference enables bidirectional tracing.

Examples:
- "NewInstFlag = 1: instrument must be included in FTP calculation but
  excluded from prior-period comparison. → AC-EC-001"
- "Named revision date in effect: FTP rate must be sourced from the
  rate table effective at the named date, not the current rate table.
  → AC-EC-002"
- "Naming note: the codebase uses both 'MktRisk' and 'MarketRisk' in
  different files -- build team must verify which is authoritative for
  this feature before writing tests. → AC-EC-003"

Edge cases from each of the seven categories (interaction sequence,
cascading behaviour, concurrency, state boundary, cross-component
dependency, data integrity, failure and recovery) should be grouped
under subheadings for clarity.]

---

## 12. Open items (Deferred Items)

[Automatically generated from the Unified Deferred Items List. Include all
items with status "Open" or "Accepted". Format:

| DI ID | Question | Section | Category | PM Reason | Status |
|-------|----------|---------|----------|-----------|--------|
| DI-001 | Q2.3 -- current vs new behaviour | P2 | Calculation | "Need to check with finance" | Accepted |
| DI-002 | Q5b.6 -- component states for grid | P6 | UI | "Will decide during development" | Accepted |
]

If no deferred items: "No open items -- all questions resolved during
interview."

Items with status "Accepted" indicate known gaps that must be resolved
before the PRD can pass prd-completeness-check at full score.

---

## Component specification file structure

The component specification is a separate file at `.sage/prds/[FEATURE_ID]/component-spec.md`.
Title: "[Feature title] -- Component Specification"

For each UI component identified in Section 5b:

---

### [Component name and type]
(e.g., "ProcessSelector -- multi-select dropdown")

**Functional description:**
[Predicate form -- what it does, not what it looks like. From Q5b.5b.]

**States:**
| State | Trigger | Description |
|-------|---------|-------------|
| Default | Page load | [description] |
| Loading | Data fetch initiated | [description] |
| [state] | [trigger] | [description] |

**User interactions:**
[From Q5b.10. List each interaction and what it does.]

**Selectable options:**
[From Q5b.5c. For dropdowns/selects: list all options or the data source.
For calculated fields: name the stored procedure or view.]

**Data binding:**
[From Q5b.5c. Name the specific field: Adjusted_GL field name, ProcessID,
SP parameter name, or view column name. Generic references do not pass
prd-completeness-check D5.]

---

