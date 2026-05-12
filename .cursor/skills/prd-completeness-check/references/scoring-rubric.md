# Scoring Rubric -- Detailed Sub-criteria and Examples

Reference file for prd-completeness-check. Read this when scoring is
ambiguous, when a finding needs a worked example, or when handling an
edge case not covered in the main SKILL.md.

---

## D1 -- Requirement coverage: vague language examples

FAILS (deduct 2 each):
- "The save button should feel responsive to user input."
- "The allocation table may include subtotals where appropriate."
- "The system handles errors gracefully."
- "The export function should be performant."
- "Users can manage their allocation rules."

PASSES:
- "The save button becomes disabled within 100ms of the user clicking
  it and re-enables when the save operation resolves."
- "The allocation table includes a subtotals row when the result set
  contains more than one department."
- "When the stored procedure returns an error code, the system displays
  an inline error message within 200ms."

Profitability-specific vague language that fails:
- "Allocations follow the standard calculation methodology." -- which
  methodology? Reference the specific stored procedure by name.
- "The report reflects the current period data." -- which ProcessID?
  Which revision date?
- "FTP rates are applied correctly." -- define "correctly" in terms of
  the specific rate table and revision date logic.

---

## D2 -- AC specificity: agent-evaluable examples

PASSES (agent can evaluate without human judgment):
- "Given ProcessID = 1001 and instrument type = Loan, when the
  calculation runs, then FTP_NetInterestIncome = sum of
  FTP_GrossInterestIncome minus FTP_FundingCost for all instruments
  in the portfolio."
- "When the user selects a date range with no instruments, the
  result table displays the message 'No instruments found for
  selected period' and the export button is disabled."
- "When usp_AllocateExpense returns -3, the UI displays 'Allocation
  blocked: instrument not initialised' in the status panel."

FAILS (requires human judgment):
- "The FTP calculation returns the expected result."
- "The allocation looks correct for the test dataset."
- "The UI is intuitive."

---

## D3 -- Return code handling (Profitability-specific)

Return codes -1 through -8 indicate initialisation blocking conditions.
For any PRD that touches calculation triggers, verify all return codes
are handled.

Return codes and their expected UI/system behaviour must be specified:
- -1: General initialisation failure
- -2: Missing instrument record
- -3: Instrument not initialised for this process
- -4: Missing FTP rate
- -5: Missing allocation rule
- -6: Missing capital factor
- -7: Missing provision rate
- -8: Calculation locked by concurrent process

A PRD that says "handle errors from the stored procedure" without
specifying each return code separately fails D3.

---

## D5 -- Component specification: detailed guidance

### Functional description -- predicate form

The functional description must answer: what does this component DO,
not what does it LOOK LIKE.

FAILS:
- "A dropdown menu showing available processes."
- "A blue button in the top right corner."
- "A table with columns for instrument ID, FTP rate, and allocation."

PASSES:
- "Filters the calculation result set to the instruments associated
  with the selected ProcessIDs. When no ProcessID is selected, all
  instruments in the current revision date are shown."
- "Triggers usp_ExportResults with the current filter state as
  parameters. Disabled while a calculation is running (indicated
  by ProcessStatus = 'Running' in the session state)."
- "Displays one row per instrument from vw_BI_AllInstruments. Rows
  are sorted by InstrumentID ascending by default. Supports column
  sorting on all 42 measures."

### Data binding -- Profitability-specific examples

Generic (FAILS D5 data binding element):
- "Populated from the calculation results."
- "Shows the current allocation data."
- "Bound to the instrument data."

Specific (PASSES):
- "Populated from vw_BI_AllInstruments filtered by the selected
  ProcessID and revision date. Column FTP_NII maps to
  FTP_NetInterestIncome in the view."
- "ProcessID dropdown options populated from the Processes table
  in Dataverse, filtered to active processes (IsActive = 1)."
- "Allocation amount sourced from GLAllocationLog.AllocatedAmount
  where AllocationRuleID matches the selected rule."
- "SP parameter @ProcessID passed from the session state
  ProcessSelector.selectedValue."

### Minimum states by component type

Dropdown / select:
  default (no selection), open, selected (one or more items),
  disabled, error (load failure), loading (async population)

Table / data grid:
  populated, empty (zero rows with empty state message), loading,
  error (fetch failure), filtered (subset shown)

Button:
  default, hover, active (click in progress), disabled, loading
  (async operation triggered)

Form field / text input:
  default, focused, filled (has value), error (validation failure
  with message), disabled, read-only

Modal / side panel:
  hidden, opening (animation), visible, loading (content fetching),
  error, closing (animation)

Checkbox / toggle:
  unchecked, checked, indeterminate (if applicable), disabled

