# SAGE Framework — Implementation Tracker

**Codebase:** Profitability (`C:\Users\RoryIgo\cursor-prof\Profitability`)  
**Branch:** `dev-main`  
**Last verified:** 2026-04-27  
**Source plan:** [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md)

---

## Progress Summary

| Phase | Steps Complete | Steps Total | Status |
|---|---|---|---|
| Phase 1 — Repository setup | 0 | 6 | Not started |
| Phase 2 — Developer machine setup | 2 | 3 | Partial |
| Phase 3 — Linear configuration | 0 | 7 | Not started |
| Phase 4 — Hook script validation | 0 | 2 | Not started |
| Phase 5 — SAGE Intel + Hone setup | 0 | 4 | Not started |
| Phase 6 — PRD authoring setup | 0 | 3 | Not started |
| Phase 7 — First live session | 0 | 3 | Not started |
| **Total** | **2** | **28** | **7% complete** |

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
| 1.1 | Create `.sage/` directory structure (`sessions/`, `active-session.txt`, `skill-update-history.jsonl`, `current-phase.txt`, `workflow-config.json`) | `[ ]` | FAIL | None of the `.sage/` paths exist. Run the PowerShell commands from [Phase 1.1](reference-docs/implementation-plan.md) |
| 1.1b | Create `.skill-update-triggers/` and `.skill-update-staging/` directories | `[ ]` | FAIL | Both directories absent |
| 1.2 | Copy `.cursor/hooks/hooks.json` and all 12 Python hook scripts to `.cursor/hooks/scripts/` | `[ ]` | FAIL | `.cursor/hooks/` does not exist. Copy from [hooks-spec/](hooks-spec/) in this repo |
| 1.2b | Copy `.cursor/skills/` (10 skill directories), `.cursor/agents/` (14 agent files), `.cursor/rules/sage-session.mdc` + `phase-context.mdc`, `.cursor/templates/session-manifest-template.md` | `[ ]` | FAIL | None of `.cursor/skills/`, `.cursor/agents/`, `.cursor/templates/` exist. `.cursor/rules/rules.mdc` exists but SAGE rules are missing |
| 1.3 | Copy `AGENTS.md` to repository root | `[ ]` | FAIL | `AGENTS.md` is absent from the Profitability repo root |
| 1.4 | Add SAGE entries to `.gitignore` (`.sage/sessions/active-session.txt`, `.sage/current-phase.txt`, `manifest.lock`, `.skill-update-triggers/`) | `[ ]` | FAIL | No SAGE entries found in `.gitignore` |
| 1.5 | Commit all framework files with message `init: SAGE framework structure` and push to `main` | `[ ]` | FAIL | No matching commit found in git log |
| 1.6 | Configure GitHub branch protection on `main` (require PR, 1 approval, require status checks, no force push) | `[-]` | MANUAL | Requires GitHub admin UI — cannot be verified programmatically |

---

## Phase 2 — Developer machine setup

