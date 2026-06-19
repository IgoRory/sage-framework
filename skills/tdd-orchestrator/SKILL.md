---
name: tdd-orchestrator
description: Coordinates automated TDD RED/GREEN/REFACTOR loops for phases, checkpoints, bug batches, and exploratory findings. Use when asked to run TDD cycles, remediate code-review findings, fix bugs with tests, batch QA issues, advance SAGE gates after TDD, or orchestrate subagents through planning, implementation, quality review, testing, and refinement.
---

# TDD Orchestrator

Run high-standard RED/GREEN/REFACTOR cycles until the scoped TDDs pass, all in-scope Critical/Major findings are resolved, or a real blocker requires user or product decision.

TDDs may be scoped to a SAGE phase, checkpoint, bug batch, exploratory QA finding, PR review finding, or one-off issue.

---

## Core Mission

Use subagents to preserve orchestrator context aggressively:

1. Create concrete plans to implement the TDDs.
2. Have the plans assessed for quality before implementation.
3. Implement only after the plan is verified.
4. Have implementation checked by a second agent for quality.
5. Run tests and assess qualitative test coverage.
6. Refine in a loop until scoped Major/Critical issues are resolved.

Tests must maximize value and simplicity. Avoid shallow tests that only assert source shape unless the behavior is impractical to exercise any other way.

---

## Operating Modes

### Bug Batch Mode

Default for exploratory QA, bug reports, and fast iteration.

Use when the user says things like "found another issue", "bug", "keep iterating", "batch these", or "manual QA".

Behavior:
- Batch related bugs into a short ledger.
- Run focused TDD loops and targeted tests.
- Update only lightweight TDD or bug-batch artifacts when applicable.
- Keep the ledger in chat by default. Persist it only when the user asks or a
  SAGE session artifact is explicitly approved.
- If persisted, write only under the active phase directory using a non-gate
  artifact name such as `phase-{N}-bug-batch-[slug].md`.
- Do not automatically advance SAGE gates.
- Do not rerun S6/S6.5/S7 unless the user asks to close the batch, proceed, or rerun gates.
- Do not place hook markers such as `STATUS: PASS` or `Critical findings: 0`
  in bug-batch ledgers unless they are inside the formal artifact owned by the
  corresponding SAGE role.

### Phase Gate Mode

Use when the user explicitly asks to proceed through SAGE, close a checkpoint, complete a phase, rerun gates, or move to the next SAGE step.

Behavior:
- Run the same TDD loop as Bug Batch Mode.
- Re-run formal quality gates after implementation stabilizes.
- Use the owning SAGE role for every formal artifact; the orchestrator must not
  write role-owned gate artifacts directly.
- Require S5a RED confirmation before S5b production edits.
- Require S5b TDD results, S6 code review, S6.5 security review, and S7 agent
  testing to pass before S8 completion reporting.
- Proceed toward S8 only after S7 passes and unresolved deferrals are recorded.

### Spike Mode

Use when requirements or root cause are unclear.

Behavior:
- Investigate and produce a TDD plan only.
- Do not implement.
- Convert to Bug Batch Mode or Phase Gate Mode after approval.

---

## Standards Loading

Do not hardcode project standards into this skill. Load the standards that apply to the current scope before planning or editing.

| Scope | Required context |
|---|---|
| SAGE session | Active session file, session manifest, phase artifacts, role constraints |
| Angular/frontend | Project Angular standards and frontend test conventions |
| Backend/API | Architecture standards, API conventions, backend test conventions |
| SQL/database | SQL standards and required task/date metadata before SQL edits |
| Security-sensitive | Security review criteria, authorization model, OWASP-relevant project guidance |
| Existing feature area | Local implementation patterns and similar tests before inventing new abstractions |

Every planning and quality-review handoff must state which standards were consulted or why a standard did not apply.

---

## SAGE Role And Write Ownership

The orchestrator coordinates work. It does not collapse SAGE roles or bypass
their write boundaries. In Phase Gate Mode, each formal step must be performed
by the role that owns the artifact and write surface.

| Step | Owner | Allowed writes | Required gate output |
|---|---|---|---|
| S5a RED | `test-author` | Test files and current phase artifacts only | `phase-{N}-red-results.md` with `STATUS: RED CONFIRMED` |
| S5b GREEN/REFACTOR | `tdd-builder` | Production/source files and current phase artifacts only | `phase-{N}-tdd-results.md` with `STATUS: PASS` |
| S5b simplification | `code-simplifier` | Scoped production files touched by the completed task only | Inline simplification result; no formal gate marker |
| S6 code review | `code-reviewer` | `phase-{N}-code-review.md` only | `Critical findings: 0` |
| S6.5 security review | `security-reviewer` | `phase-{N}-security-review.md` only | `Critical findings: 0` |
| S7 agent testing | `test-runner` | Test execution results and `phase-{N}-test-results.md` only | `STATUS: PASS` |
| S8 completion | `orchestrator` | Completion report and session completion records only | Completion report after S7 passes |

