"""
foundation_verified_gate.py
SAGE Framework — Hook: foundation-verified-gate
Event: preToolUse
Blocking: True

Blocks Dependent phase lanes from entering S5 (build) until the
session manifest field foundationVerified = true.

This flag is set by the orchestrator after:
  - All Foundation phases have merged to main
  - All Independent phases have merged to main
  - Post-merge regression tests have passed

Dependent phases can freely progress through S1–S4 in parallel
with Foundation/Independent phases. The gate only applies at S5.

Phase type (Foundation / Independent / Dependent) is read from
phases[N].definition.phaseType in the session manifest.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit, write_telemetry_event,
    NoSessionError, SessionIntegrityError
)

BUILD_INITIATING_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "run_build"
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
    if tool_name not in BUILD_INITIATING_TOOLS:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    if current_step != "build":
        permit()
        return

    definition = phase_data.get("definition", {})
    phase_type = definition.get("phaseType", "").lower()

    # Only applies to Dependent phases
    if phase_type != "dependent":
        permit()
        return

    # Check session-level foundationVerified flag
    session_state = manifest.get("sessionState", {})
    foundation_verified = session_state.get("foundationVerified", False)

    if foundation_verified is True:
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "foundation-verified-gate",
        "phaseId": phase_id,
        "phaseType": phase_type,
        "foundationVerified": foundation_verified,
        "reason": "Foundation phases not yet verified — Dependent phase S5 blocked"
    })

    block(
        message=(
            f"FOUNDATION GATE — Build blocked for Dependent phase {phase_id}.\n\n"
            f"Foundation and Independent phases must merge and pass regression\n"
            f"before this Dependent phase can begin implementation.\n\n"
            f"Current status: foundationVerified = false\n\n"
            f"Continue progressing through S1–S4 while waiting.\n"
            f"The orchestrator will set foundationVerified = true in the session\n"
            f"manifest once all upstream phases have merged and regression has passed."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
