"""
backfill_manifest.py
SAGE Framework — One-time manifest telemetry backfill

Scans each phase directory for existing step artifacts and updates the
session manifest's stepStatus, stepTimestamps, and currentStep to reflect
actual progress. Seeds workflow-telemetry.jsonl with synthetic events
marked "source": "backfill".

Usage:
    python .cursor/hooks/scripts/backfill_manifest.py --dry-run
    python .cursor/hooks/scripts/backfill_manifest.py
    python .cursor/hooks/scripts/backfill_manifest.py --mark-s1-complete
    python .cursor/hooks/scripts/backfill_manifest.py --mark-s1-complete 1,2,3
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (
    find_repo_root,
    get_session_root,
    read_manifest,
    find_marker_value,
    has_status_marker,
    write_telemetry_event,
    NoSessionError,
    SessionIntegrityError,
    _replace_manifest_json,
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
    "red-results.md": None,
    "tdd-results.md": "build",
    "code-review.md": "code-review",
    "security-review.md": "security-review",
    "test-results.md": "agent-testing",
    "completion-report.md": "completion-report",
}

STEP_DOES_NOT_AUTO_ADVANCE = {"plan-validation"}


def _next_step(current: str) -> str | None:
    try:
        idx = STEP_SEQUENCE.index(current)
        if idx + 1 < len(STEP_SEQUENCE):
            return STEP_SEQUENCE[idx + 1]
    except ValueError:
        pass
    return None


def _step_index(step: str) -> int:
    try:
        return STEP_SEQUENCE.index(step)
    except ValueError:
        return -1


def _scan_phase_artifacts(phase_dir: Path, phase_id: str) -> dict:
    """
    Scan a phase directory for step artifacts. Returns a dict of
    {step_name: {"suffix": str, "path": Path, "mtime": str}} for
    each found artifact, plus a "red_results" key if that sub-step
    artifact exists.
    """
    results = {}
    if not phase_dir.exists():
        return results

    prefix = f"phase-{phase_id}-"
    for child in phase_dir.iterdir():
        if not child.is_file():
            continue
        name = child.name
        if not name.startswith(prefix):
            continue

        suffix = name[len(prefix):]
        if suffix not in ARTIFACT_TO_STEP:
            continue

        mtime = datetime.fromtimestamp(
            child.stat().st_mtime, tz=timezone.utc
        ).isoformat()

        step = ARTIFACT_TO_STEP[suffix]
        if step is None:
            results["_red_results"] = {
                "suffix": suffix,
                "path": child,
                "mtime": mtime,
            }
        else:
            if step not in results or mtime > results[step]["mtime"]:
                results[step] = {
                    "suffix": suffix,
                    "path": child,
                    "mtime": mtime,
                }

    return results


def _check_gate_markers(artifact_info: dict, phase_dir: Path, phase_id: str) -> dict:
    """
    Read artifact contents and check gate markers. Returns a dict of
    {step: {"passed": bool, "detail": str}} for steps that have gate markers.
    """
    markers = {}
    prefix = f"phase-{phase_id}-"

    if "traceability-review" in artifact_info:
        path = artifact_info["traceability-review"]["path"]
        content = path.read_text(encoding="utf-8")
        count = find_marker_value(content, "Blocker findings")
        if count is not None:
            markers["traceability-review"] = {
                "passed": count == 0,
                "detail": f"Blocker findings: {count}",
            }

    if "code-review" in artifact_info:
        path = artifact_info["code-review"]["path"]
        content = path.read_text(encoding="utf-8")
        count = find_marker_value(content, "Critical findings")
        if count is not None:
            markers["code-review"] = {
                "passed": count == 0,
                "detail": f"Critical findings: {count}",
            }

    if "security-review" in artifact_info:
        path = artifact_info["security-review"]["path"]
        content = path.read_text(encoding="utf-8")
        count = find_marker_value(content, "Critical findings")
        if count is not None:
            markers["security-review"] = {
                "passed": count == 0,
                "detail": f"Critical findings: {count}",
            }

    if "_red_results" in artifact_info:
        path = artifact_info["_red_results"]["path"]
        content = path.read_text(encoding="utf-8")
        markers["_red_results"] = {
            "passed": has_status_marker(content, "STATUS: RED CONFIRMED"),
            "detail": "STATUS: RED CONFIRMED" if has_status_marker(content, "STATUS: RED CONFIRMED") else "RED not confirmed",
        }

    if "build" in artifact_info:
        path = artifact_info["build"]["path"]
        content = path.read_text(encoding="utf-8")
        markers["build"] = {
            "passed": has_status_marker(content, "STATUS: PASS"),
            "detail": "STATUS: PASS" if has_status_marker(content, "STATUS: PASS") else "STATUS: FAIL or missing",
        }

    if "agent-testing" in artifact_info:
        path = artifact_info["agent-testing"]["path"]
        content = path.read_text(encoding="utf-8")
        markers["agent-testing"] = {
            "passed": has_status_marker(content, "STATUS: PASS"),
            "detail": "STATUS: PASS" if has_status_marker(content, "STATUS: PASS") else "STATUS: FAIL or missing",
        }

    return markers


def _compute_updates(
    phase_id: str,
    artifact_info: dict,
    gate_markers: dict,
    mark_s1: bool,
    current_runtime: dict,
) -> tuple[dict, list[dict]]:
    """
    Compute manifest field updates and telemetry events for a single phase.
    Returns (updates_dict, telemetry_events_list).
    Only advances state forward -- never regresses completed steps.
    """
    base = f"phases.{phase_id}.runtime"
    updates = {}
    events = []
    highest_completed_idx = -1

    existing_status = current_runtime.get("stepStatus", {})

    if mark_s1 and "dev-interview" not in artifact_info:
        if existing_status.get("dev-interview") != "complete":
            now = datetime.now(timezone.utc).isoformat()
            updates[f"{base}.stepStatus.dev-interview"] = "complete"
            updates[f"{base}.stepTimestamps.dev-interview.completedAt"] = now
            events.append({
                "event": "backfill_step_complete",
                "source": "backfill",
                "phaseId": phase_id,
                "step": "dev-interview",
                "reason": "mark-s1-complete flag (interview conducted pre-hooks)",
            })
            highest_completed_idx = max(highest_completed_idx, 0)

    for step in STEP_SEQUENCE:
        if step not in artifact_info:
            continue
        if existing_status.get(step) == "complete":
            highest_completed_idx = max(highest_completed_idx, _step_index(step))
            continue

        info = artifact_info[step]
        updates[f"{base}.stepStatus.{step}"] = "complete"
        updates[f"{base}.stepTimestamps.{step}.completedAt"] = info["mtime"]

        events.append({
            "event": "backfill_step_complete",
            "source": "backfill",
            "phaseId": phase_id,
            "step": step,
            "artifact": info["suffix"],
            "artifactMtime": info["mtime"],
        })

        if step in gate_markers:
            gm = gate_markers[step]
            events.append({
                "event": "backfill_gate_marker",
                "source": "backfill",
                "phaseId": phase_id,
                "step": step,
                "passed": gm["passed"],
                "detail": gm["detail"],
            })

        highest_completed_idx = max(highest_completed_idx, _step_index(step))

    if "_red_results" in artifact_info:
        gm = gate_markers.get("_red_results", {})
        if gm.get("passed"):
            updates[f"{base}.buildSubStep"] = "green-refactor"
            events.append({
                "event": "backfill_substep_transition",
                "source": "backfill",
                "phaseId": phase_id,
                "step": "build",
                "buildSubStep": "green-refactor",
            })

    if "build" in artifact_info:
        updates[f"{base}.buildSubStep"] = None

    if highest_completed_idx >= 0:
        completed_step = STEP_SEQUENCE[highest_completed_idx]

        if completed_step == "completion-report":
            updates[f"{base}.currentStep"] = "complete"
            if completed_step in artifact_info:
                updates[f"{base}.completedAt"] = artifact_info[completed_step]["mtime"]
        elif completed_step not in STEP_DOES_NOT_AUTO_ADVANCE:
            nxt = _next_step(completed_step)
            if nxt:
                updates[f"{base}.currentStep"] = nxt
                if existing_status.get(nxt) not in ("complete", "in-progress"):
                    updates[f"{base}.stepStatus.{nxt}"] = "in-progress"
                    updates[f"{base}.stepTimestamps.{nxt}.startedAt"] = (
                        datetime.now(timezone.utc).isoformat()
                    )
        else:
            updates[f"{base}.currentStep"] = completed_step

        if not current_runtime.get("startedAt"):
            earliest = None
            for step in STEP_SEQUENCE:
                if step in artifact_info:
                    mt = artifact_info[step]["mtime"]
                    if earliest is None or mt < earliest:
                        earliest = mt
            if earliest:
                updates[f"{base}.startedAt"] = earliest

    return updates, events


def main():
    parser = argparse.ArgumentParser(
        description="Backfill session manifest from existing phase artifacts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changes without applying them",
    )
    parser.add_argument(
        "--mark-s1-complete",
        nargs="?",
        const="all",
        default=None,
        metavar="PHASES",
        help="Mark S1 complete for phases without a dev-interview artifact. "
             "Pass comma-separated phase IDs (e.g. 1,2,3) or omit for all.",
    )
    args = parser.parse_args()

    s1_phases: set[str] | None = None
    if args.mark_s1_complete is not None:
        if args.mark_s1_complete == "all":
            s1_phases = None
        else:
            s1_phases = {p.strip() for p in args.mark_s1_complete.split(",")}

    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        manifest = read_manifest(session_root)
    except (NoSessionError, SessionIntegrityError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    session_id = manifest.get("sessionId", "unknown")
    feature = manifest.get("featureTitle", "unknown")
    phases = manifest.get("phases", {})

    print(f"Session: {session_id}")
    print(f"Feature: {feature}")
    print(f"Phases:  {len(phases)}")
    print(f"Mode:    {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    all_updates = {}
    all_events = []

    for phase_id in sorted(phases.keys(), key=lambda x: int(x)):
        phase = phases[phase_id]
        runtime = phase.get("runtime", {})
        definition = phase.get("definition", {})
        title = definition.get("title", "Untitled")
        phase_dir = session_root / f"phase-{phase_id}"

        print(f"--- Phase {phase_id}: {title} ---")
        print(f"    Current step:   {runtime.get('currentStep', 'unknown')}")
        print(f"    Phase dir:      {phase_dir}")

        artifact_info = _scan_phase_artifacts(phase_dir, phase_id)
        if artifact_info:
            artifact_names = [
                info["suffix"]
                for key, info in artifact_info.items()
                if key != "_red_results"
            ]
            if "_red_results" in artifact_info:
                artifact_names.append(artifact_info["_red_results"]["suffix"])
            print(f"    Artifacts found: {', '.join(artifact_names)}")
        else:
            print("    Artifacts found: (none)")

        gate_markers = _check_gate_markers(artifact_info, phase_dir, phase_id)

        mark_s1 = (
            args.mark_s1_complete is not None
            and (s1_phases is None or phase_id in s1_phases)
        )

        updates, events = _compute_updates(
            phase_id, artifact_info, gate_markers, mark_s1, runtime
        )

        if updates:
            print("    Updates:")
            for field, value in updates.items():
                short_field = field.replace(f"phases.{phase_id}.runtime.", "")
                print(f"      {short_field} = {json.dumps(value)}")
        else:
            print("    Updates: (none — already up to date)")

        if events:
            print(f"    Telemetry events: {len(events)}")
            for evt in events:
                print(f"      [{evt['event']}] {evt.get('step', '')} {evt.get('detail', evt.get('reason', ''))}")

        print()

        all_updates.update(updates)
        all_events.extend(events)

    if not all_updates and not all_events:
        print("Nothing to backfill — manifest is already up to date.")
        return

    print(f"TOTAL: {len(all_updates)} manifest field updates, {len(all_events)} telemetry events")
    print()

    if args.dry_run:
        print("DRY RUN — no changes applied. Re-run without --dry-run to apply.")
        return

    try:
        from filelock import FileLock

        lock_path = session_root / "manifest.lock"
        lock = FileLock(str(lock_path), timeout=10)

        with lock:
            manifest = read_manifest(session_root)
            for field_path, value in all_updates.items():
                keys = field_path.split(".")
                target = manifest
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value

            manifest_path = session_root / "session-manifest.md"
            _replace_manifest_json(manifest_path, manifest)

        print("Manifest updated successfully.")

    except ImportError:
        print(
            "WARNING: filelock not installed. Writing without lock.",
            file=sys.stderr,
        )
        manifest = read_manifest(session_root)
        for field_path, value in all_updates.items():
            keys = field_path.split(".")
            target = manifest
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value
        manifest_path = session_root / "session-manifest.md"
        _replace_manifest_json(manifest_path, manifest)
        print("Manifest updated (without lock).")

    for evt in all_events:
        write_telemetry_event(session_root, evt)

    print(f"Wrote {len(all_events)} telemetry events to workflow-telemetry.jsonl")
    print()
    print("Backfill complete. Hooks will track all future step transitions in real time.")


if __name__ == "__main__":
    main()
