"""Blocking-contract checks for Cursor hook response semantics."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.sage_framework_e2e.reporting import EvidenceReport


def _run_script(repo_root: Path, script_name: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(repo_root / "hooks" / "scripts" / script_name)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=10,
    )


def run(repo_root: Path) -> EvidenceReport:
    report = EvidenceReport("blocking_contract")
    report.metadata["repo_root"] = str(repo_root)

    exit2 = _run_script(repo_root, "intentional_block.py")
    if exit2.returncode == 2:
        report.pass_("exit_2_block_code", "intentional_block.py exited 2")
    else:
        report.fail(
            "exit_2_block_code",
            f"expected 2, got {exit2.returncode}; stderr={exit2.stderr.strip()}",
        )

    exit1 = _run_script(repo_root, "intentional_block_exit1.py")
    if exit1.returncode == 1:
        report.pass_("exit_1_fail_open_control", "intentional_block_exit1.py exited 1")
    else:
        report.fail(
            "exit_1_fail_open_control",
            f"expected 1, got {exit1.returncode}; stderr={exit1.stderr.strip()}",
        )

    deny = _run_script(repo_root, "intentional_block_json_deny.py")
    try:
        payload = json.loads(deny.stdout)
    except json.JSONDecodeError as exc:
        report.fail("json_deny_parse", f"invalid JSON stdout: {exc}")
    else:
        if deny.returncode == 0 and payload.get("permission") == "deny":
            report.pass_("json_deny_contract", "stdout permission=deny with exit 0")
        else:
            report.fail(
                "json_deny_contract",
                f"exit={deny.returncode}, permission={payload.get('permission')!r}",
            )

    return report
