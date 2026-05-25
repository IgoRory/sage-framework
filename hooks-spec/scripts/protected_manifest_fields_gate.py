"""
protected_manifest_fields_gate.py
SAGE Framework — Hook: protected-manifest-fields-gate
Event: preToolUse
Blocking: True

Guards against agents modifying protected fields in session-manifest.md.
Protected fields are those that require explicit developer action:
  - validationConfirmed
  - batches[*].confirmed
  - foundationVerified

On write-tool calls targeting session-manifest.md: parses the proposed
content, extracts the JSON block, and compares protected fields against
the current manifest values. Blocks if any protected field changed.

If the proposed content cannot be parsed, permits (fail-open for this guard).
"""

import sys
import json
import re
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, block, permit,
    write_telemetry_event,
    NoSessionError, SessionIntegrityError
)

WRITE_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "overwrite_file",
    "insert_content", "patch_file"
}


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

    tool_name = event_input.get("tool_name", "").lower().replace("-", "_")
    if tool_name not in WRITE_TOOLS:
        permit()
        return

    tool_input = event_input.get("tool_input", {})
    target_path = tool_input.get("path") or tool_input.get("file_path") or tool_input.get("file") or ""
    if "session-manifest.md" not in target_path:
        permit()
        return

    proposed_content = tool_input.get("content") or tool_input.get("new_string") or ""
    if not proposed_content:
        permit()
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
