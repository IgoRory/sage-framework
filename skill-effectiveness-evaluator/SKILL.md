---
name: skill-effectiveness-evaluator
description: >
  Evaluates skill quality across every 5 completed work cycles. Analyses
  cross-session telemetry and session performance reports to identify
  patterns, then proposes specific SKILL.md edits with rationale and
  evidence. Only evaluates skills invoked in at least 3 of the 5 sessions.
  Stages proposed diffs for human approval via Linear. On approval, applies
  changes via Linear webhook trigger. Background, readonly except for
  Notion posts, Linear issue creation, and approved SKILL.md writes.
  Never invoked manually — triggered by session counter in manifest system.
---

# Skill Effectiveness Evaluator

Evaluates whether skills are producing the outcomes they were designed
to produce, using evidence accumulated across 5 completed work cycles.
Proposes targeted SKILL.md edits — exact text changes with evidence-backed
rationale — for human approval via Linear before applying.

**Operating constraints:**
- Runs every 5 completed sessions — triggered by session counter
- Only evaluates skills invoked in ≥3 of the 5 sessions
- Only surfaces High and Medium confidence proposals for approval
- Low confidence findings recorded but not actioned
- Does not re-propose a rejected change for 2 evaluation cycles
- Never modifies SKILL.md directly — writes only after Linear approval
  via webhook trigger

---

## Trigger condition

Triggered when the session counter in `[WORKFLOW_ROOT]/.meta/session-counter.json`
reaches a multiple of 5. The trigger passes:
- `evaluation_cycle` — which cycle number this is (1, 2, 3...)
- `session_ids` — the 5 session IDs to evaluate
- `session_roots` — file system paths to those 5 session directories

---

## Step 1 — Determine qualifying skills

A skill qualifies for evaluation in this cycle if it was invoked in at
least 3 of the 5 sessions being evaluated.

Determine invocation by checking `workflow-telemetry.jsonl` in each
session for `subagentStart` events whose `active_agent` field matches
a skill name.

Skills currently in scope for evaluation:
- `prd-completeness-check` — invoked whenever a PRD is assessed
- `prd-interviewer` — invoked whenever a PRD is drafted
- `phase-splitter` — invoked at kick-off for every Sprint
  or Pair work stream

Build the qualifying skills list. If no skills qualify (fewer than 3
invocations each), post a brief note to Notion and exit:
> "Evaluation cycle [N] — no skills met the 3-invocation threshold.
> No proposals generated."

---

## Step 2 — Load cross-session data

For each of the 5 sessions, load:

**Telemetry:**
- `workflow-telemetry.jsonl` — all hook events
- Session performance report (from Notion session page, via MCP)

**Skill-specific artifacts:**
- `prd-completeness-check`: all `prd-completeness-report.md` files
  produced during these sessions
- `prd-interviewer`: all PRD drafts and component spec drafts produced,
  plus their subsequent completeness check scores
- `phase-splitter`: all `phase-breakdown.md` files produced, plus
  team adjustment records from kick-off confirmation sections

**History:**
- `skill-update-history.jsonl` — load to identify suppressed changes
  that should not be re-proposed this cycle

---

## Step 3 — Evaluate each qualifying skill

Apply the per-skill criteria in `references/per-skill-criteria.md`.
Read the relevant section for each qualifying skill before evaluating.

For each skill, produce:
- A list of patterns observed (with session evidence)
- A confidence level per pattern: High (4–5 sessions), Medium (3 sessions)
- A proposed change per pattern, or a finding with no change if the
  pattern is informational only
- The specific SKILL.md text being proposed as a replacement

Do not propose changes based on a single session's data regardless of
how significant the finding appears. Minimum evidence requirement is
3 sessions showing the same pattern.

---

## Step 4 — Check suppression list

Before finalising proposals, check `skill-update-history.jsonl` for
any proposed changes that were rejected in a prior cycle and are still
within their suppression window (`suppressed_until_cycle` > current
`evaluation_cycle`).

Remove any suppressed proposals from the list. Do not surface them.
If a suppressed change's evidence has grown significantly stronger
(e.g. the pattern now appears in all 5 sessions rather than 3), note
it in the Notion report but still respect the suppression window.

---

## Step 5 — Stage proposed diffs

For each approved proposal (High or Medium confidence, not suppressed):

1. Produce a diff in this format:

```
SKILL UPDATE PROPOSAL
=====================
Skill:           [skill-name]
Evaluation cycle: [N]
Confidence:      [High / Medium]
Sessions:        [LIN-session-id list]

CHANGE [N of N]:

Current text (lines [X]–[Y] of SKILL.md or references/[file].md):
---
[exact current text]
---

Proposed replacement:
---
[exact proposed text]
---

Rationale:
[What pattern was observed, in which sessions, with specific evidence.
 What this change is designed to fix or improve. How confidence was assessed.]

Expected outcome:
[What should improve in future sessions if this change is effective.
 How Agent 1 or this evaluator will detect whether the change worked.]
```

2. Write the diff to:
   `[WORKFLOW_ROOT]/.skill-update-staging/LIN-[issue-id]-diff.md`
   (The issue ID is assigned in the next step.)

3. Bundle all changes for the same skill into a single diff file,
   clearly numbered (CHANGE 1 of 3, CHANGE 2 of 3, etc.).

---

## Step 6 — Create Linear approval issues

For each qualifying skill with at least one proposal, create one Linear
issue:

