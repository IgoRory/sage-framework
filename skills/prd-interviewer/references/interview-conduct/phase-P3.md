# Phase P3 — Calculation logic (conditional)

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines only
the P3-specific scope, the worked-example mandate, the pre-enumerated
exclusion classes, the CL-NNN in-flow assignment rule, the seven
cross-cutting sub-batches with predicate triggers, and the P3
self-review.

**Phase ID:** `P3`
**Conditional — runs only when the P2 §4 coverage map declares §4.2 CL
in scope (the trigger predicate: "breakdown indicates calculation logic
in scope" OR PM amended the coverage map at P2 to include §4.2 CL).**
**Question catalogue:** [`../question-sets/section-3-calculation.md`](../question-sets/section-3-calculation.md)

---

## Trigger predicate (conditional)

The coordinator enters P3 only when, at P2 exit, the §4 coverage map
declared at least one of:

- **breakdown indicates calculation** logic in scope (`breakdown
  .investigation_context.affected_calculation_processes` non-empty, or
  `breakdown` Calculation Pattern Summaries present), OR
- PM amended the P2 coverage map to include §4.2 CL because the
  feature introduces a new calculation or modifies an existing one.

If neither condition holds, the coordinator skips P3 and routes to P4
(if AL in scope), else P5 (if UI in scope), else P6.

When P3 is skipped, §4.2 carries an explicit `Not applicable — [reason]`
notice in the PRD; no silent omission.

---

## Scope

P3 establishes the before / after behaviour of every affected
calculation in scope, downstream metric impacts, exclusion handling, and
the cross-cutting concerns that ride alongside calculation logic
(validation, permissions, notifications, audit, workflow, integration,
performance).

Calculation here is the **scalar-transformation** sense: one or more
inputs are combined by a stated formula to produce one output per row /
per group. Allocation (one source distributed across many targets via a
driver) is distinct and lives in P4.

---

## Worked-example structure (mandatory)

Every calculation captured at P3 carries a worked example with four
parts. The interviewer NEVER invents numbers — if the PM cannot supply
specific numeric values, the example is flagged
`[NUMBERS TBD — requires PM decision]` with a DI entry (status `Open`)
that blocks the single conclusion gate APPROVE.

The four parts:

1. **Inputs.** Specific numeric values for every input the formula
   consumes. Real product values (e.g. balance = 1,250,000.00; rate =
   3.50; days = 30) preferred over placeholders.
2. **Transformation.** The PM's plain-language formula. The interviewer
   records the formula verbatim; if the PM uses internal mechanism prose
   (SP names, view columns), Family J J2 surfaces the breach and asks
   for a business-language restatement. Internal mechanism prose is
   admissible verbatim ONLY when the PM explicitly requests
   carry-through (L2 carry-over).
3. **Outputs.** Specific numeric value(s) the transformation produces
   for the inputs above. Reconciles with the formula.
4. **Boundary case.** At least one of: NULL input, zero input, maximum
   value, minimum value, or a missing reference (e.g. missing rate
   source). The PM picks which boundary is most representative of the
   real-world risk.

The four-part shape lives in `interview-answers.json` under each
`CL-NNN` entry. PRD §4.2 references the worked example by `CL-NNN` ID.

---

## Pre-enumerated exclusion classes (delta-style ask, fixed enumeration)

Because the calculation-domain YAMLs (Path 2) are deferred, P3 cannot
ask "which exclusions apply?" against a canonical catalogue. Instead it
runs a fixed enumeration of five exclusion classes and asks the PM to
classify per class: `yes` (this exclusion applies, here is the outcome),
`no` (does not apply), `different` (a different exclusion logic applies,
PM describes verbatim).

The five classes:

1. **NULL-input handling.** What happens when any required input is
   NULL? (skip the row / treat as zero / halt the calculation / error
   message).
2. **Zero-input handling.** What happens when an input is present but
   zero? (proceed / skip / produce zero output / flag).
3. **Missing-instrument handling.** What happens when an expected
   reference instrument (e.g. an account, a product, a rate row) is
   missing? (skip / halt / produce a flagged row / fallback to a
   default).
4. **Missing-pricing-data handling.** What happens when an input depends
   on a pricing source (e.g. FTP curve, market rate) and that source is
   unavailable? (use last-known / halt / flag / fallback).
5. **Missing-rate-source handling.** What happens when a rate-source
   record is missing (e.g. no rate row for the effective date)? (skip /
   halt / fallback / interpolate).

Each PM answer creates an in-flow §4.2 CL entry OR a §4.7 ER entry,
depending on whether the outcome is calculation behaviour (continue
with stated handling) or error behaviour (halt + message). Both kinds
are admissible; the classification determines which §4 sub-section
the entry lives in.

If the PM describes a `different` exclusion that does not match any of
the five classes, the entry is captured verbatim and flagged in PRD §7
Open Items as "novel exclusion pattern — candidate for future Path 2
calculation domain YAML".

---

## CL-NNN assigned in-flow (closure check against breakdown)

`CL-NNN` IDs are assigned **at the moment of capture**, not at PRD
generation. Every calculation surfaced at P3 — whether a new metric or
a behaviour change to an existing process — gets a `CL-NNN` ID at the
moment the PM confirms the worked example.

**Closure check at P3 exit.** The interviewer compares the count of
`CL-NNN` entries captured against
`breakdown.investigation_context.affected_calculation_processes.count`
(or equivalent breakdown field). If the counts mismatch, the
interviewer surfaces the mismatch BEFORE phase exit:

- **Captured < breakdown.** Interviewer enumerates the processes the
  breakdown lists but P3 did not cover, asks the PM to confirm each as
  in scope (run targeted catch-up question for each) or out of scope
  (move to §3.2 with reason).
- **Captured > breakdown.** PM confirms the extra captures are real
  (breakdown was thin) or were misread (interviewer removes the spurious
  entries). Extra-captures are common and acceptable; the closure check
  is a safety net, not a blocker.

The closure check is a hard depth-bar item — P3 cannot exit until the
mismatch is reconciled (resolved or PM-acknowledged with a DI entry).

---

## P3 cross-cutting sub-batches (seven predicate triggers)

After the calculation logic itself is captured, P3 runs seven cross-
cutting sub-batches. Each sub-batch is a one-shot predicate question
(Family A predicate discipline). A `yes` answer triggers a small batch
of structured follow-up questions; a `no` answer records the
sub-section as `Not applicable — [reason]` for this calculation and
moves on.

The seven sub-batches and their predicates:

1. **VC-NNN — Validation & Constraints.** Trigger:
   > "Validation rules for inputs beyond the standard exclusion
   > classes? (e.g. value must be in range, value must match a
   > reference list, value must not exceed a parent value)"
   On `yes`: structured follow-up captures per-rule the failed-value
   behaviour and message text (per Family F three-tier sourcing).

2. **PA-NNN — Permissions & Access Control.** Trigger:
   > "Who can trigger this recalculation? Same as the role baseline
   > from P1 or different?"
   On `yes` (different): captures the role × action pair as a PA-NNN
   entry. On `no` (same as baseline): no PA-NNN entry — the baseline
   PA-NNN entries already cover.

3. **NM-NNN — Notifications & Messaging.** Trigger:
   > "Does completion (or failure) of this calculation trigger any
   > notification — toast, email, alert, banner?"
   On `yes`: captures per-trigger the notification text (Family F),
   audience (roles), and delivery channel.

4. **AU-NNN — Audit & Telemetry.** Trigger:
   > "Does this calculation produce an audit-log entry? If so, what
   > fields are logged (who, when, inputs, outputs, exclusions
   > applied)?"
   On `yes`: captures the audit-log row shape.

5. **WF-NNN — Workflow & State.** Trigger:
   > "When does this calculation run? Manual (user clicks a button) /
   > scheduled (overnight, intra-day) / on-event (triggered by a state
   > transition) / on user save?"
   On `yes` (any non-manual): captures the trigger event and the
   resulting state transition for the affected entities. Manual-only
   calculations do not produce WF-NNN entries.

6. **IN-NNN — Integration & External Surfaces.** Trigger:
   > "Does this calculation feed any external system (Dataverse,
   > downstream BI, regulatory feed, partner API)?"
   On `yes`: captures the consumer, the shape of the payload, and the
   freshness contract (real-time / batched / on-demand).

