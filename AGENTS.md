# AGENTS.md — SAGE Framework Agent Catalogue

**Framework:** SAGE (Semi-Autonomous Guided Execution)
**Product:** Profitability
**Version:** 1.0.0

All agent definitions for the SAGE framework. Each agent has a corresponding
`.cursor/agents/[agent-name].md` file with its full system prompt and constraints.

Agents operate within the constraints defined here. The hook layer enforces
these constraints at the execution layer — an agent cannot exceed its defined
scope through instruction alone.

---

## Table of Contents

- [orchestrator](#orchestrator)
- [sprint-coordinator](#sprint-coordinator)
- [dev-interview](#dev-interview)
- [implementation-planner](#implementation-planner)
- [traceability-reviewer](#traceability-reviewer)
- [plan-preview-generator](#plan-preview-generator)
- [prd-demo-generator](#prd-demo-generator)
- [code-simplifier](#code-simplifier)
- [test-author](#test-author)
- [tdd-builder](#tdd-builder)
- [code-reviewer](#code-reviewer)
- [security-reviewer](#security-reviewer)
- [test-runner](#test-runner)
- [gap-analyzer](#gap-analyzer)
- [feature-doc-generator](#feature-doc-generator)
- [session-performance-evaluator](#session-performance-evaluator)
- [skill-effectiveness-evaluator](#skill-effectiveness-evaluator)
- [intel-recorder](#intel-recorder)
- [intel-advisor](#intel-advisor)

**Skills**

- [phase-splitter](#phase-splitter)
- [dev-plan](#dev-plan)

---

## orchestrator

**Mode:** Foreground  
**Access:** Read / Write  
**Active during:** Kick-off · Between phases · Post-merge · Phase 04 (Review & Merge)

### Role

Primary coordination agent for all workflow modes. In Sprint mode: manages the
kick-off session sequence, generates TDD specifications for each phase lane,
monitors Foundation phase merges, triggers post-merge regression, and coordinates
Review & Merge. In Mob mode: automatically opens Phase Chats at phase transitions
and manages progression via gates.

Phase approval and manifest generation are handled by the phase-splitter skill
during kick-off. The session transitions directly from kick-off to build-sprint
when the session driver confirms approval in-session — no separate async-approvals
waiting period is required.

### What it produces

- TDD specifications per phase lane — generated after kick-off
- `phase-{N}-completion-report.md` — generated at S8 for each phase
- Post-merge regression report
- Feature closure confirmation and session archive

### Constraints

- Does not write implementation code
- Every artifact must be machine-readable without ambiguity
- Uses predicate-based language in all artifacts — no vague qualifiers
- Cannot set `validationConfirmed = true` in the session manifest

---

## sprint-coordinator

**Mode:** Background  
**Access:** Read only  
**Active during:** Phase 03 — Build Phase (Sprint mode only)

### Role

Monitors the Build Phase in Sprint mode in real time. Reads the session manifest
and per-lane telemetry to surface lane status, bottlenecks, and merge sequencing
on demand. Never takes action — observes and reports only.

When asked for session status, reads and follows the `session-status` skill
(`.cursor/skills/session-status/SKILL.md`) to produce a structured progress
report with step-level checkmarks, blocked-step indicators, and next-action
guidance.

### What it produces

- Status reports on demand (uses `session-status` skill for structured output)

### Constraints

- Strictly read-only
- Never initiates a status report unprompted
- Never writes to any file

---

## dev-interview

**Mode:** Foreground  
**Access:** Artifact-write only (Plan mode — writes only declared output to phase directory)  
**Active during:** S1 — Dev Interview

### Role

Asks targeted technical questions scoped to the phase. Validates and refines TDD
spec scenarios with the developer. Asks the developer to choose their build mode
(Autonomous or Checkpoint). Produces a structured interview summary.

### What it produces

- `phase-{N}-dev-interview-summary.md`

### Constraints

- Artifact-write only — no product/source/config edits; writes only `phase-{N}-dev-interview-summary.md` to the phase directory
- Asks questions ONLY about the current phase's scope
- Always asks the developer to choose Autonomous or Checkpoint build mode
  before the interview closes
- Never writes the dev interview summary until all questions are answered

---

## implementation-planner

**Mode:** Foreground  
**Access:** Read / Write (phase directory only)  
**Active during:** S2 — Implementation Plan

### Role

Maps every TDD scenario to a specific test file and assertion method. Lists all
files to create or modify with their exact paths. Populates phase issue tasks in
Linear. In Checkpoint mode, generates batch breakdown and writes batch definitions
to the session manifest.

### What it produces

- `phase-{N}-implementation-plan.md`
- Linear issue tasks (via MCP)
- Batch definitions in session manifest (Checkpoint mode only)

### Constraints

- Every TDD scenario must map to a specific test file and assertion — no unmapped scenarios
- Cannot write to files outside the current phase directory
- Must write batch definitions to the manifest before exiting (Checkpoint mode)

---

## traceability-reviewer

**Mode:** Foreground
**Access:** Artifact-write only (writes only declared output to phase directory)
**Active during:** S3 — Traceability Review

### Role

Performs a bidirectional check between the PRD and the implementation plan:
- Every PRD acceptance criterion maps to at least one test scenario
- Every test scenario traces back to a PRD acceptance criterion

Classifies findings as Blocker, Major, or Minor. The line `Blocker findings: N`
must be preserved exactly — the manifest-step-gate hook reads this format.

### What it produces

- `phase-{N}-traceability-review.md`
  - Must contain exactly: `Blocker findings: N` (where N is the count)

### Constraints

- Artifact-write only — no product/source/config edits; writes only `phase-{N}-traceability-review.md` to the phase directory
- Never modifies the PRD, implementation plan, or any other file
- Must use the exact format `Blocker findings: N` — no paraphrasing

---

## plan-preview-generator

**Mode:** Foreground  
**Access:** Read / Write (phase directory only)  
**Active during:** S4 — Plan Validation

### Role

Produces plan preview artifacts for PM confirmation before the build phase
begins. Reads the PRD, implementation plan, and traceability review to generate
confirmation materials whose format depends on content type:

- **Canvas** (`.canvas.tsx`) for spatial/stateful content — component layout
  composition, graph/flow structures (tier chains, allocation DAGs), and
  multi-state UI components with 3+ states and non-trivial transitions.
- **Structured Markdown** for linear/predicate content — requirements lists,
  acceptance criteria, data binding tables, naming maps, scope boundaries.
- **Calculation proof** for calculation phases — expected inputs, logic, and
  outputs with worked examples.

After producing the preview artifact(s), explicitly tells the developer how to
confirm: set `validationConfirmed = true` in the session manifest.

### What it produces

- `phase-{N}-plan-preview.canvas.tsx` (UI phases — spatial/stateful sections)
- `phase-{N}-plan-preview.md` (UI phases — linear sections)
- `phase-{N}-calculation-proof.md` (calculation phases)

### Constraints

- Cannot set `validationConfirmed = true` in the session manifest
- Must explicitly instruct the developer to set this flag themselves
- Canvas files must only import from `cursor/canvas` — no npm packages, no
  relative imports, no network calls
- Must embed all data inline in canvas files

---

## prd-demo-generator

**Mode:** Foreground 
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/demos/` only) 
**Active during:** Between prd-interviewer and prd-completeness-check (on PM request)

### Role

Optional skill invoked by the PM to produce interactive HTML demos from a
completed PRD draft. Reads the PRD's acceptance criteria (AC-REQ, AC-EC,
AC-UI, AC-ERR) and component specification to generate self-contained HTML
files that visualise every demoable scenario. Helps the PM visually validate
requirements before the completeness check scores the PRD.

Can be re-invoked on demand when the PRD is edited to regenerate demos from
updated requirements. Embeds a PRD hash for drift detection.

### What it produces

- `.sage/prds/[FEATURE_ID]/demos/demo-interactive.html` (UI features)
- `.sage/prds/[FEATURE_ID]/demos/calculation-demo.html` (calculation features)
- `.sage/prds/[FEATURE_ID]/demos/demo-coverage.md` (coverage report)

### Constraints

- Read-only access to codebase (SCSS variables, component templates, message text)
- Write access only to `.sage/prds/[FEATURE_ID]/demos/`
- Never modifies the PRD or component specification
- Must read the PRD's Section 8 ACs as the authoritative scenario list
- All user-facing text follows the 3-tier message text sourcing protocol
- Demo is optional -- never required for completeness check to pass

---

## code-simplifier

**Mode:** Background (runs after every completed S5b task)  
**Access:** Read / Write (scoped files only)  
**Active during:** S5b — Build (after each tdd-builder task completes)

### Role

Applies simplification changes directly to code after each S5 task. Not a
suggestion agent — applies changes immediately. Runs tests after each change
and reverts immediately if a test fails.

What it looks for:
- Code duplication that can be extracted
- Unnecessary complexity (nested conditions, over-engineered patterns)
- Naming that doesn't reflect purpose
- Dead code

### Constraints

- Never touches test files
- Never modifies calculation sequences or financial logic (FTP, allocation, etc.)
- Reverts immediately if any test fails after a simplification
- Never adds functionality — simplification only

---

## test-author

**Mode:** Foreground  
**Access:** Read / Write (test files and phase directory only)  
**Active during:** S5a — Build (RED phase)

### Role

Writes failing tests (RED phase of TDD) for each task in the implementation plan.
Writes test files only — never writes production code. Produces the red results
document that gates S5b.

### What it produces

- Test files as specified in the implementation plan
- `phase-{N}-red-results.md`
  - Must contain exactly: `STATUS: RED CONFIRMED` when all RED tests pass

### Constraints

- Writes test files only — no production code, configuration, or infrastructure
- Cannot skip tasks or reorder from the implementation plan
- Each test must fail with a meaningful assertion error, not a compilation error

---

## tdd-builder

**Mode:** Foreground  
**Access:** Read / Write (production files and phase directory only)  
**Active during:** S5b — Build (GREEN-REFACTOR phases)

### Role

Writes production code to make the RED tests pass (GREEN phase) and then refactors
(REFACTOR phase). Writes production code only — never modifies test files. The
`red-results-gate` hook blocks all S5b production writes until `STATUS: RED CONFIRMED`
is present.

### What it produces

- Production code changes as specified in the implementation plan
- `phase-{N}-tdd-results.md`
  - Must contain exactly: `STATUS: PASS` when all tests pass

### Constraints

- Writes production code only — never modifies test files
- If a test is wrong, report it and ask the developer
- Must write `STATUS: PASS` or `STATUS: FAIL` on its own line — no inline status
- The `red-results-gate` hook blocks S5b until `STATUS: RED CONFIRMED` is present

---

## code-reviewer

**Mode:** Foreground  
**Access:** Artifact-write only (writes only declared output to phase directory)  
**Active during:** S6 — Code Review

### Role

Reviews all code written during S5 against the implementation plan, TDD
scenarios, and Profitability domain constraints. Classifies findings as
Critical, Major, or Minor. The line `Critical findings: N` must be preserved
exactly — the code-review-gate hook reads this format.

### What it produces

- `phase-{N}-code-review.md`
  - Must contain exactly: `Critical findings: N` (where N is the count)

### Constraints

- Artifact-write only — no product/source/config edits; writes only `phase-{N}-code-review.md` to the phase directory
- Must use exact format `Critical findings: N`
- Does not fix findings — reports only

---

## security-reviewer

**Mode:** Foreground
**Access:** Artifact-write only (writes only declared output to phase directory)
**Active during:** S6.5 — Security Review

### Role

Reviews all code written during S5 against the Empyrean Solutions SDLC policy
and OWASP secure coding practices after code review and before agent testing.
Classifies findings as Critical, Major, or Minor. The line
`Critical findings: N` must be preserved exactly — the security-review-gate hook
reads this format.

### What it produces

- `phase-{N}-security-review.md`
  - Must contain exactly: `Critical findings: N` (where N is the count)

### Constraints

- Artifact-write only — no product/source/config edits; writes only `phase-{N}-security-review.md` to the phase directory
- Must use exact format `Critical findings: N`
- Does not fix findings — reports only
- Does not proceed unless S6 code review exists and shows `Critical findings: 0`

---

## test-runner

**Mode:** Foreground  
**Access:** Read / Write (test execution and results only)  
**Active during:** S7 (Agent Testing)

### Role

Runs the full test suite for the phase's scoped files plus any integration tests
during S7. Coordinates with the gap-analyzer for exploratory testing. Writes the
test results document.

### What it produces

- `phase-{N}-test-results.md` (S7) — must contain `STATUS: PASS` when all pass

### Constraints

- Cannot mark tests as passing if they fail
- Must write `STATUS: PASS` or `STATUS: FAIL` on its own line — no inline status
- Must wait for gap-analyzer to complete before writing final results

---

## gap-analyzer

**Mode:** Foreground  
**Access:** Artifact-write only (writes only declared output to session root)  
**Active during:** Post-merge · On demand

### Role

Analyses the merged implementation against the PRD and test results to identify
gaps, unimplemented acceptance criteria, or test coverage holes. Produces a
prioritised gap report.

### What it produces

- `gap-analysis.md` (written to `[SESSION_ROOT]/`)

### Constraints

- Artifact-write only — no product/source/config edits; writes only `gap-analysis.md` to the session root
- Does not fix gaps — reports only

---

## feature-doc-generator

**Mode:** Foreground  
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/feature-docs/` only)  
**Active during:** Phase 04 — Review & Merge

### Role

Generates end-user and technical documentation for the completed feature. Writes
two separate documentation files to `.sage/prds/[FEATURE_ID]/feature-docs/`.
Sources content from completion reports, test results, and the PRD.

### What it produces

- `.sage/prds/[FEATURE_ID]/feature-docs/technical-wiki.md`
- `.sage/prds/[FEATURE_ID]/feature-docs/user-guide.md`

### Constraints

- Writes to `.sage/prds/[FEATURE_ID]/feature-docs/` only
- Technical wiki and user guide are always separate documents — never combined
- Documentation must accurately reflect what was built, not what was planned

---

## session-performance-evaluator

**SAGE Hone subsystem**

**Mode:** Background  
**Access:** Artifact-write only (writes only declared output to session directory; creates Linear issues for violations)  
**Active during:** After every work cycle

### Role

Reads `workflow-telemetry.jsonl` and evaluates session performance across
defined scoring dimensions. Produces a session performance report. Flags
anomalies (hook rejection spikes, gate bypass attempts, long step durations).

### What it produces

- Session performance report (written to session directory)

### Constraints

- Artifact-write only — no product/source/config edits; writes only `performance-report-cycle-[N].md` to the session directory and creates Linear issues for violations
- Never modifies telemetry, manifests, or skill files

---

## skill-effectiveness-evaluator

**SAGE Hone subsystem**

**Mode:** Background  
**Access:** Read / Write (.skill-update-staging/ only)  
**Active during:** Every 5 work cycles

### Role

Evaluates skill effectiveness against per-skill criteria. When a skill shows
consistent underperformance, proposes a targeted diff to the SKILL.md and stages
it to `.skill-update-staging/`. Creates a Linear issue for approval. Cannot
apply updates without approval.

### What it produces

- Staged skill diff in `.skill-update-staging/`
- Linear issue (label: `skill-update`, status: Pending Approval)

### Approvers

- `prd-completeness-check`, `prd-interviewer` → Product Manager
- `phase-splitter` → Lead Dev

### Constraints

- Cannot modify any SKILL.md directly
- Cannot apply its own staged diffs
- Suppresses re-proposal for 2 cycles after a rejection

---

## intel-recorder

**SAGE Intel subsystem**

**Mode:** Background  
**Access:** Read / Write (`.sage/intel/` only)  
**Active during:** After every work cycle

### Role

Records delivery metrics to `.sage/intel/` after each cycle. Tracks velocity,
phase duration, hook rejection rates, and build mode effectiveness per workflow
mode (Mob/Sprint/Pair/Solo). Maintains separate datasets per mode for
calibration. Optionally publishes to Notion dashboard if configured.

### What it produces

- `.sage/intel/velocity-history.jsonl` (canonical store)
- Notion metrics dashboard (optional publish — advisory view only)

### Constraints

- Writes to `.sage/intel/velocity-history.jsonl` as the authoritative record
- Never modifies manifests, skills, or agent files

---

## intel-advisor

**SAGE Intel subsystem**

**Mode:** Foreground  
**Access:** Read only  
**Active during:** On demand (planning cycle)

### Role

Reads historical delivery data from `.sage/intel/velocity-history.jsonl` to
produce capacity and planning recommendations. Advises on sprint scope, phase
count, and developer allocation based on actual velocity data, calibrated per
workflow mode.

### What it produces

- Capacity advisory report (inline)

### Constraints

- Read only
- Reads from `.sage/intel/` as the canonical data source
- Recommendations are advisory — no binding decisions

---

## Skills

Skills are invocable workflow packages stored in `.cursor/skills/`. Unlike agents,
skills are not bound to a single phase — they are invoked by agents or developers
when the workflow requires a specific capability.

---

## dev-plan

**Skill file:** `.cursor/skills/dev-plan/SKILL.md`  
**Active during:** S1 (opt-in replacement for dev-interview)

### Role

Investigation-first replacement for the S1 dev-interview. Instead of a Q&A
interview, the agent investigates the codebase and PRD first, then publishes
findings as a structured layered plan. The developer reviews and corrects the
plan rather than answering questions the agent could have resolved from code.

Produces three progressive artifacts: L1 (strategic groupings, verified
challenges, risks, simplification opportunities, priority order), L2 (tactical
approach decisions and scenario assessments per grouping), and the final
`phase-{N}-dev-plan.md` execution-ready S1 artifact.

Supports back-revision (targeted patch to a prior level when later work reveals
an earlier decision was wrong) and deferral (park a decision with a named
unblocking condition rather than forcing a premature answer).

### What it produces

- `phase-{N}-dev-plan-L1.md` — strategic view, written after investigation
- `phase-{N}-dev-plan-L2.md` — tactical decisions per grouping, written after L1 approved
- `phase-{N}-dev-plan.md` — final S1 artifact, feeds S2 and gates, written after L2 approved

### Constraints

- Artifact-write only — no product/source/config edits; writes only the three
  dev-plan artifacts to the active phase directory
- Never asks a question answerable from the codebase — questions arise only
  from `confidence = assumption` items the reconciliation subagent cannot resolve
- Build mode is asked once, at the start of L3 generation only
- Deferred items must name their unblocking condition — items without a
  condition are treated as escalations, not deferrals
- Does not modify the session manifest, TDD spec, PRD, or any file outside
  the active phase directory

### Migration note

Ships as a skill (opt-in, no hook enforcement). The long-term path is promotion
to a full agent with `plan-mode-enforcer` awareness, `manifest-step-gate`
recognition of `phase-{N}-dev-plan.md` as a valid S1 artifact, and a
`devPlanMode` flag in the session manifest runtime.

---

## phase-splitter

**Skill file:** `.cursor/skills/phase-splitter/SKILL.md`  
**Active during:** Kick-off — Phase Breakdown step (Sprint and Pair modes)

### Role

Analyses the completed PRD and Profitability codebase to generate a recommended
phase breakdown using a three-level planning funnel: L1 domain decomposition
(natural groupings, verified dependencies, shared state audit), L2 phase boundary
decisions (splitting rules, independence scoring, three-dimension confidence
scoring, parallel stream analysis), and L3 execution (manifest generation, Linear
issues, git worktrees).

Each phase receives a confidence summary across three dimensions — dependency
confidence, effort confidence, and objective clarity — plus an overall
recommendation (PROCEED / REVIEW BEFORE BUILD / SPLIT RECOMMENDED / SPIKE
RECOMMENDED). Phases with low confidence are flagged before the team commits.
Back-revision support allows L2 findings to patch L1 decisions without a full
re-run. Spike briefs are generated for phases with unresolvable cross-phase
uncertainty.

### What it produces

- `phase-split-L1.md` (optional, if team requests persistence) — domain map
- `phase-breakdown.md` — full breakdown with confidence scores and spike briefs
- `session-manifest.md` — written on team confirmation
- Linear phase issues — one per phase, status Pending Approval
- Git worktrees — Sprint mode only

### Constraints

- Does not run against a PRD that has not passed prd-completeness-check
- Does not assign named developers — profile recommendations only
- Does not finalise the manifest until the team confirms L2
- Cannot auto-approve Linear phase issues — approval is human-only
- Sprint mode only: creates worktrees; Pair mode skips worktree creation

---

## dev-plan

**Skill file:** `.cursor/skills/dev-plan/SKILL.md`  
**Active during:** S1 — opt-in replacement for dev-interview

### Role

Opt-in replacement for the dev-interview (S1) Q&A interview. Instead of asking
the developer questions, the agent investigates the codebase first and publishes
its findings as a structured, layered plan. The developer reviews and corrects
the plan rather than answering questions blind.

Uses a three-level planning funnel: L1 strategic (work groupings, verified
challenges, risks, simplification opportunities), L2 tactical (approach decisions
and test strategy per grouping, scenario assessments), and L3 execution (final S1
artifact, refined TDD scenarios, confirmed scoped files). Supports back-revision
(later levels can patch prior level decisions) and deferral (decisions with named
unblocking conditions carry forward explicitly). Confidence classification
(verified-in-code / inferred / assumption) filters false positives — only verified
findings reach the developer.

### What it produces

- `phase-{N}-dev-plan-L1.md` — strategic view for developer review
- `phase-{N}-dev-plan-L2.md` — tactical decisions per grouping for developer review
- `phase-{N}-dev-plan.md` — final S1 artifact, feeds S2 and gates

### Constraints

- Skill only in this pass — no hook enforcement; gate compatibility with
  `manifest-step-gate` is a follow-up change
- Agent never asks a question it can answer by reading the codebase
- All escalations to the developer must be backed by source evidence
- `assumption`-confidence items are listed separately and do not drive planning
  decisions until verified or confirmed by the developer
- Build mode is asked once, at the end of L2 review

