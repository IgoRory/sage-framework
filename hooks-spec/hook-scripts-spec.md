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

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def find_repo_root() -> Path:
    """
    Walk up from cwd until a directory containing .git is found.
    Raises RuntimeError if no .git directory is found within 10 levels.
    """
    current = Path.cwd()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise RuntimeError(
        "HOOK ERROR: Could not locate .git directory. "
        "Are you running inside a git repository?"
    )


def get_session_root(repo_root: Path) -> Path:
    """
    Read the active session root path from
    [REPO_ROOT]/.sage/sessions/active-session.txt.
    Raises RuntimeError if the file does not exist (no active session).
    """
    active_session_file = repo_root / ".sage" / "sessions" / "active-session.txt"
    if not active_session_file.exists():
        raise RuntimeError(
            "HOOK ERROR: No active session found. "
            "Expected file: .sage/sessions/active-session.txt\n"
            "Run the session initialiser at kick-off before starting phase work."
        )
    return Path(active_session_file.read_text(encoding="utf-8").strip())


def get_phase_id() -> str:
    """
    Read the current phase ID from the CURSOR_PHASE environment variable.
    Set by Cursor when launching a phase chat from the session manifest.
    Falls back to reading from .sage/current-phase.txt if env var not set.
    """
    phase = os.environ.get("CURSOR_PHASE")
    if phase:
        return phase
    repo_root = find_repo_root()
    phase_file = repo_root / ".sage" / "current-phase.txt"
    if phase_file.exists():
        return phase_file.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "HOOK ERROR: Cannot determine current phase. "
        "CURSOR_PHASE environment variable not set and "
        ".sage/current-phase.txt does not exist."
    )


def read_manifest(session_root: Path) -> dict:
    """
    Read and parse session-manifest.md as structured data.
    The manifest uses a defined YAML-like header block for machine-readable
    fields, followed by human-readable content.
    Returns the parsed header dict.
    """
    manifest_path = session_root / "session-manifest.md"
    if not manifest_path.exists():
        raise RuntimeError(
            f"HOOK ERROR: Session manifest not found at {manifest_path}.\n"
            "The manifest must be created at kick-off before phase work begins."
        )
    # Parse the machine-readable JSON block embedded in the manifest
    # (delimited by ```json ... ``` at the top of the file)
    content = manifest_path.read_text(encoding="utf-8")
    import re
    match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise RuntimeError(
            "HOOK ERROR: Session manifest does not contain a valid JSON "
            "machine-readable block. Re-generate the manifest at kick-off."
        )
    return json.loads(match.group(1))


def get_phase_dir(session_root: Path, phase_id: str) -> Path:
    """Return the phase directory path for a given phase ID."""
    return session_root / f"phase-{phase_id}"


def get_telemetry_path(session_root: Path, phase_id: str) -> Path:
    """Return the telemetry file path for a phase lane."""
    return get_phase_dir(session_root, phase_id) / "telemetry.jsonl"


def write_telemetry_event(
    session_root: Path,
    phase_id: str,
    event_name: str,
    data: dict
) -> None:
    """
    Append a telemetry event record to the phase lane's telemetry.jsonl.
    Creates the file and directory if they do not exist.
    Never raises — telemetry write failures are logged to stderr only,
    and do not affect hook exit codes.
    """
    try:
        telemetry_path = get_telemetry_path(session_root, phase_id)
        telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "hook_event_name": event_name,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "phase": phase_id,
            "step": data.get("step", "unknown"),
            "active_agent": os.environ.get("CURSOR_AGENT", "unknown"),
            "conversation_id": os.environ.get("CURSOR_CONVERSATION_ID", "unknown"),
            **data
        }
        with open(telemetry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[telemetry] WARNING: Failed to write telemetry event: {e}",
              file=sys.stderr)


def block(message: str, telemetry_data: dict = None,
          session_root: Path = None, phase_id: str = None) -> None:
    """
    Block the hook with a clear error message and optionally write a
    hook_rejection telemetry event. Exits with code 1.
    """
    if session_root and phase_id and telemetry_data:
        write_telemetry_event(
            session_root, phase_id, "hook_rejection",
            {**telemetry_data, "rejection_message": message}
        )
    print(f"\n🔴 GATE BLOCKED\n{message}\n", file=sys.stderr)
    sys.exit(1)


