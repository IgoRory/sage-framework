"""
completion_report_stop_gate.py
SAGE Framework — Hook: completion-report-stop-gate
Event: stop
Blocking: True

Fires when the agent tries to end its turn (stop event).
Blocks the agent from ending its turn until:
  - phase-{N}-test-results.md exists in the phase directory
  - AND contains 'STATUS: PASS'

This ensures the agent cannot declare completion without confirmed
passing test results. The stop event fires every time the agent
would naturally end — the gate keeps it active until tests pass.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit, write_telemetry_event
)

TEST_RESULTS_FILENAME = "phase-{N}-test-results.md"
PASS_MARKER = "STATUS: PASS"


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        # No active session — not in workflow context, allow stop
        permit()
        return

    if not phase_id:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    # Only enforce at S8 completion-report step
    if current_step != "completion-report":
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    results_filename = TEST_RESULTS_FILENAME.replace("{N}", phase_id)
    results_path = phase_dir / results_filename

    if not results_path.exists():
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "completion-report-stop-gate",
            "phaseId": phase_id,
            "reason": "test-results.md not found — cannot mark phase complete"
        })
        block(
            message=(
                f"COMPLETION GATE — Phase {phase_id} cannot be marked complete.\n\n"
                f"{results_filename} not found in phase directory:\n"
                f"  {phase_dir}\n\n"
                f"The agent-testing step (S7) must produce passing test results\n"
                f"before the completion report (S8) can be finalised.\n\n"
                f"Complete S7 agent testing first."
            ),
            phase_id=phase_id
        )

    content = results_path.read_text(encoding="utf-8")
    if PASS_MARKER not in content:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "completion-report-stop-gate",
            "phaseId": phase_id,
            "reason": "test-results.md does not contain STATUS: PASS"
        })
        block(
            message=(
                f"COMPLETION GATE — Phase {phase_id} cannot be marked complete.\n\n"
                f"Test results do not show STATUS: PASS.\n"
                f"  {results_path}\n\n"
                f"All tests must pass before the completion report is finalised.\n"
                f"Fix failing tests in S7 before declaring this phase complete."
            ),
            phase_id=phase_id
        )

    permit()


if __name__ == "__main__":
    main()
