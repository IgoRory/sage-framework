"""
prd_telemetry_append.py
Append one PRD interview telemetry JSON object to the path in
.sage/workflow-config.json → prd.telemetryFile (default .sage/prd-interview-telemetry.jsonl).

Usage:
  python prd_telemetry_append.py '{"event":"prd_preflight",...}'
  echo '{"event":"prd_preflight"}' | python prd_telemetry_append.py

This utility does not block workflows. Failures are silent (exit 0), matching
telemetry_logger.py behaviour.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_TELEMETRY_REL = ".sage/prd-interview-telemetry.jsonl"


def find_repo_root() -> Optional[Path]:
    project_dir = os.environ.get("CURSOR_PROJECT_DIR")
    if project_dir:
        p = Path(project_dir)
        if p.exists():
            return p
    current = Path.cwd()
    for _ in range(12):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def resolve_telemetry_path(repo_root: Path) -> Path:
    cfg = repo_root / ".sage" / "workflow-config.json"
    rel = DEFAULT_TELEMETRY_REL
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            prd = data.get("prd") or {}
            rel = prd.get("telemetryFile") or DEFAULT_TELEMETRY_REL
        except Exception:
            pass
    resolved = (repo_root / rel).resolve()
    if not str(resolved).startswith(str(repo_root.resolve()) + os.sep):
        resolved = repo_root / DEFAULT_TELEMETRY_REL
    return resolved


def main() -> None:
    try:
        repo_root = find_repo_root()
        if repo_root is None:
            return

        payload = ""
        if len(sys.argv) >= 2:
            payload = sys.argv[1].strip()
        else:
            payload = sys.stdin.read().strip()

        if not payload:
            return

        record = json.loads(payload)
        if "timestamp" not in record:
            record["timestamp"] = datetime.now(timezone.utc).isoformat()

        target = resolve_telemetry_path(repo_root)
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
