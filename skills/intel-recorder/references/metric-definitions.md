# Metric Definitions

Reference for intel-recorder. Defines each metric, its calculation
method, and how to handle edge cases.

---

## actualHours

Definition: total elapsed time the developer spent actively working
on the phase, excluding time blocked waiting for Foundation Verified.

Calculation:
  Read stepTimestamps from the session manifest.
  Sum: (S1.completedAt - S1.startedAt) + (S2.completedAt - S2.startedAt)
  + ... + (S8.completedAt - S8.startedAt) for all completed steps.
  For Dependent phases: subtract foundationWaitMinutes from S5 duration.
  Convert to hours (divide by 60).

Edge cases:
  If a step was started but not completed (phase abandoned): record
  actualHours as the time to the last completed step only.
  If timestamps are missing: record null and note in the record.

---

## foundationWaitMinutes

Definition: elapsed time between S4 completion and S5 start for
Dependent phases. Represents time the developer was blocked waiting
for Foundation Verified signal.

Calculation:
  phases[N].runtime.stepTimestamps.build.startedAt
  minus
  phases[N].runtime.stepTimestamps.plan-validation.completedAt
  in minutes.

Only applicable to Dependent phase type. Record null for Foundation
and Independent phases.

---

## tddGreenFirstPassRate

Definition: proportion of tasks where the GREEN (implementation)
phase passed on the first test run.

Calculation:
  Count tasks where GREEN attempt count = 1 (from tdd-results.md task table).
  Divide by total tasks.
  Round to 2 decimal places.

If tdd-results.md is missing or malformed: record null.

---

## refactorCompletionRate

Definition: proportion of tasks where a REFACTOR step was completed.

Calculation:
  Count tasks where REFACTOR column in tdd-results.md = PASS.
  Divide by total tasks.
  Round to 2 decimal places.

---

## s7TestPassRate

Definition: proportion of tests passing in the S7 agent testing run.

Calculation:
  Read "N passed" and "N failed" from phase-N-test-results.md.
  passed / (passed + failed).
  Round to 2 decimal places.

If STATUS: PASS and no individual test counts are available: record 1.00.
If STATUS: FAIL and no individual counts: record null.

---

## Hook rejection count

Definition: total hook rejections across all steps for this phase.

Source: phases[N].runtime.hookRejectionCount in the session manifest.
This field is incremented by the hook scripts on each rejection.

If null or absent: count manually from telemetry --
count all {event: "hook_rejection", phaseId: "N"} records.

