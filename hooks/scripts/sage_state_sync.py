"""
sage_state_sync.py
SAGE Framework — Hook: sage-state-sync
Event: afterFileEdit
Blocking: False

Pushes the current phase directory to the parent feature branch after any
phase file is written (phase-manifest.json, telemetry, or phase artifacts).
Provides cross-machine phase visibility in Sprint mode.

Per-phase architecture: each phase writes only to its own phase-{N}/
directory. No manifest merge or telemetry union is needed because each
worktree owns a unique phase directory. The root manifest is rarely
modified and is pushed at kickoff by phase-splitter.

Uses git plumbing commands (hash-object, read-tree, update-index,
write-tree, commit-tree) with an alternate index file to create a commit
on the parent branch without touching the developer's working tree or
index. Retries on push conflicts (up to 3 retries). Silently no-ops on
any failure.
"""

import sys
import json
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (
    find_repo_root,
    get_session_root,
    get_phase_id,
    get_phase_dir,
    read_manifest,
    read_phase_runtime,
    NoSessionError,
    SessionIntegrityError,
)

MAX_RETRIES = 3


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


def _is_phase_file(file_path: str, session_root: Path, phase_id: str) -> bool:
    """Return True if the edited file is inside the current phase directory."""
    phase_dir = get_phase_dir(session_root, phase_id)
    try:
        Path(file_path).resolve().relative_to(phase_dir.resolve())
        return True
    except ValueError:
        pass
    normalized = str(Path(file_path)).replace("\\", "/")
    return f"phase-{phase_id}/" in normalized


def _build_commit_message(phase_id: str, runtime: dict) -> str:
    current_step = runtime.get("currentStep", "unknown")
    step_status = runtime.get("stepStatus", {})
    completed = [s for s, v in step_status.items() if v == "complete"]
    prev_step = completed[-1] if completed else "unknown"
    return f"[sage-sync] Phase {phase_id}: {prev_step} complete -> {current_step}"


def _collect_phase_files(session_root: Path, phase_id: str) -> list[Path]:
    """Returns all files in the phase directory."""
    phase_dir = get_phase_dir(session_root, phase_id)
    if not phase_dir.exists():
        return []
    return [child for child in phase_dir.rglob("*") if child.is_file() and not child.is_symlink()]


def _sync_to_parent(
    repo_root: Path,
    session_root: Path,
    parent_branch: str,
    phase_id: str,
    runtime: dict,
) -> None:
    commit_msg = _build_commit_message(phase_id, runtime)
    phase_files = _collect_phase_files(session_root, phase_id)

    if not phase_files:
        return

    alt_index = session_root / ".sage-sync-index"

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
        env_with_alt_index["GIT_INDEX_FILE"] = str(alt_index)

        try:
            rt_result = subprocess.run(
                ["git", "read-tree", base_tree],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=env_with_alt_index,
            )
            if rt_result.returncode != 0:
                return

            for abs_path in phase_files:
                rel_path = abs_path.relative_to(repo_root)
                git_path = str(rel_path).replace("\\", "/")

                result = _run_git(
                    ["hash-object", "-w", str(abs_path)],
                    cwd=repo_root,
                )
                if result.returncode != 0:
                    return
                blob_sha = result.stdout.strip()

                ui_result = subprocess.run(
                    ["git", "update-index", "--add", "--cacheinfo",
                     f"100644,{blob_sha},{git_path}"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    env=env_with_alt_index,
                )
                if ui_result.returncode != 0:
                    return

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
    if not file_path:
        sys.exit(0)

    try:
        repo_root = find_repo_root()
        session_root = get_session_root(repo_root)
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    phase_id = get_phase_id()
    if not phase_id:
        sys.exit(0)

    if not _is_phase_file(file_path, session_root, phase_id):
        sys.exit(0)

    try:
        manifest = read_manifest(session_root)
    except (NoSessionError, SessionIntegrityError):
        sys.exit(0)

    parent_branch = manifest.get("sessionState", {}).get("parentBranch")
    if not parent_branch:
        sys.exit(0)

    runtime = read_phase_runtime(session_root, phase_id)

    try:
        _sync_to_parent(repo_root, session_root, parent_branch, phase_id, runtime)
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
