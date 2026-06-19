---
name: skill-effectiveness-evaluator
description: >
  Evaluates skill effectiveness every 5 work cycles by analysing execution
  patterns across the full telemetry dataset. When a skill shows consistent
  underperformance, proposes a targeted diff to its SKILL.md and stages it
  for human approval via Linear. Cannot apply its own staged diffs. Use this
  skill every 5 completed cycles. Do not invoke more frequently -- the
  evaluation requires enough data to detect patterns rather than noise.
---

# Skill Effectiveness Evaluator

Analyses execution patterns across the full session telemetry dataset
every 5 cycles. Identifies skills that are consistently underperforming
against their intended purpose, drafts a targeted SKILL.md improvement,
stages it for approval, and creates a Linear issue. Cannot apply changes
without human approval.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| workflow-telemetry.jsonl | [SESSION_ROOT]/ | Yes |
| All performance reports | [SESSION_ROOT]/performance-report-cycle-*.md | Yes |
| skill-update-history.jsonl | .sage/ | Yes |
| All SKILL.md files | skills/**/SKILL.md | Yes |

---

## Coordination with prd-interviewer-effectiveness-evaluator

When **`skills/prd-interviewer-effectiveness-evaluator/SKILL.md`** exists in the repository, **`prd-interviewer` is evaluated only by that skill**. Skip the entire **### prd-interviewer** subsection below in Step 2 — do not propose duplicate SKILL updates or Linear issues for **`prd-interviewer`**. PRD telemetry lives in **`prd.telemetryFile`** (see `.sage/workflow-config.json`), not session **`workflow-telemetry.jsonl`**.

---

## Step 1 -- Check eligibility

Before evaluating any skill:

1. Read skill-update-history.jsonl.
2. For each skill, check if it was rejected in the last 2 cycles.
   If yes: suppress evaluation for that skill this cycle. Log suppression.
3. Check if a Pending Approval Linear issue already exists for the skill.
   If yes: do not create a duplicate. Log and skip.
4. Verify at least 3 invocations of the skill exist in telemetry.
   If fewer than 3: insufficient data. Skip with note.

---

## Step 2 -- Evaluate each skill

### prd-completeness-check

Underperforming if:
PRDs consistently score below 70/100 on the same dimension across 3+
consecutive cycles. Check which dimension is consistently low -- this
indicates the scoring rubric for that dimension needs recalibration, or
the dimension's criteria are ambiguous.

Signal to look for in telemetry:
  Multiple re-runs of prd-completeness-check for the same PRD (indicates
  PRDs are failing and requiring repeated remediation on the same points).

Proposed fix type:
  Rubric clarification for the specific dimension. Add a worked example
  or tighten the language in the sub-criteria. Do not change point values
  without strong evidence.

### prd-interviewer

**Skip if `prd-interviewer-effectiveness-evaluator` is deployed** (see Coordination above).

Underperforming if:
Traceability reviews (S3) consistently find Blocker findings that relate
to missing PRD sections. Cross-reference S3 Blocker categories against
the prd-interviewer question set -- if a Blocker type is not covered by
any question, that is the gap.

Signal to look for:
  phase-N-traceability-review.md files with Blocker findings > 0, where
  the Blocker description references a PRD section type that the
  prd-interviewer should have elicited.

Proposed fix type:
  Add a targeted question to the relevant phase of the question set.
  Do not restructure the entire question set -- one targeted addition.

### phase-splitter

Underperforming if:
Phases are consistently splitting incorrectly. Evidence:
  - Phases >8 hours actual (too large -- sub-split missed)
  - Phases <1 hour actual (too small -- merge missed)
  - Foundation phases being blocked by Dependent phase work (dependency
    direction was wrong)
  - High hook rejection rate on foundation-verified-gate (Dependent phases
    starting S5 too early -- dependency detection failed)

Proposed fix type:
  Add a splitting rule or adjust an existing rule in the heuristics.
  Tighten the independence scoring deduction for the pattern observed.

### kickoff-dev-review

