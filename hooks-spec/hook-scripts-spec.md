# Hook Scripts Specification

Full specification for every Python script referenced in hooks.json.
Each script lives in `.cursor/hooks/scripts/`.

All scripts share a common pattern:
- Resolve REPO_ROOT by walking up from cwd until `.git` is found
- Read SESSION_ROOT from `[REPO_ROOT]/.sage/sessions/active-session.txt`
- Read the session manifest from `[SESSION_ROOT]/session-manifest.md`
- Determine current phase from manifest or environment
- Execute their specific check logic
- Exit 0 (permit) or exit 1 with a message (block)
- Write a telemetry event (enforcement hooks write hook_rejection on block)

The telemetry-logger handles all standard event logging.
Enforcement hooks only write telemetry on rejection (hook_rejection event).

---

## Shared utilities: `hooks_utils.py`

All scripts import from this shared module. Specify once here.

```python
# .cursor/hooks/scripts/hooks_utils.py
# This is a summary of the actual implementation — see the source file for full code.

import os
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone


# ── Typed exceptions ──────────────────────────────────────────────

class NoSessionError(Exception):
    """No active SAGE session — fail-open is correct."""
    pass

class SessionIntegrityError(Exception):
    """Active session exists but data is invalid — should NOT fail-open."""
    pass


# ── Repository and session resolution ─────────────────────────────

def find_repo_root() -> Path:
    """Walk up from cwd until .git is found. Raises NoSessionError."""

def get_session_root(repo_root: Path) -> Path:
    """
    Read active session from .sage/sessions/active-session.txt.
    Raises NoSessionError when file missing (fail-open).
    Raises SessionIntegrityError when session ID exists but directory doesn't.
    """

def get_phase_id() -> str | None:
    """Read from SAGE_PHASE_ID env var, falling back to .sage/current-phase.txt."""

def get_phase_dir(session_root: Path, phase_id: str) -> Path:
    """Return session_root / f'phase-{phase_id}'."""

def read_manifest(session_root: Path) -> dict:
    """
    Parse ```json ... ``` block from session-manifest.md.
    Raises SessionIntegrityError if file exists but JSON is malformed.
    """


# ── Anchored line parsing ────────────────────────────────────────

def find_marker_value(content: str, prefix: str) -> int | None:
    """
    Search for a line matching `<prefix>: <integer>` anchored at start-of-line.
    Returns the integer value, or None if no matching line is found.
    """

def has_status_marker(content: str, marker: str) -> bool:
    """
    Return True if `marker` appears as a standalone line (anchored at start-of-line).
    Prevents false matches inside narrative text.
    """


# ── Gate outcomes ─────────────────────────────────────────────────

def block(message: str, phase_id: str | None = None) -> None:
    """Print message to stderr, exit code 1 (block)."""

def permit() -> None:
    """Exit code 0 (permit)."""


# ── Telemetry ─────────────────────────────────────────────────────

def write_telemetry_event(session_root: Path, event: dict) -> None:
    """
    Append event to workflow-telemetry.jsonl in session_root.
    Silently no-ops on failure.
    Signature: (session_root, event_dict) — 2 parameters.
    """
```

**Important notes on spec vs. actual implementation:**

- **Phase ID resolution:** The actual implementation checks `SAGE_PHASE_ID` env var first, then falls back to `.sage/current-phase.txt` in the repo root. This covers worktrees and branch-based workflows where the env var is not set.
- **`write_telemetry_event` signature:** The actual implementation takes 2 parameters `(session_root, event_dict)`, not 4. Telemetry writes to a session-level `workflow-telemetry.jsonl`, not per-phase files.
- **`block` signature:** The actual implementation takes `(message, phase_id=None)` — 2 parameters. When `phase_id` is provided, `block()` auto-increments `hookRejectionCount` in the manifest before exiting.
- **`manifest.lock`:** Implemented using the `filelock` package (cross-platform). Acquired by `write_manifest_field()`, `write_manifest_fields()`, and `increment_rejection_count()`.
- **`stepTimestamps`, `hookRejectionCount`:** Written by the `manifest-step-writer` hook (step transitions) and `block()` in `hooks_utils` (rejection count). `findingSummary` is documented in schema but not yet written by any hook.
- **All gate scripts** use typed exceptions: `except NoSessionError: permit()` (fail-open) and `except SessionIntegrityError as e: block(...)` (fail-closed).

---

## Script 1: `telemetry_logger.py`

**Purpose:** Logging and idle detection. Writes every hook event to the
session-level `workflow-telemetry.jsonl`. Never blocks. Also detects idle
gaps between consecutive events for the same phase — when the gap exceeds
`telemetry.idleThresholdMinutes` (from `workflow-config.json`), emits
`step_paused` and `step_resumed` event pairs retrospectively.

**State file:** `.telemetry-last-event.json` in `[SESSION_ROOT]/` tracks
the last event timestamp per phase.

**Idle detection events emitted:**

| Event | Timestamp | Fields |
|---|---|---|
| `step_paused` | `lastEventTime + idleBufferMinutes` | `phaseId`, `sessionId`, `step`, `idleGapMinutes` |
| `step_resumed` | current time | `phaseId`, `sessionId`, `step`, `idleGapMinutes` |

See `hooks-spec/scripts/telemetry_logger.py` for the canonical implementation.

---

## Script 2: `plan_mode_enforcer.py`

**Purpose:** Blocks file-write tool calls during S1 dev interview.
Enforces Plan mode structurally — the agent cannot write code or
modify files regardless of its mode setting.

**Gate:** Applies only when `manifest.phases[current_phase].currentStep
= "dev-interview"`.

**Blocks:** Any tool call whose name contains "write", "edit", "create",
"apply", "insert", or "delete" (case-insensitive). Specifically targets:
`str_replace_editor`, `write_file`, `create_file`, `apply_diff`,
`edit_file`, and any tool matching the write pattern.

**Permits:** All read tools, search tools, MCP tools, shell commands that
are read-only (git log, git status, cat, ls, etc.).

