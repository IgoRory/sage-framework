---
name: session-performance-evaluator
description: >
  Evaluates agent execution quality after every completed work cycle. Reads
  session telemetry and phase artifacts, scores the session across five
  dimensions, surfaces systematic violations as Linear issues for the Lead Dev,
  and writes a performance report. Use this skill after every work cycle
  completes (all phase issues reach Build Complete). Do not invoke during
  active build work -- wait for the cycle to close.
---

# Session Performance Evaluator

Reads workflow-telemetry.jsonl and phase artifacts after every work cycle.
Scores execution across five dimensions and identifies patterns, particularly
systematic violations where the same gate fires repeatedly against the same
agent. Produces a performance report and creates Linear issues for violations
that require human attention.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| workflow-telemetry.jsonl | [SESSION_ROOT]/ | Yes |
| Phase artifacts (S1-S8) | [SESSION_ROOT]/phase-N/ | Yes |
| Session manifest | [SESSION_ROOT]/session-manifest.md | Yes |
| Prior performance reports | [SESSION_ROOT]/performance-report-cycle-*.md | No (for trend detection) |

---

## Step 1 -- Read all inputs

Read workflow-telemetry.jsonl. Parse all events for the current cycle.
Read the session manifest to identify all phases in this cycle.
For each phase, read:
- phase-N-dev-interview-summary.md
- phase-N-implementation-plan.md
- phase-N-traceability-review.md
- tdd-results.md
- phase-N-code-review.md
- phase-N-test-results.md
- phase-N-completion-report.md (if exists)

---

## Step 2 -- Score each dimension

### Dimension A -- Step compliance

Check: all steps S1-S8 executed in correct sequence, all required artifacts
present, no steps skipped or combined.

OK: all steps in order, all artifacts present
Warning: one artifact missing or one anomalous step duration (>2x estimate)
  but no steps skipped
Fail: any step skipped, any two steps combined, or step sequence does not
  match manifest progression

Solo mode exception: S1 (dev interview) is not required in Solo mode.
Absence of the dev interview summary is not a compliance failure for Solo.

### Dimension B -- Hook discipline

Check hook rejections per step from telemetry:

OK: 0-1 rejections per step
Warning: 2-3 rejections of different types (agent probing, not repeating)
Fail: 3+ rejections of the same type on the same step (repeated attempts)

Rejection type interpretation:
- preToolUse during S1 (file write in Plan mode): serious -- fail if >1
- stop hook rejection at S8 (completion without test results): always fail,
  always creates a Linear violation issue
- Any other type: count and categorise

A rejection that fires once and is not repeated is healthy -- the hook
worked correctly. The concern is repetition of the same rejection.

### Dimension C -- TDD cycle quality

Check from tdd-results.md and telemetry:

RED discipline (test written before code):
  OK: all tasks show RED event before first GREEN attempt
  Warning: 1 task with ambiguous sequence (telemetry gap)
  Fail: any task where GREEN was attempted before RED confirmed failing

GREEN first-pass rate:
  OK: >= 70% of tasks pass GREEN on first attempt
  Warning: 50-69%
  Fail: < 50% (implementation plan was poorly formed)

REFACTOR completion rate:
  OK: >= 80% of tasks include REFACTOR step
  Warning: 60-79%
  Fail: < 60%

### Dimension D -- Gate bypass attempts

Check telemetry for any attempt to set validationConfirmed or
batches[N].confirmed via agent action (not via developer edit).

OK: no bypass attempts detected
Fail: any bypass attempt detected -- automatic fail, always creates a
  Linear violation issue regardless of other scores

### Dimension E -- Phase duration

Compare actual phase duration against the estimate in the manifest.

OK: within 25% of estimate
Warning: 25-50% over estimate
Fail: >50% over estimate OR phase abandoned without completion

---

## Step 3 -- Detect systematic violations

A systematic violation is one of:
- Same hook rejection type firing 3+ times on the same step in one phase
- Dimension D failure (gate bypass attempt)
- Same Fail pattern appearing across two consecutive cycles

Systematic violations always create a Linear issue.

---

## Step 4 -- Write performance report

Write to [SESSION_ROOT]/performance-report-cycle-[N].md:

``````markdown
# Session Performance Report -- Cycle [N]

**Session:** [session ID]
**Cycle:** [N]
**Date:** [ISO date]
**Phases evaluated:** [list]

## Overall: [OK / WARNING / FAIL]

| Dimension | Score | Notes |
|-----------|-------|-------|
| A - Step compliance | OK / WARNING / FAIL | [detail] |
| B - Hook discipline | OK / WARNING / FAIL | [rejection counts by type] |
| C - TDD quality | OK / WARNING / FAIL | [GREEN rate, REFACTOR rate] |
| D - Gate bypass attempts | OK / FAIL | [detail or "None detected"] |
| E - Phase duration | OK / WARNING / FAIL | [actual vs estimate] |

## Findings

[For each non-OK dimension: specific finding, what happened in telemetry,
what it indicates about agent behaviour or skill effectiveness]

## Trend

[If prior cycles exist: note whether scores are improving, stable, or
degrading compared to the last 3 cycles]

## Systematic violations

[List any systematic violations. If none: "None detected this cycle."]
Linear issues created: [list issue IDs or "None"]
``````

---

## Step 5 -- Create Linear issues for violations

For each systematic violation:

Create a Linear issue:
- Label: violation
- Title: "SAGE violation -- [dimension] -- [session ID] cycle [N]"
- Status: Needs Review
- Assignee: Lead Dev
- Description: paste the relevant finding from the performance report,
  including the specific telemetry events that triggered the violation

---

## Constraints

- Read only (except writing the performance report and creating Linear issues)
- Never modifies telemetry, manifests, skill files, or source code
- Invoke only after all phases in a cycle reach Build Complete
- Performance thresholds are guidance -- flag, do not auto-remediate

---

## Reference files

Read references/scoring-dimensions.md for:
- Detailed sub-criteria for each dimension
- Worked examples of OK / Warning / Fail conditions
- Telemetry event patterns for common violation types

