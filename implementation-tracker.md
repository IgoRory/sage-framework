# SAGE Framework — Implementation Tracker

**Codebase:** Profitability (verified clone: `C:\Users\RoryIgo\repos\cursor\Profitability`)  
**Branch:** `develop` (at time of check)  
**Last verified:** 2026-05-11  
**Source plan:** [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md)

**Framework counts (handoff parity):** `.cursor/hooks/scripts/` **13** Python modules · **16** agent files · **7** top-level skill directories (including `sage-intel/`). Root **`AGENTS.md`** = SAGE agent catalogue; product context = [`docs/agents-profitability.md`](docs/agents-profitability.md).

---

## Progress Summary

| Phase | Steps Complete | Steps Total | Status |
|---|---|---|---|
| Phase 1 — Repository setup | 5 | 6 | Mostly complete (branch protection manual) |
| Phase 2 — Developer machine setup | 2 | 6 | Partial |
| Phase 3 — Linear configuration | 5 | 8 | Partial — blocked |
| Phase 4 — Hook script validation | 0 | 13 | Not started (scripts present; behaviour not exercised) |
| Phase 5 — SAGE Intel + Hone setup | 0 | 4 | Not started |
| Phase 6 — PRD authoring setup | 0 | 3 | Not started |
| Phase 7 — First live session | 0 | 3 | Not started |
| **Total** | **12** | **43** | **~28% complete** |

---

## Status Key

| Symbol | Meaning |
|---|---|
| `[ ]` | Not started |
| `[~]` | Partial / in progress |
| `[x]` | Complete |
| `[!]` | Blocked — action required |
| `[-]` | Manual only — cannot be verified programmatically |

**Verified by Agent** column: `PASS` = confirmed present/correct · `FAIL` = confirmed absent/incorrect · `MANUAL` = cannot be checked programmatically · `N/A` = not yet applicable

---

## Phase 1 — Repository setup

**Owner:** Lead Dev · **Effort:** ~2 hours · **Dependency:** None

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 1.1 | Create `.sage/` directory structure (`sessions/`, `active-session.txt`, `skill-update-history.jsonl`, `current-phase.txt`, `workflow-config.json`) | `[x]` | PASS | `.sage/` present with `workflow-config.json`, `sessions/`, `sessions/active-session.txt` |
| 1.1b | Create `.skill-update-triggers/` and `.skill-update-staging/` directories | `[x]` | PASS | Both directories exist |
| 1.2 | Copy `.cursor/hooks/hooks.json` and all Python hook scripts to `.cursor/hooks/scripts/` | `[x]` | PASS | **13** `.py` modules present (parity copy also in [`hooks-spec/scripts/`](hooks-spec/scripts/)) |
| 1.2b | Copy `.cursor/skills/`, `.cursor/agents/`, `.cursor/rules/` (SAGE rules), `.cursor/templates/`, `.cursor/mcp.json` | `[x]` | PASS | **7** skill roots including `sage-intel/`; **16** agents; `sage-session.mdc`, `phase-context.mdc`, `rules.mdc`; template + `mcp.json` |
| 1.3 | Root `AGENTS.md` = SAGE catalogue; product context in `docs/` / rules | `[x]` | PASS | Catalogue at repo root; product guide documented as [`docs/agents-profitability.md`](docs/agents-profitability.md) in **this** handoff repo |
| 1.4 | Add SAGE entries to `.gitignore` | `[x]` | PASS | `.sage/sessions/active-session.txt`, `.sage/current-phase.txt`, `.skill-update-triggers/`, etc. |
| 1.5 | Commit framework files (`init: SAGE framework structure` or equivalent) | `[x]` | PASS | Commit `1be3350d` present on clone |
| 1.6 | Configure GitHub branch protection on `main` | `[-]` | MANUAL | Requires GitHub admin UI |

---

## Phase 2 — Developer machine setup

