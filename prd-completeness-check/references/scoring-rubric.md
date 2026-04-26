# Scoring Rubric — Detailed Sub-criteria and Examples

Reference file for `prd-completeness-check`. Read this when scoring is
ambiguous, when a finding needs a worked example to confirm it applies,
or when handling an edge case not covered in the main SKILL.md.

---

## Table of contents

1. [D1 — Requirement coverage](#d1)
2. [D2 — AC specificity](#d2)
3. [D3 — Edge/empty/error state coverage](#d3)
4. [D4 — Mockup file completeness](#d4)
5. [D5 — UI component specification](#d5)
6. [D6 — Out-of-scope clarity](#d6)
7. [Edge cases in scoring](#edge-cases)

---

## D1 — Requirement coverage {#d1}

### Vague language — examples

**Fails (deduct 2 each):**
- "The save button should feel responsive to user input."
- "The allocation table may include subtotals where appropriate."
- "The system handles errors gracefully."
- "The export function should be performant."
- "Users can manage their allocation rules."

**Passes:**
- "The save button becomes disabled within 100ms of the user clicking it
  and re-enables when the save operation resolves."
- "The allocation table includes a subtotals row when the result set
  contains more than one department."
- "When the stored procedure returns an error code, the system displays
  an inline error message in the form header within 200ms."

### Unstated assumption — Profitability examples

**Fails (deduct 3 each):**
- "The export respects the user's existing column preferences." —
  'existing column preferences' is not defined in this PRD or any
  linked document.
- "Allocations follow the standard calculation methodology." —
  'standard methodology' is not defined here.
- "The component uses the current FTP rate." — which FTP rate, from
  which source, at which granularity is not specified.

**Passes:**
- "The export includes only columns currently visible in the table at
  the time the export is triggered, as defined in REQ-14."
- "FTP rate is read from the Adjusted_GL FTPRate field for the
  instrument's ProcessID as defined in the ProcessID reference table."

### Implied requirement absent — Profitability examples

If the PRD has a requirement "Users can edit cost pool allocation rules"
and there is no requirement covering what happens to historical allocation
results when a rule is edited retroactively, that is an implied requirement
that is absent. Deduct 4.

If the PRD adds a new ProcessID category but does not include a requirement
covering how existing records with no ProcessID assignment are handled,
that is an implied requirement that is absent. Deduct 4.

---

## D2 — AC specificity {#d2}

### Well-formed ACs — Profitability examples

These pass without deduction:
- "The allocation results table refreshes within 2 seconds of a filter
  change on a dataset of up to 50,000 rows."
- "The stored procedure returns HTTP 422 with a field-level error message
  identifying the specific ProcessID when a ProcessID is not found in
  the reference table."
- "The department filter renders the empty state message 'No departments
  found' and a 'Clear filters' link when the filtered result set is empty."
- "Users with Viewer role see the read-only allocation summary; the Edit
  Rule button is not present in the DOM."
- "The export file is named [FeatureName]_[YYYY-MM-DD].csv and downloads
  immediately without a confirmation dialog."

### Poorly formed ACs — examples

**Restates requirement (deduct 2):**
- Requirement: "Users can filter the allocation table by department."
  AC: "The allocation table can be filtered by department."

**Subjective (deduct 2):**
- "The filter interaction feels immediate."
- "Error messages are clear and helpful."
- "The export completes in a reasonable time."

**Cannot be expressed as pass/fail (deduct 3):**
- "The UI is consistent with existing allocation screens." — no objective
  test is possible without defining which attributes must match.
- "Performance is acceptable under production load." — no threshold.

---

## D3 — Edge/empty/error state coverage {#d3}

### How to identify functional areas

A functional area is any discrete piece of behaviour with its own data
operations, UI surface, or user interaction path. For Profitability features,
typical functional areas include:

- Allocation rule configuration form
- Allocation results table or grid
- Export / download function
- Filter or search controls
- Rule save / publish / activate flow
- Any background calculation or stored procedure invocation

Each is a separate functional area for D3 purposes.

### Empty state — what counts

An empty state is required when a functional area can render data that
might not exist. The spec must state:
- What visual element renders (illustration, icon, message, or all three)
- What the message text is (or that it is defined in the mockup)
- Whether any action is available (e.g. "Add your first rule" CTA)

"Shows empty state" without detail does not satisfy this. A component
spec entry in D5 that specifies the empty state for that component does
satisfy it — note the cross-reference in the finding.

### Error state — what counts

Must cover at minimum:
- API / stored procedure failure: what the user sees when the call fails
- Validation failure: what renders when form input is invalid
- Timeout: what happens if the operation exceeds the expected duration
- Data integrity error: relevant for Profitability features where a
  ProcessID or GL code reference fails to resolve

### Boundary conditions — Profitability examples

Required when the PRD involves:
- Percentage / ratio fields: behaviour at 0%, 100%, and > 100%
- Allocation weight fields: behaviour when weights do not sum to 100%
- Date range inputs: behaviour when end date precedes start date
- Numeric cost inputs: min/max and behaviour at boundary values
- Text fields for GL codes, account numbers: character limits and
  format validation

---

## D4 — Mockup file completeness {#d4}

### Handling implicit paths

Some PRDs reference mockups by screen name without explicit file paths.
In this case:
1. Check the repo for a `mockups/` or `designs/` directory at project root
2. Look for files whose names match or closely correspond to screen names
3. If a reasonable match exists: record EXISTS with a note that the path
   was inferred
4. If no match: record MISSING

Do not assume a file exists because the PRD says it was created.

### What D4 does not assess

D4 does not score annotation quality, visual accuracy, or whether the
mockup reflects the written requirements. These are not D4 concerns:
- Whether the mockup shows correct data
- Whether the mockup includes state annotations
- Whether navigation flows are labelled

These are assessed through D5 (component specification) and the BA
interview at kick-off. A mockup that exists but is visually wrong still
scores full points in D4. The hook at S5 of the build phase enforces
that mockups are read — it does not enforce that they are correct.

---

## D5 — UI component specification {#d5}

### Minimum state requirements by component type

A component spec listing fewer states than the minimum below is incomplete
unless the PRD explicitly excludes specific states with a rationale.

| Component type | Minimum required states |
|---|---|
| Text input / form field | default, focused, populated, error, disabled, read-only |
| Numeric input | default, focused, populated, error (invalid), error (out of range), disabled |
| Button (primary action) | default, hover, active/pressed, loading, disabled |
| Button (destructive) | default, hover, active/pressed, disabled, confirmation (if destructive) |
| Dropdown / single-select | closed-default, closed-selected, open, option-hovered, selected, disabled, empty (no options) |
| Multi-select | closed-default, closed-with-selections, open, option-hovered, option-selected, all-selected, disabled, empty |
| Data table / grid | loading, populated, empty, row-hovered, row-selected, error, sorted (asc/desc per column) |
| Modal / dialog | closed, opening (if animated), open, loading (if async content), error, closing |
| Toggle / switch | on, off, loading, disabled |
| Date picker | closed, open, date-selected, range-selected (if range), invalid-date, disabled |
| Tab set | default (first tab active), tab-N-active, tab-hovered |
| Tooltip | hidden, visible |
| Filter panel | collapsed, expanded, filters-active, filters-cleared |
| Progress indicator | idle, in-progress (with %), complete, error |

### Functional description — what passes and what fails

**Fails:**
- "Displays the allocation summary." — visual description only
- "Shows cost pool data." — no behaviour specified
- "A dropdown for selecting departments." — describes form, not function

**Passes:**
- "Filters the allocation results table to show only rows matching the
  selected department. Re-queries the view immediately on selection.
  When 'All departments' is selected, no filter is applied and all rows
  are shown."
- "Accepts a percentage value between 0 and 100. On blur, validates that
  the sum of all weight fields on the form equals 100. If the sum is not
  100, sets all weight fields to error state and displays the variance."

### Data binding — Profitability examples

**Fails:**
- "Reads allocation data from the API."
- "Populated from the database."
- "Shows the FTP rate."

**Passes:**
- "Reads from `Adjusted_GL.FTPRate` filtered by `ProcessID` using stored
  procedure `usp_GetFTPRateByProcessID`. No write operation."
- "Reads available departments from `vw_DepartmentList`. Writes the
  selected DepartmentID to the active filter state, which triggers a
  re-execution of `usp_GetAllocationResults` with the DepartmentID
  parameter."
- "Reads from `GLAllocationLog.AllocatedAmount` grouped by CostPoolID
  for the current reporting period. Read-only — no write operation."
- "Derives display value from `Adjusted_GL.InterestIncome /
  Adjusted_GL.AverageBalance * 12 * 100`. Calculated at query time —
  not stored. No write operation."

### Selectable options — Profitability examples

If a dropdown presents ProcessID categories:
```
Options:
  - "All categories" (value: null, default selection)
  - "Core" (value: "CORE")
  - "FTP" (value: "FTP")
  - "Capital" (value: "CAPITAL")
  - "Overhead" (value: "OVERHEAD")
Display logic: all options always visible; no conditional hiding
Default: "All categories"
```

If a dropdown's options are data-driven (loaded from an API):
```
Options: dynamically loaded from usp_GetActiveCostPools
Format: [CostPoolName] (value: CostPoolID)
Default: first item in result set
Empty state: dropdown disabled, placeholder "No cost pools configured"
```

### Reused component scoring

If a component spec says "Same as the Department Filter on the Allocation
Summary page" and lists no differences:
- Element 2 (functional description): MISSING — deduct applies
- Element 3 (states): MISSING — deduct applies
- Elements 1, 4, 5, 6 may be satisfied by the reference if the
  referenced spec is complete and accessible

A reused component spec that explicitly lists only the delta from the
referenced component — "Same as Department Filter on Allocation Summary
page, with the following differences: [list]" — satisfies elements 2
and 3 fully if the delta covers all behavioural and state differences.

### Affected components — what counts

"Affected" means the component's behaviour, appearance, available options,
data source, or state transitions change as a result of this feature, even
if the component already exists and is not being rebuilt. Examples:

- An existing filter panel gains a new filter option → affected
- An existing table gains a new sortable column → affected
- An existing form gains a new conditional validation rule → affected
- An existing button's disabled condition changes → affected
- An existing modal gains a new error state → affected

If a component is visually unchanged and its behaviour is unchanged, it is
not affected and does not need a spec entry.

---

## D6 — Out-of-scope clarity {#d6}

### Well-formed out-of-scope section — Profitability example

```
## Out of scope

The following are explicitly excluded from this feature:

- Bulk rule editing across multiple cost pools simultaneously
  (planned as separate feature)
- Historical rule versioning and audit trail for allocation rule changes
- Export of the allocation results table — this feature adds export of
  the rule configuration only
- Changes to the Pyramid Analytics data model or IMDB — this feature
  writes to Adjusted_GL only; Pyramid model updates are a separate
  work stream owned by Sriyanka
- Retroactive recalculation of historical periods when a rule is
  changed — the rule change applies to the current and future periods
  only
```

### What triggers a deduction — Profitability examples

**Deduct 3 per implied adjacent behaviour:**
- PRD adds a new cost pool type but does not address whether existing
  ProcessID assignments need re-mapping → deduct 3
- PRD adds instrument-level yield display but does not address whether
  the Pyramid data model needs updating → deduct 3
- PRD modifies the allocation results table but does not address whether
  the corresponding export format changes → deduct 3

**Deduct 4 for shared data model boundary missing:**
- Feature writes to Adjusted_GL but out-of-scope section does not name
  which fields are written and which are not touched → deduct 4
- Feature calls a stored procedure also called by another feature but
  does not address whether the stored procedure signature is changing →
  deduct 4

---

## Edge cases in scoring {#edge-cases}

### PRD with no screen inventory

- D4: 0/15 — cannot verify file existence without a list
- D5: assess as best possible from requirements; note that component
  count may be underestimated; flag in report
- Report note: "Add an explicit screen inventory listing all affected
  pages and screens with their expected mockup file paths."

### Non-UI feature (background process, stored procedure change, API endpoint)

**D4 adjustment:**
Replace the mockup file check with a data flow / sequence diagram check.
- Diagram committed to repo showing: inputs, processing steps, outputs,
  error paths, and any integration points → 15/15
- Diagram present but missing error paths or integration points → 9/15
- No diagram → 0/15

**D5 adjustment:**
Replace the component specification check with a data contract
specification check. The spec must document:
1. Input parameters (name, type, valid range, required/optional)
2. Output schema (field names, types, nullability)
3. Error codes and their meanings
4. Side effects (what other tables or systems are affected)
5. ProcessID or GL code dependencies (Profitability-specific)
6. Performance characteristics (expected execution time, row volume)

Score using the same six-element per-unit structure as UI components,
treating the stored procedure or API endpoint as the "component."

### Re-assessment after a FAIL

- Re-score all six dimensions from scratch — do not carry forward prior scores
- Include prior score and delta in the report (see report template)
- Call out which findings were resolved and which remain open
- If a previously passing dimension has regressed (PRD was edited and
  introduced new issues), score the regression and note it explicitly

### Component specification child page exists but is empty or a template stub

Treat as absent. Record D5 = 0/25 with finding:
"Component specification page exists but contains no component entries.
Populate the spec for all [N] new and affected components before
re-assessment."
