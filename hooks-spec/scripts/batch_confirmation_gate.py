"""
batch_confirmation_gate.py
SAGE Framework — Hook: batch-confirmation-gate
Event: preToolUse
Blocking: True

In Checkpoint build mode only: blocks the next batch's build tool call
until the developer has set batches[currentBatchId].confirmed = true
in the session manifest.

Flow:
  1. Agent builds batch N tasks
  2. Agent runs batch N tests
  3. Agent writes phase-{N}-batch-{M}-review.md
  4. Agent pauses and tells developer to review + set confirmed = true
  5. This gate blocks the next build tool call until confirmed = true
  6. Developer sets confirmed = true in the manifest
  7. Gate passes — agent proceeds to batch N+1

confirmed = true CANNOT be set by the agent. Only the developer can set it.

Permits immediately in autonomous mode or any step other than 'build'.
"""

import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, block, permit, write_telemetry_event
)

BUILD_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "run_build", "execute_command"
}


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
        manifest = read_manifest(session_root)
    except RuntimeError:
        permit()
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
    if tool_name not in BUILD_TOOLS:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    if current_step != "build":
        permit()
        return

    build_mode = runtime.get("buildMode", "autonomous")
    if build_mode != "checkpoint":
        permit()
        return

    current_batch_id = runtime.get("currentBatchId")
    if current_batch_id is None:
        # No batch in progress yet — first batch is always permitted
        permit()
        return

    batches = runtime.get("batches", [])
    current_batch = next(
        (b for b in batches if b.get("id") == current_batch_id), None
    )

    if current_batch is None:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "batch-confirmation-gate",
            "phaseId": phase_id,
            "currentBatchId": current_batch_id,
            "reason": "Batch not found in manifest — configuration error"
        })
        block(
            message=(
                f"CHECKPOINT GATE — Configuration error for phase {phase_id}.\n\n"
                f"Batch {current_batch_id} referenced in currentBatchId but not found\n"
                f"in the batches array. Check the session manifest for consistency."
            ),
            phase_id=phase_id
        )

    if current_batch.get("confirmed", False) is True:
        permit()
        return

    manifest_path = session_root / "session-manifest.md"
    batch_label = current_batch.get("label", f"Batch {current_batch_id}")
    review_path = current_batch.get("reviewPath", f"phase-{phase_id}-batch-{current_batch_id}-review.md")

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "batch-confirmation-gate",
        "phaseId": phase_id,
        "batchId": current_batch_id,
        "batchLabel": batch_label,
        "reason": "Developer has not confirmed batch review"
    })

    block(
        message=(
            f"CHECKPOINT GATE — Next batch blocked for phase {phase_id}.\n\n"
            f"Current batch: {batch_label} (id: {current_batch_id})\n\n"
            f"Review the batch report before proceeding:\n"
            f"  {review_path}\n\n"
            f"To unblock:\n"
            f"  1. Review the batch review document and test results\n"
            f"  2. Open: {manifest_path}\n"
            f"  3. Set batches[{current_batch_id}].confirmed = true\n\n"
            f"This flag cannot be set by the agent."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
