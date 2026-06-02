---
name: phase-splitter
description: >
  Analyses a completed PRD and the Profitability codebase to generate a
  recommended phase breakdown for a Sprint or Pair work stream. Uses a
  layered planning funnel (L1 domain decomposition → L2 phase boundary
  decisions → L3 manifest generation) with confidence scoring per phase,
  back-revision support, and spike recommendations for high-risk boundaries.
  Scores each candidate phase for independence, identifies dependency chains,
  estimates effort, produces a phase breakdown document for team review, and
  generates the session manifest, Linear phase issues, and git worktrees on
  confirmation. Use this skill during Step 2 of the kick-off session (Phase
  Breakdown) for every Sprint and Pair work stream. Do not manually define
  phases before running this skill -- the skill's output is the starting
  point for team adjustment, not a blank discussion.
---

# Phase Splitter

Generates a recommended phase breakdown from a PRD that has passed
prd-completeness-check. Uses a three-level planning funnel so that domain
decomposition (L1) is verified before phase cuts are made (L2), and manifest
generation (L3) only happens after the team confirms the phase plan.

Each phase in the final breakdown carries a three-dimension confidence score
(dependency confidence, effort confidence, objective clarity) and an overall
recommendation (PROCEED / REVIEW BEFORE BUILD / SPLIT RECOMMENDED / SPIKE
RECOMMENDED). Phases with low confidence are flagged before the team commits
to the plan.

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

## Planning funnel overview

The skill runs three levels. Each level is reviewed before the next begins.
Any level can trigger a back-revision to a prior level (see Back-revision
rules). The team can defer a decision at any level with a named unblocking
condition (see Deferral rules).

```
L1 — Domain decomposition   Identify groupings, verify dependencies, audit shared state
L2 — Phase boundary decisions   Apply splitting rules, score confidence, flag risks
L3 — Execution   Generate manifest, Linear issues, worktrees
```

---

## L1 — Domain decomposition

### Step 1 -- Load all inputs

Read the PRD from `.sage/prds/[FEATURE_ID]/prd.md`.
Read the component specification from `.sage/prds/[FEATURE_ID]/component-spec.md`.
Read the phase-splitter briefing from the session root.
Read the session manifest template.

### Step 2 -- Codebase reconnaissance

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

### Step 3 -- Identify natural groupings with confidence classification

From the codebase reconnaissance, identify natural technical groupings -- sets
of files that are functionally related and would move together.

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the confidence
classification scheme (verified-in-code / inferred / assumption) and usage rules.

For each grouping, classify every dependency claim using that scheme.
`assumption`-confidence dependencies are listed separately in an "Unverified
dependencies" section. They do not drive grouping decisions until verified or
confirmed by the team.

### Step 4 -- Shared mutable state audit

For each proposed grouping boundary, identify:
- Shared tables, views, or stored procedures that multiple groupings would write to
- Shared configuration objects or global services
- Shared caches or in-memory state

These are hidden coupling points not visible from the PRD. A shared mutable
state finding may promote a grouping dependency from `inferred` to
`verified-in-code`, or may require a new Foundation grouping to own the
shared resource.

### Step 5 -- Interface trace per boundary

For each boundary between groupings, trace the data contract:
- If the interface exists in code: name the exact file, method, and signature
- If the interface does not yet exist: specify the exact signature it needs to
  expose for the consuming grouping to work

An interface that cannot be named is an `assumption`-confidence dependency.

### Step 6 -- Produce L1 domain map

Write the L1 findings to a structured summary (held in chat or written to
`[SESSION_ROOT]/phase-split-L1.md` if the team requests persistence):

```markdown
# Phase Split L1 — Domain Map: [Feature title]

## Natural groupings
| Grouping | Files | Purpose |
|----------|-------|---------|

## Verified dependencies between groupings
| From | To | Contract | Confidence |
|------|----|----------|------------|

## Shared mutable state
| Resource | Groupings affected | Risk |
|----------|--------------------|------|

## Unverified dependencies (assumption-confidence)
| Dependency | Basis | Resolution needed |
|------------|-------|-------------------|

## Open deferrals
[Any L1 decisions deferred with named unblocking conditions]
```

### Step 7 -- Present L1 to team and collect feedback

Present the domain map to the team. Ask:
1. Do the groupings reflect how the team thinks about this work?
2. Are any verified dependencies wrong?
3. Are there shared mutable state risks the team recognises that are not listed?
4. Are there unverified dependencies the team can resolve now?

Wait for team feedback before proceeding to L2. Apply corrections to the domain
map. Record deferrals with conditions before moving on.

---

## L2 — Phase boundary decisions

Only begin L2 after the team approves L1 (or approves with noted corrections
and deferrals).

### Step 8 -- Apply splitting rules

Apply the splitting rules from `references/splitting-heuristics.md` to the L1
domain map to generate candidate phases.

Each candidate phase must satisfy:
1. Single objective -- one verb phrase describes the entire phase
2. Exclusive file ownership -- no file appears in two phases
3. At least one independently runnable test
4. Effort in the 2-8 hour range (phases outside this range need review)

