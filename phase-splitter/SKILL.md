---
name: phase-splitter
description: >
  Analyses a completed PRD and the Profitability codebase to generate a
  recommended phase breakdown for a Sprint or Pair work stream.
  Scores each candidate phase for independence, identifies dependency chains,
  estimates effort, and produces a phase breakdown document for team review
  at the kick-off session. Use this skill during Step 2 of the kick-off
  session (Phase Breakdown) for every Sprint and Pair work stream.
  Do not manually define phases before running this skill — the skill's
  output is the starting point for team adjustment, not a blank discussion.
---

# Phase Splitter

Generates a recommended phase breakdown from a PRD that has passed
`prd-completeness-check`. Produces a single recommended split with
independence scores, dependency chain, effort estimates, and developer
profile recommendations. The team reviews and adjusts at kick-off —
the skill provides the starting point, not the final answer.

**Design principle:** A good phase has exactly one objective, is
independently testable without any other phase being complete, and can
be owned entirely by one developer. If a phase requires coordination
with another developer mid-execution, it needs to be re-split.

---

## Inputs required

| Input | Source | Required |
|---|---|---|
| PRD | Notion page (must be at Linear status `Ready`) | Yes |
| Component specification | Notion child page linked from PRD | Yes |
| Codebase | Read access via Cursor file system | Yes |
| Session manifest template | `.cursor/templates/session-manifest.md` | Yes |

Do not run this skill against a PRD that has not passed
`prd-completeness-check`. If the PRD is not at `Ready` status in Linear,
stop and notify the PM.

---

## Step 1 — Load the PRD and component specification

Fetch the full PRD and its Component Specification child page from Notion.
Extract and record:

- Complete requirements list (REQ-N identifiers)
- Screen inventory (pages and screens affected)
- Component inventory (from component spec — new, affected, reused)
- Data operations (reads and writes — tables, stored procedures, views)
- Out-of-scope section
- Any existing phase suggestions noted in the PRD

---

## Step 2 — Codebase reconnaissance

Scan the codebase to identify the full set of files this feature will
touch. Record findings across four categories:

**UI files:**
- Page/view files for each affected screen
- Component files for each new or affected component
- Style files if component-specific styles are being added
- Route or navigation files if navigation is changing

**Backend / API files:**
- Stored procedures being created or modified (`usp_` prefix)
- Views being created or modified (`vw_` prefix)
- Functions being created or modified (`fn_` prefix)
- API controllers or endpoints being added or changed

**Data / schema files:**
- Migration files or schema change scripts
- Seed data or reference data files (e.g. ProcessID reference updates)
- Any configuration files that define GL code ranges or ProcessID mappings

**Test files:**
- Existing test files for affected components or stored procedures
- Test fixtures or seed data that will need updating

Record every file in a working inventory. This inventory is the input
to the dependency analysis in Step 4.

---

## Step 3 — Generate candidate phases

Apply the splitting heuristics in `references/splitting-heuristics.md`
to generate candidate phases. Read that file now before proceeding.

Each candidate phase must have:
- A single, clearly named objective
- An explicit scope: which files, components, stored procedures, and
  data operations it owns
- No file that appears in two phases' scope (file ownership is exclusive)
- At least one independently runnable test

Generate phases by working through the heuristics in order:

1. Identify natural layer boundaries (data, API/backend, UI)
2. Identify discrete user-facing capabilities within the feature
3. Identify component boundaries for complex new UI components
4. Check for shared infrastructure that must be built first
5. Merge phases that are too small (<2 hours estimated) if they can
   be merged without creating file ownership conflicts
6. Split phases that are too large (>6 hours estimated) if a clean
   boundary exists

Aim for phases in the 2–5 hour range. Prefer more smaller phases over
fewer larger ones — parallel execution means smaller phases complete
faster and unblock downstream phases sooner.

---

## Step 4 — Score independence for each phase

For each candidate phase, calculate an independence score (0–100).

Score starts at 100. Apply deductions per `references/splitting-heuristics.md`
→ Independence scoring section.

A phase scoring below 60 is a flag — it has significant dependencies
that will create coordination overhead. Present these prominently in
the output and suggest resolution options (re-split, reorder, or
accept with documented interface contract).

