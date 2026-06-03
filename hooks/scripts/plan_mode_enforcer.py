"""
plan_mode_enforcer.py
SAGE Framework — Hook: plan-mode-enforcer
Event: preToolUse
Blocking: True

Blocks file-write tool calls during S1 dev-interview, except for the
agent's declared output artifact (phase-{N}-dev-interview-summary.md).

Permits immediately if:
- No active session exists (workflow not initialised)
- No SAGE_PHASE_ID set (not in a phase context)
- currentStep is not 'dev-interview'
- The tool call is not a file-write operation
- The write target is phase-{N}-dev-interview-summary.md in the phase directory
"""

import sys
import json
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, get_phase_dir, block, permit,
    write_telemetry_event, NoSessionError, SessionIntegrityError
)

# Tool names that constitute file-write operations
WRITE_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "overwrite_file",
    "insert_content", "delete_content", "patch_file"
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

    # Read tool call from stdin
    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    # Only check file-write tool calls
    tool_name = event_input.get("tool_name", "").lower().replace("-", "_")
    if tool_name not in WRITE_TOOLS:
        permit()
        return

    # Check current step in manifest
    runtime = read_phase_runtime(session_root, phase_id)
    current_step = runtime.get("currentStep", "")

    if current_step != "dev-interview":
        permit()
        return

    # Allow the dev-interview agent to write its declared output artifact
    tool_input = event_input.get("tool_input", {})
    target_path = tool_input.get("path") or tool_input.get("file_path") or tool_input.get("file") or ""
    if target_path:
        target = Path(target_path)
        allowed_artifact = get_phase_dir(session_root, phase_id) / f"phase-{phase_id}-dev-interview-summary.md"
        try:
            if target.resolve() == allowed_artifact.resolve():
                permit()
                return
        except (OSError, ValueError):
            pass

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "plan-mode-enforcer",
        "phaseId": phase_id,
        "toolName": tool_name,
        "reason": "File write blocked during S1 dev interview (Plan mode enforced)"
    })

    block(
        message=(
            "PLAN MODE — File writes are blocked during S1 Dev Interview.\n\n"
            "The dev-interview agent may only write phase-{N}-dev-interview-summary.md\n"
            "to the phase directory. All other file writes are blocked.\n\n"
            "To proceed: finish the dev interview, write the summary, then update\n"
            "currentStep to 'implementation-plan' in the session manifest."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