```python
# .cursor/hooks/scripts/plan_mode_enforcer.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, write_telemetry_event, block, permit
)

# Tool names that constitute file-write operations
WRITE_TOOL_PATTERNS = [
    "str_replace_editor", "write_file", "create_file", "apply_diff",
    "edit_file", "insert_content", "delete_file", "rename_file",
    "write", "edit", "create", "apply", "insert", "delete"
]

def is_write_tool(tool_name: str) -> bool:
    tool_lower = tool_name.lower()
    return any(pattern in tool_lower for pattern in WRITE_TOOL_PATTERNS)


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    tool_name = event_input.get("tool_name", "")

    # Only check during dev-interview step
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    current_step = phase_data.get("currentStep", "")

    if current_step != "dev-interview":
        permit()
        return

    if not is_write_tool(tool_name):
        permit()
        return

    block(
        message=(
            f"PLAN MODE ENFORCED — S1 Dev Interview\n"
            f"Tool '{tool_name}' is a file-write operation.\n"
            f"File-write tools are blocked during the dev interview step.\n"
            f"The dev interview runs in Plan mode (read-only).\n"
            f"Complete the interview and advance to S2 before writing any files."
        ),
        telemetry_data={
            "step": "dev-interview",
            "tool_name": tool_name,
            "rejection_reason": "plan_mode_write_attempt"
        },
        session_root=session_root,
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
```

---

## Script 3: `manifest_step_gate.py`

**Purpose:** Enforces sequential step progression. Before a step-specific
tool can run, the prior step must be marked complete in the manifest.

**Step → required prior completion mapping:**

| Current step tool being called | Required prior step status |
|---|---|
| implementation-plan tool (S2) | S1 dev-interview = complete |
| traceability-review tool (S3) | S2 implementation-plan = complete |
| plan-preview tool (S4) | S3 traceability-review = complete, zero Blockers |
| code-review tool (S6) | S5 build = complete (tdd-results STATUS:PASS) |
| security-reviewer tool (S6.5) | S6 code-review = complete, zero Critical findings |
| test-runner tool (S7) | S6 code-review and S6.5 security-review = complete, zero Critical findings |
| completion-report tool (S8) | S7 agent-testing = complete (test-results STATUS:PASS) |

```python
# .cursor/hooks/scripts/manifest_step_gate.py

import sys
import json
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit
)

# Maps tool names to the step they initiate and what prior step must be done
STEP_GATE_MAP = {
    "generate_implementation_plan": {
        "current_step": "implementation-plan",
        "required_step": "dev-interview",
        "required_artifact": "phase-{phase_id}-dev-interview-summary.md",
    },
    "run_traceability_review": {
        "current_step": "traceability-review",
        "required_step": "implementation-plan",
        "required_artifact": "phase-{phase_id}-implementation-plan.md",
    },
    "generate_plan_preview": {
        "current_step": "plan-validation",
        "required_step": "traceability-review",
        "required_artifact": "phase-{phase_id}-traceability-review.md",
        "required_condition": "zero_blockers"
    },
    "run_code_review": {
        "current_step": "code-review",
        "required_step": "build",
        "required_artifact": "phase-{phase_id}-tdd-results.md",
        "required_condition": "tdd_status_pass"
    },
    "run_test_suite": {
        "current_step": "agent-testing",
        "required_step": "code-review",
        "required_artifact": "phase-{phase_id}-code-review.md",
        "required_condition": "zero_critical_findings"
    },
    "generate_completion_report": {
        "current_step": "completion-report",
        "required_step": "agent-testing",
        "required_artifact": "phase-{phase_id}-test-results.md",
        "required_condition": "test_status_pass"
    },
}


def check_condition(condition: str, artifact_path: Path,
                    phase_id: str) -> tuple[bool, str]:
    """
    Check a required condition on an artifact file.
    Returns (passed: bool, reason: str).
    """
    if not artifact_path.exists():
        return False, f"Required artifact not found: {artifact_path.name}"

    content = artifact_path.read_text(encoding="utf-8")

    if condition == "tdd_status_pass":
        if "STATUS: PASS" not in content:
            return False, (
                f"{artifact_path.name} does not contain 'STATUS: PASS'.\n"
                f"All TDD tests must pass before code review can begin."
            )

    elif condition == "test_status_pass":
        if "STATUS: PASS" not in content:
            return False, (
                f"{artifact_path.name} does not contain 'STATUS: PASS'.\n"
                f"All agent tests must pass before completion report can be generated."
            )

    elif condition == "zero_blockers":
        import re
        blocker_match = re.search(
            r"Blocker findings[:\s]+(\d+)", content, re.IGNORECASE)
        if blocker_match and int(blocker_match.group(1)) > 0:
            count = blocker_match.group(1)
            return False, (
                f"{artifact_path.name} has {count} unresolved Blocker finding(s).\n"
                f"All Blocker findings must be resolved before plan validation."
            )

    elif condition == "zero_critical_findings":
        import re
        critical_match = re.search(
            r"Critical findings[:\s]+(\d+)", content, re.IGNORECASE)
        if critical_match and int(critical_match.group(1)) > 0:
            count = critical_match.group(1)
            return False, (
                f"{artifact_path.name} has {count} unresolved Critical finding(s).\n"
                f"All Critical code review findings must be resolved before testing."
            )

    return True, ""


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    tool_name = event_input.get("tool_name", "")
    gate = STEP_GATE_MAP.get(tool_name)

    if not gate:
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    artifact_name = gate["required_artifact"].format(phase_id=phase_id)
    artifact_path = phase_dir / artifact_name

    # Check artifact existence
    if not artifact_path.exists():
        block(
            message=(
                f"STEP GATE BLOCKED — {gate['current_step'].upper()}\n"
                f"Required artifact not found: {artifact_name}\n"
                f"Step '{gate['required_step']}' must be completed before "
                f"'{gate['current_step']}' can begin.\n"
                f"Complete {gate['required_step']} and ensure the output "
                f"file is written to the phase directory."
            ),
            telemetry_data={
                "step": gate["current_step"],
                "tool_name": tool_name,
                "rejection_reason": "missing_prior_step_artifact",
                "missing_artifact": artifact_name
            },
            session_root=session_root,
            phase_id=phase_id
        )

    # Check condition if required
    condition = gate.get("required_condition")
    if condition:
        passed, reason = check_condition(condition, artifact_path, phase_id)
        if not passed:
            block(
                message=(
                    f"STEP GATE BLOCKED — {gate['current_step'].upper()}\n"
                    f"{reason}"
                ),
                telemetry_data={
                    "step": gate["current_step"],
                    "tool_name": tool_name,
                    "rejection_reason": f"condition_failed_{condition}",
                    "condition": condition,
                    "artifact": artifact_name
                },
                session_root=session_root,
                phase_id=phase_id
            )

    permit()


if __name__ == "__main__":
    main()
```

---

## Script 4: `required_references_gate.py`

**Purpose:** Blocks any code-writing shell command during S5 build until
every file listed in `manifest.phases[phase_id].required_references`
has a corresponding `afterReadFile` event in the phase telemetry log.

