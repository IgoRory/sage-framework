"""
protected_manifest_fields_gate.py
SAGE Framework — Hook: protected-manifest-fields-gate
Event: preToolUse
Blocking: True

Guards against agents modifying protected fields in session-manifest.md
and phase-manifest.json files.

Protected fields that require explicit developer action:
  - validationConfirmed (phase-manifest.json)
  - batches[*].confirmed (phase-manifest.json)
  - foundationVerified (session-manifest.md)

On write-tool calls targeting either manifest type: parses the proposed
content, extracts the relevant data, and compares protected fields against
the current values. Blocks if any protected field changed.

If the proposed content cannot be parsed, permits (fail-open for this guard).
"""

import sys
import json
import re
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, block, permit,
    write_telemetry_event, is_write_tool, is_full_write_tool,
    get_target_path, get_proposed_content,
    NoSessionError, SessionIntegrityError
)

PROTECTED_PHASE_FIELDS_PATTERN = re.compile(
    r'"(validationConfirmed|confirmed)"\s*:\s*(true|false)', re.IGNORECASE
)


def extract_json_block(content: str) -> dict | None:
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return None


def collect_protected_values_from_root(manifest: dict) -> dict[str, bool]:
    """Collect protected boolean fields from the root manifest.
    foundationVerified lives in sessionState of the root manifest.
    """
    protected = {}
    session_state = manifest.get("sessionState", {})
    protected["sessionState.foundationVerified"] = session_state.get("foundationVerified", False)
    return protected


def check_proposed_has_runtime_fields(proposed_manifest: dict) -> list[str]:
    """Check if the proposed root manifest write contains runtime fields
    that should be in per-phase manifests. Block if so."""
    violations = []
    for phase_id, phase_data in proposed_manifest.get("phases", {}).items():
        runtime = phase_data.get("runtime", {})
        if "validationConfirmed" in runtime:
            violations.append(
                f"  phases.{phase_id}.runtime.validationConfirmed "
                f"(belongs in phase-{phase_id}/phase-manifest.json)"
            )
        for batch in runtime.get("batches", []):
            if "confirmed" in batch:
                batch_id = batch.get("id", "?")
                violations.append(
                    f"  phases.{phase_id}.runtime.batches[{batch_id}].confirmed "
                    f"(belongs in phase-{phase_id}/phase-manifest.json)"
                )
    return violations


def _extract_phase_id_from_path(target_path: str) -> str | None:
    """Extract the phase ID from a path like .../phase-3/phase-manifest.json."""
    m = re.search(r'phase-(\d+)[/\\]phase-manifest\.json', target_path)
    return m.group(1) if m else None