Start with a layer-based split (database / API / UI / data-library).
Sub-split within a layer only if: a single layer has >8 hours of work,
or two parts of the same layer have zero file overlap and independent
test suites.

### Step 9 -- Score independence for each phase

For each candidate phase, calculate an independence score (0-100) using the
deduction table in `references/splitting-heuristics.md`.

A phase scoring below 60 is flagged with an explanation.
Record for each phase:
- Independence score
- Upstream dependencies (phases that must complete before this one)
- Downstream consumers (phases that depend on this one)
- Dependency nature (shared data contract, shared file, runtime dependency)

### Step 10 -- Build the dependency map and assign phase types

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

### Step 11 -- Calculate three-dimension confidence score per phase

For each candidate phase, score three dimensions using the criteria in
`references/splitting-heuristics.md`:

**Dependency confidence** — is the dependency analysis based on verified code
or inferred from the PRD?
- HIGH: every dependency claim is verified-in-code; interface contract is named
- MEDIUM: most dependencies verified; one or two inferred with no code trace
- LOW: at least one dependency is assumption-confidence with no code trace

**Effort confidence** — is the effort estimate grounded in the codebase?
- HIGH: grounded in delta classification + test layer count + intel-advisor data
- MEDIUM: grounded in delta classification and test layers; no historical data
- LOW: derived from PRD complexity alone; no delta or test layer analysis

**Objective clarity** — is the phase's single objective genuinely single?
- HIGH: one sentence, one verb; TDD scenarios cluster around one file group
- MEDIUM: clear objective but scenarios fall into two loosely related groups
- LOW: requires "and" to state; scenarios fall into two distinct clusters

Apply the overall recommendation decision rules from `references/splitting-heuristics.md`.

### Step 12 -- Estimate effort per phase

For each phase, produce an effort range using the heuristics in
`references/splitting-heuristics.md`. Ground estimates in delta classification
(net-new vs extending) and test layer count rather than PRD complexity alone.

Express as [low]-[high] hours.
Flag any phase estimated over 8 hours -- consider sub-splitting.
Flag any phase estimated under 1 hour -- consider merging with adjacent.

When intel-advisor historical data is available for similar phase types and
layers, use it to calibrate estimates and note any significant deviation.

### Step 13 -- Recommend developer profiles

For each phase, recommend a developer profile:
- UI-heavy (strong frontend / component skills)
- Backend-heavy (API, service layer, business logic)
- Database (stored procedures, schema, views)
- Full-stack (touches multiple layers)
- Any (no strong skill preference)

Do not assign named developers -- that happens at the planning cycle.

### Step 14 -- Check for back-revision triggers

Before presenting L2 to the team, check whether any L2 finding invalidates
an L1 decision:
- Does a phase boundary decision reveal that two L1 groupings are more tightly
  coupled than the domain map showed?
- Does a file ownership conflict surface a dependency that was not in the L1
  verified-dependency list?
- Does an independence score below 60 indicate an L1 grouping boundary is wrong?

If any back-revision trigger is found, surface it before presenting L2. The
team approves the L1 patch before L2 continues (see Back-revision rules).

### Step 15 -- Present L2 to team and collect feedback

Present the phase breakdown to the team. Walk through:
1. Phase count and overall structure -- does this feel right?
2. Tier structure -- do the dependency assignments match team intuition?
3. Confidence scores -- are any LOW ratings a surprise? Do they agree?
4. Spike recommendations -- is the team willing to time-box the spike?
5. Independence flags -- are any flagged phases actually more independent?
6. Effort ranges -- does the team's intuition agree?
7. Developer profile recommendations -- any concerns?

For each proposed adjustment:
- Check for file ownership conflicts
- Check independence score impact
- Check tier impact
- Check confidence score impact

Apply corrections. Record deferrals with named conditions.
Do not proceed to L3 until the team confirms L2.

---

## L3 — Execution

Only begin L3 after the team confirms L2.

### Step 16 -- Produce final phase breakdown document

Write `[SESSION_ROOT]/phase-breakdown.md` using the output structure in
`references/splitting-heuristics.md`. Include confidence summaries and any
spike briefs.

### Step 17 -- Populate the session manifest

1. Update `phase-breakdown.md` with final agreed phases
2. Populate the session manifest:
   - One entry per phase with all required fields from the template
   - Validate all file paths in scopedFiles exist in the codebase
   - Record any paths that cannot be validated as NEW (not an error)
   - Set `sessionState.parentBranch` to the current git branch name
     (the parent feature branch). This enables the sage-state-sync hook
     to push manifest updates for cross-machine visibility.
   - Write to [SESSION_ROOT]/session-manifest.md
   - Write session ID to .sage/sessions/active-session.txt
3. Bootstrap per-phase runtime:
   - Create `[SESSION_ROOT]/phase-{N}/` for every phase.
   - Write `[SESSION_ROOT]/phase-{N}/phase-manifest.json` for every phase.
   - Seed each phase runtime with:
     - `linearIssueStatus`: `"Pending Approval"`
     - `currentStep`: `"dev-interview"`
     - `buildMode`: `"autonomous"`
     - `validationConfirmed`: `false`
     - `stepStatus`: every configured phase step set to `"pending"`
     - `timestamps`: every configured phase step set to `null`
     - `batches`: `[]` unless Checkpoint mode is later selected

