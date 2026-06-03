"""
tdd_results_gate.py
SAGE Framework — Hook: tdd-results-gate
Event: preToolUse
Blocking: True

Blocks S6 (code review) from starting until the phase's
phase-{N}-tdd-results.md file exists in the phase directory AND contains
the line 'STATUS: PASS'.

The file is written by the test-runner agent after all TDD scenarios have
been executed during S5 build.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, get_phase_dir, block, permit,
    write_telemetry_event, is_write_tool,
    has_status_marker, NoSessionError, SessionIntegrityError
)

def tdd_results_filename(phase_id: str) -> str:
    return f"phase-{phase_id}-tdd-results.md"


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

    if not is_write_tool(event_input):
        permit()
        return

    runtime = read_phase_runtime(session_root, phase_id)
    current_step = runtime.get("currentStep", "")

    if current_step != "code-review":
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    filename = tdd_results_filename(phase_id)
    tdd_results_path = phase_dir / filename

    if not tdd_results_path.exists():
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "tdd-results-gate",
            "phaseId": phase_id,
            "reason": f"{filename} not found"
        })
        block(
            message=(
                f"TDD RESULTS GATE — Code review blocked for phase {phase_id}.\n\n"
                f"{filename} not found in the phase directory:\n"
                f"  {phase_dir}\n\n"
                f"The test-runner agent must complete all TDD scenarios and write\n"
                f"{filename} with 'STATUS: PASS' before code review can begin."
            ),
            phase_id=phase_id
        )

    content = tdd_results_path.read_text(encoding="utf-8")
    if not has_status_marker(content, "STATUS: PASS"):
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "tdd-results-gate",
            "phaseId": phase_id,
            "reason": f"{filename} does not contain STATUS: PASS"
        })
        block(
            message=(
                f"TDD RESULTS GATE — Code review blocked for phase {phase_id}.\n\n"
                f"{filename} exists but does not contain 'STATUS: PASS'.\n"
                f"  {tdd_results_path}\n\n"
                f"All TDD scenarios must pass before code review can proceed.\n"
                f"Fix failing tests in S5 before advancing."
            ),
            phase_id=phase_id
        )

    permit()


if __name__ == "__main__":
    main()
