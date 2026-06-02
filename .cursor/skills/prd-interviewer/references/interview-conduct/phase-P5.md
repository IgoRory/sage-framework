# Phase P5 — UI and UX (conditional)

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines only
the P5-specific scope, the full UI surface map, the performance-budget
absorption rule, the CP-NNN / WF-NNN in-flow assignment rules, the
seven cross-cutting sub-batches calibrated for UI, the three nested
UI-bound sub-drivers (permission-role, validation-dependency,
audit-trail), the Family N anchor extraction at P5 closure, the
Component Pattern Confirmation Report authored at P5 end, and the
P5 self-review.

**Phase ID:** `P5`
**Conditional — runs only when the P2 §4 coverage map declares §4.5 UI
in scope (the trigger predicate: "breakdown indicates UI change in
scope" OR PM amended the coverage map at P2 to include §4.5 UI).**
**Question catalogue:** [`../question-sets/section-5-ui-and-ux.md`](../question-sets/section-5-ui-and-ux.md)

---

## Trigger predicate (conditional)

The coordinator enters P5 only when, at P2 exit, the §4 coverage map
declared at least one of:

- **breakdown indicates UI** change in scope
  (`breakdown.investigation_context.affected_pages` non-empty AND any
  affected page surfaces a UI change, or Component Pattern Summaries
  carry UI components matched to the feature), OR
- PM amended the P2 coverage map to include §4.5 UI because the feature
  introduces a new UI affordance or modifies an existing one.

If neither condition holds, the coordinator skips P5 and routes to P6
(Edge cases — always runs). When P5 is skipped, §4.5 carries an
explicit `Not applicable — [reason]` notice in the PRD; no silent
omission. Note: §4.4 WF, §4.11 PF, and §4.14 CP may still be populated
by P3 / P4 / P6 even when §4.5 is N/A.

---

## Scope — full UI surface map

P5 is the heaviest phase in most interviews. It establishes the full
UI surface for the feature. Five inventories are captured, each
producing in-flow §4.NNN IDs:

1. **Screen inventory.** Every screen the feature touches (new screen
   or modified existing). For each: stated purpose, the navigation
   trigger that brings the user to it, and the classification
   (`new` / `modified`). Modified screens carry an explicit before /
   after delta.
2. **Component inventory.** Every component on every in-scope screen.
   For each, the six-element spec from
   [`../component-spec-template.md`](../component-spec-template.md) is
   captured: name/type, functional description, states + triggers,
   interactions, selectable options, data binding. Matched components
   from the breakdown's Component Pattern Summaries use the delta-style
   ask (only the deltas from the canonical Pattern Block are
   re-asked — Family E E1 prohibits mid-interview YAML recon).
3. **State models.** Every component state and every transition is
   captured. Each transition produces a `WF-NNN` entry (see below).
4. **Micro-detail (D-DETAIL).** For every UI surface: label text,
   tooltip text, placeholder text, validation message text, empty-
   state copy, hover behaviour, disabled-state reason text, sort /
   filter defaults, keyboard behaviour. Every piece of user-facing
   text follows the Family F three-tier message text sourcing protocol
   (Tier 1 verbatim YAML; Tier 2 PRD outcome PM-approved; Tier 3
   interviewer-drafted marked and PM-approved before write).
5. **Cross-page impact check (D-CROSS).** For every entity this
   feature displays or modifies, every page / dashboard / report /
   export / downstream calculation that consumes that entity is
   confirmed in scope or out of scope. Inbound and outbound impacts
   produce `CP-NNN` entries (see below).

---

## Performance budget absorbed at P5 (PF-NNN seeds)

The legacy P6 performance category is **dropped**; performance
questions for UI surfaces live here. For each in-scope UI surface, the
interviewer runs the predicate:

> "Is there a performance budget for this UI surface — page-load time,
> first-paint time, grid-render time for a representative row count, or
> a maximum-rows-rendered cap?"

On `yes`, each budget produces a `PF-NNN` entry with: target metric,
threshold value, measurement methodology (how the team will verify),
and the failure-mode behaviour if the budget is breached (degrade
gracefully / block the action / show warning toast / etc.). On `no`,
the surface is recorded with `PF: Not applicable — [reason]`.

Calculation and allocation performance budgets are captured at P3 / P4
respectively under the PF cross-cutting sub-batch; they do not double
here.

---

## In-flow ID assignment — WF-NNN and CP-NNN

- **Every state transition → a `WF-NNN` entry.** When the PM names a
  component transition (read → edit, draft → submitted, valid → dirty,
  etc.), the interviewer assigns a `WF-NNN` ID at the moment of
  capture with: from-state, to-state, trigger event, side-effects
  (saves / refreshes / cross-page propagation), and rollback / cancel
  behaviour.
- **Every cross-page impact → a `CP-NNN` entry.** The interviewer
  records, per impact:
  - `direction`: `inbound` (another sub-PRD or page changes something
    this feature consumes) OR `outbound` (this feature changes
    something another sub-PRD or page consumes).
  - `consumer-sub-PRD-or-page`: the named consumer (or producer for
    inbound).
  - `consumed-behaviour-reference`: pointer to the canonical behaviour
    entry in the originating sub-PRD by sub-PRD ID + requirement ID
    (e.g. `sub-prd-2:CL-014`). **No behaviour duplication** — §4.14
    is a relationship pointer register, not a behaviour duplicator.

Both ID prefixes seed the P2 coverage map (CP/WF were declared in
scope at P2). P5 reconciles the declared coverage by populating these
entries in-flow.

---

## P5 cross-cutting sub-batches (seven predicate triggers, UI-calibrated)

After the surface map and PF/CP/WF seeds, P5 runs the same seven
cross-cutting sub-batches as P3 / P4, calibrated for UI semantics.
Each sub-batch is a one-shot predicate; `yes` triggers structured
follow-ups, `no` records the sub-section as `Not applicable —
[reason]` for the in-scope UI surfaces.

1. **VC-NNN — Validation & Constraints.** Trigger:
   > "Are there field-level or form-level validation rules on this UI
   > beyond the standard required-field / type-format checks?"
   On `yes`: captures per rule the failed-value behaviour, the
   message text (Family F three-tier sourcing), and the recovery
   action.

2. **PA-NNN — Permissions & Access Control.** Trigger:
   > "Are there role-gated affordances on this surface — buttons,
   > columns, fields, or actions that some roles see and others don't?
   > Same as the P1 role baseline or different?"
   On `yes` (different): captures the role × affordance pair as a
   `PA-NNN` entry.

3. **NM-NNN — Notifications & Messaging.** Trigger:
   > "Does any user action on this surface trigger a notification —
   > toast, banner, modal, alert, badge, email, in-app message?"
   On `yes`: captures per-trigger the notification text, audience,
   channel, dismissal behaviour, and any escalation.

4. **AU-NNN — Audit & Telemetry.** Trigger:
   > "Does any user action on this surface produce an audit-log
   > entry or a telemetry event? Which fields (who, when, before /
   > after values, source page)?"
   On `yes`: captures the audit-log row shape and any telemetry
   event name.

5. **WF-NNN — Workflow & State (cross-page propagation).** Trigger:
   > "Does an action on this surface change state on another page or
   > entity beyond this screen? (cross-page state transition)"
   On `yes`: captures the cross-page state change as an additional
   `WF-NNN` entry beyond the in-page state transitions already
   captured in the state-model inventory.

6. **IN-NNN — Integration & External Surfaces.** Trigger:
   > "Does any action on this surface push data to or pull data from
   > an external system — Dataverse, downstream BI, regulatory feed,
   > consolidation engine, third-party API?"
   On `yes`: captures the consumer, payload shape, freshness
   contract, and failure mode.

7. **PF-NNN — Performance & Scale (surface budget).** This sub-batch
   is the umbrella for the performance-budget questions already
   absorbed into the surface map above; the interviewer confirms
   every in-scope surface has either a PF-NNN entry or a
   `PF: Not applicable — [reason]` notice.

Every `yes` produces a §4 sub-section entry under its prefix. Every
`no` reinforces the §4 sub-section's `Not applicable` notice for
this surface.

---

## Nested UI-bound sub-drivers (preserved per L8 sub-driver rule)

The L8 lock preserves three nested sub-drivers **inside** P5. These
are not promoted to coordinator-level phases; they run as nested
sub-driver states within P5 and exit before P5 exits. They are
triggered by the corresponding cross-cutting sub-batch returning `yes`
with enough complexity to warrant a sub-driver walk.

1. **`permission-role` sub-driver.** Entered from the PA-NNN
   cross-cutting sub-batch when the surface carries multiple
   role-gated affordances OR when the PM's answer at P1 (role
   baseline) was "different per surface". Walks every role × every
   affordance and captures the visibility / interactivity matrix.
   Exits when every cell of the role × affordance matrix is filled or
   marked DI with status `Open` for resolution at the conclusion
   gate.
