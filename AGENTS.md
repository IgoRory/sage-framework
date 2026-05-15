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

### What it produces

- `session-manifest.md` — generated at kick-off
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

### What it produces

- Status reports on demand

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
