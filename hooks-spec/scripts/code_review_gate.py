"""
code_review_gate.py
SAGE Framework — Hook: code-review-gate
Event: preToolUse
Blocking: True

Blocks S7 (agent testing) from starting until the phase's code-review.md
exists in the phase directory AND contains 'Critical findings: 0'.

The code-review.md is written by the code-reviewer agent during S6.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit, write_telemetry_event,
    find_marker_value, NoSessionError, SessionIntegrityError
)

TESTING_INITIATING_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "execute_command", "run_build"
}

CODE_REVIEW_FILENAME = "phase-{N}-code-review.md"


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

    tool_name = event_input.get("tool_name", "").lower().replace("-", "_")
    if tool_name not in TESTING_INITIATING_TOOLS:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    if current_step != "agent-testing":
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    review_filename = CODE_REVIEW_FILENAME.replace("{N}", phase_id)
    review_path = phase_dir / review_filename

    if not review_path.exists():
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "code-review-gate",
            "phaseId": phase_id,
            "reason": f"{review_filename} not found"
        })
        block(
            message=(
                f"CODE REVIEW GATE — Agent testing blocked for phase {phase_id}.\n\n"
                f"{review_filename} not found in phase directory:\n"
                f"  {phase_dir}\n\n"
                f"The code-reviewer agent must complete S6 and produce a code review\n"
                f"document before agent testing can begin."
            ),
            phase_id=phase_id
        )

    content = review_path.read_text(encoding="utf-8")
    if find_marker_value(content, "Critical findings") != 0:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "code-review-gate",
            "phaseId": phase_id,
            "reason": "Code review has Critical findings > 0"
        })
        block(
            message=(
                f"CODE REVIEW GATE — Agent testing blocked for phase {phase_id}.\n\n"
                f"Code review contains Critical findings that must be resolved.\n"
                f"  {review_path}\n\n"
                f"Required: 'Critical findings: 0' in the code review document.\n"
                f"Address all Critical findings in S5/S6 before proceeding to S7."
            ),
            phase_id=phase_id
        )

    permit()


if __name__ == "__main__":
    main()
