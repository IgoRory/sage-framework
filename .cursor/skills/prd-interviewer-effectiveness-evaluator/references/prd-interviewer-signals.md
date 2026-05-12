# PRD interviewer — evaluation signals

Reference for **`prd-interviewer-effectiveness-evaluator`**. Telemetry field names align with **`prd-interviewer`** SKILL (`workflowKind: "prd_interview"`).

---

## Evidence thresholds

Do **not** propose a SKILL diff unless:

- At least **3** completed interview runs appear in PRD JSONL (`prd_interview_completed` and/or distinct `prdRunId`), **and**
- The same pattern appears across **multiple** runs (not a single outlier), **and**
- The fix is **one** targeted addition or clarification (question, gate language, or telemetry instruction).

---

## Telemetry-derived signals

### Preflight discipline

**Pattern:** `prd_preflight` with `preflightOutcome: fail`, then later events show P1–P9 progression **without** `override: true` on a subsequent `prd_preflight`.

**Interpretation:** Step 0 gate may be ignored — strengthen SKILL enforcement language or require explicit PM acknowledgment in transcript.

### Phase coverage

**Pattern:** For several `linearIssueId` values, **`prd_phase_completed`** never appears for a given **`phaseId`** (e.g. P6 missing for UI-heavy features).

**Interpretation:** Section mapping or conditional logic may be wrong — add or sharpen questions in **`references/question-sets.md`** for that phase.

### Abandonment / stalls

**Pattern:** Large delta between `prd_phase_started` and `prd_phase_completed` timestamps, or interviews that stop without `prd_interview_completed`.

**Interpretation:** Parking / pacing guidance in SKILL may need clarification.

---

## Traceability review mapping (optional input)

When **`phase-*-traceability-review.md`** exists, map Blocker themes to interview phases:

| Blocker theme | Check phaseId / section |
|---------------|-------------------------|
| Calculation logic | P2 — Section 2 |
| Allocation methodology | P3 — Section 3 |
| Acceptance criteria | P4 — Section 4 |
| UI / component behaviour | P6 — Section 5b |
| Edge cases / constraints | P7 — Section 6 |
| Scope / boundaries | P5 — Section 5a |

If Blockers recur for a theme **not** covered by existing probing in **`question-sets.md`**, propose **one** targeted question or probe note.

---

## Diff scope rules

- Prefer **one** new probe or question clause over restructuring the interview.
- Do not change Notion / Linear operational steps unrelated to the observed gap.
- Coordinate with **`skill-effectiveness-evaluator`**: it must **skip** **`prd-interviewer`** while this evaluator is deployed.