Date picker:
  default (no date), open (calendar visible), selected, disabled,
  error (invalid date)

### Reused components

A component that exists in the codebase and is NOT modified by this
feature does not require a component specification entry. Only NEW
components and components that are MODIFIED (new state, new interaction,
new data binding) are assessed in D5.

If a reused component is modified for this feature, only document the
delta -- what changes, not the full existing spec.

### Non-UI features

For features with no UI components (pure calculation, stored procedure,
data pipeline), D5 is replaced by a data contract specification check:

Check that the PRD specifies:
- Input parameters with types and constraints
- Output schema with field names, types, and nullability
- Error conditions and their return values
- Performance contract (if applicable -- e.g., max execution time)

Score D5 against these four elements (25/4 = 6.25pts each, round to
nearest integer).

---

## Edge cases in scoring

### PRD with no screen inventory

If there is no screen inventory section, D4 = 0/15.
Record finding: "No screen inventory section found in PRD."
Do not attempt to infer screens from mockup content.

### PRD for a non-UI feature (pure calculation or data)

D4 = N/A -- treat as 15/15 (no screens to check).
D5 = replaced by data contract specification check (see above).

### Re-assessment of a previously scored PRD

When re-assessing a PRD that has a prior score on record:
1. Score all dimensions fresh -- do not carry forward prior scores
2. After scoring, append the delta section to the report showing:
   - Prior score and date
   - Points gained per dimension
   - Findings resolved
   - Findings still open
3. If the prior score was >= threshold and the new score drops below:
   flag explicitly -- a regression has occurred.

---

## D3 -- Edge-case category coverage (Tier 2+ features)

For features classified at Tier 2 (Medium) or above by the prd-interviewer's
complexity classifier, the PRD's edge cases section (Section 11) must contain
edge cases from each applicable category.

### Applicability rules

Determine which categories apply by examining the feature scope:

**Interaction sequence** applies when the feature has two or more
user-triggered actions that could interact (e.g., filter + operation,
save + navigate, edit + delete).

**Cascading behaviour** applies when the feature creates or modifies an
entity that is referenced by other components, views, or stored procedures
identified in the codebase.

**Concurrency** applies when the feature modifies state that is shared
across users or processes (database records, configuration tables,
calculation results).

**State boundary** applies when the feature includes components that can
be in multiple states (populated/empty, enabled/disabled, running/idle).

**Cross-component dependency** applies when the feature has upstream
data sources or downstream consumers identified in the prd-interviewer's
codebase reconnaissance.

**Data integrity** applies when the feature creates or modifies persistent
data (database writes, configuration changes).

**Failure and recovery** applies when the feature involves operations
that can fail (stored procedure calls, API requests, data writes,
background calculations).

### Scoring

Count the applicable categories and the categories with at least one
documented edge case.

PASS: every applicable category has at least one edge case documented.

Deductions:
- Applicable category with no edge cases: -2 per category
- Tier 3+ feature with fewer than 3 applicable categories addressed: -5 (additional)

### Examples

PASSES D3 edge-case category check:
- A Tier 3 UI feature with documented edge cases in: interaction sequence
  (filter + save), cascading behaviour (entity rename propagation),
  concurrency (simultaneous edit), state boundary (empty grid, disabled
  buttons), cross-component dependency (downstream view refresh), failure
  and recovery (save failure, retry). Six of seven categories addressed.

FAILS D3 edge-case category check:
- A Tier 3 UI feature with three edge cases documented, all in the
  "state boundary" category. Five applicable categories have zero
  edge cases. Deduction: -10 (5 categories × -2) + -5 (Tier 3+ with
  fewer than 3 categories) = -15, which exhausts D3.

---

## D1 -- Message text sourcing (applies to all features)

All user-facing message text in the PRD must either:
(a) be quoted verbatim from the codebase with a source file reference
    in the format `[Source: path/to/file.ext:lineN]`, or
(b) be marked as `[Proposed — approved by PM]`, `[PM-provided]`, or
    `[TEXT TBD — requires PM decision]`

Message text includes: toast/notification messages, error messages, tooltip
text, dialog titles and body text, validation messages, status labels.

PASSES:
- "When the save operation fails, the system displays 'Failed to save
  changes. Please try again.' [Source: cost-pools.service.ts:142]"
- "When the allocation completes, the system displays a success message.
  [TEXT TBD — requires PM decision]"
- "When the user saves a new rule, the system displays 'Rule saved
  successfully.' [Proposed — approved by PM]"

FAILS:
- "When the save operation fails, the system displays 'An error occurred
  while saving your data. Please check your input and try again.'"
  (No source reference and no TBD marker — this text may be fabricated.)

Deductions: -2 per instance of unsourced, un-marked message text.

