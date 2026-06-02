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

**Pattern:** For several `linearIssueId` values, **`prd_phase_completed`** never appears for a given **`phaseId`** (e.g. P6 missing for UI-heavy features), OR the phase completed but `coverageDimensions` shows D-PRED unsatisfied for that phase.

**Interpretation:** Either the section mapping/conditional logic is wrong (phase not run), or the phase ran but did not produce testable predicates. In the first case, add or sharpen questions in the corresponding per-section file under **`prd-interviewer/references/question-sets/`**. In the second case, strengthen the probing guidance or depth indicator for the affected category.

### Abandonment / stalls

**Pattern:** Large delta between `prd_phase_started` and `prd_phase_completed` timestamps, or interviews that stop without `prd_interview_completed`.

**Interpretation:** Parking / pacing guidance in SKILL may need clarification.

---

## Understanding-quality signals

These signals use `coverageDimensions` fields from `prd_phase_completed` events and
the structure of `interview-answers.json` to detect quality problems that question
count cannot surface.

### Vague-predicate signal

**Pattern:** completeness-check D2 (AC specificity) failures correlated with
`prd_phase_completed` events where `coverageDimensions.D-PRED` is `false` or absent
for one or more phases.

**Interpretation:** The interviewer accepted vague answers without establishing
testable predicates. Strengthen probing guidance or the depth indicator for the
affected section in the corresponding per-section file under
**`prd-interviewer/references/question-sets/`**.

### Thin-edge-case signal

**Pattern:** traceability-review Blockers in the "Edge cases / constraints" theme
correlated with phases where `coverageDimensions.D-EC` reports fewer than 5 of 7
categories satisfied at `prd_phase_completed` for P7.

**Interpretation:** The edge-case phase was too shallow. Strengthen the challenger
probe guidance for the under-covered EC categories in
**`prd-interviewer/references/question-sets/section-7-edge-cases.md`**.

### No dynamic follow-up signal

**Pattern:** A `prd_phase_completed` event where the corresponding
`interview-answers.json` contains only canonical `Q[section]` IDs and zero
`Q[section].DYN-N` entries for that phase, correlated with D-PRED failures for that
phase.

**Interpretation:** The interviewer ran the canonical questions but never generated
follow-up questions grounded in the PM's answers. The depth indicators or probing
language in the affected category need strengthening.

### Surface-only-interview signal

**Pattern:** A `prd_phase_completed` event for P6 (Section 5b — UI) where
`coverageDimensions.D-COMP` is satisfied but `coverageDimensions.D-DETAIL` is `false`
or absent.

**Interpretation:** The interviewer captured what the component does (functional
description, states) but not what it says (label text, tooltip copy, placeholder text,
empty-state message). The PRD will require re-interview before completeness check can
pass the UI-detail scoring. Correlate micro-detail gaps with completeness-check D4
(UI component specification) failures. Correlate D3 (Demo bundle completeness) only
when the evidence is missing or malformed demo artifacts, and do not use D5
(Out-of-scope clarity) as a UI-detail signal. Propose strengthening the D-DETAIL
comprehensiveness checklist in
**`prd-interviewer/references/question-sets/section-5-ui-and-ux.md`** for the
Component Inventory and State Models categories.

### Stenographer signal

**Pattern:** A phase where `coverageDimensions.D-RATIONALE` is `false` or absent
across multiple non-obvious design choices, combined with a ratio of DYN-N follow-up
IDs to canonical Q-IDs below 0.3 for that phase across multiple interview runs.

**Interpretation:** The interviewer recorded PM answers without challenging them. No
"why" questions were asked; no alternatives were surfaced. PRDs from these interviews
are at elevated risk of scope-change rework during build because incidental decisions
were treated as deliberate requirements. Propose adding explicit challenger-probe
reminders to the SKILL conclusion gate or to the affected section's depth indicator in
the corresponding per-section file under
**`prd-interviewer/references/question-sets/`**.

### Missing-cross-impact signal

**Pattern:** A phase that satisfies D-PRED for a feature touching shared entities (SPs
consumed by multiple features, data shown on multiple screens) but where
`coverageDimensions.D-CROSS` is `false` or absent.

**Interpretation:** Side effects were not traced. Correlated with traceability-review
Blockers in "Scope / boundaries" or "UI / component behaviour" themes. Propose
strengthening the cross-page impact check reminder in Section 5b and the D-CROSS
guidance in **`references/complexity-classifier.md`**.

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

If Blockers recur for a theme **not** covered by existing probing in the corresponding per-section file under **`prd-interviewer/references/question-sets/`**, propose **one** targeted question or probe note.

---

## Diff scope rules

- Prefer **one** new probe or question clause over restructuring the interview.
- Do not change Notion / Linear operational steps unrelated to the observed gap.
- Coordinate with **`skill-effectiveness-evaluator`**: it must **skip** **`prd-interviewer`** while this evaluator is deployed.
