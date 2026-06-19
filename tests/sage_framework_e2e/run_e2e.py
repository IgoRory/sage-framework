"""SAGE framework E2E runner."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.sage_framework_e2e.reporting import EvidenceReport  # noqa: E402
from tests.sage_framework_e2e.scenarios import agent_behavior  # noqa: E402
from tests.sage_framework_e2e.scenarios import blocking_contract  # noqa: E402
from tests.sage_framework_e2e.scenarios import red_results_gate  # noqa: E402


def _run_command(name: str, command: list[str]) -> EvidenceReport:
    report = EvidenceReport(name)
    result = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    if result.returncode == 0:
        report.pass_("command", output or f"exit={result.returncode}")
    else:
        report.fail("command", output or f"exit={result.returncode}")
    report.metadata["command"] = " ".join(command)
    return report


def run_local_checks() -> list[EvidenceReport]:
    return [
        _run_command("local_hook_tests", [sys.executable, "hooks/scripts/test_hooks.py"]),
        _run_command(
            "plugin_contract",
            [sys.executable, "hooks/scripts/verify_plugin_contract.py"],
        ),
    ]


def print_reports(reports: list[EvidenceReport]) -> int:
    exit_code = 0
    for report in reports:
        print(report.render_markdown())
        print()
        if report.verdict != "PASS":
            exit_code = 1
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAGE framework E2E scenarios.")
    parser.add_argument(
        "--scenario",
        choices=[
            "smoke",
            "local",
            "blocking-contract",
            "red-results",
            "agent-red-results",
        ],
        default="smoke",
    )
    parser.add_argument(
        "--mode",
        choices=["prepare", "validate", "restore"],
        default="prepare",
        help="Mode for agent-red-results.",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=REPO_ROOT.parent,
        help="Workspace containing sage-framework and sage-sessions.",
    )
    parser.add_argument("--session-id", help="Fixture session ID for validate/restore.")
    parser.add_argument("--report-json", type=Path, help="Optional JSON report path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    reports: list[EvidenceReport] = []

    if args.scenario in {"smoke", "local"}:
        reports.extend(run_local_checks())

    if args.scenario in {"smoke", "blocking-contract"}:
        reports.append(blocking_contract.run(REPO_ROOT))

    if args.scenario in {"smoke", "red-results"}:
        reports.append(red_results_gate.run())

    if args.scenario == "agent-red-results":
        workspace_root = args.workspace_root.resolve()
        if args.mode == "prepare":
            reports.append(agent_behavior.prepare(workspace_root))
        else:
            if not args.session_id:
                print("--session-id is required for validate/restore", file=sys.stderr)
                return 2
            if args.mode == "validate":
                reports.append(agent_behavior.validate(workspace_root, args.session_id))
            elif args.mode == "restore":
                reports.append(agent_behavior.restore(workspace_root, args.session_id))

    if args.report_json:
        combined = EvidenceReport("combined")
        combined.metadata["report_count"] = len(reports)
        for report in reports:
            combined.add(report.scenario, report.verdict, report.render_markdown())
        combined.write_json(args.report_json)

    return print_reports(reports)


if __name__ == "__main__":
    sys.exit(main())