7. **PF-NNN — Performance & Scale.** Trigger:
   > "Is there a performance budget for this calculation? Must
   > complete within N seconds, must process N rows per second, must
   > not block the UI thread beyond M ms?"
   On `yes`: captures the budget verbatim and the failure mode if the
   budget is exceeded (warning / halt / queue).

Every `yes` answer also creates an entry in the corresponding §4
sub-section under its prefix. Every `no` answer reinforces the §4
sub-section's `Not applicable` notice for this calculation (the §4
sub-section as a whole may still be in scope from other phases).

---

## Depth bar

P3 is complete when **all** of the following are true:

- Every affected business metric (named in P1 or surfaced via breakdown)
  is recorded with an explicit before / after direction, downstream
  consumers traced.
- Every affected calculation process has a `CL-NNN` ID and a worked
  example with all four parts (or a `[NUMBERS TBD]` marker linked to a
  DI entry).
- The closure check against
  `breakdown.investigation_context.affected_calculation_processes` is
  reconciled.
- All five exclusion classes have been asked per calculation; each
  outcome lives in a §4.2 CL entry, §4.7 ER entry, or `Not applicable`
  notice.
- All seven cross-cutting sub-batches have been asked; each one either
  produced cross-cutting entries (VC / PA / NM / AU / WF / IN / PF) or
  recorded `Not applicable — [reason]`.
