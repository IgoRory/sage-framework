# Acceptance Criteria Template

Reference for prd-interviewer. Self-contained — no external skill references.

Use this template to produce `acceptance-criteria.md` for one sub-PRD.
The file is saved to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md` and is the
authoritative AC artifact consumed by `dev-interview`,
`traceability-reviewer`, `orchestrator` (TDD-spec generation), and
`prd-completeness-check`.

The AC file is a **sibling** of the PRD, not a section of it. The PRD
§4 entries are the canonical requirements; this file's AC entries each
link forward to one or more §4.NNN IDs via `linked_requirement_ids`.
This prevents the failure mode where ACs are scattered across PRD prose
and component-spec addenda, which defeats traceability and breaks
`dev-interview`'s read path.

---

## Hard rule — outcome-only

**ACs describe what the user observes, not what the system does internally.**

A production-grade AC is a testable predicate over observable state. The
Given clause names a starting observable state. The When clause names a
user action or external event. The Then clause names the next observable
state the user, the data, or a downstream consumer can verify. The
eXample clause carries verbatim numeric / textual examples grounded in
the cited YAML or PM-provided values.

Internal mechanisms — SP calls, return codes, flag mutations, internal
service invocations — are forbidden in AC text. Translate every such
concept into the observable outcome it produces.

See `production-grade-quality-bar.md` §2 for the AC bar.

---

## ID scheme — sequential `AC-NNN`, no buckets

**Format:** `AC-NNN` where `NNN` is a zero-padded 3-digit integer.

- **No buckets.** The legacy categorised format `AC-{REQ|EC|UI|ERR}-NNN`
  is **explicitly retired** (PM rejected). Category lives in the
  `surface` field on each AC entry, not in the ID.
- **One sequence per sub-PRD.** `AC-001`, `AC-002`, `AC-003`, … without
  per-category resets.
- **Assigned at write time. Immutable thereafter.** Edits to an AC's
  text do not change its ID. Removed ACs leave their ID in a "Removed
  AC IDs" section with `removed in [version]: [reason]` rather than
  freeing the ID for reuse — this preserves test-file and traceability
  references.

### Per-AC fields

Every AC entry carries:

- `id` — `AC-NNN`.
- `title` — one-line summary in business English.
- `linked_requirement_ids` — list of one or more §4 sub-section IDs
  (`{PREFIX}-NNN`) that this AC verifies. Every AC links to ≥1 §4.NNN;
  the bidirectional invariant requires every §4.NNN to link to ≥1 AC
  (validated at P8 derivation and by `traceability-reviewer`
  downstream).
- `given` / `when` / `then` / `example` — the GWTX clauses.
- `expected_result` — a one-sentence restatement of the observable
  outcome (used by `dev-interview` and test-author for assertion
  phrasing).
- `surface` — one of `UI`, `calc`, `data`, `error`. Surface determines
  which downstream artefact owns the demonstrable proof of the AC
  (UI → demo scenario; calc → calculation-demo step; data → sample-
  data record set; error → demo error scenario or error-state row).
- `demoable` — boolean. `true` when the AC has an observable outcome a
  demo scenario can render; `false` when the AC depends on a runtime
  condition no static demo can capture (e.g. multi-browser timing).
  `demoable: false` ACs are flagged in `traceability.md` Section 3.

---

## Legacy bucketed AC backfill-on-touch

Pre-lift sub-PRDs continue with the legacy `AC-{REQ|EC|UI|ERR}-NNN`
layout until next touched. On next touch (any PM amendment), the bundle
migrates fully: AC IDs are renumbered to sequential `AC-NNN`, the
`surface` field is added (derived from the old prefix: `REQ`→`UI` or
the surface implied by the §4 link; `EC`→inherit from linked §4; `UI`
→`UI`; `ERR`→`error`), and a one-time entry is appended to the AC file
section "Migrated from legacy bucketed IDs" mapping old → new IDs.
Downstream consumers carry dual-layout read logic until every active
sub-PRD has been touched once post-lift.

---

## Anti-pattern examples (forbidden in AC text)

| Anti-pattern | Why it fails | Correct rewrite |
|---|---|---|
| "Then the system calls `usp_SaveProductCosts`." | Internal mechanism — unobservable to user / QA. | "Then the row counters reset to clean and the toast `Success` / `Product Unit Costs saved successfully` appears." |
| "Then the `isAODDependent` flag is true." | Internal flag — unobservable. | "Then the page refreshes when the global As-Of Date changes." |
| "Then the modal opens." | Vague — which modal, which copy, which buttons? | "Then a modal with the title `Out of Date Records`, body [verbatim text], and three buttons `Cancel` / `Load Latest` / `Save Anyway` appears." |
| "Then save succeeds." | Outcome unobservable to QA without inspecting state. | "Then a green toast `Success` / `Product Unit Costs saved successfully` appears for 5 seconds and the grid returns to clean state." |
| "Then validation fires." | Vague — what does the user see? | "Then the cell renders with red text and a red border, the row background changes to light-red, the Save button disables, and the toast `Validation Error` / `Unit Cost must be a positive dollar value with up to 11 digits.` appears." |

---

## Template

The AC file begins with a YAML derivative frontmatter block (see
[`prd-section-schema.md`](./prd-section-schema.md) — "Frontmatter for
every other derivative"). The frontmatter is terminated by a `---`
delimiter. The body content begins immediately after.

````markdown
---
derivativeOf: prd.md
prdHash: [sha256-hex of prd.md body content at the moment this file was written]
writtenAt: [ISO 8601 UTC]
producer: interviewer
---

# Acceptance Criteria — [Feature Title] — [sub-prd-id]

**Parent PRD:** [link to `prd.md`]
**Date:** [DD-MMM-YYYY]
**Version:** [v1.0 | v1.1 | …]

---

## 1. Conventions

- Every AC carries `id`, `title`, `linked_requirement_ids`, `given`,
  `when`, `then`, `example`, `expected_result`, `surface`, `demoable`.
- Then / Expected Result text is **outcome-only** — never implementation.
- Verbatim user-facing strings (toast copy, dialog body, validation
  messages, button labels) are quoted exactly. Sources are noted with
  one of: `[Source: path/to/file:lineN]`, `[Proposed — approved by PM]`,
  `[PM-provided]`, or `[TEXT TBD — requires PM decision]`.
- Each AC is independent — it does not depend on the order of other ACs
  unless the Given clause names the prior state explicitly.

---

## 2. Acceptance criteria

### AC-001

- **Title:** Side navigation shows Unit Costing parent under Expense Allocations
- **linked_requirement_ids:** UI-001, PA-002
- **surface:** UI
- **demoable:** true
- **Given:** the user is signed in as a Profitability Admin AND the side
  navigation is rendered
- **When:** the Expense Allocations group is expanded
- **Then:** a `Unit Costing` parent entry is the last entry inside the
  Expense Allocations group AND it has two children
  `Product Unit Costs` and `Transaction Unit Costs` AND each child shows
  the `AOD` badge
- **eXample:** With the Admin role, expanding Expense Allocations shows
  `Unit Costing` as the fifth entry; clicking it expands to show two
  children, each with the `AOD` badge.
- **Expected Result:** Side navigation entry layout matches the above.
  Clicking the `Unit Costing` parent toggles its expand/collapse only —
  no navigation occurs.
- **Notes:** [optional — link to demo `scenario_id`, sample-data record IDs]

---

### AC-002

- **Title:** Product page filtered-empty state with toggle on
- **linked_requirement_ids:** UI-005, WF-003
- **surface:** UI
- **demoable:** true
- **Given:** the Product read view is loaded AND every leaf row has its
  Unit Cost cleared to NULL
- **When:** the toolbar toggle `Hide leaves without Unit Costs` is turned ON
- **Then:** every NULL-cost leaf is hidden AND every non-leaf row whose
  visible descendants drop to zero collapses out AND the resulting empty
  tree displays the message `No products match the search criteria` AND
  the switch-view button stays enabled
- **eXample:** With 100 leaves all NULL, toggling the hide-empty switch
  collapses every row; the empty-state message renders verbatim.
- **Expected Result:** Filtered-empty message visible, switch-view
  button enabled.
- **Notes:** Demoed via `scenario_id: prod-filtered-empty`. See demo
  `_summary.md` for the documented seed inversion (see traceability §1).

---

### AC-003

- **Title:** Validation rejects invalid Unit Cost values
- **linked_requirement_ids:** VC-001, ER-002, UI-007
- **surface:** error
- **demoable:** true
- **Given:** the Product edit view is loaded AND the user is editing a
  leaf row's Unit Cost cell
- **When:** the user enters `0`, `abc`, or `1,000,000,000.00`
- **Then:** the cell renders with red text AND a red border AND the row
  background changes to light-red AND the Save button becomes disabled
  AND a toast appears with title `Validation Error` and body
  `Unit Cost must be a positive dollar value with up to 11 digits.`
  [Source: PRD §4.6 VC-001, brief Section 5.9]
- **eXample:** Entering `0` in a leaf cell shows red text + red border +
  light-red row background; Save disabled; toast matches verbatim.
- **Expected Result:** Visible cell + row styling per above; Save
  disabled; toast text matches verbatim.

---

### AC-004

- **Title:** Saving dirty edits commits and surfaces success toast
- **linked_requirement_ids:** WF-002, UI-008, NM-003
- **surface:** UI
- **demoable:** true
- **Given:** the Product edit view is loaded AND at least one leaf row
  has a dirty pending Unit Cost edit AND no cell is invalid
- **When:** the user clicks the `Save` button
- **Then:** a loader overlay with the message `Loading` appears briefly
  AND a green toast with title `Success` and body
  `Product Unit Costs saved successfully` appears for 5 seconds AND
  every previously-dirty row returns to clean styling
- **eXample:** Three dirty rows in the grid; clicking Save shows the
  loader for ~500ms; success toast renders verbatim; all three rows
  return to clean styling.
- **Expected Result:** Loader visible, success toast visible with
  verbatim copy, grid clean.

---

[Repeat for every AC, in sequential order AC-001, AC-002, …]

---

## 3. Removed AC IDs (preserve traceability)

| AC ID | Removed in version | Reason |
|---|---|---|
| AC-014 | v1.1 | Subsumed by AC-013 after PM clarified the guard fires identically across all navigation targets. |

[If none: `None — no ACs removed in this sub-PRD's history.`]

