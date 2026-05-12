# Per-Skill Criteria

Reference for skill-effectiveness-evaluator. Detailed signal patterns,
evidence thresholds, and diff scope guidance for each skill.

---

## Evidence thresholds

Do not propose a diff unless:
- At least 3 invocations of the skill are in telemetry
- The underperformance pattern appears in at least 3 consecutive cycles
  (not just one anomalous cycle)
- The pattern is specific enough to point to a single targeted change

A single bad cycle is noise. Three consecutive cycles with the same
pattern is signal.

---

## prd-completeness-check

Signals that indicate a diff is warranted:
- The same dimension scores 0 or near-0 across 3+ consecutive PRD
  assessments, with different PRDs (same PRD failing repeatedly is
  a PRD quality issue, not a skill issue)
- The same finding type appears in every assessment (e.g., every PRD
  fails D2 for the same reason -- AC specificity is ambiguous in the rubric)
- Lead Dev or Product Manager feedback (via Linear issue comments)
  that a finding was incorrectly scored

Diff scope:
  Change the specific sub-criteria or example in the scoring rubric.
  Do not change point values or add/remove dimensions without strong
  evidence and Product Manager approval.
  Maximum diff scope: one dimension's rubric section.

---

## prd-interviewer

Signals that indicate a diff is warranted:
- S3 traceability review Blocker findings consistently reference
  a PRD section type that maps to a specific question phase (P1-P9)
  in the question set
- The same PRD section is missing across multiple features --
  the question that should elicit it is either absent or insufficiently
  specific

How to map Blocker categories to question phases:
  Calculation logic Blockers -> check P2 (calculation changes)
  Allocation methodology Blockers -> check P3 (allocation changes)
  Acceptance criteria Blockers -> check P4 (AC section)
  UI/component Blockers -> check P5b (UI/UX section)
  Edge case Blockers -> check P6 (edge cases)

Diff scope:
  Add or strengthen one question in the relevant phase.
  Do not restructure the question set or change the interview flow.

---

## phase-splitter

Signals that indicate a diff is warranted:
- Phases consistently over 8 hours actual in the same layer type
  (splitting rule for that layer is too permissive)
- Phases consistently under 1 hour actual (merge rule is not triggering)
- foundation-verified-gate rejections on phases that should have been
  Independent (dependency detection missed a case)
- File ownership conflicts discovered during build (two phases modified
  the same file -- the Rule 2 conflict resolution was not triggered)

Diff scope:
  Add or tighten a specific splitting rule.
  Adjust a specific independence scoring deduction value.
  Do not change the overall splitting rule priority order.

---

## kickoff-dev-review

Signals that indicate a diff is warranted:
- High ADDRESSED_IN_PRD count at kick-off (5+ concerns closed as
  "already covered") followed by Blocker findings at S3 on the
  same topic areas -- concerns were closed without verification
- CODEBASE_CONFLICT concerns that were not surfaced to the team
  immediately (they appear in the transcript but were not flagged)

Diff scope:
  Add a verification step to the ADDRESSED_IN_PRD handling.
  Add a specific codebase pattern to the CODEBASE_CONFLICT detection.

---

## Evidence quality

A high-quality diff proposal includes:
1. Specific telemetry event sequences or artifact text that shows the problem
2. The exact text being changed and why it is causing the observed behaviour
3. A clear description of how the proposed change prevents the pattern
4. An estimate of which cycle the improvement should be visible in

A low-quality proposal (likely to be rejected):
- "The skill seems to underperform sometimes -- add more detail."
- Changes that restructure the file without addressing a specific pattern
- Changes that expand the skill's scope beyond its designed purpose