def _guard_phase_manifest(
    session_root: Path, target_path: str, proposed_content: str, is_full_write: bool
):
    """Guard validationConfirmed and batches[*].confirmed in phase-manifest.json.

    For full-file writes: parse as JSON and compare fields against current runtime.
    For partial edits (str_replace etc.): block if the edit text contains any
    protected field assignment, since we cannot reliably determine the resulting
    document state from a partial diff.
    """
    phase_id = _extract_phase_id_from_path(target_path)

    if not is_full_write:
        if PROTECTED_PHASE_FIELDS_PATTERN.search(proposed_content):
            try:
                write_telemetry_event(session_root, {
                    "event": "hook_rejection",
                    "hook": "protected-manifest-fields-gate",
                    "target": "phase-manifest.json",
                    "phaseId": phase_id,
                    "reason": "Partial edit contains protected field assignment"
                }, phase_id=phase_id)
            except Exception:
                pass
            block(
                message=(
                    "PROTECTED FIELDS GATE — Blocked partial edit to phase-manifest.json.\n\n"
                    "The edit contains a protected field (validationConfirmed or confirmed).\n"
                    "These fields can only be set by the developer, not by any agent.\n"
                    "Remove the protected field changes and retry."
                ),
                phase_id=phase_id
            )
            return
        permit()
        return

    try:
        proposed = json.loads(proposed_content)
    except (json.JSONDecodeError, ValueError):
        permit()
        return

    current_runtime = {}
    if phase_id:
        try:
            current_runtime = read_phase_runtime(session_root, phase_id)
        except Exception:
            pass

    changed_fields = []

    current_vc = current_runtime.get("validationConfirmed", False)
    proposed_vc = proposed.get("validationConfirmed", current_vc)
    if proposed_vc != current_vc:
        changed_fields.append(
            f"  validationConfirmed: {current_vc} → {proposed_vc}"
        )

    current_batches = current_runtime.get("batches", [])
    proposed_batches = proposed.get("batches", [])
    current_confirmed = {
        b.get("id"): b.get("confirmed", False) for b in current_batches
    }
    for batch in proposed_batches:
        bid = batch.get("id")
        cur = current_confirmed.get(bid, False)
        prop = batch.get("confirmed", cur)
        if prop != cur:
            changed_fields.append(
                f"  batches[{bid}].confirmed: {cur} → {prop}"
            )

    if not changed_fields:
        permit()
        return

    try:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "protected-manifest-fields-gate",
            "target": "phase-manifest.json",
            "changedFields": changed_fields,
            "reason": "Agent attempted to modify protected phase manifest fields"
        }, phase_id=phase_id)
    except Exception:
        pass

    field_list = "\n".join(changed_fields)
    block(
        message=(
            f"PROTECTED FIELDS GATE — Blocked modification to phase-manifest.json.\n\n"
            f"The following protected fields were changed in the proposed content:\n"
            f"{field_list}\n\n"
            f"These fields can only be set by the developer, not by any agent.\n"
            f"Remove the protected field changes and retry."
        ),
        phase_id=phase_id
    )


def main():
    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        manifest = read_manifest(session_root)
    except NoSessionError:
        permit()
        return
    except SessionIntegrityError as e:
        block(message=f"SESSION INTEGRITY ERROR — {e}")
        return

    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        permit()
        return

    if not is_write_tool(event_input):
        permit()
        return

    target_path = get_target_path(event_input)

    is_session_manifest = "session-manifest.md" in target_path
    is_phase_manifest = "phase-manifest.json" in target_path

    if not is_session_manifest and not is_phase_manifest:
        permit()
        return

    proposed_content = get_proposed_content(event_input)
    if not proposed_content:
        permit()
        return

    if is_phase_manifest:
        _guard_phase_manifest(
            session_root, target_path, proposed_content,
            is_full_write_tool(event_input)
        )
        return

    proposed_manifest = extract_json_block(proposed_content)
    if proposed_manifest is None:
        permit()
        return

    # Check if proposed write contains runtime fields that belong in per-phase manifests
    runtime_violations = check_proposed_has_runtime_fields(proposed_manifest)

    # Check foundationVerified changes in root manifest
    current_protected = collect_protected_values_from_root(manifest)
    proposed_protected = collect_protected_values_from_root(proposed_manifest)

    changed_fields = []
    for field_key, current_val in current_protected.items():
        proposed_val = proposed_protected.get(field_key, current_val)
        if proposed_val != current_val:
            changed_fields.append(f"  {field_key}: {current_val} → {proposed_val}")

    changed_fields.extend(runtime_violations)

    if not changed_fields:
        permit()
        return

    try:
        write_telemetry_event(session_root, {
            "event": "hook_rejection",
            "hook": "protected-manifest-fields-gate",
            "changedFields": changed_fields,
            "reason": "Agent attempted to modify protected manifest fields"
        })
    except Exception:
        pass

    field_list = "\n".join(changed_fields)
    block(
        message=(
            f"PROTECTED FIELDS GATE — Blocked modification to session-manifest.md.\n\n"
            f"The following protected fields were changed in the proposed content:\n"
            f"{field_list}\n\n"
            f"These fields can only be set by the developer, not by any agent.\n"
            f"Remove the protected field changes and retry."
        )
    )


if __name__ == "__main__":
    main()
