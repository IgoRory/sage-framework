"""
manifest_step_writer.py
SAGE Framework — Hook: manifest-step-writer
Event: afterFileEdit
Blocking: False

Detects phase step artifact writes and updates the session manifest's
stepStatus, stepTimestamps, and currentStep fields in real time. This
gives cross-phase visibility in Sprint mode — all worktrees share the
same .sage/ directory, so manifest updates are instantly visible.

Also detects batch review documents (phase-{N}-batch-{M}-review.md) in
Checkpoint mode and emits batch_completed telemetry events with duration.

This hook never blocks. All errors are silently swallowed.
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone

from hooks_utils import (
    find_repo_root,
    get_session_root,
    get_phase_id,
    get_phase_dir,
    read_phase_runtime,
    write_phase_runtime,
    write_telemetry_event,
    NoSessionError,
    SessionIntegrityError,
)

STEP_SEQUENCE = [
    "dev-interview",
    "implementation-plan",
    "traceability-review",
    "plan-validation",
    "build",
    "code-review",
    "security-review",
    "agent-testing",
    "completion-report",
]

ARTIFACT_TO_STEP = {
    "dev-interview-summary.md": "dev-interview",
    "implementation-plan.md": "implementation-plan",
    "traceability-review.md": "traceability-review",
    "plan-preview.canvas.tsx": "plan-validation",
    "plan-preview.md": "plan-validation",
    "calculation-proof.md": "plan-validation",
    "red-results.md": None,  # sub-step transition, not a full step
    "tdd-results.md": "build",
    "code-review.md": "code-review",
    "security-review.md": "security-review",
    "test-results.md": "agent-testing",
    "completion-report.md": "completion-report",
}

STEP_DOES_NOT_AUTO_ADVANCE = {"plan-validation"}

BATCH_REVIEW_PATTERN = re.compile(r"^phase-(\d+)-batch-(\d+)-review\.md$")


def _next_step(current: str) -> str | None:
    """Return the step after current in the sequence, or None if last."""
    try:
        idx = STEP_SEQUENCE.index(current)
        if idx + 1 < len(STEP_SEQUENCE):
            return STEP_SEQUENCE[idx + 1]
    except ValueError:
        pass
    return None


def _extract_artifact_suffix(file_path: str, phase_id: str) -> str | None:
    """
    Given a file path like '.../phase-1-dev-interview-summary.md',
    extract 'dev-interview-summary.md' (the part after 'phase-N-').
    Returns None if the file does not match the phase artifact pattern.
    """
    basename = Path(file_path).name
    prefix = f"phase-{phase_id}-"
    if basename.startswith(prefix):
        return basename[len(prefix):]
    return None


def _handle_batch_review(session_root: Path, phase_id: str, batch_id_str: str) -> None:
    """
    Handle a batch review document write: emit batch_completed telemetry
    and update batch completedAt in phase-manifest.json.
    """
    try:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        batch_id = int(batch_id_str)

        runtime = read_phase_runtime(session_root, phase_id)
        batches = runtime.get("batches", [])

        current_batch = next(
            (b for b in batches if b.get("id") == batch_id), None
        )
        if not current_batch:
            return

        if current_batch.get("completedAt"):
            return

        batch_label = current_batch.get("label", f"Batch {batch_id}")
        batch_started_at = current_batch.get("startedAt")

        duration_minutes = None
        if batch_started_at:
            try:
                started = datetime.fromisoformat(batch_started_at)
                duration_minutes = round((now - started).total_seconds() / 60)
            except Exception:
                pass

        batch_idx = next(
            (i for i, b in enumerate(batches) if b.get("id") == batch_id), None
        )
        if batch_idx is not None:
            write_phase_runtime(session_root, phase_id, {
                f"batches.{batch_idx}.completedAt": now_iso,
            })

        write_telemetry_event(session_root, {
            "event": "batch_completed",
            "phaseId": phase_id,
            "sessionId": session_root.name,
            "batchId": batch_id,
            "batchLabel": batch_label,
            "testsPassing": current_batch.get("testsPassing"),
            "durationMinutes": duration_minutes,
        }, phase_id=phase_id)

    except Exception:
        pass


def _update_telemetry_state(
    session_root: Path, phase_id: str, updates: dict
) -> None:
    """
    Write currentStep to .telemetry-last-event.json so telemetry_logger
    can source the current step without reading the manifest.
    """
    try:
        current_step = updates.get("currentStep")
        if current_step is None:
            return
        state_path = session_root / ".telemetry-last-event.json"
        state = {}
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception:
                state = {}
        state["currentStep"] = current_step
        state["phaseId"] = phase_id
        state["updatedAt"] = datetime.now(timezone.utc).isoformat()
        state_path.write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    if not phase_id:
        sys.exit(0)

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        event_input = {}

    file_path = event_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Check for batch review document pattern
    basename = Path(file_path).name
    batch_match = BATCH_REVIEW_PATTERN.match(basename)
    if batch_match:
        matched_phase = batch_match.group(1)
        matched_batch = batch_match.group(2)
        if matched_phase == phase_id:
            _handle_batch_review(session_root, phase_id, matched_batch)
        sys.exit(0)

    suffix = _extract_artifact_suffix(file_path, phase_id)
    if not suffix:
        sys.exit(0)

    now = datetime.now(timezone.utc).isoformat()
    updates: dict[str, object] = {}

    if suffix == "red-results.md":
        updates["buildSubStep"] = "green-refactor"
        write_phase_runtime(session_root, phase_id, updates)
        sys.exit(0)

    completed_step = ARTIFACT_TO_STEP.get(suffix)
    if not completed_step:
        sys.exit(0)

    updates[f"stepStatus.{completed_step}"] = "complete"
    updates[f"stepTimestamps.{completed_step}.completedAt"] = now

    if completed_step == "completion-report":
        updates["currentStep"] = "complete"
        updates["completedAt"] = now
    elif completed_step not in STEP_DOES_NOT_AUTO_ADVANCE:
        next_step = _next_step(completed_step)
        if next_step:
            updates["currentStep"] = next_step
            updates[f"stepStatus.{next_step}"] = "in-progress"
            updates[f"stepTimestamps.{next_step}.startedAt"] = now

    if completed_step == "build":
        updates["buildSubStep"] = None

    write_phase_runtime(session_root, phase_id, updates)

    # Update telemetry state file so telemetry_logger can read currentStep
    # without parsing the manifest on every invocation
    _update_telemetry_state(session_root, phase_id, updates)
    sys.exit(0)


if __name__ == "__main__":
    main()