- **Title:** `Skill update proposal — [skill-name] — cycle [N] — [M] change(s)`
- **Description:** Full diff content (all changes for this skill)
- **Assignee:**
  - `prd-completeness-check` → the Product Manager
  - `prd-interviewer` → the Product Manager
  - `phase-splitter` → Lead Dev
- **Status:** `Pending Approval`
- **Label:** `skill-update`
- **Priority:** Medium
- **Linked sessions:** Link all 5 session issues evaluated in this cycle
- **Metadata block `diff_path`:** Path to the staged diff file — written to the `sage_metadata` block in the issue description

Write the Linear issue ID back to the staged diff file header
(`linear_issue_id` field) and to the trigger file template for the
webhook receiver.

---

## Step 7 — Post evaluation report to Notion

Post to `/Workflow/Skill Effectiveness Reviews` as a new child page:
`Skill Effectiveness Review — Cycle [N] — [ISO date]`

```
# Skill Effectiveness Review — Cycle [N]

Date:     [ISO date]
Sessions: [list of 5 session IDs with links]
Skills evaluated: [list of qualifying skills]
Skills below threshold: [list of skills with <3 invocations, if any]

---

## Proposals generated

| Skill | Changes | Confidence | Linear issue | Assignee |
|---|---|---|---|---|
| [skill] | [N] | [High/Medium] | [LIN-XXX] | [name] |
...

[If none: "No proposals generated this cycle."]

---

## Low confidence findings (recorded, not actioned)

[For each Low confidence pattern observed:]

Skill: [skill-name]
Pattern: [description]
Sessions: [which sessions showed this]
Evidence: [brief summary]
Status: Monitoring — will surface for approval if pattern persists
        into evaluation cycle [N+1] or later.

[If none: "None."]

---

## Suppressed proposals (still within window)

| Skill | Originally proposed | Suppressed until cycle | Rejection rationale |
|---|---|---|---|
...

[If none: "None."]

---

## Cumulative effectiveness summary

[After cycle 3+, include this section. Before cycle 3, omit.]

For each skill that has had at least one approved change applied:
- What was changed (brief summary)
- Whether the expected outcome was observed in subsequent sessions
- Whether further changes are likely based on current trajectory

[If no changes have been applied yet: "No approved changes applied yet —
 cumulative assessment available from cycle 3 onward."]
```

---

## Step 8 — Handle webhook trigger (apply step)

This step executes when a Linear `skill-update` issue moves to `Approved`
status via webhook. It is a separate execution path from Steps 1–7.

**Trigger input** (from `.skill-update-triggers/[LIN-id].json`):
```json
{
  "linear_issue_id": "LIN-XXX",
  "skill_name": "prd-completeness-check",
  "approved_by": "approver@organisation.com",
  "approved_at": "[ISO datetime]",
  "diff_path": "[WORKFLOW_ROOT]/.skill-update-staging/LIN-XXX-diff.md",
  "confidence": "High",
  "evaluation_cycle": 3
}
```

**Apply procedure:**
1. Read the staged diff from `diff_path`
2. For each change in the diff:
   - Locate the `Current text` block in the target SKILL.md or
     references file
   - Verify it matches exactly (character-for-character)
   - If it matches: apply the replacement
   - If it does not match: the file has been edited since staging —
     abort this change, log conflict, continue to next change
3. After applying all non-conflicting changes:
   - Commit to repo:
     ```
     git commit -m "skill-update([skill-name]): [one-line summary]

     Approved by [approver] via [LIN-XXX]
     Evaluation cycle [N] — [M] change(s) applied"
     ```
4. Update Linear issue:
   - Status → `Applied`
   - Comment: `Changes applied. Commit: [hash]. [N] of [M] changes
     applied. [If any conflicts: N changes skipped due to conflict —
     see child issue LIN-XXX for manual review.]`
5. Write to `skill-update-history.jsonl`:
   ```json
   {
     "linear_issue_id": "LIN-XXX",
     "skill_name": "prd-completeness-check",
     "evaluation_cycle": 3,
     "outcome": "applied",
     "approved_by": "approver@organisation.com",
     "applied_at": "[ISO datetime]",
     "commit_hash": "[hash]",
     "changes_applied": 2,
     "changes_skipped": 0
   }
   ```

**Conflict handling:**
If any change cannot be applied due to a conflict:
- Create child Linear issue:
  - Title: `Manual skill update required — [skill-name] — [LIN-XXX]`
  - Assignee: Lead Dev
  - Status: `Needs Review`
  - Description: the conflicting change block with explanation of
    what changed in the file since staging
- Move parent issue status to `Partially Applied` if some changes
  applied, `Apply Failed` if none applied

**Rejection handling:**
When a Linear `skill-update` issue moves to `Rejected`:
1. Read the rejection comment from the Linear issue
2. Write to `skill-update-history.jsonl`:
   ```json
   {
     "linear_issue_id": "LIN-XXX",
     "skill_name": "prd-completeness-check",
     "evaluation_cycle": 3,
     "outcome": "rejected",
     "rejected_by": "[name]",
     "rejected_at": "[ISO datetime]",
     "rejection_rationale": "[comment text]",
     "suppressed_until_cycle": [N+2]
   }
   ```
3. Update Linear issue status to `Rejected — recorded`
4. No further action — the suppression window is now active

---

## Reference files

Read `references/per-skill-criteria.md` for:
- Specific correlation patterns to evaluate per skill
- What evidence constitutes a genuine pattern vs. noise
- How to formulate well-targeted proposed changes
- Profitability-specific signal interpretation
