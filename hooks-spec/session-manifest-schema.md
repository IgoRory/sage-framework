# Session Manifest Schema

## Overview

`session-manifest.md` is the single source of truth for the hook
layer and all agent consumers throughout a Sprint work cycle.
It lives at `[SESSION_ROOT]/session-manifest.md` and is committed
to the repository.

The file has two parts:
1. A machine-readable JSON block (delimited by ```json ... ```) at the
   top of the file. This is what all hooks and agents read and write.
2. A human-readable markdown rendering below the JSON block, generated
   from the JSON at kick-off and at each significant state change.
   The markdown is for the team — it is never parsed by hooks.

> **Note:** The canonical manifest structure is defined by the
> session-manifest-template at `.cursor/templates/session-manifest-template.md`.
> The expanded schema below documents the full field set including fields
> that may be added during the work cycle. When in doubt, the template
> and running hooks in Profitability are the source of truth.

**Write ownership:**
- `phase-splitter` skill writes the initial manifest at kick-off, including
  assigning `phaseType` per phase using this logic:
  - `foundation` — no `upstreamPhases` AND has `downstreamPhases`
  - `independent` — no `upstreamPhases` AND no `downstreamPhases`
  - `dependent` — has one or more `upstreamPhases`
- Hook scripts update `phases[N].runtime.currentStep`,
  `phases[N].runtime.stepStatus`, and `phases[N].runtime.validationConfirmed`
  during the build sprint
- Orchestrator agent sets `sessionState.foundationVerified`
  after post-merge regression
- No agent or hook ever modifies `phases[N].definition`
  after kick-off — definitions are immutable once written

---

## Full JSON schema

