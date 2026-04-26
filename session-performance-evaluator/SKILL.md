---
name: session-performance-evaluator
description: >
  Evaluates agent execution quality after a completed Sprint, Pair,
  or Solo work cycle. Runs automatically when all phase issues in a Linear
  session reach Build Complete status. Reads workflow-telemetry.jsonl and
  all phase artifacts to produce a session performance report posted to the
  Notion session page. Flags systematic hook violations as Linear issues
  assigned to the Lead Dev. Does not require manual invocation — triggered by the
  stop hook on the final phase completion. Background, readonly agent.
---

# Session Performance Evaluator

Evaluates agent execution quality for a completed work cycle. Produces a
session performance report and flags any systematic issues that should be
resolved before the next session of the same type starts.

**Operating constraints:**
- Background agent — runs without blocking any active work
- Readonly — never writes to the codebase or modifies session artifacts
- Only write operations: posting to Notion, creating Linear issues for
  systematic violation flags
- Triggered automatically — never invoked manually

---

## Trigger condition

This skill is invoked by the `stop` hook when all phase Linear issues
in the current session are at status `Build Complete`. The hook passes:
- `session_id` — the session identifier from the manifest
- `session_root` — the file system path to the session directory
- `linear_project_id` — the Linear project for this session

Do not run if any phase issue is not yet at `Build Complete`. If called
prematurely, log the condition and exit silently.

---

## Step 1 — Load session data

Load all of the following. If any file is missing, note it in the report
as a data gap and continue with available data — do not abort.

**From the file system:**
- `[SESSION_ROOT]/workflow-telemetry.jsonl` — all hook events
- `[SESSION_ROOT]/session-manifest.md` — planned phase breakdown,
  effort estimates, tier structure, dependency ordering
- `[SESSION_ROOT]/phase-N/` for each phase:
  - `phase-N-dev-interview-summary.md`
  - `phase-N-implementation-plan.md`
  - `phase-N-traceability-review.md`
  - `phase-N-tdd-results.md`
  - `phase-N-code-review.md`
  - `phase-N-test-results.md`
  - `phase-N-completion-report.md`

**From Linear (via MCP):**
- All phase issues for this session: actual start time, approval time,
  Build Complete time, any comments added during execution

---

## Step 2 — Parse telemetry

From `workflow-telemetry.jsonl`, extract per-phase, per-step records.

Build a step duration table for each phase:

| Phase | Step | Start | End | Duration (min) | Estimated (min) | Delta |
|---|---|---|---|---|---|---|

Calculate duration as the time between the step's entry event and the
next step's entry event (or the `stop` event for S8).

Extract all hook rejection events. For each rejection record:
- `hook_event_name`
- `active_agent`
- `tool_name` (the tool call that was rejected)
- `rejection_reason`
- `step` (derived from `manifest.currentStep` at event time)
- `phase`

Group rejections by: phase, step, hook type, and agent.

Extract all TDD cycle events. For each RED-GREEN-REFACTOR cycle:
- `phase`
- `task_id` (from implementation plan)
- `red_attempts` (how many times RED was run before GREEN was attempted)
- `green_attempts` (how many times GREEN was run before passing)
- Whether REFACTOR was completed

---

## Step 3 — Evaluate per-phase performance

For each phase, evaluate across five dimensions. Read
`references/scoring-dimensions.md` for detailed criteria and thresholds.

**Dimension A — Step compliance**
Did all steps execute in the correct order with required artifacts
produced? Check manifest step status progression against telemetry
event sequence.

**Dimension B — Hook discipline**
How many hook rejections occurred per step? A rejection indicates an
agent attempted a disallowed action — the hook did its job, but
repeated rejections on the same step suggest the agent's system prompt
needs refinement.

**Dimension C — TDD cycle quality**
RED failure rate per task, GREEN first-pass rate, REFACTOR completion
rate. High RED failure rates on first attempt are expected and healthy —
they confirm tests were written before implementation. Multiple RED
attempts on the same task after GREEN was attempted signal the
implementation plan was ambiguous.

**Dimension D — Review finding rates**
Traceability review (S3) finding counts by severity. Code review (S6)
finding counts by severity. High finding rates are not inherently
bad — they mean the review agents are working. The signal is whether
the same finding categories repeat across phases, which suggests a
systematic gap in the implementation planning.

**Dimension E — Effort accuracy**
Actual step duration vs. manifest estimate. Variance within ±30% is
normal. Variance > 50% in either direction is flagged. Consistent
over-estimation or under-estimation across phases suggests the
effort estimation heuristics need calibration.

