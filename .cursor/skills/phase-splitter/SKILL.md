---
name: phase-splitter
description: >
  Analyses a completed PRD and the Profitability codebase to generate a
  recommended phase breakdown for a Sprint or Pair work stream. Scores each
  candidate phase for independence, identifies dependency chains, estimates
  effort, produces a phase breakdown document for team review, and generates
  the session manifest, Linear phase issues, and git worktrees on confirmation.
  Use this skill during Step 2 of the kick-off session (Phase Breakdown) for
  every Sprint and Pair work stream. Do not manually define phases before
  running this skill -- the skill's output is the starting point for team
  adjustment, not a blank discussion.
---

# Phase Splitter

Generates a recommended phase breakdown from a PRD that has passed
prd-completeness-check. Produces a single recommended split with
independence scores, dependency chains, effort estimates, and developer
profile recommendations. The team reviews and adjusts at kick-off --
the skill provides the starting point, not the final answer.

Design principle: a good phase has exactly one objective, is independently
testable without any other phase being complete, and can be owned entirely
by one developer. If a phase requires coordination with another developer
mid-execution, it must be re-split.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| PRD | `.sage/prds/[FEATURE_ID]/prd.md` (must be at Linear status Ready) | Yes |
| Component specification | `.sage/prds/[FEATURE_ID]/component-spec.md` | Yes (UI features) |
| Phase-splitter briefing | [SESSION_ROOT]/phase-splitter-briefing.md | Yes (Sprint/Mob) |
| Codebase | Read access via Cursor file system | Yes |
| Session manifest template | .cursor/templates/session-manifest-template.md | Yes |

Do not run this skill against a PRD that has not passed prd-completeness-check.

---

## Step 1 -- Load all inputs

Read the PRD from `.sage/prds/[FEATURE_ID]/prd.md`.
Read the component specification from `.sage/prds/[FEATURE_ID]/component-spec.md`.
Read the phase-splitter briefing from the session root.
Read the session manifest template.

---

## Step 2 -- Codebase reconnaissance

Scan the codebase to identify all files this feature will touch.

Record findings in four categories:
- UI files (components, pages, styles)
- Backend / API files (services, controllers, handlers)
- Data / schema files (stored procedures, views, migrations, models)
- Test files (existing tests that will need updating)

For each file, record:
- File path
- Current role in the codebase
- What this feature will change about it
- Whether it is shared with other features currently in development

Profitability-specific: pay particular attention to:
- Stored procedures (usp_* naming pattern)
- Views (vw_BI_*, Global_Result)
- The 42-measure output set
- Dataverse boundary -- flag any requirement that appears to cross it
- Flag logic files (NewInstFlag, ClosedInstFlag, PlugInstrumentFlag)

---

## Step 3 -- Generate candidate phases

Apply the splitting rules from references/splitting-heuristics.md in order.

Each candidate phase must satisfy:
1. Single objective -- one verb phrase describes the entire phase
2. Exclusive file ownership -- no file appears in two phases
3. At least one independently runnable test
4. Effort in the 2-8 hour range (phases outside this range need review)

Before layer-based splitting, apply the shell-first rule (Rule 0):
if any candidate phase introduces a new page or major UI container,
verify a Foundation-lane phase exists that delivers the routing,
layout skeleton, and state management shell. If not, create one and
set all UI phases that depend on it to Dependent. Skip only when the
feature modifies existing pages without new routing or layout.

Start with a layer-based split (database / API / UI / data-library).
Sub-split within a layer only if: a single layer has >8 hours of work,
or two parts of the same layer have zero file overlap and independent
test suites.

---

## Step 4 -- Score independence for each phase

For each candidate phase, calculate an independence score (0-100).
Apply deductions from references/splitting-heuristics.md.

A phase scoring below 60 is flagged with an explanation.
Record for each phase:
- Independence score
- Upstream dependencies (phases that must complete before this one)
- Downstream consumers (phases that depend on this one)
- Dependency nature (shared data contract, shared file, runtime dependency)

---

## Step 4.5 -- Cross-phase contract generation

Identify all data boundaries that cross phase boundaries:
- API endpoints consumed by one phase and produced by another
- Shared state shapes or Angular service interfaces
- Database schema dependencies (tables/views one phase creates that
  another phase reads)

For each boundary, generate a contract entry in
`[SESSION_ROOT]/phase-{N}-contracts.md` for the consuming phase:

- Interface/endpoint name
- Direction: produces or consumes
- Data shape (TypeScript interface, SQL result set, or JSON schema)
- Mock data example (valid sample payload or result row)
- Owning phase (which phase produces this contract)

Use the contract template at `.cursor/templates/contract-template.md`.

Add each contract file to `requiredReferences` for the consuming phase.
The existing `required-references-gate` hook enforces that these files
are read before S5 build begins.

If no cross-phase data boundaries exist, skip this step and record
"No cross-phase contracts required" in the phase breakdown document.

---

## Step 5 -- Build the dependency map and assign phase types

From the dependency map, assign a phase type to each phase:

Foundation:
  No upstream dependencies. Has at least one downstream consumer.
  Must merge before Dependent phases can enter S5 build.
  Start immediately in parallel with Independent phases.

Independent:
  No upstream dependencies. No downstream consumers.
  Start immediately in parallel with Foundation phases.
  Participates in the regression trigger after merge.

Dependent:
  Has at least one upstream dependency.
  Can progress through S1-S4 in parallel.
  S5 build is blocked until foundationVerified = true in the manifest.

---

## Step 6 -- Estimate effort per phase

For each phase, produce an effort range using the heuristics in
references/splitting-heuristics.md.

Express as [low]-[high] hours.
Flag any phase estimated over 8 hours -- consider sub-splitting.
Flag any phase estimated under 1 hour -- consider merging with adjacent.

---

## Step 7 -- Recommend developer profiles

For each phase, recommend a developer profile:
- UI-heavy (strong frontend / component skills)
- Backend-heavy (API, service layer, business logic)
- Database (stored procedures, schema, views)
- Full-stack (touches multiple layers)
- Any (no strong skill preference)

Do not assign named developers -- that happens at the planning cycle.

---

## Step 8 -- Produce the phase breakdown document

Write to [SESSION_ROOT]/phase-breakdown.md.
Use references/splitting-heuristics.md for the output structure.

Include:
- Phase count and rationale
- Tier structure (Foundation / Independent / Dependent)
- One section per phase: objective, type, files in scope, independence
  score, effort range, developer profile
- Dependency map (text or table)
- Any flags (phases below 60 independence, phases outside effort range)

---

## Step 9 -- Present at kick-off and facilitate adjustment

Present the breakdown to the team. Walk through:
1. Phase count and overall structure -- does this feel right?
2. Tier structure -- do the dependency assignments match team intuition?
3. Independence flags -- are any flagged phases actually more independent
   than scored?
4. Effort ranges -- does the team's intuition agree?
5. Developer profile recommendations -- any concerns?

For each proposed adjustment:
- Check for file ownership conflicts (does merging two phases create
  a file that appears in both?)
- Check independence score impact (does the merge create a new dependency?)
- Check tier impact (does the merge change a Foundation to a Dependent?)

Update phase-breakdown.md with agreed changes.
Do not finalise until the team confirms.

---

## Step 10 -- Finalise and generate session artifacts

Once the team confirms the breakdown:

1. Update phase-breakdown.md with final agreed phases

2. Populate the session manifest:
   - One entry per phase with all required fields from the template
   - Validate all file paths in scopedFiles exist in the codebase
   - Record any paths that cannot be validated as NEW (not an error)
   - Set `sessionState.parentBranch` to the current git branch name
     (the parent feature branch). This identifies the branch for
     cross-machine visibility (developers pull this branch to see
     other phases' progress).
   - Write to [SESSION_ROOT]/session-manifest.md
   - Write session ID to .sage/sessions/active-session.txt

3. Create Linear phase issues (via Linear MCP):
   - One issue per phase
   - Title: "[Feature title] -- Phase N: [objective]"
   - Status: Pending Approval
   - Custom field worktree_path: "phase-N/[kebab-objective]"
   - Link upstream dependencies to their phase issues

4. Create git worktrees (Sprint mode only):
   - Branch naming: "LIN-[issue-id]-phase-N-[kebab-objective]"
   - Worktree path: C:\Sage\worktrees\[feature-id]\phase-N\

5. Bootstrap session state in each worktree (Sprint mode only):
   Each worktree is an independent working tree with its own `.sage/`
   directory. Hooks resolve session context from the worktree root, so
   every worktree must have the session files populated. For each
   worktree created in step 4:
   - Copy `.sage/sessions/active-session.txt` (containing the session ID)
   - Copy `.sage/workflow-config.json`
   - Copy the full session directory
     `[SESSION_ROOT]/` to `.sage/sessions/[session-id]/` in the worktree
   - Write the phase number (e.g. `2`) to `.sage/current-phase.txt`
     in the worktree root. This file is the persistent fallback for
     `SAGE_PHASE_ID` — hooks read it when the environment variable
     is not set.
   - Copy `.sage/prds/` to the worktree so required references resolve
   - Bootstrap `phase-{N}/phase-manifest.json` in each worktree's
     session directory with the initial phase runtime:
     ```json
     {
       "currentStep": "dev-interview",
       "stepStatus": { "dev-interview": "not-started" },
       "stepTimestamps": {},
       "buildMode": null,
       "batches": [],
       "validationConfirmed": false,
       "hookRejectionCount": 0,
       "linearIssueStatus": "Pending Approval",
       "startedAt": null,
       "completedAt": null,
       "findingSummary": {},
       "deferredItems": []
     }
     ```
   - Bootstrap `phase-{N}/workflow-telemetry.jsonl` as an empty file
     in each worktree's session directory (telemetry_logger will write
     per-phase events here).

   If any copy fails, warn but do not abort — the worktree is still
   usable, but hooks will degrade silently without session context.

6. Report completion of artifact generation (do not end the skill here --
   proceed to Step 11 for approval).