2. **`validation-dependency` sub-driver.** Entered from the VC-NNN
   cross-cutting sub-batch when validation rules carry inter-field
   dependencies (field A's validity depends on field B's value, or a
   form-level rule spans 3+ fields). Walks every dependency chain and
   captures the cycle / order. Exits when every dependency is recorded
   with explicit ordering and failure-mode behaviour.
3. **`audit-trail` sub-driver.** Entered from the AU-NNN cross-
   cutting sub-batch when the surface produces audit-log entries
   with non-trivial row shape (more than `{ who, when, what }`). Walks
   the audit-log row shape, retention policy, who can view it, and
   any redaction / masking rules. Exits when the row shape is
   complete and the retention / access rules are captured.

(The `concurrency-contention` sub-driver lives in P6 — see
[`phase-P6.md`](./phase-P6.md) §"Nested sub-drivers".)

Sub-drivers are nested constructs; the coordinator never sees their
transitions. The P5 module owns the entry / exit decisions.

---

## Component Pattern Block discipline (delta-style, no recon)

For each matched component from the breakdown's Component Pattern
Summaries, the interviewer presents the canonical Pattern Block
in-line and asks only the deltas the feature introduces. The
interviewer does NOT re-open the component YAML mid-interview
(Family E E1); the Pattern Summaries are the source. See
[`../component-matching.md`](../component-matching.md) for the
Pattern Block format and the delta-question protocol.

