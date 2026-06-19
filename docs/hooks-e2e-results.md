# Hooks E2E Results

## Local Contract

- command: `python hooks/scripts/verify_plugin_contract.py`
- status: PASS
- checked_at: 2026-06-16
- notes: Validates plugin manifest hook pointer, hook command resolution, and referenced script compile/import health.

## Session Store Resolution

- steady_state: The SAGE plugin/framework owns hooks, skills, agents, rules, and templates; live session metadata is resolved from an external session store.
- external_layout: `<session-store>/sessions/active-session.txt` and `<session-store>/sessions/<session-id>/...`.
- resolver_priority:
  1. `SAGE_SESSIONS_ROOT` from the process environment when non-blank.
  2. `SAGE_SESSIONS_ROOT` from workspace-level `.env` when non-blank, where the workspace is the active repo's parent directory.
  3. Workspace sibling `sage-sessions` when present next to the active repo.
  4. No resolved store: hooks raise `NoSessionError` and fail open.
- local_setup: Use `<workspace>/.env` or place `sage-sessions` as a sibling directory next to the active repo.
- compatibility: Repo-local `.sage/sessions/active-session.txt` is not an active runtime fallback; project/framework repos should not own live session state.

## Live Cursor Verification

| Check | Status | Evidence |
|---|---|---|
| plugin_loaded | PASS | `verify_plugin_contract.py` CONTRACT PASSED; live `preToolUse` hooks executed during agent tool calls |
| hook_fired | PASS | `red-results-gate` ran on Write; `hookRejectionCount` incremented 0→1 in `phase-1/phase-manifest.json` |
| telemetry_recorded | PARTIAL | `workflow-telemetry.jsonl` received `hook_rejection` event; no `preToolUse` row from `telemetry_logger.py` in this run |
| block_scenario | FAIL | Gate exited 1 and logged rejection, but Write to `sage-framework/tmp/sage-hook-e2e/target.txt` still succeeded (`blocked-attempt-live` written) |
| permit_scenario | PASS | Read of `session-manifest.md` succeeded without rejection telemetry |

Session fixture: `hook-e2e-20260616-1829` (phase 1, `currentStep=build`, `buildSubStep=green-refactor`, no `phase-1-red-results.md`).

Subprocess control (with `SAGE_SESSIONS_ROOT` + `SAGE_PHASE_ID=1`): `red_results_gate.py` exit code 1 as expected.

## Exit-Code Blocking Verdict (live retest after reload — 2026-06-16)

- cursor_honors_exit_code_blocking: **INCONCLUSIVE** (test hooks did not appear to fire; see notes)
- verified_by: live agent Write tool calls in Cursor (Composer), minimal intentional-block hooks prepended to `hooks/hooks.json`
- verified_at: 2026-06-16 (post-reload retest)
- notes: User reloaded Cursor before retest. Agent prepended test hooks to `hooks/hooks.json` and immediately attempted Writes — **no blocking observed for any variant**. No `INTENTIONAL BLOCK` stderr surfaced on tool calls. All three Writes succeeded and files were created on disk. **Likely cause:** `hooks.json` edits made after window reload do not hot-reload; test hooks never executed. Prior E2E (with hooks loaded at reload time) showed product gates *do* fire but exit **1** fail-open. **Definitive exit-2 / JSON-deny blocking test still requires:** prepend test hook → reload Cursor → agent Write attempt.

### Minimal blocking contract retest results

| Test | Hook script | Expected | Observed | File on disk |
|---|---|---|---|---|
| A | `intentional_block.py` (exit **2**) | BLOCK | **PERMIT** (Write succeeded) | `block-contract-test.txt` created, then deleted |
| B | `intentional_block_exit1.py` (exit **1**) | PERMIT (fail-open) | **PERMIT** (Write succeeded) | `block-contract-test-exit1.txt` created, then deleted |
| C | `intentional_block_json_deny.py` (JSON deny, exit 0) | BLOCK | **PERMIT** (Write succeeded) | `block-contract-test-json.txt` created, then deleted |

**Interpretation:** A/B/C all behaved identically (permit) — consistent with **zero test-hook invocations**, not with Cursor ignoring exit 2 while honoring exit 1. Cannot confirm or deny Cursor exit-2 contract from this run alone.

**Recommended `block()` change:** Still **yes, change to `sys.exit(2)`** (or JSON deny) based on Cursor docs + prior live E2E where product gates exited 1, logged rejection, and Write still succeeded. Exit-2 minimal hook retest remains **pending** with reload-after-`hooks.json`-edit workflow.

## Blocking Contract Investigation

Investigated 2026-06-16 after live E2E showed `red_results_gate` telemetry rejection while Write still succeeded.

### Cursor blocking schema (official)

