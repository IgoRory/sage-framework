"""
verify_plugin_contract.py
SAGE Framework - Local plugin hook contract verification.

Validates the Cursor plugin manifest and hook package without requiring a live
Cursor process. This is a pre-flight check; live exit-code blocking still needs
manual Cursor verification.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_MANIFEST = REPO_ROOT / ".cursor-plugin" / "plugin.json"
EXPECTED_HOOKS_PATH = "hooks/hooks.json"
HOOKS_CONFIG = REPO_ROOT / EXPECTED_HOOKS_PATH
SCRIPTS_DIR = REPO_ROOT / "hooks" / "scripts"
PLUGIN_ROOT_TOKEN = "${CURSOR_PLUGIN_ROOT}"
SCRIPT_REF_RE = re.compile(
    r"\$\{CURSOR_PLUGIN_ROOT\}[/\\]([^\"'\s]+?\.py)",
    re.IGNORECASE,
)


class ContractResult:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def pass_(self, message: str) -> None:
        print(f"PASS: {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"FAIL: {message}")


def load_json(path: Path, label: str, result: ContractResult) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.fail(f"{label} is missing: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as exc:
        result.fail(f"{label} is invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    return None


def validate_plugin_manifest(result: ContractResult) -> bool:
    manifest = load_json(PLUGIN_MANIFEST, "Plugin manifest", result)
    if manifest is None:
        return False

    result.pass_(".cursor-plugin/plugin.json is valid JSON")
    hooks_value = manifest.get("hooks")
    if hooks_value != EXPECTED_HOOKS_PATH:
        result.fail(
            "Plugin manifest must declare "
            f'"hooks": "{EXPECTED_HOOKS_PATH}" so Cursor can load the hook map'
        )
        return False

    if not HOOKS_CONFIG.exists():
        result.fail(f"Plugin manifest hooks path does not exist: {EXPECTED_HOOKS_PATH}")
        return False

    result.pass_(f"Plugin manifest points to {EXPECTED_HOOKS_PATH}")
    return True


def validate_hooks_config(result: ContractResult) -> list[Path]:
    hooks_config = load_json(HOOKS_CONFIG, "Hook config", result)
    if hooks_config is None:
        return []

    result.pass_("hooks/hooks.json is valid JSON")
    hooks_map = hooks_config.get("hooks")
    if not isinstance(hooks_map, dict) or not hooks_map:
        result.fail('hooks/hooks.json must contain a non-empty "hooks" object')
        return []

    result.pass_("hooks/hooks.json contains a hooks map")
    referenced_scripts: list[Path] = []

    for event_name, hooks in hooks_map.items():
        if not isinstance(hooks, list) or not hooks:
            result.fail(f'Hook event "{event_name}" must be a non-empty list')
            continue

        for index, hook in enumerate(hooks, start=1):
            location = f"{event_name}[{index}]"
            if not isinstance(hook, dict):
                result.fail(f"{location} must be an object")
                continue

            command = hook.get("command")
            if not isinstance(command, str) or not command.strip():
                result.fail(f"{location} must declare a non-empty command")
                continue

            if PLUGIN_ROOT_TOKEN not in command:
                result.fail(f"{location} command must reference {PLUGIN_ROOT_TOKEN}: {command}")
                continue

            match = SCRIPT_REF_RE.search(command)
            if match is None:
                result.fail(f"{location} command must reference a Python script under {PLUGIN_ROOT_TOKEN}")
                continue

            script_path = (REPO_ROOT / match.group(1)).resolve()
            try:
                script_path.relative_to(REPO_ROOT.resolve())
            except ValueError:
                result.fail(f"{location} resolves outside the repo: {script_path}")
                continue

            if not script_path.exists():
                result.fail(f"{location} references missing script: {script_path.relative_to(REPO_ROOT)}")
                continue

            referenced_scripts.append(script_path)
            result.pass_(f"{location} resolves to {script_path.relative_to(REPO_ROOT)}")

    return sorted(set(referenced_scripts))


def import_script(script_path: Path) -> None:
    module_name = f"_sage_contract_{script_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not create import spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def compile_script(script_path: Path) -> None:
    source = script_path.read_text(encoding="utf-8")
    compile(source, str(script_path), "exec")


def validate_scripts(scripts: list[Path], result: ContractResult) -> None:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(SCRIPTS_DIR))
    for script_path in scripts:
        label = str(script_path.relative_to(REPO_ROOT))
        try:
            compile_script(script_path)
            import_script(script_path)
        except Exception as exc:
            result.fail(f"{label} must compile and import successfully: {type(exc).__name__}: {exc}")
            continue
        result.pass_(f"{label} compiles and imports")


def main() -> int:
    result = ContractResult()
    validate_plugin_manifest(result)
    scripts = validate_hooks_config(result)
    validate_scripts(scripts, result)

    if result.failures:
        print(f"\nCONTRACT FAILED: {len(result.failures)} issue(s)")
        return 1

    print("\nCONTRACT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
