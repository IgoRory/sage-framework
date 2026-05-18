"""
sage_state_sync.py
SAGE Framework — Hook: sage-state-sync
Event: afterFileEdit
Blocking: False

Pushes .sage/ session state to the parent feature branch after the
manifest-step-writer updates session-manifest.md. Provides cross-machine
phase visibility in Sprint mode without requiring developers to manually
commit and push session state.

Uses git plumbing commands (hash-object, mktree, commit-tree) to create
a commit on the parent branch without touching the developer's working
tree or index. Retries on push conflicts (up to 2 retries). Silently
no-ops on any failure.
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (
    find_repo_root,
    get_session_root,
    get_phase_id,
    read_manifest,
    NoSessionError,
    SessionIntegrityError,
)

MAX_RETRIES = 2


def _run_git(args: list[str], cwd: str | Path, timeout: int = 10, stdin_data: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        input=stdin_data,
        env=env,
    )


def _is_manifest_edit(file_path: str) -> bool:
    return Path(file_path).name == "session-manifest.md"


def _build_commit_message(phase_id: str | None, manifest: dict) -> str:
    current_step = "unknown"
    prev_step = "unknown"
    if phase_id:
        phase = manifest.get("phases", {}).get(phase_id, {})
        runtime = phase.get("runtime", {})
        current_step = runtime.get("currentStep", "unknown")
        step_status = runtime.get("stepStatus", {})
        completed = [s for s, v in step_status.items() if v == "complete"]
        if completed:
            prev_step = completed[-1]

    return f"[sage-sync] Phase {phase_id or '?'}: {prev_step} complete -> {current_step}"


def _collect_session_files(session_root: Path, phase_id: str | None) -> list[Path]:
    """
    Returns a list of absolute paths for all session files that should
    be synced to the parent branch.
    """
    files: list[Path] = []
    manifest_path = session_root / "session-manifest.md"
    if manifest_path.exists():
        files.append(manifest_path)

    telemetry_path = session_root / "workflow-telemetry.jsonl"
    if telemetry_path.exists():
        files.append(telemetry_path)

    if phase_id:
        phase_dir = session_root / f"phase-{phase_id}"
        if phase_dir.exists():
            for child in phase_dir.rglob("*"):
                if child.is_file():
                    files.append(child)

    return files


def _sync_to_parent(
    repo_root: Path,
    session_root: Path,
    parent_branch: str,
    phase_id: str | None,
    manifest: dict,
) -> None:
    commit_msg = _build_commit_message(phase_id, manifest)
    session_files = _collect_session_files(session_root, phase_id)

    if not session_files:
        return

    for attempt in range(MAX_RETRIES + 1):
        result = _run_git(
            ["fetch", "origin", parent_branch],
            cwd=repo_root,
            timeout=15,
        )
        if result.returncode != 0:
            return

        parent_ref = f"origin/{parent_branch}"
        result = _run_git(["rev-parse", parent_ref], cwd=repo_root)
        if result.returncode != 0:
            return
        parent_sha = result.stdout.strip()

        result = _run_git(["rev-parse", f"{parent_ref}^{{tree}}"], cwd=repo_root)
        if result.returncode != 0:
            return
        base_tree = result.stdout.strip()

        env_with_alt_index = os.environ.copy()
        env_with_alt_index["GIT_TERMINAL_PROMPT"] = "0"
        alt_index = session_root / ".sage-sync-index"
        env_with_alt_index["GIT_INDEX_FILE"] = str(alt_index)

        try:
            subprocess.run(
                ["git", "read-tree", base_tree],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=env_with_alt_index,
            )

            for abs_path in session_files:
                rel_path = abs_path.relative_to(repo_root)
                git_path = str(rel_path).replace("\\", "/")

                result = _run_git(
                    ["hash-object", "-w", str(abs_path)],
                    cwd=repo_root,
                )
                if result.returncode != 0:
                    return
                blob_sha = result.stdout.strip()

                subprocess.run(
                    ["git", "update-index", "--add", "--cacheinfo",
                     f"100644,{blob_sha},{git_path}"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    env=env_with_alt_index,
                )

            result = subprocess.run(
                ["git", "write-tree"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=env_with_alt_index,
            )
            if result.returncode != 0:
                return
            new_tree = result.stdout.strip()

            if new_tree == base_tree:
                return

            result = _run_git(
                ["commit-tree", new_tree, "-p", parent_sha, "-m", commit_msg],
                cwd=repo_root,
            )
            if result.returncode != 0:
                return
            new_commit = result.stdout.strip()

            result = _run_git(
                ["push", "origin", f"{new_commit}:{parent_branch}"],
                cwd=repo_root,
                timeout=15,
            )

            if result.returncode == 0:
                return

            if attempt < MAX_RETRIES and "non-fast-forward" in (result.stderr or ""):
                continue
            else:
                return
        finally:
            if alt_index.exists():
                alt_index.unlink(missing_ok=True)


def main():
    try:
        event_input = json.loads(sys.stdin.read())
    except Exception:
        event_input = {}

    file_path = event_input.get("file_path", "")
    if not file_path or not _is_manifest_edit(file_path):
        sys.exit(0)

    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
        manifest = read_manifest(session_root)
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    parent_branch = manifest.get("sessionState", {}).get("parentBranch")
    if not parent_branch:
        sys.exit(0)

    phase_id = get_phase_id()

    try:
        _sync_to_parent(repo_root, session_root, parent_branch, phase_id, manifest)
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