---

## Step 4 — Evaluate cross-phase performance

Assess how the phases interacted as a system:

**Dependency ordering:**
Did phases start in the correct tier order? Did any Tier 1 phase start
before its Tier 0 upstream posted a completion report? (Should be
structurally prevented by Linear gates — if it happened anyway, flag
as a gate configuration issue.)

**Parallel execution:**
Did Tier 0 phases actually run in parallel, or did they serialise?
Calculate the overlap window: the period during which multiple phase
lanes had active telemetry events simultaneously. Low overlap suggests
coordination friction or resource constraints worth noting.

**Interface contract adherence:**
For phases with downstream dependencies, check whether the upstream
phase's completion report explicitly confirmed the interface contract
outputs were produced as specified in the phase breakdown.

**Cascade effects:**
Did any rework event in one phase (a step that had to be re-run) cause
a delay in a downstream phase's start time?

---

## Step 5 — Identify systematic violations

A systematic violation is defined as any of:

- The same hook type rejected by the same agent 3 or more times within
  a single session
- A required artifact missing at step gate for 2 or more phases in the
  same session (suggesting a manifest configuration issue, not a
  one-off agent failure)
- A step executing out of order in 2 or more phases
- A TDD REFACTOR step skipped in more than 50% of tasks across the
  session

For each systematic violation identified:
- Create a Linear issue:
  - Title: `Systematic violation — [violation type] — [session ID]`
  - Assignee: Lead Dev
  - Status: `Needs Review`
  - Priority: High
  - Label: `workflow-violation`
  - Description: violation type, frequency, affected phases, affected
    agent, relevant telemetry excerpts, suggested root cause
- Add a note to the session performance report linking the Linear issue

A session with one or more systematic violation flags should not start
a new Sprint session of the same type until the Lead Dev has reviewed
and closed or dismissed the flag. Note this constraint in the report.

---

## Step 6 — Produce the session performance report

Post to the Notion session page as a child page titled:
`Session Performance Report — [session ID] — [feature title]`

Use exactly this structure:

```
# Session Performance Report

Session:   [session ID]
Feature:   [feature title]
Mode:      [Sprint / Pair / Solo]
Completed: [ISO datetime]
Phases:    [N]

---

## Summary scorecard

| Phase | A: Compliance | B: Hook discipline | C: TDD quality | D: Review findings | E: Effort accuracy |
|---|---|---|---|---|---|
| Phase 1 | [✅ / ⚠️ / ❌] | [✅ / ⚠️ / ❌] | [✅ / ⚠️ / ❌] | [✅ / ⚠️ / ❌] | [✅ / ⚠️ / ❌] |
...

✅ = within normal range  ⚠️ = notable, worth monitoring  ❌ = anomaly

---

## Cross-phase assessment

**Dependency ordering:** [✅ held as designed / ⚠️ minor deviation / ❌ violation — details]
**Parallel execution:** [overlap window, % of theoretical maximum]
**Interface contract adherence:** [✅ all confirmed / ⚠️ gaps noted — details]
**Cascade effects:** [none / details if any]

---

## Step duration detail

| Phase | Step | Estimated | Actual | Delta | Flag |
|---|---|---|---|---|---|
...

---

## Hook rejection detail

| Phase | Step | Hook | Agent | Tool | Reason | Count |
|---|---|---|---|---|---|---|
...

[If no rejections: "No hook rejections recorded."]

---

## TDD cycle detail

| Phase | Task | RED attempts | GREEN attempts | REFACTOR completed |
|---|---|---|---|---|
...

---

## Top findings

[3–5 most significant observations from this session, in plain language.
Each finding includes: what was observed, why it matters, and a specific
actionable suggestion directed at one of: workflow config, sub-agent
system prompt, or upstream PRD/phase breakdown quality.]

1. [Finding]
   Observation: [what the data shows]
   Significance: [why it matters]
   Suggestion: [specific action — who should do what]

2. ...

---

## Systematic violations

[If none: "No systematic violations identified."]

[If any:]
⚠️ [Violation type] — Linear issue [LIN-XXX] created, assigned to the Lead Dev
[Description of violation]

---

## Data gaps

[Any missing telemetry files or artifacts that limited this evaluation.
If none: "Complete data — no gaps."]
```

---

## Reference files

Read `references/scoring-dimensions.md` for:
- Detailed thresholds for each scoring dimension (A–E)
- What constitutes ✅ / ⚠️ / ❌ for each
- How to handle incomplete telemetry
- Profitability-specific interpretation notes