def permit() -> None:
    """Permit the hook. Exits with code 0."""
    sys.exit(0)
```

---

## Script 1: `telemetry_logger.py`

**Purpose:** Logging only. Writes every hook event to the phase lane's
telemetry.jsonl. Never blocks. Runs alongside all other hooks.

```python
# .cursor/hooks/scripts/telemetry_logger.py

import sys
import os
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    write_telemetry_event, permit
)

def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
    except RuntimeError:
        # No active session — not in a phase chat. Do not log, do not block.
        permit()
        return

    # Read the event context passed by Cursor via stdin as JSON
    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        event_input = {}

    event_name = event_input.get("event", "unknown")
    step = os.environ.get("CURSOR_STEP", "unknown")

    # Build event-specific data fields
    data = {"step": step}

    if event_name == "preToolUse":
        data["tool_name"] = event_input.get("tool_name", "unknown")
        data["tool_input_summary"] = str(
            event_input.get("tool_input", {}))[:200]

    elif event_name in ("beforeShellExecution", "afterShellExecution"):
        data["command"] = event_input.get("command", "")[:300]
        if event_name == "afterShellExecution":
            data["exit_code"] = event_input.get("exit_code")
            data["stdout_summary"] = event_input.get("stdout", "")[:200]

    elif event_name == "afterFileEdit":
        data["file_path"] = event_input.get("file_path", "unknown")
        data["edit_type"] = event_input.get("edit_type", "unknown")

    elif event_name == "afterMCPExecution":
        data["mcp_tool"] = event_input.get("tool_name", "unknown")
        data["mcp_result_summary"] = str(
            event_input.get("result", {}))[:200]

    elif event_name == "stop":
        data["stop_reason"] = event_input.get("reason", "unknown")

    write_telemetry_event(session_root, phase_id, event_name, data)
    permit()


if __name__ == "__main__":
    main()
```

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
| validation-mockup tool (S4) | S3 traceability-review = complete, zero Blockers |
| code-review tool (S6) | S5 build = complete (tdd-results STATUS:PASS) |
| test-runner tool (S7) | S6 code-review = complete, zero Critical findings |
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
    "generate_validation_mockup": {
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
            f"1. Review the validation mockup generated in S4\n"
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

**Purpose:** Blocks phase launch (S1 dev interview) until the Linear
phase issue for this phase is at status "Approved". Reads Linear
via MCP. This is the gate enforced by async approvals in Phase 03.

**Only fires once** — when the dev-interview tool is first called.
After S1 is marked complete in the manifest, this gate does not
re-check Linear status.

**Note on mode:** The workflow mode (mob, sprint, pair, solo) is applied
to the Linear phase issue as a label from the `SAGE Workflow Mode` label
group (e.g. `mode:sprint`). This is set automatically by the
`phase-splitter` skill at kick-off. Hook scripts read mode from the
session manifest `mode` field — not from Linear.

```python
# .cursor/hooks/scripts/phase_approval_gate.py

import sys
import json
import subprocess
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit
)

