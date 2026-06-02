# Phase P1 — Feature and capability

Reference for `prd-interviewer`. Self-contained — no external skill
references. All cross-phase behavioural rules (Families A–N, L11 failure
rows, ABORT path, re-entry, backfill-on-touch) live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines only
the P1-specific scope, depth bar, in-flow ID seeds, and self-review.

**Phase ID:** `P1`
**Always asked. First substantive phase after Step 0.**
**Question catalogue:** [`../question-sets/section-1-feature-definition.md`](../question-sets/section-1-feature-definition.md)

---

## Step 0 preamble — repo preflight (runs before P1)

P1 only begins after Step 0 has either passed all L5 readiness checks or
the PM has acknowledged an L5.2 override. Step 0 is owned by the
coordinator (`SKILL.md`); P1 inherits its outputs. The full Step 0 matrix
(hard-stop vs override-eligible categories, telemetry events,
reduced-fidelity markers) is defined in
[`shared-protocols.md`](./shared-protocols.md) under **L5 — Inputs &
Preconditions**.

Before the first P1 question, the coordinator MUST have completed all of
the following. P1 fails fast and surfaces to PM if any item is missing:

1. **Breakdown read.** `prd-breakdown.[sub-prd-id].md` parsed;
   `investigation_context` and Component Pattern Summaries extracted into
   the in-memory interview state.
2. **L5.1 hard-stop checks passed** (breakdown present and parseable,
   sub-PRD ID in breakdown, on required branch, working tree clean in
   scoped paths). Any hard-stop emits `prd_interview_hard_stopped` and
   terminates the interview before P1.
3. **L5.2 override decisions logged.** Any thin Component Pattern
   Summaries, stale manifest, missing cited YAMLs, mass-stale citations,
   or telemetry sink unavailability has been surfaced to the PM and either
   resolved or PM-acknowledged. Each acknowledgement emitted
   `prd_interview_override_applied` with the matching `overrideType`.
   Acknowledged overrides flag the PRD with the K2 reduced-fidelity
   marker.
4. **Pre-lift bundle detection completed.** If the bundle is pre-lift per
   the detection rule in `shared-protocols.md`, backfill-on-touch
   migration has been performed before P1 begins.
5. **Context checklist + investigation summary confirmed.** PM has
   reviewed the investigation summary and corrections have been applied
   per `shared-protocols.md`.
6. **`prdRunId` generated** (UUID v4) and stamped onto every telemetry
   event envelope emitted from this run.

If any precondition fails after the coordinator's Step 0 attempts to
satisfy it, P1 does NOT start; control returns to the coordinator for
hard-stop or override handling.

---

## Scope

Establish what the feature lets a user do that they cannot do today, who
the users are, what kind of change the feature represents, and seed the
canonical ID streams that downstream phases continue. Three categories:

1. **Feature identity** — purpose statement, business outcome, primary
   user value.
2. **Change classification** — primary change type plus any secondary
   classifications (hybrid features are explicitly allowed; the schema is
   a multi-classification list, not a single-pick).
3. **User roles** — every role that interacts with this feature, the
   shape of each interaction, and the permission level (delta against the
   roles already gating the affected pages).

**Urgency is NOT asked here.** Urgency lives in Linear / ADO at the work
item level. The legacy P1 urgency question is permanently removed; the
PRD §1 schema has no urgency field.

---

## Change-type enumeration (multi-classification allowed)

Every feature MUST carry at least one of the following change types in
the PRD §1 Feature Definition. Hybrid features carry two or more:

- `new-capability` — adds a capability the user could not perform before.
- `capability-extension` — extends an existing capability to a new entity
  class, new state, new role, or new surface.
- `behaviour-change` — alters the outcome of an existing user action
  without exposing a new capability.
- `data-migration-only` — no user-facing behaviour change; backend data
  shape changes only (rare for this product).
- `removal` — deprecates and removes an existing capability.
- `bug-fix-with-business-impact` — defect fix that materially changes the
  business outcome (not a cosmetic fix; cosmetic fixes do not warrant a
  PRD).

The PM picks one or more from this fixed enumeration. New change types
require a schema amendment, not an inline addition.

---

## Role baseline (delta against breakdown.investigation_context)

Roles are NOT asked open-endedly. The interviewer issues a **delta-style
predicate** against the roles already gating the affected pages, sourced
from `breakdown.investigation_context.affected_pages`:

> "This feature touches pages [X, Y]. Today those pages are gated by
> [role list from breakdown]. Same or different for this feature?"

PM answers in one of three shapes:

- **Same** — confirms the same roles gate the new feature. PA-NNN seed
  carries the existing role list.
- **Different** — PM names the changed role set verbatim; PA-NNN seed
  records the delta with explicit additions / removals.
- **Mixed** — same roles can see the feature but a different role can
  trigger it (or similar). PM specifies the partition verbatim.

If `breakdown.investigation_context.affected_pages` is empty or thin
(L5.2 override condition was acknowledged), the delta question falls back
to an open-ended role enumeration; the PRD carries the K2 reduced-fidelity
marker for §1.4 / §4.9.

---

## In-flow ID seeds (assigned at P1, continued downstream)

P1 is the first phase that assigns canonical §4 sub-section IDs. Two
streams seed here; both follow the in-flow assignment rule (every
captured item gets its ID at the moment of capture, not at PRD
generation):