---

## 4. Migrated from legacy bucketed IDs (if applicable)

[Populated only when this sub-PRD was migrated from the legacy
`AC-{REQ|EC|UI|ERR}-NNN` scheme via backfill-on-touch.

| Legacy ID | New ID | surface |
|---|---|---|
| AC-REQ-001 | AC-001 | UI |
| AC-EC-001 | AC-002 | UI |
| AC-UI-001 | AC-003 | error |

If this sub-PRD was authored fresh against the new schema:
`Not applicable — this sub-PRD was authored against the sequential AC-NNN
scheme from inception.`]

---

## Appendix A — Self-review checklist (run before writing this file)

- [ ] Every AC has `id`, `title`, `linked_requirement_ids`, `given`,
  `when`, `then`, `example`, `expected_result`, `surface`, `demoable`.
- [ ] No AC's Then clause names an internal mechanism (SP, flag, return
  code, class name, internal service invocation).
- [ ] Every verbatim user-facing string carries one of the four sourcing
  markers (`[Source: …]`, `[Proposed — approved by PM]`, `[PM-provided]`,
  `[TEXT TBD — requires PM decision]`).
- [ ] No AC ID is reused. Removed ACs are recorded in Section 3.
- [ ] Every AC ID uses the sequential format `AC-NNN`. No legacy
  bucketed IDs appear outside Section 4 (Migrated from legacy bucketed
  IDs).