**Only active during S5 (build step).** Permits all commands in other steps.

**What counts as a "code-writing" command:** Any shell command that writes
to a source file. Identified by the presence of file extension patterns
in the command string: `.cs`, `.ts`, `.js`, `.py`, `.sql`, `.html`,
`.css`, `.json` — combined with write-intent verbs (`>`, `tee`,
`write`, `Set-Content`) or editor invocations. Read-only commands
(git status, cat, ls, dotnet test, npm test) are always permitted.

```python
# .cursor/hooks/scripts/required_references_gate.py

import sys
import json
import re
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_telemetry_path, block, permit
)

# Patterns that suggest a shell command is writing to a source file
WRITE_COMMAND_PATTERNS = [
    r"\s>\s",           # output redirect
    r"tee\s",           # tee command
    r"Set-Content",     # PowerShell write
    r"Out-File",        # PowerShell write
    r"new-item.*-value",# PowerShell create
]

# Extensions that indicate a source/config file
SOURCE_EXTENSIONS = [
    ".cs", ".ts", ".js", ".tsx", ".jsx", ".py", ".sql",
    ".html", ".css", ".scss", ".json", ".yaml", ".yml",
    ".csproj", ".sln", ".config"
]

def is_write_command(command: str) -> bool:
    for pattern in WRITE_COMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

def get_read_files_from_telemetry(telemetry_path: Path) -> set:
    """
    Parse the telemetry log and return a set of all file paths that
    have an afterFileEdit event with edit_type = 'read' or an
    afterReadFile event.
    """
    read_files = set()
    if not telemetry_path.exists():
        return read_files
    with open(telemetry_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get("hook_event_name") in (
                    "afterReadFile", "afterFileEdit"
                ):
                    file_path = record.get("file_path", "")
                    if file_path:
                        read_files.add(Path(file_path).name.lower())
                        read_files.add(file_path.lower())
            except json.JSONDecodeError:
                continue
    return read_files


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    # Only check during S5 build step
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    current_step = phase_data.get("currentStep", "")
    if current_step != "build":
        permit()
        return

    command = event_input.get("command", "")
    if not is_write_command(command):
        permit()
        return

    # Get required references from manifest
    required_refs = phase_data.get("required_references", [])
    if not required_refs:
        permit()
        return

    # Get files already read from telemetry
    telemetry_path = get_telemetry_path(session_root, phase_id)
    read_files = get_read_files_from_telemetry(telemetry_path)

    # Check each required reference
    unread = []
    for ref in required_refs:
        ref_name = Path(ref).name.lower()
        ref_full = ref.lower()
        if ref_name not in read_files and ref_full not in read_files:
            unread.append(ref)

    if not unread:
        permit()
        return

    unread_list = "\n  - ".join(unread)
    block(
        message=(
            f"BUILD BLOCKED — Required references not yet read\n"
            f"The following files must be opened and read before "
            f"any code can be written:\n\n"
            f"  - {unread_list}\n\n"
            f"Open each file, read its contents, then retry the build command.\n"
            f"These files are listed in the session manifest under "
            f"phase-{phase_id}.required_references."
        ),
        telemetry_data={
            "step": "build",
            "rejection_reason": "required_references_not_read",
            "unread_files": unread,
            "command_summary": command[:200]
        },
        session_root=session_root,
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
```

---

## Script 5: `validation_confirmed_gate.py`

**Purpose:** Blocks the build tool from launching if
`manifest.phases[phase_id].validation_confirmed` is not `true`.
Works in tandem with required_references_gate — both must pass.

**Cannot be bypassed by the agent.** The `validation_confirmed` field
can only be set by the developer explicitly. No automated process
sets this field.

```python
# .cursor/hooks/scripts/validation_confirmed_gate.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit
)

BUILD_TOOLS = ["run_build", "start_build", "execute_build", "build"]

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    tool_name = event_input.get("tool_name", "").lower()
    if not any(bt in tool_name for bt in BUILD_TOOLS):
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    validation_confirmed = phase_data.get("validation_confirmed", False)

    if validation_confirmed is True:
        permit()
        return

    block(
        message=(
            f"BUILD BLOCKED — Plan validation not confirmed\n"
            f"manifest.phases.{phase_id}.validation_confirmed is not set to true.\n\n"
            f"To unblock:\n"
            f"1. Review the plan preview generated in S4\n"
            f"2. Confirm it accurately represents the implementation plan\n"
            f"3. Set validation_confirmed: true in the session manifest\n\n"
            f"This field must be set by the developer. "
            f"It cannot be auto-set by the agent."
        ),
        telemetry_data={
            "step": "build",
            "tool_name": tool_name,
            "rejection_reason": "validation_not_confirmed"
        },
        session_root=session_root,
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
```

---

## Script 6: `phase_approval_gate.py`

**Purpose:** Blocks phase launch (S1 dev interview) until the phase's
`linearIssueStatus` in the session manifest is "Approved" (or a
downstream status). This is a manifest-local check — it does not query
Linear directly.

The phase-splitter skill updates `linearIssueStatus` to "Approved" in
the manifest during kick-off (Step 11) after the session driver confirms
approval. This gate acts as a safety net: if the manifest was not updated
(e.g. the session was interrupted before approval), it blocks S1 entry.

**Only fires at S1 entry** — when `currentStep` is `dev-interview`.
After the step advances past `dev-interview`, this gate permits all
subsequent tool calls unconditionally.

**Note on mode:** The workflow mode (mob, sprint, pair, solo) is applied
to the Linear phase issue as a label from the `SAGE Workflow Mode` label
group (e.g. `mode:sprint`). This is set automatically by the
`phase-splitter` skill at kick-off. Hook scripts read mode from the
session manifest `mode` field — not from Linear.

```python
# .cursor/hooks/scripts/phase_approval_gate.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit, write_telemetry_event,
    NoSessionError, SessionIntegrityError
)

APPROVED_STATUSES = {"Approved", "Foundation Verified", "In Progress", "Build Complete", "Done"}

INTERVIEW_INITIATING_TOOLS = {
    "read_file", "list_directory", "search_files",
    "write_file", "create_file", "edit_file"
}


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except NoSessionError:
        permit()
        return
    except SessionIntegrityError as e:
        block(message=f"SESSION INTEGRITY ERROR — {e}")
        return

    if not phase_id:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    if current_step != "dev-interview":
        permit()
        return

    linear_status = runtime.get("linearIssueStatus", "Pending Approval")
    if linear_status in APPROVED_STATUSES:
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "phase-approval-gate",
        "phaseId": phase_id,
        "linearIssueStatus": linear_status,
        "reason": "Phase not yet approved in Linear"
    })

    block(
        message=(
            f"APPROVAL GATE — Phase {phase_id} has not been approved.\n\n"
            f"Current Linear status: {linear_status}\n"
            f"Required status: Approved\n\n"
            f"The Product Manager and Lead Dev must approve this phase issue in Linear "
            f"before build work can begin. Once approved, update linearIssueStatus "
            f"in the session manifest to 'Approved'."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
```

