# Splitting Heuristics

Reference for `phase-splitter`. Contains the rules for generating candidate
phases, the independence scoring deduction table, and effort estimation
heuristics.

---

## Table of contents

1. [Splitting rules — in order of application](#splitting-rules)
2. [Independence scoring](#independence-scoring)
3. [Effort estimation](#effort-estimation)
4. [Special cases](#special-cases)

---

## Splitting rules {#splitting-rules}

Apply these in order. Earlier rules take priority.

---

### Rule 1 — Shared infrastructure goes first

If the feature requires any of the following that don't already exist,
they become Phase 1 (or Phase 0 if truly foundational):

- A new database table or schema change that multiple phases depend on
- A new stored procedure or view that multiple phases call
- A new shared UI component that multiple phases use
- A new API endpoint or service method that multiple phases consume
- A ProcessID reference table addition that multiple phases depend on

A shared infrastructure phase has no upstream dependencies (Tier 0)
and all phases that use the infrastructure become Tier 1 or higher.

Exception: if only one phase uses the infrastructure and no other phase
touches it, fold it into that phase rather than creating a separate one.

---

### Rule 2 — Split at layer boundaries

If the feature spans multiple architectural layers, each layer is a
candidate phase boundary:

- **Data layer:** Schema changes, stored procedure creation/modification,
  view creation/modification, reference data updates
- **API / backend layer:** Controller methods, service methods, data
  access methods, business logic not in stored procedures
- **UI layer:** Page components, feature components, routing, navigation

Split at layer boundaries when:
- The layer has more than ~3 hours of work on its own
- Different developers have different strengths in each layer
- The layer can be tested independently (e.g. stored procedure can be
  unit tested before UI exists)

Do not split at layer boundaries when:
- A component and its data fetching logic are tightly coupled and
  separation would create an untestable phase
- The total work in a layer is less than 2 hours (fold into adjacent layer)

---

### Rule 3 — Split at discrete user-facing capabilities

Each distinct user-facing capability within the feature is a candidate
phase. A capability is a complete unit of user value — something the user
can do end-to-end that they couldn't do before.

Examples of capabilities that warrant their own phase:
- "User can configure a cost pool allocation rule"
- "User can view allocation results filtered by department"
- "User can export the allocation rule configuration"
- "User can publish a rule to make it active"

A capability phase should include all layers needed to deliver that
capability — UI, backend, and data — unless Rule 1 has already separated
shared infrastructure.

---

### Rule 4 — Split at complex component boundaries

If a single capability requires building a complex new UI component
(estimated >3 hours for the component alone), that component becomes
its own phase:

- Multi-column sortable data table with custom cell rendering
- Complex form with conditional validation logic across multiple fields
- Interactive chart or visualisation component
- Modal with multi-step flow

Simpler components (buttons, basic dropdowns, read-only fields) do not
warrant their own phase — fold them into the capability phase they serve.

---

### Rule 5 — File ownership must be exclusive

After generating candidate phases, check every file in the codebase
inventory against the phase scopes. No file should appear in more than
one phase's scope.

If a file appears in two phases:
- Determine which phase is the primary owner (the phase that makes
  the more significant change)
- The other phase reads from but does not write to that file
- If both phases make significant changes: this is a dependency —
  the phase with the foundational change goes first (higher tier)

If a shared component file needs changes from two phases:
- Create a Phase 0 for the shared component change
- Both original phases become Tier 1 and read the updated component

---

### Rule 6 — Size boundaries

After applying Rules 1–5, check estimated effort (see Effort estimation
below). Apply size corrections:

**Too small (< 2 hours):**
Merge with an adjacent phase if:
- Merging does not create a file ownership conflict
- Merging does not push the combined phase above 6 hours
- The phases are in the same tier

If no safe merge exists, keep the small phase as-is. A 1.5-hour phase
is not a problem — it simply completes faster and unblocks downstream
phases sooner.

**Too large (> 6 hours):**
Look for a clean split boundary within the phase:
- A sub-capability that could be independently tested
- A component that could be extracted
- A layer that could be separated (if test independence allows)

If no clean boundary exists, keep the phase as-is and note the risk in
the breakdown document. A 7-hour phase is not ideal but is preferable
to an artificial split that creates dependency problems.

---

## Independence scoring {#independence-scoring}

Score starts at 100 per phase. Apply deductions for each dependency.
A phase scoring below 60 is flagged for team review.

| Dependency type | Condition | Deduction |
|---|---|---|
| File dependency | This phase writes to a file another phase also writes to (should have been caught by Rule 5, but flag if found) | −25 |
| Hard data dependency | This phase calls a stored procedure, reads a table, or uses a schema element that another phase creates | −20 |
| Interface dependency | This phase calls a function, method, or API endpoint that another phase builds | −15 |
| Shared component read | This phase uses (but does not modify) a component that another phase is building | −10 |
| Test dependency | This phase's automated tests require output or state produced by another phase to run | −15 |
| Soft data dependency | This phase uses reference data (e.g. ProcessID categories) that another phase adds — but the phase can run with existing data in a test environment | −5 |

**Score interpretation:**
- 90–100: Highly independent — can start immediately in parallel
- 70–89: Minor dependencies — manageable with clear interface contracts
- 50–69: Significant dependencies — flag for team review; consider re-split
- Below 50: High dependency — this phase should not be parallelised;
  run sequentially after its upstream phases complete

**Note on interface contracts:**
Any phase with a score below 90 due to an interface or data dependency
must have an explicit interface contract in the phase breakdown document.
The contract states exactly what the upstream phase will produce (field
names, return types, error codes) so the downstream phase can build
against a known specification even before the upstream phase completes.

---

## Effort estimation {#effort-estimation}

Effort is agent execution time, not calendar time. Estimates account for
the full S1–S8 build phase cycle for a single developer/agent lane.

### Base estimates by work type

| Work type | Base estimate |
|---|---|
| Simple UI component (button, label, read-only field) | 0.5–1 hour |
| Standard UI component (dropdown, form field with validation) | 1–2 hours |
| Complex UI component (table, modal, multi-field form) | 2–4 hours |
| Simple stored procedure (single table, straightforward logic) | 1–2 hours |
| Moderate stored procedure (joins, conditional logic, error handling) | 2–3 hours |
| Complex stored procedure (multi-table, recursive, or financial calculation) | 3–5 hours |
| View creation or modification | 1–2 hours |
| Schema change / migration | 1–2 hours |
| ProcessID reference table update | 0.5–1 hour |
| API endpoint (simple CRUD) | 1–2 hours |
| API endpoint (with business logic) | 2–3 hours |
| Navigation / routing change | 0.5–1 hour |

### Adjustment factors

Apply these to the base estimate:

| Factor | Condition | Adjustment |
|---|---|---|
| Existing pattern | Work closely follows an existing, well-tested pattern in the codebase | −20% |
| Novel pattern | Work requires a new pattern with no existing reference | +30% |
| Complex data binding | Component reads from multiple sources or has derived calculations | +25% |
| Role-conditional behaviour | Component has different states/options by user role | +20% |
| Cross-phase interface contract | Phase must produce an output consumed by another phase | +15% |
| Profitability calculation | Phase involves FTP, capital, or yield calculations | +30% |
| Shared component modification | Modifying a component used in multiple places in the codebase | +25% |

### Total feature estimate

Sum low estimates across all phases → total low
Sum high estimates across all phases → total high

Calendar time estimate for parallel execution:
- Identify the critical path (longest chain of sequential phases)
- Calendar time ≈ sum of effort estimates along the critical path
- Note: assumes one developer per phase running in parallel

---

## Special cases {#special-cases}

### Feature with no UI surface (stored procedure / background process only)

Skip Rules 3 and 4. Apply Rules 1, 2, 5, and 6 only.
Phase boundaries are: schema changes → stored procedure(s) → calling
layer / integration point.
Minimum phase count: 1 (if the entire change is contained in one SP
with no schema dependency).

### Feature that modifies only existing components (no new components)

Skip Rule 4. Apply all other rules.
Each modified component is a candidate phase only if the modification
is >2 hours. Minor modifications to existing components should be
folded into the capability phase they serve.

### Feature with a single affected page and few components

If the feature has only one affected page and fewer than 3 components,
a single-phase breakdown (Pair or Solo mode) may be more appropriate
than a multi-phase Sprint breakdown. Flag this for the team:

> "This feature has limited natural phase boundaries. A single-phase
> Pair or Solo work stream may be more appropriate than Sprint.
> Recommend reconsidering mode assignment."

Present the single-phase option alongside a two-phase option if one
exists, and let the team decide.

### Feature that touches the Pyramid Analytics data model

Pyramid model updates are out of scope for Profitability build phases
per the standard out-of-scope boundary. If the PRD includes Pyramid
model changes:
- Flag this immediately: "PRD includes Pyramid model changes — this
  requires coordination with Sriyanka and is a separate work stream.
  These items should not be in the phase breakdown."
- Remove Pyramid-related scope from all candidate phases
- Note the separate work stream requirement in the breakdown document

### Adjusted_GL field additions or ProcessID changes

These are data layer changes with broad downstream impact. They must
always be Phase 1 (Tier 0) regardless of feature structure. All phases
that depend on the new field or ProcessID category become Tier 1 minimum.
