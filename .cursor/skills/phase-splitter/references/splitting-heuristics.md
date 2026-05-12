# Splitting Heuristics

Reference for phase-splitter. Contains splitting rules, independence
scoring deductions, effort estimation heuristics, and the phase breakdown
document output structure.

---

## Splitting rules (apply in order)

Rule 1 -- Layer boundary (primary split)
Split at the boundary between layers: database, API/service, UI, and
data-library. One phase per layer by default.
Exception: if a layer has zero files in scope, skip it.

Rule 2 -- File ownership conflict resolution
If two candidate phases share a file, one phase must own it exclusively.
Assign to the phase where the majority of changes to that file originate.
Record the file as a cross-phase dependency for the other phase.

Rule 3 -- Size constraint
If a single-layer phase is estimated over 8 hours, split it within the
layer using these sub-split boundaries:

  Database sub-splits:
    A: Schema changes + migrations
    B: Core CRUD stored procedures
    C: Edge case procedures + functions + views

  API sub-splits:
    A: Data models + repository / DAL
    B: Service layer + business logic
    C: Controllers + endpoints + error handling

  UI sub-splits:
    A: Component structure + data binding
    B: State transitions + interactions
    C: Error states + edge cases + empty states

  Data-library sub-splits:
    A: Models + interfaces
    B: DAL methods
    C: Helpers + utilities

Rule 4 -- Minimum size
If a candidate phase is estimated under 1 hour, merge it with the
most closely related adjacent phase. Record the merge rationale.

Rule 5 -- Shared stored procedure / view
If a stored procedure or view is called by multiple phases, it belongs
in its own phase (database layer). All calling phases depend on it.
Do not split shared procedures across phases.

Rule 6 -- Profitability calculation isolation
Phases that modify FTP calculations, expense allocation, income
allocation, capital allocation, or provisions must be isolated from
phases that only modify UI or reporting. Never mix calculation logic
with UI or reporting changes in the same phase.

Rule 7 -- Test isolation
Each phase must have at least one test that runs without any other
phase being built. If a proposed phase cannot be tested in isolation,
it must be re-split or merged into its dependency.

---

## Independence scoring deductions

Score starts at 100. Apply deductions:

| Condition | Deduction |
|-----------|-----------|
| Reads a file also written by another phase | -10 |
| Depends on a schema change in another phase | -15 |
| Depends on a stored procedure in another phase | -20 |
| Depends on an API endpoint in another phase | -15 |
| Shares a configuration file with another phase | -5 |
| Requires a runtime service started by another phase | -20 |
| Has more than two upstream dependencies | -10 additional |
| Cannot be tested without another phase's code present | -30 |

Phases scoring below 60 must be flagged. Possible resolutions:
- Extract the shared element into its own Foundation phase
- Merge the dependent phase into its dependency
- Accept the low score and assign Dependent type (blocks at S5)

---

## Effort estimation by layer and task type

These are baseline estimates for the Profitability codebase. Calibrate
against intel-advisor historical data when available.

Database tasks:
  New stored procedure (standard CRUD): 1.5-2.5 hours
  New stored procedure (calculation logic): 3-5 hours
  Modify existing stored procedure: 1-3 hours
  New view: 0.5-1.5 hours
  Schema migration: 0.5-2 hours
  Test coverage for each procedure: 0.5-1 hour

API / service tasks:
  New service method: 1-2 hours
  New endpoint + controller: 1-2 hours
  Modify existing service: 0.5-1.5 hours
  Repository / DAL method: 0.5-1 hour
  Test coverage: 0.5-1 hour per method

UI tasks:
  New component (simple): 2-3 hours
  New component (with multiple states): 3-5 hours
  Modify existing component: 1-2 hours
  New page / view: 3-6 hours
  Test coverage (component): 1-2 hours

Effort range formula:
  Phase low estimate = sum of task low estimates
  Phase high estimate = sum of task high estimates * 1.2 (complexity buffer)

---

## Phase breakdown document output structure

Write [SESSION_ROOT]/phase-breakdown.md with this structure:

``````markdown
# Phase Breakdown -- [Feature title]

**Feature:** [Linear feature issue ID]
**Generated:** [ISO date]
**Mode:** [Sprint / Pair]
**Phase count:** [N]

## Tier structure

Foundation phases (start immediately): Phase [N], Phase [N]
Independent phases (start immediately): Phase [N]
Dependent phases (wait for Foundation Verified): Phase [N]

## Dependency map

Phase [N] (Foundation) --> Phase [N] (Dependent)
Phase [N] (Independent) --> (no dependents)

## Phases

### Phase 1: [Objective]

**Type:** Foundation / Independent / Dependent
**Layer:** database / api / ui / data-library / full-stack
**Independence score:** [N]/100 [OK / FLAGGED: reason]
**Effort range:** [low]-[high] hours
**Developer profile:** [profile]

**Files in scope:**
- [exact file path] -- [what changes]
- ...

**Upstream dependencies:** [None / Phase N (reason)]
**Downstream consumers:** [None / Phase N (reason)]

**Test approach:**
[How this phase will be tested in isolation]

### Phase 2: ...

## Flags

[Any phases flagged for low independence score or effort outside range,
with recommended resolution]

## Adjustment notes

[Record any changes the team makes during kick-off review]
``````