---

## Script 7: `completion_report_stop_gate.py`

**Purpose:** The hardest gate in the workflow. Fires on the `stop` event.
Blocks the agent from ending its turn to generate the completion report
unless `phase-N-test-results.md` exists with a line containing exactly
`STATUS: PASS`. No exceptions.

This is the structural fix for the Expense Allocations failure where
the agent declared the phase complete without running tests.

```python
# .cursor/hooks/scripts/completion_report_stop_gate.py

import sys
import json
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit
)


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    # Only block if the agent is attempting to generate a completion report
    # Check current step and stop reason
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    current_step = phase_data.get("currentStep", "")
    stop_reason = event_input.get("reason", "")

    # Apply gate if in completion-report step or if agent is trying to stop
    # after S7 (common failure mode: combining S7 and S8)
    relevant_steps = {"completion-report", "agent-testing", "build"}
    if current_step not in relevant_steps:
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    test_results_path = phase_dir / f"phase-{phase_id}-test-results.md"

    # Check file exists
    if not test_results_path.exists():
        block(
            message=(
                f"COMPLETION BLOCKED — Test results not found\n"
                f"Cannot generate completion report for phase {phase_id}.\n\n"
                f"Required file does not exist:\n"
                f"  {test_results_path.name}\n\n"
                f"Step S7 (agent testing) must complete successfully and write\n"
                f"test results before this phase can be declared complete.\n\n"
                f"Do not combine S7 and S8. Complete S7 fully first."
            ),
            telemetry_data={
                "step": current_step,
                "rejection_reason": "test_results_missing",
                "expected_file": test_results_path.name
            },
            session_root=session_root,
            phase_id=phase_id
        )

    # Check STATUS: PASS
    content = test_results_path.read_text(encoding="utf-8")
    if "STATUS: PASS" not in content:
        # Check if STATUS: FAIL is present
        status_line = "unknown"
        for line in content.splitlines():
            if "STATUS:" in line:
                status_line = line.strip()
                break

        block(
            message=(
                f"COMPLETION BLOCKED — Tests not passing\n"
                f"Cannot generate completion report for phase {phase_id}.\n\n"
                f"File {test_results_path.name} does not contain 'STATUS: PASS'.\n"
                f"Current status line: {status_line}\n\n"
                f"All tests must pass before the phase can be declared complete.\n"
                f"Resolve failing tests and re-run the test suite."
            ),
            telemetry_data={
                "step": current_step,
                "rejection_reason": "test_results_not_passing",
                "status_found": status_line
            },
            session_root=session_root,
            phase_id=phase_id
        )

    permit()


if __name__ == "__main__":
    main()
```

---

## Script 8: `tdd_results_gate.py`

**Purpose:** Blocks the code-review tool (S6) from running unless
`phase-N-tdd-results.md` exists with `STATUS: PASS`.

```python
# .cursor/hooks/scripts/tdd_results_gate.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    get_phase_dir, block, permit
)

CODE_REVIEW_TOOLS = ["run_code_review", "code_review", "start_code_review"]

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    tool_name = event_input.get("tool_name", "").lower()
    if not any(t in tool_name for t in CODE_REVIEW_TOOLS):
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    tdd_results_path = phase_dir / f"phase-{phase_id}-tdd-results.md"

    if not tdd_results_path.exists():
        block(
            message=(
                f"CODE REVIEW BLOCKED — TDD results not found\n"
                f"Required file does not exist: {tdd_results_path.name}\n\n"
                f"Complete S5 (build with TDD red-green-refactor) before "
                f"running code review.\n"
                f"The TDD results file must be written by the build step."
            ),
            telemetry_data={
                "step": "code-review",
                "rejection_reason": "tdd_results_missing"
            },
            session_root=session_root,
            phase_id=phase_id
        )

    content = tdd_results_path.read_text(encoding="utf-8")
    if "STATUS: PASS" not in content:
        block(
            message=(
                f"CODE REVIEW BLOCKED — TDD suite not passing\n"
                f"{tdd_results_path.name} does not contain 'STATUS: PASS'.\n\n"
                f"All TDD tests must be green before code review begins.\n"
                f"Fix failing tests and re-run the TDD suite."
            ),
            telemetry_data={
                "step": "code-review",
                "rejection_reason": "tdd_results_not_passing"
            },
            session_root=session_root,
            phase_id=phase_id
        )

    permit()

if __name__ == "__main__":
    main()
```

---

## Script 9: `code_review_gate.py`

**Purpose:** Blocks the security-reviewer tool (S6.5) and test-runner tool
(S7) from launching unless `phase-N-code-review.md` exists with zero open
Critical findings.

```python
# .cursor/hooks/scripts/code_review_gate.py

import sys
import json
import re
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    get_phase_dir, block, permit
)

TEST_RUNNER_TOOLS = ["run_test_suite", "run_tests", "start_testing", "test_runner"]

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    tool_name = event_input.get("tool_name", "").lower()
    if not any(t in tool_name for t in TEST_RUNNER_TOOLS):
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    review_path = phase_dir / f"phase-{phase_id}-code-review.md"

    if not review_path.exists():
        block(
            message=(
                f"TESTING BLOCKED — Code review not found\n"
                f"Required file does not exist: {review_path.name}\n\n"
                f"Complete S6 (code review) before running the test suite."
            ),
            telemetry_data={
                "step": "agent-testing",
                "rejection_reason": "code_review_missing"
            },
            session_root=session_root,
            phase_id=phase_id
        )

    content = review_path.read_text(encoding="utf-8")
    critical_match = re.search(
        r"Critical findings[:\s]+(\d+)", content, re.IGNORECASE)

    if critical_match and int(critical_match.group(1)) > 0:
        count = critical_match.group(1)
        block(
            message=(
                f"TESTING BLOCKED — Unresolved Critical findings\n"
                f"{review_path.name} has {count} unresolved Critical finding(s).\n\n"
                f"All Critical code review findings must be resolved before "
                f"the test suite can run.\n"
                f"Address each Critical finding and re-run code review."
            ),
            telemetry_data={
                "step": "agent-testing",
                "rejection_reason": "critical_findings_unresolved",
                "critical_count": count
            },
            session_root=session_root,
            phase_id=phase_id
        )

    permit()

if __name__ == "__main__":
    main()
```

