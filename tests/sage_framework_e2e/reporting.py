"""Structured reporting for SAGE framework E2E scenarios."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Check:
    name: str
    status: str
    evidence: str


@dataclass
class EvidenceReport:
    scenario: str
    checks: list[Check] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, name: str, status: str, evidence: str) -> None:
        self.checks.append(Check(name=name, status=status, evidence=evidence))

    def pass_(self, name: str, evidence: str) -> None:
        self.add(name, "PASS", evidence)

    def fail(self, name: str, evidence: str) -> None:
        self.add(name, "FAIL", evidence)

    def blocked(self, name: str, evidence: str) -> None:
        self.add(name, "BLOCKED", evidence)

    @property
    def verdict(self) -> str:
        statuses = {check.status for check in self.checks}
        if "FAIL" in statuses:
            return "FAIL"
        if "BLOCKED" in statuses:
            return "BLOCKED"
        return "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "verdict": self.verdict,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
            "checks": [check.__dict__ for check in self.checks],
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def render_markdown(self) -> str:
        lines = [
            f"## Scenario: {self.scenario}",
            "",
            f"- verdict: {self.verdict}",
        ]
        for key, value in self.metadata.items():
            lines.append(f"- {key}: `{value}`")
        lines.extend(["", "| Check | Status | Evidence |", "|---|---|---|"])
        for check in self.checks:
            evidence = check.evidence.replace("\n", "<br>")
            lines.append(f"| {check.name} | {check.status} | {evidence} |")
        return "\n".join(lines)
