"""
telemetry_logger.py
SAGE Framework — Hook: telemetry-logger
Event: preToolUse, afterFileEdit, beforeShellExecution,
       afterShellExecution, afterMCPExecution, stop
Blocking: False

Writes a structured event record to workflow-telemetry.jsonl for every
hook fire. This is the primary data source for session-performance-evaluator
and skill-effectiveness-evaluator.

Idle detection: compares the current event timestamp against the last
recorded event for the same phase. If the gap exceeds the configured
idleThresholdMinutes, emits step_paused and step_resumed events
retrospectively. Threshold is read from .sage/workflow-config.json.

Uses hooks_utils for session/phase resolution so that the
current-phase.txt fallback is available in worktrees.

This hook never blocks. All errors are silently swallowed.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (
    find_repo_root,
    get_session_root,
    get_phase_id,
    get_phase_dir,
    NoSessionError,
    SessionIntegrityError,
)

IDLE_THRESHOLD_DEFAULT = 30
IDLE_BUFFER_DEFAULT = 5
STATE_FILENAME = ".telemetry-last-event.json"


def _read_idle_config(repo_root: Path) -> tuple[int, int]:
    """Read idle detection thresholds from workflow-config.json."""
    try:
        cfg_path = repo_root / ".sage" / "workflow-config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            telemetry = cfg.get("telemetry", {})
            threshold = telemetry.get("idleThresholdMinutes", IDLE_THRESHOLD_DEFAULT)
            buffer = telemetry.get("idleBufferMinutes", IDLE_BUFFER_DEFAULT)
            return int(threshold), int(buffer)
    except Exception:
        pass
    return IDLE_THRESHOLD_DEFAULT, IDLE_BUFFER_DEFAULT


def _read_last_event_state(session_root: Path) -> dict:
    """Read the per-phase last-event state file."""
    try:
        state_path = session_root / STATE_FILENAME
        if state_path.exists():
            return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"phases": {}}


def _write_last_event_state(session_root: Path, state: dict) -> None:
    """Write the per-phase last-event state file."""
    try:
        state_path = session_root / STATE_FILENAME
        state_path.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


def _append_event(telemetry_path: Path, record: dict) -> None:
    """Append a single event record to the telemetry file."""
    with open(telemetry_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _get_current_step_from_state(session_root: Path, phase_id: str) -> str | None:
    """Read currentStep from .telemetry-last-event.json state file.
    Written by manifest_step_writer — avoids parsing the manifest on every fire."""
    try:
        state_path = session_root / STATE_FILENAME
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if state.get("phaseId") == phase_id:
                return state.get("currentStep")
            phases = state.get("phases", {})
            phase_state = phases.get(phase_id, {})
            return phase_state.get("currentStep")
    except Exception:
        return None


def main():
    try:
        try:
            event_input = json.loads(sys.stdin.read())
        except Exception:
            event_input = {}

        try:
            repo_root = find_repo_root()
            session_root = get_session_root(repo_root)
        except (NoSessionError, SessionIntegrityError):
            sys.exit(0)

        session_id = session_root.name
        hook_event = os.environ.get("CURSOR_HOOK_EVENT", "unknown")
        phase_id = get_phase_id()
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # Per-phase telemetry: write to phase-{N}/workflow-telemetry.jsonl
        # when phase_id is set, otherwise to session-root (session-level events)
        if phase_id:
            phase_dir = get_phase_dir(session_root, phase_id)
            phase_dir.mkdir(parents=True, exist_ok=True)
            telemetry_path = phase_dir / "workflow-telemetry.jsonl"
        else:
            telemetry_path = session_root / "workflow-telemetry.jsonl"

        # Idle detection: emit step_paused/step_resumed if gap exceeds threshold
        if phase_id:
            threshold_min, buffer_min = _read_idle_config(repo_root)
            try:
                from filelock import FileLock, Timeout
                lock = FileLock(str(session_root / ".telemetry-last-event.lock"), timeout=1)
                with lock:
                    state = _read_last_event_state(session_root)
                    phases_state = state.get("phases", {})
                    phase_state = phases_state.get(phase_id)

                    if phase_state and phase_state.get("lastTimestamp"):
                        try:
                            last_ts = datetime.fromisoformat(phase_state["lastTimestamp"])
                            gap = now - last_ts
                            gap_minutes = gap.total_seconds() / 60

                            if gap_minutes > threshold_min:
                                current_step = (
                                    phase_state.get("currentStep")
                                    or _get_current_step_from_state(session_root, phase_id)
                                )
                                idle_gap_minutes = round(gap_minutes)

                                paused_at = last_ts + timedelta(minutes=buffer_min)
                                _append_event(telemetry_path, {
                                    "timestamp": paused_at.isoformat(),
                                    "event": "step_paused",
                                    "phaseId": phase_id,
                                    "sessionId": session_id,
                                    "step": current_step,
                                    "idleGapMinutes": idle_gap_minutes,
                                })
                                _append_event(telemetry_path, {
                                    "timestamp": now_iso,
                                    "event": "step_resumed",
                                    "phaseId": phase_id,
                                    "sessionId": session_id,
                                    "step": current_step,
                                    "idleGapMinutes": idle_gap_minutes,
                                })
                        except Exception:
                            pass

                    current_step = _get_current_step_from_state(session_root, phase_id)
                    phases_state[phase_id] = {
                        "lastTimestamp": now_iso,
                        "currentStep": current_step,
                    }
                    state["phases"] = phases_state
                    _write_last_event_state(session_root, state)
            except (ImportError, Timeout):
                pass

        # Write the normal telemetry event
        record = {
            "timestamp": now_iso,
            "event": hook_event,
            "phaseId": phase_id,
            "sessionId": session_id,
        }

        if hook_event == "preToolUse":
            record["toolName"] = event_input.get("tool_name")
            tool_input = event_input.get("tool_input")
            if tool_input:
                serialized = json.dumps(tool_input) if not isinstance(tool_input, str) else tool_input
                record["toolInput"] = serialized[:500] if len(serialized) > 500 else serialized

        elif hook_event == "afterFileEdit":
            record["filePath"] = event_input.get("file_path")
            record["editType"] = event_input.get("edit_type")

        elif hook_event in ("beforeShellExecution", "afterShellExecution"):
            record["command"] = event_input.get("command")
            if hook_event == "afterShellExecution":
                record["exitCode"] = event_input.get("exit_code")

        elif hook_event == "afterMCPExecution":
            record["mcpServer"] = event_input.get("server_name")
            record["mcpTool"] = event_input.get("tool_name")

        elif hook_event == "stop":
            record["stopReason"] = event_input.get("reason")

        _append_event(telemetry_path, record)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
