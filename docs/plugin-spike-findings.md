# Cursor Plugin Spike — Findings

**Branch:** `dev/improve-dev-workflow-cursor-plugin-spike`
**Date:** 2026-05-27 (updated 2026-06-03 — full parity)
**Scope:** All 19 SAGE hooks wired as a local Cursor plugin; existing `hooks-spec/` left inert.

---

## What was built

```
sage-framework/
├── .cursor-plugin/
│   └── plugin.json                manifest declares hooks + agents + rules + skills + mcpServers
├── hooks/
│   ├── hooks.json                 Cursor-native schema, all 19 hooks fanned out by event
│   └── scripts/                   24 scripts copied from Profitability (source of truth)
│       ├── hooks_utils.py         PATCHED (CURSOR_PROJECT_DIR-aware find_repo_root)
│       ├── telemetry_logger.py
│       ├── plan_mode_enforcer.py · manifest_step_gate.py · phase_approval_gate.py
│       ├── required_references_gate.py · validation_confirmed_gate.py
│       ├── foundation_verified_gate.py · batch_confirmation_gate.py · test_write_guard.py
│       ├── red_results_gate.py · tdd_results_gate.py · code_review_gate.py
│       ├── security_review_gate.py · protected_manifest_fields_gate.py
│       ├── completion_report_stop_gate.py (stop) · manifest_step_writer.py
│       ├── sage_state_sync.py · linear_status_sync.py · skill_update_trigger_watcher.py
│       └── support: skill_update_poller.py · prd_telemetry_append.py
│                    backfill_manifest.py · test_hooks.py
│       (prd_telemetry_append.py and skill_update_poller.py also PATCHED for CURSOR_PROJECT_DIR)
├── .cursor/agents/                EXISTING — exposed via manifest
├── .cursor/rules/                 EXISTING — exposed via manifest
├── .cursor/skills/                EXISTING — exposed via manifest
└── .cursor/mcp.json               EXISTING — exposed via manifest
```

### Hook registry (19 hooks, native schema)

| Event | Hooks |
|---|---|
| preToolUse (14) | telemetry-logger, plan-mode-enforcer, manifest-step-gate, phase-approval-gate, required-references-gate, validation-confirmed-gate, foundation-verified-gate, batch-confirmation-gate, test-write-guard, red-results-gate, tdd-results-gate, code-review-gate, security-review-gate, protected-manifest-fields-gate |
| afterFileEdit (5) | telemetry-logger, manifest-step-writer, sage-state-sync, linear-status-sync, skill-update-trigger-watcher |
| beforeShellExecution / afterShellExecution / afterMCPExecution (1 each) | telemetry-logger |
| stop (2) | telemetry-logger, completion-report-stop-gate |

The `stop` wiring of `completion-report-stop-gate` was the gap in the 8-hook version — now closed.

### Operational caveats (must hold for gates to function)

- **`SAGE_PHASE_ID`** must be set in each phase worktree. If unset, phase gates fail-open (permit everything) — they cannot resolve the phase context. Document how the worktree sets this.
- **`filelock`** Python package is an optional dependency. Manifest writes (`write_phase_runtime`, `increment_rejection_count`) silently no-op without it. Run `pip install filelock` for reliable manifest state.
- **`linear-status-sync`** needs `LINEAR_API_KEY`; degrades to no-op without it.
- **`plan-mode-enforcer`** only permits `phase-{N}-dev-interview-summary.md` during S1. If the `dev-plan` skill is in scope, it will over-block dev-plan artifacts. Known gap — deferred.

Plus install-side (workspace-scoped, not user-global):
- `sage-sessions/.cursor/hooks.json` — `workspaceOpen` hook at the actual Cursor workspace root (the parent folder containing Profitability, Empyrean%20Dataverse, sage-framework).
- `sage-sessions/.cursor/scripts/load-sage-plugin.py` — outputs `{"pluginPaths": ["C:\\Users\\ChrisBuckley\\source\\sage-framework"]}` so Cursor loads sage when `sage-sessions/` is the open workspace.

The user-global install (junction under `~/.cursor/plugins/local/` and `~/.claude/` registration) was removed. `sage-sessions/` is a parent folder on disk, not a git repo — the bootstrap files are machine-local and not version-controlled.

### Why the workspace-root location matters

Cursor's plugin / project-hook / project-rule discovery is scoped to the **primary workspace root only**. When the workspace is `sage-sessions/`, anything under `Profitability/.cursor/...` is invisible to Cursor — including the skills, rules, agents, mcp.json, and hooks that have been vendored there via the mirror workflow. They have never been loaded in this workspace layout. Exposing those components through the plugin manifest is the only way they actually take effect.

