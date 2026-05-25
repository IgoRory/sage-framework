---
name: session-status
description: >
  Produces a visual progress report for the active SAGE session showing
  completed steps with green checkmarks, current step status indicators
  (Not Started, In Progress, Blocked), and actionable next-step guidance.
  Use when the user asks "what is the session status", "sage session status",
  "show session progress", "where are we", or any variation requesting
  current workflow state. Read-only -- never modifies any file.
---

# Session Status

Reads the session manifest, phase artifacts, kickoff telemetry, and
workflow telemetry to produce a structured inline progress report.
Covers the full lifecycle from PRD completeness check through to
phase completion. Sprint mode is the primary target.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| Session manifest | `[SESSION_ROOT]/session-manifest.md` | Yes |
| Active session ID | `.sage/sessions/active-session.txt` | Yes |
| Phase artifacts | `[SESSION_ROOT]/phase-N/` | Yes |
| PRD/kickoff telemetry | `.sage/prd-interview-telemetry.jsonl` | No (enriches kickoff section) |
| Workflow telemetry | `[SESSION_ROOT]/workflow-telemetry.jsonl` | No (enriches TDD spec section) |
| Workflow config | `.sage/workflow-config.json` | No (for telemetry file path) |

---

## Step 1 -- Resolve session

Read `.sage/sessions/active-session.txt` to get the active session ID.
If the file does not exist or is empty, report:

> No active SAGE session found. Run a kick-off to create a session, or
> check that `.sage/sessions/active-session.txt` contains a valid session ID.

Read the session manifest from `[SESSION_ROOT]/session-manifest.md`.
Parse the JSON block. Extract:
- `sessionId`, `featureId`, `featureTitle`, `mode`, `kickoffDate`
- `sessionState` (status, foundationVerified, completionLog, etc.)
- All phase definitions (from root manifest)

Then read each phase's runtime from `phase-{N}/phase-manifest.json`
(plain JSON). These files contain `currentStep`, `stepStatus`,
`stepTimestamps`, `buildMode`, `batches`, `validationConfirmed`,
`hookRejectionCount`, `linearIssueStatus`, `startedAt`, `completedAt`,
etc. Assemble the unified view by combining root definitions with
per-phase runtime.

---

## Step 2 -- Read kickoff telemetry

Read `.sage/prd-interview-telemetry.jsonl` (path from
`workflow-config.json` field `prd.telemetryFile`, default
`.sage/prd-interview-telemetry.jsonl`).

Filter to events matching the session's feature ID (`linearIssueId`
or `featureId` from the manifest header). Look for:

| Event | What it confirms |
|-------|-----------------|
| `completeness_check_completed` | PRD scored and passed. Extract `score`, `passed` |
| `kickoff_dev_review_completed` | Dev review ran. Extract `concernCount`, `prdUpdatesApplied` |
| `phase_splitter_completed` | Session created. Extract `phaseCount` |

If the telemetry file does not exist or events are missing, mark those
kickoff steps as "No telemetry" rather than failing. The manifest itself
is sufficient proof that the session was created.

---

## Step 3 -- Read workflow telemetry

Read `[SESSION_ROOT]/workflow-telemetry.jsonl`. Look for:

| Event | What it confirms |
|-------|-----------------|
| `session_created` | Workflow telemetry bootstrapped |
| `tdd_specs_all_complete` | TDD specs generated. Extract `totalScenarioCount` |

If the file does not exist, skip this section.

---

## Step 4 -- Read phase artifacts

For each phase in the manifest, check the phase directory
`[SESSION_ROOT]/phase-N/` for these artifacts:

| Step | Artifact | Gate marker to check |
|------|----------|---------------------|
| S1 | `phase-N-dev-interview-summary.md` | Existence only |
| S2 | `phase-N-implementation-plan.md` | Existence only |
| S3 | `phase-N-traceability-review.md` | `Blocker findings: N` (anchored line) |
| S4 | `phase-N-plan-preview.canvas.tsx` or `phase-N-plan-preview.md` or `phase-N-calculation-proof.md` | Existence only |
| S5a | `phase-N-red-results.md` | `STATUS: RED CONFIRMED` (anchored line) |
| S5b | `phase-N-tdd-results.md` | `STATUS: PASS` (anchored line) |
| S6 | `phase-N-code-review.md` | `Critical findings: N` (anchored line) |
| S6.5 | `phase-N-security-review.md` | `Critical findings: N` (anchored line) |
| S7 | `phase-N-test-results.md` | `STATUS: PASS` (anchored line) |
| S8 | `phase-N-completion-report.md` | Existence only |

When checking anchored lines, use start-of-line matching to avoid
false positives in narrative text.

---

## Step 5 -- Determine step status per phase

For each phase, determine the display status for every step using
this precedence:

1. If `runtime.stepStatus[step]` is `"complete"` OR the step artifact
   exists with a passing gate marker: **Complete**
2. If `runtime.stepStatus[step]` is `"in-progress"` OR `runtime.currentStep`
   matches this step: **In Progress**
3. If any blocking condition applies (see blocked conditions table below):
   **Blocked** with reason
4. Otherwise: **Not Started**

### Blocked conditions table

