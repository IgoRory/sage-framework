"""
skill_update_trigger_watcher.py
SAGE Framework — Hook: skill-update-trigger-watcher
Event: afterFileEdit
Blocking: False

Watches the .skill-update-triggers/ directory. When a new trigger file
appears (written by the Linear webhook receiver after an approval event),
this hook reads the trigger, applies the staged skill diff, commits the
updated SKILL.md, and logs the result to .sage/skill-update-history.jsonl.

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
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from hooks_utils import find_repo_root, write_telemetry_event


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


def apply_skill_update(repo_root: Path, trigger: dict) -> tuple[bool, str]:
    """
    Apply the staged diff to the target SKILL.md.
    Returns (success, message).
    """
    diff_path = repo_root / trigger["diffPath"]
    if not diff_path.exists():
        return False, f"Diff file not found: {diff_path}"

    result = subprocess.run(
        ["git", "apply", str(diff_path)],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, f"git apply failed: {result.stderr.strip()}"

    # Commit the applied diff
    skill_name = trigger.get("skillName", "unknown")
    issue_id = trigger.get("linearIssueId", "unknown")
    commit_msg = (
        f"skill-update({skill_name}): apply approved update from {issue_id}\n\n"
        f"Approved by: {trigger.get('approvedBy', 'unknown')}\n"
        f"Approved at: {trigger.get('approvedAt', 'unknown')}\n"
        f"Diff: {trigger['diffPath']}"
    )

    subprocess.run(["git", "add", f".cursor/skills/{skill_name}/"], cwd=repo_root)
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    if commit_result.returncode != 0:
        return False, f"git commit failed: {commit_result.stderr.strip()}"

    return True, f"Skill update applied and committed for {skill_name}"


def main():
    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    # Only watch edits to the trigger directory
    file_path = event_input.get("file_path", "")
    if ".skill-update-triggers" not in file_path:
        sys.exit(0)

    try:
        repo_root = find_repo_root()
    except RuntimeError:
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

    if action == "approved":
        success, message = apply_skill_update(repo_root, trigger)
        event_type = "skill_update_applied" if success else "skill_update_apply_failed"
        log_to_history(repo_root, {
            "event": event_type,
            "linearIssueId": issue_id,
            "skillName": skill_name,
            "success": success,
            "message": message
        })

        # Try to get session root for telemetry
        try:
            active_file = repo_root / ".sage" / "sessions" / "active-session.txt"
            if active_file.exists():
                session_id = active_file.read_text().strip()
                session_root = repo_root / ".sage" / "sessions" / session_id
                write_telemetry_event(session_root, {
                    "event": event_type,
                    "skillName": skill_name,
                    "linearIssueId": issue_id,
                    "success": success,
                    "message": message
                })
        except Exception:
            pass

        # Archive the trigger file
        archive_dir = repo_root / ".skill-update-triggers" / "processed"
        archive_dir.mkdir(exist_ok=True)
        trigger_path.rename(archive_dir / trigger_path.name)

    elif action == "rejected":
        log_to_history(repo_root, {
            "event": "skill_update_rejected",
            "linearIssueId": issue_id,
            "skillName": skill_name,
            "reason": trigger.get("rejectionReason", "No reason provided")
        })
        trigger_path.rename(
            repo_root / ".skill-update-triggers" / "processed" / trigger_path.name
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
