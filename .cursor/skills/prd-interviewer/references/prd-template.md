# PRD Template -- Profitability Domain

Reference for prd-interviewer. Use this structure when generating the PRD
draft from the interview answer record. Every section heading and subsection
must appear in the output, even if the content is a TODO placeholder.

---

## PRD structure

The PRD is generated as a Notion page with this exact structure:

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

[One AC per requirement. Format:
"Given [precondition], when [action], then [measurable outcome]."

The precondition and outcome must be specific enough that an agent can
evaluate pass/fail without human judgment.

Derive from Q4.1 and Q4.2. If parked: TODO.]

### Performance requirements
[From Q4.3. If none: "No performance requirements specified."]

### Test scope
[From Q4.4. Name specific test files in scope.]

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
| Screen name | New / Modified | Purpose |
|-------------|---------------|---------|
| [name] | [New/Modified] | [one sentence] |
]

### Navigation
[From Q5b.4. What triggers navigation to each screen.]

### Mockup files
[For each screen: the expected file path in the repository where the
wireframe-agent will write the mockup. Format:
| Screen | Mockup path |
|--------|------------|
| [name] | docs/wireframes/[feature-id]/[screen-name].html |
]

### Component specification
[This section states that the component specification is maintained in
a separate Notion child page. Write:
"Component specifications for all new and modified UI components are
documented in the companion Component Specification page linked below.

[Link to Component Specification Notion child page]

The component specification covers: [list component names]."
]

---

## 11. Edge cases and constraints

[From Section 6. Format each as:
"[Condition]: [required behaviour]."

Examples:
- "NewInstFlag = 1: instrument must be included in FTP calculation but
  excluded from prior-period comparison."
- "Named revision date in effect: FTP rate must be sourced from the
  rate table effective at the named date, not the current rate table."
- "Naming note: the codebase uses both 'MktRisk' and 'MarketRisk' in
  different files -- build team must verify which is authoritative for
  this feature before writing tests."
]

---

## 12. Open items (TODOs)

[Automatically generated from all parked questions. Format:
| Question | Topic | Owner |
|----------|-------|-------|
| Q[N].[N] | [topic] | Product Manager |
]

If no parked questions: "No open items."

---

## Component specification page structure

The component specification is a Notion child page of the PRD.
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

