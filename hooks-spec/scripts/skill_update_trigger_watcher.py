"""
skill_update_trigger_watcher.py
SAGE Framework — Hook: skill-update-trigger-watcher
Event: afterFileEdit
Blocking: False

Watches the .skill-update-triggers/ directory. When a new trigger file
appears (written by the Linear webhook receiver after an approval event),
this hook validates the trigger JSON, logs it to skill-update-history.jsonl
with status pending_manual_apply, writes a telemetry event, archives the
trigger file, and prints a manual-apply instruction to stderr.

The hook does NOT apply diffs or make commits — all git operations for
skill updates must be performed manually by the developer.

Trigger file format (JSON):
{
  "linearIssueId": "PROF-123",
  "skillName": "prd-completeness-check",
  "action": "approved" | "rejected",
  "diffPath": ".skill-update-staging/PROF-123.diff",
  "approvedBy": "Product Manager",
  "approvedAt": "2026-01-15T09:30:00Z"
}

Non-blocking: errors are logged but do not affect the agent's tool call.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from hooks_utils import find_repo_root, write_telemetry_event, NoSessionError


def log_to_history(repo_root: Path, record: dict) -> None:
    history_path = repo_root / ".sage" / "skill-update-history.jsonl"
    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **record
            }) + "\n")
    except Exception:
        pass


def try_write_telemetry(repo_root: Path, event: dict) -> None:
    try:
        active_file = repo_root / ".sage" / "sessions" / "active-session.txt"
        if active_file.exists():
            session_id = active_file.read_text(encoding="utf-8").strip()
            session_root = repo_root / ".sage" / "sessions" / session_id
            if session_root.exists():
                write_telemetry_event(session_root, event)
    except Exception:
        pass


def main():
    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    file_path = event_input.get("file_path", "")
    if ".skill-update-triggers" not in file_path:
        sys.exit(0)

    try:
        repo_root = find_repo_root()
    except (NoSessionError, Exception):
        sys.exit(0)

    trigger_path = Path(file_path)
    if not trigger_path.exists() or not trigger_path.suffix == ".json":
        sys.exit(0)

    try:
        trigger = json.loads(trigger_path.read_text(encoding="utf-8"))
    except Exception as e:
        log_to_history(repo_root, {
            "event": "trigger_parse_error",
            "triggerFile": file_path,
            "error": str(e)
        })
        sys.exit(0)

    action = trigger.get("action", "")
    skill_name = trigger.get("skillName", "unknown")
    issue_id = trigger.get("linearIssueId", "unknown")
    diff_path = trigger.get("diffPath", "")

    archive_dir = repo_root / ".skill-update-triggers" / "processed"
    archive_dir.mkdir(parents=True, exist_ok=True)

    if action == "approved":
        log_to_history(repo_root, {
            "event": "skill_update_pending_manual_apply",
            "status": "pending_manual_apply",
            "linearIssueId": issue_id,
            "skillName": skill_name,
            "diffPath": diff_path,
            "approvedBy": trigger.get("approvedBy", "unknown"),
            "approvedAt": trigger.get("approvedAt", "unknown")
        })

        try_write_telemetry(repo_root, {
            "event": "skill_update_pending_manual_apply",
            "skillName": skill_name,
            "linearIssueId": issue_id,
            "diffPath": diff_path
        })

        trigger_path.rename(archive_dir / trigger_path.name)

        print(
            f"Approved skill update for '{skill_name}' is ready.\n"
            f"Apply manually: git apply {diff_path}",
            file=sys.stderr
        )

    elif action == "rejected":
        log_to_history(repo_root, {
            "event": "skill_update_rejected",
            "status": "rejected",
            "linearIssueId": issue_id,
            "skillName": skill_name,
            "reason": trigger.get("rejectionReason", "No reason provided")
        })

        try_write_telemetry(repo_root, {
            "event": "skill_update_rejected",
            "skillName": skill_name,
            "linearIssueId": issue_id
        })

        trigger_path.rename(archive_dir / trigger_path.name)

    sys.exit(0)


if __name__ == "__main__":
    main()
