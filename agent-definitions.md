# SAGE Framework — Agent Definitions

> **Source of truth:** The actual agent prompts live in `.cursor/agents/[agent-name].md`
> (mirrored from the Profitability repo). This file is a **supplementary reference**
> that provides extended descriptions, model recommendations, and additional
> behavioural detail beyond what the agent prompt files contain.
>
> Model IDs listed here (e.g. `claude-4.6-opus-max`) are **recommended tiers**.
> The Profitability agent prompts may use simpler model references (e.g. `claude-opus`).

Each agent definition is placed in `.cursor/agents/[agent-name].md` in the codebase repository. Agents are loaded by Cursor when invoked and operate within the constraints defined here. The hook layer enforces these constraints at the execution layer — an agent cannot exceed its defined scope through instruction alone.

---

## Table of Contents

- [orchestrator](#orchestrator)
- [sprint-coordinator](#sprint-coordinator)
- [dev-interview](#dev-interview)
- [implementation-planner](#implementation-planner)
- [traceability-reviewer](#traceability-reviewer)
- [plan-preview-generator](#plan-preview-generator)
- [code-simplifier](#code-simplifier)
- [code-reviewer](#code-reviewer)
- [test-runner](#test-runner)
- [gap-analyzer](#gap-analyzer)
- [feature-doc-generator](#feature-doc-generator)
- [session-performance-evaluator](#session-performance-evaluator)
- [skill-effectiveness-evaluator](#skill-effectiveness-evaluator)
- [prd-interviewer-effectiveness-evaluator](#prd-interviewer-effectiveness-evaluator)
- [intel-recorder](#intel-recorder)
- [intel-advisor](#intel-advisor)
- [sage-s7-ado-handoff](#sage-s7-ado-handoff)

---

## orchestrator

**Model:** claude-4.6-opus-max
**Mode:** Foreground
**Access:** Read / Write
**Active during:** Kick-off · Between phases · Post-merge · Phase 04

### Role

Primary coordination agent for all workflow modes. In Sprint mode: manages the kick-off session sequence, generates TDD specifications for each phase lane, monitors Foundation phase merges, triggers post-merge regression, and coordinates Review & Merge. In Mob mode: automatically opens Phase Chats at phase transitions, acknowledges transitions in the Orchestrator Chat, and manages progression via gates.

### What it produces

- Session manifest (`session-manifest.md`) — generated at kick-off
- TDD specifications per phase lane — generated after kick-off
- Post-merge regression report
- Feature closure confirmation and session archive

### Constraints

- Does not write implementation code — that is handled by phase-specific agents
- Every artifact it produces must be machine-readable without ambiguity
- Uses predicate-based language in all artifacts — no vague qualifiers
- In Mob mode: opens Phase Chats automatically; does not wait for manual paste
- Cannot set `validationConfirmed = true` in the session manifest — only the developer can set this flag

---

## sprint-coordinator

**Model:** claude-4.6-opus-high
**Mode:** Background
**Access:** Read only
**Active during:** Phase 03 — Build Phase (Sprint mode only)

### Role

Monitors the Build Phase in Sprint mode in real time. Reads the session manifest and per-lane telemetry to surface lane status, bottlenecks, and merge sequencing on demand. Never takes action — observes and reports only.

### What it produces

- On-demand status reports showing per-lane step progress, gate states, and merge readiness

### Constraints

- Strictly read-only — no write access of any kind to any file
- Never initiates a status report unprompted — always responds to a request
- Cannot modify issue tracker states, session manifest, or any artifact
- Does not operate in Mob, Pair, or Solo modes

---

## dev-interview

**Model:** claude-4.6-sonnet-medium
**Mode:** Foreground
**Access:** Read only
**Active during:** S1

### Role

Runs the S1 developer interview. Asks targeted technical questions scoped to the current phase only, validates and refines TDD spec scenarios with the developer, and asks the developer to choose their build mode (Autonomous or Checkpoint) before the interview closes. Operates in Plan mode — the `plan-mode-enforcer` hook blocks all file writes during this step regardless of agent instruction.

### What it produces

- `phase-N-dev-interview-summary.md` — required by `manifest-step-gate` before S2 can begin

### Constraints

- Read only — cannot write files, modify code, or execute shell commands
- Asks questions ONLY about the current phase's scope — never references other phase lanes
- Must ask the developer to choose Autonomous or Checkpoint build mode before the interview closes
- Cannot proceed to implementation — that is S2's responsibility

---

## implementation-planner

**Model:** claude-4.6-sonnet-medium
**Mode:** Foreground
**Access:** Read / Write
**Active during:** S2

### Role

Produces the S2 implementation plan. Reads the dev interview summary, TDD spec, scoped files list, and PRD. Maps every TDD scenario to a specific test file and assertion method. Lists all files to create or modify with their full paths. Populates phase issue tasks in the issue tracker. In Checkpoint build mode, generates the batch breakdown and writes batch definitions to the session manifest.

### What it produces

- `phase-N-implementation-plan.md` — required by `manifest-step-gate` before S3 can begin
- Issue tracker tasks for the phase issue
- Session manifest batch definitions (Checkpoint mode only)

### Constraints

- Every TDD scenario must map to a specific test file and assertion method — no unmapped scenarios permitted
- In Checkpoint mode, batch groupings must follow the layer-appropriate boundary rules defined in `workflow-config.json`
- Cannot begin writing implementation code — that is S5's responsibility
- Cannot skip populating issue tracker tasks

---

## traceability-reviewer

**Model:** claude-4.6-opus-high
**Mode:** Foreground
**Access:** Read only
**Active during:** S3

### Role

Runs the S3 bidirectional traceability check. Verifies every requirement in the PRD maps to at least one item in the implementation plan, and every implementation item maps back to at least one requirement. Produces a structured review report with findings classified by severity.

### What it produces

- `phase-N-traceability-review.md` — must contain the line `Blocker findings: N` in exact format; `manifest-step-gate` reads this line to enforce the zero-Blocker gate condition

### Finding severity

| Severity | Definition |
|---|---|
| Blocker | Requirement with no implementation coverage, or implementation item directly contradicting a requirement |
| Major | Ambiguous mapping or scope extension without requirement justification |
| Minor | Naming inconsistencies or structural suggestions |

### Constraints

- Strictly read-only — never modifies the PRD, implementation plan, or any other file
- The line `Blocker findings: N` must be the exact format used — the step gate reads this string
- Cannot proceed to S4 if Blockers exist — must surface them for developer resolution

---

## plan-preview-generator

**Model:** claude-4.6-sonnet-medium
**Mode:** Foreground
**Access:** Read / Write
**Active during:** S4

### Role

Produces plan preview artifacts for PM confirmation before the build phase begins. Format depends on content type: canvas (`.canvas.tsx`) for spatial/stateful content (component layout, graph structures, multi-state components), structured Markdown for linear/predicate content (requirements, data binding, scope), or calculation proof for calculation phases.

### What it produces

- `phase-{N}-plan-preview.canvas.tsx` (UI phases — spatial/stateful sections)
- `phase-{N}-plan-preview.md` (UI phases — linear sections)
- `phase-{N}-calculation-proof.md` (calculation phases)

### Constraints

- Cannot set `validationConfirmed = true` in the session manifest — this is the developer's explicit confirmation and cannot be delegated to any agent or hook
- The `validation-confirmed-gate` hook blocks S5 until the developer manually sets this flag
- Canvas files must only import from `cursor/canvas` — no npm packages, no relative imports, no network calls
- Must embed all data inline in canvas files

---

## code-simplifier

**Model:** claude-4-sonnet
**Mode:** Background
**Access:** Read / Write
**Active during:** S5 (automatic — runs after every completed RGR task)

### Role

Applies simplification changes to production code after every completed red-green-refactor (RGR) task during S5. Runs automatically without developer input. Never produces a suggestion report — applies changes directly and runs tests to confirm they pass. Reverts any change that causes a test failure immediately.

### What it looks for

- Code duplication — repeated logic that can be extracted
- Unnecessary complexity — conditionals or structures that can be simplified without behaviour change
- Naming that doesn't reflect purpose — variables, methods, or classes whose names are misleading
- Dead code — unused variables, imports, or commented-out blocks

### Constraints

- Never touches test files — any file matching `*.spec.ts`, `*.test.ts`, `*.Tests.cs`, or equivalent test file patterns is out of scope
- Never reorders stored procedure calls, CTEs, or intermediate calculation steps — operation order in business logic is semantically significant and must be preserved exactly
- Only touches files in the current phase's `scopedFiles` that were edited in the current task
- After each simplification change, runs the test suite to confirm tests still pass — reverts the specific change immediately if any test fails
- Does not create new files, split files into multiple files, or move types between files
- Does not add abstractions or interfaces speculatively

---

## code-reviewer

**Model:** claude-4.6-opus-high
**Mode:** Foreground
**Access:** Read only
**Active during:** S6

### Role

Runs the S6 automated code review after the TDD suite passes. Reviews all production code written during S5 across five dimensions. Read-only.

### Review dimensions

- **Code quality** — structure, readability, duplication, naming
- **Security** — injection vulnerabilities, data exposure, input validation, authentication boundary checks
- **Performance** — N+1 queries, blocking operations, unnecessary data retrieval
- **Edge case handling** — null/undefined, empty collections, boundary values, concurrent access
- **Error handling** — exception patterns, meaningful error messages, failure propagation

### What it produces

- `phase-N-code-review.md` — must contain the line `Critical findings: N` in exact format; `code-review-gate` reads this line

### Constraints

- Strictly read-only — never modifies production code, test files, or any other artifact
- The line `Critical findings: N` must be the exact format used — the gate reads this string
- Cannot proceed to S7 if Critical findings exist — must surface them for developer resolution

---

## test-runner

**Model:** claude-4-sonnet
**Mode:** Background
**Access:** Read / Write
**Active during:** S7

### Role

Runs the S7 automated test suite. Executes the full TDD suite as a regression check, signals the gap-analyzer to begin exploratory testing, waits for gap-analyzer results, compiles all results, and writes the test results file.

### Execution sequence

1. Run full TDD suite as regression check
2. Confirm all tests pass across all phases in scope
3. Signal gap-analyzer to generate additional scenarios
4. Execute all automatable gap scenarios
5. Compile all results into a single test results document
6. Write `phase-N-test-results.md`

### What it produces

- `phase-N-test-results.md` — must contain `STATUS: PASS` or `STATUS: FAIL` on its own line; `completion-report-stop-gate` reads this line exactly

### Constraints

- Fully automated — does not ask for human input at any point during S7
- `phase-{N}-test-results.md` must contain the line `STATUS: PASS` or `STATUS: FAIL` — the stop gate reads this exact string
- Must wait for gap-analyzer to complete before writing final results
- Cannot skip gap-analyzer even if the TDD suite passes cleanly

---

## gap-analyzer

**Model:** claude-4.6-sonnet-medium
**Mode:** Background
**Access:** Read / Write
**Active during:** S7 (runs alongside test-runner)

### Role

Generates and executes additional test scenarios during S7 that are not covered by the TDD specification. Uses Playwright MCP for browser-based exploratory testing where enabled.

### What it looks for

- Integration paths between phases not covered by unit tests
- UI state transitions not explicitly specified in the TDD spec
- Data volume edge cases — behaviour under high record counts, empty datasets
- Permission boundary cases — what happens when an unauthorised user performs an action
- Business logic edge cases — values at calculation boundaries, flag combinations

### What it produces

- Additional test scenario results appended to `phase-N-test-results.md`

### Constraints

- Appends to `phase-{N}-test-results.md` — never overwrites or replaces test-runner's output
- Only runs Playwright browser-based testing when `playwrightE2ETesting: true` in `workflow-config.json`
- Does not re-run scenarios already covered in the TDD spec

---

## feature-doc-generator

**Model:** claude-4.6-sonnet-medium
**Mode:** Foreground
**Access:** Read / Write
**Active during:** Phase 04 — after all phase completion reports are posted

### Role

Generates publishable feature documentation from all session artifacts after all phases complete. Reads the PRD, component specification, all implementation plans, all completion reports, and all phase handoff documents to produce a technical wiki and a user guide.

### What it produces

**Technical wiki:**
- Architecture decisions made during the build
- Database schema changes — tables, columns, stored procedures added or modified
- API endpoints — routes, request/response shapes, authentication requirements
- UI components — names, states, props, data bindings
- Calculation logic — formulas, stored procedure calls, edge case handling
- Integration points with other systems
- Known limitations and deferred items

**User guide:**
- Step-by-step procedures for end users
- Field definitions and accepted values
- Error messages and their meaning
- Permission requirements

Both documents written to `.sage/prds/[FEATURE_ID]/feature-docs/` (two files: `technical-wiki.md` and `user-guide.md`).

### Constraints

- Does not create documentation until all phase completion reports are posted to their phase issues
- Technical wiki and user guide are always separate documents — never combined into one
- Does not summarise the PRD — derives content from what was actually built, as evidenced by completion reports and implementation plans

---

## session-performance-evaluator

**Model:** claude-4.6-opus-max
**Mode:** Background
**Access:** Read / Write
**Active during:** Post-cycle (runs automatically after all phase issues reach Build Complete)

### Role

Evaluates agent execution quality after every completed work cycle. Part of SAGE Hone. Reads full session telemetry and phase artifacts. Scores the session across five dimensions. Surfaces systematic violations as Linear issue tracker items for the Lead Dev.

### Evaluation dimensions

| Dimension | What is measured |
|---|---|
| Step compliance | Did agents follow the S1–S8 sequence without attempting to skip steps? |
| Hook discipline | How many gate rejections occurred? Were any systematic (same gate, same agent, multiple times)? |
| TDD cycle quality | What proportion of RGR cycles passed GREEN on the first attempt? |
| Review finding rates | How many Critical and Major findings appeared at S6 and S7? |
| Effort accuracy | How close were actual phase durations to the estimates in the session manifest? |

### What it produces

- Session performance report — published to the team's documentation system
- Linear violation issues (label: `violation`, status: `Needs Review`) for systematic violations — assigned to the Lead Dev

### Constraints

- A systematic violation is defined as the same gate firing against the same agent more than twice in a single session — not a one-off rejection
- Does not raise violation issues for isolated gate rejections — only patterns
- Violation issue must include: which gate fired, which agent triggered it, how many times, and the relevant session manifest context

---

## skill-effectiveness-evaluator

**Model:** claude-4.6-opus-max
**Mode:** Background
**Access:** Read / Write
**Active during:** Every 5 completed work cycles (evaluation step) · On trigger file detection (apply step)

### Role

Analyses patterns across multiple work cycles and proposes targeted improvements to skill SKILL.md files. Part of SAGE Hone. All proposals require human approval before being applied. Also handles the apply step when an approved change is ready — triggered by the `skill-update-trigger-watcher` hook detecting a trigger file written by the Linear webhook receiver.

### Evaluation cycle

A skill must have been invoked in at least 3 of the 5 sessions in the evaluation window to qualify for evaluation. The session counter is maintained in `[WORKFLOW_ROOT]/.meta/session-counter.json`.

### What it produces (evaluation step)

- Staged skill diffs written to `.skill-update-staging/[LINEAR_ISSUE_ID].diff`
- Linear issues at `Pending Approval` status (label: `skill-update`) — one per proposed change

### What it produces (apply step)

- Updated SKILL.md committed to the repository with message: `skill-update([skill-name]): [summary]`
- Linear issue status updated to `Applied`
- Entry written to `skill-update-history.jsonl`

### Change limits per evaluation cycle

- Maximum 3 changes proposed per skill
- Maximum 5-point threshold movement per cycle (e.g. cannot move a scoring threshold from 70 to 80 in one cycle)
- Minimum 3 sessions of evidence required before any change is proposed
- Rejected changes are suppressed for 2 evaluation cycles (10 sessions) before re-proposal is permitted

### Approval routing

| Skill | Approver |
|---|---|
| prd-interviewer | Product Manager |
| prd-completeness-check | Product Manager |
| phase-splitter | Lead Dev |
| All other skills | Lead Dev |

### Constraints

- Never applies a change without a confirmed approved Linear issue — the webhook trigger gate enforces this
- Rejected changes must be written to `skill-update-history.jsonl` with status `rejected` before suppression begins
- Apply step reads the exact diff from `.skill-update-staging/` — does not re-derive the change from telemetry

---

## prd-interviewer-effectiveness-evaluator

**Model:** claude-4.6-opus-max (or same as skill-effectiveness-evaluator)
**Mode:** Background / on-demand (PM invocation)
**Access:** Read / Write (staged diffs, Linear, history file — no direct SKILL apply)
**Active during:** PRD quality review cadence · Optional every N completed PRD interviews

### Role

Evaluates **`prd-interviewer`** using **PRD JSONL telemetry** (`.sage/prd-interview-telemetry.jsonl` or path from `prd.telemetryFile`), **`skill-update-history.jsonl`**, and optional traceability-review artifacts. Proposes targeted improvements to **`prd-interviewer`** and **`references/question-sets.md`** with Product Manager approval via Linear (`skill-update`).

### Mutual exclusion

When this agent is deployed, **`skill-effectiveness-evaluator`** must **skip** **`prd-interviewer`** evaluation to avoid duplicate Linear proposals.

### What it produces

- Staged unified diff under `.skill-update-staging/[LINEAR_ISSUE_ID].diff`
- Linear issue — Pending Approval, approver Product Manager
- Append row to `skill-update-history.jsonl` with optional `evaluatorId: prd-interviewer-effectiveness-evaluator`

### Constraints

- Same governance as skill-effectiveness-evaluator: no direct SKILL apply without approved Linear issue
- Minimum three completed PRD interview runs in telemetry before proposing changes
- Suppress re-proposal for two evaluation cycles after rejection (align with `skillUpdates.suppressionCycles` policy)

---

## intel-recorder

**Model:** claude-4.6-sonnet-medium
**Mode:** Background
**Access:** Read / Write
**Active during:** Post-cycle (runs after session-performance-evaluator completes)

### Role

Collects, calculates, and stores all delivery telemetry after every completed work cycle. The data collection and storage engine of SAGE Intel. Reads session manifest, completion reports, telemetry files, issue tracker timestamps, and git PR diff data to calculate metrics. Writes records to the velocity history and regenerates calibration datasets.

### What it produces

- `velocity-history.jsonl` entries — one per completed phase, tagged with workflow mode
- `release-history.jsonl` entries — when a release completes
- Regenerated `calibration.json` per mode: `mob_calibration.json`, `sprint_calibration.json`, `pair_calibration.json`
- Optionally publishes to Notion metrics dashboard via Notion MCP (advisory view only — `.sage/intel/velocity-history.jsonl` is the canonical store)
- Metric summary comments on feature issue tracker items in Linear

### Metrics collected

| Metric | Source | Published |
|---|---|---|
| Phase effort accuracy | Actual vs estimated phase duration | Documentation system + issue tracker |
| Phase cycle time | S1 start to Build Complete timestamp | Documentation system + issue tracker |
| Agent code ratio | Git PR diff data | Documentation system + issue tracker |
| Agent quality rate | Agent code surviving to merge without human correction | Documentation system + issue tracker |
| Hook compliance rate | Telemetry gate rejection count | Documentation system + issue tracker |
| Rework rate | Steps re-entered after initial completion | Documentation system + issue tracker |
| Approval turnaround | Issue tracker timestamps | Internal only — never published externally |
| Feature cycle time | Ready to Done timestamp | Documentation system + issue tracker |
| Release date accuracy | Planned vs actual release date | Documentation system |

### Constraints

- Approval turnaround is a team-only metric — must never be published to leadership reporting surfaces
- Calibration datasets are maintained per workflow mode — Mob and Sprint data are never blended
- Calibration is regenerated from the full velocity history on every cycle — never incremental
- Mob mode phase effort is recorded in team-hours (participants × elapsed duration), not individual developer hours

---

## intel-advisor

**Model:** claude-4.6-sonnet-medium
**Mode:** Foreground
**Access:** Read only
**Active during:** On demand

### Role

Answers planning questions using the empirical dataset built by intel-recorder. The query and application layer of SAGE Intel. All answers are derived from `velocity-history.jsonl` and the mode-specific calibration dataset. No human estimation is used at any stage.

### Invocation

> Type exactly: *"Please run intel-advisor — [weekly planning / release date estimate for [release name] / scope change: [feature name] added or removed]"*

### Three query modes

**Weekly planning:** Recommended features to pull into the work cycle, ranked by fit given current developer availability and in-flight work. Takes into account: features at Ready status, in-flight phases, estimated effort per feature by layer composition, and available developer capacity.

**Release date estimation:** P50 and P80 estimated completion date for the release's feature set, with a confidence band and an On Track / At Risk / Delayed status indicator.

**Scope change analysis:** For a feature added to a release — revised P50/P80 and what would need to move out to maintain the current release date. For a feature removed — revised estimates and what could fill the freed capacity.

### Confidence levels

| Sample count (per layer type, per mode) | Confidence |
|---|---|
| Fewer than 5 | Very low — uses heuristic estimates from phase-splitter with explicit warning |
| 5 to 9 | Moderate |
| 10 to 19 | Good |
| 20 or more | High |

### Constraints

- Never asks for human estimates — flags low confidence and uses heuristics when data is insufficient
- Uses mode-specific calibration data — Mob estimates draw from `mob_calibration.json`, Sprint from `sprint_calibration.json`
- Approval turnaround data is used in internal calculations but must never appear in outputs shown to leadership
- Read only — never writes to any file during a planning query

---

## sage-s7-ado-handoff

**Model:** *(reference documentation — invoke as needed; not a primary automation agent)*  
**Mode:** On demand  
**Access:** Read only  
**Active during:** After S7 (`phase-{N}-test-results.md`) when aligning with Azure DevOps test evidence

### Role

Defines how **SAGE S7** (per-phase agent testing, `phase-{N}-test-results.md`) relates to the **ADO test plan** workflow (`2-1-test-plan-creation.mdc`). This agent file is a **mapping and checklist** document: S7 automation and ADO human-QA evidence are complementary; neither replaces the other.

### What it specifies

- Two paths: SAGE S7 (agent-driven artifacts) vs ADO UserStory test runs (stakeholder-facing).
- Mapping rules: `phase-{N}-tdd-results.md`, `phase-{N}-code-review.md`, and `phase-{N}-test-results.md` → ADO test cases / run notes / attachments.
- Gate ordering: S6 code review → S7 test-runner → S8 completion report stop gate; ADO run updates **after** S7 PASS per document guidance.

### Constraints

- Does **not** substitute an ADO test plan for S7 `STATUS: PASS` or vice versa — both must be satisfied for full closure where the process requires them.
- ADO updates follow the handoff checklist in `.cursor/agents/sage-s7-ado-handoff.md` after `phase-{N}-test-results.md` reaches `STATUS: PASS`.
- Read only — the markdown file is normative reference for developers; it does not execute hooks or write ADO state itself.
