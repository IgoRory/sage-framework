# Phase P7 — Final approval

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines
only the P7-specific scope: the plain-language summary structured by
§4 sub-section, the pre-APPROVE walk of L6 closure rules, the
interview-statistics presentation, the `interview-answers.json` write
discipline, and the APPROVE / REJECT / REDIRECT routing.

**Phase ID:** `P7`
**Always asked. Runs after the single conclusion gate
([`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md)) emits APPROVE.**

P7 is **not** an interview phase in the traditional sense — no new
§4.NNN entries are introduced here. P7 is the PM-facing summary +
final sign-off step. New entries arrive only via REJECT / REDIRECT
back to an earlier phase.

---

## Scope

P7 produces:

1. **A plain-language summary structured by §4 sub-section.** The PM
   sees, for every one of the 14 §4 sub-sections: which entries were
   captured (in plain English, not as §4.NNN ID lists), or that the
   sub-section is explicitly `Not applicable — [reason]`.
2. **A pre-APPROVE walk of the L6 closure rules.** For every §4.NNN
   entry with a closure rule (CL-NNN calculation closure, AL-NNN
   allocation closure, WF-NNN state closure, PA-NNN / VC-NNN
   permission / validation closure), the closure items are
   re-verified in PM-facing language.
3. **Interview statistics.** Total questions asked, complexity tier,
   per-phase duration, deferred items final status (all `Closed` or
   `Accepted` per the gate exit predicate).
4. **A persisted `interview-answers.json`.** Verbatim PM answer
   record across P1–P6 and the gate is written to the sub-PRD
   folder before the APPROVE prompt.
5. **An explicit APPROVE / REJECT / REDIRECT** from the PM. APPROVE
   proceeds to P8 (PRD draft + AC derivation). REJECT or REDIRECT
   re-run the named phase(s) AND the conclusion gate before P7 can
   re-run.

---

## Step 1 — Plain-language summary structured by §4 sub-section

The interviewer walks every §4 sub-section in order, sourced from the
reconciled coverage map captured at the conclusion gate
(`interview-answers.json.gate.reconciled_coverage_map`). For each
sub-section, the interviewer states one of:

- **In scope, captured.** A plain-English paragraph (2–6 sentences)
  describing what the feature does in this sub-section. The
  paragraph references entries by what they do, not by §4.NNN ID
  (e.g. "the calculation transforms input value X into output value
  Y using formula Z" rather than "CL-001 captures the transformation
  from input to output"). PM-facing language is mandatory.
- **Not applicable — [reason].** The reason recorded at P2 or
  amended at the conclusion gate is presented verbatim.

The 14 sub-sections are walked in order:

1. §4.1 Data Model & Entities (DM)
2. §4.2 Calculation & Logic (CL)
3. §4.3 Allocation & Distribution (AL)
4. §4.4 Workflow & State (WF)
5. §4.5 UI & Interaction (UI)
6. §4.6 Validation & Constraints (VC)
7. §4.7 Error Handling (ER)
8. §4.8 Notifications & Messaging (NM)
9. §4.9 Permissions & Access Control (PA)
10. §4.10 Integration & External Surfaces (IN)
11. §4.11 Performance & Scale (PF)
12. §4.12 Audit & Telemetry (AU)
13. §4.13 Reporting & Export (RX)
14. §4.14 Cross-Page Impacts (CP)

Where a sub-section is `Not applicable`, the rationale must be a
specific reason (not "no calculation in this feature" alone — the
explicit P2 declaration or amendment is reproduced). Silent omissions
are not permitted by the L4 schema's mandatory "Not applicable" rule.

PM can interrupt at any sub-section to amend. Amendments route via
REJECT or REDIRECT below; P7 itself is read-only over the captured
state.

---

## Step 2 — Pre-APPROVE walk of L6 closure rules

For every §4.NNN entry that has a closure rule, P7 re-verifies the
closure items aloud in PM-facing language. This is the safety net
catching any closure rule that passed an in-phase self-review but
the PM would want to revisit before final sign-off.

- **CL-NNN closure (P3).** For every CL-NNN entry: input set,
  transformation prose, output, exclusion list, ordering across
  multiple metrics. Verified one CL-NNN at a time.
- **AL-NNN closure (P4).** For every AL-NNN entry: driver, scope,
  source pool, target pool, exclusions, fractional-remainder, and
  ordering across multiple allocation rules. Verified one AL-NNN at
  a time.
- **WF-NNN closure (P5 / P6).** For every WF-NNN transition: from-
  state, to-state, trigger event, side-effects, rollback / cancel
  behaviour. Includes both P5 in-page transitions and P6 edge-case
  transitions.
- **PA-NNN / VC-NNN closure (P5 and cross-cutting).** Permission and
  validation entries: role × affordance matrix (PA), failed-value
  behaviour + message text (VC).

Any closure item the PM amends triggers REJECT or REDIRECT back to
the originating phase. Amendments to PA-NNN / VC-NNN that are limited
to message text (Family F three-tier sourcing only) can be captured
inline in P7 without REJECT — the §4 entry is updated and the change
is recorded under `gate.post_gate_amendments` in
`interview-answers.json` with the original closure-walk record kept
for traceability.

---

## Step 3 — Interview statistics

The interviewer presents the run statistics:

- **Total questions asked** across P1–P6 plus the conclusion gate.
- **Complexity tier** classification (per
  [`../complexity-classifier.md`](../complexity-classifier.md);
  interviewer scope is Tier 1 or Tier 2 only).
- **Per-phase duration** sourced from the
  `prd_phase_started` / `prd_phase_completed` envelope timestamps.
- **Deferred items final status.** Every DI entry is either `Closed`
  (resolved at the gate) or `Accepted` (deferred with documented
  reason). Zero `Open` items by gate exit predicate.
- **§4 coverage summary.** Count of §4.NNN entries per prefix; count
  of sub-sections marked `Not applicable`.
- **L5 overrides applied.** Any `prd_interview_override_applied`
  events emitted at Step 0 are listed by `overrideType` and
  justification; the K2 reduced-fidelity marker that will appear in
  the PRD is named.

Statistics are PM-facing — no internal mechanism references
(no SP names, no return codes, no class names). PM-directed SQL
admissible verbatim only where the PM explicitly authorised it
(carry-over from L2).

---

## Step 4 — Write `interview-answers.json`

Before the APPROVE prompt, the interviewer writes the verbatim PM
answer record across P1–P6 and the conclusion gate to
`interview-answers.json` in the sub-PRD folder.

The file is the canonical record of every PM utterance captured
in-flow plus the reconciled coverage map snapshot, the deferred items
final status, the L5 override events, and any post-gate amendments
captured at Step 2. It is the audit trail for the P8 PRD derivation
and the input the `prd-amend` flow consults on later edits.

Pre-write checks (L6 G3 artifact-bar walk for `interview-answers.json`
Pass Conditions):

- Every captured PM utterance is recorded verbatim — no
  interviewer paraphrasing in the `answers.*` keys.
- Interviewer interpretation lives in PRD-draft state only (P8) and
  is excluded from `interview-answers.json` per Family B B3.
- `prdRunId` is stamped at file head for telemetry correlation.
- The reconciled coverage map snapshot is present.
- The deferred items final status block carries no `Open` items.

If any Pass Condition fails, the interviewer does NOT write — the
failure is surfaced to the PM and the underlying gap is resolved
before the write retries. Failure emits
`prd_pre_write_bar_walk_failed` with
`artifact: interview-answers` and the failing Pass Condition
named verbatim.

---

## Step 5 — Explicit PM confirmation (APPROVE / REJECT / REDIRECT)

Only after Steps 1–4 pass cleanly:

> "I am satisfied this is a complete and accurate record of the
> requirements you've stated. Shall I proceed to generate the PRD
> bundle (P8)?"

PM responds with exactly one of:

- **APPROVE.** P7 emits `prd_phase_completed` with `phaseId: P7`.
  Coordinator routes to [`phase-P8.md`](./phase-P8.md) (PRD draft +
  AC derivation + reuse map).
- **REJECT.** PM names the phase(s) to restart from (any of P1–P6,
  or "restart from P1"). P7 emits `prd_phase_rejected` with
  `phaseId: P7`, `restartPhaseId: <named phase>`,
  `rejectionReason: <verbatim PM utterance>`. Coordinator restarts
  at the named phase; the conclusion gate must re-run before P7 can
  re-run.
- **REDIRECT.** PM directs the coordinator to a named earlier phase
  for a scope change without rejecting the entire interview. P7
  emits `prd_phase_redirected` with `phaseId: P7`,
  `fromPhaseId: P7`, `toPhaseId: <named phase>`,
  `redirectReason: <verbatim PM utterance>`. The named phase re-runs;
  downstream phases re-run only if the redirect outcome alters their
  inputs. The conclusion gate re-runs before P7 can re-run.

APPROVE here is the only path to P8. There is no separate P7→P8
gate — the single conclusion gate already ran before P7 and the
pre-APPROVE walk at Step 2 is the P7-side closure check.

---

## Telemetry

P7-scoped emit sites only:

- `prd_phase_started` — `phaseId: P7` at Step 1 entry.
- `prd_phase_completed` — `phaseId: P7` at Step 5 APPROVE.
- `prd_phase_rejected` — `phaseId: P7`, `restartPhaseId: <named>`,
  `rejectionReason: <verbatim>` on REJECT.
- `prd_phase_redirected` — `phaseId: P7`, `fromPhaseId: P7`,
  `toPhaseId: <named>`, `redirectReason: <verbatim>` on REDIRECT.
- `prd_pre_write_bar_walk_failed` — emitted if any Pass Condition
  fails on the `interview-answers.json` write.

---

## Cross-cutting protocols invoked (pointer only)

P7 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family B — Verbatim recording.** `interview-answers.json` is
  written here; B1 / B2 / B3 apply to the entire file.
- **Family D — Conclusion gates.** D2 APPROVE / REJECT / REDIRECT
  semantics; REJECT may restart any earlier phase (D3 / D4).
- **Family G — Self-review gates.** G3 pre-write artifact-bar walk
  for `interview-answers.json` — Pass Conditions in
  [`../production-grade-quality-bar.md`](../production-grade-quality-bar.md)
  must all be met before the write.
- **Family H — Closure & thoroughness.** Steps 1–3 are the final
  closure walk; no required dimension may be skipped in the §4
  sub-section walk.
- **Family K — Production-grade bar.** K2 reduced-fidelity markers
  are explicitly named in Step 3 statistics when any L5 override
  was applied.

---

## Next phase

On Step 5 APPROVE → [`phase-P8.md`](./phase-P8.md) (PRD draft + AC
derivation + reuse map + Component Pattern Confirmation Report
verification). The interviewer chat loads `prd-section-schema.md`,
`prd-template.md`, and `acceptance-criteria-template.md` at P8 entry.

On REJECT or REDIRECT, coordinator routes to the named earlier phase;
the single conclusion gate
([`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md)) must re-run
before P7 can re-run.
