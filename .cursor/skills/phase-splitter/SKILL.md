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
| PRD | Notion page (must be at Linear status Ready) | Yes |
| Component specification | Notion child page | Yes (UI features) |
| Phase-splitter briefing | [SESSION_ROOT]/phase-splitter-briefing.md | Yes (Sprint/Mob) |
| Codebase | Read access via Cursor file system | Yes |
| Session manifest template | .cursor/templates/session-manifest-template.md | Yes |

Do not run this skill against a PRD that has not passed prd-completeness-check.

---

## Step 1 -- Load all inputs

Fetch the PRD and component specification from Notion.
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

5. Report completion:
   "[N] phases finalised. Session manifest written. Linear issues and
   worktrees created. Product Manager and Lead Dev will approve phase
   issues async -- phases unlock when status moves to Approved."

---

## Constraints

- Do not run against a PRD below completeness threshold
- Do not assign named developers -- profile recommendations only
- Do not finalise the manifest until the team confirms the breakdown
- Sprint mode only: create worktrees. Pair mode: skip worktree creation.
- Cannot auto-approve Linear phase issues -- approval is human-only

---

## Reference files

Read references/splitting-heuristics.md for:
- Splitting rules in order of application
- Independence scoring deduction table
- Effort estimation heuristics by layer and task type
- Phase breakdown document output structure

