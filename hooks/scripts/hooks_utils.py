"""
hooks_utils.py
SAGE Framework — Shared hook utilities
Used by all hook scripts in .cursor/hooks/scripts/

Per-phase architecture: phase runtime (currentStep, stepStatus, batches,
etc.) lives in phase-{N}/phase-manifest.json. The root session-manifest.md
holds definitions, sessionState, and kickoff metadata only.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class NoSessionError(Exception):
    """No active SAGE session — fail-open is correct."""
    pass


class SessionIntegrityError(Exception):
    """Active session exists but data is invalid — should NOT fail-open."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Repository and session resolution
# ─────────────────────────────────────────────────────────────────────────────

def find_repo_root() -> Path:
    """
    Resolve the workspace repository root.

    Prefers the CURSOR_PROJECT_DIR environment variable set by Cursor when
    invoking plugin hooks (the workspace root, independent of hook CWD).
    Falls back to walking up from cwd until a .git directory is found, so
    direct/test invocations still work.

    Raises NoSessionError if no repo root can be determined.
    """
    project_dir = os.environ.get("CURSOR_PROJECT_DIR")
    if project_dir:
        p = Path(project_dir)
        if p.exists():
            return p
    current = Path.cwd()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise NoSessionError(
        "Could not locate repo root via CURSOR_PROJECT_DIR or .git walk."
    )


