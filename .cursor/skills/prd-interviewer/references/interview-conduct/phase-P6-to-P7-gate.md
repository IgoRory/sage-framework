# Gate — Single conclusion gate (after P6, before P7)

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module is the
**single conclusion gate** that collapses the legacy two-gate pattern
(legacy P6→P7 and P7→P8 gates) into one gate after P6 edge cases,
before P7 final approval. The legacy `phase-P7-to-P8-gate.md` is
removed.

**Runs after:** P6 self-review pass, before P7 entry.
**Six-step protocol — execute every step in order. PM must explicitly
confirm at Step 6 before P7 begins. No `Open` Deferred Items may
survive Step 5.**

---

## Telemetry envelope

The gate emits:

- `prd_phase_started` — `phaseId: Gate` at Step 1 entry.
- `prd_phase_completed` — `phaseId: Gate` at Step 6 APPROVE.
- `prd_phase_rejected` — `phaseId: Gate`, `restartPhaseId: <named>`
  on REJECT (the PM names the phase to restart from).
- `prd_phase_redirected` — `phaseId: Gate`,
  `fromPhaseId: Gate`, `toPhaseId: <named>` on REDIRECT.

REJECT / REDIRECT routing is described under Step 6.

---

## Step 1 — Present structured summary across P1–P6

Present everything captured during P1–P6, organised by phase. Each
phase summary is 2–4 sentences highlighting the key decisions and the
§4 sub-section IDs assigned:

- **P1 — Feature & capability.** One-sentence capability statement
  (verbatim), change type(s) from the enumeration, role baseline,
  DM-NNN seeds, PA-NNN seeds.
- **P2 — Scope boundaries.** In-scope / out-of-scope decisions, the
  six-category downstream consumer check outcomes, the declared §4
  coverage map.
- **P3 — Calculation** (if run). CL-NNN entries captured, worked
  examples completed, cross-cutting sub-batch outcomes.
- **P4 — Allocation** (if run). AL-NNN entries captured, worked
  examples completed, cross-cutting sub-batch outcomes.
- **P5 — UI & UX** (if run). Screen inventory, component inventory,
  WF-NNN transitions, CP-NNN impacts, PF-NNN budgets, Family N
  anchors captured, Component Pattern Confirmation Report written.
- **P6 — Edge cases.** Outcomes per category with §4 ID per outcome,
  challenger exchanges recorded.

The summary is read aloud (or rendered in chat) without paraphrasing.
PM can interrupt at any line to amend.

---

## Step 2 — Flag vague answers that survived per-phase in-flow flagging

The L4 sub-section ID assignment catches most vague answers in flow
(by forcing every captured outcome into a §4.NNN entry with stated
shape). This step lists every answer that:

- Was short or unclear when captured.
- Carried a `[TBD]` or `[NUMBERS TBD]` marker that was not later
  resolved.
- Was captured under a "Family F Tier 3 — interviewer drafted"
  marker but never PM-approved.
- Was challenged at P6 but the challenge response was itself vague.

The PM is asked to elaborate on each in turn. Each elaboration is
recorded verbatim into `interview-answers.json` against the original
phase's section.

---

## Step 3 — Open-ended coverage check (combined)

Single combined question:

> "Anything about this feature's core requirements OR its edge-case
> behaviour that you're worried we haven't covered before we move to
> final approval?"

Every additional concern raised is captured into the appropriate §4
sub-section in-flow, with the §4.NNN ID assigned at the moment of
capture (in the same shape as the originating phase would have used).
If a concern doesn't fit any §4 sub-section, the new-concept rule at
the end of Step 4 applies.

---

## Step 4 — Comprehensiveness self-assessment with §4 coverage map reconciliation

This step is the **safety net** that reconciles what was declared at
P2 against what was actually captured across P1–P6.

### 4a — Show the §4 coverage map declared at P2

Present the §4 sub-section coverage map declared at P2 exit:

```text
§4.1  DM   In scope    (or N/A — [reason])
§4.2  CL   In scope    (or N/A — [reason])
§4.3  AL   In scope    (or N/A — [reason])
§4.4  WF   In scope    (or N/A — [reason])
§4.5  UI   In scope    (or N/A — [reason])
§4.6  VC   In scope    (or N/A — [reason])
§4.7  ER   In scope    (or N/A — [reason])
§4.8  NM   In scope    (or N/A — [reason])
§4.9  PA   In scope    (or N/A — [reason])
§4.10 IN   In scope    (or N/A — [reason])
§4.11 PF   In scope    (or N/A — [reason])
§4.12 AU   In scope    (or N/A — [reason])
§4.13 RX   In scope    (or N/A — [reason])
§4.14 CP   In scope    (or N/A — [reason])
```

### 4b — Show what was actually captured P1–P6

For every sub-section, list the §4.NNN entries captured during the
relevant phase(s). Walk every sub-section in order — silence is not
acceptable; each sub-section either has entries OR an explicit
`Not applicable — [reason]` notice.

For every in-scope sub-section, the interviewer states aloud:

