# Scoring Dimensions -- Detailed Sub-criteria

Reference for session-performance-evaluator. Contains worked examples
and telemetry event patterns for each dimension.

---

## Dimension A -- Step compliance: telemetry patterns

A compliant S1->S2 transition in telemetry looks like:
  {event: "afterFileEdit", filePath: "phase-1-dev-interview-summary.md"}
  followed by
  {event: "preToolUse", toolName: "write_file", ...} (implementation plan)

A skipped step looks like:
  {event: "afterFileEdit", filePath: "phase-1-implementation-plan.md"}
  with NO preceding dev-interview-summary event in this session.

A combined step looks like:
  Two artifact files written within the same tool call sequence
  without the expected intervening developer action.

---

## Dimension B -- Hook discipline: rejection patterns

Healthy rejection (fires once, not repeated):
  {event: "hook_rejection", hook: "plan-mode-enforcer", phaseId: "1"}
  followed by no further plan-mode-enforcer rejections for phase 1.
  Interpretation: agent tried once, was redirected, complied. OK.

Systematic rejection (same hook, same phase, 3+ times):
  {event: "hook_rejection", hook: "validation-confirmed-gate", phaseId: "2"}
  {event: "hook_rejection", hook: "validation-confirmed-gate", phaseId: "2"}
  {event: "hook_rejection", hook: "validation-confirmed-gate", phaseId: "2"}
  Interpretation: agent is repeatedly attempting to start build without
  developer confirmation. System prompt for the build step needs revision.
  Flag as FAIL.

Stop hook rejection (always serious):
  {event: "hook_rejection", hook: "completion-report-stop-gate", phaseId: "1"}
  Interpretation: agent tried to end its turn without test results passing.
  This is the most serious rejection type. Always FAIL. Always Linear issue.

---

## Dimension C -- TDD quality: calculation examples

Example session with 5 tasks:
  Task 1: RED confirmed, GREEN on attempt 1, REFACTOR done
  Task 2: RED confirmed, GREEN on attempt 2, REFACTOR done
  Task 3: RED confirmed, GREEN on attempt 1, REFACTOR done
  Task 4: RED confirmed, GREEN on attempt 1, REFACTOR done
  Task 5: RED confirmed, GREEN on attempt 3, REFACTOR skipped

GREEN first-pass rate: 3/5 = 60% -- Warning
REFACTOR completion rate: 4/5 = 80% -- OK
Overall C score: Warning (driven by GREEN rate)

Low GREEN first-pass rate indicates the implementation plan (S2) was
insufficiently specific. The implementation-planner agent system prompt
or the dev interview questions may need refinement.

Low REFACTOR rate indicates the code-simplifier agent is not completing
its pass, or that tasks are too small to warrant refactoring. Check
code-simplifier telemetry for reverts.

---

## Dimension D -- Gate bypass: detection

Gate bypass attempts appear in telemetry as:
  {event: "afterFileEdit", filePath: "session-manifest.md",
   content_contains: "validationConfirmed": true}
  where the edit timestamp is within an agent session (not a developer
  edit -- developer edits occur outside of hook event sequences).

How to distinguish agent edit from developer edit:
  Agent edits appear inside hook event sequences (preceded and followed
  by preToolUse or afterFileEdit events with tool context).
  Developer edits typically appear as isolated afterFileEdit events
  without surrounding tool context.

If ambiguous: flag as Warning rather than Fail, note in the report,
and ask the Lead Dev to confirm whether the edit was manual.

---

## Dimension E -- Duration: interpretation

A phase that runs significantly over estimate often indicates:
  - Implementation plan was insufficiently detailed (S2 quality issue)
  - Phase scope was too broad (splitting issue)
  - Developer was blocked waiting for a Foundation phase (expected)
  - Unexpected codebase complexity discovered during build

A phase that runs significantly under estimate may indicate:
  - Steps were combined or skipped (check Dimension A)
  - Estimate was too conservative (adjust intel-recorder baseline)
  - Phase scope was too narrow (consider merging with adjacent next time)

Phases blocked waiting for Foundation Verified are expected to show
extended elapsed time between S4 completion and S5 start. This is
not a duration failure -- exclude the wait time from the calculation
when the phase is Dependent type.