The root `session-manifest.md` stores session metadata, phase definitions,
session-level state, path validation, and kick-off outputs. Runtime fields
that hooks gate on live in `phase-{N}/phase-manifest.json`; keep those files
in sync with Linear and SAGE step transitions.

If L3 generation surfaces a file ownership conflict or phase boundary problem,
trigger a targeted L2 back-revision before continuing (see Back-revision rules).

### Step 18 -- Create Linear phase issues

Use the Linear MCP:
- One issue per phase
- Title: "[Feature title] -- Phase N: [objective]"
- Status: Pending Approval
- Custom field worktree_path: "phase-N/[kebab-objective]"
- Link upstream dependencies to their phase issues

### Step 19 -- Create git worktrees (Sprint mode only)

- Branch naming: "LIN-[issue-id]-phase-N-[kebab-objective]"
- Worktree path: C:\Sage\worktrees\[feature-id]\phase-N\

### Step 20 -- Team approval and transition to build sprint

After artifacts are generated, prompt the session driver for approval.
The approver is whoever is driving the kick-off session (Product Manager,
Lead Dev, or both).

1. Present a summary of all phases with their objectives, types, confidence
   scores, and effort estimates. Then ask:

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

If the session driver declines or requests changes, return to Step 15
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

**At the end of Step 15** (after team confirms the L2 breakdown but before
L3 artifact generation), emit:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"event":"phase_splitter_phases_proposed","workflowKind":"phase_splitter","linearIssueId":"[FEATURE_ID]","phaseCount":[N],"phases":[{"phaseId":"1","phaseType":"foundation","layer":"api","independenceScore":[N],"effortEstimateHours":{"low":[N],"high":[N]}}, ...]}'
```

**At the end of Step 19** (after manifest, Linear issues, and worktrees
are created), emit the completion event and bootstrap `workflow-telemetry.jsonl`:

```
python .cursor/hooks/scripts/prd_telemetry_append.py '{"event":"phase_splitter_completed","workflowKind":"phase_splitter","linearIssueId":"[FEATURE_ID]","sessionId":"[session ID]","phaseCount":[N],"manifestPath":"[SESSION_ROOT]/session-manifest.md","worktreesCreated":[true|false],"linearIssuesCreated":[N]}'
```

Then immediately write the bootstrap event to `workflow-telemetry.jsonl` so
the file exists before the orchestrator generates TDD specs and before any
Cursor hook fires:

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

---

## Back-revision rules

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the full
back-revision protocol (how to trigger, patch scope, change note format,
needs-recheck propagation, level counter preservation).

**Trigger conditions specific to phase-splitter** (also checked in Step 14):

- A phase boundary decision reveals two L1 groupings are more tightly coupled
  than the domain map showed
- A file ownership conflict surfaces a dependency not in the L1
  verified-dependency list
- An independence score below 60 indicates an L1 grouping boundary is wrong
- L3 manifest population surfaces a file ownership conflict or phase boundary
  problem

---

## Deferral rules

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the full deferral
protocol (condition requirement, carry-forward rules, open-deferrals section,
escalation vs deferral distinction).

**phase-splitter-specific downstream treatment:**

- Deferred phase boundary decisions produce a phase with `status: deferred`
  in the breakdown document and are noted in the manifest with the unblocking
  condition.
- A deferred dependency claim that remains open at L3 is listed in the
  `## Open deferrals` section of `phase-breakdown.md` so the team can see
  exactly what is unresolved before build begins.

---

## Spike recommendation

When a phase receives an overall recommendation of **SPIKE RECOMMENDED**, the
phase breakdown document includes a spike brief:

```markdown
**Spike recommended before build:**
Question: [specific unknown that must be resolved]
Scope: [files or interfaces to investigate]
Time-box: [suggested hours — typically 1-3]
Success condition: [what the spike must produce to unblock the phase]
Convert to: [Bug Batch Mode or Phase Gate Mode after spike]
```

The spike is run via `tdd-orchestrator` Spike Mode before the phase's S5
build gate opens. S1–S4 planning for the phase can proceed in parallel --
the spike does not block early planning steps.

---

## Constraints

- Do not run against a PRD below completeness threshold
- Do not assign named developers -- profile recommendations only
- Do not finalise the manifest until the team confirms L2
- Sprint mode only: create worktrees. Pair mode: skip worktree creation.
- Cannot approve Linear phase issues without explicit confirmation from the
  session driver (PM or Lead Dev) in the active kick-off session
- The existing independence score (0–100) is preserved unchanged --
  confidence scoring is additive, not a replacement

---

## Reference files

Read `references/splitting-heuristics.md` for:
- Splitting rules in order of application
- Independence scoring deduction table
- Effort estimation heuristics by layer and task type
- Confidence scoring criteria (dependency, effort, objective clarity)
- Overall recommendation decision rules
- Phase breakdown document output structure