**Owner:** Lead Dev (coordinates across all developers) · **Effort:** ~1 hour · **Dependency:** Phase 1 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 2.1 | Install `filelock` Python package on every developer machine (`pip install filelock --break-system-packages`) | `[ ]` | FAIL | `pip show filelock` returned no output — package not installed |
| 2.2 | Set `LINEAR_API_KEY`, `NOTION_API_KEY`, `M365_ACCESS_TOKEN` as User environment variables; restart Cursor | `[ ]` | FAIL | All three env vars are unset on this machine |
| 2.3a | Confirm Python 3.12.x installed | `[x]` | PASS | Python 3.12.10 confirmed |
| 2.3b | Confirm Node.js v24.x installed | `[x]` | PASS | Node v24.13.0 confirmed |
| 2.3c | Create `C:\Sage\worktrees\` directory | `[ ]` | FAIL | Directory does not exist |
| 2.3d | Connect Linear, Notion, and Microsoft 365 MCPs in Cursor settings | `[-]` | MANUAL | Requires Cursor UI — cannot be verified programmatically |

---

## Phase 3 — Linear configuration

**Owner:** Product Manager (with Lead Dev for phase states) · **Effort:** ~3 hours · **Dependency:** None (parallel with Phase 2)

All steps in this phase are manual-only.

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 3.1 | Create Feature issue workflow states in Linear: `Backlog → PRD In Progress → PRD Under Review → Ready → Planned` | `[-]` | MANUAL | Linear admin UI required |
| 3.2 | Create Sprint phase workflow states: `Pending Approval → Approved → Foundation Verified → In Progress → Build Complete → Done` | `[-]` | MANUAL | Linear admin UI required |
| 3.2b | Create Mob/Pair/Solo phase workflow states: `Pending Approval → Approved → In Progress → Build Complete → Done` | `[-]` | MANUAL | Linear admin UI required |
| 3.3 | Create Skill Update issue workflow states: `Pending Approval → Approved → Applied → Rejected—recorded → Apply Failed` | `[-]` | MANUAL | Linear admin UI required |
| 3.4 | Create Violation issue workflow states: `Needs Review → Closed` | `[-]` | MANUAL | Linear admin UI required |
| 3.5 | Create `SAGE Workflow Mode` label group with labels: `mode:mob`, `mode:sprint`, `mode:pair`, `mode:solo` | `[-]` | MANUAL | Linear admin UI required |
| 3.6 | Configure Linear ↔ GitHub integration (auto-link commits via `LIN-[id]`, auto-link PRs, update status on merge) | `[-]` | MANUAL | Linear + GitHub admin UI required |
| 3.7 | Deploy Linear webhook receiver (`webhook/webhook_receiver.py`) as a Windows Scheduled Task using `webhook/setup_webhook_receiver.ps1` | `[ ]` | FAIL | Webhook receiver not deployed — see [`webhook/README.md`](webhook/README.md) for setup guide |

---

## Phase 4 — Hook script validation

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phases 1 + 2 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 4.1a | Validate `plan_mode_enforcer.py` — attempt file write during S1, confirm rejection | `[ ]` | FAIL | Script not present (Phase 1.2 incomplete) |
| 4.1b | Validate `manifest_step_gate.py` — attempt S2 without S1 artifact, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1c | Validate `required_references_gate.py` — attempt S5 without required files read, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1d | Validate `validation_confirmed_gate.py` — attempt S5 with `validationConfirmed: false`, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1e | Validate `phase_approval_gate.py` — attempt S1 on unapproved Linear issue, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1f | Validate `tdd_results_gate.py` — attempt S6 without `STATUS: PASS` in tdd-results, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1g | Validate `code_review_gate.py` — attempt S7 with Critical findings, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1h | Validate `foundation_verified_gate.py` — attempt S5 on Dependent phase before Foundation merge, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1i | Validate `batch_confirmation_gate.py` — attempt next batch without confirmation flag, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1j | Validate `completion_report_stop_gate.py` — attempt S8 without `STATUS: PASS` in test results, confirm rejection | `[ ]` | FAIL | Script not present |
| 4.1k | Validate `telemetry_logger.py` — trigger any hook event, confirm events written to `telemetry.jsonl` | `[ ]` | FAIL | Script not present |
| 4.1l | Validate `skill_update_trigger_watcher.py` — drop `.json` file in `.skill-update-triggers/`, confirm apply step fires | `[ ]` | FAIL | Script not present |
| 4.2 | Full S1–S8 dry run on a test branch — all 8 steps complete in sequence, all artifacts produced, all gates fire at correct transitions | `[-]` | MANUAL | Requires a live Cursor agent session — cannot be automated |

---

## Phase 5 — SAGE Intel and SAGE Hone setup

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phase 4 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 5.1 | Create SAGE Intel metrics dashboard in Notion using [`sage-intel/intel-recorder/references/notion-metrics-template.md`](sage-intel/intel-recorder/) as template; add URL to `workflow-config.json` under `notionMetricsPageUrl` | `[ ]` | FAIL | `workflow-config.json` not present (Phase 1.1 incomplete) |
| 5.2 | Create Release Calendar page in Notion; add URL to `workflow-config.json` under `releaseCalendarUrl` | `[ ]` | FAIL | `workflow-config.json` not present |
| 5.3 | Verify SAGE Hone pipeline: `session-performance-evaluator` runs after test cycle, `skill-effectiveness-evaluator` configured with correct cycle counter, webhook receiver running and receiving Linear approval events | `[ ]` | FAIL | Depends on Phase 3.7 (webhook) and Phase 1.2 (skills) |
| 5.4 | Configure Playwright MCP per [`playwright-spec/playwright-mcp-spec.md`](playwright-spec/); set `playwrightE2ETesting: true` in `workflow-config.json` | `[-]` | MANUAL | Playwright MCP configuration requires Cursor UI + `workflow-config.json` present |

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
1.1  Create .sage/ directory structure
1.1b Create .skill-update-triggers/ and .skill-update-staging/
1.2  Copy .cursor/hooks/ (hooks.json + 12 scripts)
1.2b Copy .cursor/skills/, .cursor/agents/, .cursor/templates/
1.3  Copy AGENTS.md to repo root
1.4  Update .gitignore
1.5  Commit and push
  └─► 2.1  pip install filelock
  └─► 2.2  Set LINEAR_API_KEY, NOTION_API_KEY, M365_ACCESS_TOKEN
  └─► 2.3c Create C:\Sage\worktrees\
       └─► 3.7  Deploy webhook receiver
            └─► 4.1a–4.1l  Validate each of the 12 hook scripts
                 └─► 4.2  Full S1–S8 dry run
                      └─► 5.1–5.3  SAGE Intel + Hone setup
                           └─► 6.1–6.3  PRD authoring setup (PM)
                                └─► 7.1–7.3  First live session
```

---

## How to re-verify

Ask in the Profitability Cursor chat:

> **"Re-verify the SAGE implementation tracker"**

I will re-run all automated checks against the Profitability repo and push an updated version of this file to `IgoRory/sage-framework/implementation-tracker.md` with fresh pass/fail results and an updated timestamp.

To implement a specific phase:

> **"Implement Phase 1 of the SAGE setup"**

I will execute all automatable steps for that phase and re-verify immediately after.

---

*Tracker maintained by Cursor agent. Source: [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md) · [`hooks-spec/hook-scripts-spec.md`](hooks-spec/hook-scripts-spec.md)*