Sources: [Hooks | Cursor Docs](https://cursor.com/docs/hooks), [Third Party Hooks](https://cursor.com/docs/reference/third-party-hooks), [Plugins Reference](https://cursor.com/docs/reference/plugins).

| Mechanism | Contract | SAGE today |
|---|---|---|
| Exit code `0` | Success; parse stdout JSON if present | `permit()` ✓ |
| Exit code `2` | **Block** (equivalent to `permission: "deny"`) | Not used |
| Exit code `1` (or other non-zero) | Hook **failed** — action proceeds (**fail-open**) | `block()` uses `sys.exit(1)` ✗ |
| stdout JSON `{"permission": "deny", ...}` | Block `preToolUse` | Not used by gates |
| `failClosed: true` on hook entry | Block on crash/timeout/invalid JSON | Not set |
| `blocking: true` in hooks.json | **Not a Cursor field** | Only in `hooks-spec/` internal doc format |

Per-hook `hooks.json` fields supported by Cursor: `command` (required), `type`, `timeout`, `loop_limit`, `failClosed`, `matcher`. There is **no** `blocking` metadata field in the Cursor schema.

`preToolUse` output fields: `permission` (`allow` \| `deny`), optional `user_message`, `agent_message`, `updated_input`.

Plugin hooks: declared in plugin manifest `"hooks": "hooks/hooks.json"`, commands should use `${CURSOR_PLUGIN_ROOT}` for script paths. Manifest lives at `.cursor-plugin/plugin.json` (correct for SAGE).

### Current `hooks/hooks.json` gaps

| Item | Status | Impact |
|---|---|---|
| `version: 1` | Missing | Recommended by schema; plugin still loads and hooks fire without it |
| `blocking: true` per entry | N/A | Not part of Cursor format; `hooks-spec/hooks.json` uses a separate internal schema |
| Exit code contract in scripts | **Wrong code** | `hooks_utils.block()` → `sys.exit(1)`; Cursor treats 1 as fail-open |
| JSON deny response | Not implemented | Alternative blocking path per docs |

### `run_gate()` / `block()` analysis

Subprocess tests (isolated temp session store, E2E fixture `hook-e2e-20260616-1829`):

| Test | Exit code | Notes |
|---|---|---|
| `red_results_gate.py` direct | 1 | Blocks logically; stderr + telemetry fire |
| `red_results_gate.py` via shell (`python "${CURSOR_PLUGIN_ROOT}/..."`) | 1 | Shell does not mask exit code |
| `run_gate(main)` + injected `block()` | 1 | `SystemExit` re-raised; **not swallowed** |
| `run_gate(main)` + injected crash | 0 | Unexpected exceptions fail-open (by design) |
| `intentional_block.py` | **2** | Minimal test hook (exit 2) |
| `intentional_block_exit1.py` | 1 | Control for fail-open behavior |

**Conclusion:** `run_gate()` is not the cause. The mismatch is `block()` using exit code **1** against Cursor's documented block code **2**.

### `plugin.json` location

- SAGE manifest: `sage-framework/.cursor-plugin/plugin.json` with `"hooks": "hooks/hooks.json"`.
- Matches [Plugins Reference](https://cursor.com/docs/reference/plugins) layout.
- `verify_plugin_contract.py` passes; live E2E confirms hooks execute from the plugin.
- **Not** a partial-load / wrong-manifest-path issue.

### Tool type / path scope (prior E2E evidence)

| Hypothesis | Evidence |
|---|---|
| Tool type mismatch | Unlikely — gate matched Write, incremented `hookRejectionCount`, emitted `hook_rejection` telemetry |
| Target under `sage-framework/tmp/` | Tested; Write succeeded despite gate exit 1 |
| Repo root vs workspace root | `find_repo_root()` prefers `CURSOR_PROJECT_DIR` (workspace root). Session store resolves via `SAGE_SESSIONS_ROOT` / sibling `sage-sessions`. Prior E2E used workspace `sage-improvements/` with external session store — resolution worked (gate logic ran). |

### Workspace vs project `.cursor/hooks`

- Workspace `sage-improvements/.cursor/` exists but has **no** `hooks.json`.
- SAGE hooks load exclusively via the **plugin** manifest, not project-level `.cursor/hooks.json`.
- User-level `~/.cursor/hooks.json` is a separate channel; `${CURSOR_PLUGIN_ROOT}` only resolves in plugin hook commands.

### Minimal live-test setup

Test scripts (do not modify product gates):

- `hooks/scripts/intentional_block.py` — exit **2** (expected to block)
- `hooks/scripts/intentional_block_exit1.py` — exit **1** (expected fail-open control)
- `hooks/scripts/intentional_block_json_deny.py` — JSON deny on stdout, exit 0

Registration snippet: `hooks/hooks-intentional-block-snippet.json`

**Steps:**

1. Prepend to `hooks/hooks.json` → `preToolUse` (first entry):

```json
{ "command": "python \"${CURSOR_PLUGIN_ROOT}/hooks/scripts/intentional_block.py\"" }
```

2. Reload Cursor window.
3. Ask agent to Write `sage-framework/tmp/block-contract-test.txt`.
4. **Pass:** Write blocked, stderr shows `INTENTIONAL BLOCK`.
5. Swap command to `intentional_block_exit1.py` → **expect Write succeeds** (confirms exit-1 fail-open).
6. Swap to `intentional_block_json_deny.py` → **expect Write blocked** (JSON deny path).
7. Remove test entry; reload.

### Recommended conclusion

| Verdict | Confidence | Rationale |
|---|---|---|
| **Misconfiguration (exit code contract)** | **High** | Cursor docs explicitly: exit 2 blocks, other non-zero fail-open. SAGE `block()` exits 1. Hooks fire; rejection side-effects run; tool proceeds — exactly the observed E2E pattern. |
| Cursor plugin cannot block | Low (pending retest) | Only if exit-2 and JSON-deny minimal hooks also fail to block in live Cursor. |
| Missing `blocking: true` in hooks.json | Ruled out | Field is SAGE internal spec only; not in Cursor schema. |

**Next action:** Run minimal `intentional_block.py` live test. If it blocks, fix `block()` to `sys.exit(2)` or emit JSON `permission: "deny"` (product change, out of scope for this investigation).
