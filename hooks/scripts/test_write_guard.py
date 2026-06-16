"""
test_write_guard.py
SAGE Framework — Hook: test-write-guard
Event: preToolUse
Blocking: True

Blocks test-file writes during S5b GREEN/REFACTOR phase. The tdd-builder
agent must never modify test files — only the test-author (S5a RED phase)
writes tests. This hook enforces that constraint structurally.

Permits test-file writes during S5a (buildSubStep == "red").
Permits all non-test writes unconditionally (production code is handled
by red-results-gate instead).
"""

import os
import sys
import json
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_phase_runtime, block, permit,
    write_telemetry_event, is_write_tool, get_target_path,
    NoSessionError, SessionIntegrityError, run_gate
)

FILENAME_INDICATORS = (".spec.", ".test.", ".Tests.")

FILENAME_SUFFIX_INDICATORS = ("Tests.cs", "Tests.ts", "Tests.js")


def _is_test_file(path: str) -> bool:
    """Detect test files using filename and path-segment checks."""
    basename = os.path.basename(path)
    if any(ind in basename for ind in FILENAME_INDICATORS):
        return True
    if basename.endswith(tuple(FILENAME_SUFFIX_INDICATORS)):
        return True
    if "_test." in basename:
        return True
    if basename.startswith("test_"):
        return True
    return False


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        phase_id = get_phase_id()
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
    build_sub_step = runtime.get("buildSubStep", "")

    if current_step != "build":
        permit()
        return

    if build_sub_step == "red":
        permit()
        return

    if build_sub_step != "green-refactor":
        permit()
        return

    target_path = get_target_path(event_input)

    if not _is_test_file(target_path):
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "test-write-guard",
        "phaseId": phase_id,
        "reason": f"Test file write blocked during GREEN phase: {target_path}"
    })
    block(
        message=(
            f"TEST WRITE GUARD — Test file modification blocked for phase {phase_id}.\n\n"
            f"File: {target_path}\n\n"
            f"During S5b (GREEN/REFACTOR), only the test-author agent may write test files.\n"
            f"The tdd-builder must write production code only. If a test is wrong,\n"
            f"report it to the developer — do not modify the test yourself."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    run_gate(main)
