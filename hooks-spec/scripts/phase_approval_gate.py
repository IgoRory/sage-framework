"""
phase_approval_gate.py
SAGE Framework — Hook: phase-approval-gate
Event: preToolUse
Blocking: True

Blocks S1 (dev-interview) from starting until the phase's Linear issue
status is 'Approved'. The approval is set by the Product Manager and Lead Dev
in Linear — it cannot be auto-set by any agent or hook.

Reads the linearIssueStatus from the session manifest runtime block.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit, write_telemetry_event,
    NoSessionError, SessionIntegrityError
)

APPROVED_STATUSES = {"Approved", "Foundation Verified", "In Progress", "Build Complete", "Done"}

# Only gate on tools that would initiate S1 work
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

    # Only applies at the very start of S1
    if current_step != "dev-interview":
        permit()
        return

    # Check approval status
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
