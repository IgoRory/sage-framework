"""
security_review_gate.py
SAGE Framework — Hook: security-review-gate
Event: preToolUse
Blocking: True

Blocks S7 (agent testing) from starting until the phase's security review exists
in the phase directory and contains 'Critical findings: 0'.

The security review is written by the security-reviewer agent during S6.5.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, get_phase_dir, block, permit,
    write_telemetry_event, is_write_tool, is_shell_tool,
    find_marker_value, NoSessionError, SessionIntegrityError, run_gate
)

SECURITY_REVIEW_FILENAME = "phase-{N}-security-review.md"


def security_review_enabled(manifest: dict) -> bool:
    """Return True when the configured SAGE step sequence includes S6.5."""
    configured_steps = manifest.get("phases", {}).get("stepSequence")
    if isinstance(configured_steps, list):
        return "security-review" in configured_steps

    # Session manifests may not embed workflow-config. Current SAGE config enables
    # security review, so fail closed unless the manifest explicitly says otherwise.
    return True


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

    if not phase_id or not security_review_enabled(manifest):
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

    if current_step != "agent-testing":
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    review_filename = SECURITY_REVIEW_FILENAME.replace("{N}", phase_id)
    review_path = phase_dir / review_filename

    if not review_path.exists():
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "security-review-gate",
            "phaseId": phase_id,
            "reason": f"{review_filename} not found"
        })
        block(
            message=(
                f"SECURITY REVIEW GATE — Agent testing blocked for phase {phase_id}.\n\n"
                f"{review_filename} not found in phase directory:\n"
                f"  {phase_dir}\n\n"
                f"The security-reviewer agent must complete S6.5 and produce a security review\n"
                f"document before agent testing can begin."
            ),
            phase_id=phase_id
        )

    content = review_path.read_text(encoding="utf-8")
    if find_marker_value(content, "Critical findings") != 0:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "security-review-gate",
            "phaseId": phase_id,
            "reason": "Security review has Critical findings > 0"
        })
        block(
            message=(
                f"SECURITY REVIEW GATE — Agent testing blocked for phase {phase_id}.\n\n"
                f"Security review contains Critical findings that must be resolved.\n"
                f"  {review_path}\n\n"
                f"Required: 'Critical findings: 0' in the security review document.\n"
                f"Address all Critical findings before proceeding to S7."
            ),
            phase_id=phase_id
        )

    permit()


if __name__ == "__main__":
    run_gate(main)