def get_session_root(repo_root: Path) -> Path:
    """
    Read the active session root from .sage/sessions/active-session.txt.
    Raises NoSessionError when no active-session.txt exists (fail-open).
    Raises SessionIntegrityError when session ID exists but directory doesn't.
    """
    active_file = repo_root / ".sage" / "sessions" / "active-session.txt"
    if not active_file.exists():
        raise NoSessionError(
            "No active session found — .sage/sessions/active-session.txt does not exist."
        )
    session_id = active_file.read_text(encoding="utf-8").strip()
    if not session_id:
        raise NoSessionError(
            "active-session.txt is empty — no active session."
        )
    if "/" in session_id or "\\" in session_id or ".." in session_id:
        raise SessionIntegrityError(
            f"Session ID contains path separators or traversal: '{session_id}'"
        )
    session_root = (repo_root / ".sage" / "sessions" / session_id).resolve()
    if not str(session_root).startswith(str(repo_root.resolve()) + os.sep):
        raise SessionIntegrityError(
            f"Session root escapes repository boundary: {session_root}"
        )
    if not session_root.exists():
        raise SessionIntegrityError(
            f"Session ID '{session_id}' found in active-session.txt but session "
            f"directory does not exist: {session_root}"
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
    This is the canonical location for phase artifacts, per-phase manifest,
    and per-phase telemetry.
    Does not check existence — callers should verify as needed.
    """
    if not re.match(r'^\d+$', phase_id):
        raise SessionIntegrityError(
            f"Invalid phase ID format: {phase_id!r} — expected numeric only"
        )
    return session_root / f"phase-{phase_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Root manifest reading (definitions + sessionState)
# ─────────────────────────────────────────────────────────────────────────────

def read_manifest(session_root: Path) -> dict:
    """
    Read and parse the session manifest JSON block from session-manifest.md.
    Returns the parsed dict containing header, phase definitions, sessionState,
    pathValidation, and kickoffOutputs. Phase runtime data is NOT in this file —
    use read_phase_runtime() for that.
    Raises SessionIntegrityError if the file exists but JSON is malformed.
    Raises NoSessionError if the manifest file does not exist.
    """
    manifest_path = session_root / "session-manifest.md"
    if not manifest_path.exists():
        raise SessionIntegrityError(
            f"session-manifest.md not found at: {manifest_path}\n"
            "Session directory exists but manifest is missing."
        )

    content = manifest_path.read_text(encoding="utf-8")

    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise SessionIntegrityError(
            "No JSON block found in session-manifest.md. "
            "The manifest must contain a ```json ... ``` block."
        )

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise SessionIntegrityError(
            f"Failed to parse session manifest JSON: {e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Per-phase runtime reading and writing
# ─────────────────────────────────────────────────────────────────────────────

def read_phase_runtime(session_root: Path, phase_id: str) -> dict:
    """
    Read phase runtime from phase-{N}/phase-manifest.json.
    Returns the parsed dict (currentStep, stepStatus, batches, etc.).
    Returns an empty dict if the file does not exist (phase not yet started).
    Raises SessionIntegrityError if the file exists but is malformed JSON.
    """
    phase_dir = get_phase_dir(session_root, phase_id)
    manifest_path = phase_dir / "phase-manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SessionIntegrityError(
            f"Failed to parse phase-manifest.json for phase {phase_id}: {e}"
        )


def write_phase_runtime(
    session_root: Path, phase_id: str, updates: dict[str, object]
) -> None:
    """
    Locked read-modify-write of fields in phase-{N}/phase-manifest.json.
    updates is a dict of {field_path: value} where field_path uses dot notation
    relative to the phase runtime root (e.g. "stepStatus.build", "currentStep").

    Creates the phase directory and manifest file if they don't exist.
    Silently no-ops on any failure.
    """
    try:
        from filelock import FileLock, Timeout

        phase_dir = get_phase_dir(session_root, phase_id)
        phase_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = phase_dir / "phase-manifest.json"
        lock_path = phase_dir / "phase-manifest.lock"
        lock = FileLock(str(lock_path), timeout=10)

        with lock:
            if manifest_path.exists():
                runtime = json.loads(
                    manifest_path.read_text(encoding="utf-8")
                )
            else:
                runtime = {}

            for field_path, value in updates.items():
                keys = field_path.split(".")
                target = runtime
                for key in keys[:-1]:
                    if isinstance(target, list):
                        try:
                            idx = int(key)
                        except ValueError:
                            break
                        if 0 <= idx < len(target):
                            target = target[idx]
                        else:
                            break
                    else:
                        if key not in target or not isinstance(
                            target[key], (dict, list)
                        ):
                            target[key] = {}
                        target = target[key]
                else:
                    last_key = keys[-1]
                    if isinstance(target, list):
                        try:
                            idx = int(last_key)
                        except ValueError:
                            continue
                        if 0 <= idx < len(target):
                            target[idx] = value
                    else:
                        target[last_key] = value

            runtime["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()
            manifest_path.write_text(
                json.dumps(runtime, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    except ImportError:
        pass
    except Exception:
        pass


def increment_rejection_count(session_root: Path, phase_id: str) -> None:
    """
    Increment hookRejectionCount in phase-{N}/phase-manifest.json by 1.
    Called by block() to track rejection frequency.
    Silently no-ops on any failure.
    """
    try:
        from filelock import FileLock, Timeout

        phase_dir = get_phase_dir(session_root, phase_id)
        phase_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = phase_dir / "phase-manifest.json"
        lock_path = phase_dir / "phase-manifest.lock"
        lock = FileLock(str(lock_path), timeout=10)

        with lock:
            if manifest_path.exists():
                runtime = json.loads(
                    manifest_path.read_text(encoding="utf-8")
                )
            else:
                runtime = {}

            current = runtime.get("hookRejectionCount", 0)
            runtime["hookRejectionCount"] = current + 1
            runtime["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()

            manifest_path.write_text(
                json.dumps(runtime, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    except ImportError:
        pass
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Anchored line parsing
# ─────────────────────────────────────────────────────────────────────────────

def find_marker_value(content: str, prefix: str) -> int | None:
    """
    Search for a line matching `<prefix>: <integer>` anchored at start-of-line.
    Returns the integer value, or None if no matching line is found.
    """
    match = re.search(rf"^{re.escape(prefix)}:\s*(\d+)\s*$", content, re.MULTILINE)
    return int(match.group(1)) if match else None


def has_status_marker(content: str, marker: str) -> bool:
    """
    Return True if `marker` appears as a standalone line (anchored at start-of-line).
    Prevents false matches inside narrative text.
    """
    pattern = rf"^{re.escape(marker)}\s*$"
    return bool(re.search(pattern, content, re.MULTILINE))


# ─────────────────────────────────────────────────────────────────────────────
# Gate outcomes
# ─────────────────────────────────────────────────────────────────────────────

def block(message: str, phase_id: str | None = None) -> None:
    """
    Exit with code 1, blocking the tool call.
    Prints the message to stderr so Cursor surfaces it to the developer.
    When phase_id is provided, increments the phase's hookRejectionCount
    in phase-manifest.json before exiting.
    """
    if phase_id:
        try:
            repo_root = find_repo_root()
            session_root = get_session_root(repo_root)
            increment_rejection_count(session_root, phase_id)
        except Exception:
            pass
    print(message, file=sys.stderr)
    sys.exit(1)


def permit() -> None:
    """
    Exit with code 0, allowing the tool call to proceed.
    """
    sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# Root manifest writing (locked read-modify-write)
# ─────────────────────────────────────────────────────────────────────────────

def _replace_manifest_json(manifest_path: Path, manifest: dict) -> None:
    """
    Replace the ```json ... ``` block inside session-manifest.md with
    the serialised manifest dict. Preserves all content outside the block.
    """
    content = manifest_path.read_text(encoding="utf-8")
    new_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    updated = re.sub(
        r"```json\s*\n.*?\n```",
        f"```json\n{new_json}\n```",
        content,
        count=1,
        flags=re.DOTALL,
    )
    manifest_path.write_text(updated, encoding="utf-8")


def write_manifest_field(
    session_root: Path, field_path: str, value
) -> None:
    """
    Locked read-modify-write of a single field in the root manifest JSON block.
    Use for sessionState and definition fields only — phase runtime fields
    should use write_phase_runtime() instead.
    field_path uses dot notation: e.g. "sessionState.foundationVerified"
    Silently no-ops on any failure.
    """
    try:
        from filelock import FileLock, Timeout

        lock_path = session_root / "manifest.lock"
        lock = FileLock(str(lock_path), timeout=10)

        with lock:
            manifest = read_manifest(session_root)

            keys = field_path.split(".")
            target = manifest
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value

            if "header" in manifest:
                manifest["header"]["lastUpdatedAt"] = (
                    datetime.now(timezone.utc).isoformat()
                )

            manifest_path = session_root / "session-manifest.md"
            _replace_manifest_json(manifest_path, manifest)

    except ImportError:
        pass
    except Timeout:
        pass
    except Exception:
        pass


def write_manifest_fields(
    session_root: Path, updates: dict[str, object]
) -> None:
    """
    Locked batch update of multiple fields in the root manifest.
    Use for sessionState and definition fields only — phase runtime fields
    should use write_phase_runtime() instead.
    updates is a dict of {field_path: value} where field_path uses dot notation.
    """
    try:
        from filelock import FileLock, Timeout

        lock_path = session_root / "manifest.lock"
        lock = FileLock(str(lock_path), timeout=10)

        with lock:
            manifest = read_manifest(session_root)

            for field_path, value in updates.items():
                keys = field_path.split(".")
                target = manifest
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value

            if "header" in manifest:
                manifest["header"]["lastUpdatedAt"] = (
                    datetime.now(timezone.utc).isoformat()
                )

            manifest_path = session_root / "session-manifest.md"
            _replace_manifest_json(manifest_path, manifest)

    except ImportError:
        pass
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry
# ─────────────────────────────────────────────────────────────────────────────

def write_telemetry_event(
    session_root: Path, event: dict, phase_id: str | None = None
) -> None:
    """
    Append a structured event to the appropriate workflow-telemetry.jsonl.
    When phase_id is provided, writes to phase-{N}/workflow-telemetry.jsonl.
    When phase_id is None, writes to the session-root telemetry file
    (for session-level events like kickoff).
    Silently no-ops on any write failure — telemetry must never affect gates.
    """
    try:
        if phase_id:
            phase_dir = get_phase_dir(session_root, phase_id)
            phase_dir.mkdir(parents=True, exist_ok=True)
            telemetry_path = phase_dir / "workflow-telemetry.jsonl"
        else:
            telemetry_path = session_root / "workflow-telemetry.jsonl"

        event_with_ts = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event
        }
        with open(telemetry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_with_ts) + "\n")
    except Exception:
        pass
