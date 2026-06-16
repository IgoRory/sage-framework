#!/usr/bin/env python3
"""
check_tool_drift.py
SAGE Framework — On-demand Cursor tool-name drift checker

Reads workflow telemetry, collects every distinct tool name Cursor has actually
invoked, and diffs it against the shared allowlist in hooks_utils. Reports:

  - DRIFT: observed tool names that no gate or known set recognises. These are
    candidates for a Cursor rename/addition — a gate may now silently fail-open.
  - UNUSED: allowlist entries never observed in telemetry. Candidate dead
    entries (or simply tools not yet exercised in this workspace).

This is a REPORT, not a gate. It never blocks, never edits, never touches the
network or Linear. Exit code is always 0 (2 only on a usage error).

Run it after a Cursor update, or when a gate seems not to be firing:

    python hooks/scripts/check_tool_drift.py [workspace_or_telemetry_path]

With no argument it uses $CURSOR_PROJECT_DIR, then the current directory.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hooks_utils import (  # noqa: E402
    WRITE_TOOLS,
    SHELL_TOOLS,
    SUPPORTED_CURSOR_TOOLS,
    normalize_tool,
)


def _normalize(raw: str) -> str:
    """Normalise a raw tool name the same way hooks_utils.normalize_tool does."""
    return normalize_tool({"tool_name": raw})


def resolve_root(arg: str | None) -> Path:
    """Resolve the search root: explicit arg, else CURSOR_PROJECT_DIR, else cwd."""
    if arg:
        return Path(arg)
    env = os.environ.get("CURSOR_PROJECT_DIR")
    if env:
        return Path(env)
    return Path.cwd()


def find_telemetry_files(root: Path) -> list[Path]:
    """
    Find every workflow-telemetry.jsonl under the root. Accepts either a
    workspace root (searches .sage/sessions/**) or a direct path to a
    telemetry file.
    """
    if root.is_file():
        return [root]
    candidates: list[Path] = []
    sessions_dir = root / ".sage" / "sessions"
    if sessions_dir.is_dir():
        candidates.extend(sessions_dir.glob("**/workflow-telemetry.jsonl"))
    # Also tolerate a workspace that nests product repos one level down.
    candidates.extend(root.glob("**/.sage/sessions/**/workflow-telemetry.jsonl"))
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in candidates:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(p)
    return unique


def collect_observed_tools(files: list[Path]) -> dict[str, str]:
    """
    Scan telemetry files for preToolUse records and collect distinct tool
    names. Returns a mapping of normalised-key -> first raw name seen, so the
    report can show the human-readable Cursor name.
    """
    observed: dict[str, str] = {}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            # telemetry_logger writes current records with "toolName"; tolerate
            # older "tool_name" records so drift checks cover legacy telemetry.
            if rec.get("event") != "preToolUse":
                continue
            raw = rec.get("toolName") or rec.get("tool_name")
            if not raw:
                continue
            key = _normalize(raw)
            observed.setdefault(key, raw)
    return observed


def build_report(observed: dict[str, str]) -> tuple[list[str], list[str]]:
    """Return (drift, unused) — drift raw names, unused normalised keys."""
    drift = sorted(
        raw for key, raw in observed.items() if key not in SUPPORTED_CURSOR_TOOLS
    )
    gate_keys = WRITE_TOOLS | SHELL_TOOLS
    unused = sorted(key for key in gate_keys if key not in observed)
    return drift, unused


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report Cursor tool-name drift from SAGE telemetry "
                    "(report-only; never blocks or edits).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Workspace root or a workflow-telemetry.jsonl file. "
             "Defaults to $CURSOR_PROJECT_DIR, then the current directory.",
    )
    args = parser.parse_args(argv)

    root = resolve_root(args.path)
    if not root.exists():
        print(f"check_tool_drift: path does not exist: {root}")
        return 0

    files = find_telemetry_files(root)
    print("SAGE tool-name drift report")
    print(f"  root:            {root}")
    print(f"  telemetry files: {len(files)}")

    if not files:
        print("  (no telemetry found — nothing to check)")
        return 0

    observed = collect_observed_tools(files)
    print(f"  distinct tools observed (preToolUse): {len(observed)}")
    if observed:
        for key in sorted(observed):
            print(f"    - {observed[key]}")

    drift, unused = build_report(observed)

    print("")
    if drift:
        print("DRIFT - observed tool names not in the shared allowlist:")
        for raw in drift:
            print(f"    ! {raw}")
        print("  Action: if these are real write/shell tools, add their "
              "normalised key to WRITE_TOOLS/SHELL_TOOLS in hooks_utils.py;")
        print("          otherwise add their key to SUPPORTED_CURSOR_TOOLS there.")
    else:
        print("DRIFT - none. All observed tools are recognised.")

    print("")
    if unused:
        print("UNUSED - gate allowlist entries never observed in telemetry:")
        for key in unused:
            print(f"    ? {key}")
        print("  Note: may simply be unexercised in this workspace, not "
              "necessarily dead.")
    else:
        print("UNUSED - none. Every gate allowlist entry has been observed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
