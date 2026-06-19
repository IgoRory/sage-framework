# Phase P4 — Allocation methodology (conditional)

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines only
the P4-specific scope, the allocation-vs-calculation distinction, the
worked-example mandate calibrated for allocation, the pre-enumerated
allocation patterns, the AL-NNN in-flow assignment rule, the seven
cross-cutting sub-batches calibrated for allocation, and the P4
self-review.

**Phase ID:** `P4`
**Conditional — runs only when the P2 §4 coverage map declares §4.3 AL
in scope (the trigger predicate: "breakdown indicates allocation logic
in scope" OR PM amended the coverage map at P2 to include §4.3 AL).**
**Question catalogue:** [`../question-sets/section-4-allocation.md`](../question-sets/section-4-allocation.md)

---

## Trigger predicate (conditional)

The coordinator enters P4 only when, at P2 exit, the §4 coverage map
declared at least one of:

- **breakdown indicates allocation** logic in scope (`breakdown
  .investigation_context.affected_allocation_rules` non-empty, or
  `breakdown` Allocation Pattern Summaries present), OR
- PM amended the P2 coverage map to include §4.3 AL because the feature
  introduces a new allocation rule or modifies an existing one.

If neither condition holds, the coordinator skips P4 and routes to P5
(if UI in scope), else P6. When P4 is skipped, §4.3 carries an explicit
`Not applicable — [reason]` notice in the PRD; no silent omission.

---

## Allocation is distinct from calculation

Allocation distributes one source value across many target rows via a
driver. Calculation (P3) transforms inputs into outputs row-by-row. The
shapes are different, the mandatory artefacts are different, and the
phase modules are independent.

Key shape distinctions captured at P4 (not P3):

- **Driver.** The dimension or column used to apportion the source
  across targets (e.g. headcount, square footage, transaction volume,
  weighted score).
- **Scope.** The set of target rows that receive an allocation share.
- **Source pool.** The value being allocated (e.g. total facilities
  cost = 4,000,000).
- **Target pool.** The set of receivers (e.g. all cost centres in a
  region, all products under an org unit).
- **Fractional-remainder handling.** What happens to rounding remainder
  after the integer / decimal split (residue to largest receiver / pro
  rata across all / drop / dedicated rounding bucket).
- **Ordering across multiple rules.** When two or more allocation rules
  feed each other (output of rule A becomes input of rule B), the
  ordering is explicit.

---

## Worked-example structure (mandatory, calibrated for allocation)

Every allocation rule captured at P4 carries a worked example with
**six** parts (calculation's four parts plus two allocation-specific
items). The interviewer NEVER invents numbers — `[NUMBERS TBD —
requires PM decision]` markers blocking the single conclusion gate
otherwise.

The six parts:

1. **Driver.** Specific named driver column / dimension with example
   values per target row.
2. **Scope.** Specific list (or selection rule) for the target rows the
   allocation applies to.
3. **Source pool.** Specific numeric value of the pool being allocated
   (e.g. 4,000,000.00 total cost).
4. **Target pool.** Specific list of target rows with their driver
   values and the resulting allocated share (so the example
   reconciles).
5. **Exclusions.** Which target rows are excluded from receiving an
   allocation share, and why.
6. **Fractional-remainder handling.** What happens to the rounding
   residue after the driver-based split.

If multiple allocation rules apply, the **ordering** between rules is
recorded as a separate item in the example (rule A runs first, its
output becomes rule B's input, etc.).

The six-part shape lives in `interview-answers.json` under each
`AL-NNN` entry. PRD §4.3 references the worked example by `AL-NNN` ID.

---

## Pre-enumerated allocation patterns (delta-style ask)

Because the allocation-domain YAMLs are deferred (Path 2), P4 cannot
ask against a canonical catalogue. It runs a fixed enumeration of four
allocation patterns and asks the PM to classify per rule:

1. **Driver-based.** Allocation share = source pool × (target driver
   value / sum of all in-scope target driver values). Standard
   pro-rata-by-driver.
2. **Equal split.** Source pool / count of target rows. Each target
   receives the same share regardless of driver.
3. **Pro-rata.** Allocation share weighted by an explicit ratio
   (similar to driver-based but the ratio is precomputed, not
   recomputed at allocation time).
4. **Weighted.** Allocation share computed by a weighted combination of
   two or more drivers (e.g. 70% headcount + 30% transaction volume).

PM responses per allocation rule:

- **One of the four.** Pattern is recorded; the worked example fills in
  the pattern's required parameters.
- **A different pattern.** PM describes verbatim; entry is captured and
  flagged in PRD §7 Open Items as "novel allocation pattern — candidate
  for future Path 2 allocation domain YAML".
- **Hybrid.** Pattern combines two of the four (or modifies one). PM
  describes the combination verbatim.

---

## AL-NNN assigned in-flow (closure check against breakdown)

`AL-NNN` IDs are assigned **at the moment of capture**. Every cost pool
or income stream the PM names — and every allocation rule introduced or
changed — gets an `AL-NNN` ID at the moment the PM confirms the worked
example.

**Closure check at P4 exit.** Same shape as P3's closure check: compare
the count of `AL-NNN` entries captured against
`breakdown.investigation_context.affected_allocation_rules.count`. Any
mismatch is reconciled before phase exit (PM either confirms each
missing rule as in scope with a targeted catch-up, or as out of scope
with a §3.2 entry).

The closure check is a hard depth-bar item.

---

## P4 cross-cutting sub-batches (seven predicate triggers, calibrated for allocation)

After the allocation methodology is captured, P4 runs the same seven
cross-cutting sub-batches as P3, calibrated for allocation semantics.
Each sub-batch is a one-shot predicate; `yes` triggers structured
follow-ups, `no` records the sub-section as `Not applicable — [reason]`
for this allocation rule.

1. **VC-NNN — Validation & Constraints.** Trigger:
   > "Validation rules beyond the standard exclusions? (e.g. driver
   > value must be > 0, target row must be active, total allocated
   > must equal source pool within tolerance)"
   On `yes`: captures per-rule the failed-value behaviour and message
   text (Family F three-tier sourcing).

2. **PA-NNN — Permissions & Access Control.** Trigger:
   > "Who can trigger this re-allocation or edit the rule? Same as the
   > P1 role baseline or different?"
   On `yes` (different): captures the role × action pair as a PA-NNN
   entry.

3. **NM-NNN — Notifications & Messaging.** Trigger:
   > "Does completion (or failure) of this allocation run trigger any
   > notification — toast, email, alert, banner?"
   On `yes`: captures per-trigger the notification text, audience, and
   channel.

4. **AU-NNN — Audit & Telemetry.** Trigger:
   > "Does this allocation produce an audit-log entry? Which fields
   > (who ran it, when, source pool, allocation rule version, target
   > shares produced)?"
   On `yes`: captures the audit-log row shape.

5. **WF-NNN — Workflow & State.** Trigger:
   > "When does this allocation run? Manual / scheduled / on-event / on
   > user save / on month-end close?"
   On `yes` (non-manual): captures the trigger event and the resulting
   state transition for the affected entities.

6. **IN-NNN — Integration & External Surfaces.** Trigger:
   > "Does this allocation feed any external system (Dataverse,
   > downstream BI, regulatory feed, consolidation engine)?"
   On `yes`: captures the consumer, payload shape, and freshness
   contract.

