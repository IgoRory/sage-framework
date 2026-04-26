# Per-Skill Criteria — Skill Effectiveness Evaluator

Specific patterns to look for when evaluating each qualifying skill.
Read the relevant section before evaluating that skill. Each section
defines: what the skill is supposed to produce, what signals indicate
it is or isn't working, and how to formulate targeted change proposals.

---

## Table of contents

1. [prd-completeness-check](#prd-completeness-check)
2. [prd-interviewer](#prd-interviewer)
3. [phase-splitter](#phase-splitter)
4. [General change proposal guidance](#general-guidance)

---

## prd-completeness-check {#prd-completeness-check}

**What this skill is supposed to produce:**
PRDs that, when they reach `Ready` status, produce build sprints with
minimal gaps surfaced at the dev interview (S1), minimal traceability
review findings (S3), and minimal mid-build clarifications. A PRD
scoring 80+ should correlate with a clean build.

**Approver: the Product Manager**

---

### Pattern 1 — Threshold calibration

**What to measure:**
For each session, collect: PRD completeness score → S1 gap count
(number of questions surfaced in dev interview that were not in the PRD)
→ S3 Blocker + Major finding count → S6 Critical + Major finding count.

**Signal that threshold is too permissive (80 is too low):**
PRDs scoring 80–85 consistently produce S1 gap counts ≥ 3 or S3 Major
finding counts ≥ 4 per phase. If this pattern appears in 3+ sessions,
the threshold may need raising.

**Proposed change template:**
Raise threshold in SKILL.md Step 5 from 80 to [85/90] based on observed
correlation. Rationale: PRDs at [80–85] range produced an average of
[N] S1 gaps and [N] S3 Major findings across [N] sessions.

**Signal that threshold is too strict:**
PRDs consistently scoring 85–90 but producing very clean builds (S1 gap
count ≤1, S3 Major findings ≤1) may indicate the threshold is higher
than necessary, adding friction to the PRD process without quality benefit.

**Do not adjust threshold based on a single session.** Minimum 3 sessions
showing consistent directional signal before proposing a change.

---

### Pattern 2 — Dimension under-weighting

**What to measure:**
For each S1 gap and S3 finding, attempt to classify which completeness
dimension the gap corresponds to:
- Gap about requirement clarity → D1
- Gap about testable outcomes → D2
- Gap about error/empty states → D3
- Gap about component behaviour not in mockup → D5
- Gap about scope boundary → D6

**Signal that a dimension is under-weighted:**
If gaps in a specific dimension category appear in 4+ of the 5 sessions,
and the PRDs that passed had scores ≥10/15 (or ≥20/25 for D5) in that
dimension, the scoring criteria for that dimension may be too lenient.

**Proposed change template:**
Increase deduction amounts for specific finding types within the
under-weighted dimension. Example: if D3 error state gaps appear
repeatedly, increase the "functional area with no error state defined"
deduction from 3 to 4, or add a new deduction type for a specific
pattern not currently covered.

**D5 special attention:**
Component specification gaps are the highest-impact failure mode
identified in the retrospective. Pay particular attention to:
- Which of the six elements is most often missing across sessions
- Whether the minimum state table in the rubric is covering all
  component types that appear in Profitability features
- Whether the data binding criteria is catching insufficient specificity
  (e.g. "reads from API" passing when it should not)

---

### Pattern 3 — False negatives

**What to measure:**
A false negative is a PRD that scored ≥80 (PASS) but produced a
build with significant problems attributable to PRD quality, not
agent execution.

Distinguish PRD quality problems from agent execution problems:
- Agent execution: hook violations, TDD cycle failures, code review
  findings about code quality → not PRD quality issues
- PRD quality: S1 gaps about requirements not in PRD, S3 findings
  about requirements contradicted by the PRD, mid-build scope
  questions → PRD quality issues

**Signal:**
Two or more false negatives in 5 sessions is a meaningful pattern.
Examine the completeness reports for those PRDs — which dimensions
scored highest and which specific items passed that should not have.

**Proposed change:** Add or tighten specific scoring criteria in the
rubric for the dimension(s) that failed to catch the gap.

---

## prd-interviewer {#prd-interviewer}

**What this skill is supposed to produce:**
PRD drafts and component specification drafts that:
- Score ≥80 on the first `prd-completeness-check` run without
  significant revision
- Have no ⚠️ GAP markers remaining when submitted to the check
- Produce component specs where D5 scores ≥20/25

**Approver: the Product Manager**

---

### Pattern 1 — First-run pass rate

**What to measure:**
For each PRD produced by `prd-interviewer` in the 5 sessions, record:
- Did it pass on the first `prd-completeness-check` run?
- If not, how many dimensions failed?
- Which dimensions failed most frequently?

**Signal that the interviewer is missing questions:**
If the same dimension fails on first run across 3+ PRDs, the
corresponding interview phase is likely missing questions.

Cross-reference: which interview phase covers which dimension?
- P2 (functional scope) → D1 (requirement coverage)
- P7 (acceptance criteria) → D2 (AC specificity)
- P6 (edge/error states) → D3 (edge/error coverage)
- P9 (mockup confirmation) → D4 (mockup file completeness)
- P4+P5 (component inventory + spec) → D5 (component specification)
- P8 (out-of-scope) → D6 (out-of-scope clarity)

**Proposed change template:**
Add specific questions to the failing phase in `references/question-sets.md`.
The proposed questions should directly target the gap type that is
repeatedly failing — e.g. if D3 error states are failing, add questions
in P6 specifically about stored procedure error codes and data integrity
errors relevant to Profitability features.

---

### Pattern 2 — Component spec gap rate

**What to measure:**
For each component specification produced by `prd-interviewer`, count:
- Number of ⚠️ GAP markers remaining at submission
- Which of the six elements most frequently has gaps (by comparing
  D5 scoring findings against which element was missing)

**Signal:**
If the same element (e.g. Element 6 — data binding) is consistently
incomplete across 3+ sessions, the P5 questions for that element are
not probing deeply enough or the follow-up discipline for vague answers
is not triggering correctly.

**Proposed change template:**
Strengthen the relevant P5 question block or add to the vague answer
follow-up table for the specific answer type that is producing gaps.
Example: if data binding gaps are recurrent for Profitability calculation
components, add a specific follow-up for components involving calculated
values: "Is this value stored in Adjusted_GL or derived at query time?
If derived, what are the component fields and the calculation?"

---

### Pattern 3 — Parked item resolution rate

**What to measure:**
For each interview session, count the number of items that were parked
during the interview vs. the number that remained as ⚠️ GAP markers
in the final submitted PRD.

**Signal:**
If parked items consistently remain unresolved (high gap-to-park ratio),
either:
- The post-interview resolution step is not being completed (process
  adherence issue — note in report but do not propose a skill change)
- The park threshold is too low — questions are being parked that
  should be answerable during the interview with better framing

If the same questions are repeatedly parked across sessions, they may
be asking for information the PM doesn't have readily available. Propose
rephrasing those questions to be more accessible, or splitting them into
smaller questions that are easier to answer progressively.

---

## phase-splitter {#phase-splitter}

**What this skill is supposed to produce:**
Phase breakdowns that:
- Are accepted with minimal adjustment by the team at kick-off
- Produce independence scores that accurately predict parallel
  execution friction
- Generate effort estimates that correlate with actual step durations
  from telemetry

**Approver: Lead Dev**

---

### Pattern 1 — Team adjustment rate and direction

**What to measure:**
For each `phase-breakdown.md` produced in the 5 sessions, check the
"Changes from recommended breakdown" field in the Team confirmation
section. Record:
- How many phases were adjusted (merged, split, or reordered)
- Direction: merging (too granular) or splitting (too coarse)
- Reason given by the team (if recorded)

**Signal — consistently too granular (teams always merge phases):**
If teams merge phases in 3+ of 5 sessions, the minimum effort threshold
for a standalone phase (currently 2 hours) may be too low. Consider
raising to 3 hours, or tightening Rule 6 (merge threshold) in
`splitting-heuristics.md`.

**Signal — consistently too coarse (teams always split phases):**
If teams split phases in 3+ of 5 sessions, Rule 4 (complex component
boundary) may not be triggering aggressively enough, or the maximum
effort threshold (6 hours) may be too high.

**Signal — consistent reordering:**
If teams consistently reorder phases (changing tier assignments), the
dependency detection logic in splitting-heuristics.md may be missing
a common dependency pattern. Examine what dependency the team identified
that the skill missed — add it to the heuristics as a new pattern.

---

### Pattern 2 — Independence score prediction accuracy

**What to measure:**
For each phase, compare the independence score from the phase breakdown
against observed coordination friction in the telemetry:
- Did phases scored ≥90 actually run in parallel without friction?
- Did phases scored 60–89 produce the coordination overhead predicted?
- Did any phase scored ≥90 produce unexpected blocking (false high score)?

**Signal — false high scores:**
If phases scored ≥90 but produced coordination friction (parallel
execution significantly below theoretical maximum, interface contract
violations, cascade delays), the independence scoring is missing a
dependency type.

Examine what caused the friction — was it a file conflict, data
dependency, or interface gap not caught by the scoring rules? Add the
missing dependency type to the independence scoring table in
`splitting-heuristics.md` with an appropriate deduction value.

---

### Pattern 3 — Effort estimate accuracy

**What to measure:**
For each phase in each session, compare:
- Phase-splitter effort estimate (from phase breakdown manifest estimate)
- Actual phase duration (from telemetry: S1 start to S8 completion)

Calculate the mean absolute percentage error (MAPE) across all phases
in the 5 sessions.

**Signal thresholds:**
- MAPE ≤ 30%: estimates are well-calibrated, no change needed
- MAPE 31–50%: estimates are drifting, examine by work type
- MAPE > 50%: systematic calibration issue, propose base estimate
  revisions

**Directional breakdown:**
Separate over-estimates from under-estimates. If a specific work type
(e.g. complex stored procedures, Profitability calculation phases) is
consistently under-estimated, propose increasing the base estimate or
adjustment factor for that work type in `splitting-heuristics.md`.

**Profitability note:**
If calculation phases (FTP, capital, yield) are consistently
over-running, verify that the +30% calculation adjustment factor is
being applied. If it is being applied and phases still over-run by
>30%, propose increasing the factor to +45% or +50%.

---

## General change proposal guidance {#general-guidance}

### What makes a good proposed change

A good proposed change is:
- **Targeted:** Changes the minimum text necessary to address the
  pattern. Does not rewrite sections unrelated to the observed gap.
- **Evidence-backed:** References specific sessions and specific data
  points, not general impressions.
- **Testable:** States an expected outcome that can be measured in
  future sessions. "This should reduce S1 gap count for D3 from an
  average of 3.2 to ≤1.5 per phase."
- **Reversible:** Small enough that if it turns out to be wrong, it
  can be reverted without cascading effects.

### What makes a poor proposed change

- Rewriting an entire question set because one question was weak
- Changing a scoring dimension because of a single session anomaly
- Proposing to add complexity (more dimensions, more questions) when
  the evidence points to a precision problem in existing criteria
- Proposing changes to multiple skills simultaneously based on a
  pattern that could be explained by a single session's unusual feature

### Confidence calibration

**High confidence (4–5 sessions showing pattern):**
The pattern is reliable. Propose the change directly.

**Medium confidence (3 sessions showing pattern):**
The pattern is plausible but not certain. Propose the change with a
note: "Medium confidence — recommend monitoring for 2 further sessions
to confirm before applying if there is any doubt."

**Low confidence (1–2 sessions):**
Do not propose a change. Record the finding in the Notion report under
"Low confidence findings." If the same pattern appears in the next
evaluation cycle's data, confidence will rise.

### Proposed change scope limits

To prevent the skills from drifting significantly in a single cycle,
apply these limits per skill per evaluation cycle:

- Maximum 3 proposed changes per skill per cycle
- No change to threshold values by more than 5 points in a single cycle
- No addition of more than 2 new questions to any interview phase
- No addition of more than 2 new deduction types to any scoring dimension
- No removal of existing questions or deduction types (additions only —
  removals require explicit human judgment, not automated proposal)
