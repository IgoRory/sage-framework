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

## Artifact authoring rules

These rules apply to every foreground agent's declared output artifact unless
its agent definition explicitly overrides them.

- No introduction, recap, or closing sections. Start with the required header
  block; end after the last finding/row.
- No restatement of the PRD, implementation plan, or any prior artifact. Cite
  by relative path and section anchor (e.g. `prd.md#ac-3.2`).
- Frontmatter for structured fields; bullets or tables for the rest. Prose only
  when prose is the deliverable (e.g. handoff notes).
- One assertion per bullet. No qualifiers ("clearly", "robust", "comprehensive",
  "appropriate", "correct").
- Do not duplicate gate-required lines. Each appears exactly once on its own
  line in the body.
- Tables: omit a section's table entirely when its row count is zero — write
  "None." instead.

---

## Table of Contents

- [orchestrator](#orchestrator)
- [sprint-coordinator](#sprint-coordinator)
- [dev-interview](#dev-interview)
- [implementation-planner](#implementation-planner)
- [traceability-reviewer](#traceability-reviewer)
- [plan-preview-generator](#plan-preview-generator)
- [prd-orchestrator](#prd-orchestrator)
- [prd-interviewer](#prd-interviewer)
- [prd-amend](#prd-amend)
- [prd-demo-generator](#prd-demo-generator)
- [prd-stale-check](#prd-stale-check)
- [prd-walkthrough](#prd-walkthrough)
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
- [tdd-orchestrator](#tdd-orchestrator)

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
- Cannot set `validationConfirmed = true` in `phase-{N}/phase-manifest.json`

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
to the phase runtime manifest.

### What it produces

- `phase-{N}-implementation-plan.md`
- Linear issue tasks (via MCP)
- Batch definitions in `phase-{N}/phase-manifest.json` (Checkpoint mode only)

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
confirm: set `validationConfirmed = true` in `phase-{N}/phase-manifest.json`.

### What it produces

- `phase-{N}-plan-preview.canvas.tsx` (UI phases — spatial/stateful sections)
- `phase-{N}-plan-preview.md` (UI phases — linear sections)
- `phase-{N}-calculation-proof.md` (calculation phases)

### Constraints

- Cannot set `validationConfirmed = true` in `phase-{N}/phase-manifest.json`
- Must explicitly instruct the developer to set this flag themselves
- Canvas files must only import from `cursor/canvas` — no npm packages, no
  relative imports, no network calls
- Must embed all data inline in canvas files

---

## prd-orchestrator

**Mode:** Foreground
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/` only)
**Active during:** Before the first prd-interviewer session for any feature

### Role

Receives a large feature (ADO work item or Linear issue), performs exhaustive
silent codebase reconnaissance, classifies each sub-area by complexity tier,
recommends a PRD breakdown that keeps every sub-PRD at Tier 1–2, and writes
`prd-breakdown.md` with a machine-readable `investigation_context` block for
prd-interviewer instances to consume. Always runs before the first
prd-interviewer session for a feature.

### What it produces

- `.sage/prds/[FEATURE_ID]/prd-breakdown.md` — machine-readable breakdown with
  `investigation_context` block; consumed by all prd-interviewer instances for
  this feature

### Constraints

- Always completes Step 0 repo preflight before any investigation
- Always confirms context checklist with PM before silent recon
- Never narrates the recon process to the PM
- Never shows SP names, return codes, view column names, class names, or any
  internal technical construct to the PM
- Never recommends a split that leaves a sub-PRD at Tier 3+ complexity
- Never writes component or SP data into PRD output files
- The PM must explicitly confirm before `prd-breakdown.md` is written

---

## prd-interviewer

**Mode:** Foreground
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/[sub-prd-id]/` only)
**Active during:** Per sub-PRD, after prd-orchestrator confirms the breakdown

### Role

Conducts a structured interview with the Product Owner for one sub-PRD scope
to produce a complete sub-PRD bundle against the L1–L12 architectural model.
Reads `prd-breakdown.[sub-prd-id].md` and consumes Component Pattern
Summaries directly — does not re-run codebase recon. Runs a 9-phase
interview (Step 0 preflight, P1–P9 with P3/P4/P5 conditional on
breakdown indicators), assigns §4 sub-section IDs (DM/CL/AL/WF/UI/VC/ER/
NM/PA/IN/PF/AU/RX/CP-NNN) in-flow during the phase that captures the
requirement, declares a §4 coverage map at P2 and reconciles it at the
single conclusion gate, derives sequential acceptance criteria (AC-NNN
with `surface` field) at P8, authors three manual handoff briefs at P9,
verifies handoff returns via Family N anchor attestation, and finalises
`bundle-manifest.json` at end of P9. Enforces Step 0 repo preflight with
consolidated L5 readiness checks, appends telemetry to
`.sage/prd-interview-telemetry.jsonl`, and routes a single conclusion
gate with APPROVE / REJECT / REDIRECT semantics.

### What it produces

Interviewer-chat-authored (light artifacts):

- `prd.md` — 8-section PRD against `prd-section-schema.md`; YAML frontmatter
  with `prdHash` SHA-256 of body content
- `acceptance-criteria.md` — sibling AC file; sequential `AC-NNN`; each AC
  carries `linked_requirement_ids` (one or more §4.NNN), GWTX, `surface`
  field (UI/calc/data/error), `demoable` flag
- `reuse-map-draft.md` — disk-first full reuse map
- `component-pattern-confirmation.md` — written at end of P5; bulk
  Pattern Block validation
- `interview-answers.json` — verbatim PM answer record
- `traceability.md` — auto-built at P9 from in-memory AC list + three
  handoff `_summary.md` files; bidirectional AC ↔ §4.NNN; table-only
- `demos/_brief.md`, `sample-data/_brief.md`, `component-spec/_brief.md`
  — manual-handoff briefs with Family N `{ path, read_mode,
  expected_anchors }` per cited YAML in Section 3
- `bundle-manifest.json` — finalised at end of P9; declares every file
  in the bundle with `prdHash`, `writtenAt`, `producer`, `role`

Handoff-chat-authored (heavy artifacts, validated on return):

- `demos/demo-interactive.html`, optional `demos/calculation-demo.html`,
  `demos/demo-behavior-manifest.md`, `demos/demo-coverage.md`,
  `demos/_summary.md` (with `## YAML reads` anchor attestation H2)
- `sample-data/*.json`, `sample-data/_summary.md`
- `component-spec.md`, `component-spec/_summary.md`

### Constraints

- Always reads `prd-breakdown.[sub-prd-id].md` before P1 — no recon
  from scratch; never re-opens cited YAMLs mid-interview (Family E)
- Step 0 consolidates ALL L5 readiness checks (breakdown presence,
  sub-PRD ID validity, Component Pattern Summaries populated, cited
  YAMLs on disk, branch state, dirty tree). Hard-stop vs override-
  eligible matrix per L5; override emits
  `prd_interview_override_applied`
- Asks questions in batches of 2–4; never dumps a section as a list
- Records PM answers verbatim; interviewer interpretation lives in
  PRD only, never in `interview-answers.json`
- Single conclusion gate after P6 edge cases (legacy two-gate pattern
  is collapsed); APPROVE / REJECT / REDIRECT; reconciles the §4
  coverage map declared at P2 against what was captured P1–P6
- §4 sub-section IDs assigned in-flow during the phase that captures
  the requirement (not at PRD generation)
- AC IDs are sequential `AC-NNN`, no buckets; category lives in
  `surface` field; legacy `AC-{REQ|EC|UI|ERR}-NNN` retired (preserved
  during dual-layout backfill-on-touch window only)
- Every §4 sub-section in the P2 coverage map either has at least
  one §4.NNN entry OR carries explicit `Not applicable — [reason]`
  notice (no silent omissions)
- Family N (handoff-chat read discipline, N1–N8): brief Section 3
  declares per-YAML `expected_anchors`; handoff `_summary.md` carries
  `## YAML reads` H2 with `anchors_extracted`; interviewer post-return
  validation reads only YAML files (not heavy artifact) to verify each
  anchor; N5 spot-check on random artifact rows
- Family M (application-fidelity): when a production UI affordance
  exists, brief MUST cite the relevant YAMLs; "no application
  equivalent" flagged explicitly in brief
- Family J (anti-hallucination): every UI / data assertion traceable
  to YAML or PM answer; if unsure, ask PM
- Pre-write artifact-bar walk (L6 G3) for every interviewer-authored
  artifact — must pass `production-grade-quality-bar.md` Pass
  Conditions before file write; failure: do not write, surface
  failing Pass Condition, resolve gap, retry
- All user-facing message text follows the three-tier sourcing
  protocol (Tier 1 verbatim YAML; Tier 2 PRD outcome PM-approved;
  Tier 3 interviewer-drafted, marked, PM-approved before write)
- Cannot set `validationConfirmed = true` in the session manifest
- Cannot run codebase recon mid-interview — that is the
  orchestrator's job, captured in `prd-breakdown`

---

## Sub-agent delegation contract

The three sub-agent-built surfaces of a sub-PRD — **demo**, **sample-data**,
and **component-spec** — are produced via a manual chat handoff, not via
programmatic sub-agent spawning. The pattern was proven in Phase 0 of the
PRD Pipeline Production-Grade Lift and is the production contract for every
sub-PRD that produces these surfaces.

**The manual handoff is the production pattern.** Programmatic spawning via
the `Task` tool is reserved as an optional optimisation only when a
suitable `subagent_type` becomes locally available; until then, the manual
pattern is canonical.

**Three surfaces, one contract.** Each surface has a brief, a paste-ready
handoff prompt, and a structured summary file:

| Surface | Brief | Artifact | Summary |
|---|---|---|---|
| Demo | `demos/_brief.md` | `demos/demo-interactive.html` (and/or `demos/calculation-demo.html`) | `demos/_summary.md` |
| Sample-data | `sample-data/_brief.md` | `sample-data/*.json` | `sample-data/_summary.md` |
| Component-spec | `component-spec/_brief.md` | `component-spec.md` | `component-spec/_summary.md` |

**The PM is the orchestrator.** The prd-interviewer chat authors the brief
and presents a paste-ready handoff prompt. The PM opens a fresh Cursor chat
per brief and pastes the corresponding prompt unchanged. The handoff chat
reads the brief plus every cited YAML, produces the artifact plus the
summary, and STOPS.

**The interviewer chat reads only the summary file on return — never the
full artifact.** Validation against the summary's claims preserves the
context-saving intent of the manual pattern. If a claim looks unsupported,
the interviewer spot-checks the artifact; otherwise the summary is the
contract.

**Application-fidelity hard rule.** When a UI affordance exists in the
production application, the brief MUST cite the relevant component YAML
file(s) under `.context/components/` (or equivalent), and the handoff chat
has zero discretion to invent a different pattern. The brief author is
responsible for naming every YAML a demo will need before the brief is
finalised. Production-grade design freedom applies only where there is no
application equivalent — those affordances must be flagged explicitly in
the brief as "no application equivalent — generator's choice". No silent
gaps. This rule is binding across all three surfaces.

**Authoritative reference:**
[`.cursor/skills/prd-interviewer/references/sub-agent-delegation.md`](.cursor/skills/prd-interviewer/references/sub-agent-delegation.md)
defines the orchestration sequence, brief format, summary-file contract,
the application-fidelity rule with its brief-author checklist, and the
handoff-chat self-review obligations. Paste-ready prompts live at
[`.cursor/skills/prd-interviewer/references/handoff-prompt-templates.md`](.cursor/skills/prd-interviewer/references/handoff-prompt-templates.md).

---

## prd-amend

**Mode:** Foreground
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/[sub-prd-id]/` only — diff briefs and prdHash header updates)
**Active during:** On PM request, after the PM edits a sub-PRD's `prd.md` and one or more derivatives are STALE

### Role

Orchestrates re-generation of derivative artefacts that have drifted from
an amended `prd.md`. Runs or consumes a prd-stale-check report, generates
a targeted diff brief for each STALE surface (demo, sample-data,
component-spec), and guides the PM through re-running the corresponding
manual handoff chat per the Phase C three-surface handoff discipline.
FRESH surfaces are never re-run. Operates in two modes: `auto` (amend all
STALE surfaces using stale-check output) and `targeted` (PM names the
specific surface to regenerate).

### What it produces

- `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_brief.amend.md` — diff brief for the demo surface (when STALE)
- `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_brief.amend.md` — diff brief for the sample-data surface (when STALE)
- `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec-brief.amend.md` — diff brief for the component-spec surface (when STALE)
- Updated `prdHash` header in each regenerated derivative after the handoff chat completes

### Constraints

- Never regenerates FRESH surfaces (in `auto` mode)
- Never edits `prd.md` — the PM is the sole PRD author
- Never edits `acceptance-criteria.md` or `traceability.md` directly
- One handoff chat per surface — inherits the Phase C three-surface handoff discipline
- Inherits the production-grade quality bar from `.cursor/skills/prd-interviewer/references/production-grade-quality-bar.md`

---

## prd-demo-generator

**Status:** **DEPRECATED — permanently inert; preserved for archaeological reference.**

**Mode:** Foreground (legacy — never invoked)
**Access:** Read / Write (`.sage/prds/[FEATURE_ID]/demos/` only)
**Active during:** Never. This skill is not invoked by any current pipeline. It is preserved as a historical artefact only.

### Replacement

The replacement is the **three-surface manual handoff** owned by
`prd-interviewer`. Demo artifacts are produced by the demo handoff chat
described in:

- `.cursor/skills/prd-interviewer/references/handoff-prompt-templates.md` —
  Template 1 (Demo handoff prompt) — paste-ready prompt the PM hands to a
  fresh Cursor chat.
- `.cursor/skills/prd-interviewer/references/sub-agent-delegation.md` —
  orchestration sequence, brief format, summary-file contract, application-
  fidelity hard rule, and Tier 1 inside-chat self-review protocol.

### Preservation record

The `.cursor/skills/prd-demo-generator/SKILL.md` file is **permanently
preserved** by PM ruling at Phase E close (25-MAY-2026). The Phase A locked
decision A5 ("deletion queued for Phase E") is overridden by this ruling.
The file is retained as a historical artefact for reference purposes only.
No pipeline reads from it; no pipeline invokes it.

### Legacy role (historical record — not invoked)

Optional skill that was previously invoked by the PM to produce interactive
HTML demos from a completed PRD draft. Reads the PRD's acceptance criteria
(AC-REQ, AC-EC, AC-UI, AC-ERR) and component specification to generate
self-contained HTML files that visualise every demoable scenario.

### What it produces (legacy — not produced by any current invocation)

- `.sage/prds/[FEATURE_ID]/demos/demo-interactive.html` (UI features)
- `.sage/prds/[FEATURE_ID]/demos/calculation-demo.html` (calculation features)
- `.sage/prds/[FEATURE_ID]/demos/demo-coverage.md` (coverage report)

### Constraints

- **No downstream pipeline reads from this file.** Re-activation requires PM
  approval and a fresh evaluation against the current pipeline.
- Read-only access to codebase (SCSS variables, component templates, message text)
- Write access only to `.sage/prds/[FEATURE_ID]/demos/`
- Never modifies the PRD or component specification

---

## prd-stale-check

**Mode:** Foreground
**Access:** Read only (`.sage/prds/[FEATURE_ID]/[sub-prd-id]/` only; writes one report file)
**Active during:** On PM request — before running prd-amend, or whenever the PM suspects a sub-PRD's derivatives may have drifted from an edited `prd.md`

### Role

Detects drift between a sub-PRD (`prd.md`) and its derivative artefacts
by comparing the embedded `prdHash` header in each derivative against the
current SHA-256 of `prd.md`. Produces a stale-check report listing every
derivative as FRESH, STALE, or MISSING. Read-only — never regenerates
artefacts. Diagnoses only; the PM decides whether to invoke prd-amend.

### What it produces

- `.sage/prds/[FEATURE_ID]/[sub-prd-id]/stale-check.md` — per-derivative status report with FRESH / STALE / MISSING classification and section delta notes where computable

### Constraints

- Read-only on all derivatives — never modifies any artefact
- Never regenerates surfaces — diagnosis only
- Must emit `prd_stale_check_started` at Step 1 and `prd_stale_check_completed` at Step 4

---

## prd-walkthrough

**Mode:** Foreground
**Access:** Read only (`.sage/prds/[FEATURE_ID]/[sub-prd-id]/` — all artefacts)
**Active during:** On PM request — to review a completed sub-PRD bundle without opening multiple files

### Role

Presents a completed sub-PRD bundle to the PM in a structured, readable
format via a seven-section in-chat walkthrough: PRD overview, functional
surfaces, reuse posture, demo highlights, sample-data shape, open
ambiguities, and traceability coverage statement. Uses `_summary.md` files
by default to avoid reading full artefacts (T2/T6 context-reduction
discipline). Deep-reads the full artefact only when the PM challenges a
specific item. Emits one telemetry event per invocation.

### What it produces

- In-chat walkthrough only (no file written)
- Telemetry: `prd_walkthrough_run`

### Constraints

- Read-only — never modifies any artefact, framework file, or application source file
- Summary-first — never reads full HTML, JSON, or component-spec when a `_summary.md` exists and the PM has not challenged a specific item
- One `prd_walkthrough_run` telemetry emit per invocation

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
`devPlanMode` flag in phase runtime.

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

## tdd-orchestrator

**Skill file:** `.cursor/skills/tdd-orchestrator/SKILL.md`
**Active during:** On demand — bug batches, phase gates, spikes, and finding remediation

### Role

Coordinates automated TDD RED/GREEN/REFACTOR loops for SAGE phases,
checkpoint batches, bug batches, exploratory QA findings, and review findings.
Uses subagents for planning, implementation, review, test coverage assessment,
and refinement while preserving SAGE gate ownership boundaries.

Supports three operating modes:
- **Bug Batch Mode** — focused TDD loops for grouped bugs or exploratory QA
- **Phase Gate Mode** — formal SAGE gate progression with owning agents writing
  gate artifacts
- **Spike Mode** — investigation and TDD planning only; no implementation

### What it produces

- In chat by default: bug ledgers, remediation plans, and test summaries
- Optional phase-local bug batch artifacts:
  `phase-{N}-bug-batch-[slug].md`
- Formal gate artifacts only through the owning SAGE role, not directly

### Constraints

- Does not bypass SAGE gates or write role-owned gate artifacts directly
- Does not write test files during S5b GREEN/REFACTOR
- Requires S5a RED confirmation before S5b production edits
- Keeps spike work read-only until the developer approves implementation