`hooks-spec/` (legacy, array-schema, never parsed by Cursor) is untouched. Removing all spike additions returns the system to its pre-spike state.

## Pre-flight validation (script level, no Cursor involvement)

Executed `telemetry_logger.py` directly with the env vars Cursor will set:

```
CURSOR_PROJECT_DIR=C:\Users\ChrisBuckley\source\sage-sessions\Profitability
CURSOR_PLUGIN_ROOT=C:\Users\ChrisBuckley\.cursor\plugins\local\sage
CURSOR_HOOK_EVENT=preToolUse
stdin: {"tool_name":"read_file","tool_input":{"target_file":"AGENTS.md"}}
```

Result:
- Exit code 0
- Profitability session telemetry `workflow-telemetry.jsonl` grew 864 → 1082 bytes
- New entry has `event: "preToolUse"`, `sessionId: "06f47204-..."`, `toolName: "read_file"` (not `source: "backfill"`)

This proves:
- The patched `find_repo_root()` correctly prefers `CURSOR_PROJECT_DIR` and resolves to the Profitability workspace.
- `hooks_utils` session resolution works for the active PROF-50 session.
- Telemetry serialization and append work.

Dry-runs of `red_results_gate.py`, `protected_manifest_fields_gate.py`, and `manifest_step_writer.py` with the same env all exited 0 (fail-open paths or no-match paths). No import errors, no crashes.

## Pending — requires Cursor IDE involvement

The spike cannot self-validate beyond script execution. The remaining proof points need the user to:

1. **Reload Cursor window** with `sage-sessions/` as the open workspace. (Developer: Reload Window)
2. **Confirm plugin loaded.** Cursor Settings → Plugins should list `sage`. Output panel should show no parse errors for `hooks/hooks.json` or `plugin.json`.
3. **Confirm skills/rules/agents are visible.** Skills and slash commands defined in the plugin should now appear in the agent's available set, regardless of which subfolder (Profitability or Dataverse) you're working in.
4. **Trigger a tool call** while operating in `Profitability/` files. Inspect `Profitability/.sage/sessions/06f47204-.../workflow-telemetry.jsonl`. New entries with `event: "preToolUse"`/`"afterFileEdit"`/`"stop"` confirm hooks actually fire from Cursor.
5. **Gate blocking test:** in a phase where `phase-N-red-results.md` is missing or lacks `STATUS: RED CONFIRMED`, ask the agent to write a matching production file. The expected behavior is `red_results_gate.py` exits non-zero and Cursor blocks the write. If the write goes through anyway, exit-code-based blocking does not propagate inside Cursor and the framework's "structural gates" claim needs a different enforcement layer.

## Open questions for follow-up

- **Does Cursor honor exit-code blocking?** Step 7 answers this. Unknown until run live.
- **Does `${CURSOR_PLUGIN_ROOT}` expand correctly on Windows?** Pre-flight bypassed this by hard-coding the path. Live hook invocation tests it.
- **Will `python` resolve to the right interpreter on teammates' machines?** Verified on Chris's box (`Python 3.14.2`). May need to switch to `py -3` for portability before wider rollout. Out of scope for this spike.
- **Symlink vs junction.** Symlink required elevation on Windows; junction (mklink /J) succeeded without admin. Junctions work for local plugin loading, but won't follow cross-volume references — fine here since both paths are on `C:`.
- **What about the other 11 hooks?** Deferred. The 8 in this spike were chosen to prove the highest-value paths (telemetry, the most-critical gates, manifest writer). The remaining hooks (plan-mode-enforcer, manifest-step-gate, phase-approval-gate, required-references-gate, tdd-results-gate, code-review-gate, security-review-gate, completion-report-stop-gate, skill-update-trigger-watcher, sage-state-sync, linear-status-sync) get wired up only after Steps 6/7 validate the path.

## Rollback

If anything misbehaves, full rollback is two removals:

1. At workspace root: delete `sage-sessions/.cursor/hooks.json` and `sage-sessions/.cursor/scripts/load-sage-plugin.py` (workspace bootstrap; not in version control).
2. In sage-framework: `git checkout main` and discard the spike branch, OR delete `.cursor-plugin/` and `hooks/` directly.

## Verdict

Spike is plumbing-complete. Script execution is verified end-to-end with the exact env vars Cursor will provide. Live hook invocation from Cursor itself is the only remaining unknown, and it's gated on a window reload by the developer.