Unmatched components (no canonical pattern in the breakdown) fall back
to the open-ended catalogue in
[`../question-sets/section-5-ui-and-ux.md`](../question-sets/section-5-ui-and-ux.md)
and are flagged in PRD §7 Open Items as "novel UI pattern — candidate
for future component-YAML capture".

---

## Family N anchor extraction at P5 closure

P5 is where the Family N N1 anchor structures are first populated.
During the Component Pattern Block work above, the cited component
YAMLs are already in memory (loaded from the breakdown's Component
Pattern Summaries — not via mid-interview disk read). At P5 closure,
for each cited YAML, the interviewer stores an in-memory anchor
structure of the form:

```text
{
  path: ".context/components/<component>.yaml",
  read_mode: "full",
  anchors: {
    <anchor_key>: "<verbatim value from the cited Pattern Summary>",
    ...
  }
}
```

Anchor selection rule (Family N N1):

- Anchors are short, low-cost, read-proof tokens the handoff chat
  will be required to attest having read.
- Each cited YAML carries between 3 and 8 anchors covering at minimum:
  state names (e.g. third state name), empty-state copy strings
  verbatim, action button count, top-level header / version values,
  and any verbatim copy string the demo must reproduce.
- Anchors are extracted **from the in-memory Pattern Summary**, not
  by re-opening the YAML on disk. Family E E1 prohibits mid-interview
  recon; the Pattern Summary is the source.

These anchor structures are pulled into the P9 demo / sample-data /
component-spec briefs at Section 3 (per Family N N8 brief
pre-extraction). P9 does not re-open the YAMLs to build the brief —
the heavy YAML read is paid once, by the chat that already has them
in memory. See
[`../sub-agent-delegation.md`](../sub-agent-delegation.md) for the
brief Section 3 format and the on-return Family N anchor
verification.

If a cited YAML's Pattern Summary is too thin to extract 3 anchors,
the interviewer surfaces this to the PM at P5 closure and either
(a) accepts an L5.2 override for thin Pattern Summaries
(`prd_interview_override_applied` already emitted at Step 0) and
records a DI entry for the affected surface, or (b) escalates back to
`prd-orchestrator` for a re-run.

---

## Component Pattern Confirmation Report (authored at end of P5)

At the end of P5, **before** the P5 self-review, the interviewer
authors the bulk Component Pattern Confirmation Report to
`component-pattern-confirmation.md` in the sub-PRD folder. This
artifact validates the canonical Pattern Block usage across every
matched component and replaces the deprecated D4 screenshot pattern.

Report sections:

1. **Matched components.** One row per matched component from the
   breakdown's Component Pattern Summaries; columns: component name,
   canonical Pattern Block fingerprint, delta-questions asked, PM
   answers, retained-or-amended classification.
2. **Unmatched components.** One row per component with no canonical
   match; columns: component name, the open-ended capture path
   followed, the resulting six-element spec, the candidate-for-YAML
   flag.
3. **Pattern fidelity summary.** Per matched component: a one-line
   statement of whether the feature retains the canonical pattern
   verbatim, amends a specific cell, or diverges enough to warrant
   PM-confirmed override (with override reason recorded).
4. **Carry-over to P9 briefs.** A pointer list naming which matched
   components' anchors feed which P9 brief Section 3 entries.

The Confirmation Report is authored at P5 end so the bulk Pattern
Block validation work happens once and is not re-litigated at P9. The
P5 self-review checks the Confirmation Report is present and well-
formed before phase exit. The pre-write artifact-bar walk (L6 G3)
runs against `component-pattern-confirmation.md`'s Pass Conditions
before the file is written.

---

## Depth bar

P5 is complete when **all** of the following are true:

- Every screen in the screen inventory is classified (`new` /
  `modified`) with a stated purpose, navigation trigger, and (for
  modified) before / after delta.
- Every component has all six spec elements captured (per
  `component-spec-template.md`).
