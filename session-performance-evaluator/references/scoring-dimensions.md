# Scoring Dimensions — Session Performance Evaluator

Detailed thresholds for dimensions A–E. Read before scoring any phase.

---

## Dimension A — Step compliance

**What it checks:**
- All steps S1–S8 executed in correct sequence
- Required artifact exists for each step gate
- No step skipped or combined with another
- Manifest step status matches telemetry event sequence

**Thresholds:**
- ✅ All steps completed in order, all artifacts present
- ⚠️ One artifact missing or one step with anomalous duration (>2x estimate)
  but no steps skipped or out of order
- ❌ Any step skipped, any two steps combined, or step sequence does not
  match manifest progression

**Special case — Solo mode:**
S1 (dev interview) is not required in Solo mode. Absence of the dev
interview summary is not a compliance failure in Solo sessions.

---

## Dimension B — Hook discipline

**What it checks:**
Number and type of hook rejections per step per phase.

**Thresholds per step:**
- ✅ 0–1 rejections
- ⚠️ 2–3 rejections of different types (agent is probing boundaries,
  not repeatedly attempting the same blocked action)
- ❌ 3+ rejections of the same type on the same step (agent repeatedly
  attempting a disallowed action — system prompt needs refinement)

**Rejection type interpretation:**
- `preToolUse` rejection during S1 (dev interview): agent attempted to
  write files during Plan mode — serious, flag as ❌ if more than once
- `beforeShellExecution` rejection during S5 (build): most likely a
  required reference file not yet read — check which file and whether
  it was subsequently read before build proceeded
- `stop` hook rejection at S8: agent attempted completion report without
  test results — most serious violation, always ❌, always contributes
  to systematic violation check

**Note:** A rejection that fires once and is not repeated indicates the
hook worked correctly — the agent was redirected and complied. This is
healthy behaviour. The concern is repetition.

---

## Dimension C — TDD cycle quality

**What it checks:**
- RED written before GREEN attempted (confirmed by telemetry sequence)
- GREEN first-pass rate
- REFACTOR completion rate
- Multiple RED attempts on same task after GREEN was previously attempted

**Thresholds:**

RED discipline (tests written before code):
- ✅ All tasks: RED event precedes first GREEN attempt in telemetry
- ⚠️ 1 task where sequence is ambiguous (telemetry gap)
- ❌ Any task where GREEN was attempted before RED was confirmed failing

GREEN first-pass rate (implementation quality signal):
- ✅ ≥70% of tasks pass GREEN on first attempt
- ⚠️ 50–69% first-pass rate
- ❌ <50% first-pass rate (implementation plan was poorly formed)

REFACTOR completion:
- ✅ ≥80% of tasks include REFACTOR step
- ⚠️ 60–79% REFACTOR completion
- ❌ <60% REFACTOR completion (code quality risk)

**Interpretation note:**
Low GREEN first-pass rate is the most actionable signal. It correlates
directly with implementation plan quality (S2). If a phase has ❌ on
GREEN first-pass rate, check the implementation plan for:
- Ambiguous TDD scenario descriptions
- Missing edge case scenarios that emerged during build
- Incorrect file-to-scenario mapping

This finding should surface in the session report as a suggestion to
improve the implementation plan sub-agent system prompt.

---

## Dimension D — Review finding rates

**What it checks:**
Finding counts from S3 (traceability review) and S6 (code review),
broken down by severity. Pattern of finding categories across phases.

**Traceability review (S3) thresholds:**
- ✅ Zero Blocker findings, ≤2 Major findings per phase
- ⚠️ Zero Blocker, 3–5 Major findings — review agent working hard,
  may indicate implementation plan gaps
- ❌ Any unresolved Blocker finding at S4 gate (gate should have
  prevented progression — if it didn't, flag as gate configuration issue)

**Code review (S6) thresholds:**
- ✅ Zero Critical findings, ≤3 Major findings per phase
- ⚠️ Zero Critical, 4–6 Major findings
- ❌ Any Critical finding (gate should have blocked S7 — if it didn't,
  flag as gate configuration issue)

**Cross-phase pattern check:**
If the same finding category appears in S3 or S6 across 3 or more phases
in the same session, it is a systematic pattern, not a phase-specific issue.

Common Profitability-specific patterns to watch for:
- Repeated S3 findings about missing ProcessID boundary handling →
  suggests prd-completeness-check D3 is not catching this
- Repeated S6 findings about stored procedure error handling →
  suggests the implementation plan sub-agent is not including
  SP error handling in its TDD scenario generation
- Repeated S6 findings about Adjusted_GL field null handling →
  suggests component spec data binding entries are not specifying
  nullability

Record cross-phase patterns as Top Findings in the report with a
suggestion directed at the upstream skill (completeness check,
interviewer, or implementation plan agent).

---

## Dimension E — Effort accuracy

**What it checks:**
Actual step durations vs. phase-splitter estimates from the manifest.

**Thresholds:**
- ✅ Actual total phase duration within ±30% of manifest estimate
- ⚠️ Actual total phase duration ±31–50% of manifest estimate
- ❌ Actual total phase duration >50% over or under manifest estimate

**Step-level flags (regardless of overall phase rating):**
Any individual step where actual duration is >2x the estimate is flagged
in the step duration detail table, even if the overall phase is ✅.

**Directional interpretation:**
- Consistent over-runs (actual > estimate) across most phases →
  effort estimation heuristics are systematically low; suggest
  adjusting base estimates in phase-splitter splitting-heuristics.md
- Consistent under-runs across most phases →
  estimates are conservative; less urgent but worth noting
- Mixed (some phases over, some under) with no pattern →
  normal variance, no action needed

**Profitability-specific note:**
Phases involving Profitability calculation logic (FTP, capital, yield,
RAROC) consistently run longer than general heuristics predict. If a
calculation phase over-runs by >50%, check whether the +30% calculation
adjustment factor was applied in the phase breakdown. If it wasn't,
note the oversight in the report.

---

## Handling incomplete telemetry

If `workflow-telemetry.jsonl` is missing events for a step (gap in the
record), apply these rules:

- Missing step entry event: cannot calculate step duration — mark as
  `N/A` in duration table, do not flag as ❌
- Missing hook events for a step: assume 0 rejections for that step —
  note the data gap in the report
- Missing TDD cycle events for a task: mark that task as `N/A` in TDD
  detail, do not count toward pass/fail rates
- If more than 30% of expected telemetry events are missing across the
  session: note prominently in Data Gaps section; overall session
  evaluation reliability is reduced — add disclaimer to report summary
