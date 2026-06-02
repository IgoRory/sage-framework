---
name: prd-completeness-check
description: >
  Scores a PRD for machine-readability and sprint-session readiness across
  nine dimensions: requirement coverage, edge/empty/error state coverage,
  demo completeness, UI component specification, out-of-scope clarity,
  traceability completeness, sample-data coverage, ambiguity-scan-clean,
  and Component Pattern Confirmation completeness. Produces a
  dimension-by-dimension remediation report and sets the Linear feature
  issue status to Ready when the score meets threshold. Use this skill
  whenever a PRD needs to be assessed for planning-cycle eligibility. Do
  not proceed to planning-cycle assignment without running this skill
  first. Acceptance criteria are NOT scored here -- ACs live in the
  sibling `acceptance-criteria.md` and are generated downstream during
  the TDD spec phase.
---

# PRD Completeness Check

Assesses a PRD bundle for readiness to enter the planning cycle. A PRD must
score >= 80/100 across nine dimensions before its Linear feature issue can
be set to Ready. Below threshold, the skill produces a remediation report
detailing exactly what must be fixed before re-assessment.

Critical distinction this skill enforces: a mockup or demo shows what a UI
looks like. A component specification defines what it does, what states it
can be in, and how users interact with it. These are separate artifacts
with separate requirements. A passing demo check does not substitute for a
passing component specification check.

**Post-Phase-D scope.** Acceptance criteria are explicitly NOT scored by
this skill. ACs live in the sibling `acceptance-criteria.md` artifact and
are generated downstream during the TDD spec phase from PRD + component
specification. Whatever consumes ACs (dev-interview, traceability-reviewer,
TDD spec generator) is responsible for scoring AC quality.

**Demo screenshots are deferred.** Phase C of the PRD Pipeline
Production-Grade Lift converted demo generation to the three-surface
manual handoff and did not wire screenshot generation. Until screenshot
generation is restored, this skill does NOT score screenshot coverage.
The pre-Phase-D `D4 — Mockup file completeness` dimension is retained as
`D3 — Demo bundle completeness` and now scores the demo HTML, behaviour
manifest, and coverage report instead of mockup PNG paths.

---

## L1–L12 contract alignment (binding)

This skill consumes prd-interviewer bundles produced against the locked
L1–L12 architectural model. The contract that ties this skill to the
interviewer outputs is recorded in
[`prd-interviewer/references/downstream-agent-contract.md`](../prd-interviewer/references/downstream-agent-contract.md).
The binding alignment points are:

- **Bundle discovery via `bundle-manifest.json`.** The list of files in
  the sub-PRD bundle is taken from
  `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` (finalised
  by the interviewer at end of P9). Heuristic disk discovery is forbidden
  — if a derivative named in this skill's Inputs table is not present in
  the manifest, record the absence under the corresponding dimension and
  continue. If `bundle-manifest.json` itself is absent, fall back to the
  legacy disk-walk for the duration of the backfill-on-touch window.
- **9 scoring dimensions against the 8-section schema + 14 §4 sub-sections.**
  D1 requirement coverage and D6 traceability score against the §4
  sub-section IDs (`DM` / `CL` / `AL` / `WF` / `UI` / `VC` / `ER` / `NM`
  / `PA` / `IN` / `PF` / `AU` / `RX` / `CP` — 14 prefixes per the locked
  L4 schema). Every §4 sub-section in the PRD's coverage map must either
  carry at least one `{PREFIX}-NNN` entry OR an explicit `Not applicable
  — [reason]` notice; silent omissions are a D1 finding.
- **Anchor Attestation completeness is its own scored dimension.** D9
  consumes the `## YAML reads` H2 table in every handoff `_summary.md`
  and scores its completeness — every cited YAML in each brief's Section
  3 must appear in the corresponding summary's `## YAML reads` table
  with verbatim `anchors_extracted` values matching the YAML. D9 also
  continues to cover Component Pattern Confirmation Report completeness;
  for new-format bundles the two checks live in the same dimension.
  Anchor mismatches detected during scoring are recorded as a D9 finding
  with the YAML path and the expected vs. extracted values.
