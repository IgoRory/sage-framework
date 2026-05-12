"""
telemetry_logger.py
SAGE Framework — Hook: telemetry-logger
Event: preToolUse, afterFileEdit, beforeShellExecution,
       afterShellExecution, afterMCPExecution, stop
Blocking: False

Writes a structured event record to workflow-telemetry.jsonl for every
hook fire. This is the primary data source for session-performance-evaluator
and skill-effectiveness-evaluator.

This hook never blocks. All errors are silently swallowed.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone


def main():
    try:
        # Read event input from stdin
        try:
            event_input = json.loads(sys.stdin.read())
        except Exception:
            event_input = {}

        # Resolve paths
        repo_root = None
        current = Path.cwd()
        for _ in range(10):
            if (current / ".git").exists():
                repo_root = current
                break
            parent = current.parent
            if parent == current:
                break
            current = parent

        if repo_root is None:
            sys.exit(0)

        active_file = repo_root / ".sage" / "sessions" / "active-session.txt"
        if not active_file.exists():
            sys.exit(0)

        session_id = active_file.read_text(encoding="utf-8").strip()
        if not session_id:
            sys.exit(0)

        session_root = repo_root / ".sage" / "sessions" / session_id
        if not session_root.exists():
            sys.exit(0)

        # Build event record
        hook_event = os.environ.get("CURSOR_HOOK_EVENT", "unknown")
        phase_id = os.environ.get("SAGE_PHASE_ID")

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": hook_event,
            "phaseId": phase_id,
            "sessionId": session_id,
        }

        # Attach relevant event-specific fields
        if hook_event == "preToolUse":
            record["toolName"] = event_input.get("tool_name")
            record["toolInput"] = event_input.get("tool_input")

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

        # Write to telemetry file
        telemetry_path = session_root / "workflow-telemetry.jsonl"
        with open(telemetry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    except Exception:
        pass  # telemetry logger is always silent on failure

    sys.exit(0)


if __name__ == "__main__":
    main()