- **DM-NNN — Data Model & Entities.** Every data entity the PM names in
  plain English during P1 gets a `DM-NNN` ID at capture. Examples: "the
  cost pool record", "the allocation rule", "the unit-cost rule list".
  IDs are zero-padded 3-digit, sequenced per sub-PRD, never renumbered.
- **PA-NNN — Permissions & Access Control.** Every distinct role × action
  pair surfaced in the role baseline delta gets a `PA-NNN` ID at capture.
  Examples: "FP&A analyst can edit the rule list", "Auditor can read but
  not edit".

These seeds are not final — P2 confirms scope, P3–P6 add further DM /
PA entries when phase-local items surface. P1 only assigns IDs to items
explicitly named here.

---

## One-sentence capability statement — hard depth-bar item

P1 cannot exit without a one-sentence capability statement recorded
**verbatim as a PM utterance** in `interview-answers.json` under the §1.1
Purpose record. The sentence must complete the form:

> "This feature lets [role] [verb] [object] so that [business outcome]."

If the PM offers a phrasing that does not parse into that form, the
interviewer asks one targeted refinement question (Family A predicate
discipline) and re-records verbatim. The interviewer NEVER paraphrases
the PM's wording; an unparseable verbatim is preferable to a clean
paraphrase, per Family B B3.

If the PM cannot supply a one-sentence statement after three honest
attempts, the item is recorded as a DI entry (status `Open`) and P1
cannot exit until the DI is resolved at the single conclusion gate.
This is the only DI category that blocks the single conclusion gate from
APPROVE.

---

## Depth bar

P1 is complete when **all** of the following are true. Failure of any
item surfaces in the P1 self-review and either re-runs the failing item
or records a DI entry:

- One-sentence capability statement recorded verbatim per the form above.
- Primary change type recorded from the fixed enumeration; secondary
  classifications also recorded if the feature is hybrid.
- Business outcome (§1.2) stated in business language (no internal
  mechanism prose — Family J J2 cross-checks).
- Role baseline reconciled with breakdown; every role named has a stated
  interaction shape AND a permission level (either captured or marked
  `[TBD — requires PM decision]` with a DI entry).
- DM-NNN IDs assigned to every entity the PM has named so far.
- PA-NNN IDs assigned to every role × action pair surfaced so far.
- Dependencies (§1.3) seeded across the five sub-categories
  (Prerequisite / Blocks-Downstream / Concurrent / Reference /
  Cross-Sub-PRD) — partial population is acceptable; later phases
  continue to add entries.

---

## P1-specific self-review (4 items) — phase exit checklist

This is the per-phase L6 G1 self-review, run by the interviewer before
the PM sees the next phase. It REPLACES the generic checklist for P1.
The four items are evaluated as yes/no predicates; any `no` either
re-runs the failing item or is recorded as a DI entry with PM
acknowledgement. The four items:

1. **One-sentence capability statement recorded verbatim.** The exact
   PM utterance is present in `interview-answers.json` under §1.1 and
   parses into the `[role] [verb] [object] so that [outcome]` form (or
   has a `[REFINEMENT TBD]` marker with an associated DI entry).
2. **Change type from enumeration is recorded.** At least one of the six
   enumerated change types appears in §1; hybrid features have two or
   more recorded.
3. **Every role named has a stated interaction.** No role appears in §1.4
   without an associated interaction sentence. PA-NNN IDs cover every
   role × action pair surfaced.
4. **Every role's permission level is captured or DI-tracked.** Each role
   in §1.4 has either a captured permission level (read / read-write /
   trigger / approve / configure / admin) or a `[TBD — requires PM
   decision]` marker linked to a DI entry with status `Open` or
   `Accepted`.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P1`, and `failedChecklistItem` naming which
of the four items failed.

---

## Telemetry

P1-scoped emit sites only (the full event catalogue is in
[`telemetry-schema.md`](../telemetry-schema.md)):

- `prd_phase_started` — `phaseId: P1`, emitted before the first P1
  question.
- `prd_phase_completed` — `phaseId: P1`, emitted after the P1 self-review
  passes and before the coordinator transitions to P2.
- `prd_self_review_gate_failed` — emitted if the P1-specific self-review
  fails any of the four items.
- `prd_phase_rejected` — emitted only if the PM REJECTs at a later phase
  and the restart target is P1.
- `prd_phase_redirected` — emitted if a later phase REDIRECTs back to P1.

All telemetry envelopes carry the `prdRunId` assigned at Step 0.

---

## Cross-cutting protocols invoked (pointer only)

P1 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). The families that bind
most heavily in P1:

- **Family A — Question discipline.** Predicate-based phrasing only;
  batches of 2–4.
- **Family B — Verbatim recording.** Capability statement and any role
  delta recorded verbatim.
- **Family E — No mid-interview recon.** Role baseline runs against
  breakdown only; interviewer never opens YAMLs.
- **Family F — Three-tier message text sourcing.** Any user-facing text
  surfaced at P1 (e.g. permission denial copy) is sourced per the
  three-tier protocol.
- **Family J — Anti-hallucination.** Capability statement must reflect
  what the PM said; the interviewer never invents user value.

---

## Next phase

On P1 exit (self-review pass + `prd_phase_completed` emitted), the
coordinator transitions to [`phase-P2.md`](./phase-P2.md) (Scope
boundaries — always asked).
