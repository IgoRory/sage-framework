"""
required_references_gate.py
SAGE Framework — Hook: required-references-gate
Event: preToolUse
Blocking: True

Blocks S5 build from starting until all files listed in the phase's
requiredReferences array in the session manifest have been read in the
current session.

"Read" is confirmed by the presence of a telemetry record with:
  event: "preToolUse", toolName: "read_file", filePath: <path>

This ensures the agent has loaded and processed all PRD and domain
reference files before writing implementation code.
"""

import sys
import json
from pathlib import Path
from hooks_utils import (
    find_repo_root, get_session_root, get_phase_id,
    read_manifest, read_phase_runtime, get_phase_dir, block, permit,
    write_telemetry_event,
    NoSessionError, SessionIntegrityError
)

BUILD_INITIATING_TOOLS = {
    "write_file", "create_file", "edit_file", "str_replace",
    "str_replace_editor", "apply_edit", "run_build"
}


def get_read_files_from_telemetry(session_root: Path, phase_id: str | None = None) -> set:
    """
    Parse workflow-telemetry.jsonl and return the set of file paths
    that have been read (confirmed by read_file preToolUse events).
    Reads both session-root and per-phase telemetry files.
    """
    read_files: set[str] = set()
    telemetry_paths = [session_root / "workflow-telemetry.jsonl"]
    if phase_id:
        telemetry_paths.append(
            get_phase_dir(session_root, phase_id) / "workflow-telemetry.jsonl"
        )

    for telemetry_path in telemetry_paths:
        if not telemetry_path.exists():
            continue
        with open(telemetry_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if (
                        record.get("event") == "preToolUse"
                        and record.get("toolName") in {"read_file", "view_file"}
                    ):
                        fp = record.get("toolInput", {})
                        if isinstance(fp, dict):
                            path = fp.get("path") or fp.get("file_path")
                        else:
                            path = str(fp)
                        if path:
                            read_files.add(Path(path).name)
                            read_files.add(path)
                except Exception:
                    continue

    return read_files


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
    if tool_name not in BUILD_INITIATING_TOOLS:
        permit()
        return

    runtime = read_phase_runtime(session_root, phase_id)
    current_step = runtime.get("currentStep", "")

    if current_step != "build":
        permit()
        return

    definition = manifest.get("phases", {}).get(phase_id, {}).get("definition", {})
    required_refs = definition.get("requiredReferences", [])

    if not required_refs:
        permit()
        return

    read_files = get_read_files_from_telemetry(session_root, phase_id)

    missing = []
    for ref in required_refs:
        ref_path = Path(ref)
        if ref not in read_files and ref_path.name not in read_files:
            missing.append(ref)

    if not missing:
        permit()
        return

    write_telemetry_event(session_root, {
        "event": "hook_rejection",
        "hook": "required-references-gate",
        "phaseId": phase_id,
        "missingReferences": missing,
        "reason": "Required reference files not yet read"
    })

    missing_list = "\n".join(f"  - {r}" for r in missing)
    block(
        message=(
            f"REFERENCES GATE — Build blocked for phase {phase_id}.\n\n"
            f"The following required reference files have not been read this session:\n"
            f"{missing_list}\n\n"
            f"Read all required references before beginning implementation.\n"
            f"Use read_file on each path listed above."
        ),
        phase_id=phase_id
    )


if __name__ == "__main__":
    main()