Record for each phase:
- Independence score
- Which other phases it depends on (upstream dependencies)
- Which phases depend on it (downstream consumers)
- The nature of each dependency (file, data, interface, or test)

---

## Step 5 — Build the dependency map

From the dependency records, build the execution order:

- **Tier 0:** Phases with no upstream dependencies — can start immediately
  in parallel at build sprint start
- **Tier 1:** Phases that depend only on Tier 0 phases — unlock when their
  upstream Tier 0 completion report is posted
- **Tier 2:** Phases that depend on Tier 1 phases — and so on

If any phase has dependencies on multiple phases across different tiers,
it belongs to the highest tier of its dependencies.

A healthy phase breakdown for a Sprint session has most phases
in Tier 0 — parallel from the start. If most phases are in Tier 1 or
higher, the feature should be reconsidered for a sequential (Pair or Solo)
work stream rather than Sprint.

---

## Step 6 — Estimate effort per phase

For each phase, produce an effort range in hours using the estimation
heuristics in `references/splitting-heuristics.md` → Effort estimation
section.

Express as: `[low]–[high] hours`

Also produce a total range for the full feature:
`Total estimated effort: [low]–[high] hours across [N] phases`

Note that this is agent execution time, not calendar time. Parallel
execution means calendar time ≈ longest dependency chain, not total hours.

---

## Step 7 — Recommend developer profiles per phase

For each phase, note which developer profile is best suited based on
phase content:

- **UI-heavy:** Developer with strongest front-end / component experience
- **Backend-heavy:** Developer with strongest stored procedure / data layer
  experience
- **Full-stack:** Phase spans UI and backend — developer needs both
- **Data-only:** Stored procedure, migration, or reference data change only
- **Any:** Phase is self-contained and any developer can execute it

Do not assign named developers — that happens at the planning cycle.
Profile recommendations inform the assignment decision.

---

## Step 8 — Produce the phase breakdown document

Use `references/phase-breakdown-template.md` to structure the output.

Save as `[SESSION_ROOT]/phase-breakdown.md`.

Also produce a summary for verbal presentation at the kick-off session —
a short version that can be read aloud in 2–3 minutes covering: phase
count, tier structure, total effort range, any independence flags.

---

## Step 9 — Present at kick-off and facilitate adjustment

At the kick-off session, present the recommended breakdown to the team.
Walk through:

1. Phase count and names — does the team agree the objectives are right?
2. Tier structure — does the dependency ordering make sense?
3. Any independence flags — does the team accept the dependency or want
   to re-split?
4. Effort ranges — does the team's intuition agree?
5. Developer profile recommendations — any concerns?

Facilitate adjustments. For each proposed change, check:
- Does the change create a file ownership conflict?
- Does it change any phase's independence score significantly?
- Does it change the tier structure?

Update the breakdown document with agreed changes. Do not finalize
until the team confirms.

---

## Step 10 — Finalize and feed the session manifest

Once the team confirms the breakdown:

1. Update `phase-breakdown.md` with final agreed phases
2. Populate the session manifest template:
   - One entry per phase with: name, objective, scope, tier, effort range,
     developer profile, upstream dependencies
   - Validate all file paths in scope exist in the codebase
   - Record any paths that cannot be validated (may be new files to be
     created — note explicitly as NEW rather than failing)
3. Create Linear issues — one per phase:
   - Title: `[Feature title] — Phase N: [objective]`
   - Status: `Pending Approval` (awaiting the Product Manager and Lead Dev async approval)
   - Custom field: `worktree_path` = `phase-N/[kebab-objective]`
   - Dependencies linked to upstream phase issues
4. Create git worktrees — one per phase:
   - Branch naming: `LIN-[issue-id]-phase-N-[kebab-objective]`

Report completion to the team:
> "[N] phases finalised. Linear issues and worktrees created.
> the Product Manager and Lead Dev will approve async — phases unlock in Linear
> when their issue status moves to Approved."

---

## Reference files

- `references/splitting-heuristics.md` — splitting rules, independence
  scoring deductions, effort estimation heuristics
- `references/phase-breakdown-template.md` — output document template
