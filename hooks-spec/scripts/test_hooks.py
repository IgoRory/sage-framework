"""
test_hooks.py
SAGE Framework — Hook verification tests (per-phase manifest architecture)

Each test creates an isolated temp directory with sample root manifest,
per-phase phase-manifest.json, and artifact files. Sets env vars, invokes
hook scripts as subprocess with JSON on stdin, and asserts exit code.

Coverage:
- All 13 blocking gates
- 3 non-blocking hooks (manifest-step-writer, telemetry-logger, linear-status-sync)
- Typed exception behavior (NoSessionError → permit, SessionIntegrityError → block)
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

SCRIPTS_DIR = Path(__file__).parent


def _create_session_structure(
    tmp: Path,
    manifest_json: dict,
    phase_id: str = "1",
    phase_runtime: dict | None = None,
) -> Path:
    """Create a minimal session directory structure for testing."""
    sage_dir = tmp / ".sage" / "sessions"
    session_id = "TEST-SESSION"
    session_root = sage_dir / session_id
    phase_dir = session_root / f"phase-{phase_id}"

    sage_dir.mkdir(parents=True)
    session_root.mkdir()
    phase_dir.mkdir()

    (sage_dir / "active-session.txt").write_text(session_id, encoding="utf-8")

    manifest_md = f"# Session Manifest\n\n```json\n{json.dumps(manifest_json, indent=2)}\n```\n"
    (session_root / "session-manifest.md").write_text(manifest_md, encoding="utf-8")

    if phase_runtime is not None:
        (phase_dir / "phase-manifest.json").write_text(
            json.dumps(phase_runtime, indent=2), encoding="utf-8"
        )

    (tmp / ".git").mkdir()

    return session_root


def _base_manifest(phase_id: str = "1", phase_type: str = "foundation") -> dict:
    """Root manifest with definitions and sessionState only — no runtime."""
    return {
        "header": {"sessionId": "TEST-SESSION", "lastUpdatedAt": "2026-01-01T00:00:00Z"},
        "phases": {
            phase_id: {
                "definition": {
                    "phaseType": phase_type,
                    "requiredReferences": [],
                    "linearIssueId": "PROF-99",
                }
            }
        },
        "sessionState": {"foundationVerified": False}
    }


def _base_phase_runtime(current_step: str = "dev-interview", **overrides) -> dict:
    """Per-phase runtime for phase-manifest.json."""
    runtime = {
        "currentStep": current_step,
        "buildMode": "autonomous",
        "validationConfirmed": False,
        "stepStatus": {},
        "stepTimestamps": {},
        "batches": [],
        "hookRejectionCount": 0,
        "linearIssueStatus": "Pending Approval",
        "startedAt": None,
        "completedAt": None,
    }
    runtime.update(overrides)
    return runtime


def _run_hook(
    script_name: str,
    stdin_data: dict,
    cwd: Path,
    phase_id: str = "1",
    env_overrides: dict | None = None,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SAGE_PHASE_ID"] = phase_id
    if env_overrides:
        env.update(env_overrides)
    script_path = SCRIPTS_DIR / script_name
    return subprocess.run(
        ["python", str(script_path)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=10,
    )


# ─────────────────────────────────────────────────────────────────────────────
# plan_mode_enforcer: S1 write restrictions
# ─────────────────────────────────────────────────────────────────────────────

def test_plan_mode_enforcer_blocks_arbitrary_write():
    """Write to an arbitrary file during S1 should be blocked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview"),
        )
        result = _run_hook("plan_mode_enforcer.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "some-file.ts")}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_plan_mode_enforcer_allows_summary_write():
    """Write to the dev-interview-summary during S1 should be permitted."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview"),
        )
        summary_path = session_root / "phase-1" / "phase-1-dev-interview-summary.md"
        result = _run_hook("plan_mode_enforcer.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(summary_path)}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# manifest_step_gate: step progression enforcement
# ─────────────────────────────────────────────────────────────────────────────

def test_manifest_step_gate_blocks_plan_validation_with_blockers():
    """Plan-validation should block when traceability review has Blocker findings > 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("plan-validation"),
        )
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-traceability-review.md").write_text(
            "# Review\n\nBlocker findings: 2\nMajor findings: 0\n", encoding="utf-8"
        )
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_manifest_step_gate_permits_plan_validation_zero_blockers():
    """Plan-validation should permit when traceability review has Blocker findings: 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("plan-validation"),
        )
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-traceability-review.md").write_text(
            "# Review\n\nBlocker findings: 0\nMajor findings: 1\n", encoding="utf-8"
        )
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# phase_approval_gate: Linear approval check
# ─────────────────────────────────────────────────────────────────────────────

def test_phase_approval_gate_blocks_pending():
    """S1 should block when linearIssueStatus is Pending Approval."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview", linearIssueStatus="Pending Approval"),
        )
        result = _run_hook("phase_approval_gate.py", {
            "tool_name": "read_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_phase_approval_gate_permits_approved():
    """S1 should permit when linearIssueStatus is Approved."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview", linearIssueStatus="Approved"),
        )
        result = _run_hook("phase_approval_gate.py", {
            "tool_name": "read_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# validation_confirmed_gate: developer confirmation
# ─────────────────────────────────────────────────────────────────────────────

def test_validation_confirmed_gate_blocks_unconfirmed():
    """Build should block when validationConfirmed is false."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", validationConfirmed=False),
        )
        result = _run_hook("validation_confirmed_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_validation_confirmed_gate_permits_confirmed():
    """Build should permit when validationConfirmed is true."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", validationConfirmed=True),
        )
        result = _run_hook("validation_confirmed_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# foundation_verified_gate: Dependent phase blocking
# ─────────────────────────────────────────────────────────────────────────────

def test_foundation_verified_gate_blocks_dependent():
    """Dependent phase build should block when foundationVerified is false."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest(phase_type="dependent")
        _create_session_structure(
            tmp_path, manifest,
            phase_runtime=_base_phase_runtime("build"),
        )
        result = _run_hook("foundation_verified_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_foundation_verified_gate_permits_verified():
    """Dependent phase build should permit when foundationVerified is true."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest(phase_type="dependent")
        manifest["sessionState"]["foundationVerified"] = True
        _create_session_structure(
            tmp_path, manifest,
            phase_runtime=_base_phase_runtime("build"),
        )
        result = _run_hook("foundation_verified_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


def test_foundation_verified_gate_permits_foundation_phase():
    """Foundation phase should always permit (gate only applies to Dependent)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(phase_type="foundation"),
            phase_runtime=_base_phase_runtime("build"),
        )
        result = _run_hook("foundation_verified_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# red_results_gate: S5b TDD discipline
# ─────────────────────────────────────────────────────────────────────────────

def test_red_results_gate_blocks_without_red_confirmed():
    """S5b production write should block when red-results.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", buildSubStep="green-refactor"),
        )
        result = _run_hook("red_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "src" / "app.ts")}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_red_results_gate_permits_with_red_confirmed():
    """S5b production write should permit when STATUS: RED CONFIRMED exists."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", buildSubStep="green-refactor"),
        )
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-red-results.md").write_text(
            "# Red Results\n\nSTATUS: RED CONFIRMED\n", encoding="utf-8"
        )
        result = _run_hook("red_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "src" / "app.ts")}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


def test_red_results_gate_permits_test_file_writes():
    """Test file writes should always be permitted even without RED CONFIRMED."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", buildSubStep="green-refactor"),
        )
        result = _run_hook("red_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "src" / "app.spec.ts")}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# tdd_results_gate: anchored pass-marker parsing
# ─────────────────────────────────────────────────────────────────────────────

def test_tdd_results_gate_rejects_narrative_status_pass():
    """STATUS: PASS inside narrative text should NOT match (anchored parsing)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("code-review"),
        )
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-tdd-results.md").write_text(
            "# Results\n\nThe developer mentioned STATUS: PASS in the chat.\n\nSTATUS: FAIL\n",
            encoding="utf-8",
        )
        result = _run_hook("tdd_results_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_tdd_results_gate_permits_anchored_status_pass():
    """STATUS: PASS on its own line should match (anchored parsing)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("code-review"),
        )
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-tdd-results.md").write_text(
            "# Results\n\nSTATUS: PASS\n", encoding="utf-8"
        )
        result = _run_hook("tdd_results_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# code_review_gate: Critical findings check
# ─────────────────────────────────────────────────────────────────────────────

def test_code_review_gate_blocks_missing_review():
    """Security review step should block when code-review.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("security-review"),
        )
        result = _run_hook("code_review_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_code_review_gate_blocks_critical_findings():
    """Security review step should block when code-review has Critical findings > 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("security-review"),
        )
        (session_root / "phase-1" / "phase-1-code-review.md").write_text(
            "# Code Review\n\nCritical findings: 3\nMajor findings: 1\n", encoding="utf-8"
        )
        result = _run_hook("code_review_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_code_review_gate_permits_zero_critical():
    """Security review step should permit when Critical findings: 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("security-review"),
        )
        (session_root / "phase-1" / "phase-1-code-review.md").write_text(
            "# Code Review\n\nCritical findings: 0\nMajor findings: 2\n", encoding="utf-8"
        )
        result = _run_hook("code_review_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# security_review_gate: Critical findings check
# ─────────────────────────────────────────────────────────────────────────────

def test_security_review_gate_blocks_missing_review():
    """Agent testing should block when security-review.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("agent-testing"),
        )
        result = _run_hook("security_review_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_security_review_gate_permits_zero_critical():
    """Agent testing should permit when security-review has Critical findings: 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("agent-testing"),
        )
        (session_root / "phase-1" / "phase-1-security-review.md").write_text(
            "# Security Review\n\nCritical findings: 0\n", encoding="utf-8"
        )
        result = _run_hook("security_review_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# batch_confirmation_gate: Checkpoint mode
# ─────────────────────────────────────────────────────────────────────────────

def test_batch_confirmation_gate_blocks_unconfirmed():
    """Next batch should block when current batch confirmed is false."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime(
                "build",
                buildMode="checkpoint",
                currentBatchId=1,
                batches=[{"id": 1, "label": "Batch 1", "confirmed": False, "taskIds": ["t1"]}],
            ),
        )
        result = _run_hook("batch_confirmation_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_batch_confirmation_gate_permits_confirmed():
    """Next batch should permit when current batch confirmed is true."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime(
                "build",
                buildMode="checkpoint",
                currentBatchId=1,
                batches=[{"id": 1, "label": "Batch 1", "confirmed": True, "taskIds": ["t1"]}],
            ),
        )
        result = _run_hook("batch_confirmation_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


def test_batch_confirmation_gate_permits_autonomous():
    """Autonomous build mode should always permit (no batch gating)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build", buildMode="autonomous"),
        )
        result = _run_hook("batch_confirmation_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# completion_report_stop_gate: stop event gating
# ─────────────────────────────────────────────────────────────────────────────

def test_completion_report_stop_gate_blocks_missing_results():
    """Stop at completion-report should block when test-results.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("completion-report"),
        )
        result = _run_hook("completion_report_stop_gate.py", {
            "reason": "agent_stop"
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_completion_report_stop_gate_permits_passing_results():
    """Stop at completion-report should permit when test-results has STATUS: PASS."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("completion-report"),
        )
        (session_root / "phase-1" / "phase-1-test-results.md").write_text(
            "# Test Results\n\nSTATUS: PASS\n", encoding="utf-8"
        )
        result = _run_hook("completion_report_stop_gate.py", {
            "reason": "agent_stop"
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# protected_manifest_fields_gate: field protection
# ─────────────────────────────────────────────────────────────────────────────

def test_protected_fields_gate_blocks_foundation_verified_change():
    """Changing foundationVerified via write should be blocked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest()
        session_root = _create_session_structure(tmp_path, manifest)

        modified = _base_manifest()
        modified["sessionState"]["foundationVerified"] = True
        proposed = f"# Manifest\n\n```json\n{json.dumps(modified, indent=2)}\n```\n"

        result = _run_hook("protected_manifest_fields_gate.py", {
            "tool_name": "write_file",
            "tool_input": {
                "path": str(session_root / "session-manifest.md"),
                "content": proposed,
            }
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_protected_fields_gate_blocks_runtime_in_root_manifest():
    """Writing runtime fields (validationConfirmed) into root manifest should be blocked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest()
        session_root = _create_session_structure(tmp_path, manifest)

        modified = _base_manifest()
        modified["phases"]["1"]["runtime"] = {"validationConfirmed": True}
        proposed = f"# Manifest\n\n```json\n{json.dumps(modified, indent=2)}\n```\n"

        result = _run_hook("protected_manifest_fields_gate.py", {
            "tool_name": "write_file",
            "tool_input": {
                "path": str(session_root / "session-manifest.md"),
                "content": proposed,
            }
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_protected_fields_gate_permits_non_protected_change():
    """Changing non-protected fields should be permitted."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest()
        session_root = _create_session_structure(tmp_path, manifest)

        modified = _base_manifest()
        modified["sessionState"]["status"] = "build-sprint"
        proposed = f"# Manifest\n\n```json\n{json.dumps(modified, indent=2)}\n```\n"

        result = _run_hook("protected_manifest_fields_gate.py", {
            "tool_name": "write_file",
            "tool_input": {
                "path": str(session_root / "session-manifest.md"),
                "content": proposed,
            }
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# required_references_gate: reference file reading
# ─────────────────────────────────────────────────────────────────────────────

def test_required_references_gate_permits_no_refs():
    """Build should permit when requiredReferences is empty."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build"),
        )
        result = _run_hook("required_references_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# Typed exceptions: NoSessionError → permit, SessionIntegrityError → block
# ─────────────────────────────────────────────────────────────────────────────

def test_no_session_permits():
    """When no active-session.txt exists, gates should fail-open (permit)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".sage" / "sessions").mkdir(parents=True)
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}"


def test_session_integrity_error_blocks():
    """When active-session.txt points to nonexistent dir, gates should block."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / ".git").mkdir()
        sessions_dir = tmp_path / ".sage" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "active-session.txt").write_text("NONEXISTENT", encoding="utf-8")
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file", "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


# ─────────────────────────────────────────────────────────────────────────────
# manifest_step_writer: non-blocking step state updates
# ─────────────────────────────────────────────────────────────────────────────

def test_manifest_step_writer_updates_phase_manifest():
    """Writing a step artifact should update phase-manifest.json."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview"),
        )
        phase_dir = session_root / "phase-1"
        summary_path = phase_dir / "phase-1-dev-interview-summary.md"
        summary_path.write_text("# Summary\n\nContent here.\n", encoding="utf-8")

        result = _run_hook("manifest_step_writer.py", {
            "file_path": str(summary_path)
        }, tmp_path)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"

        phase_manifest = json.loads((phase_dir / "phase-manifest.json").read_text(encoding="utf-8"))
        assert phase_manifest.get("stepStatus", {}).get("dev-interview") == "complete", \
            f"Expected dev-interview complete, got: {phase_manifest.get('stepStatus')}"
        assert phase_manifest.get("currentStep") == "implementation-plan", \
            f"Expected currentStep=implementation-plan, got: {phase_manifest.get('currentStep')}"


def test_manifest_step_writer_updates_telemetry_state():
    """Writing a step artifact should update .telemetry-last-event.json."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("dev-interview"),
        )
        phase_dir = session_root / "phase-1"
        summary_path = phase_dir / "phase-1-dev-interview-summary.md"
        summary_path.write_text("# Summary\n", encoding="utf-8")

        _run_hook("manifest_step_writer.py", {"file_path": str(summary_path)}, tmp_path)

        state_path = session_root / ".telemetry-last-event.json"
        assert state_path.exists(), ".telemetry-last-event.json was not created"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state.get("currentStep") == "implementation-plan", \
            f"Expected currentStep=implementation-plan, got: {state.get('currentStep')}"


# ─────────────────────────────────────────────────────────────────────────────
# telemetry_logger: per-phase telemetry writing
# ─────────────────────────────────────────────────────────────────────────────

def test_telemetry_logger_writes_phase_telemetry():
    """With phase_id set, telemetry should write to phase-{N}/workflow-telemetry.jsonl."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(
            tmp_path, _base_manifest(),
            phase_runtime=_base_phase_runtime("build"),
        )
        result = _run_hook("telemetry_logger.py", {
            "tool_name": "write_file",
            "tool_input": {"path": "/some/file.ts"}
        }, tmp_path, env_overrides={"CURSOR_HOOK_EVENT": "preToolUse"})
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"

        phase_telemetry = session_root / "phase-1" / "workflow-telemetry.jsonl"
        assert phase_telemetry.exists(), "Per-phase telemetry file was not created"
        lines = [l for l in phase_telemetry.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 1, "No telemetry events written"
        event = json.loads(lines[0])
        assert event.get("event") == "preToolUse"
        assert event.get("phaseId") == "1"


def test_telemetry_logger_writes_session_telemetry_no_phase():
    """Without phase_id, telemetry should write to session-root telemetry file."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(tmp_path, _base_manifest())

        env = os.environ.copy()
        env.pop("SAGE_PHASE_ID", None)
        env["CURSOR_HOOK_EVENT"] = "preToolUse"
        script_path = SCRIPTS_DIR / "telemetry_logger.py"
        result = subprocess.run(
            ["python", str(script_path)],
            input=json.dumps({"tool_name": "read_file"}),
            capture_output=True, text=True,
            cwd=str(tmp_path), env=env, timeout=10,
        )
        assert result.returncode == 0

        # No .sage/current-phase.txt → phase_id is None → session-root telemetry
        session_telemetry = session_root / "workflow-telemetry.jsonl"
        assert session_telemetry.exists(), "Session-root telemetry file was not created"


# ─────────────────────────────────────────────────────────────────────────────
# linear_status_sync: graceful no-op without API key
# ─────────────────────────────────────────────────────────────────────────────

def test_linear_status_sync_noop_without_api_key():
    """linear-status-sync should exit 0 immediately when LINEAR_API_KEY is not set."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _create_session_structure(tmp_path, _base_manifest())
        env_overrides = {}
        env = os.environ.copy()
        env.pop("LINEAR_API_KEY", None)
        env["SAGE_PHASE_ID"] = "1"
        script_path = SCRIPTS_DIR / "linear_status_sync.py"
        result = subprocess.run(
            ["python", str(script_path)],
            input=json.dumps({"file_path": "some-file.md"}),
            capture_output=True, text=True,
            cwd=str(tmp_path), env=env, timeout=10,
        )
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        # plan_mode_enforcer
        test_plan_mode_enforcer_blocks_arbitrary_write,
        test_plan_mode_enforcer_allows_summary_write,
        # manifest_step_gate
        test_manifest_step_gate_blocks_plan_validation_with_blockers,
        test_manifest_step_gate_permits_plan_validation_zero_blockers,
        # phase_approval_gate
        test_phase_approval_gate_blocks_pending,
        test_phase_approval_gate_permits_approved,
        # validation_confirmed_gate
        test_validation_confirmed_gate_blocks_unconfirmed,
        test_validation_confirmed_gate_permits_confirmed,
        # foundation_verified_gate
        test_foundation_verified_gate_blocks_dependent,
        test_foundation_verified_gate_permits_verified,
        test_foundation_verified_gate_permits_foundation_phase,
        # red_results_gate
        test_red_results_gate_blocks_without_red_confirmed,
        test_red_results_gate_permits_with_red_confirmed,
        test_red_results_gate_permits_test_file_writes,
        # tdd_results_gate
        test_tdd_results_gate_rejects_narrative_status_pass,
        test_tdd_results_gate_permits_anchored_status_pass,
        # code_review_gate
        test_code_review_gate_blocks_missing_review,
        test_code_review_gate_blocks_critical_findings,
        test_code_review_gate_permits_zero_critical,
        # security_review_gate
        test_security_review_gate_blocks_missing_review,
        test_security_review_gate_permits_zero_critical,
        # batch_confirmation_gate
        test_batch_confirmation_gate_blocks_unconfirmed,
        test_batch_confirmation_gate_permits_confirmed,
        test_batch_confirmation_gate_permits_autonomous,
        # completion_report_stop_gate
        test_completion_report_stop_gate_blocks_missing_results,
        test_completion_report_stop_gate_permits_passing_results,
        # protected_manifest_fields_gate
        test_protected_fields_gate_blocks_foundation_verified_change,
        test_protected_fields_gate_blocks_runtime_in_root_manifest,
        test_protected_fields_gate_permits_non_protected_change,
        # required_references_gate
        test_required_references_gate_permits_no_refs,
        # exception behavior
        test_no_session_permits,
        test_session_integrity_error_blocks,
        # manifest_step_writer (non-blocking)
        test_manifest_step_writer_updates_phase_manifest,
        test_manifest_step_writer_updates_telemetry_state,
        # telemetry_logger (non-blocking)
        test_telemetry_logger_writes_phase_telemetry,
        test_telemetry_logger_writes_session_telemetry_no_phase,
        # linear_status_sync (non-blocking)
        test_linear_status_sync_noop_without_api_key,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            print(f"  PASS  {test_fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test_fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test_fn.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed, {len(tests)} total")
    exit(1 if failed else 0)