---

## Script 9b: `security_review_gate.py`

**Purpose:** Blocks the test-runner tool (S7) from launching unless
`phase-N-security-review.md` exists with zero open Critical findings.

**Gate condition:** Applies when the current manifest step is `agent-testing`.
The hook reads `[SESSION_ROOT]/phase-{N}/phase-{N}-security-review.md` and
requires an anchored `Critical findings: 0` marker. Missing markers, missing
files, or non-zero Critical counts block S7.

**Implementation note:** The script mirrors `code_review_gate.py` and uses
`find_marker_value(content, "Critical findings")` from `hooks_utils.py` so
narrative mentions do not satisfy the gate.

---

## Script 10b: `foundation_verified_gate.py`

**Purpose:** Blocks Dependent phases from starting S5 build until all
Foundation phases have merged to main and passed the post-merge
regression suite. Foundation phases are never blocked by this gate.
Dependent phases may complete S1–S4 before Foundation is verified —
only S5 build is gated.

**Gate condition:** `manifest.sessionState.foundationVerified = true`

This field is set by the orchestrator agent after it runs the
regression suite on main following all Foundation phase merges.
It cannot be set manually or by any hook script.

```python
# .cursor/hooks/scripts/foundation_verified_gate.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit
)

BUILD_TOOLS = ["run_build", "start_build", "execute_build", "build"]

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    # Only check during S5 build step
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    if runtime.get("currentStep") != "build":
        permit()
        return

    # Only check for build tool calls
    tool_name = event_input.get("tool_name", "").lower()
    if not any(bt in tool_name for bt in BUILD_TOOLS):
        permit()
        return

    # Foundation and Independent phases are never blocked by this gate
    phase_definition = phase_data.get("definition", {})
    phase_type = phase_definition.get("phaseType", "foundation")
    if phase_type in ("foundation", "independent"):
        permit()
        return

    # Dependent phase — check foundationVerified flag
    session_state = manifest.get("sessionState", {})
    foundation_verified = session_state.get("foundationVerified", False)

    if foundation_verified:
        permit()
        return

    # Determine which Foundation phases this phase depends on
    upstream = phase_definition.get("upstreamDependencies", [])
    upstream_str = ", ".join(f"Phase {p}" for p in upstream) if upstream else "upstream phases"

    block(
        message=(
            f"DEPENDENT PHASE BLOCKED — Foundation not yet verified\n"
            f"Phase {phase_id} is a Dependent phase.\n"
            f"Depends on: {upstream_str}\n\n"
            f"manifest.sessionState.foundationVerified is not set to true.\n\n"
            f"This gate will unlock automatically after:\n"
            f"1. All Foundation phase PRs are merged to main\n"
            f"2. The orchestrator runs the post-merge regression suite\n"
            f"3. All regression tests pass\n\n"
            f"You may continue S1\u2013S4 planning steps while you wait.\n"
            f"Only S5 build is blocked until Foundation is verified.\n\n"
            f"If Foundation phases have merged but this gate is still\n"
            f"blocking, check: the regression suite may have failed.\n"
            f"Look for a Linear issue flagging a regression failure."
        ),
        telemetry_data={
            "step": "build",
            "rejection_reason": "foundation_not_verified",
            "phase_type": "dependent",
            "upstream_dependencies": upstream
        },
        session_root=session_root,
        phase_id=phase_id
    )

if __name__ == "__main__":
    main()
```

---

## Script 10a: `batch_confirmation_gate.py`

**Purpose:** In checkpoint build mode, blocks the next batch's build tool
from launching until the developer has confirmed the current batch by
setting `batches[currentBatchId].confirmed = true` in the session manifest.
Also emits batch lifecycle telemetry events (`batch_started`,
`batch_confirmed`) when the gate passes.

**Only active during S5 AND when `buildMode = "checkpoint"`.**
In autonomous mode or any other step, permits immediately.

**Batch telemetry events emitted on gate pass:**

| Event | Condition | Fields |
|---|---|---|
| `batch_started` | First pass for a batch (gate permits) | `phaseId`, `sessionId`, `batchId`, `batchLabel`, `taskCount` |
| `batch_confirmed` | Pass after confirmation wait (confirmed flipped from false to true) | `phaseId`, `sessionId`, `batchId`, `batchLabel`, `confirmationWaitMinutes` |

**State file:** `.telemetry-batch-state.json` in `[SESSION_ROOT]/` prevents
duplicate event emission on repeated gate checks.

```python
# .cursor/hooks/scripts/batch_confirmation_gate.py

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit
)

BUILD_TOOLS = ["run_build", "start_build", "execute_build", "build"]

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})

    # Only check during build step
    if runtime.get("currentStep") != "build":
        permit()
        return

    # Only check in checkpoint mode
    if runtime.get("buildMode", "autonomous") != "checkpoint":
        permit()
        return

    # Only check for build tool calls
    tool_name = event_input.get("tool_name", "").lower()
    if not any(bt in tool_name for bt in BUILD_TOOLS):
        permit()
        return

    # First batch has no prior batch to confirm — permit
    current_batch_id = runtime.get("currentBatchId")
    if current_batch_id is None:
        permit()
        return

    # Find current batch and check confirmation
    batches = runtime.get("batches", [])
    current_batch = next((b for b in batches if b.get("id") == current_batch_id), None)

    if not current_batch or current_batch.get("confirmed") is True:
        permit()
        return

    review_path = current_batch.get("reviewPath",
        f"phase-{phase_id}-batch-{current_batch_id}-review.md")
    batch_label = current_batch.get("label", f"Batch {current_batch_id}")

    block(
        message=(
            f"CHECKPOINT BUILD BLOCKED — Batch {current_batch_id} not confirmed\n"
            f"Batch: {batch_label}\n\n"
            f"To unblock:\n"
            f"1. Review batch results: {review_path}\n"
            f"2. Verify all batch tests are passing\n"
            f"3. Set phases.{phase_id}.runtime.batches[{current_batch_id-1}]"
            f".confirmed = true in the session manifest\n\n"
            f"This field must be set manually. The next batch cannot start\n"
            f"until you have reviewed and confirmed this batch."
        ),
        telemetry_data={
            "step": "build",
            "rejection_reason": "batch_not_confirmed",
            "current_batch_id": current_batch_id,
            "batch_label": batch_label
        },
        session_root=session_root,
        phase_id=phase_id
    )

if __name__ == "__main__":
    main()
```