- Every component has every state and every transition defined; each
  transition has a `WF-NNN` ID, a trigger event, side-effects, and
  rollback / cancel behaviour.
- D-DETAIL is satisfied for every in-scope UI surface (every label,
  tooltip, placeholder, validation message, empty-state copy, hover,
  disabled-state reason, keyboard interaction recorded — or
  explicitly TBD with a DI entry).
- D-CROSS is satisfied: every consumed / consuming entity has been
  walked; every cross-page impact has a `CP-NNN` entry.
- Every in-scope surface has a `PF-NNN` entry OR a
  `PF: Not applicable — [reason]` notice.
- All seven cross-cutting sub-batches have been asked.
- Every entered sub-driver (`permission-role`, `validation-
  dependency`, `audit-trail`) has exited cleanly.
- Family N anchor structures are populated for every cited YAML
  (3–8 anchors per YAML, drawn from the in-memory Pattern Summary).
- `component-pattern-confirmation.md` is written and the pre-write
  artifact-bar walk passes.

---

## P5-specific self-review (D-COMP / D-DETAIL / D-CROSS walk) — phase exit checklist

P5-specific L6 G1 self-review walks the three coverage dimensions
explicitly. The interviewer verifies, item by item:

1. **D-COMP — Component completeness.** For every component captured,
   all six spec elements present; every state and every transition
   recorded with `WF-NNN` IDs.
2. **D-DETAIL — Micro-detail completeness.** For every in-scope
   surface: every label / tooltip / placeholder / validation message /
   empty-state copy / hover / disabled-state reason / keyboard
   behaviour captured or DI-tracked.
3. **D-CROSS — Cross-page impact completeness.** Every consumed /
   consuming entity walked; every impact carries a `CP-NNN` entry
   with `direction`, `consumer-sub-PRD-or-page`, and
   `consumed-behaviour-reference`. No CP-NNN entry duplicates
   behaviour text.
4. **PF coverage.** Every in-scope surface has a `PF-NNN` entry or a
   `PF: Not applicable — [reason]`.
5. **Sub-driver closure.** Every entered nested sub-driver
   (`permission-role`, `validation-dependency`, `audit-trail`) has
   exited cleanly with its matrix / chain / row shape captured.
6. **Family N anchors.** Every cited YAML has 3–8 anchors in the
   in-memory anchor structure; thin Pattern Summaries are flagged
   with a DI entry.
7. **Component Pattern Confirmation Report.** Written; all four
   sections populated; pre-write artifact-bar walk passed.

Any item that fails either re-runs the failing capture or is recorded
as a DI entry with status `Open` for the conclusion gate to resolve.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P5`, and `failedChecklistItem` naming the
specific dimension or item that failed.

---

## Telemetry

P5-scoped emit sites only:

- `prd_phase_started` — `phaseId: P5`.
- `prd_phase_completed` — `phaseId: P5`. Coverage dimensions
  `D-COMP`, `D-DETAIL`, `D-CROSS` are evaluated here.
- `prd_self_review_gate_failed` — emitted if the D-COMP / D-DETAIL /
  D-CROSS / PF / sub-driver / anchor / Confirmation Report walk
  fails.
- `prd_coverage_dimension_blocked` — emitted with the specific
  `dimension` if any of D-COMP / D-DETAIL / D-CROSS cannot be closed
  at P5.
- `prd_pre_write_bar_walk_failed` — emitted if the artifact-bar walk
  fails on `component-pattern-confirmation.md`; the file is NOT
  written until the failing Pass Condition is resolved.

---

## Cross-cutting protocols invoked (pointer only)

P5 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family E — No mid-interview recon.** Component YAMLs are not
  re-opened mid-interview; the Pattern Summaries from the breakdown
  are the source. Anchor extraction draws from the in-memory state,
  not from disk.
- **Family F — Three-tier message text sourcing.** Every UI string
  captured here is Tier 1 (verbatim YAML), Tier 2 (PM-approved
  outcome phrasing), or Tier 3 (interviewer-drafted, marked,
  PM-approved).
- **Family J — Anti-hallucination.** No invented labels, no invented
  states, no invented role-gating, no invented validation rules.
- **Family M — Application-fidelity.** When a production UI affordance
  exists, the P9 brief MUST cite the relevant YAML(s) — anchors
  captured here seed that obligation.
- **Family N — Handoff-chat read discipline.** N1 / N8 anchor
  extraction happens here at P5 closure for the downstream P9 briefs.
- **Family A — Question discipline.** Each cross-cutting sub-batch is
  one predicate followed by 2–4 structured follow-ups on `yes`;
  never a list-dump.

---

## Next phase

On P5 exit (self-review pass + `component-pattern-confirmation.md`
written + `prd_phase_completed` emitted), the coordinator routes to
[`phase-P6.md`](./phase-P6.md) (Edge cases — always runs).
