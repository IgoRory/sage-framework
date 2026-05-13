"""
test_hooks.py
SAGE Framework — Hook verification tests

Each test creates an isolated temp directory with sample manifest and
artifact files, sets env vars, invokes hook scripts as subprocess with
JSON on stdin, and asserts exit code.

Coverage:
- S1 summary allowance (plan_mode_enforcer)
- Traceability blocker rejection (manifest_step_gate)
- Anchored pass-marker parsing (tdd_results_gate)
- Protected manifest field rejection (protected_manifest_fields_gate)
- Red-results-gate blocking (red_results_gate)
- Typed exception behavior (NoSessionError → permit, SessionIntegrityError → block)
"""

import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def _create_session_structure(tmp: Path, manifest_json: dict, phase_id: str = "1") -> Path:
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

    (tmp / ".git").mkdir()

    return session_root


def _base_manifest(current_step: str = "dev-interview", phase_id: str = "1") -> dict:
    return {
        "header": {"sessionId": "TEST-SESSION", "lastUpdatedAt": "2026-01-01T00:00:00Z"},
        "phases": {
            phase_id: {
                "definition": {"phaseType": "foundation"},
                "runtime": {
                    "currentStep": current_step,
                    "buildMode": "autonomous",
                    "validationConfirmed": False,
                    "stepStatus": {},
                    "batches": []
                }
            }
        },
        "sessionState": {"foundationVerified": False}
    }


