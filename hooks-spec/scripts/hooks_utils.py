"""
hooks_utils.py
SAGE Framework — Shared hook utilities
Used by all hook scripts in .cursor/hooks/scripts/
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# Repository and session resolution
# ─────────────────────────────────────────────────────────────────────────────

def find_repo_root() -> Path:
    """
    Walk up from cwd until a directory containing .git is found.
    Raises RuntimeError if not found within 10 levels.
    """
    current = Path.cwd()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise RuntimeError(
        "HOOK ERROR: Could not locate .git directory. "
        "Ensure this script runs inside the Profitability repository."
    )


def get_session_root(repo_root: Path) -> Path:
    """
    Read the active session root from .sage/sessions/active-session.txt.
    Raises RuntimeError if no active session exists.
    """
    active_file = repo_root / ".sage" / "sessions" / "active-session.txt"
    if not active_file.exists():
        raise RuntimeError(
            "HOOK ERROR: No active session found.\n"
            "Expected: .sage/sessions/active-session.txt\n"
            "Run the session initialiser at kick-off before starting phase work."
        )
    session_id = active_file.read_text(encoding="utf-8").strip()
    if not session_id:
        raise RuntimeError(
            "HOOK ERROR: active-session.txt is empty.\n"
            "Run the session initialiser to populate this file."
        )
    session_root = repo_root / ".sage" / "sessions" / session_id
    if not session_root.exists():
        raise RuntimeError(
            f"HOOK ERROR: Session directory not found: {session_root}\n"
            "The session ID in active-session.txt does not match any session folder."
        )
    return session_root


def get_phase_id() -> str | None:
    """
    Read the current phase ID from the SAGE_PHASE_ID environment variable.
    Returns None if not set (hook not running inside a phase context).
    """
    return os.environ.get("SAGE_PHASE_ID")


def get_phase_dir(session_root: Path, phase_id: str) -> Path:
    """
    Return the phase artifact directory path for a given phase ID.
    Does not check existence — callers should verify as needed.
    """
    return session_root / f"phase-{phase_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Manifest reading
# ─────────────────────────────────────────────────────────────────────────────

def read_manifest(session_root: Path) -> dict:
    """
    Read and parse the session manifest JSON block from session-manifest.md.
    The manifest file contains a markdown document with an embedded JSON block
    delimited by ```json ... ```.
    Returns the parsed dict.
    Raises RuntimeError if the file or JSON block is missing/invalid.
    """
    manifest_path = session_root / "session-manifest.md"
    if not manifest_path.exists():
        raise RuntimeError(
            f"HOOK ERROR: session-manifest.md not found at:\n  {manifest_path}\n"
            "Ensure the phase-splitter has run and the manifest has been generated."
        )

    content = manifest_path.read_text(encoding="utf-8")

    # Extract JSON block
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise RuntimeError(
            "HOOK ERROR: No JSON block found in session-manifest.md.\n"
            "The manifest must contain a ```json ... ``` block."
        )

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"HOOK ERROR: Failed to parse session manifest JSON: {e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Gate outcomes
# ─────────────────────────────────────────────────────────────────────────────

def block(message: str, phase_id: str | None = None) -> None:
    """
    Exit with code 1, blocking the tool call.
    Prints the message to stderr so Cursor surfaces it to the developer.
    """
    print(message, file=sys.stderr)
    sys.exit(1)


def permit() -> None:
    """
    Exit with code 0, allowing the tool call to proceed.
    """
    sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry
# ─────────────────────────────────────────────────────────────────────────────

def write_telemetry_event(session_root: Path, event: dict) -> None:
    """
    Append a structured event to workflow-telemetry.jsonl in session_root.
    Silently no-ops on any write failure — telemetry must never affect gates.
    """
    try:
        telemetry_path = session_root / "workflow-telemetry.jsonl"
        event_with_ts = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event
        }
        with open(telemetry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_with_ts) + "\n")
    except Exception:
        pass  # telemetry failures are silent