---

## Step 11 -- Approve phases and transition to build sprint

After Step 10 artifacts are generated, prompt the session driver for
approval. The approver is whoever is driving the kick-off session
(Product Manager, Lead Dev, or both).

1. Present a summary of all phases with their objectives, types, and
   effort estimates. Then ask:

   "The phase breakdown is complete. [N] phases have been created in
   Linear at Pending Approval. Do you approve all phases to proceed
   to the build sprint?"

2. Wait for explicit confirmation. Do not proceed without a clear "yes"
   or equivalent affirmative from the session driver.

3. On confirmation, for each phase issue:
   - Call Linear MCP to update the phase issue status from
     "Pending Approval" to "Approved"
   - Update `linearIssueStatus` to `"Approved"` in the phase's
     `phase-{N}/phase-manifest.json`

4. Update session-level state in session-manifest.md:
   - Set `sessionState.status` to `"build-sprint"`
   - Set `sessionState.allPhasesApproved` to `true`

5. Report final completion:
   "[N] phases approved. Session manifest updated. Linear issues moved
   to Approved. Session is now in build-sprint -- TDD spec generation
   will begin next."

If the session driver declines or requests changes, return to Step 9
to facilitate further adjustment. Do not approve until confirmation
is received.

---

## Telemetry

Emit three telemetry events using `prd_telemetry_append.py` (pre-session
events) and one bootstrap event directly to `workflow-telemetry.jsonl`
(post-session-creation). Pre-session events use
`workflowKind: "phase_splitter"`.

**At the start of Step 1** (before loading inputs), emit:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"event":"phase_splitter_started","workflowKind":"phase_splitter","linearIssueId":"[FEATURE_ID]","mode":"[mob|sprint|pair]"}'
```

**At the end of Step 9** (after team confirms the breakdown but before
artifact generation), emit:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"event":"phase_splitter_phases_proposed","workflowKind":"phase_splitter","linearIssueId":"[FEATURE_ID]","phaseCount":[N],"phases":[[{"phaseId":"1","phaseType":"foundation","layer":"api","independenceScore":[N],"effortEstimateHours":{"low":[N],"high":[N]}}, ...]]}'
```

**At the end of Step 10** (after manifest, Linear issues, and worktrees
are created), emit the completion event to `prd-interview-telemetry.jsonl`
and bootstrap `workflow-telemetry.jsonl`:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"event":"phase_splitter_completed","workflowKind":"phase_splitter","linearIssueId":"[FEATURE_ID]","sessionId":"[session ID]","phaseCount":[N],"manifestPath":"[SESSION_ROOT]/session-manifest.md","worktreesCreated":[true|false],"linearIssuesCreated":[N]}'
```

Then immediately write the bootstrap event to the session-root
`workflow-telemetry.jsonl` (session-level events like kickoff go here;
per-phase events go to `phase-{N}/workflow-telemetry.jsonl`):

```python
import json
from datetime import datetime, timezone
from pathlib import Path

bootstrap = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "event": "session_created",
    "sessionId": "[session ID]",
    "featureId": "[FEATURE_ID]",
    "mode": "[mob|sprint|pair]",
    "phaseCount": [N]
}
telemetry_path = Path("[SESSION_ROOT]") / "workflow-telemetry.jsonl"
telemetry_path.parent.mkdir(parents=True, exist_ok=True)
with open(telemetry_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(bootstrap) + "\n")
```

Pre-session events are appended to the PRD telemetry file configured in
`workflow-config.json` (default: `.sage/prd-interview-telemetry.jsonl`).
The bootstrap event is written directly to the session's
`workflow-telemetry.jsonl`. Failures are silent and do not affect the
phase-splitter workflow.

**Immediately after writing the bootstrap event**, initialize the idle
detection state file so the first tool call in each phase can detect gaps
from kickoff:

```python
import json
from datetime import datetime, timezone
from pathlib import Path

now_iso = datetime.now(timezone.utc).isoformat()
session_root = Path("[SESSION_ROOT]")
state = {"phases": {}}
for phase_id in ["1", "2", ...]:  # all phase IDs
    state["phases"][phase_id] = {
        "lastTimestamp": now_iso,
        "currentStep": "dev-interview",
    }
state_path = session_root / ".telemetry-last-event.json"
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
```

This writes `.telemetry-last-event.json` with the current timestamp for
all phases. Without this, the first idle gap (between kickoff and when a
developer starts their phase) would never be detected.

---

## Constraints

- Do not run against a PRD below completeness threshold
- Do not assign named developers -- profile recommendations only
- Do not finalise the manifest until the team confirms the breakdown
- Sprint mode only: create worktrees and bootstrap `.sage/` in each.
  Pair mode: skip worktree creation.
- Cannot approve Linear phase issues without explicit confirmation from the
  session driver (PM or Lead Dev) in the active kick-off session

---

## Reference files

Read references/splitting-heuristics.md for:
- Splitting rules in order of application
- Independence scoring deduction table
- Effort estimation heuristics by layer and task type
- Phase breakdown document output structure