Underperforming if:
Concerns categorised as ADDRESSED_IN_PRD during kick-off are later
surfaced again as Blocker findings at S3 traceability review. This
indicates concerns were closed too quickly without verifying the PRD
actually covered them.

Signal: high ADDRESSED_IN_PRD count at kick-off + Blocker findings at S3
covering the same topic areas.

Proposed fix type:
  Add a verification step -- when categorising ADDRESSED_IN_PRD, require
  citing the specific PRD section and line rather than the general area.

### session-performance-evaluator

Underperforming if:
Performance reports are produced but Lead Dev reports they are not
actionable (feedback collected via Linear issue comments).

Proposed fix type:
  Improve specificity of finding descriptions. Add telemetry event
  examples to the scoring dimensions reference.

### skill-effectiveness-evaluator

Underperforming if:
Proposed SKILL.md diffs are consistently rejected. Review rejection
reasons from skill-update-history.jsonl to identify the pattern.

Proposed fix type:
  Adjust the evaluation criteria for the skill type being over-proposed.
  Add a higher evidence bar before triggering a proposal.

### intel-recorder

Underperforming if:
velocity-history.jsonl contains missing or null fields, indicating
metrics are not being captured correctly.

Proposed fix type:
  Add explicit null checks and logging for the missing fields.

### intel-advisor

Underperforming if:
Advisor recommendations consistently diverge from actual outcomes
(assess by comparing recommended effort ranges against
velocity-history.jsonl actuals from subsequent cycles).

Proposed fix type:
  Adjust the calibration logic or add a low-sample-size warning when
  fewer than 5 data points exist for a layer/mode combination.

---

## Step 3 -- Draft the skill diff

For each underperforming skill, draft a unified diff targeting the
specific SKILL.md (and reference file if applicable).

The diff must be:
- Targeted: change only what is needed. Do not restructure the whole file.
- Justified: the diff description must explain what pattern was observed
  and why this specific change addresses it.
- Testable: describe how you would verify the change improved outcomes
  in subsequent cycles.

Diff format:

``````diff
--- a/skills/[skill-name]/SKILL.md
+++ b/skills/[skill-name]/SKILL.md
@@ -[line],[count] +[line],[count] @@
 [context line]
-[removed line]
+[added line]
 [context line]
``````

Write the diff to: .skill-update-staging/[LINEAR_ISSUE_ID].diff
(Generate a temporary placeholder ID if the Linear issue does not
yet exist -- replace after creation.)

---

## Step 4 -- Create Linear issues

For each proposed diff, create a Linear issue:

- Label: skill-update
- Status: Pending Approval
- Title: "Skill update -- [skill-name] -- cycle [N]"
- Description:
  ``````
  Skill: [skill-name]
  Evaluation cycle: [N]
  Evidence: [specific pattern observed across N cycles]
  Change: [what the diff does in plain language]
  Rationale: [why this change addresses the observed pattern]
  Diff path: .skill-update-staging/[issue-id].diff
  Approver: [see below]
  ``````

Approvers:
  prd-completeness-check, prd-interviewer -> Product Manager
  phase-splitter -> Lead Dev
  All others -> Lead Dev

---

## Step 5 -- Log to skill-update-history.jsonl

Append to .sage/skill-update-history.jsonl:

``````json
{
  "timestamp": "[ISO datetime]",
  "cycle": [N],
  "skillName": "[skill-name]",
  "action": "proposed",
  "linearIssueId": "[issue-id]",
  "diffPath": ".skill-update-staging/[issue-id].diff",
  "evidenceSummary": "[one sentence]"
}
``````

---

## Constraints

- Cannot modify any SKILL.md directly -- diffs only, staged for approval
- Cannot apply its own staged diffs
- Minimum 3 skill invocations before evaluating
- Suppresses re-proposal for 2 cycles after rejection
- One Linear issue per skill per evaluation cycle -- no duplicates
- Invoke only every 5 cycles -- not more frequently

---

## Reference files

Read references/per-skill-criteria.md for:
- Detailed signal patterns for each skill
- Worked examples of underperformance indicators
- Guidance on diff scope and evidence thresholds

