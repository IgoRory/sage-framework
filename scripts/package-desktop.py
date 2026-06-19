#!/usr/bin/env python3
"""
Package the SAGE plugin as a zip for Claude Desktop upload.

Zips the plugin payload from the WORKING TREE (so uncommitted changes are included)
using an explicit allowlist — keeps the zip lean (framework docs/specs excluded) and
correct regardless of commit state. Output: sage.zip in the repo root, unpacking to a
single `sage/` root.

Usage:  python scripts/package-desktop.py
"""

import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PREFIX = "sage"

# Plugin payload only — what the IDE loaders actually read.
INCLUDE_DIRS = ["agents", "skills", "rules", "hooks", "templates",
                ".claude-plugin", ".cursor-plugin"]
INCLUDE_FILES = [".mcp.json", "README.md", "AGENTS.md"]
# Never ship these even if nested under an included dir.
EXCLUDE_PARTS = {"__pycache__", ".git"}


def included(path: Path) -> bool:
    return not (EXCLUDE_PARTS & set(path.parts)) and path.suffix != ".pyc"


def main() -> None:
    out = REPO / "sage.zip"
    if out.exists():
        out.unlink()
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for d in INCLUDE_DIRS:
            base = REPO / d
            if not base.is_dir():
                continue
            for f in base.rglob("*"):
                if f.is_file() and included(f):
                    z.write(f, f"{PREFIX}/{f.relative_to(REPO).as_posix()}")
                    n += 1
        for name in INCLUDE_FILES:
            f = REPO / name
            if f.is_file():
                z.write(f, f"{PREFIX}/{name}")
                n += 1
    print(f"wrote {out.name} ({n} files) — upload via Claude Desktop plugin install")


if __name__ == "__main__":
    main()
