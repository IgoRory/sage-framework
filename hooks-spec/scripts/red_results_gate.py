"""
red_results_gate.py
SAGE Framework — Hook: red-results-gate
Event: preToolUse
Blocking: True

Blocks S5b production writes until phase-{N}-red-results.md exists in the
phase directory AND contains 'STATUS: RED CONFIRMED' on its own line.

This enforces the TDD discipline: all tests must be written and confirmed
failing (RED) before any production code (GREEN) can be written.

The file is written by the test-author agent during S5a.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit, write_telemetry_event,
    has_status_marker, NoSessionError, SessionIntegrityError
)

PRODUCTION_WRITE_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit"
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

    tool_name = event_input.get("tool_name", "").lower().replace("-", "_")
    if tool_name not in PRODUCTION_WRITE_TOOLS:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")
    build_sub_step = runtime.get("buildSubStep", "")

    if current_step != "build" or build_sub_step != "green-refactor":
        permit()
        return

    # Allow writes to test files (test-author may still be adjusting)
    tool_input = event_input.get("tool_input", {})
    target_path = tool_input.get("path") or tool_input.get("file_path") or tool_input.get("file") or ""
    test_indicators = (".spec.", ".test.", ".Tests.", "_test.", "test_")
    if any(indicator in target_path for indicator in test_indicators):
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    red_results_filename = f"phase-{phase_id}-red-results.md"
    red_results_path = phase_dir / red_results_filename

    if not red_results_path.exists():
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "red-results-gate",
            "phaseId": phase_id,
            "reason": f"{red_results_filename} not found"
        })
        block(
            message=(
                f"RED RESULTS GATE — Production writes blocked for phase {phase_id}.\n\n"
                f"{red_results_filename} not found in the phase directory:\n"
                f"  {phase_dir}\n\n"
                f"The test-author agent must complete all RED tests (S5a) and write\n"
                f"{red_results_filename} with 'STATUS: RED CONFIRMED' before production\n"
                f"code can be written."
            ),
            phase_id=phase_id
        )
        return

    content = red_results_path.read_text(encoding="utf-8")
    if not has_status_marker(content, "STATUS: RED CONFIRMED"):
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "red-results-gate",
            "phaseId": phase_id,
            "reason": f"{red_results_filename} does not contain STATUS: RED CONFIRMED"
        })
        block(
            message=(
                f"RED RESULTS GATE — Production writes blocked for phase {phase_id}.\n\n"
                f"{red_results_filename} exists but does not contain 'STATUS: RED CONFIRMED'.\n"
                f"  {red_results_path}\n\n"
                f"All RED tests must be confirmed failing before production code\n"
                f"can be written. Complete S5a first."
            ),
            phase_id=phase_id
        )
        return

    permit()


if __name__ == "__main__":
    main()