**Owner:** Lead Dev (coordinates across all developers) · **Effort:** ~1 hour · **Dependency:** Phase 1 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 2.1 | Install `filelock` Python package on every developer machine (`pip install filelock --break-system-packages`) | `[ ]` | FAIL | `pip show filelock` returned no output — package not installed on verification host |
| 2.2 | Set `LINEAR_API_KEY`, `NOTION_API_KEY`, `M365_ACCESS_TOKEN` as User environment variables; restart Cursor | `[ ]` | FAIL | All three env vars unset on verification host |
| 2.3a | Confirm Python 3.12.x installed | `[x]` | PASS | Python 3.12.10 confirmed (prior check) |
| 2.3b | Confirm Node.js v24.x installed | `[x]` | PASS | Node v24.13.0 confirmed (prior check) |
| 2.3c | Create `C:\Sage\worktrees\` directory | `[ ]` | FAIL | Directory does not exist on verification host |
| 2.3d | Connect Linear, Notion, and Microsoft 365 MCPs in Cursor settings | `[-]` | MANUAL | Requires Cursor UI — cannot be verified programmatically |

---

## Phase 3 — Linear configuration

**Owner:** Product Manager (with Lead Dev for phase states) · **Effort:** ~3 hours · **Dependency:** None (parallel with Phase 2)

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 3.1 | Create Feature issue workflow states: `Backlog → PRD In Progress → PRD Under Review → Ready → Planned` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.2 | Create Sprint phase workflow states: `Pending Approval → Approved → Foundation Verified → In Progress → Build Complete → Done` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.2b | Create Mob/Pair/Solo phase workflow states: `Pending Approval → Approved → In Progress → Build Complete → Done` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.3 | Create Skill Update issue workflow states: `Pending Approval → Approved → Applied → Rejected—recorded → Apply Failed` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.4 | Create Violation issue workflow states: `Needs Review → Closed` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.5 | Create `SAGE Workflow Mode` label group with labels: `mode:mob`, `mode:sprint`, `mode:pair`, `mode:solo` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.6 | Configure Linear ↔ GitHub integration (auto-link commits via `LIN-[id]`, auto-link PRs, update status on merge) | `[!]` | MANUAL | Blocked — PM and Lead Dev awaiting Workspace Admin access in Linear |
| 3.7 | ~~Deploy Linear webhook receiver~~ — Replaced by `skill_update_poller.py` (polling approach, no webhook/ngrok required). Set `LINEAR_API_KEY` env var and run poller manually or on schedule. | `[x]` | MANUAL | Complete — webhook architecture removed in favour of polling |

---

## Phase 4 — Hook script validation

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phases 1 + 2 complete

Scripts **exist** in the Profitability repo; rows below track **runtime validation** in Cursor (not yet executed).

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 4.1a | Validate `plan_mode_enforcer.py` — attempt file write during S1, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1b | Validate `manifest_step_gate.py` — attempt S2 without S1 artifact, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1c | Validate `required_references_gate.py` — attempt S5 without required files read, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1d | Validate `validation_confirmed_gate.py` — attempt S5 with `validationConfirmed: false`, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1e | Validate `phase_approval_gate.py` — attempt S1 on unapproved Linear issue, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1f | Validate `tdd_results_gate.py` — attempt S6 without `STATUS: PASS` in tdd-results, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1g | Validate `code_review_gate.py` — attempt S7 with Critical findings, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1h | Validate `foundation_verified_gate.py` — attempt S5 on Dependent phase before Foundation merge, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1i | Validate `batch_confirmation_gate.py` — attempt next batch without confirmation flag, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1j | Validate `completion_report_stop_gate.py` — attempt S8 without `STATUS: PASS` in test results, confirm rejection | `[ ]` | FAIL | Runtime validation not run |
| 4.1k | Validate `telemetry_logger.py` — trigger any hook event, confirm events written to session telemetry | `[ ]` | FAIL | Runtime validation not run (`workflow-telemetry.jsonl` per `workflow-config.json`) |
| 4.1l | Validate `skill_update_trigger_watcher.py` — drop `.json` file in `.skill-update-triggers/`, confirm apply step fires | `[ ]` | FAIL | Runtime validation not run |
| 4.2 | Full S1–S8 dry run on a test branch — all 8 steps complete in sequence, all artifacts produced, all gates fire at correct transitions | `[-]` | MANUAL | Requires a live Cursor agent session — cannot be automated |

---

## Phase 5 — SAGE Intel and SAGE Hone setup

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phase 4 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 5.1 | Create SAGE Intel metrics dashboard in Notion using [`sage-intel/intel-recorder/references/notion-metrics-template.md`](sage-intel/intel-recorder/) as template; add URL to `workflow-config.json` under `notionMetricsPageUrl` | `[ ]` | FAIL | Not verified — requires Notion UI |
| 5.2 | Create Release Calendar page in Notion; add URL to `workflow-config.json` under `releaseCalendarUrl` | `[ ]` | FAIL | Not verified |
| 5.3 | Verify SAGE Hone pipeline: `session-performance-evaluator` runs after test cycle, `skill-effectiveness-evaluator` configured with correct cycle counter, polling script detects Linear approval events | `[ ]` | FAIL | Depends on Phase 3.7 (now unblocked — verify poller integration) |
| 5.4 | Configure Playwright MCP per [`playwright-spec/playwright-mcp-spec.md`](playwright-spec/); set `playwrightE2ETesting: true` in `workflow-config.json` | `[-]` | MANUAL | Playwright MCP configuration requires Cursor UI |

---

## Phase 6 — PRD authoring setup

**Owner:** Product Manager · **Effort:** ~3 hours · **Dependency:** Phase 3 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 6.1 | Confirm Notion PRD storage location; add parent page URL to `workflow-config.json` under `notionPRDParentUrl` | `[-]` | MANUAL | Requires Notion access to confirm page structure |
| 6.2 | Test `prd-interviewer` skill — confirm Notion MCP active, PRD page created in correct location, component spec child page linked | `[-]` | MANUAL | Requires live Cursor session |
| 6.3 | Test `prd-completeness-check` skill — confirm scoring runs correctly and Linear issue status updates to Ready on pass | `[-]` | MANUAL | Requires live Cursor session + Linear connection |

---

## Phase 7 — First live session

**Owner:** Lead Dev + Product Manager + Full team · **Effort:** ~1 day · **Dependency:** All phases complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 7.1 | Select a suitable first feature (real but low-risk, multi-component, well-understood) | `[-]` | MANUAL | Team decision |
| 7.2 | Run full SAGE workflow end-to-end: PRD → completeness check → Feature Walkthrough (optional) → Sprint Kick-off → S1–S8 per developer → Review & Merge | `[-]` | MANUAL | Requires full team, live session |
| 7.3 | Debrief: review hook compliance rate, step timing vs estimates, configuration issues, SAGE Intel data from first cycle | `[-]` | MANUAL | Post-session review |

---

## Automated critical path

The steps that are blocking everything else — in order:

```
1.1  Create .sage/ directory structure                    [DONE on verified clone]
1.1b Create .skill-update-triggers/ and staging         [DONE]
1.2  Copy .cursor/hooks/ (hooks.json + 13 scripts)       [DONE — see hooks-spec/scripts mirror]
1.2b Copy .cursor/skills/, agents/, rules/, templates/   [DONE]
1.3  Root AGENTS.md catalogue + product context pattern   [DONE — see docs/agents-profitability.md in handoff]
1.4  Update .gitignore                                   [DONE]
1.5  Commit and push                                   [DONE — init commit present]
  └─► 2.1  pip install filelock
  └─► 2.2  Set LINEAR_API_KEY, NOTION_API_KEY, M365_ACCESS_TOKEN
  └─► 2.3c Create C:\Sage\worktrees\
       └─► 3.6  Linear ↔ GitHub integration  [BLOCKED — awaiting Linear admin access]
       └─► 3.7  Skill update poller            [COMPLETE — polling replaces webhook]
            └─► 4.1a–4.1l  Validate each hook script in Cursor
                 └─► 4.2  Full S1–S8 dry run
                      └─► 5.1–5.3  SAGE Intel + Hone setup
                           └─► 6.1–6.3  PRD authoring setup (PM)
                                └─► 7.1–7.3  First live session
```

---

## How to re-verify

Ask in the Profitability Cursor chat:

> **"Re-verify the SAGE implementation tracker"**

Re-run automated checks against the Profitability repo and update this file with fresh pass/fail results and an updated timestamp.

To implement a specific phase:

> **"Implement Phase N of the SAGE setup"**

Execute all automatable steps for that phase and re-verify immediately after.

---

*Tracker maintained by Cursor agent. Source: [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md) · [`hooks-spec/hook-scripts-spec.md`](hooks-spec/hook-scripts-spec.md)*