---

## Script 10: `skill_update_trigger_watcher.py`

**Purpose:** Fires on afterFileEdit. Detects when a new trigger file
appears in `[REPO_ROOT]/.skill-update-triggers/`. When detected,
invokes the skill-effectiveness-evaluator apply step by launching
it as a background process.

**Non-blocking.** Never prevents a file edit from completing.

```python
# .cursor/hooks/scripts/skill_update_trigger_watcher.py

import sys
import json
import subprocess
from pathlib import Path
from hooks_utils import find_repo_root, permit

def main():
    try:
        repo_root = find_repo_root()
    except RuntimeError:
        permit()
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    file_path = event_input.get("file_path", "")
    triggers_dir = repo_root / ".skill-update-triggers"

    # Only care about new files in the triggers directory
    if not file_path or str(triggers_dir) not in file_path:
        permit()
        return

    trigger_file = Path(file_path)
    if not trigger_file.exists() or not trigger_file.suffix == ".json":
        permit()
        return

    # Launch the apply step as a background process
    # The apply script reads the trigger file and handles the rest
    apply_script = repo_root / ".cursor" / "hooks" / "scripts" / "apply_skill_update.py"
    if apply_script.exists():
        subprocess.Popen(
            ["python", str(apply_script), str(trigger_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

    permit()

if __name__ == "__main__":
    main()
```

---

## Script 11: `manifest_step_writer.py`

**Purpose:** Non-blocking hook that detects phase step artifact writes and
updates `stepStatus`, `stepTimestamps`, and `currentStep` in the session
manifest in real time. This provides cross-phase visibility in Sprint mode —
all worktrees share the same `.sage/` directory, so manifest updates are
instantly visible without git operations.

Also detects batch review documents (`phase-{N}-batch-{M}-review.md`) in
Checkpoint mode and emits `batch_completed` telemetry events with duration.

**Events:** `afterFileEdit`
**Blocking:** No

**Detection logic:** When a file is written whose name matches
`phase-N-[artifact-suffix]`, the hook maps the suffix to a step and
updates the manifest:

| Artifact suffix | Step completed | Auto-advances to |
|---|---|---|
| `dev-interview-summary.md` | dev-interview | implementation-plan |
| `implementation-plan.md` | implementation-plan | traceability-review |
| `traceability-review.md` | traceability-review | plan-validation |
| `plan-preview.canvas.tsx` / `plan-preview.md` / `calculation-proof.md` | plan-validation | (no auto-advance — requires `validationConfirmed`) |
| `red-results.md` | (sub-step only) | Sets `buildSubStep = "green-refactor"` |
| `tdd-results.md` | build | code-review |
| `code-review.md` | code-review | security-review |
| `security-review.md` | security-review | agent-testing |
| `test-results.md` | agent-testing | completion-report |
| `completion-report.md` | completion-report | complete (sets `completedAt`) |

**Batch review detection:** When a file matches `phase-{N}-batch-{M}-review.md`:
- Reads the batch's `startedAt` from the manifest to calculate duration
- Updates `batches[M].completedAt` in the manifest
- Emits a `batch_completed` telemetry event with `batchId`, `batchLabel`,
  `testsPassing`, and `durationMinutes`

For each step transition, the hook writes (via `write_manifest_fields()`):
- `stepStatus.[completed_step] = "complete"`
- `stepTimestamps.[completed_step].completedAt = now`
- `currentStep = [next_step]`
- `stepStatus.[next_step] = "in-progress"`
- `stepTimestamps.[next_step].startedAt = now`

Uses `write_manifest_fields()` from `hooks_utils.py` for locked batch
manifest updates. Silently no-ops on any failure.

**Artifact location requirement:** Step artifacts MUST be written to
`.sage/sessions/[session-id]/phase-N/` with the naming convention
`phase-{N}-{artifact-suffix}` (e.g. `phase-2-dev-interview-summary.md`).
Artifacts written to any other location (e.g. `docs/cursor/...` or a
different session directory) will not trigger manifest updates. If a
phase completes outside the SAGE artifact pipeline, the
`linear-status-sync` hook (Script 13) provides a safety net by syncing
the Linear Done status back to the manifest.

---

## Script 12: `sage_state_sync.py`

**Purpose:** Non-blocking hook that pushes `.sage/` session state to
the parent feature branch after any session file is written (manifest,
telemetry, or phase artifacts). Provides cross-machine phase visibility
in Sprint mode without requiring developers to manually commit and push
session state.

**Event:** `afterFileEdit`
**Blocking:** No
**Timeout:** 15000 ms

Uses git plumbing commands (hash-object, read-tree, update-index,
write-tree, commit-tree) with an alternate index file to create a commit
on the parent branch without touching the developer's working tree or
index.

Manifest sync uses per-phase merge: the remote manifest's runtime for
other phases is preserved; only the current phase's runtime is taken
from local. Telemetry sync uses append-only union: remote lines are
kept, and only locally-new lines are appended.

Retries on push conflicts (up to 3 retries). Silently no-ops on any
failure.

---

## Script 13: `linear_status_sync.py`

**Purpose:** Non-blocking hook that polls Linear for phase issue status
changes and syncs `linearIssueStatus` (and `assignedDeveloper`) back to
the session manifest. Closes the gap where Linear status diverges from
the manifest after kick-off.

**Event:** `afterFileEdit`
**Blocking:** No
**Timeout:** 5000 ms

### Trigger and debounce

Fires on every `afterFileEdit` event but debounces using a cursor file
(`linear-sync-cursor.txt` in the session directory). Skips the poll if
the last successful poll was within the configurable interval (default
60 seconds, from `workflow-config.json` field `linearSync.pollIntervalSeconds`).

### Authentication

Uses the `LINEAR_API_KEY` environment variable (same key used by
`skill_update_poller.py` and the Linear MCP server). Silently exits if
the key is not set.

### Logic

1. Read the session manifest and collect all `phases[N].definition.linearIssueId`
   identifiers.
2. Query Linear GraphQL API in a single batch request for all phase issues.
3. For each phase, compare Linear status against `phases[N].runtime.linearIssueStatus`:
   - If different, update `linearIssueStatus` via `write_manifest_fields()`.
   - If Linear assignee differs from `definition.assignedDeveloper`, update it.
4. If `linearSync.autoCompleteManifestOnDone` is `true` and Linear status is
   `Done` but manifest `currentStep` is not `done`/`complete`:
   - Set `currentStep` to `done` and all `stepStatus` entries to `complete`.
   - Set `completedAt` from the Linear issue's `completedAt`.
   - Emit a `linear_status_sync` telemetry event with `autoCompleted: true`.