7. **PF-NNN — Performance & Scale.** Trigger:
   > "Is there a performance budget? Must complete within N seconds,
   > must allocate N rows per second, must not block the close cycle
   > beyond M minutes?"
   On `yes`: captures budget verbatim and the failure mode if the
   budget is exceeded.

Every `yes` produces a §4 sub-section entry under its prefix. Every
`no` reinforces the §4 sub-section's `Not applicable` notice for this
allocation rule.

---

## Depth bar

P4 is complete when **all** of the following are true:

- Every affected allocation rule has an `AL-NNN` ID and a six-part
  worked example (or a `[NUMBERS TBD]` marker linked to a DI entry).
- The closure check against
  `breakdown.investigation_context.affected_allocation_rules` is
  reconciled.
- Every cost pool / income stream named at any point has a driver and
  an explicit exclusion list.
- The fractional-remainder handling is explicit per rule.
- The ordering across multiple allocation rules is explicit (if multiple
  rules apply).
- The pattern classification (driver-based / equal / pro-rata /
  weighted / different / hybrid) is recorded per rule.
- All seven cross-cutting sub-batches have been asked; each one either
  produced cross-cutting entries (VC / PA / NM / AU / WF / IN / PF) or
  recorded `Not applicable — [reason]`.
- If the allocation produces an audit-log impact (§4.12 AU): the
  additional / changed information and backward-compatibility
  behaviour is defined.

---

## P4-specific self-review (closure-rule walk per allocation rule) — phase exit checklist

P4-specific L6 G1 self-review walks the **closure rule per allocation
rule**. For each `AL-NNN` entry captured at P4, the interviewer
verifies:

1. **Driver.** Named driver column / dimension with example values per
   target row.
2. **Scope.** Target row set is explicit (a list or a selection rule a
   developer can reproduce).
3. **Source pool.** Numeric value of the pool being allocated.
4. **Target pool.** Target rows with driver values and resulting
   shares; example reconciles.
5. **Exclusions.** Each excluded target row carries a stated reason.
6. **Fractional-remainder handling.** Behaviour for rounding residue is
   explicit.
7. **Ordering.** If this allocation feeds (or is fed by) another
   allocation rule, the ordering is recorded in §1.3 Dependencies.

Any `AL-NNN` that fails any of the seven closure items either re-runs
the failing item or is recorded as a DI entry with status `Open`.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P4`, and `failedChecklistItem` naming the
specific closure item that failed (and the AL-NNN it failed for).

---

## Telemetry

P4-scoped emit sites only:

- `prd_phase_started` — `phaseId: P4`.
- `prd_phase_completed` — `phaseId: P4`.
- `prd_self_review_gate_failed` — emitted if the closure-rule walk
  fails for any `AL-NNN`.
- `prd_coverage_dimension_blocked` — emitted if a coverage dimension
  cannot be closed at P4.

---

## Cross-cutting protocols invoked (pointer only)

P4 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family J — Anti-hallucination.** No invented drivers, no invented
  numeric values, no invented target rows. The PM is the only source.
- **Family A — Question discipline.** Each cross-cutting sub-batch is
  one predicate followed by 2–4 structured follow-ups on `yes`.
- **Family B — Verbatim recording.** Pattern descriptions and exclusion
  reasons recorded verbatim.
- **Family E — No mid-interview recon.** Allocation-domain YAMLs do not
  yet exist; interviewer does not re-read allocation source code.

---

## Next phase

On P4 exit (self-review pass + `prd_phase_completed` emitted), the
coordinator routes per the §4 coverage map declared at P2:

- §4.5 UI in scope → [`phase-P5.md`](./phase-P5.md) (UI & UX).
- Else → [`phase-P6.md`](./phase-P6.md) (Edge cases — always runs).
