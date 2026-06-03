"""
validation_confirmed_gate.py
SAGE Framework — Hook: validation-confirmed-gate
Event: preToolUse
Blocking: True

Blocks S5 build from starting until the developer has manually set
validationConfirmed = true in the session manifest for this phase.

This flag CANNOT be set by any agent or hook. It is the developer's
explicit acknowledgement that the S4 validation mockup is acceptable
and the implementation plan is approved to proceed to code.

The plan-preview-generator agent produces the preview artifact; only the
developer confirms it by editing the session manifest directly.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, get_phase_dir, block, permit,
    write_telemetry_event, is_write_tool, is_shell_tool,
    NoSessionError, SessionIntegrityError
)


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

    if not (is_write_tool(event_input) or is_shell_tool(event_input)):
        permit()
        return

    runtime = read_phase_runtime(session_root, phase_id)
    current_step = runtime.get("currentStep", "")

    if current_step != "build":
        permit()
        return

    validation_confirmed = runtime.get("validationConfirmed", False)
    if validation_confirmed is True:
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "validation-confirmed-gate",
        "phaseId": phase_id,
        "validationConfirmed": validation_confirmed,
        "reason": "Developer has not confirmed plan validation"
    })

    phase_manifest_path = get_phase_dir(session_root, phase_id) / "phase-manifest.json"
    block(
        message=(
            f"VALIDATION GATE — Build blocked for phase {phase_id}.\n\n"
            f"The implementation plan has not been validated by the developer.\n\n"
            f"To unblock:\n"
            f"  1. Review the validation mockup in the phase directory\n"
            f"  2. Open: {phase_manifest_path}\n"
            f"  3. Set validationConfirmed = true in the JSON\n\n"
            f"This flag cannot be set by the agent. It requires your explicit confirmation."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