| Step | Blocked when | Reason text |
|------|-------------|-------------|
| S1 | `runtime.linearIssueStatus` not in `{Approved, Foundation Verified, In Progress, Build Complete, Done}` | Phase not yet approved in Linear |
| S4 | S3 artifact has `Blocker findings` > 0 | Traceability review has [N] unresolved Blocker findings |
| S5 | `runtime.validationConfirmed` is not `true` | Plan validation not confirmed by developer |
| S5 | Phase type is `dependent` AND `sessionState.foundationVerified` is not `true` | Waiting for Foundation verification |
| S5b | S5a artifact missing or does not contain `STATUS: RED CONFIRMED` | RED phase not confirmed |
| S5 (checkpoint) | Current batch `confirmed` is `false` | Batch [N] not confirmed by developer |
| S6.5 | S6 artifact has `Critical findings` > 0 | Code review has [N] unresolved Critical findings |
| S7 | S6 artifact has `Critical findings` > 0 | Code review has [N] unresolved Critical findings |
| S7 | S6.5 artifact has `Critical findings` > 0 | Security review has [N] unresolved Critical findings |
| S8 | S7 artifact missing or does not contain `STATUS: PASS` | Agent testing not passing |

---

## Step 6 -- Generate next-action guidance

For each phase that is not yet complete, produce one actionable
guidance line. Use the first matching rule:

| Condition | Guidance |
|-----------|----------|
| Phase complete (in completionLog) | "Phase complete. Ready for merge." |
| S8 complete | "Completion report written. Phase ready for merge sequencing." |
| S7 complete + `STATUS: PASS` | "All tests passing. Generate the completion report (S8)." |
| S7 in progress | "Agent testing in progress. Wait for test suite to complete." |
| S6.5 complete + `Critical findings: 0` | "Security review clear. Proceed to agent testing (S7)." |
| S6.5 complete + `Critical findings` > 0 | "Security review found [N] critical findings. Fix and re-run security review." |
| S6 complete + `Critical findings: 0` | "Code review clear. Proceed to security review (S6.5)." |
| S6 complete + `Critical findings` > 0 | "Code review found [N] critical findings. Fix and re-run code review." |
| S5 complete (`STATUS: PASS`) | "Build complete, all TDD tests green. Proceed to code review (S6)." |
| S5 in progress + checkpoint + batch not confirmed | "Batch [N] review is ready at `[reviewPath]`. Review it, then set `batches[N].confirmed = true` in the session manifest." |
| S5 in progress | "Build in progress ([buildMode] mode, [buildSubStep] sub-step)." |
| S5 blocked (foundation) | "Blocked on Foundation verification. [Upstream phase(s)] must complete, merge, and pass regression. S1-S4 can proceed in parallel." |
| S5 blocked (validation) | "Plan preview is ready. Review it, then set `validationConfirmed = true` in the session manifest to unblock the build." |
| S4 complete + `validationConfirmed = false` | "Plan preview generated. Review it, then set `validationConfirmed = true` in the session manifest." |
| S4 in progress | "Plan preview generation in progress." |
| S3 complete + `Blocker findings` > 0 | "Traceability review has [N] Blocker findings. Resolve them before plan validation (S4)." |
| S3 complete + `Blocker findings: 0` | "Traceability review clear. Proceed to plan validation (S4)." |
| S3 in progress | "Traceability review in progress." |
| S2 complete | "Implementation plan ready. Proceed to traceability review (S3)." |
| S2 in progress | "Implementation planning in progress." |
| S1 complete | "Dev interview complete. Proceed to implementation planning (S2)." |
| S1 in progress | "Dev interview active. Complete all questions and choose build mode (Autonomous or Checkpoint)." |
| S1 not started + Linear approved | "Phase approved. Open the phase chat and begin the dev interview (S1)." |
| S1 not started + Linear not approved | "Phase not yet approved in Linear. PM or Lead Dev must approve the phase issue." |

---

## Step 7 -- Render output

Produce the report inline (not as a file). Use this exact structure:

``````
## SAGE Session Status — [featureTitle] ([sessionId])

**Mode:** [mode] · **Kickoff:** [kickoffDate] · **State:** [sessionState.status]

### Kickoff

[For each kickoff step, show checkmark if telemetry event found, or
dash if no telemetry. Include extracted metrics.]

✅ PRD completeness check — Score: [score]/100
✅ Developer review — [concernCount] concerns, [prdUpdatesApplied] PRD updates
✅ Phase breakdown — [phaseCount] phases created
✅ TDD specs generated — [totalScenarioCount] scenarios

[If a kickoff event is missing from telemetry but the session exists,
show the step with a dash and note "No telemetry recorded":]
— PRD completeness check — No telemetry recorded

### Phase [N]: [title] ([phaseType] — [layer])

**Developer:** [assignedDeveloper or "Unassigned"] · **Linear:** [linearIssueStatus]

[For each step S1-S8, show the appropriate icon:]
✅ S1 Dev Interview
✅ S2 Implementation Plan
▶ S3 Traceability Review — In Progress
⬜ S4 Plan Validation
⬜ S5 Build ([buildMode])
⬜ S6 Code Review
⬜ S6.5 Security Review
⬜ S7 Agent Testing
⬜ S8 Completion Report

[Repeat for each phase]

[If sessionState.foundationVerified is relevant, add:]

### Foundation Status

[foundationVerified ? "✅ Foundation verified — Dependent phases unblocked"
 : "⬜ Foundation not yet verified — Dependent phases blocked at S5"]

---

### What to do next

[One bullet per phase that is not yet complete, using the guidance
from Step 6. Order by phase number.]

- **Phase [N]:** [guidance text]
- **Phase [N]:** [guidance text]
``````

### Status icons

| Icon | Meaning |
|------|---------|
| ✅ | Complete |
| ▶ | In Progress |
| 🔴 | Blocked (with reason shown after dash) |
| ⬜ | Not Started |

---

## Constraints

- Strictly read-only — never writes to any file
- Never modifies the session manifest, telemetry, or any artifact
- If a data source is unavailable, degrade gracefully (show what is
  available, note what is missing)
- Produces inline output only — no artifact files
- Works in any chat context (orchestrator chat, phase chat, or
  standalone query)
