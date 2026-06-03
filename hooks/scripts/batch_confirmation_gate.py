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

Also emits batch_started and batch_confirmed telemetry events using a
state file (.telemetry-batch-state.json) to prevent duplicate emissions
on repeated gate checks.

Permits immediately in autonomous mode or any step other than 'build'.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, block, permit, write_telemetry_event,
    is_write_tool, is_shell_tool,
    NoSessionError, SessionIntegrityError
)

try:
    from filelock import FileLock, Timeout as LockTimeout
except ImportError:
    FileLock = None
    LockTimeout = None

BATCH_STATE_FILENAME = ".telemetry-batch-state.json"


def _read_batch_state(session_root: Path) -> dict:
    """Read batch telemetry state tracking file."""
    try:
        state_path = session_root / BATCH_STATE_FILENAME
        if state_path.exists():
            return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"phases": {}}


def _write_batch_state(session_root: Path, state: dict) -> None:
    """Write batch telemetry state tracking file."""
    try:
        state_path = session_root / BATCH_STATE_FILENAME
        state_path.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


def _emit_batch_started(
    session_root: Path, phase_id: str, batch: dict, state: dict
) -> None:
    """Emit batch_started event if not already emitted for this batch."""
    phases_state = state.get("phases", {})
    phase_state = phases_state.get(phase_id, {})
    started_batches = phase_state.get("startedBatches", [])

    batch_id = batch.get("id")
    if batch_id in started_batches:
        return

    task_ids = batch.get("taskIds", [])
    write_telemetry_event(session_root, {
        "event": "batch_started",
        "phaseId": phase_id,
        "sessionId": session_root.name,
        "batchId": batch_id,
        "batchLabel": batch.get("label", f"Batch {batch_id}"),
        "taskCount": len(task_ids),
    }, phase_id=phase_id)

    started_batches.append(batch_id)
    phase_state["startedBatches"] = started_batches
    phases_state[phase_id] = phase_state
    state["phases"] = phases_state
    _write_batch_state(session_root, state)


def _emit_batch_confirmed(
    session_root: Path, phase_id: str, batch: dict, state: dict
) -> None:
    """Emit batch_confirmed event if not already emitted for this batch."""
    phases_state = state.get("phases", {})
    phase_state = phases_state.get(phase_id, {})
    confirmed_batches = phase_state.get("confirmedBatches", [])

    batch_id = batch.get("id")
    if batch_id in confirmed_batches:
        return

    now = datetime.now(timezone.utc)
    confirmation_wait_minutes = None
    completed_at = batch.get("completedAt")
    if completed_at:
        try:
            completed = datetime.fromisoformat(completed_at)
            confirmation_wait_minutes = round(
                (now - completed).total_seconds() / 60
            )
        except Exception:
            pass

    write_telemetry_event(session_root, {
        "event": "batch_confirmed",
        "phaseId": phase_id,
        "sessionId": session_root.name,
        "batchId": batch_id,
        "batchLabel": batch.get("label", f"Batch {batch_id}"),
        "confirmationWaitMinutes": confirmation_wait_minutes,
    }, phase_id=phase_id)

    confirmed_batches.append(batch_id)
    phase_state["confirmedBatches"] = confirmed_batches
    phases_state[phase_id] = phase_state
    state["phases"] = phases_state
    _write_batch_state(session_root, state)


def _locked_batch_emit(
    session_root: Path,
    phase_id: str,
    batch: dict,
    next_batch: dict | None,
    emit_started: bool = False,
    emit_confirmed: bool = False,
) -> None:
    """Execute batch telemetry emissions under a file lock to prevent races."""
    try:
        if FileLock is not None:
            lock = FileLock(str(session_root / ".telemetry-batch-state.lock"), timeout=1)
            with lock:
                state = _read_batch_state(session_root)
                if emit_confirmed:
                    _emit_batch_confirmed(session_root, phase_id, batch, state)
                if emit_started:
                    target = next_batch if next_batch else batch
                    _emit_batch_started(session_root, phase_id, target, state)
        else:
            state = _read_batch_state(session_root)
            if emit_confirmed:
                _emit_batch_confirmed(session_root, phase_id, batch, state)
            if emit_started:
                target = next_batch if next_batch else batch
                _emit_batch_started(session_root, phase_id, target, state)
    except Exception:
        pass


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

    build_mode = runtime.get("buildMode", "autonomous")
    if build_mode != "checkpoint":
        permit()
        return

    current_batch_id = runtime.get("currentBatchId")
    if current_batch_id is None:
        # No batch in progress yet — first batch starts now
        batches = runtime.get("batches", [])
        if batches:
            _locked_batch_emit(session_root, phase_id, batches[0], None, emit_started=True)
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
        }, phase_id=phase_id)
        block(
            message=(
                f"CHECKPOINT GATE — Configuration error for phase {phase_id}.\n\n"
                f"Batch {current_batch_id} referenced in currentBatchId but not found\n"
                f"in the batches array. Check the session manifest for consistency."
            ),
            phase_id=phase_id
        )
        return

    if current_batch.get("confirmed", False) is True:
        # Batch confirmed — emit confirmed event for this batch and
        # started event for the next batch
        current_idx = next(
            (i for i, b in enumerate(batches) if b.get("id") == current_batch_id),
            None
        )
        next_batch = None
        if current_idx is not None and current_idx + 1 < len(batches):
            next_batch = batches[current_idx + 1]

        _locked_batch_emit(session_root, phase_id, current_batch, next_batch, emit_confirmed=True, emit_started=bool(next_batch))

        permit()
        return

    from hooks_utils import get_phase_dir
    phase_manifest_path = get_phase_dir(session_root, phase_id) / "phase-manifest.json"
    batch_label = current_batch.get("label", f"Batch {current_batch_id}")
    review_path = current_batch.get("reviewPath", f"phase-{phase_id}-batch-{current_batch_id}-review.md")

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "batch-confirmation-gate",
        "phaseId": phase_id,
        "batchId": current_batch_id,
        "batchLabel": batch_label,
        "reason": "Developer has not confirmed batch review"
    }, phase_id=phase_id)

    block(
        message=(
            f"CHECKPOINT GATE — Next batch blocked for phase {phase_id}.\n\n"
            f"Current batch: {batch_label} (id: {current_batch_id})\n\n"
            f"Review the batch report before proceeding:\n"
            f"  {review_path}\n\n"
            f"To unblock:\n"
            f"  1. Review the batch review document and test results\n"
            f"  2. Open: {phase_manifest_path}\n"
            f"  3. Set batches[{current_batch_id}].confirmed = true\n\n"
            f"This flag cannot be set by the agent."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