- [ ] Every AC links to ≥1 §4.NNN via `linked_requirement_ids`.
- [ ] Every §4.NNN in `prd.md` is linked from ≥1 AC (bidirectional
  invariant — validated at P8 derivation).
- [ ] No AC duplicates PRD prose verbatim — the AC describes the testable
  outcome; the PRD describes the requirement.
- [ ] `surface` is set per the four-value enum (`UI` / `calc` / `data` /
  `error`).
- [ ] `demoable: false` ACs carry a Note explaining why (referenced from
  `traceability.md` Section 3).

---

## Appendix B — Terminology / Glossary

[Per-sub-PRD glossary of business terms used in the AC clauses. Every
non-obvious term that appears in any AC's Given / When / Then / eXample
clauses is defined here, in business language.

Example:
- **AOD (As-Of Date)** — the effective date the Unit Cost applies on.
  Set globally via the page header date-picker; changes refresh the grid
  before any further edit is accepted.
- **Leaf row** — a row in the Product hierarchy grid with no descendants;
  only leaf rows carry a Unit Cost value.
- **Dirty row** — a leaf row whose Unit Cost has been edited in the
  current edit session but not yet saved.

If the sub-PRD has no domain-specific terminology: `Not applicable —
all AC clauses use widely-understood business language.`]
````

---

## Notes for the interviewer

- AC derivation is the **only AC-creation step** in the pipeline (the
  legacy P6 mid-interview AC-write was removed). ACs are derived at P8
  from the in-flow §4.NNN entries captured during P3 / P4 / P5 / P6.
- Bidirectional coverage rule: every §4.NNN ID produces ≥1 AC-NNN.
  Coverage check pre-write at P8.
- Pre-write artifact-bar walk (Family G G3) runs against
  `production-grade-quality-bar.md` §2 (AC bar) before the file is
  written. Failure: do not write. Surface failing Pass Condition.
  Resolve gap. Retry.
- `prdHash` derivative header is computed from the SHA-256 of `prd.md`
  body content at the moment this file is written.