### GraphQL query

```graphql
query PhaseStatusSync($identifiers: [String!]!) {
  issues(filter: { identifier: { in: $identifiers } }) {
    nodes {
      identifier
      state { name }
      assignee { name }
      completedAt
      startedAt
    }
  }
}
```

### Manifest fields written

| Field path | Condition |
|---|---|
| `phases[N].runtime.linearIssueStatus` | Linear status differs from manifest |
| `phases[N].definition.assignedDeveloper` | Linear assignee differs from manifest |
| `phases[N].runtime.currentStep` | Linear status is Done + autoComplete enabled |
| `phases[N].runtime.stepStatus[*]` | Linear status is Done + autoComplete enabled |
| `phases[N].runtime.completedAt` | Linear status is Done + autoComplete enabled |
| `phases[N].runtime.startedAt` | Linear startedAt present + manifest startedAt null |

### Failure mode

Silently no-ops on any failure (network, auth, parse, write). All errors
are swallowed — this hook must never block agent work or corrupt the manifest.

---

## Shared utilities additions

The following functions were added to `hooks_utils.py` to support
manifest writing:

### `write_manifest_field(session_root, field_path, value)`

Locked read-modify-write of a single field using dot notation
(e.g. `"phases.1.runtime.currentStep"`). Uses `filelock` package.
Updates `header.lastUpdatedAt`. Silently no-ops on failure.

### `write_manifest_fields(session_root, updates)`

Locked batch update of multiple fields in a single lock acquisition.
`updates` is `{field_path: value}`. More efficient than multiple
single-field calls.

### `increment_rejection_count(session_root, phase_id)`

Increments `phases[phase_id].runtime.hookRejectionCount` by 1.
Called automatically by `block()` when `phase_id` is provided.

### `_replace_manifest_json(manifest_path, manifest)`

Internal helper. Replaces the ````json ... ```` block inside
`session-manifest.md` with the serialised dict. Preserves all
content outside the block.

### gate_evaluated event

Emitted by gates on their primary permit path (condition satisfied) via
`permit_with_telemetry()` in `hooks_utils.py`. Not emitted on early exits
(wrong tool, wrong step, no session).

| Field | Value |
|---|---|
| `event` | `"gate_evaluated"` |
| `hook` | The hook ID (e.g. `"validation-confirmed-gate"`) |
| `phaseId` | Current phase ID or null |
| `result` | `"permit"` |

---

## Directory structure

```
phase-N/
├── telemetry.jsonl
├── phase-N-dev-interview-summary.md     — build mode recorded here
├── phase-N-implementation-plan.md       — batch breakdown here (checkpoint mode)
├── phase-N-traceability-review.md
├── phase-N-batch-1-review.md            — checkpoint mode only, one per batch
├── phase-N-batch-2-review.md
├── phase-N-batch-3-review.md
├── phase-N-red-results.md               — S5a RED test confirmation (STATUS: RED CONFIRMED)
├── phase-N-tdd-results.md               — S5b GREEN-REFACTOR results (STATUS: PASS)
├── phase-N-code-review.md
├── phase-N-test-results.md
├── phase-N-completion-report.md
└── phase-N-handoff.md
```

### Checkpoint batch review format (`phase-N-batch-M-review.md`)

Written by the build agent at the end of each batch in checkpoint mode,
before pausing for developer confirmation.

```markdown
# Phase N — Batch M Review
# [batch label]
# Written: [ISO datetime]

## What was built

### Files changed
- [filename]: [what changed — new methods, modified logic]
- ...

### Methods / functions added
- [class or file]: [method name] — [one-line purpose]
- ...

## Batch test results

Tests run: [N]
Passing:   [N]
Failing:   [0 — must be 0 before this review is written]

[Test names and pass/fail status]

## Deviations from implementation plan

[None — if none]
[Or: description of any deviation and why it was made]

## Ready for your review

All [N] batch tests are passing.

To proceed to the next batch:
Set phases.[N].runtime.batches[[M-1]].confirmed = true
in the session manifest: [SESSION_ROOT]/session-manifest.md

The batch_confirmation_gate.py hook will block the next batch
until this field is set.
```
        ├── hooks_utils.py                    ← shared utilities (NoSessionError, SessionIntegrityError, find_marker_value, has_status_marker)
        ├── telemetry_logger.py               ← logging (non-blocking)
        ├── prd_telemetry_append.py           ← PRD interview telemetry helper
        ├── plan_mode_enforcer.py             ← S1 Plan mode gate (allows dev-interview summary write)
        ├── manifest_step_gate.py             ← S2-S8 step progression (anchored blocker parsing)
        ├── required_references_gate.py       ← S5 reference files gate
        ├── validation_confirmed_gate.py      ← S5 validation gate
        ├── phase_approval_gate.py            ← S1 Linear approval gate
        ├── foundation_verified_gate.py       ← S5 foundation gate (Dependent phases)
        ├── batch_confirmation_gate.py        ← S5 checkpoint batch gate
        ├── protected_manifest_fields_gate.py ← protected field guard (validationConfirmed, batches[*].confirmed, foundationVerified)
        ├── red_results_gate.py               ← S5b production write gate (requires STATUS: RED CONFIRMED)
        ├── completion_report_stop_gate.py    ← S8 stop hook (hardest gate)
        ├── tdd_results_gate.py               ← S6 TDD results gate (anchored status parsing)
        ├── code_review_gate.py               ← S7 code review gate (anchored finding parsing)
        ├── manifest_step_writer.py           ← step transition writer (non-blocking, real-time manifest updates)
        └── skill_update_trigger_watcher.py   ← skill update watcher (notification-only, no git ops)

.sage/
├── sessions/
│   ├── active-session.txt                    ← current SESSION_ROOT path
│   └── [feature-id]/                         ← SESSION_ROOT
│       ├── session-manifest.md
│       ├── phase-breakdown.md
│       ├── kickoff-dev-review-log.md
│       ├── phase-1/
│       │   ├── telemetry.jsonl               ← phase lane telemetry
│       │   ├── phase-1-dev-interview-summary.md
│       │   ├── phase-1-implementation-plan.md
│       │   ├── phase-1-traceability-review.md
│       │   ├── phase-1-tdd-results.md
│       │   ├── phase-1-code-review.md
│       │   ├── phase-1-test-results.md
│       │   ├── phase-1-completion-report.md
│       │   └── phase-1-handoff.md
│       └── phase-N/
│           └── ...
└── current-phase.txt                         ← active phase ID
    skill-update-history.jsonl                ← skill update audit trail

