"""Fixture session helpers for SAGE framework E2E scenarios."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def timestamp_session_id(prefix: str = "sage-e2e") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}"


def base_manifest(session_id: str, phase_id: str = "1") -> dict:
    return {
        "header": {
            "sessionId": session_id,
            "lastUpdatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "phases": {
            phase_id: {
                "definition": {
                    "phaseType": "foundation",
                    "requiredReferences": [],
                    "linearIssueId": "PROF-512",
                }
            }
        },
        "sessionState": {"foundationVerified": True},
    }


def base_phase_runtime(**overrides: object) -> dict:
    runtime = {
        "currentStep": "build",
        "buildSubStep": "green-refactor",
        "buildMode": "autonomous",
        "validationConfirmed": True,
        "stepStatus": {},
        "stepTimestamps": {},
        "batches": [],
        "hookRejectionCount": 0,
        "linearIssueStatus": "Approved",
        "startedAt": None,
        "completedAt": None,
    }
    runtime.update(overrides)
    return runtime


@dataclass
class FixtureSession:
    workspace_root: Path
    repo_root: Path
    session_store: Path
    session_id: str
    phase_id: str = "1"
    original_active_session: str | None = None

    @property
    def sessions_dir(self) -> Path:
        return self.session_store / "sessions"

    @property
    def active_session_file(self) -> Path:
        return self.sessions_dir / "active-session.txt"

    @property
    def session_root(self) -> Path:
        return self.sessions_dir / self.session_id

    @property
    def phase_dir(self) -> Path:
        return self.session_root / f"phase-{self.phase_id}"

    @property
    def red_results_path(self) -> Path:
        return self.phase_dir / f"phase-{self.phase_id}-red-results.md"

    def create(self, activate: bool = True) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.phase_dir.mkdir(parents=True, exist_ok=True)

        if self.active_session_file.exists():
            self.original_active_session = self.active_session_file.read_text(
                encoding="utf-8"
            ).strip()
        else:
            self.original_active_session = None

        manifest = base_manifest(self.session_id, self.phase_id)
        manifest_text = (
            "# Session Manifest\n\n"
            f"```json\n{json.dumps(manifest, indent=2)}\n```\n"
        )
        (self.session_root / "session-manifest.md").write_text(
            manifest_text, encoding="utf-8"
        )
        (self.phase_dir / "phase-manifest.json").write_text(
            json.dumps(base_phase_runtime(), indent=2), encoding="utf-8"
        )
        (self.session_root / "original-active-session.txt").write_text(
            self.original_active_session or "", encoding="utf-8"
        )

        if activate:
            self.active_session_file.write_text(self.session_id, encoding="utf-8")

    def restore_active_session(self) -> None:
        if self.original_active_session:
            self.active_session_file.write_text(
                self.original_active_session, encoding="utf-8"
            )
        elif self.active_session_file.exists():
            self.active_session_file.unlink()


def load_existing_fixture(workspace_root: Path, session_id: str) -> FixtureSession:
    repo_root = workspace_root / "sage-framework"
    session_store = workspace_root / "sage-sessions"
    fixture = FixtureSession(
        workspace_root=workspace_root,
        repo_root=repo_root,
        session_store=session_store,
        session_id=session_id,
    )
    marker = fixture.session_root / "original-active-session.txt"
    if marker.exists():
        value = marker.read_text(encoding="utf-8").strip()
        fixture.original_active_session = value or None
    return fixture
