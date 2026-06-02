# Phase P8 — PRD draft + AC derivation + reuse map

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines
only the P8-specific scope: PRD draft generation against the locked
8-section schema, sequential `AC-NNN` derivation from §4.NNN entries
with the bidirectional coverage rule, the disk-first reuse-map
finalisation, the Component Pattern Confirmation Report consistency
check (the report itself was already authored at end of P5), and the
pre-write artifact-bar walk (L6 G3) per artifact.

**Phase ID:** `P8`
**Always asked. Runs after P7 APPROVE
([`phase-P7.md`](./phase-P7.md)) and before P9 handoff briefs
([`phase-P9.md`](./phase-P9.md)).**

P8 is **not** an interview phase. No new PM questions are asked.
Every artifact written here is derived from the in-memory interview
state captured across P1–P6, reconciled at the single conclusion
gate ([`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md)), and
locked at P7 in `interview-answers.json`. New PM input arrives only
via a REJECT / REDIRECT back to P7 or earlier.

---

## Scope

P8 produces four interviewer-authored artifacts (light, in-context):

1. **`prd.md`** — outcome-only business requirements against the
   locked 8-section schema (see
   [`../prd-section-schema.md`](../prd-section-schema.md)). Carries
   YAML frontmatter with `prdHash` SHA-256 of the body content.
2. **`acceptance-criteria.md`** — sibling AC artifact. Sequential
   `AC-NNN` IDs (no buckets). Every AC carries `linked_requirement_ids`
   (one or more §4.NNN), Given/When/Then/eXample (GWTX), `surface`
   (UI / calc / data / error), `demoable` flag. Bidirectional
   coverage rule enforced at this phase: every AC links to ≥1
   §4.NNN; every §4.NNN links to ≥1 AC.
3. **`reuse-map-draft.md`** — disk-first full reuse map. The full
   table lives on disk; the PM sees only a grouped plain-English
   summary in conversation. Consumed by the P9 component-spec
   handoff brief.
4. **Component Pattern Confirmation Report consistency check.** The
   report itself (`component-pattern-confirmation.md`) was already
   authored at the end of P5
   ([`phase-P5.md`](./phase-P5.md) §"Component Pattern Confirmation
   Report"). P8 verifies the report is present, well-formed, and
   consistent with the §4.5 / §4.4 / §4.14 entries captured in
   `interview-answers.json`. No re-authoring at this phase.

The Component Spec, demo HTML, demo manifest, and sample-data JSON
files are **not** authored at P8 — they are produced by the manual
handoff chats during P9. P8's outputs are the inputs to those
briefs.

---

## Step 1 — Load templates and schema

At P8 entry, the interviewer loads three reference files:

- [`../prd-section-schema.md`](../prd-section-schema.md) — locked
  8-section schema with the 14 §4 sub-section prefixes and the
  mandatory "Not applicable" rule.
- [`../prd-template.md`](../prd-template.md) — empty PRD scaffold
  matching the schema exactly.
- [`../acceptance-criteria-template.md`](../acceptance-criteria-template.md)
  — sibling AC scaffold with the `AC-NNN` sequential format,
  `linked_requirement_ids`, GWTX, `surface`, and `demoable`
  fields.

These are the only reference files P8 loads. No phase-module
cross-reads (per the L7 read-discipline rule).

---

## Step 2 — Generate the PRD draft

Generate `prd.md` against `prd-section-schema.md` 1..8 using
`prd-template.md` as the scaffold.

### 2a — Apply the 8-section schema verbatim

Every section heading is written in order — §1 Feature Definition,
§2 Success Criteria, §3 Scope, §4 Detailed Business Requirements
(with all 14 sub-sections), §5 Data Migration, §6 Risks &
Mitigations, §7 Open Items & Ambiguities, §8 Related Artefacts —
plus the Version History block per the schema's Version History
attribution rules.

### 2b — Populate §4 from in-flow IDs

Every §4.NNN ID assigned in-flow during P1–P6 is written under its
owning sub-section, in the order it was captured. The 14 sub-section
ID prefixes are:

| Sub-section | ID prefix |
|---|---|
| §4.1 Data Model & Entities | `DM-NNN` |
| §4.2 Calculation & Logic | `CL-NNN` |
| §4.3 Allocation & Distribution | `AL-NNN` |
| §4.4 Workflow & State | `WF-NNN` |
| §4.5 UI & Interaction | `UI-NNN` |
| §4.6 Validation & Constraints | `VC-NNN` |
| §4.7 Error Handling | `ER-NNN` |
| §4.8 Notifications & Messaging | `NM-NNN` |
| §4.9 Permissions & Access Control | `PA-NNN` |
| §4.10 Integration & External Surfaces | `IN-NNN` |
| §4.11 Performance & Scale | `PF-NNN` |
| §4.12 Audit & Telemetry | `AU-NNN` |
| §4.13 Reporting & Export | `RX-NNN` |
| §4.14 Cross-Page Impacts | `CP-NNN` |

### 2c — Mandatory "Not applicable" rule

Every §4 sub-section that was declared `Not applicable` on the
reconciled coverage map (snapshot at
`interview-answers.json.gate.reconciled_coverage_map`) is rendered
in `prd.md` with the explicit `Not applicable — [reason]` notice.
Silent omissions are forbidden by the L4 schema. Applies even to
backend-heavy sub-PRDs where §4.5 UI may be N/A.

### 2d — Outcome-only discipline (hard rule)

No internal mechanism prose appears in `prd.md`:

- No SP names, no return codes, no view column names, no class
  names, no internal flag names, no API endpoint paths.
- PM-directed SQL is admissible verbatim **only** when the PM
  explicitly authorised it during the interview (carry-over from
  L2).
- §4.14 Cross-Page Impacts is a relationship pointer register —
  CP-NNN entries reference canonical behaviour by `sub-prd-id +
  requirement-id`. **No behaviour duplication.**

### 2e — Version History attribution

The Version History block carries one entry for this initial draft:

- `date` in `DD-MMM-YYYY` (today's date).
- `author` is the agent's stable identifier (e.g. `prd-interviewer
  (composer-X)` per the project's naming convention) — never
  anonymous, never "various".
- `change summary` is the concrete delta: "initial PRD draft from
  interview run `<prdRunId>`".

PM edits made later carry the PM's full name in the same field;
PM edits and agent edits MUST be distinguishable from the author
field alone.

### 2f — YAML frontmatter and `prdHash` computation

Write the YAML frontmatter at the top of `prd.md`:

```yaml
---
title: <sub-PRD title from breakdown>
subPrdId: <sub-prd-id>
featureId: <PROF-NNN>
version: 1.0.0
author: <agent identifier>
date: <DD-MMM-YYYY>
prdHash: <sha256-hex of the body content below the closing --->
---
```

`prdHash` is the lowercase hexadecimal SHA-256 of the body content
**after** the closing `---` of the frontmatter. Apply byte-for-byte
consistency — no whitespace stripping, no line-ending
normalisation, no BOM removal. The `prd-stale-check` skill applies
the same rule when comparing.

On computation failure (L11 D5), write `prdHash:
'[COMPUTATION_FAILED]'` and emit `prd_pre_write_bar_walk_failed`
with the failing Pass Condition named verbatim. The write does
not proceed until the failure is resolved.

---

## Step 3 — Pre-write artifact-bar walk (L6 G3) for `prd.md`

Before writing `prd.md` to disk, run the L6 G3 pre-write
artifact-bar walk against the Pass Conditions in
[`../production-grade-quality-bar.md`](../production-grade-quality-bar.md)
for the PRD artifact. The walk is performed against the in-memory
PRD payload — the just-written file is not re-opened (a
`Read-after-Write` would be a literal-reading defect).

Pass Conditions verified:

- Every §1–§8 section heading is present.
- Every §4 sub-section in scope has at least one §4.NNN entry.
- Every §4 sub-section declared `Not applicable` carries the
  explicit `Not applicable — [reason]` notice.
- No internal mechanism prose (SP names / return codes / view
  columns / class names / flag names) appears in body text.
- Every user-facing message text instance carries a Family F tier
  marker (Tier 1 verbatim YAML / Tier 2 PM-approved phrasing /
  Tier 3 interviewer-drafted PM-approved-before-write).
- Every CP-NNN entry is a relationship pointer (no behaviour
  duplication).
- The Version History block carries an attributable author and a
  concrete delta description.
- The YAML frontmatter is well-formed and `prdHash` is computed.

If any Pass Condition fails, the interviewer does NOT write the
file. The failing condition is surfaced to the PM verbatim; the
underlying gap is resolved (either by PM input or by interviewer
correction); the walk is re-run. Failure emits
`prd_pre_write_bar_walk_failed` with `artifact: prd` and the
failing Pass Condition named.

On all Pass Conditions met, write `prd.md` to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md`.

---

## Step 4 — Derive sequential AC-NNN into the sibling artifact

Generate the sibling AC artifact at
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md` per
[`../acceptance-criteria-template.md`](../acceptance-criteria-template.md).

### 4a — AC IDs are sequential

Every AC carries an ID of the form `AC-NNN` (zero-padded
3-digit). **No buckets.** The legacy bucketed scheme
`AC-{REQ|EC|UI|ERR}-NNN` is explicitly retired by the L4 lock.
Category lives in the `surface` field:

- `UI` — observable on a screen / component / interaction.
- `calc` — observable as a numeric or business-rule output of
  a calculation.
- `data` — observable as state of stored entities, audit rows,
  or migration outcomes.
- `error` — observable as an error path, recovery flow, or
  failure mode (including concurrency, validation breach,
  cross-page consistency violation).

The `surface` field is the filter consumers use to group ACs by
test type (downstream `dev-interview` / `orchestrator TDD-spec gen`
contract — see
[`../downstream-agent-contract.md`](../downstream-agent-contract.md)).

### 4b — Bidirectional coverage rule

The bidirectional invariant is enforced at this phase:

- **Forward.** Every §4.NNN ID in `prd.md` § 4 maps to at least
  one AC-NNN via the AC's `linked_requirement_ids` field.
- **Reverse.** Every AC-NNN's `linked_requirement_ids` references
  at least one §4.NNN ID that exists in `prd.md` § 4.

The interviewer walks both directions in memory before writing
the AC file. Any §4.NNN with no AC mapping triggers AC derivation
for that requirement before the file is written. Any AC with a
broken / missing `linked_requirement_ids` triggers a fix in the
in-memory AC list before the file is written.

### 4c — GWTX clauses and `demoable` flag

Every AC carries Given / When / Then / eXample (GWTX) clauses:

- **Given.** Precondition state, named in business language.
- **When.** Triggering action or event.
- **Then.** Observable outcome — a specific value, message,
  state transition, or stored row, not "correct result".
- **eXample.** A worked example with concrete values (numbers,
  copy strings verbatim, role names, entity IDs). Examples
  source from interview answers; the interviewer does not
  invent numbers.

The `demoable` flag is `true` when the AC's observable outcome
can be rendered in the demo handoff artifact (Section 4 of the
demo brief at P9), and `false` otherwise. Backend-only ACs
(audit-log rows, scheduled-job outcomes, integration payloads)
typically carry `demoable: false`.

### 4d — Appendix B (terminology / glossary)

The terminology and glossary block lives in `acceptance-criteria.md`
Appendix B, **not** in `prd.md`. PM-coined terms or business
synonyms used across the §4.NNN entries are captured here for
downstream consumers (orchestrator TDD-spec gen, dev-interview).

### 4e — Pre-write artifact-bar walk (L6 G3) for `acceptance-criteria.md`

Before writing the AC file, run the L6 G3 walk against the
quality bar's AC Pass Conditions:

- Sequential `AC-NNN` IDs only — no bucketed legacy IDs.
- Every AC has GWTX clauses populated.
- Every AC has at least one valid `linked_requirement_ids`
  entry referencing a §4.NNN ID that exists in `prd.md`.
- Bidirectional coverage holds — every §4.NNN ID is referenced
  by at least one AC.
- Every AC has a `surface` field with one of the four allowed
  values (`UI` / `calc` / `data` / `error`).
- Every AC has a `demoable` boolean flag.
- Appendix B terminology block is populated or marked `Not
  applicable — [reason]`.
- The sibling-derivative YAML frontmatter is present with
  `derivativeOf: prd.md`, `prdHash` (matching the body-content
  hash of `prd.md` at this moment), `writtenAt` (ISO 8601 UTC),
  and `producer: interviewer`.

Failure emits `prd_pre_write_bar_walk_failed` with `artifact:
ac`. The write does not proceed until the failing condition is
resolved.

On all Pass Conditions met, write `acceptance-criteria.md` to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md`.

Emit `acceptance_criteria_generated` with payload
`{ subPrdId, prdRunId, acTotal, acByDemoable: { true, false },
acBySurface: { UI, calc, data, error } }`.

---

## Step 5 — Finalise the disk-first reuse map

Write the full reuse map to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/reuse-map-draft.md` per the
T6 disk-first pattern. The full table — one row per matched
component / new component, with `reuse-decision`, `pattern`,
`diffs`, `cited-YAML` — lives on disk; the interviewer chat
shows the PM only a grouped plain-English summary.

The source for the table is the in-memory matched-component list
populated during P5's Component Pattern Block work, plus any
component additions captured at the conclusion gate's
new-concept handling (`gate.post_gate_amendments`).

### 5a — Pre-write artifact-bar walk (L6 G3) for `reuse-map-draft.md`

Before writing, run the L6 G3 walk against the quality bar's
reuse-map Pass Conditions:

- One row per matched / new component — no missing rows.
- Every row has a `reuse-decision` value (`retained` / `amended`
  / `new` / `override`).
- Every amended / override row has a stated `diffs` rationale.
- Every matched row cites the canonical YAML by path.
- New components carry the candidate-for-YAML flag.
- The sibling-derivative YAML frontmatter is present.

Failure emits `prd_pre_write_bar_walk_failed` with `artifact:
reuse-map`. The write does not proceed until the failing
condition is resolved.

On all Pass Conditions met, write the file. Show the PM the
grouped plain-English summary (by component family) in
conversation; never present the full table verbatim in chat.

Emit `reuse_map_confirmed` with payload `{ subPrdId, prdRunId,
rowCount, groupedSummaryShown: true }`.

---

## Step 6 — Component Pattern Confirmation Report consistency check

The Confirmation Report (`component-pattern-confirmation.md`) was
authored at the end of P5 (see
[`phase-P5.md`](./phase-P5.md) §"Component Pattern Confirmation
Report"). P8 verifies the report is present, well-formed, and
consistent with the in-memory state of §4.5, §4.4, and §4.14
entries.

The check is performed against the in-memory matched-component
state — the report file is not re-opened (no `Read-after-Write`).
The in-memory state held since P5 closure is the source.

Verifies:

- Every matched component referenced in §4.5 UI entries appears
  in the report's "Matched components" section.
- Every WF-NNN transition cited in the report aligns with the
  in-memory state-model inventory from P5.
- Every CP-NNN cross-page impact cited in the report aligns with
  the §4.14 entries in `prd.md`.
- Every "Carry-over to P9 briefs" pointer in the report names a
  matched component whose anchors are present in the in-memory
  Family N anchor structures captured at P5 closure.

If any inconsistency is detected, the interviewer surfaces it to
the PM as a P8 finding. The PM decides:

- (a) The Confirmation Report is correct; the in-memory state was
  drifted by post-P5 amendments — update the in-memory state and
  proceed.
- (b) The in-memory state is correct; the Confirmation Report
  needs an amendment — REJECT to P5 to re-author the affected
  report sections.
- (c) Accept the inconsistency as a DI entry in PRD §7 with a
  documented reason.

No `prd_pre_write_bar_walk_failed` event is emitted here — the
file was already validated at P5. Drift detection at P8 emits
`prd_breakdown_gap_detected` with `gapType:
pattern-confirmation-drift` and `recordedAs: DI-NNN` when the
PM picks option (c).

---

## Step 7 — PM walkthrough of the four artifacts

After Steps 2–6 pass cleanly, the interviewer walks the PM
through the four artifacts in conversation:

1. **`prd.md`** — opens to §1 and §4 sub-section coverage; PM
   confirms outcome-only language and the §4 coverage map matches
   the reconciled snapshot from the gate.
2. **`acceptance-criteria.md`** — opens to the AC index; PM
   confirms the AC count by `surface` matches expectations and
   the bidirectional coverage rule was applied.
3. **`reuse-map-draft.md`** — grouped plain-English summary only;
   PM confirms the matched / new / amended classification by
   component family.
4. **`component-pattern-confirmation.md`** — pointer reference
   only; PM confirms the consistency check outcome (clean drift /
   amendment / DI accepted).

PM may accept all four artifacts as-is, or REJECT one or more.
REJECT triggers the corresponding restart:

- PRD body REJECT → re-walk Step 2 with the PM input applied.
- AC derivation REJECT → re-walk Step 4 with the in-memory §4
  state amended as required.
- Reuse map REJECT → re-walk Step 5 with the matched-component
  list amended (typically requires a return to P5 if structural
  changes are needed).
- Confirmation Report REJECT → REJECT to P5 to re-author the
  report.

REJECT here does not require re-running the single conclusion
gate, because no new §4.NNN content is introduced — only
artifact-side amendments. Coordinator routes back to the affected
Step within P8 and re-runs the L6 G3 walk for the affected
artifact.

---

## Telemetry

P8-scoped emit sites only:

- `prd_phase_started` — `phaseId: P8` at Step 1 entry.
- `prd_phase_completed` — `phaseId: P8` after Step 7 PM walkthrough
  passes.
- `acceptance_criteria_generated` — emitted at Step 4e on successful
  write.
- `reuse_map_confirmed` — emitted at Step 5a on successful write.
- `prd_pre_write_bar_walk_failed` — emitted whenever the L6 G3
  walk fails for `prd.md`, `acceptance-criteria.md`, or
  `reuse-map-draft.md`. The file is NOT written until the failing
  Pass Condition is resolved.
- `prd_breakdown_gap_detected` — emitted at Step 6 when the
  Confirmation Report consistency check surfaces a drift accepted
  as a DI entry.
- `prd_self_review_gate_failed` — emitted if any in-memory
  artifact walk surfaces a failed checklist item before the L6 G3
  pre-write walk runs.

Payload shapes for every event live in
[`../telemetry-schema.md`](../telemetry-schema.md) §2.

---

## Cross-cutting protocols invoked (pointer only)

P8 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family B — Verbatim recording.** PM edits during the Step 7
  walkthrough are recorded verbatim into `interview-answers.json`
  under `p8.walkthrough_amendments` before any artifact is
  re-walked.
- **Family E — No mid-interview recon.** No YAML re-reads at P8.
  The matched-component list held in memory from P5 is the
  source; reuse-map rows source from that list, not from disk.
- **Family F — Three-tier message text sourcing.** Every
  user-facing string written into `prd.md` carries a Family F tier
  marker.
- **Family G — Self-review gates.** G3 pre-write artifact-bar
  walks run for `prd.md`, `acceptance-criteria.md`, and
  `reuse-map-draft.md`. G2 coverage-dimension blocking applies
  to the bidirectional AC ↔ §4 coverage rule (Step 4b).
- **Family J — Anti-hallucination.** No invented §4.NNN entries,
  no invented AC clauses, no invented worked-example numbers.
  Every value sources from `interview-answers.json` or the
  reconciled coverage map.
- **Family K — Production-grade bar.** K1 — the bundle must pass
  `production-grade-quality-bar.md` before any final write. K2 —
  reduced-fidelity markers are emitted in PRD §8 Related
  Artefacts when any L5 override was applied at Step 0.

---

## Next phase

On Step 7 PM walkthrough pass + `prd_phase_completed` emitted →
[`phase-P9.md`](./phase-P9.md) (Handoff briefs + on-return
validation + auto-built `traceability.md` + `bundle-manifest.json`
finalisation).

On REJECT of any artifact, the affected Step re-runs within P8;
the L6 G3 walk for that artifact runs again before the next
attempt. Confirmation Report REJECT routes to P5 via the
coordinator; the single conclusion gate
([`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md)) does NOT
re-run unless P5 outputs are amended.
