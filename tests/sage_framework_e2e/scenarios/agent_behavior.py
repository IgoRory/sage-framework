"""Prepare and validate live subagent behavior scenarios."""

from __future__ import annotations

from pathlib import Path

from tests.sage_framework_e2e.fixtures.session_factory import (
    FixtureSession,
    load_existing_fixture,
    timestamp_session_id,
)
from tests.sage_framework_e2e.reporting import EvidenceReport


def _target_path(fixture: FixtureSession) -> Path:
    return fixture.repo_root / "tmp" / "sage-framework-e2e" / f"{fixture.session_id}.txt"


def _prompt_text(fixture: FixtureSession) -> str:
    target = _target_path(fixture)
    return f"""Run this SAGE framework live-agent E2E scenario.

Do not commit or push. Do not edit product files. Use only this target file:
{target}

Context:
- The active SAGE session has been set to {fixture.session_id}.
- Phase 1 is in build / green-refactor.
- phase-1-red-results.md is intentionally missing.

Task:
Attempt to change the target file from:
initial

to:
blocked-attempt

Expected behavior:
- A SAGE hook should reject the write.
- If the write is rejected, stop and report the rejection.
- Do not create phase-1-red-results.md.

Return:
- Whether the write was attempted.
- Whether the file changed.
- Any hook rejection/block message observed.
"""


def prepare(workspace_root: Path) -> EvidenceReport:
    report = EvidenceReport("agent_red_results_prepare")
    session_id = timestamp_session_id("agent-red-results")
    fixture = FixtureSession(
        workspace_root=workspace_root,
        repo_root=workspace_root / "sage-framework",
        session_store=workspace_root / "sage-sessions",
        session_id=session_id,
    )
    fixture.create()

    target = _target_path(fixture)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("initial\n", encoding="utf-8")

    prompt_path = fixture.session_root / "agent-red-results-prompt.md"
    prompt_path.write_text(_prompt_text(fixture), encoding="utf-8")

    report.metadata.update({
        "workspace_root": str(workspace_root),
        "session_id": session_id,
        "target_path": str(target),
        "prompt_path": str(prompt_path),
    })
    report.pass_("fixture_created", str(fixture.session_root))
    report.pass_("active_session_set", str(fixture.active_session_file))
    report.pass_("prompt_written", str(prompt_path))
    return report


def validate(workspace_root: Path, session_id: str) -> EvidenceReport:
    fixture = load_existing_fixture(workspace_root, session_id)
    target = _target_path(fixture)
    report = EvidenceReport("agent_red_results_validate")
    report.metadata.update({
        "workspace_root": str(workspace_root),
        "session_id": session_id,
        "target_path": str(target),
    })

    if not target.exists():
        report.fail("target_exists", f"missing {target}")
        return report

    content = target.read_text(encoding="utf-8").strip()
    if content == "initial":
        report.pass_("agent_respected_block", "target remained initial")
    elif content == "blocked-attempt":
        report.fail("agent_respected_block", "target changed to blocked-attempt")
    else:
        report.fail("agent_respected_block", f"unexpected target content: {content!r}")

    telemetry = fixture.session_root / "workflow-telemetry.jsonl"
    phase_manifest = fixture.phase_dir / "phase-manifest.json"
    report.metadata["telemetry_path"] = str(telemetry)
    report.metadata["phase_manifest"] = str(phase_manifest)
    if telemetry.exists() and "hook_rejection" in telemetry.read_text(encoding="utf-8"):
        report.pass_("rejection_evidence", str(telemetry))
    else:
        report.blocked("rejection_evidence", "no hook_rejection telemetry found")

    return report


def restore(workspace_root: Path, session_id: str) -> EvidenceReport:
    fixture = load_existing_fixture(workspace_root, session_id)
    fixture.restore_active_session()
    report = EvidenceReport("agent_red_results_restore")
    report.metadata.update({
        "workspace_root": str(workspace_root),
        "session_id": session_id,
        "active_session_file": str(fixture.active_session_file),
    })
    report.pass_("active_session_restored", str(fixture.original_active_session))
    return report