```json
{
  // ─────────────────────────────────────────────────────────────────
  // LAYER 1: SESSION HEADER
  // Written once at kick-off by phase-splitter. Never modified.
  // ─────────────────────────────────────────────────────────────────
  "header": {
    "sessionId": "[FEATURE_ID]",
    "featureTitle": "string — matches Linear feature issue title exactly",
    "featureLinearId": "string — Linear feature issue ID e.g. PROF-7",
    "featurePrdPath": "string — repo-relative path to PRD e.g. .sage/prds/PROF-7/prd.md",
    "featureComponentSpecPath": "string — repo-relative path to component spec e.g. .sage/prds/PROF-7/component-spec.md",
    "mode": "mob | sprint | pair | solo",
    "prdCompletenessScore": 87,
    "kickoffDate": "ISO 8601 date e.g. 2026-05-12",
    "kickoffParticipants": ["the Product Manager", "Developer 1", "Developer 2", "Developer 3", "the Product Manager"],
    "createdAt": "ISO 8601 datetime",
    "lastUpdatedAt": "ISO 8601 datetime — updated on every write",
    "repoRoot": "string — absolute path to repo root on this machine",
    "sessionRoot": "string — absolute path to SESSION_ROOT",
    "workflowConfigPath": "string — path to workflow-config.json"
  },

  // ─────────────────────────────────────────────────────────────────
  // LAYER 2: PHASE DEFINITIONS
  // Written once at kick-off by phase-splitter. Never modified.
  // One entry per phase. Key is the phase number as a string.
  // ─────────────────────────────────────────────────────────────────
  "phases": {
    "1": {

      // ── Definition (immutable after kick-off) ────────────────────
      "definition": {
        "objective": "string — single sentence: what will exist after this phase",
        "phaseType": "foundation | independent | dependent",
        "tier": 0,
        "independenceScore": 95,
        "effortEstimateHours": { "low": 3, "high": 5 },
        "developerProfile": "ui-heavy | backend-heavy | full-stack | data-only | any",
        "upstreamDependencies": [],
        "downstreamConsumers": ["2"],
        "interfaceContract": "string | null — what this phase produces for downstream phases",
        "linearIssueId": "LIN-4822",
        "worktreeBranch": "LIN-4822-phase-1-allocation-rules-ui",
        "worktreePath": "string — absolute path to this phase's worktree",
        "requiredReferences": [
          "mockups/allocation-rules.html",
          "mockups/allocation-results.html"
        ],
        "scopedFiles": {
          "ui": [
            "src/app/features/allocation/allocation-rules.component.ts",
            "src/app/features/allocation/allocation-rules.component.html"
          ],
          "backend": [],
          "data": [],
          "test": [
            "src/app/features/allocation/allocation-rules.component.spec.ts"
          ]
        }
      },

      // ── Runtime state (written/updated by hooks during build) ────
      "runtime": {
        "assignedDeveloper": "string — name of developer assigned at planning",
        "linearIssueStatus": "Pending Approval | Approved | In Progress | Build Complete | Done",
        "currentStep": "dev-interview | implementation-plan | traceability-review | plan-validation | build | code-review | agent-testing | completion-report | complete",
        "buildMode": "autonomous | checkpoint",
        "buildSubStep": "red | green-refactor | null — tracks S5a/S5b progression within the build step",
        "validationConfirmed": false,
        "startedAt": "ISO 8601 datetime | null",
        "completedAt": "ISO 8601 datetime | null",
        "actualDurationHours": null,
        "stepStatus": {
          "dev-interview":       "pending | in-progress | complete | blocked",
          "implementation-plan": "pending | in-progress | complete | blocked",
          "traceability-review": "pending | in-progress | complete | blocked",
          "plan-validation":     "pending | in-progress | complete | blocked",
          "build":               "pending | in-progress | complete | blocked",
          "code-review":         "pending | in-progress | complete | blocked",
          "agent-testing":       "pending | in-progress | complete | blocked",
          "completion-report":   "pending | in-progress | complete | blocked"
        },
        "stepTimestamps": {
          "dev-interview":       { "startedAt": null, "completedAt": null },
          "implementation-plan": { "startedAt": null, "completedAt": null },
          "traceability-review": { "startedAt": null, "completedAt": null },
          "plan-validation":     { "startedAt": null, "completedAt": null },
          "build":               { "startedAt": null, "completedAt": null },
          "code-review":         { "startedAt": null, "completedAt": null },
          "agent-testing":       { "startedAt": null, "completedAt": null },
          "completion-report":   { "startedAt": null, "completedAt": null }
        },
        "batches": [
          {
            "id": 1,
            "label": "string — e.g. 'Component structure and data binding'",
            "taskIds": ["task-1", "task-2"],
            "confirmed": false,
            "startedAt": null,
            "completedAt": null,
            "testsPassing": null,
            "reviewPath": null
          }
        ],
        "currentBatchId": null,
        "findingSummary": {
          "traceabilityBlockers": 0,
          "traceabilityMajors": 0,
          "traceabilityMinors": 0,
          "codeReviewCriticals": 0,
          "codeReviewMajors": 0,
          "codeReviewMinors": 0
        },
        "hookRejectionCount": 0,
        "deferredItems": []
      }
    }
    // Repeat for "2", "3", ... per phase count from phase-splitter
  },

  // ─────────────────────────────────────────────────────────────────
  // LAYER 3: SESSION-LEVEL RUNTIME STATE
  // Updated throughout the work cycle.
  // ─────────────────────────────────────────────────────────────────
  "sessionState": {
    "status": "kick-off | async-approvals | build-sprint | review-merge | complete",
    "allPhasesApproved": false,
    "foundationVerified": false,
    "foundationVerifiedAt": null,
    "foundationRegressionResult": "pending | pass | fail | not-run",
    "buildSprintStartedAt": null,
    "buildSprintCompletedAt": null,
    "integrationTestStatus": "pending | pass | fail | not-run",
    "mergeOrder": ["1", "2", "3"],
    "activeLanes": ["1", "2"],
    "completedLanes": [],
    "blockedLanes": []
  },

  // ─────────────────────────────────────────────────────────────────
  // LAYER 4: PATH VALIDATION RECORD
  // Written by phase-splitter at kick-off after validating all paths.
  // Records the result of each path check so hooks can trust the
  // paths in phase definitions are real.
  // ─────────────────────────────────────────────────────────────────
  "pathValidation": {
    "validatedAt": "ISO 8601 datetime",
    "results": [
      {
        "path": "mockups/allocation-rules.html",
        "status": "EXISTS | NEW | MISSING",
        "resolvedAbsolutePath": "string"
      }
      // One entry per path across all phase scopedFiles and requiredReferences
    ],
    "missingPaths": [],
    "newPaths": [],
    "validationPassed": true
  },

  // ─────────────────────────────────────────────────────────────────
  // LAYER 5: KICK-OFF OUTPUTS
  // Written during Phase 02 kick-off. Never modified after kick-off.
  // ─────────────────────────────────────────────────────────────────
  "kickoffOutputs": {
    "devReviewLogPath": "string — path to kickoff-dev-review-log.md",
    "phaseSplitterBriefing": [
      {
        "raisedBy": "string — developer name",
        "concern": "string — plain language description",
        "implication": "string — what phase-splitter should know",
        "handledAs": "string — how it was addressed in the phase breakdown"
      }
    ],
    "prdUpdatesApplied": 0,
    "prdScoreAfterUpdate": 87,
    "phaseBreakdownPath": "string — path to phase-breakdown.md"
  },

  // ─────────────────────────────────────────────────────────────────
  // LAYER 6: COMPLETION LOG
  // Appended to as each phase completes. Read by session-performance-
  // evaluator and sprint-coordinator.
  // ─────────────────────────────────────────────────────────────────
  "completionLog": [
    {
      "phaseId": "1",
      "completedAt": "ISO 8601 datetime",
      "actualDurationHours": 4.5,
      "estimatedDurationHours": { "low": 3, "high": 5 },
      "testsPassing": true,
      "hookRejections": 1,
      "deferredItemCount": 0,
      "handoffDocPath": "string — path to phase-N-handoff.md",
      "completionReportPath": "string — path to phase-N-completion-report.md"
    }
  ]
}
```