- Every requirement has a §4.NNN ID.
- Every numeric example is present (or a `[NUMBERS TBD]` DI exists).
- Every cross-page impact is named with a CP-NNN entry.
- Every edge-case category that maps to this sub-section is covered
  (per P6's category-to-prefix mapping).
- Every coverage dimension applicable to this sub-section is at 100%
  OR carries a DI entry with status `Accepted`.

### 4c — Show gaps (declared in scope at P2 but empty)

For every sub-section that was declared in scope at P2 but has no
§4.NNN entries captured:

- The PM either fills the gap now (any new captures get §4.NNN IDs in
  the same shape as the originating phase would have used), OR
- The PM explicitly marks the sub-section as `Not applicable —
  [reason]` and the gap is closed.

### 4d — Show unexpected captures (not declared at P2 but captured)

For every sub-section that was declared N/A at P2 but has §4.NNN
entries captured anyway (because P3 / P4 / P5 / P6 surfaced
something genuinely new):

- The PM confirms the entries are in scope and the sub-section is
  moved to "In scope" in the reconciled coverage map, OR
- The PM moves the entries to §3.2 Out of Scope and the §4.NNN
  entries are deleted from `interview-answers.json`.

### 4e — New-concept handling

If any captured item doesn't fit any of the 14 §4 sub-sections (rare
— L4 schema covers 14 prefixes by design), the PM picks one of:

- Fold the item into the closest existing sub-section (interviewer
  proposes the closest, PM confirms).
- Add a custom requirement section under §4 with a temporary
  `[CUSTOM-NNN]` ID; the item is also recorded for future L4 schema
  amendment review.
- Mark out of scope (§3.2).

Recurring novel patterns across multiple sub-PRDs are flagged in the
`prd-interviewer-effectiveness-evaluator` data set as candidates for
future L4 schema amendment.

### 4f — Reconciled coverage map snapshot

After 4a–4e, the reconciled §4 coverage map is captured as a snapshot
in `interview-answers.json` under `gate.reconciled_coverage_map`.
This snapshot is the input to P7's plain-language summary structured
by §4 sub-section.

---

## Step 5 — Deferred Items final review

Present the full Unified Deferred Items List accumulated across P1–P6.
For every item still with status `Open`:

- (a) **Resolve now.** PM provides the missing answer; status →
  `Closed`. The §4.NNN entry the DI relates to is updated.
- (b) **Accept deferral.** PM confirms the item is acceptable as
  unresolved with a documented reason; status → `Accepted`. The PRD
  §7 Open Items section will reflect it.
- (c) **Out of scope.** PM confirms the item is not part of this
  sub-PRD; status → `Closed` with `out-of-scope` reason. The PRD §3.2
  will reflect it.

**After Step 5, no items may remain `Open`.** This is enforced by the
gate's exit predicate — Step 6 cannot proceed while any item has
status `Open`.

---

## Step 6 — Explicit PM confirmation (APPROVE / REJECT / REDIRECT)

Only after Steps 1–5 pass cleanly:

> "I am satisfied we have comprehensive coverage of the core
> requirements and edge cases. Shall I proceed to final approval
> (P7)?"

PM responds with exactly one of:

- **APPROVE.** Gate emits `prd_phase_completed` with `phaseId: Gate`.
  Coordinator routes to [`phase-P7.md`](./phase-P7.md) (Final
  approval).
- **REJECT.** PM names the phase to restart from (any of P1–P6).
  Gate emits `prd_phase_rejected` with `phaseId: Gate`,
  `restartPhaseId: <named phase>`, and `rejectionReason: <verbatim
  PM utterance>`. Coordinator restarts at the named phase; downstream
  phases re-run if dependent. The reconciled coverage map snapshot is
  preserved and re-validated at the next gate run.
- **REDIRECT.** PM directs the coordinator to a different phase
  without rejecting (e.g. "I want to revisit P2 scope but not
  restart from P1"). Gate emits `prd_phase_redirected` with
  `phaseId: Gate`, `fromPhaseId: Gate`,
  `toPhaseId: <named phase>`, `redirectReason: <verbatim PM
  utterance>`. Coordinator routes to the named phase; downstream
  phases re-run only if the redirect outcome alters their inputs.

REJECT and REDIRECT both re-run this gate when the named phase exits
again. There is no separate second gate — APPROVE here is the only
path to P7.

---

## Cross-cutting protocols invoked (pointer only)

The gate applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family C — Deferred Items List.** Step 5 enforces the
  no-`Open`-items-past-the-gate rule (C3).
- **Family D — Conclusion gates.** D1 (every phase has a gate); D2
  (APPROVE / REJECT / REDIRECT); D3 (REJECT restarts the named
  phase); D4 (REDIRECT rewinds to any earlier phase).
- **Family H — Closure & thoroughness.** Step 4's §4 coverage map
  reconciliation is the explicit closure check.
- **Family B — Verbatim recording.** Step 6 PM responses recorded
  verbatim; REJECT / REDIRECT reasons are PM utterances, not
  paraphrases.

---

## Next phase

On Step 6 APPROVE → [`phase-P7.md`](./phase-P7.md) (Final approval).
On REJECT or REDIRECT, coordinator routes to the named phase per the
PM utterance; the gate re-runs at that phase's exit.
