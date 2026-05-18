---
name: intel-recorder
description: >
  Records delivery metrics to .sage/intel/ after every completed work cycle.
  Captures velocity, phase duration, hook rejection rates, and build mode
  effectiveness per workflow mode (Mob/Sprint/Pair/Solo). Maintains separate
  datasets per mode for accurate per-mode calibration. Optionally publishes
  to Notion dashboard if configured. Use after every cycle close -- do not
  invoke during active build work.
---

# Intel Recorder

Part of the SAGE Intel subsystem. Records structured delivery metrics
after every work cycle to support capacity planning and velocity
calibration. All metrics are written to `.sage/intel/` as the canonical
store. Optionally publishes to Notion dashboard if `intel.notionPublishEnabled`
is true in workflow-config.json. Maintains separate per-mode datasets --
Sprint velocity data is never mixed with Mob or Pair data.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| Session manifest | [SESSION_ROOT]/session-manifest.md | Yes |
| Phase artifacts (completion reports, test results, code review) | [SESSION_ROOT]/phase-N/ | Yes |
| workflow-telemetry.jsonl | [SESSION_ROOT]/ | Yes |
| prd-interview-telemetry.jsonl | `.sage/prd-interview-telemetry.jsonl` (path from `workflow-config.json`) | Yes |
| phase-{N}-tdd-results.md per phase | [SESSION_ROOT]/phase-{N}/ | Yes |

---

## Metrics to record per completed phase

| Metric | Source | Notes |
|--------|--------|-------|
| Session ID | Manifest | |
| Phase ID | Manifest | |
| Mode | Manifest sessionState | mob/sprint/pair/solo |
| Layer | Manifest phase definition | database/api/ui/data-library/full-stack |
| Phase type | Manifest phase definition | foundation/independent/dependent |
| Estimated hours | Manifest phase definition | From phase-splitter output |
| Actual hours | Manifest runtime.actualDurationHours | |
| Build mode | Manifest runtime.buildMode | autonomous/checkpoint |
| S1 duration (minutes) | Manifest stepTimestamps | |
| S2 duration (minutes) | Manifest stepTimestamps | |
| S3 duration (minutes) | Manifest stepTimestamps | |
| S4 duration (minutes) | Manifest stepTimestamps | |
| S5 duration (minutes) | Manifest stepTimestamps | |
| S6 duration (minutes) | Manifest stepTimestamps | |
| S7 duration (minutes) | Manifest stepTimestamps | |
| Hook rejection count | Manifest runtime.hookRejectionCount | |
| TDD GREEN first-pass rate | phase-{N}-tdd-results.md | |
| REFACTOR completion rate | phase-{N}-tdd-results.md | |
| S7 test pass rate | phase-N-test-results.md | |
| Critical findings at S6 | phase-N-code-review.md | |
| Foundation wait time (minutes) | Telemetry | Dependent phases only: time between S4 complete and S5 start |
| Completeness check duration (minutes) | prd-interview-telemetry.jsonl | Time between `completeness_check_started` and `completeness_check_completed` |
| Completeness check score | prd-interview-telemetry.jsonl | `score` from `completeness_check_completed` event |
| Dev review duration (minutes) | prd-interview-telemetry.jsonl | Time between `kickoff_dev_review_started` and `kickoff_dev_review_completed` |
| Dev review concern count | prd-interview-telemetry.jsonl | `concernCount` from `kickoff_dev_review_completed` event |
| Phase splitter duration (minutes) | prd-interview-telemetry.jsonl | Time between `phase_splitter_started` and `phase_splitter_completed` |
| TDD spec generation duration (minutes) | workflow-telemetry.jsonl | Per phase: time between `tdd_spec_generation_started` and `tdd_spec_generation_completed` |
| TDD spec total scenario count | workflow-telemetry.jsonl | `totalScenarioCount` from `tdd_specs_all_complete` event |

---

## Step 1 -- Collect metrics

Read all required inputs.

Read prd-interview-telemetry.jsonl and filter to events matching the
current session's `linearIssueId`. Extract kickoff timing from
`completeness_check_started`/`completed`, `kickoff_dev_review_started`/
`completed`, and `phase_splitter_started`/`completed` event pairs.
Calculate duration for each as elapsed minutes between the started and
completed timestamps.

Read workflow-telemetry.jsonl and extract TDD spec generation timing from
`tdd_spec_generation_started`/`completed` event pairs (per phase) and
`tdd_specs_all_complete` for the total scenario count.

For each phase that reached Build Complete in this cycle, collect all
metrics listed above.

For Dependent phases: calculate foundation wait time as the elapsed
time between the S4 completion timestamp and the S5 start timestamp.
Record separately from total actual hours (wait time is not execution
time).

Kickoff metrics are session-level (not per-phase). Record them in every
phase record's `kickoff` block so each phase record is self-contained.
If a kickoff event is missing (e.g., Solo mode has no dev review),
record null for that field.

---

## Step 2 -- Write to velocity-history.jsonl

Append one record per phase to `.sage/intel/velocity-history.jsonl`
(path configurable via `intel.velocityFile` in workflow-config.json):

``````json
{
  "timestamp": "[ISO datetime]",
  "sessionId": "[session ID]",
  "phaseId": "[N]",
  "mode": "[mob|sprint|pair|solo]",
  "layer": "[layer]",
  "phaseType": "[foundation|independent|dependent]",
  "estimatedHours": [N.N],
  "actualHours": [N.N],
  "buildMode": "[autonomous|checkpoint]",
  "stepDurationMinutes": {
    "s1": [N],
    "s2": [N],
    "s3": [N],
    "s4": [N],
    "s5": [N],
    "s6": [N],
    "s7": [N],
    "s8": [N]
  },
  "hookRejectionCount": [N],
  "tddGreenFirstPassRate": [0.00],
  "refactorCompletionRate": [0.00],
  "s7TestPassRate": [0.00],
  "criticalFindingsAtS6": [N],
  "foundationWaitMinutes": [N],
  "kickoff": {
    "completenessCheckDurationMinutes": [N],
    "completenessCheckScore": [N],
    "devReviewDurationMinutes": [N],
    "devReviewConcernCount": [N],
    "phaseSplitterDurationMinutes": [N],
    "tddSpecGenerationDurationMinutes": [N],
    "tddSpecScenarioCount": [N]
  }
}
``````

If any metric is unavailable (artifact missing or field null):
record null for that field. Do not skip the record.

---

## Step 3 -- Publish to Notion (optional)

If `intel.notionPublishEnabled` is true in workflow-config.json:
write the same data to the Notion metrics database via Notion MCP.
One record per phase per cycle.

If the Notion write fails: log the failure to velocity-history.jsonl
as a metadata note. Do not retry in this invocation -- the local
`.sage/intel/velocity-history.jsonl` is the authoritative record.

If `intel.notionPublishEnabled` is false or not set: skip this step.

---

## Constraints

- Writes to `.sage/intel/velocity-history.jsonl` as the canonical store
- Optionally publishes to Notion dashboard (advisory view only)
- Never modifies manifests, skills, agents, or source code
- Never aggregates across modes -- one dataset per mode
- Records null for missing fields rather than skipping the record
- Invoke after cycle close only -- not during active build work

