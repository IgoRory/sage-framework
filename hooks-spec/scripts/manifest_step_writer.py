"""
manifest_step_writer.py
SAGE Framework — Hook: manifest-step-writer
Event: afterFileEdit
Blocking: False

Detects phase step artifact writes and updates the session manifest's
stepStatus, stepTimestamps, and currentStep fields in real time. This
gives cross-phase visibility in Sprint mode — all worktrees share the
same .sage/ directory, so manifest updates are instantly visible.

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
    write_manifest_fields,
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

    suffix = _extract_artifact_suffix(file_path, phase_id)
    if not suffix:
        sys.exit(0)

    now = datetime.now(timezone.utc).isoformat()
    base = f"phases.{phase_id}.runtime"
    updates: dict[str, object] = {}

    if suffix == "red-results.md":
        updates[f"{base}.buildSubStep"] = "green-refactor"
        write_manifest_fields(session_root, updates)
        sys.exit(0)

    completed_step = ARTIFACT_TO_STEP.get(suffix)
    if not completed_step:
        sys.exit(0)

    updates[f"{base}.stepStatus.{completed_step}"] = "complete"
    updates[f"{base}.stepTimestamps.{completed_step}.completedAt"] = now

    if completed_step == "completion-report":
        updates[f"{base}.currentStep"] = "complete"
        updates[f"{base}.completedAt"] = now
    elif completed_step not in STEP_DOES_NOT_AUTO_ADVANCE:
        next_step = _next_step(completed_step)
        if next_step:
            updates[f"{base}.currentStep"] = next_step
            updates[f"{base}.stepStatus.{next_step}"] = "in-progress"
            updates[f"{base}.stepTimestamps.{next_step}.startedAt"] = now

    if completed_step == "build":
        updates[f"{base}.buildSubStep"] = None

    write_manifest_fields(session_root, updates)
    sys.exit(0)


if __name__ == "__main__":
    main()