- For FTP-style calculations specifically: pricing date, rate source,
  product scope each carry an explicit in / out / behaviour-change
  decision.

---

## P3-specific self-review (closure-rule walk per metric) — phase exit checklist

P3-specific L6 G1 self-review walks the **closure rule per metric**.
For each `CL-NNN` entry captured at P3, the interviewer verifies:

1. **Input set.** The worked example lists every input the
   transformation consumes.
2. **Transformation.** The plain-language formula is recorded verbatim
   and matches inputs → outputs.
3. **Output.** The worked example states the output value(s) for the
   stated inputs.
4. **Exclusions.** Each of the five exclusion classes has a recorded
   outcome for this metric (yes / no / different).
5. **Ordering.** If this calculation depends on the result of another
   calculation, the ordering is stated explicitly and the dependency is
   recorded in §1.3 Dependencies.

Any `CL-NNN` that fails any of the five closure items either re-runs
the failing item or is recorded as a DI entry with status `Open`.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P3`, and `failedChecklistItem` naming the
specific closure item that failed (and the CL-NNN it failed for).

---

## Telemetry

P3-scoped emit sites only:

- `prd_phase_started` — `phaseId: P3`.
- `prd_phase_completed` — `phaseId: P3`. Coverage dimension `D-SP`
  (every affected calculation process has a before / after behaviour
  statement) is evaluated here.
- `prd_self_review_gate_failed` — emitted if the closure-rule walk
  fails for any `CL-NNN`.
- `prd_coverage_dimension_blocked` — emitted with
  `dimension: D-SP` if the dimension cannot be closed at P3.

---

## Cross-cutting protocols invoked (pointer only)

P3 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family J — Anti-hallucination.** The interviewer NEVER invents
  numbers, formulas, or exclusion outcomes. Every numeric value in the
  worked example comes from a PM utterance verbatim.
- **Family A — Question discipline.** Each cross-cutting sub-batch is
  one predicate followed by 2–4 structured follow-ups on `yes`; never
  a list-dump.
- **Family B — Verbatim recording.** Formula prose and exclusion
  outcomes recorded verbatim.
- **Family E — No mid-interview recon.** Calculation-domain YAMLs do
  not yet exist; interviewer does not re-read calculation source code.

---

## Next phase

On P3 exit (self-review pass + `prd_phase_completed` emitted), the
coordinator routes per the §4 coverage map declared at P2:

- §4.3 AL in scope → [`phase-P4.md`](./phase-P4.md) (Allocation).
- Else §4.5 UI in scope → [`phase-P5.md`](./phase-P5.md) (UI & UX).
- Else → [`phase-P6.md`](./phase-P6.md) (Edge cases — always runs).