.skill-update-triggers/                       ← webhook trigger files land here
└── LIN-[id].json
```

---

## Linear issue metadata block

Linear does not support arbitrary custom properties. The following
fields are written as a structured YAML block at the top of the
issue description when the issue is created. Agents and skills
read these values via the Linear MCP description field.

**Format:**

```
---
sage_metadata:
  worktree_path: C:\Sage\worktrees\LIN-4821\phase-1\
  diff_path: .skill-update-staging/LIN-512.diff
  evaluation_cycle: 3
---
```

**Field usage:**

| Field | Written by | Read by | Applies to |
|---|---|---|---|
| `worktree_path` | `phase-splitter` skill | orchestrator, sprint-coordinator | Sprint and Pair phase issues |
| `diff_path` | `skill-effectiveness-evaluator` | `skill-update-trigger-watcher` hook | Skill update issues only |
| `evaluation_cycle` | `skill-effectiveness-evaluator` | `skill-effectiveness-evaluator` (apply step) | Skill update issues only |

Fields that do not apply to a given issue type are omitted from the
block entirely. A Solo phase issue, for example, carries no
`sage_metadata` block at all.

---

## Session manifest machine-readable block

Every hook reads the manifest's embedded JSON block. It must follow
this schema. The manifest generator at kick-off is responsible for
writing this block correctly.

```json
{
  "sessionId": "LIN-4821",
  "featureTitle": "Expense Allocation Re-design",
  "mode": "sprint",
  "phases": {
    "1": {
      "linearIssueId": "LIN-4822",
      "currentStep": "dev-interview",
      "validation_confirmed": false,
      "required_references": [
        "mockups/allocation-rules.html",
        "mockups/allocation-results.html"
      ],
      "stepStatus": {
        "dev-interview": "pending",
        "implementation-plan": "pending",
        "traceability-review": "pending",
        "plan-validation": "pending",
        "build": "pending",
        "code-review": "pending",
        "agent-testing": "pending",
        "completion-report": "pending"
      }
    },
    "2": {
      "linearIssueId": "LIN-4823",
      "currentStep": "dev-interview",
      "validation_confirmed": false,
      "required_references": [
        "mockups/allocation-results.html"
      ],
      "stepStatus": { "...": "pending" }
    }
  }
}
```

---

## PRD and kickoff telemetry (optional helper)

PRD and kickoff lifecycle lines are **not** emitted by `telemetry_logger.py`. They go to the append-only file configured under **`prd.telemetryFile`** in `.sage/workflow-config.json` (default: `.sage/prd-interview-telemetry.jsonl`).

**Script:** `prd_telemetry_append.py` (same `hooks-spec/scripts/` catalogue as other hook utilities; product repos mirror into `.cursor/hooks/scripts/`).

**Behaviour:** Resolve repo root, read `prd.telemetryFile`, append one minified JSON line. Adds `timestamp` if missing. **Never raises** — failures exit 0 (same spirit as `telemetry_logger.py`).

**Invocation:** `python prd_telemetry_append.py '<json-object>'` or pipe JSON on stdin. Used by **`prd-interviewer`**, **`prd-completeness-check`**, **`kickoff-dev-review`**, and **`phase-splitter`** skill instructions.

### Event catalogue

All events include `timestamp`, `event`, `workflowKind`, and `linearIssueId`.

**PRD interview events** (`workflowKind: "prd_interview"`):

| Event | Emitted by | Key fields |
|---|---|---|
| `prd_preflight` | prd-interviewer | `preflightOutcome`, `override`, `overrideReason` |
| `prd_investigation_manifest` | prd-interviewer | Investigation details (internal) |
| `prd_complexity_classified` | prd-interviewer | `tier`, `expectedDuration` |
| `prd_phase_started` | prd-interviewer | `phaseId` (`P1`–`P9`), `prdRunId` |
| `prd_phase_completed` | prd-interviewer | `phaseId`, `prdRunId` |
| `prd_interview_completed` | prd-interviewer | `prdRunId`, `parkedCount` |

**Completeness check events** (`workflowKind: "completeness_check"`):

| Event | Emitted by | Key fields |
|---|---|---|
| `completeness_check_started` | prd-completeness-check | `prdRunId`, `prdPath` |
| `completeness_check_completed` | prd-completeness-check | `prdRunId`, `score`, `passThreshold`, `passed`, `dimensionScores` (`D1`–`D6`), `findingCount`, `linearStatusSet` |

**Kickoff dev review events** (`workflowKind: "kickoff_dev_review"`):

| Event | Emitted by | Key fields |
|---|---|---|
| `kickoff_dev_review_started` | kickoff-dev-review | `transcriptDurationSeconds`, `participantCount` |
| `kickoff_dev_review_completed` | kickoff-dev-review | `concernCount`, `concernsByCategory`, `prdUpdatesApplied`, `reScoreResult` |

**Phase splitter events** (`workflowKind: "phase_splitter"`):

| Event | Emitted by | Key fields |
|---|---|---|
| `phase_splitter_started` | phase-splitter | `mode` |
| `phase_splitter_phases_proposed` | phase-splitter | `phaseCount`, `phases` (array) |
| `phase_splitter_completed` | phase-splitter | `sessionId`, `phaseCount`, `manifestPath`, `worktreesCreated`, `linearIssuesCreated` |

### Workflow telemetry bootstrap

The phase-splitter also writes a `session_created` event directly to `[SESSION_ROOT]/workflow-telemetry.jsonl` after creating the session manifest and `active-session.txt`. This bootstraps the file so the telemetry-logger hook and the orchestrator's TDD spec generation telemetry have a target from their first tool call.

### TDD spec generation events (workflow-telemetry.jsonl)

These are written by the orchestrator agent directly to `[SESSION_ROOT]/workflow-telemetry.jsonl` using `hooks_utils.write_telemetry_event()`:

| Event | Emitted by | Key fields |
|---|---|---|
| `session_created` | phase-splitter | `sessionId`, `featureId`, `mode`, `phaseCount` |
| `tdd_spec_generation_started` | orchestrator | `sessionId`, `phaseId`, `phaseLane` |
| `tdd_spec_generation_completed` | orchestrator | `sessionId`, `phaseId`, `phaseLane`, `scenarioCount`, `tddSpecPath` |
| `tdd_specs_all_complete` | orchestrator | `sessionId`, `phaseCount`, `totalScenarioCount` |

See also `reference-docs/prd-interview-runbook.md` in sage-framework.
