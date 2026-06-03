"""
skill_update_poller.py
SAGE Framework — Skill Update Polling Script

Polls Linear for skill-update issues that have moved to Approved or Rejected
status and writes trigger files to .skill-update-triggers/ for the
skill_update_trigger_watcher.py hook to process.

Replaces the webhook receiver + ngrok architecture with a zero-infrastructure
polling approach.

Requirements:
  - LINEAR_API_KEY environment variable (same key used by Linear MCP)

Usage:
  python skill_update_poller.py              # One-shot poll
  python skill_update_poller.py --loop 60    # Poll every 60 seconds

Trigger files are written in camelCase to match skill_update_trigger_watcher.py:
{
  "linearIssueId": "PROF-123",
  "skillName": "prd-completeness-check",
  "action": "approved",
  "diffPath": ".skill-update-staging/PROF-123.diff",
  "approvedBy": "approver@example.com",
  "approvedAt": "2026-01-15T09:30:00Z"
}
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


LINEAR_API_URL = "https://api.linear.app/graphql"
SKILL_UPDATE_LABEL = "skill-update"
APPROVED_STATE = "approved"
REJECTED_STATE = "rejected"

POLL_CURSOR_FILENAME = "skill-update-poll-cursor.txt"

GRAPHQL_QUERY = """
query SkillUpdateIssues($labelFilter: String!, $updatedAfter: DateTime) {
  issues(
    filter: {
      labels: { name: { eq: $labelFilter } }
      updatedAt: { gt: $updatedAfter }
    }
    orderBy: updatedAt
    first: 50
  ) {
    nodes {
      id
      identifier
      title
      state { name }
      updatedAt
      assignee { email name }
      labels { nodes { name } }
    }
  }
}
"""


def find_repo_root() -> Optional[Path]:
    project_dir = os.environ.get("CURSOR_PROJECT_DIR")
    if project_dir:
        p = Path(project_dir)
        if p.exists():
            return p
    current = Path.cwd()
    for _ in range(12):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_poll_cursor(sage_dir: Path) -> str:
    cursor_file = sage_dir / POLL_CURSOR_FILENAME
    if cursor_file.exists():
        return cursor_file.read_text(encoding="utf-8").strip()
    return "2020-01-01T00:00:00Z"


def save_poll_cursor(sage_dir: Path, timestamp: str) -> None:
    cursor_file = sage_dir / POLL_CURSOR_FILENAME
    cursor_file.write_text(timestamp + "\n", encoding="utf-8")


def query_linear(api_key: str, updated_after: str) -> list:
    payload = json.dumps({
        "query": GRAPHQL_QUERY,
        "variables": {
            "labelFilter": SKILL_UPDATE_LABEL,
            "updatedAfter": updated_after,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        LINEAR_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Linear API returned {e.code}: {e.read().decode()}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] Linear API request failed: {e}", file=sys.stderr)
        return []

    if "errors" in data:
        print(f"[ERROR] GraphQL errors: {data['errors']}", file=sys.stderr)
        return []

    return data.get("data", {}).get("issues", {}).get("nodes", [])


def classify_state(state_name: str) -> Optional[str]:
    lower = state_name.lower()
    if lower == APPROVED_STATE:
        return "approved"
    if REJECTED_STATE in lower:
        return "rejected"
    return None


def extract_skill_name(title: str) -> str:
    if "\u2014" in title:
        parts = title.split("\u2014")
        if len(parts) >= 2:
            return parts[1].strip()
    if " - " in title:
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[1].strip()
    return "unknown"


def is_already_processed(triggers_dir: Path, identifier: str, action: str) -> bool:
    processed_dir = triggers_dir / "processed"
    trigger_name = f"{identifier}-{action}.json"
    if (triggers_dir / trigger_name).exists():
        return True
    if processed_dir.exists() and (processed_dir / trigger_name).exists():
        return True
    return False


def write_trigger(triggers_dir: Path, issue: dict, action: str) -> Optional[Path]:
    triggers_dir.mkdir(parents=True, exist_ok=True)

    identifier = issue.get("identifier", "unknown")
    title = issue.get("title", "")
    skill_name = extract_skill_name(title)
    assignee = issue.get("assignee") or {}
    actor = assignee.get("email") or assignee.get("name") or "unknown"
    updated_at = issue.get("updatedAt", datetime.now(timezone.utc).isoformat())

    repo_root = triggers_dir.parent
    diff_path = str(
        Path(".skill-update-staging") / f"{identifier}.diff"
    )

    trigger_data = {
        "linearIssueId": identifier,
        "skillName": skill_name,
        "action": action,
        "diffPath": diff_path,
    }

    if action == "approved":
        trigger_data["approvedBy"] = actor
        trigger_data["approvedAt"] = updated_at
    elif action == "rejected":
        trigger_data["rejectedBy"] = actor
        trigger_data["rejectedAt"] = updated_at
        trigger_data["rejectionReason"] = "Read from Linear via MCP"

    filename = f"{identifier}-{action}.json"
    trigger_path = triggers_dir / filename

    with open(trigger_path, "w", encoding="utf-8") as f:
        json.dump(trigger_data, f, indent=2)

    return trigger_path


def poll_once(repo_root: Path) -> int:
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("[ERROR] LINEAR_API_KEY not set.", file=sys.stderr)
        return 0

    sage_dir = repo_root / ".sage"
    sage_dir.mkdir(parents=True, exist_ok=True)

    triggers_dir = repo_root / ".skill-update-triggers"
    updated_after = load_poll_cursor(sage_dir)

    issues = query_linear(api_key, updated_after)
    if not issues:
        return 0

    written = 0
    latest_timestamp = updated_after

    for issue in issues:
        state_name = issue.get("state", {}).get("name", "")
        action = classify_state(state_name)
        if not action:
            continue

        identifier = issue.get("identifier", "unknown")
        if is_already_processed(triggers_dir, identifier, action):
            continue

        path = write_trigger(triggers_dir, issue, action)
        if path:
            print(f"[INFO] Trigger written: {path.name}", file=sys.stderr)
            written += 1

        issue_ts = issue.get("updatedAt", "")
        if issue_ts > latest_timestamp:
            latest_timestamp = issue_ts

    if latest_timestamp > updated_after:
        save_poll_cursor(sage_dir, latest_timestamp)

    return written


def main():
    repo_root = find_repo_root()
    if not repo_root:
        print("[ERROR] Not inside a git repository.", file=sys.stderr)
        sys.exit(1)

    loop_interval = None
    if "--loop" in sys.argv:
        idx = sys.argv.index("--loop")
        if idx + 1 < len(sys.argv):
            try:
                loop_interval = int(sys.argv[idx + 1])
            except ValueError:
                loop_interval = 60
        else:
            loop_interval = 60

    if loop_interval:
        print(f"[INFO] Polling every {loop_interval}s. Press Ctrl+C to stop.", file=sys.stderr)
        try:
            while True:
                count = poll_once(repo_root)
                if count:
                    print(f"[INFO] {count} trigger(s) written.", file=sys.stderr)
                time.sleep(loop_interval)
        except KeyboardInterrupt:
            print("\n[INFO] Polling stopped.", file=sys.stderr)
    else:
        count = poll_once(repo_root)
        if count:
            print(f"[INFO] {count} trigger(s) written.", file=sys.stderr)
        else:
            print("[INFO] No new skill-update events.", file=sys.stderr)


if __name__ == "__main__":
    main()
