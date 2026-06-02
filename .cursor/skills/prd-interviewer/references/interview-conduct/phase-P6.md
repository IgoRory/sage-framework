# Phase P6 — Edge cases (always)

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines
only the P6-specific scope, the seven edge-case categories with their
§4 sub-section ID mapping, the mandatory challenger pattern per
category, the nested `concurrency-contention` sub-driver, and the
P6 self-review.

**Phase ID:** `P6`
**Always asked, regardless of feature type.**
**Question catalogue:**
[`../question-sets/section-7-edge-cases.md`](../question-sets/section-7-edge-cases.md)
**Challenger catalogue:**
[`../question-sets/challenger-probes.md`](../question-sets/challenger-probes.md)

---

## Scope

P6 walks the seven edge-case categories below in order. Every category
is asked; depth scales with complexity tier and with the §4 coverage
map declared at P2. Each captured outcome produces an explicit §4
sub-section ID per the category-to-prefix mapping below. The phase
cannot exit a category without at least one defined outcome **and**
at least one challenger exchange recorded verbatim.

Edge-case outcomes are NEVER acceptance criteria — ACs are derived at
P8 from the §4 entries captured here, P3, P4, P5, and P1 / P2. This
phase produces §4.NNN entries; it does not write AC IDs.

---

## Seven categories with §4 sub-section ID mapping

| # | Category | §4 sub-section ID prefix |
|---|---|---|
| 1 | Interaction sequence | `WF-NNN` |
| 2 | Cascading behaviour | `WF-NNN` or `CP-NNN` |
| 3 | Concurrency | `VC-NNN` or `IN-NNN` |
| 4 | State boundary | `WF-NNN` |
| 5 | Cross-component dependency | `CP-NNN` |
| 6 | Data integrity | `DM-NNN` or `AU-NNN` |
| 7 | Failure & recovery | `ER-NNN` |

Per-category notes:

1. **Interaction sequence.** Scenarios where the order of user
   actions produces different outcomes (e.g. cancel after submit vs
   cancel before submit; reorder within a draft vs after lock). Each
   outcome produces a `WF-NNN` transition entry.
2. **Cascading behaviour.** Scenarios where one action triggers a
   chain of downstream effects (delete parent → orphan children;
   rename root → relabel descendants; recompute upstream → invalidate
   downstream cache). Each chained step produces a `WF-NNN` (in-page)
   or `CP-NNN` (cross-page) entry.
3. **Concurrency.** Scenarios where two users (or one user across
   two sessions / tabs) act on the same entity simultaneously, OR
   where a scheduled job collides with a user action. Each contention
   outcome produces a `VC-NNN` (validation / lock rule) or `IN-NNN`
   (external lock service) entry. The nested
   `concurrency-contention` sub-driver (below) runs when contention
   scenarios are non-trivial.
4. **State boundary.** Scenarios at the edges of allowed state
   transitions (transition from a state not in the canonical set;
   transition back from a terminal state; transition while the entity
   is locked or pending). Each boundary outcome produces a `WF-NNN`
   entry with the explicit allowed / disallowed classification.
5. **Cross-component dependency.** Scenarios where one component's
   behaviour depends on another component's state (filter changes
   reset grid pagination; selection state synchronises across tabs;
   header state propagates to body). Each dependency outcome produces
   a `CP-NNN` entry as a relationship pointer.
6. **Data integrity.** Scenarios where invariants must be preserved
   under partial failure (write fails after partial commit; foreign
   key violated by a parallel delete; computed totals must match
   stored values). Each invariant outcome produces a `DM-NNN`
   (entity-level invariant) or `AU-NNN` (audit-log invariant) entry.
7. **Failure & recovery.** Scenarios where the system encounters an
   external or internal failure (downstream service unavailable;
   timeout; permission revoked mid-flight; quota exceeded). Each
   failure outcome produces an `ER-NNN` entry with the user-facing
   message text (Family F three-tier sourcing), the recovery action
   available to the user, and any background retry behaviour.

---

## Mandatory challenger pattern per category

Every defined outcome in every category must be challenged at least
once with a "why this outcome and not [alternative]?" exchange. The
challenger catalogue at
[`../question-sets/challenger-probes.md`](../question-sets/challenger-probes.md)
seeds the alternative phrasings. The challenger exchange is recorded
verbatim in `interview-answers.json`; the PM's rationale becomes part
of the §4 entry's `decision-rationale` note.

Challenger rule (binding):

