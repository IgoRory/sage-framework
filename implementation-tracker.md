# SAGE Framework — Implementation Tracker

**Codebase:** Profitability (`C:\Users\RoryIgo\repos\cursor\Profitability`)  
**Branch:** `main` (local test copy)  
**Last verified:** 2026-05-01  
**Source plan:** [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md)

---

## Progress Summary

| Phase | Steps Complete | Steps Total | Status |
|---|---|---|---|
| Phase 1 — Repository setup | 5 | 6 | Partial — 1 gap (manifest.lock in .gitignore), files not yet committed |
| Phase 2 — Developer machine setup | 3 | 6 | Partial |
| Phase 3 — Linear configuration | 5 | 8 | Partial — blocked |
| Phase 4 — Hook script validation | 0 | 13 | Not started (scripts present, live validation pending) |
| Phase 5 — SAGE Intel + Hone setup | 2 | 4 | Partial |
| Phase 6 — PRD authoring setup | 0 | 3 | Not started (manual only) |
| Phase 7 — First live session | 0 | 3 | Not started |
| **Total** | **15** | **43** | **~35% complete** |

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
| 1.1 | Create `.sage/` directory structure (`sessions/`, `active-session.txt`, `skill-update-history.jsonl`, `current-phase.txt`, `workflow-config.json`) | `[x]` | PASS | All 5 items confirmed present |
| 1.1b | Create `.skill-update-triggers/` and `.skill-update-staging/` directories | `[x]` | PASS | Both directories exist |
| 1.2 | Copy `.cursor/hooks/hooks.json` and all 12 Python hook scripts to `.cursor/hooks/scripts/` | `[x]` | PASS | `hooks.json` present; 13 files in scripts/ (12 gate scripts + `hooks_utils.py`) |
| 1.2b | Copy `.cursor/skills/` (10 skill directories), `.cursor/agents/` (14 agent files), `.cursor/rules/sage-session.mdc` + `phase-context.mdc`, `.cursor/templates/session-manifest-template.md` | `[~]` | PARTIAL | All directories exist. Skills: 7 present (spec says 10 — missing 3). Agents: 15 present (spec says 14 — 1 extra). Both MDC rules and template confirmed PASS |
| 1.3 | Copy `AGENTS.md` to repository root | `[x]` | PASS | `AGENTS.md` present at repo root |
| 1.4 | Add SAGE entries to `.gitignore` (`.sage/sessions/active-session.txt`, `.sage/current-phase.txt`, `manifest.lock`, `.skill-update-triggers/`) | `[~]` | PARTIAL | 3 of 4 entries present. `manifest.lock` is missing from `.gitignore` — add this line |
| 1.5 | Commit all framework files with message `init: SAGE framework structure` and push to `main` | `[!]` | FAIL | All SAGE files are **untracked** — `.cursor/agents/`, `.cursor/hooks/`, `.cursor/skills/`, `.cursor/templates/`, `.cursor/rules/phase-context.mdc`, `.cursor/rules/sage-session.mdc`, `.sage/`, `AGENTS.md` are all untracked. `.gitignore` has uncommitted modifications. Run: `git add` then commit |
| 1.6 | Configure GitHub branch protection on `main` (require PR, 1 approval, require status checks, no force push) | `[-]` | MANUAL | Requires GitHub admin UI — cannot be verified programmatically |

---

## Phase 2 — Developer machine setup