---

## Path validation rules

The `phase-splitter` skill runs path validation before finalising
the manifest. Rules applied to every path in `scopedFiles` and
`requiredReferences` across all phases:

| Status | Condition | Action |
|---|---|---|
| `EXISTS` | File found at the resolved absolute path | Record resolved path, proceed |
| `NEW` | Path does not exist but follows a known pattern for new files (e.g. a new component file in the correct directory) | Record as NEW, proceed — hooks treat NEW paths as expected |
| `MISSING` | Path does not exist and does not match a NEW pattern | Block manifest finalisation with explicit error |

**A manifest with any `MISSING` paths is not finalised.**
The kick-off session must resolve missing paths before the manifest
is written and committed.

NEW path patterns (files expected to be created during build):
- Any path under `src/` that matches an existing directory structure
  but does not yet have the file
- Any test file (`.spec.ts`, `.test.ts`, `.Tests.cs`) that
  corresponds to a new source file in the same phase scope
- Migration files under `migrations/` or `Migrations/`

---

## Manifest update protocol

**Who can write what:**

| Field path | Writer | When |
|---|---|---|
| `header.*` | phase-splitter | Kick-off only |
| `phases[N].definition.*` | phase-splitter | Kick-off only |
| `phases[N].runtime.currentStep` | Hook scripts | During build sprint |
| `phases[N].runtime.stepStatus[step]` | Hook scripts | During build sprint |
| `phases[N].runtime.validationConfirmed` | Developer (manual) | S4 |
| `phases[N].runtime.stepTimestamps` | Hook scripts (Planned — not yet implemented) | During build sprint |
| `phases[N].runtime.findingSummary` | Agent skills (Planned — not yet implemented) | During build sprint |
| `phases[N].runtime.hookRejectionCount` | Hook scripts (Planned — not yet implemented) | On each rejection |
| `phases[N].runtime.deferredItems` | Agent skills | During build sprint |
| `phases[N].runtime.linearIssueStatus` | Hook scripts (afterMCPExecution) | On Linear status change |
| `sessionState.*` | Hook scripts + orchestrator | Throughout work cycle |
| `pathValidation.*` | phase-splitter | Kick-off only |
| `kickoffOutputs.*` | kickoff-dev-review + phase-splitter | Kick-off only |
| `completionLog` | S8 stop hook | On each phase completion |
| `header.lastUpdatedAt` | Any writer | On every write |

**Update mechanism:**
All manifest writes use a read-modify-write pattern:
1. Read the full JSON block from the manifest file
2. Apply the specific field update
3. Update `header.lastUpdatedAt`
4. Write the full JSON block back
5. Regenerate the human-readable markdown section from the updated JSON

Hook scripts that update the manifest use a file lock
(`manifest.lock`) to prevent concurrent writes from parallel
phase lanes corrupting the JSON.

---

## File lock protocol

