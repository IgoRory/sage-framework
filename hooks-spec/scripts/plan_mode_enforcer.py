"""
plan_mode_enforcer.py
SAGE Framework — Hook: plan-mode-enforcer
Event: preToolUse
Blocking: True

Blocks all file-write tool calls while the session manifest currentStep
is 'dev-interview'. Enforces Plan mode structurally during S1 — the agent
cannot write files regardless of its instructions.

Permits immediately if:
- No active session exists (workflow not initialised)
- No SAGE_PHASE_ID set (not in a phase context)
- currentStep is not 'dev-interview'
- The tool call is not a file-write operation
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit,
    write_telemetry_event
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
    except RuntimeError:
        # No active session or missing manifest — not in workflow context
        permit()
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
    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    if current_step != "dev-interview":
        permit()
        return

    # Block the write
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
            "The dev-interview agent operates in read-only Plan mode.\n"
            "Complete the interview and produce phase-{N}-dev-interview-summary.md\n"
            "before the implementation-planner agent can write files.\n\n"
            "To proceed: finish the dev interview, then update currentStep to "
            "'implementation-plan' in the session manifest."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