- Every category exit requires ≥1 challenger exchange.
- A category cannot be "skipped" — if the PM asserts no scenario
  applies in a category, the assertion itself is challenged ("why
  does this feature have no [category] edge cases?") and the
  challenger response is recorded.
- "Already covered earlier" is not sufficient. If a P3 / P4 / P5
  capture already addresses a P6 category, the interviewer states
  the cross-reference explicitly ("this category is covered by the
  CL-NNN exclusion captured at P3 — confirming with you that no
  additional scenario applies") and records the PM's confirmation.

Challenger exchanges that flip the outcome → the original outcome is
revised in-place; both the original and the revised outcome are kept
in `interview-answers.json` for traceability, and the §4 entry
carries only the revised outcome.

---

## Nested sub-driver — `concurrency-contention` (preserved per L8 sub-driver rule)

The L8 lock preserves the `concurrency-contention` nested sub-driver
**inside** P6. It is not promoted to a coordinator-level phase; it
runs as a nested sub-driver state within P6 and exits before P6
exits.

Entry trigger: any concurrency category scenario where the PM names
more than one contention pattern (simultaneous edit + lock service +
optimistic-concurrency token + scheduled job + soft delete) on the
same entity.

The sub-driver walks every contention pair (action A by user X
vs action B by user Y / job) and captures:

- Detection mechanism (optimistic token, server-side lock, version
  column, queue serialisation).
- Resolution policy (last-writer-wins, first-writer-wins,
  reject-with-merge-prompt, queue-and-retry).
- User-facing message text for the loser (Family F three-tier
  sourcing).
- Audit-log entry produced (which AU-NNN, what fields recorded).

Exit condition: every named contention pair has a captured outcome
and an explicit policy. Any unresolved pair is recorded as a DI
entry with status `Open` for the conclusion gate.

(The three UI-bound nested sub-drivers — `permission-role`,
`validation-dependency`, `audit-trail` — live in P5. See
[`phase-P5.md`](./phase-P5.md) §"Nested UI-bound sub-drivers".)

Sub-drivers are nested constructs; the coordinator never sees their
transitions. The P6 module owns entry / exit for
`concurrency-contention`.

---

## Depth bar

P6 is complete when **all** of the following are true:

- All seven categories have been walked.
- Each category has at least one scenario with a defined outcome.
- Each defined outcome has been challenged at least once.
- Each defined outcome carries a §4 sub-section ID per the category
  mapping table.
- Any `concurrency-contention` sub-driver entered has exited cleanly.
- No items remain `Open` in the Unified Deferred Items List that
  were generated by this phase (P6-originated DIs are resolved
  before exit OR carried into the conclusion gate's deferred-items
  step).

---

## P6-specific self-review (four items) — phase exit checklist

P6-specific L6 G1 self-review walks four predicates, each evaluable
as a yes/no:

1. **All 7 categories walked.** Every category in the table has at
   least one scenario with a defined outcome (D-EC satisfied).
2. **§4 ID assigned per outcome.** Every captured outcome carries an
   explicit §4 sub-section ID per the category mapping.
3. **Challenger exchange per category.** Every category has at least
   one "why this outcome and not [alternative]?" exchange recorded
   verbatim in `interview-answers.json`.
4. **No `Open` items.** No P6-originated entry remains with status
   `Open` in the Unified Deferred Items List at phase exit — items
   that cannot be resolved within P6 are explicitly carried into the
   conclusion gate's deferred-items final review.

Any item that fails either re-runs the failing capture or is recorded
as a DI entry with status `Open` for the conclusion gate.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P6`, and `failedChecklistItem` naming the
specific predicate that failed.

---

## Conclusion gate (runs after P6 exit)

Before P7 begins, the **single conclusion gate** runs. It is the
collapsed legacy two-gate pattern (legacy P6→P7 and P7→P8 gates
merged). See
[`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md) for the 6-step
protocol with §4 coverage map reconciliation and APPROVE / REJECT /
REDIRECT routing. The PM must explicitly confirm before P7 (Final
approval) starts. After the gate, no Deferred Items may remain
`Open`.

---

## Telemetry

P6-scoped emit sites only:

- `prd_phase_started` — `phaseId: P6`.
- `prd_phase_completed` — `phaseId: P6`. Coverage dimension `D-EC`
  is evaluated here.
- `prd_self_review_gate_failed` — emitted if any of the four
  self-review items fails.
- `prd_coverage_dimension_blocked` — emitted with
  `dimension: D-EC` if D-EC cannot be closed at P6.

The gate that runs after P6 emits its own telemetry per
[`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md).

---

## Cross-cutting protocols invoked (pointer only)

P6 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family A — Question discipline.** Each category opens with a
  scoped predicate ask; follow-ups are 2–4 structured questions on
  `yes`.
- **Family B — Verbatim recording.** Edge-case outcomes and
  challenger exchanges recorded verbatim.
- **Family H — Closure & thoroughness.** No silent skipping of
  categories; no quitting early; every category challenged.
- **Family J — Anti-hallucination.** No invented edge cases — every
  scenario traces to a PM utterance or a documented system constraint
  (e.g. concurrency model from the breakdown's
  `investigation_context`).

---

## Next phase

On P6 exit (self-review pass + `prd_phase_completed` emitted), the
coordinator runs the **single conclusion gate**
([`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md)) before routing
to [`phase-P7.md`](./phase-P7.md) (Final approval).
