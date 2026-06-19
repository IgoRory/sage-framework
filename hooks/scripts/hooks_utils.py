"""
hooks_utils.py
SAGE Framework — Shared hook utilities
Used by all hook scripts in hooks/scripts/

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
# Cursor payload compatibility layer
#
# Single source of truth for Cursor tool-name classification and payload
# field access. Cursor sends hook-facing tool names (Read, Write, Shell, ...)
# and the event name in the stdin payload as `hook_event_name`. Centralising
# here means a Cursor API change is a one-line edit, not a sweep across gates.
#
# Tool names verified against Cursor as of 2026-06-03. When Cursor renames or
# adds tools, update the sets below — run check_tool_drift.py to detect drift.
#
# Names are stored normalised: lower-cased with every non-alphanumeric separator
# stripped, so PascalCase ("StrReplace"), snake_case ("str_replace") and
# kebab-case ("str-replace") all collapse to the same key ("strreplace").
# ─────────────────────────────────────────────────────────────────────────────

# Tools that read file content without mutating it. Includes current Cursor
# names plus legacy hook/telemetry aliases observed before plugin migration.
READ_TOOLS = frozenset({
    "read",
    "readfile",
    "viewfile",
})

# Tools that create or mutate file content. (Write, StrReplace, EditNotebook, Delete)
WRITE_TOOLS = frozenset({
    "write",
    "strreplace",
    "editnotebook",
    "delete",
})

# Tools that execute shell commands. (Shell)
SHELL_TOOLS = frozenset({
    "shell",
})

# Write tools that replace an entire file (as opposed to a partial edit).
# Used where a gate must parse the complete proposed document rather than a diff.
FULL_WRITE_TOOLS = frozenset({
    "write",            # Write — full file contents
})

# Full set of Cursor tool-name keys understood by runtime hook telemetry and
# drift reporting. Stored normalised using normalize_tool's rules.
SUPPORTED_CURSOR_TOOLS = (
    READ_TOOLS
    | WRITE_TOOLS
    | SHELL_TOOLS
    | frozenset({
        "grep",
        "glob",
        "codebasesearch",
        "semanticsearch",
        "search",
        "listmcpresources",
        "fetchmcpresource",
        "callmcptool",
        "websearch",
        "webfetch",
        "task",
        "todowrite",
        "askquestion",
        "switchmode",
        "readlints",
        "generateimage",
        "subagent",
        "applypatch",
    })
)


def normalize_tool(event_input: dict) -> str:
    """
    Normalised tool-name key: lower-cased with all non-alphanumeric separators
    removed. Maps Cursor's PascalCase tool names ("StrReplace") and any
    snake/kebab variants onto a single comparison key ("strreplace").
    """
    raw = event_input.get("tool_name") or event_input.get("toolName") or ""
    return "".join(ch for ch in raw.lower() if ch.isalnum())


def is_read_tool(event_input: dict) -> bool:
    """True when the payload's tool reads file content without mutating it."""
    return normalize_tool(event_input) in READ_TOOLS


def telemetry_record_is_read(record: dict) -> bool:
    """
    True when a telemetry record represents a read-tool invocation.
    Accepts current `toolName` records and legacy `tool_name` variants.
    """
    if record.get("event") != "preToolUse":
        return False
    return is_read_tool({
        "tool_name": record.get("toolName") or record.get("tool_name") or ""
    })


def is_write_tool(event_input: dict) -> bool:
    """True when the payload's tool creates or mutates file content."""
    return normalize_tool(event_input) in WRITE_TOOLS


def is_shell_tool(event_input: dict) -> bool:
    """True when the payload's tool executes a shell command."""
    return normalize_tool(event_input) in SHELL_TOOLS


def is_full_write_tool(event_input: dict) -> bool:
    """
    True when the payload's tool replaces an entire file (full contents),
    as opposed to a partial edit. Callers that parse the complete proposed
    document depend on this distinction.
    """
    return normalize_tool(event_input) in FULL_WRITE_TOOLS


def get_hook_event(event_input: dict) -> str:
    """
    Resolve the hook event name. Cursor provides it as `hook_event_name` in the
    stdin payload; fall back to the CURSOR_HOOK_EVENT env var, then 'unknown'.
    """
    return (
        event_input.get("hook_event_name")
        or os.environ.get("CURSOR_HOOK_EVENT")
        or "unknown"
    )


def get_target_path(event_input: dict) -> str:
    """Extract the target file path from a tool payload, across key variants."""
    ti = event_input.get("tool_input") or {}
    return (
        ti.get("path")
        or ti.get("file_path")
        or ti.get("file")
        or ti.get("target_file")
        or ""
    )


def get_proposed_content(event_input: dict) -> str:
    """Extract proposed file content from a write payload, across key variants."""
    ti = event_input.get("tool_input") or {}
    return (
        ti.get("contents")
        or ti.get("content")
        or ti.get("new_string")
        or ti.get("code_edit")
        or ""
    )


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


class _StdinCapture:
    """Proxy stdin so hook mains consume it normally while we retain a small head."""

    def __init__(self, stream, limit: int = 500):
        self._stream = stream
        self._limit = limit
        self._head = ""
        self._total_length = 0

    def _record(self, data: str) -> None:
        if not isinstance(data, str):
            return
        self._total_length += len(data)
        remaining = self._limit - len(self._head)
        if remaining > 0:
            self._head += data[:remaining]

    def read(self, *args, **kwargs):
        data = self._stream.read(*args, **kwargs)
        self._record(data)
        return data

    def readline(self, *args, **kwargs):
        data = self._stream.readline(*args, **kwargs)
        self._record(data)
        return data

    def readlines(self, *args, **kwargs):
        lines = self._stream.readlines(*args, **kwargs)
        for line in lines:
            self._record(line)
        return lines

    @property
    def payload_head(self) -> str:
        return self._head

    @property
    def payload_truncated(self) -> bool:
        return self._total_length > self._limit

    def __getattr__(self, name):
        return getattr(self._stream, name)


def _write_hook_debug_log(stdin_capture: _StdinCapture, exc: Exception) -> Path | None:
    """
    Best-effort structured debug logging for unexpected hook crashes.
    Returns the debug path when the log write succeeds.
    """
    try:
        repo_root = find_repo_root()
        debug_dir = repo_root / ".sage"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_path = debug_dir / ".hook-debug.log"
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hookScript": Path(sys.argv[0]).name,
            "exceptionType": type(exc).__name__,
            "exceptionMessage": str(exc),
            "stdinPayloadHead": stdin_capture.payload_head,
            "stdinPayloadTruncated": stdin_capture.payload_truncated,
        }
        with open(debug_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return debug_path
    except Exception:
        return None


def run_gate(main_fn) -> None:
    """
    Execute a blocking gate fail-open for unexpected internal errors.

    Deliberate gate outcomes call block()/permit(), which raise SystemExit and
    must pass through unchanged. Only unexpected exceptions are logged and
    converted to permit.
    """
    original_stdin = sys.stdin
    stdin_capture = _StdinCapture(original_stdin)
    sys.stdin = stdin_capture
    try:
        main_fn()
    except SystemExit:
        raise
    except Exception as exc:
        debug_path = _write_hook_debug_log(stdin_capture, exc)
        suffix = f" Details logged to {debug_path}." if debug_path else ""
        print(
            f"HOOK INTERNAL ERROR — {Path(sys.argv[0]).name} crashed unexpectedly; "
            f"permitting tool call.{suffix}",
            file=sys.stderr,
        )
        permit()
    finally:
        sys.stdin = original_stdin


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
