# Splitting Heuristics

Reference for phase-splitter. Contains splitting rules, independence
scoring deductions, effort estimation heuristics, confidence scoring
criteria, overall recommendation decision rules, and the phase breakdown
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
against intel-advisor historical data when available. Note in the phase
breakdown when estimates deviate significantly from historical actuals.

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

Effort confidence adjustments:
  >70% net-new tasks in a phase: add 20% to high estimate (higher variance)
  Phase requires 4+ test layers: flag for effort review, likely over 8 hours
  Historical data available and estimate deviates >40%: note and explain

---

## Confidence scoring criteria

Each phase is scored on three dimensions. Use these criteria to assign
HIGH / MEDIUM / LOW for each dimension.

### Dimension 1: Dependency confidence

Is the dependency analysis based on verified code or inferred from the PRD?

| Rating | Criteria |
|--------|----------|
| HIGH | Every dependency claim is traced to a specific file, method, or data contract in the codebase. The interface contract at each phase boundary is named. |
| MEDIUM | Most dependencies are verified-in-code. One or two are inferred from PRD language with no direct code trace found. |
| LOW | At least one dependency is assumption-confidence. No code trace exists for it and it cannot be resolved from the PRD alone. |

Checks that build dependency confidence:
- **Interface trace**: for each phase boundary, name the exact file and method
  of the data contract. If it does not exist yet, specify the exact signature
  the consuming phase needs.
- **Shared mutable state audit**: identify shared tables, views, config objects,
  or global services that multiple phases write to. These are hidden coupling
  points not visible from the PRD.
- **Test independence check**: can a failing test be written for this phase
  without another phase being built? If not, the phases are coupled regardless
  of PRD intent.

### Dimension 2: Effort confidence

Is the effort estimate grounded in the codebase or derived from PRD complexity alone?

| Rating | Criteria |
|--------|----------|
| HIGH | Estimate is grounded in delta classification (net-new vs extending) + test layer count + intel-advisor historical data for similar phases. |
| MEDIUM | Estimate is grounded in delta classification and test layer count. No intel-advisor historical data available. |
| LOW | Estimate is derived from PRD complexity alone. No delta classification or test layer analysis performed. |

Checks that build effort confidence:
- **Delta classification**: what proportion of the phase is net-new vs extending
  existing code? Net-new is higher variance. >70% net-new with an L estimate
  should be flagged.
- **Test layer count**: how many test layers does this phase require (unit,
  integration, E2E, architecture guard, component, Playwright)? Each layer adds
  time. A phase needing all layers is likely too large.
- **Historical calibration**: if intel-advisor data exists for similar phase
  types and layers, use it. Note significant deviation from historical actuals.

### Dimension 3: Objective clarity

Is the phase's single objective genuinely single?

| Rating | Criteria |
|--------|----------|
| HIGH | Objective is stated in one sentence with one verb. Anticipated TDD scenarios cluster around a single file group or layer boundary. Reviewer needs context from one domain only. |
| MEDIUM | Objective is clear but anticipated TDD scenarios fall into two loosely related groups. A case can be made for either merging or splitting. |
| LOW | Objective requires "and" to state. Anticipated TDD scenarios fall into two distinct clusters with no shared context. Reviewer would need context from two separate domains. |

Checks that build objective clarity:
- **TDD scenario clustering**: group the phase's anticipated TDD scenarios by
  file or layer touched. Two distinct clusters with no overlap = split candidate.
- **Single-sentence test**: state the phase objective in one sentence. If "and"
  is required, it is likely two phases.
- **Reviewer scope prediction**: what does a reviewer need to understand to
  review this phase? Two domains = split candidate.

---

## Overall recommendation decision rules

Apply in order. Use the first rule that matches.

| Condition | Recommendation |
|-----------|---------------|
| Objective clarity = LOW | SPLIT RECOMMENDED (regardless of other dimensions) |
| Any dimension LOW + blast radius cross-phase | SPIKE RECOMMENDED |
| Any dimension LOW + blast radius phase-only | REVIEW BEFORE BUILD |
| All dimensions MEDIUM or above | PROCEED |

Blast radius definitions:
- **Cross-phase**: the uncertainty affects other phases' scope, sequencing, or
  interface contracts (e.g. a Foundation phase with LOW dependency confidence)
- **Phase-only**: the uncertainty is contained within this phase and does not
  affect other phases' plans (e.g. an Independent phase with LOW effort confidence)

---

## Phase breakdown document output structure

Write `[SESSION_ROOT]/phase-breakdown.md` with this structure:

```markdown
# Phase Breakdown -- [Feature title]

**Feature:** [Linear feature issue ID]
**Generated:** [ISO date]
**Mode:** [Sprint / Pair]
**Phase count:** [N]

## Tier structure

Foundation phases (start immediately): Phase [N], Phase [N]
Independent phases (start immediately): Phase [N]
Dependent phases (wait for Foundation Verified): Phase [N]

## Parallel streams

[Describe which phases can run simultaneously and with how many developers]

## Dependency map

Phase [N] (Foundation) --> Phase [N] (Dependent) — [contract: file/method name]
Phase [N] (Independent) --> (no dependents)

## Phases

### Phase 1: [Objective]

**Type:** Foundation / Independent / Dependent
**Layer:** database / api / ui / data-library / full-stack
**Independence score:** [N]/100 [OK / FLAGGED: reason]
**Effort range:** [low]-[high] hours
**Developer profile:** [profile]

**Files in scope:**
- [exact file path] -- [what changes] -- [net-new / extending]
- ...

**Upstream dependencies:** [None / Phase N (contract: file/method name)]
**Downstream consumers:** [None / Phase N (reason)]

**Test approach:**
[How this phase will be tested in isolation]

**Confidence summary:**
Dependency confidence:  HIGH / MEDIUM / LOW  — [one-line basis, e.g. "all deps traced to specific files"]
Effort confidence:      HIGH / MEDIUM / LOW  — [one-line basis, e.g. "60% net-new, 3 test layers, no historical data"]
Objective clarity:      HIGH / MEDIUM / LOW  — [one-line basis, e.g. "single verb, scenarios cluster around one SP group"]
Overall recommendation: PROCEED / REVIEW BEFORE BUILD / SPLIT RECOMMENDED / SPIKE RECOMMENDED

[Include spike brief if SPIKE RECOMMENDED — see spike brief structure below]

### Phase 2: ...

## Open deferrals

[Any phase boundary decisions or dependency claims deferred with named
unblocking conditions. Format: Decision | Unblocking condition | Affects]

## Flags

[Any phases flagged for low independence score, effort outside range,
or confidence dimensions, with recommended resolution]

## Adjustment notes

[Record any changes the team makes during kick-off review, including
back-revisions applied with their change notes]
```

---

## Spike brief structure

Include in the phase section when overall recommendation = SPIKE RECOMMENDED:

```markdown
**Spike recommended before build:**
Question: [specific unknown that must be resolved — one sentence]
Scope: [exact files or interfaces to investigate]
Time-box: [suggested hours — typically 1-3]
Success condition: [what the spike must produce to unblock the phase]
Convert to: [Bug Batch Mode or Phase Gate Mode after spike]
```

The spike runs via `tdd-orchestrator` Spike Mode before the phase's S5 build
gate opens. S1–S4 planning for the phase can proceed in parallel.
