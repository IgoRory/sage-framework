"""
manifest_step_gate.py
SAGE Framework — Hook: manifest-step-gate
Event: preToolUse
Blocking: True

Enforces the S1→S8 step progression. Before any step-initiating tool call,
checks that the prior step's required artifact exists in the phase directory.

Step → required prior artifact:
  dev-interview       → (none — first step)
  implementation-plan → phase-{N}-dev-interview-summary.md
  traceability-review → phase-{N}-implementation-plan.md
  plan-validation     → phase-{N}-traceability-review.md  (Blocker findings: 0)
  build               → phase-{N}-plan-preview.canvas.tsx  (via validationConfirmed)
  code-review         → phase-{N}-tdd-results.md with STATUS: PASS (handled by tdd-results-gate)
  agent-testing       → phase-{N}-code-review.md           (handled by code-review-gate)
  completion-report   → phase-{N}-test-results.md          (handled by stop gate)

This gate checks the artifact existence for steps 2–5.
Steps 6–8 have dedicated gates.
"""

import sys
import json
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, get_phase_dir, block, permit,
    write_telemetry_event, find_marker_value,
    NoSessionError, SessionIntegrityError
)

# Map: the step being initiated → artifact that must exist from the prior step
PRIOR_ARTIFACT = {
    "implementation-plan": "phase-{N}-dev-interview-summary.md",
    "traceability-review": "phase-{N}-implementation-plan.md",
    "plan-validation":     "phase-{N}-traceability-review.md",
    "build":               "phase-{N}-implementation-plan.md",  # broad check; validationConfirmed gate handles S4
}

# Tool calls that signal a step is being initiated
STEP_INITIATING_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "run_build", "execute_command"
}


def resolve_artifact_name(template: str, phase_id: str) -> str:
    return template.replace("{N}", phase_id)


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
    if tool_name not in STEP_INITIATING_TOOLS:
        permit()
        return

    phase_data = manifest.get("phases", {}).get(phase_id, {})
    runtime = phase_data.get("runtime", {})
    current_step = runtime.get("currentStep", "")

    required_artifact_template = PRIOR_ARTIFACT.get(current_step)
    if not required_artifact_template:
        # Either first step or a step handled by a dedicated gate
        permit()
        return

    phase_dir = get_phase_dir(session_root, phase_id)
    artifact_name = resolve_artifact_name(required_artifact_template, phase_id)
    artifact_path = phase_dir / artifact_name

    # plan-validation: check artifact exists AND Blocker findings == 0 before permitting
    if current_step == "plan-validation":
        if not artifact_path.exists():
            write_telemetry_event(session_root, {
                "event": "hook_rejection",
                "hook": "manifest-step-gate",
                "phaseId": phase_id,
                "step": current_step,
                "missingArtifact": str(artifact_path),
                "reason": f"Required artifact missing for step '{current_step}'"
            })
            block(
                message=(
                    f"STEP GATE — Cannot begin '{current_step}' for phase {phase_id}.\n\n"
                    f"Required artifact not found:\n  {artifact_path}\n\n"
                    f"Complete the traceability review (S3) before proceeding."
                ),
                phase_id=phase_id
            )
            return

        content = artifact_path.read_text(encoding="utf-8")
        if find_marker_value(content, "Blocker findings") != 0:
            write_telemetry_event(session_root, {
                "event": "hook_rejection",
                "hook": "manifest-step-gate",
                "phaseId": phase_id,
                "step": current_step,
                "reason": "Traceability review has Blocker findings — cannot advance to plan-validation"
            })
            block(
                message=(
                    f"STEP GATE — Cannot advance to plan-validation.\n\n"
                    f"The traceability review for phase {phase_id} contains Blocker findings.\n"
                    f"All Blocker findings must be resolved before plan validation can proceed.\n\n"
                    f"Review: {artifact_path}\n"
                    f"Required: 'Blocker findings: 0' in the document."
                ),
                phase_id=phase_id
            )
            return

        permit()
        return

    # All other steps: artifact existence check only
    if artifact_path.exists():
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "manifest-step-gate",
        "phaseId": phase_id,
        "step": current_step,
        "missingArtifact": str(artifact_path),
        "reason": f"Required artifact missing for step '{current_step}'"
    })

    block(
        message=(
            f"STEP GATE — Cannot begin '{current_step}' for phase {phase_id}.\n\n"
            f"Required artifact not found:\n  {artifact_path}\n\n"
            f"Complete the prior step and ensure the artifact is written to the "
            f"phase directory before proceeding."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