def get_linear_issue_status(issue_id: str) -> str:
    """
    Query Linear for the current status of a phase issue.
    Uses the Linear MCP via a subprocess call to the Cursor MCP bridge.
    Returns the status string or raises on failure.
    """
    # The Linear MCP is called via the Cursor MCP bridge CLI
    # which is available as a local command in the Cursor environment
    result = subprocess.run(
        ["cursor-mcp", "linear", "get-issue-status", "--id", issue_id],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to query Linear issue {issue_id}: {result.stderr}"
        )
    response = json.loads(result.stdout)
    return response.get("status", "unknown")


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
    if "dev_interview" not in tool_name and "dev-interview" not in tool_name:
        permit()
        return

    # If S1 is already complete, no need to re-check
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    step_status = phase_data.get("stepStatus", {})
    if step_status.get("dev-interview") == "complete":
        permit()
        return

    # Get Linear issue ID from manifest
    linear_issue_id = phase_data.get("linearIssueId")
    if not linear_issue_id:
        block(
            message=(
                f"PHASE LAUNCH BLOCKED — No Linear issue ID\n"
                f"Phase {phase_id} has no linearIssueId in the session manifest.\n"
                f"Ensure Linear issues were created at kick-off and the manifest "
                f"was updated with the issue IDs."
            ),
            telemetry_data={
                "step": "dev-interview",
                "rejection_reason": "missing_linear_issue_id"
            },
            session_root=session_root,
            phase_id=phase_id
        )

    try:
        status = get_linear_issue_status(linear_issue_id)
    except Exception as e:
        block(
            message=(
                f"PHASE LAUNCH BLOCKED — Linear status check failed\n"
                f"Could not verify approval status for issue {linear_issue_id}.\n"
                f"Error: {e}\n\n"
                f"Resolve the Linear MCP connectivity issue and retry."
            ),
            telemetry_data={
                "step": "dev-interview",
                "rejection_reason": "linear_check_failed",
                "linear_issue_id": linear_issue_id
            },
            session_root=session_root,
            phase_id=phase_id
        )

    if status.lower() == "approved":
        permit()
        return

    block(
        message=(
            f"PHASE LAUNCH BLOCKED — Awaiting approval\n"
            f"Linear issue {linear_issue_id} is at status '{status}'.\n"
            f"Phase {phase_id} cannot begin until status is 'Approved'.\n\n"
            f"the Product Manager and Lead Dev must approve this phase in Linear before the "
            f"build sprint can start.\n"
            f"Current status: {status}\n"
            f"Required status: Approved"
        ),
        telemetry_data={
            "step": "dev-interview",
            "rejection_reason": "phase_not_approved",
            "linear_issue_id": linear_issue_id,
            "linear_status": status
        },
        session_root=session_root,
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

**Purpose:** Blocks the test-runner tool (S7) from launching unless
`phase-N-code-review.md` exists with zero open Critical findings.

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

**Only active during S5 AND when `buildMode = "checkpoint"`.**
In autonomous mode or any other step, permits immediately.

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
├── phase-N-tdd-results.md               — full suite after all batches complete
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
        ├── hooks_utils.py                    ← shared utilities
        ├── telemetry_logger.py               ← logging (non-blocking)
        ├── prd_telemetry_append.py           ← PRD interview telemetry helper
        ├── plan_mode_enforcer.py             ← S1 Plan mode gate
        ├── manifest_step_gate.py             ← S2-S8 step progression
        ├── required_references_gate.py       ← S5 reference files gate
        ├── validation_confirmed_gate.py      ← S5 validation gate
        ├── phase_approval_gate.py            ← S1 Linear approval gate
        ├── foundation_verified_gate.py       ← S5 foundation gate (Dependent phases)
        ├── batch_confirmation_gate.py        ← S5 checkpoint batch gate
        ├── completion_report_stop_gate.py    ← S8 stop hook (hardest gate)
        ├── tdd_results_gate.py               ← S6 TDD results gate
        ├── code_review_gate.py               ← S7 code review gate
        └── skill_update_trigger_watcher.py   ← skill update watcher

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
  diff_path: .sage/skill-update-staging/LIN-512-diff.md
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

## PRD interview telemetry (optional helper)

PRD lifecycle lines are **not** emitted by `telemetry_logger.py`. They go to the append-only file configured under **`prd.telemetryFile`** in `.sage/workflow-config.json` (default: `.sage/prd-interview-telemetry.jsonl`).

**Script:** `prd_telemetry_append.py` (same `hooks-spec/scripts/` catalogue as other hook utilities; product repos mirror into `.cursor/hooks/scripts/`).

**Behaviour:** Resolve repo root, read `prd.telemetryFile`, append one minified JSON line. Adds `timestamp` if missing. **Never raises** — failures exit 0 (same spirit as `telemetry_logger.py`).

**Invocation:** `python prd_telemetry_append.py '<json-object>'` or pipe JSON on stdin. Used by **`prd-interviewer`** instructions and optionally by agents manually.

See also `reference-docs/prd-interview-runbook.md` in sage-framework.
