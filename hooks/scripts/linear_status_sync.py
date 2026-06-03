"""
linear_status_sync.py
SAGE Framework — Hook: linear-status-sync
Event: afterFileEdit
Blocking: False

Polls Linear for phase issue status changes and syncs linearIssueStatus
to per-phase phase-manifest.json and assignedDeveloper to the root
session manifest. Debounced to poll at most once per configurable
interval (default 60s).

Display-only: does NOT auto-complete phases when Linear status is Done.
Phase completion is exclusively controlled by SAGE gates.

Uses the LINEAR_API_KEY environment variable for authentication.
Non-blocking, silent failure — same contract as all non-gate hooks.
"""

import sys
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (
    find_repo_root,
    get_session_root,
    read_manifest,
    read_phase_runtime,
    write_phase_runtime,
    write_manifest_fields,
    write_telemetry_event,
    NoSessionError,
    SessionIntegrityError,
)


LINEAR_API_URL = "https://api.linear.app/graphql"

GRAPHQL_QUERY = """
query PhaseStatusSync($identifiers: [String!]!) {
  issues(filter: { identifier: { in: $identifiers } }) {
    nodes {
      identifier
      state { name }
      assignee { name }
    }
  }
}
"""


def _load_config(repo_root: Path) -> dict:
    config_path = repo_root / ".sage" / "workflow-config.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _should_poll(session_root: Path, interval_seconds: int) -> bool:
    cursor_file = session_root / "linear-sync-cursor.txt"
    if not cursor_file.exists():
        return True
    try:
        last_poll = float(cursor_file.read_text(encoding="utf-8").strip())
        return (time.time() - last_poll) >= interval_seconds
    except (ValueError, OSError):
        return True


def _save_poll_cursor(session_root: Path) -> None:
    cursor_file = session_root / "linear-sync-cursor.txt"
    try:
        cursor_file.write_text(str(time.time()) + "\n", encoding="utf-8")
    except OSError:
        pass


def _query_linear(api_key: str, identifiers: list[str]) -> list[dict]:
    payload = json.dumps({
        "query": GRAPHQL_QUERY,
        "variables": {"identifiers": identifiers},
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return []

    if "errors" in data:
        return []

    return data.get("data", {}).get("issues", {}).get("nodes", [])


def _sync_phases(session_root: Path, manifest: dict, issues: list[dict]) -> None:
    issues_by_id = {i["identifier"]: i for i in issues}
    phases = manifest.get("phases", {})
    root_updates: dict[str, object] = {}

    for phase_id, phase_data in phases.items():
        definition = phase_data.get("definition", {})
        linear_id = definition.get("linearIssueId")
        if not linear_id or linear_id not in issues_by_id:
            continue

        issue = issues_by_id[linear_id]
        linear_status = issue.get("state", {}).get("name", "")
        linear_assignee = (issue.get("assignee") or {}).get("name")

        runtime = read_phase_runtime(session_root, phase_id)
        manifest_status = runtime.get("linearIssueStatus", "")
        manifest_assignee = definition.get("assignedDeveloper")

        if linear_status and linear_status != manifest_status:
            write_phase_runtime(session_root, phase_id, {
                "linearIssueStatus": linear_status,
            })
            write_telemetry_event(session_root, {
                "event": "linear_status_sync",
                "source": "linear-status-sync",
                "phaseId": phase_id,
                "linearIssueId": linear_id,
                "previousStatus": manifest_status,
                "newStatus": linear_status,
            }, phase_id=phase_id)

        if linear_assignee and linear_assignee != manifest_assignee:
            root_updates[f"phases.{phase_id}.definition.assignedDeveloper"] = linear_assignee

    if root_updates:
        write_manifest_fields(session_root, root_updates)


def main():
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        sys.exit(0)

    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    config = _load_config(repo_root)
    sync_config = config.get("linearSync", {})
    interval = sync_config.get("pollIntervalSeconds", 60)

    if not _should_poll(session_root, interval):
        sys.exit(0)

    try:
        manifest = read_manifest(session_root)
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    phases = manifest.get("phases", {})
    identifiers = [
        p.get("definition", {}).get("linearIssueId")
        for p in phases.values()
        if p.get("definition", {}).get("linearIssueId")
    ]

    if not identifiers:
        sys.exit(0)

    issues = _query_linear(api_key, identifiers)
    if issues:
        _sync_phases(session_root, manifest, issues)

    _save_poll_cursor(session_root)
    sys.exit(0)


if __name__ == "__main__":
    main()