Do not ask one worker to write another role's artifact. If a subagent discovers
that a required test, production change, or review artifact belongs to a
different role, it must stop and return the exact next role to invoke.

### Protected Manifest Fields

These fields are protected by SAGE process ownership. This skill may read them
to determine state, but must never set them or ask a subagent to set them:

- `phase-{N}/phase-manifest.json.validationConfirmed` - developer confirmation after S4.
- `phase-{N}/phase-manifest.json.batches[*].confirmed` - developer checkpoint approval.
- `sessionState.foundationVerified` - orchestrator-owned after post-merge
  regression.

The skill may reference `phase-{N}/phase-manifest.json.buildSubStep` to distinguish S5a
`red` from S5b `green-refactor`, but must not use it to skip the required
artifacts or protected human confirmations.

---

## Orchestration Workflow

### 0. Resolve Scope And Mode

Determine:
- TDD scope: phase, checkpoint, batch, bug, review finding, or one-off.
- Operating mode: Bug Batch, Phase Gate, or Spike.
- Applicable standards and SAGE gates.
- Stop conditions and any user-approved deferrals.

If the scope is ambiguous, ask the smallest number of clarifying questions needed.

### 1. Planning Worker

Delegate context-heavy planning to a subagent.

Require the plan to include:
- Concrete TDD cycles in execution order.
- Acceptance criteria for each cycle.
- Expected RED, GREEN, and REFACTOR steps.
- Exact files likely to change.
- Focused and broad test commands.
- Risk classification: Critical, Major, Minor.
- Artifact updates, if any.

### 2. Plan Quality Reviewer

Use a separate reviewer before implementation.

The reviewer must check:
- Tests prove behavior through public/user-observable interfaces where practical.
- Tests are simple, valuable, and would fail on the reported bug or unmet TDD.
- Implementation direction follows project conventions.
- State management is clean and testable.
- Deferrals are explicit and justified.

Do not implement until the plan verdict is approved or required amendments are clear.

### 3. Implementation Worker

Run SAGE-compliant RED/GREEN/REFACTOR cycles. In Bug Batch Mode, keep the loop
focused and lightweight. In Phase Gate Mode, preserve the S5a/S5b split exactly.

#### Phase Gate S5 Sequence

1. Set scope from the active session manifest, current phase, implementation
   plan, TDD spec, and scoped files.
2. Invoke or prompt `test-author` for S5a RED. It writes tests only and produces
   `phase-{N}-red-results.md`.
3. Confirm the RED artifact contains `STATUS: RED CONFIRMED` before any
   production/source edit is attempted.
4. Invoke or prompt `tdd-builder` for S5b GREEN/REFACTOR. It writes production
   code only, never weakens tests, and produces `phase-{N}-tdd-results.md`.
5. Invoke `code-simplifier` only after a GREEN task completes and only within
   its scoped production-file boundaries.
6. Require `phase-{N}-tdd-results.md` to contain `STATUS: PASS` before formal
   code review begins.

Rules:
- Prefer one behavior per cycle.
- Confirm RED before implementing. In Phase Gate Mode this is mandatory.
- Write only enough code to satisfy the current behavior.
- Refactor only after GREEN.
- Run focused tests after each meaningful cycle.
- Update TDD artifacts when the workflow requires it.
- If a RED test appears incorrect, stop and ask for correction. Do not weaken or
  delete tests from the implementation side.

### 4. Independent Quality Check

Use a second agent after implementation.

It must validate:
- Each acceptance criterion is met.
- Major/Critical findings are closed or explicitly deferred.
- Tests are behavior-focused and not shallow.
- Code follows loaded project standards.
- New risks, manual QA gaps, and artifact updates are identified.

If quality check fails, loop back to the implementation worker with exact refinements.

### 5. Test And Coverage Assessment

Run the smallest useful test set first, then broaden based on risk.

Include:
- Focused tests for changed behavior.
- Relevant integration/component tests.
- Build/typecheck/lint when the project uses them and risk warrants it.
- Qualitative coverage assessment: strong, adequate, residual gaps.
- Manual QA checklist for browser-only, visual, performance, or console-warning behavior.

### 6. Formal Gates When In Phase Gate Mode

After implementation stabilizes:
- Run S6 code review through `code-reviewer` and require
  `phase-{N}-code-review.md` to contain `Critical findings: 0`.