def _run_hook(script_name: str, stdin_data: dict, cwd: Path, phase_id: str = "1") -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SAGE_PHASE_ID"] = phase_id
    script_path = SCRIPTS_DIR / script_name
    return subprocess.run(
        ["python", str(script_path)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=10
    )


# ─────────────────────────────────────────────────────────────────────────────
# plan_mode_enforcer: S1 summary allowance
# ─────────────────────────────────────────────────────────────────────────────

def test_plan_mode_enforcer_blocks_arbitrary_write():
    """Write to an arbitrary file during S1 should be blocked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(tmp_path, _base_manifest("dev-interview"))
        result = _run_hook("plan_mode_enforcer.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "some-file.ts")}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_plan_mode_enforcer_allows_summary_write():
    """Write to the dev-interview-summary during S1 should be permitted."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        session_root = _create_session_structure(tmp_path, _base_manifest("dev-interview"))
        phase_dir = session_root / "phase-1"
        summary_path = phase_dir / "phase-1-dev-interview-summary.md"
        result = _run_hook("plan_mode_enforcer.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(summary_path)}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# manifest_step_gate: traceability blocker rejection
# ─────────────────────────────────────────────────────────────────────────────

def test_manifest_step_gate_blocks_plan_validation_with_blockers():
    """Plan-validation should block when traceability review has Blocker findings > 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("plan-validation")
        session_root = _create_session_structure(tmp_path, manifest)
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-traceability-review.md").write_text(
            "# Review\n\nBlocker findings: 2\nMajor findings: 0\n", encoding="utf-8"
        )
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file",
            "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_manifest_step_gate_permits_plan_validation_zero_blockers():
    """Plan-validation should permit when traceability review has Blocker findings: 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("plan-validation")
        session_root = _create_session_structure(tmp_path, manifest)
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-traceability-review.md").write_text(
            "# Review\n\nBlocker findings: 0\nMajor findings: 1\n", encoding="utf-8"
        )
        result = _run_hook("manifest_step_gate.py", {
            "tool_name": "write_file",
            "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# tdd_results_gate: anchored pass-marker parsing
# ─────────────────────────────────────────────────────────────────────────────

def test_tdd_results_gate_rejects_narrative_status_pass():
    """STATUS: PASS inside narrative text should NOT match (anchored parsing)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("code-review")
        session_root = _create_session_structure(tmp_path, manifest)
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-tdd-results.md").write_text(
            "# Results\n\nThe developer mentioned STATUS: PASS in the chat.\n\nSTATUS: FAIL\n",
            encoding="utf-8"
        )
        result = _run_hook("tdd_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_tdd_results_gate_permits_anchored_status_pass():
    """STATUS: PASS on its own line should match (anchored parsing)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("code-review")
        session_root = _create_session_structure(tmp_path, manifest)
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-tdd-results.md").write_text(
            "# Results\n\nSTATUS: PASS\n", encoding="utf-8"
        )
        result = _run_hook("tdd_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {}
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# protected_manifest_fields_gate: field protection
# ─────────────────────────────────────────────────────────────────────────────

def test_protected_fields_gate_blocks_validation_confirmed_change():
    """Changing validationConfirmed via write should be blocked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("build")
        session_root = _create_session_structure(tmp_path, manifest)

        modified_manifest = _base_manifest("build")
        modified_manifest["phases"]["1"]["runtime"]["validationConfirmed"] = True
        proposed_content = f"# Manifest\n\n```json\n{json.dumps(modified_manifest, indent=2)}\n```\n"

        result = _run_hook("protected_manifest_fields_gate.py", {
            "tool_name": "write_file",
            "tool_input": {
                "path": str(session_root / "session-manifest.md"),
                "content": proposed_content
            }
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_protected_fields_gate_permits_non_protected_change():
    """Changing non-protected fields should be permitted."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("build")
        session_root = _create_session_structure(tmp_path, manifest)

        modified_manifest = _base_manifest("build")
        modified_manifest["phases"]["1"]["runtime"]["currentStep"] = "code-review"
        proposed_content = f"# Manifest\n\n```json\n{json.dumps(modified_manifest, indent=2)}\n```\n"

        result = _run_hook("protected_manifest_fields_gate.py", {
            "tool_name": "write_file",
            "tool_input": {
                "path": str(session_root / "session-manifest.md"),
                "content": proposed_content
            }
        }, tmp_path)
        assert result.returncode == 0, f"Expected permit (exit 0), got {result.returncode}. stderr: {result.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# red_results_gate: S5b blocking
# ─────────────────────────────────────────────────────────────────────────────

def test_red_results_gate_blocks_without_red_confirmed():
    """S5b production write should block when red-results.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("build")
        manifest["phases"]["1"]["runtime"]["buildSubStep"] = "green-refactor"
        session_root = _create_session_structure(tmp_path, manifest)
        result = _run_hook("red_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "src" / "app.ts")}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


def test_red_results_gate_permits_with_red_confirmed():
    """S5b production write should permit when STATUS: RED CONFIRMED exists."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = _base_manifest("build")
        manifest["phases"]["1"]["runtime"]["buildSubStep"] = "green-refactor"
        session_root = _create_session_structure(tmp_path, manifest)
        phase_dir = session_root / "phase-1"
        (phase_dir / "phase-1-red-results.md").write_text(
            "# Red Results\n\nSTATUS: RED CONFIRMED\n", encoding="utf-8"
        )
        result = _run_hook("red_results_gate.py", {
            "tool_name": "write_file",
            "tool_input": {"path": str(tmp_path / "src" / "app.ts")}
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
            "tool_name": "write_file",
            "tool_input": {}
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
            "tool_name": "write_file",
            "tool_input": {}
        }, tmp_path)
        assert result.returncode == 1, f"Expected block (exit 1), got {result.returncode}"


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_plan_mode_enforcer_blocks_arbitrary_write,
        test_plan_mode_enforcer_allows_summary_write,
        test_manifest_step_gate_blocks_plan_validation_with_blockers,
        test_manifest_step_gate_permits_plan_validation_zero_blockers,
        test_tdd_results_gate_rejects_narrative_status_pass,
        test_tdd_results_gate_permits_anchored_status_pass,
        test_protected_fields_gate_blocks_validation_confirmed_change,
        test_protected_fields_gate_permits_non_protected_change,
        test_red_results_gate_blocks_without_red_confirmed,
        test_red_results_gate_permits_with_red_confirmed,
        test_no_session_permits,
        test_session_integrity_error_blocks,
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