- **Dual-layout AC support (backfill-on-touch window).** AC IDs may
  appear in either the new sequential `AC-NNN` form (with the `surface`
  field on each AC carrying `UI` / `calc` / `data` / `error`) or the
  legacy bucketed `AC-{REQ|EC|UI|ERR}-NNN` form. Both are accepted by
  this skill until the last pre-lift sub-PRD has been touched once.
  Dual-layout reads do not affect scoring — they only adjust the regex
  used to enumerate AC IDs for the traceability cross-check (D6) and the
  AC sibling existence check (D6 cascade).

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| PRD content | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md` (or `.sage/prds/[FEATURE_ID]/prd.md` for legacy non-sub-PRD layout) | Yes |
| Component specification | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md` | Yes (UI features) |
| Traceability artifact | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/traceability.md` | Yes |
| Sample-data files | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/*.json` | Yes (data-bearing features) |
| Demo bundle | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-interactive.html`, `demos/demo-behavior-manifest.md`, `demos/demo-coverage.md` | Yes (UI features) |
| Component Pattern Confirmation Report | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-pattern-confirmation.md` | Yes (any feature with matched Component Pattern Blocks) |
| Acceptance-criteria sibling (existence check only — not scored) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md` | Existence only |
| Bundle manifest (file inventory + producers + `prdHash` per file) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` | Yes (new-format bundles); legacy disk-walk fallback during backfill-on-touch |
| Handoff `_summary.md` files for Anchor Attestation scoring (D9) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/{demos,sample-data,component-spec}/_summary.md` | Yes (any bundle that produced the corresponding handoff surface) |

The legacy single-folder layout (`.sage/prds/[FEATURE_ID]/prd.md` etc.)
is accepted for in-flight PRDs predating the Phase B per-sub-PRD layout.
For new PRDs, the per-sub-PRD layout is mandatory.

---

## Nine scoring dimensions

| Dimension | Points | What it assesses |
|-----------|--------|-----------------|
| D1 - Requirement coverage | 15 | All requirements as explicit, testable predicates; plain-English-only rule honoured |
| D2 - Edge/empty/error state coverage | 12 | Non-happy-path states for every functional area |
| D3 - Demo bundle completeness | 10 | Demo HTML + behaviour manifest + coverage report all present and well-formed |
| D4 - UI component specification | 18 | Full spec for every new/affected component |
| D5 - Out-of-scope clarity | 10 | Explicit out-of-scope section preventing scope creep |
| D6 - Traceability completeness | 15 | Every PRD requirement maps to component-spec section + demo scenario + sample-data record (where applicable) |
| D7 - Sample-data coverage | 8 | Every PRD-named entity has at least one record; edge cases have sample records |
| D8 - Ambiguity-scan-clean | 7 | No unresolved ambiguity markers or vague-qualifier residue in the PRD |
| D9 - Component Pattern Confirmation completeness | 5 | Every Component Pattern Block decision recorded with PM confirmation status |
| Total | 100 | |

### Weight justification

- **D4 (UI component specification) — 18.** The component specification
  drives the developer build and the TDD spec generation. It is the
  single highest-leverage artifact in the bundle. Weight reduced from 25
  pre-Phase-D because ACs are no longer scored here and some scoring
  weight rebalances across the four new dimensions.
- **D1 (Requirement coverage) and D6 (Traceability) — 15 each.**
  Requirement coverage and traceability are the two gating dimensions for
  downstream consumption. A complete requirement set with no traceability
  is still unbuildable; a complete traceability with sparse requirements
  is still unscoped. The two are weighted equally because either failing
  invalidates the PRD bundle.
- **D2 (Edge/empty/error) — 12.** Edge-case coverage is a major
  remediation source historically; weight retained from the pre-Phase-D
  level rather than reduced, because Phase C made edge cases an explicit
  P7 driver state.
- **D3 (Demo completeness) and D5 (Out-of-scope clarity) — 10 each.**
  Demo completeness is informational verification; out-of-scope clarity
  prevents scope creep. Both are important but not gating in the way D1
  / D4 / D6 are.
- **D7 (Sample-data coverage) — 8.** Sample-data is the smallest of the
  three handoff surfaces and is mostly a coverage check. Weight kept
  modest.
- **D8 (Ambiguity-scan-clean) — 7.** Mostly binary — either the PRD has
  residual vague qualifiers or it does not. Modest weight reflects the
  low information content of the dimension.
- **D9 (Component Pattern Confirmation completeness) — 5.** The
  confirmation report is itself a bulk-confirm artifact; this dimension
  is the existence-and-completeness check for the report. Low weight
  reflects that the substantive content is scored under D4 (component
  spec) and D6 (traceability).

Total: 15 + 12 + 10 + 18 + 10 + 15 + 8 + 7 + 5 = 100.

Pass threshold: 80/100. Threshold is auto-calibrated over time by the
skill-effectiveness-evaluator -- do not hardcode 80 in any downstream
logic. Read the current threshold from `.sage/workflow-config.json` field
`prd.completenessThreshold` if available -- fall back to 80 if not set.

---

## Step 1 -- Read all inputs

Read the PRD from `.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md` (legacy
fallback `.sage/prds/[FEATURE_ID]/prd.md`).

Read the component specification, traceability artifact, sample-data
files, demo bundle, and Component Pattern Confirmation Report from the
paths in the Inputs table above.

Verify the sibling `acceptance-criteria.md` exists (existence check
only — not scored). If absent, record a finding under D6 (traceability)
because traceability assumes the AC sibling exists.

If a required artifact is absent, do not abort. Score the affected
dimension with the absence rule below, record a finding, and continue.

---

## Step 2 -- Score each dimension

### D1 -- Requirement coverage (15pts)

Read every requirement statement in the PRD body (Sections 1–9 per
`references/prd-section-schema.md`). For each:

PASS condition: the requirement is a testable predicate -- it specifies
a precise condition and a precise outcome with no vague qualifiers.

Deductions:
- Vague qualifier (responsive, appropriate, correctly, seamlessly,
  efficiently, properly, well): -2 per instance
- Unstated assumption (references something not defined in this PRD
  or any linked document): -3 per instance
- Missing requirement (screen or function visible in the demo bundle
  but absent from requirements): -5 per missing item
- Plain-English-only violation (SP name, return code, internal flag
  name, view name, class/selector name, AC text inline, reuse table
  inline, API endpoint path appearing in PRD body text per the
  Phase C `prd-template.md` rule): -3 per instance

Message text sourcing check:
- User-facing message text (toast, error, tooltip, dialog title/body,
  validation messages) that is not sourced from the codebase with a
  file reference and is not marked with one of:
  `[Proposed — approved by PM]`, `[PM-provided]`, or
  `[TEXT TBD — requires PM decision]`: -2 per instance

### D2 -- Edge/empty/error state coverage (12pts)

For every functional area in the PRD, verify that the following states
are specified where applicable:

- Empty state: what the UI or output looks like when there is no data
- Error state: what happens when an operation fails
- Loading/processing state: what is shown while data is being fetched
- Boundary condition: behaviour at input extremes (zero, null, max value)

For Profitability calculation features: also check that return codes
-1 through -8 are handled and that the behaviour for each is specified.

For features classified Tier 2 or above (see
`prd-interviewer/references/complexity-classifier.md`), check that the
edge cases section covers the applicable edge-case categories:

| Category | Applicable when |
|---|---|
| Interaction sequence | Feature has 2+ user-triggered actions |
| Cascading behaviour | Feature creates or modifies entities referenced by other components |
| Concurrency | Feature modifies shared state (records, configuration, calculations) |
| State boundary | Feature has components with multiple states |
| Cross-component dependency | Feature has upstream or downstream dependencies |
| Data integrity | Feature creates or modifies persistent data |
| Failure and recovery | Feature involves operations that can fail (SP calls, API requests, data writes) |

Deductions:
- Missing empty state for a data-displaying component: -3
- Missing error state for an operation that can fail: -3
- Missing return code handling for a calculation feature: -3 per
  unhandled return code range
- Applicable edge-case category with zero edge cases documented: -2
  per category (Tier 2+ features only)
- Feature classified Tier 3+ with fewer than 3 applicable categories
  addressed: -4

### D3 -- Demo bundle completeness (10pts)

Verify the three demo artifacts exist and are well-formed:

| Artifact | Required when | Check |
|---|---|---|
| `demos/demo-interactive.html` | UI feature | File exists; first 5 lines contain a `<!-- prdHash: <sha256> -->` comment per Phase C R5 |
| `demos/calculation-demo.html` | Calculation feature | File exists when the PRD describes a calculation engine surface |
| `demos/demo-behavior-manifest.md` | Demo present | File exists; contains the scenario list keyed by `AC-*` IDs |
| `demos/demo-coverage.md` | Demo present | File exists; lists every demoable AC ID with status (rendered / partial / skipped + reason) |
| `demos/_summary.md` | Manual handoff used | File exists; `prdHash` header present |

Deductions:
- Required artifact missing: -3 per missing artifact (cap deduction at
  the dimension max of 10)
- `prdHash` mismatch between demo HTML and current `prd.md` SHA-256: -2
  (advisory — the demo may be stale; recorded under both D3 and the
  Demo freshness advisory section below)
- Demo coverage report shows any AC ID as `skipped` without a recorded
  reason: -1 per skipped-without-reason entry

If the feature is explicitly flagged as non-UI / non-calculation (no
demo applicable), record D3 = 10/10 with the rationale "no demo
applicable".

**Demo screenshots are NOT scored here** (Phase C deferred screenshot
generation — see header note). If screenshot generation is restored in
a later phase, this dimension reincorporates screenshot coverage and
the weight may rebalance.

### D4 -- UI component specification (18pts)

Read the component specification file. For every new or affected UI
component on every affected page:

Each component must document all six elements:

1. Component name and type (e.g., "ProcessSelector -- multi-select dropdown")
2. Functional description in predicate form -- what it does, not what
   it looks like. FAIL example: "A blue dropdown that shows options."
   PASS example: "Filters the result set to the selected ProcessIDs.
   When no ProcessID is selected, all instruments are shown."
3. All states with transition triggers. Minimum requirements by type:
   - Dropdown/select: default, open, selected, disabled, error
   - Table/grid: populated, empty, loading, error
   - Button: default, hover, active, disabled, loading
   - Form field: default, focused, filled, error, disabled
   - Modal/panel: hidden, visible, loading, error
4. User interactions: every action the user can take and what it does
5. Selectable options: for any component with selectable values, list
   all options or the data source they are populated from
6. Data binding: which specific data fields populate this component.
   For Profitability components: name the Adjusted_GL field, ProcessID,
   or stored procedure (SP) explicitly by name -- generic references
   like "the calculation result" do not pass.

Scoring:
Each component is worth (18 / total component count) points, rounded.
For each component, score 0-6 elements present. Partial credit applies:
each missing element reduces that component's share proportionally.

Special cases:
- If no component specification file exists: D4 = 0/18 automatically.
  Record finding: "No component specification file at
  .sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md."
- If the file exists but contains no entries: D4 = 0/18.
- Reused components (not modified by this feature): skip D4 check.
  Only new or modified components are assessed.
- Components flagged in the spec as `reuse-as-is` per the Phase C
  `component-spec-template.md` are not assessed under D4 (their
  fidelity is the reused component's responsibility, not this PRD's).

### D5 -- Out-of-scope clarity (10pts)

Verify the PRD contains an explicit out-of-scope section (Section 5
per the schema) that:
- Lists at least one item that is explicitly out of scope
- Uses language precise enough that a build agent would not implement it
- Covers any adjacent functionality that might be confused with in-scope

Deductions:
- No out-of-scope section at all: -10 (full deduction)
- Out-of-scope section present but vague (e.g., "performance is out of
  scope"): -5
- Missing entry for an obvious adjacent feature visible in the demo
  but not covered by requirements: -3

### D6 -- Traceability completeness (15pts)

Read `traceability.md` per the structure in
`prd-interviewer/references/traceability-template.md`. The artifact
contains a forward-trace (PRD requirement → AC IDs → component-spec
section → demo scenario → sample-data record) and a reverse-trace
(surface → PRD requirement).

PASS condition: every PRD requirement (each numbered business rule in
§3, each trigger / unavailability condition in §2) maps to:

- at least one AC ID in `acceptance-criteria.md` (existence check —
  the AC IDs themselves are not scored), AND
- at least one component-spec section (skip when the requirement is
  not UI-bearing — calculation-only requirements are exempt), AND
- at least one demo scenario in `demos/demo-behavior-manifest.md`
  (skip when no demo is applicable), AND
- at least one sample-data record in `sample-data/*.json` (skip when
  the requirement is not data-bearing).

Reverse-trace PASS condition: every component-spec section, demo
scenario, and sample-data record traces back to at least one PRD
requirement.

Deductions:
- `traceability.md` absent: -15 (full deduction)
- `acceptance-criteria.md` absent (existence check failure that
  cascades into traceability invalidity): -8
- PRD requirement with no AC mapping: -2 per requirement
- PRD requirement with no component-spec mapping (UI-bearing only):
  -1 per requirement
- PRD requirement with no demo-scenario mapping (UI-bearing only,
  demo applicable): -1 per requirement
- PRD requirement with no sample-data mapping (data-bearing only):
  -1 per requirement
- Reverse-trace orphan (surface artifact with no PRD requirement):
  -2 per orphan

### D7 -- Sample-data coverage (8pts)

Verify `sample-data/*.json` exists for any feature that operates on
named entities (any feature whose PRD names a domain entity such as
"Account", "Product", "Transaction Type", "Allocation Rule").

PASS condition: every PRD-named entity has at least one record in
`sample-data/*.json`, AND every edge case enumerated in PRD §7 (or
the dedicated edge-cases section) that depends on data has at least
one corresponding sample-data record. The sample-data `_summary.md`
provides the record counts; spot-check the JSON when the summary's
claims look suspect.

Deductions:
- `sample-data/` directory absent for an entity-bearing feature: -8
  (full deduction)
- PRD-named entity with zero sample-data records: -2 per entity
- Edge case requiring sample data with no corresponding record: -1
  per missing edge-case sample
- Sample-data `_summary.md` missing: -1 (process compliance — the
  manual handoff contract requires the summary)

If the feature is explicitly non-data-bearing (no PRD-named
entities; calculation-only with no persistent state), record D7 =
8/8 with rationale "no sample data applicable".

### D8 -- Ambiguity-scan-clean (7pts)

Phase C added a pre-generation ambiguity scan that surfaces vague
qualifiers for PM clarification before the PRD is generated. The scan
output lands in §15 of the PRD per the schema. This dimension verifies
that the final PRD contains zero unresolved ambiguity markers and
zero vague-qualifier residue.

Scan markers to look for in the final PRD body (any section, not
just §15):

- `[AMBIGUITY: ...]`
- `[TBD]` or `[TEXT TBD — requires PM decision]` (the second form is
  acceptable for message text per D1; for anything else it is
  unresolved)
- `[TODO]`
- `[QUESTION: ...]`
- Vague qualifiers from the locked Phase C list: `appropriate`,
  `reasonable`, `as needed`, `etc.`, `as before`, `should generally`,
  `typically`, `where applicable`, `something like`, `or similar`,
  `quickly` / `slowly` without metric, `lots of` / `a few` /
  `several` without count, `responsive`, `intuitive`, `fast`,
  `seamless`, `properly`, `correctly`, `well`

PASS condition: §15 contains either "Scan clean — no vague
qualifiers found." or a fully-resolved list with every entry marked
`clarified` / `confirmed-acceptable` / `tracked-as-DI-NNN`, AND no
unresolved marker or vague qualifier appears anywhere else in the
PRD body.

Deductions:
- §15 absent: -3
- §15 present but contains an unresolved entry (no resolution
  marker): -2 per unresolved entry
- Unresolved ambiguity marker (`[AMBIGUITY:...]`, bare `[TBD]`,
  `[TODO]`, `[QUESTION:...]`) anywhere in PRD body outside §15: -1
  per marker
- Vague qualifier from the locked list appearing in the PRD body
  outside §15 without an accompanying clarification: -1 per
  qualifier (overlap with D1's `-2 per vague qualifier` is
  intentional — D1 penalises requirement-coverage damage, D8
  penalises ambiguity-scan-discipline damage; both apply)

### D9 -- Component Pattern Confirmation completeness (5pts)

Phase C F31 produces a Component Pattern Confirmation Report at
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-pattern-confirmation.md`
at the end of P5, before P8. The report lists every Component Pattern
Block decision the interviewer made during P5 with contextual
substitutions; the PM bulk-confirms by default and only DIFFs are
re-asked.

PASS condition: the file exists, AND every Component Pattern Block
decision in the report carries a PM confirmation status (one of
`bulk-confirmed`, `pm-confirmed-as-is`, `pm-overridden` with the
override captured, or `pm-deferred-to-DI-NNN`).

Deductions:
- File absent on a feature with matched Component Pattern Blocks:
  -5 (full deduction)
- File present but a decision entry lacks a confirmation status: -1
  per missing-status entry

If the feature has zero matched Component Pattern Blocks (a wholly
new feature with no application equivalents anywhere), the report
may be absent and D9 = 5/5 with rationale "no Component Pattern
Blocks to confirm".

---

## Step 3 -- Calculate total score

Sum all nine dimension scores. Apply the pass/fail threshold from
`.sage/workflow-config.json` field `prd.completenessThreshold` (default
80).

---

## Step 4 -- Update Linear, produce report, and emit telemetry

If score >= threshold:
  Update the Linear feature issue status to Ready via Linear MCP.

Write the assessment report to:
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/completeness-assessment.md`
(legacy fallback `.sage/prds/[FEATURE_ID]/completeness-assessment.md`).

Use this exact format:

``````
PRD COMPLETENESS ASSESSMENT
Feature: [Linear issue ID] -- [Feature title]
Sub-PRD: [sub-prd-id, if applicable]
Date: [ISO date]
Assessed by: prd-completeness-check

SCORE: [total]/100  [PASS / FAIL]
Threshold: [N]/100

DIMENSION SCORES
D1 Requirement coverage              [N]/15   [OK / N findings]
D2 Edge/empty/error states           [N]/12   [OK / N findings]
D3 Demo bundle completeness          [N]/10   [OK / N findings]
D4 UI component spec                 [N]/18   [OK / N findings]
D5 Out-of-scope clarity              [N]/10   [OK / N findings]
D6 Traceability completeness         [N]/15   [OK / N findings]
D7 Sample-data coverage              [N]/8    [OK / N findings]
D8 Ambiguity-scan-clean              [N]/7    [OK / N findings]
D9 Component Pattern Confirmation    [N]/5    [OK / N findings]

FINDINGS
[Dimension] -- [Finding description] -- [Points deducted] -- [Remediation]
...

DEMO BUNDLE CHECK
[Artifact]   [expected path]   [EXISTS / MISSING]
...

SAMPLE-DATA COVERAGE
[Entity]   [Record count]   [Edge-case records]
...

TRACEABILITY CHECK
[Requirement]   [AC IDs]   [Component-spec sections]   [Demo scenarios]   [Sample records]
...

COMPONENT SPECIFICATION COVERAGE
[Component]   [Elements present N/6]   [Missing elements]
...

[If PASS:]
Linear issue status updated to Ready.
This PRD is eligible for the next planning cycle.

[If FAIL:]
Linear issue status NOT updated.
Resolve all findings above and re-run prd-completeness-check.
[N] finding(s) require attention before this PRD can reach Ready.

[If re-assessment, append:]
Prior score: [N]/100 ([date of prior assessment])
Delta: [+N / -N] points
Resolved since last assessment: [list]
Still open: [list]
``````

**Every dimension that lost points must produce at least one actionable
remediation note in the FINDINGS section.** A dimension with N findings
must contribute N entries to FINDINGS; a dimension marked OK contributes
none. The remediation note names the file and section to fix.

---

## Demo freshness advisory (non-scoring)

After writing the assessment report, check for `prdHash` drift in the
demo bundle:

For each demo file that exists:
1. Read the `prdHash` comment from the HTML file header (first 5 lines)
2. Compute the SHA-256 of the current `prd.md`
3. If they differ: append an advisory to the assessment report:
   "ADVISORY: [filename] exists but was generated from a prior PRD
   version. Consider re-running the demo handoff per
   `prd-interviewer/references/handoff-prompt-templates.md` Template 1
   to regenerate."

If no demo files exist: no advisory (D3 already records the absence
inside the score). This advisory is informational and does not affect
the score or pass/fail status.

---

## Telemetry

Emit three telemetry events per assessment using `prd_telemetry_append.py`.
All events use `workflowKind: "completeness_check"`.

**At the start of Step 1** (before reading any inputs), emit:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"timestamp":"[ISO UTC]","event":"completeness_check_started","workflowKind":"completeness_check","linearIssueId":"[FEATURE_ID]","featureId":"[FEATURE_ID]","subPrdId":"[sub-prd-id or null]","prdRunId":"[prdRunId from prior interview telemetry, or generate a new UUID if not available]","prdPath":"[full path to prd.md]"}'
```

**At the end of Step 4** (after writing the assessment report and updating
Linear if applicable), emit two events:

1. `completeness_check_completed` (canonical run-completion event):

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"timestamp":"[ISO UTC]","event":"completeness_check_completed","workflowKind":"completeness_check","linearIssueId":"[FEATURE_ID]","featureId":"[FEATURE_ID]","subPrdId":"[sub-prd-id or null]","prdRunId":"[same prdRunId as started event]","score":[total],"passThreshold":[threshold],"passed":[true|false],"dimensionScores":{"D1":[N],"D2":[N],"D3":[N],"D4":[N],"D5":[N],"D6":[N],"D7":[N],"D8":[N],"D9":[N]},"findingCount":[N],"linearStatusSet":"[Ready|null]"}'
```

2. `prd_completeness_score` (structured event for the effectiveness
evaluator's "repeatedly below threshold" pattern — added Phase D scope
item 4d; see `references/telemetry-schema.md` §3):

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"timestamp":"[ISO UTC]","event":"prd_completeness_score","workflowKind":"completeness_check","prdRunId":"[same prdRunId]","featureId":"[FEATURE_ID]","subPrdId":"[sub-prd-id or null]","totalScore":[total],"dimensionBreakdown":{"D1":[N],"D2":[N],"D3":[N],"D4":[N],"D5":[N],"D6":[N],"D7":[N],"D8":[N],"D9":[N]},"passThreshold":[threshold],"passed":[true|false]}'
```

Events are appended to the PRD telemetry file configured in
`workflow-config.json` (default `.sage/prd-interview-telemetry.jsonl`).
Failures are silent and do not affect the assessment workflow.

The schema for every event is documented in
`prd-interviewer/references/telemetry-schema.md`. Schema drift between
this skill and the schema doc is a defect — both must be updated in
the same change.

---

## Reference files

- `references/scoring-rubric.md` — detailed sub-criteria and worked
  examples for each dimension, minimum state requirements by component
  type (D4), Profitability-specific data binding examples, how to
  handle reused components, non-UI features, absent screen inventories,
  and re-assessments. Note: this file predates Phase D and references
  the pre-Phase-D six-dimension scheme; consult this skill body for
  the post-Phase-D scoring rules, and consult the rubric only for
  Profitability-specific worked examples that remain valid (D1
  message-text sourcing, D4 component-spec patterns).
- `prd-interviewer/references/telemetry-schema.md` — authoritative
  schema for every telemetry event emitted by this skill.
- `prd-interviewer/references/prd-section-schema.md` — the PRD
  section numbering this skill scores against.
- `prd-interviewer/references/traceability-template.md` — the
  structure D6 scores.
- `prd-interviewer/references/complexity-classifier.md` — tier
  thresholds used by D2.