**Owner:** Lead Dev (coordinates across all developers) · **Effort:** ~1 hour · **Dependency:** Phase 1 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 2.1 | Install `filelock` Python package on every developer machine (`pip install filelock --break-system-packages`) | `[ ]` | FAIL | `pip show filelock` — package not installed |
| 2.2 | Set `LINEAR_API_KEY`, `NOTION_API_KEY`, `M365_ACCESS_TOKEN` as User environment variables; restart Cursor | `[ ]` | FAIL | All three env vars unset on this machine |
| 2.3a | Confirm Python 3.12.x installed | `[x]` | PASS | Python 3.12.10 confirmed |
| 2.3b | Confirm Node.js v24.x installed | `[x]` | PASS | Node v24.13.0 confirmed |
| 2.3c | Create `C:\Sage\worktrees\` directory | `[x]` | PASS | Directory exists |
| 2.3d | Connect Linear, Notion, and Microsoft 365 MCPs in Cursor settings | `[-]` | MANUAL | Requires Cursor UI — cannot be verified programmatically |

---

## Phase 3 — Linear configuration

**Owner:** Product Manager (with Lead Dev for phase states) · **Effort:** ~3 hours · **Dependency:** None (parallel with Phase 2)

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 3.1 | Create Feature issue workflow states: `Backlog → PRD In Progress → PRD Under Review → Ready → Planned` | `[x]` | MANUAL | Complete — confirmed by user; reflected in `workflow-config.json` |
| 3.2 | Create Sprint phase workflow states: `Pending Approval → Approved → Foundation Verified → In Progress → Build Complete → Done` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.2b | Create Mob/Pair/Solo phase workflow states: `Pending Approval → Approved → In Progress → Build Complete → Done` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.3 | Create Skill Update issue workflow states: `Pending Approval → Approved → Applied → Rejected—recorded → Apply Failed` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.4 | Create Violation issue workflow states: `Needs Review → Closed` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.5 | Create `SAGE Workflow Mode` label group with labels: `mode:mob`, `mode:sprint`, `mode:pair`, `mode:solo` | `[x]` | MANUAL | Complete — confirmed by user |
| 3.6 | Configure Linear ↔ GitHub integration (auto-link commits via `LIN-[id]`, auto-link PRs, update status on merge) | `[!]` | MANUAL | Blocked — PM and Lead Dev awaiting Workspace Admin access in Linear. Access request already submitted |
| 3.7 | Deploy Linear webhook receiver (`webhook/webhook_receiver.py`) as a Windows Scheduled Task using `webhook/setup_webhook_receiver.ps1` | `[!]` | MANUAL | Blocked — same dependency on Workspace Admin access in Linear. See [`webhook/README.md`](webhook/README.md) |

---

## Phase 4 — Hook script validation

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phases 1 + 2 complete

> **Note:** All 12 hook scripts are now physically present in `.cursor/hooks/scripts/`. Steps below are blocked on Phase 1.5 (commit) and Phase 2.1–2.2 (env vars + filelock) before live validation can begin.

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 4.1a | Validate `plan_mode_enforcer.py` — attempt file write during S1, confirm rejection | `[ ]` | N/A | Script present — live validation pending Phase 1.5 + 2.1/2.2 |
| 4.1b | Validate `manifest_step_gate.py` — attempt S2 without S1 artifact, confirm rejection | `[ ]` | N/A | Script present |
| 4.1c | Validate `required_references_gate.py` — attempt S5 without required files read, confirm rejection | `[ ]` | N/A | Script present |
| 4.1d | Validate `validation_confirmed_gate.py` — attempt S5 with `validationConfirmed: false`, confirm rejection | `[ ]` | N/A | Script present |
| 4.1e | Validate `phase_approval_gate.py` — attempt S1 on unapproved Linear issue, confirm rejection | `[ ]` | N/A | Script present |
| 4.1f | Validate `tdd_results_gate.py` — attempt S6 without `STATUS: PASS` in tdd-results, confirm rejection | `[ ]` | N/A | Script present |
| 4.1g | Validate `code_review_gate.py` — attempt S7 with Critical findings, confirm rejection | `[ ]` | N/A | Script present |
| 4.1h | Validate `foundation_verified_gate.py` — attempt S5 on Dependent phase before Foundation merge, confirm rejection | `[ ]` | N/A | Script present |
| 4.1i | Validate `batch_confirmation_gate.py` — attempt next batch without confirmation flag, confirm rejection | `[ ]` | N/A | Script present |
| 4.1j | Validate `completion_report_stop_gate.py` — attempt S8 without `STATUS: PASS` in test results, confirm rejection | `[ ]` | N/A | Script present |
| 4.1k | Validate `telemetry_logger.py` — trigger any hook event, confirm events written to `telemetry.jsonl` | `[ ]` | N/A | Script present |
| 4.1l | Validate `skill_update_trigger_watcher.py` — drop `.json` file in `.skill-update-triggers/`, confirm apply step fires | `[ ]` | N/A | Script present |
| 4.2 | Full S1–S8 dry run on a test branch — all 8 steps complete in sequence, all artifacts produced, all gates fire at correct transitions | `[-]` | MANUAL | Requires a live Cursor agent session — cannot be automated |

---

## Phase 5 — SAGE Intel and SAGE Hone setup

**Owner:** Lead Dev · **Effort:** ~1 day · **Dependency:** Phase 4 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 5.1 | Create SAGE Intel metrics dashboard in Notion using [`sage-intel/intel-recorder/references/notion-metrics-template.md`](sage-intel/intel-recorder/) as template; add URL to `workflow-config.json` under `notionMetricsPageUrl` | `[ ]` | FAIL | `workflow-config.json` present but `notionMetricsPageUrl` key not set — add Notion page URL |
| 5.2 | Create Release Calendar page in Notion; add URL to `workflow-config.json` under `releaseCalendarUrl` | `[ ]` | FAIL | `workflow-config.json` present but `releaseCalendarUrl` key not set — add Notion page URL |
| 5.3 | Verify SAGE Hone pipeline: `session-performance-evaluator` runs after test cycle, `skill-effectiveness-evaluator` configured with correct cycle counter, webhook receiver running and receiving Linear approval events | `[~]` | PARTIAL | Both skills present in `.cursor/skills/`. Blocked on Phase 3.7 (webhook, awaiting Linear admin access) |
| 5.4 | Configure Playwright MCP per [`playwright-spec/playwright-mcp-spec.md`](playwright-spec/); set `playwrightE2E: true` in `workflow-config.json` | `[x]` | PASS | `featureFlags.playwrightE2E: true` confirmed in `workflow-config.json` |

---

## Phase 6 — PRD authoring setup

**Owner:** Product Manager · **Effort:** ~3 hours · **Dependency:** Phase 3 complete

| Step | Description | Status | Verified by Agent | Notes |
|---|---|---|---|---|
| 6.1 | Confirm Notion PRD storage location; add parent page URL to `workflow-config.json` under `notionPRDParentUrl` | `[-]` | MANUAL | `notionSpaceId` is set (`34cb0a7bc8b2813d8319e52d1dd61728`) but `notionPRDParentUrl` is not. Requires Notion access to confirm page structure then set URL |
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
1.4  Add manifest.lock to .gitignore                        [ACTION NEEDED]
1.5  git add + commit all SAGE files + push                 [ACTION NEEDED]
  └─► 2.1  pip install filelock                             [ACTION NEEDED]
  └─► 2.2  Set LINEAR_API_KEY, NOTION_API_KEY, M365_ACCESS_TOKEN  [ACTION NEEDED]
       └─► 3.6  Linear ↔ GitHub integration                 [BLOCKED — awaiting Linear admin access]
       └─► 3.7  Deploy webhook receiver                     [BLOCKED — awaiting Linear admin access]
            └─► 4.1a–4.1l  Live validate each of the 12 hook scripts
                 └─► 4.2  Full S1–S8 dry run
                      └─► 5.1  Add notionMetricsPageUrl to workflow-config.json
                      └─► 5.2  Add releaseCalendarUrl to workflow-config.json
                      └─► 5.3  Confirm webhook + Hone pipeline end-to-end
                           └─► 6.1  Add notionPRDParentUrl to workflow-config.json
                                └─► 6.2–6.3  Test PRD skills live
                                     └─► 7.1–7.3  First live session
```

### Items unblocked right now (no dependencies)

1. Add `manifest.lock` to `.gitignore`
2. `git add . && git commit -m "init: SAGE framework structure" && git push`
3. `pip install filelock --break-system-packages`
4. Set `LINEAR_API_KEY`, `NOTION_API_KEY`, `M365_ACCESS_TOKEN` as User env vars
5. Identify and copy the 3 missing skill directories to `.cursor/skills/`
6. Resolve Linear Workspace Admin access (unblocks 3.6, 3.7, 5.3)

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