- Run S6.5 security review through `security-reviewer` and require
  `phase-{N}-security-review.md` to contain `Critical findings: 0`.
- Run S7 agent testing through `test-runner` and require
  `phase-{N}-test-results.md` to contain `STATUS: PASS`.
- Prepare S8 completion artifacts only after S7 passes and deferrals are
  recorded.
- If any gate fails, return to the correct owner for remediation. Do not edit a
  formal review artifact to make a marker pass.

---

## Handoff Contract

Every worker final response must include only the fields relevant to its role.
Hook-readable markers belong in the formal artifact owned by that role, not in
generic chat summaries or unrelated ledgers.

### Planning Worker

```text
VERDICT: READY_FOR_REVIEW | BLOCKED
TDD cycles:
Expected files:
Focused tests:
Broad tests:
Standards consulted:
Residual risks:
Next action:
```

### Plan Quality Reviewer

```text
VERDICT: APPROVED | NEEDS_REVISION | BLOCKED
Required amendments:
Test quality assessment:
Standards consulted:
Residual risks:
Next action:
```

### S5a Test Author

```text
VERDICT: RED_CONFIRMED | NEEDS_REVISION | BLOCKED
Artifacts updated:
Tests written:
RED evidence:
Next action:
```

The formal artifact must contain `STATUS: RED CONFIRMED` only when RED tests
fail for the intended behavioral reason rather than compilation or setup errors.

### S5b TDD Builder

```text
VERDICT: PASS | NEEDS_REFINEMENT | BLOCKED
Files changed:
Artifacts updated:
Tests run:
Refactors applied:
Residual risks:
Next action:
```

The formal artifact must contain `STATUS: PASS` only when the scoped TDD suite
passes.

### Quality Reviewers

```text
VERDICT: PASS | NEEDS_REFINEMENT | BLOCKED
Critical findings:
Major findings:
Minor findings:
Residual risks:
Next action:
```

Only `code-reviewer` and `security-reviewer` write `Critical findings: N` gate
markers, and only in their own formal artifacts.

### Test Runner

```text
VERDICT: PASS | FAIL | BLOCKED
Tests run:
Coverage assessment:
Manual QA:
Residual risks:
Next action:
```

Only `test-runner` writes the S7 `STATUS: PASS` or `STATUS: FAIL` marker in
`phase-{N}-test-results.md`.

For SAGE artifacts, preserve exact gate-marker lines required by hooks, such as
`STATUS: RED CONFIRMED`, `STATUS: PASS`, `Critical findings: N`, or
`Blocker findings: N`, but only in the artifact that the hook reads.

---

## Bug Batch Ledger

In Bug Batch Mode, keep a concise ledger in the chat by default. If persistence
is needed, ask for or use an approved non-gate artifact under the active phase
directory:

```markdown
## Bug Batch
- B1: [bug] - planned | fixed | verified | deferred
- B2: [bug] - planned | fixed | verified | deferred

## Verification
- Focused tests:
- Broad tests:
- Manual QA:

## Deferred
- D1: [reason and owner/approval needed]
```

Do not convert a bug batch into formal SAGE completion unless the user asks to proceed.

---

## Adoption And Pilot Requirement

Before enabling this skill to advance formal Phase Gate Mode in routine SAGE
work, pilot the revised skill in Bug Batch Mode on a low-risk QA issue.

Pilot pass criteria:
- The skill preserves the S5a/S5b role split.
- No subagent writes an artifact owned by another SAGE role.
- Hook markers appear only in the formal artifacts that hooks read.
- Protected manifest fields are not modified.
- The bug-batch ledger records focused tests, broad tests, residual risks, and
  any deferrals without implying formal phase completion.

If the pilot exposes role confusion, artifact ownership confusion, or protected
field edits, stop using Phase Gate Mode until the skill is revised again.

---

## Stop Conditions

Stop the loop only when one of these is true:
- All scoped TDDs pass and quality review passes.
- All in-scope Critical/Major findings are resolved.
- Remaining issues are explicitly deferred with user/product approval.
- A blocker requires human action, missing credentials, unavailable environment, product decision, or SAGE gate confirmation.

When blocked, report the exact blocker and the next human action. Do not work around SAGE gates.

---

## Subagent Prompting Rules

Prompts should be specific enough that the worker can act without reading the full chat.

Always include:
- Repository/root context.
- Scope and operating mode.
- Required standards/artifacts to read.
- Files or areas likely involved.
- Allowed writes.
- Required output fields.
- Whether to implement, review only, or test only.

The orchestrator should retain only the active scope, verdicts, blockers, test results, and next action in foreground context.