> **Status: Planned — not yet implemented.** The `manifest.lock` /
> `fcntl` locking mechanism described below is not implemented in the
> current `hooks_utils.py`. It is documented here as the intended
> design for a future enhancement when concurrent manifest writes
> become a practical concern.

Since three phase lanes may attempt to write to the manifest
simultaneously (e.g. all three phases completing within seconds
of each other), a simple file lock is used:

```python
# In hooks_utils.py — manifest write with lock

import fcntl
import time

def write_manifest_field(
    session_root: Path,
    field_path: str,
    value: any,
    max_wait_seconds: int = 10
) -> None:
    """
    Read-modify-write a specific field in the manifest JSON block.
    Uses a file lock to prevent concurrent write corruption.
    field_path uses dot notation: e.g. "phases.1.runtime.currentStep"
    """
    manifest_path = session_root / "session-manifest.md"
    lock_path = session_root / "manifest.lock"

    deadline = time.time() + max_wait_seconds
    with open(lock_path, "w") as lock_file:
        while time.time() < deadline:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(0.1)
        else:
            raise RuntimeError(
                f"Could not acquire manifest lock within "
                f"{max_wait_seconds}s. Another process may be stuck."
            )

        try:
            # Read current manifest
            manifest = read_manifest(session_root)

            # Apply field update using dot-notation path
            keys = field_path.split(".")
            target = manifest
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value

            # Update lastUpdatedAt
            manifest["header"]["lastUpdatedAt"] = (
                datetime.now(timezone.utc).isoformat()
            )

            # Write back
            _write_manifest_json(manifest_path, manifest)

        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
```

**Note:** `fcntl` is Unix/macOS only. On Windows (developer machines
running Windows), replace with `msvcrt.locking` or use a
cross-platform lock library such as `filelock` (pip install filelock).
Since Python 3.12 is confirmed on developer machines, `filelock` is the
recommended approach for cross-platform compatibility.

---

## Human-readable markdown rendering

The section below the JSON block is regenerated from the JSON whenever
the manifest is written. It is never parsed by hooks. Its purpose is
to give developers a quick visual read of session state without
having to interpret JSON.

Rendering format:

```markdown
---

## Session: [featureTitle] ([sessionId])

**Mode:** [mode] · **Date:** [kickoffDate] · **PRD score:** [prdCompletenessScore]/100
**Participants:** [kickoffParticipants joined by ", "]

---

## Phase breakdown

| Phase | Objective | Tier | Effort | Developer | Status |
|---|---|---|---|---|---|
| 1 | [objective] | [tier] | [low]–[high]h | [assignedDeveloper] | [currentStep] |
| 2 | ... | ... | ... | ... | ... |

---

## Dependency order

Tier 0 (parallel start): Phase [N], Phase [N]
Tier 1 (unlocks after Tier 0): Phase [N]
Merge order: [mergeOrder joined by " → "]

---

## Step status

### Phase 1 — [objective]
| Step | Status | Started | Completed |
|---|---|---|---|
| S1 dev-interview | [stepStatus] | [startedAt] | [completedAt] |
| ... | ... | ... | ... |

[Repeat per phase]

---

## Completion log

[If empty: "No phases complete yet."]
[If entries exist: table of completed phases with duration and test status]

---

## Path validation

[If validationPassed: "✅ All [N] paths validated at [validatedAt]"]
[If not: "❌ [N] missing paths — manifest not finalised"]
```

---

## Initialisation procedure

The `phase-splitter` skill initialises the manifest at the end of
the kick-off session. Steps in order:

1. Build the full JSON object from the phase breakdown output
2. Run path validation across all `scopedFiles` and `requiredReferences`
3. If any path is `MISSING`: surface the error, do not write the manifest
4. Once all paths are `EXISTS` or `NEW`:
   - Write the JSON block to `session-manifest.md`
   - Generate the human-readable markdown section
   - Write `[SESSION_ROOT]` path to `.sage/sessions/active-session.txt`
   - Initialise `[SESSION_ROOT]/phase-N/telemetry.jsonl` as empty files
     (one per phase lane)
   - Commit: `git add .sage/ && git commit -m "init: session manifest
     for [featureTitle] ([sessionId])"`
   - Push to remote so all developer machines can pull

5. Each developer pulls before starting their phase lane
