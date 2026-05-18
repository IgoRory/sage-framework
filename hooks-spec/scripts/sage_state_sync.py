"""
sage_state_sync.py
SAGE Framework — Hook: sage-state-sync
Event: afterFileEdit
Blocking: False

Pushes .sage/ session state to the parent feature branch after the
manifest-step-writer updates session-manifest.md. Provides cross-machine
phase visibility in Sprint mode without requiring developers to manually
commit and push session state.

Uses a temporary worktree to commit to the parent branch without
disturbing the developer's current phase branch. Retries on push
conflicts (up to 2 retries). Silently no-ops on any failure.
"""

import sys
import json
import os
import shutil
import subprocess
import tempfile
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


def _run_git(args: list[str], cwd: str | Path, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _is_manifest_edit(file_path: str) -> bool:
    return Path(file_path).name == "session-manifest.md"


def _get_session_dir_name(session_root: Path) -> str:
    return session_root.name


def _sync_to_parent(
    repo_root: Path,
    session_root: Path,
    parent_branch: str,
    phase_id: str | None,
    manifest: dict,
) -> None:
    """
    Commits the .sage/ session state to the parent feature branch using
    a temporary worktree, then pushes to origin.
    """
    session_dir_name = _get_session_dir_name(session_root)
    session_rel = session_root.relative_to(repo_root)

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

    commit_msg = f"[sage-sync] Phase {phase_id or '?'}: {prev_step} complete -> {current_step}"

    tmp_dir = Path(tempfile.mkdtemp(prefix="sage-sync-"))
    worktree_path = tmp_dir / "sync-worktree"

    try:
        for attempt in range(MAX_RETRIES + 1):
            result = _run_git(
                ["fetch", "origin", parent_branch],
                cwd=repo_root,
                timeout=15,
            )
            if result.returncode != 0:
                return

            if worktree_path.exists():
                _run_git(["worktree", "remove", str(worktree_path), "--force"], cwd=repo_root)
                if worktree_path.exists():
                    shutil.rmtree(worktree_path, ignore_errors=True)

            result = _run_git(
                ["worktree", "add", "--detach", str(worktree_path), f"origin/{parent_branch}"],
                cwd=repo_root,
            )
            if result.returncode != 0:
                return

            wt_session_dir = worktree_path / session_rel
            wt_session_dir.mkdir(parents=True, exist_ok=True)

            manifest_src = session_root / "session-manifest.md"
            telemetry_src = session_root / "workflow-telemetry.jsonl"

            if manifest_src.exists():
                shutil.copy2(str(manifest_src), str(wt_session_dir / "session-manifest.md"))

            if telemetry_src.exists():
                shutil.copy2(str(telemetry_src), str(wt_session_dir / "workflow-telemetry.jsonl"))

            if phase_id:
                phase_dir_name = f"phase-{phase_id}"
                src_phase_dir = session_root / phase_dir_name
                dst_phase_dir = wt_session_dir / phase_dir_name
                if src_phase_dir.exists():
                    if dst_phase_dir.exists():
                        shutil.rmtree(str(dst_phase_dir), ignore_errors=True)
                    shutil.copytree(str(src_phase_dir), str(dst_phase_dir))

            _run_git(
                ["add", str(session_rel)],
                cwd=worktree_path,
            )

            status = _run_git(["status", "--porcelain"], cwd=worktree_path)
            if not status.stdout.strip():
                return

            _run_git(
                ["commit", "-m", commit_msg],
                cwd=worktree_path,
            )

            result = _run_git(
                ["push", "origin", f"HEAD:{parent_branch}"],
                cwd=worktree_path,
                timeout=15,
            )

            if result.returncode == 0:
                return

            if attempt < MAX_RETRIES and "non-fast-forward" in (result.stderr or ""):
                continue
            else:
                return
    finally:
        _run_git(["worktree", "remove", str(worktree_path), "--force"], cwd=repo_root)
        if tmp_dir.exists():
            shutil.rmtree(str(tmp_dir), ignore_errors=True)


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
