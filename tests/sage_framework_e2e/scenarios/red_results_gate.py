"""Mocked-session red-results gate E2E checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.sage_framework_e2e.fixtures.session_factory import FixtureSession
from tests.sage_framework_e2e.reporting import EvidenceReport


def _run_red_gate(repo_root: Path, store_root: Path, target_path: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["CURSOR_PROJECT_DIR"] = str(repo_root)
    env["SAGE_SESSIONS_ROOT"] = str(store_root)
    env["SAGE_PHASE_ID"] = "1"
    payload = {
        "hook_event_name": "preToolUse",
        "tool_name": "Write",
        "tool_input": {
            "path": str(target_path),
            "content": "attempted production content",
        },
    }
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[3] / "hooks" / "scripts" / "red_results_gate.py")],
        input=json.dumps(payload),
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )


def run() -> EvidenceReport:
    report = EvidenceReport("red_results_gate")

    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        repo_root = workspace / "fixture-project"
        store_root = workspace / "sage-sessions"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()
        target = repo_root / "src" / "production.py"
        target.parent.mkdir()
        target.write_text("initial\n", encoding="utf-8")

        fixture = FixtureSession(
            workspace_root=workspace,
            repo_root=repo_root,
            session_store=store_root,
            session_id="TEST-RED-GATE",
        )
        fixture.create()

        report.metadata.update({
            "workspace_root": str(workspace),
            "session_store": str(store_root),
            "target_path": str(target),
        })

        blocked = _run_red_gate(repo_root, store_root, target)
        if blocked.returncode != 0:
            report.pass_("missing_red_results_blocks", f"exit={blocked.returncode}")
        else:
            report.fail("missing_red_results_blocks", "expected non-zero exit")

        target_content = target.read_text(encoding="utf-8")
        if target_content == "initial\n":
            report.pass_("blocked_target_unchanged", "target file remained unchanged")
        else:
            report.fail("blocked_target_unchanged", f"target changed to {target_content!r}")

        telemetry = fixture.session_root / "workflow-telemetry.jsonl"
        if telemetry.exists() and "red-results-gate" in telemetry.read_text(encoding="utf-8"):
            report.pass_("rejection_telemetry", str(telemetry))
        else:
            report.fail("rejection_telemetry", f"missing red-results-gate entry at {telemetry}")

        fixture.red_results_path.write_text("STATUS: RED CONFIRMED\n", encoding="utf-8")
        permitted = _run_red_gate(repo_root, store_root, target)
        if permitted.returncode == 0:
            report.pass_("confirmed_red_results_permits", "exit=0")
        else:
            report.fail(
                "confirmed_red_results_permits",
                f"exit={permitted.returncode}; stderr={permitted.stderr.strip()}",
            )

    return report
