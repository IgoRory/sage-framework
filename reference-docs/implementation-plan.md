# SAGE Framework — Implementation Plan

**Framework:** SAGE (Semi-Autonomous Guided Execution)
**Prepared for:** Profitability Team
**Repository:** `github.com/IgoRory/empyrean-rory-profitability-workflow`
**Status:** Ready for implementation

---

## Overview

This document describes the implementation sequence for the SAGE Framework on the Profitability codebase. All framework files are fully specified and available in the handoff repository. Implementation requires no architectural decisions — only setup, configuration, and integration work.

The implementation is split into seven phases. Phases 1–5 are owned by the Lead Dev (~5–6 days total). Phase 6 is owned by the Product Manager (~3 hours). Phase 7 is joint validation.

---

## Prerequisites

Before beginning Phase 1:

- [ ] Confirm the `.cursor/` rules directory location — a `Web/cursor rules/` directory may exist in the ADO repo tree. This is likely a misplaced `.cursor/rules/` folder. Verify its location and move to repo root as `.cursor/rules/` before implementation begins.
- [ ] All developers have Cursor installed with MCP connections for Linear, Notion, and Microsoft 365
- [ ] GitHub repo is accessible to the Lead Dev with admin rights
- [ ] Linear project is created for the Profitability team

---

## Phase 1 — Repository setup

**Owner:** Lead Dev
**Estimated effort:** ~2 hours

### 1.1 Create SAGE directory structure

From the main clone on the Lead Dev's machine:

```powershell
cd C:\Users\[developer]\cursor-prof\Profitability

# Create .sage directory structure
New-Item -ItemType Directory -Path ".sage\sessions" -Force
New-Item -ItemType File -Path ".sage\sessions\active-session.txt" -Force
New-Item -ItemType File -Path ".sage\skill-update-history.jsonl" -Force
New-Item -ItemType File -Path ".sage\current-phase.txt" -Force
New-Item -ItemType File -Path ".sage\workflow-config.json" -Force

# Create trigger and staging directories
New-Item -ItemType Directory -Path ".skill-update-triggers" -Force
New-Item -ItemType Directory -Path ".skill-update-staging" -Force
```

Paste `workflow-config.json` content from `hooks-spec/workflow-config.json` in the handoff repository (same schema as Profitability `.sage/workflow-config.json`: `framework`, `linear`, `modes`, `telemetry`, `phases`, etc.).

### 1.2 Add .cursor/ files

Copy all files from the handoff repository `.cursor/` directory:

- `.cursor/hooks/hooks.json` and all Python hook scripts under `.cursor/hooks/scripts/` (13 modules: shared utils, gates, telemetry, watcher)
- `.cursor/skills/` — seven top-level skill directories (including `sage-intel/` with `intel-recorder` and `intel-advisor`)
- `.cursor/agents/` — sixteen agent definition files (`.md`)
- `.cursor/rules/sage-session.mdc`, `phase-context.mdc`, and preserve existing `rules.mdc` as applicable
- `.cursor/templates/session-manifest-template.md`
- `.cursor/mcp.json` — MCP server URLs (Linear, Notion, Microsoft 365) as needed

### 1.3 AGENTS files at the repository root (catalogue vs product context)

Cursor reads root **`AGENTS.md`** automatically. On Profitability, that file is the **SAGE Framework Agent Catalogue** (framework roles and constraints), not the long-form product/codebase guide.

1. Copy the catalogue from the handoff package root (same content as this repo’s [`AGENTS.md`](../AGENTS.md)) to the Profitability repo root:

```powershell
Copy-Item "[path-to-handoff]\AGENTS.md" -Destination "."
```

2. Add the **Profitability product context** from [`docs/agents-profitability.md`](../docs/agents-profitability.md) (same content as [`profitability-repo-files/AGENTS.md`](../profitability-repo-files/AGENTS.md)) so agents still see domain rules — typically by adding a **Cursor Project Rule** that references `docs/agents-profitability.md`, or by copying that file into `docs/` in the product repo and `@`-mentioning it in team workflow. **Do not** overwrite root `AGENTS.md` with the product guide.

> **Verify before committing:** Open the product context doc and confirm Sections 2 and 5 match the actual directory structure of the Profitability repo. Adjust any paths that differ.

### 1.4 Update .gitignore

```powershell
Add-Content .gitignore "`n# SAGE workflow runtime files"
Add-Content .gitignore ".sage/sessions/active-session.txt"
Add-Content .gitignore ".sage/current-phase.txt"
Add-Content .gitignore "manifest.lock"
Add-Content .gitignore ".skill-update-triggers/"
```

### 1.5 Commit

```powershell
git add .sage/ .cursor/ .skill-update-triggers/ .skill-update-staging/ .gitignore AGENTS.md docs/
git commit -m "init: SAGE framework structure

- .sage/ with workflow-config.json and sessions structure
- .cursor/hooks/ with hooks.json and all Python gate scripts (13 modules under scripts/)
- .cursor/skills/ with all skill directories (7 top-level, including sage-intel)
- .cursor/agents/ with all 16 agent definitions
- .cursor/rules/ with sage-session.mdc and phase-context.mdc
- .cursor/templates/ with session manifest template
- .skill-update-triggers/ and .skill-update-staging/ directories
- AGENTS.md — SAGE agent catalogue at repo root; docs/agents-profitability.md — product context"

git push origin main
```

### 1.6 Configure branch protection

In GitHub repository settings → Branches → Branch protection rules, confirm or add a rule for `main`:

| Setting | Required value |
|---|---|
| Require pull request before merging | ✅ |
| Required approvals | 1 (Lead Dev) |
| Dismiss stale reviews on new commits | ✅ |
| Require status checks to pass | ✅ |
| Restrict push to main | Lead Dev only |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

---

## Phase 2 — Developer machine setup

**Owner:** Lead Dev (coordinates across all developers)
**Estimated effort:** ~1 hour

### 2.1 Install dependencies

On every developer machine:

```powershell
pip install filelock --break-system-packages
```

### 2.2 Set environment variables

Each machine requires three environment variables. Run once in PowerShell (persists across restarts):

```powershell
[System.Environment]::SetEnvironmentVariable("LINEAR_API_KEY", "lin_api_...", "User")
[System.Environment]::SetEnvironmentVariable("NOTION_API_KEY", "secret_...", "User")
[System.Environment]::SetEnvironmentVariable("M365_ACCESS_TOKEN", "...", "User")
```

Restart Cursor after setting environment variables.

> **M365 token note:** OAuth access tokens expire (typically 1 hour). Configure a service account with token refresh or use a long-lived token. The `kickoff-dev-review` skill will fail to fetch the Teams transcript if this token has expired.

### 2.3 Machine setup checklist

**All developers:**
- [ ] Main clone at `C:\Users\[name]\cursor-prof\Profitability`
- [ ] `C:\Sage\worktrees\` directory exists (create if not)
- [ ] Pull latest `main` — confirm `.sage/` and updated `.cursor/` present
- [ ] `pip install filelock` confirmed
- [ ] `LINEAR_API_KEY` env var set
- [ ] `NOTION_API_KEY` env var set
- [ ] `M365_ACCESS_TOKEN` env var set
- [ ] Cursor restarted after env vars set
- [ ] Linear MCP connected in Cursor settings
- [ ] Notion MCP connected in Cursor settings
- [ ] Microsoft 365 MCP connected in Cursor settings
- [ ] `python --version` confirms 3.12.x
- [ ] `node --version` confirms v24.x

**Product Manager:** Same checklist. Primary use: prd-interviewer, prd-completeness-check, kickoff-dev-review, intel-advisor, planning cycle.

**Lead Dev:** Same checklist, plus:
- [ ] GitHub admin access confirmed
- [ ] Branch protection rule on `main` confirmed
- [ ] Linear ↔ GitHub integration configured and tested

---

## Phase 3 — Linear configuration

**Owner:** Product Manager (with Lead Dev for phase states)
**Estimated effort:** ~3 hours

### 3.1 Feature issue workflow states

Create the following states in the Profitability Linear project:

`Backlog` → `PRD In Progress` → `PRD Under Review` → `Ready` → `Planned`

### 3.2 Phase issue workflow states

Create two sets:

**Sprint phases:**
`Pending Approval` → `Approved` → `Foundation Verified` → `In Progress` → `Build Complete` → `Done`

**Mob / Pair / Solo phases:**
`Pending Approval` → `Approved` → `In Progress` → `Build Complete` → `Done`

### 3.3 Skill update issue workflow states

`Pending Approval` → `Approved` → `Applied` → `Rejected—recorded` → `Apply Failed`

### 3.4 Violation issue workflow states

`Needs Review` → `Closed`

### 3.5 Mode labels

Linear does not support arbitrary custom properties on issues. The `mode` field and three metadata fields are handled using two alternative mechanisms instead.

**Create four mode labels** in Linear Settings → Labels, grouped under a label group named `SAGE Workflow Mode`:

| Label | Description |
|---|---|
| `mode:mob` | Co-located or screenshare session. Single terminal, sequential phases, Driver/Navigator roles. Mob Kick-off (~2 hrs) required. Feature Walkthrough mandatory the day before. |
| `mode:sprint` | Distributed parallel session. Each developer owns one phase in their own worktree. Sprint Kick-off (~75 min) required. Phases run simultaneously after kick-off. Feature Walkthrough optional. |
| `mode:pair` | Two developers, sequential phases, no synchronous kick-off. PRD required at Ready status. Async phase breakdown only. No Feature Walkthrough. |
| `mode:solo` | Single developer, no kick-off, no PRD required. Issue tracker item sufficient. All S1–S8 gates still active. |

The `phase-splitter` skill applies the correct label automatically at kick-off — no manual labelling needed.

**Metadata fields** (`worktree_path`, `diff_path`, `evaluation_cycle`) are written as a structured YAML block at the top of the issue description by the agent that creates the issue:

```
---
sage_metadata:
  worktree_path: C:\Sage\worktrees\LIN-4821\phase-1---
```

Agents and skills read these values via the Linear MCP description field. Fields that do not apply to a given issue type are omitted entirely. Full format specification is in `hooks-spec/hook-scripts-spec.md` under "Linear issue metadata block".

### 3.6 Linear ↔ GitHub integration

In Linear Settings → Integrations → GitHub:
- Connect the GitHub organisation
- Enable: auto-link commits via `LIN-[id]` in commit messages
- Enable: auto-link PRs to Linear issues
- Enable: update Linear issue status when PR merges to main

### 3.7 Webhook configuration

Follow the setup guide in `webhook/README.md` in the handoff repository to install the Linear webhook receiver. This receives approval events for skill updates and routes them to the trigger file watcher.

---

## Phase 4 — Hook script validation

**Owner:** Lead Dev
**Estimated effort:** ~1 day

### 4.1 Validate each hook script in sequence

For each of the twelve hook scripts, run a manual validation test confirming the gate fires correctly and the telemetry event is written. Test sequence:

1. `plan_mode_enforcer.py` — attempt a file write during S1, confirm rejection
2. `manifest_step_gate.py` — attempt S2 without S1 artifact, confirm rejection
3. `required_references_gate.py` — attempt S5 without reading required files, confirm rejection
4. `validation_confirmed_gate.py` — attempt S5 with `validationConfirmed: false`, confirm rejection
5. `phase_approval_gate.py` — attempt S1 on unapproved phase issue, confirm rejection
6. `tdd_results_gate.py` — attempt S6 without `STATUS: PASS`, confirm rejection
7. `code_review_gate.py` — attempt S7 with Critical findings, confirm rejection
8. `foundation_verified_gate.py` — attempt S5 on Dependent phase before Foundation merge, confirm rejection
9. `batch_confirmation_gate.py` — attempt next batch without confirmation flag, confirm rejection
10. `completion_report_stop_gate.py` — attempt S8 without `STATUS: PASS` in test results, confirm rejection
11. `telemetry_logger.py` — confirm telemetry events written correctly to `telemetry.jsonl`
12. `skill_update_trigger_watcher.py` — confirm trigger file detection and apply step

### 4.2 Full S1–S8 dry run

Run one complete phase end-to-end on a test branch. Confirm all eight steps complete in sequence, all artifacts are produced, all gates fire at the correct transition points, and the completion report is generated.

---

## Phase 5 — SAGE Intel and SAGE Hone setup

**Owner:** Lead Dev
**Estimated effort:** ~1 day

### 5.1 Notion metrics dashboard

Create the SAGE Intel metrics dashboard in Notion using `sage-intel/intel-recorder/references/notion-metrics-template.md` as the template. Note the page URL and add to `workflow-config.json` under `notionMetricsPageUrl`.

### 5.2 Release Calendar

Create the Release Calendar page in Notion. Note the URL and add to `workflow-config.json` under `releaseCalendarUrl`.

### 5.3 Verify SAGE Hone pipeline

Confirm the session-performance-evaluator runs correctly after a test cycle. Confirm the skill-effectiveness-evaluator is configured with the correct cycle counter. Confirm the webhook receiver is running and can receive Linear approval events.

### 5.4 Playwright MCP

Follow `playwright-spec/playwright-mcp-spec.md` to configure Playwright MCP for agent testing (S7). Set `playwrightE2ETesting: true` in `workflow-config.json` when ready.

---

## Phase 6 — PRD authoring setup

**Owner:** Product Manager
**Estimated effort:** ~3 hours

### 6.1 Confirm Notion structure

Confirm or create the PRD storage location in Notion. Note the parent page URL and add to `workflow-config.json` under `notionPRDParentUrl`.

### 6.2 Test prd-interviewer

Run the prd-interviewer skill on a test feature to confirm:
- Notion MCP connection is active
- PRD page is created in the correct Notion location
- Component specification child page is linked correctly
- Mockup file path handling works from the Product Manager's machine

### 6.3 Test prd-completeness-check

Run prd-completeness-check on the test PRD from 6.2. Confirm scoring runs correctly and the Linear issue status updates to Ready on pass.

---

## Phase 7 — First live session

**Owner:** Lead Dev + Product Manager + Full team
**Estimated effort:** ~1 day

### 7.1 Select a suitable first feature

Choose a feature that is:
- Real but low-risk (not on the critical path)
- Multi-component (suited to Sprint mode)
- Well-understood by the team

### 7.2 Run the full workflow

Work through the complete SAGE workflow end-to-end:
1. Product Manager runs prd-interviewer + prd-completeness-check
2. Feature Walkthrough (optional for first session — recommended)
3. Sprint Kick-off (~75 min)
4. Each developer runs S1–S8 on their assigned phase
5. Lead Dev runs Review & Merge

### 7.3 Debrief

After the first session, review:
- Hook compliance rate (any unexpected gate rejections?)
- Step timing vs estimates
- Any configuration issues discovered during execution
- SAGE Intel data from the first cycle

---

## Estimated timeline

| Phase | Owner | Effort | Dependency |
|---|---|---|---|
| 1 — Repository setup | Lead Dev | ~2 hrs | None |
| 2 — Developer machines | Lead Dev | ~1 hr | Phase 1 complete |
| 3 — Linear configuration | Product Manager | ~3 hrs | None (parallel with Phase 2) |
| 4 — Hook validation | Lead Dev | ~1 day | Phase 1 + 2 complete |
| 5 — SAGE Intel + Hone setup | Lead Dev | ~1 day | Phase 4 complete |
| 6 — PRD authoring setup | Product Manager | ~3 hrs | Phase 3 complete |
| 7 — First live session | Full team | ~1 day | All phases complete |

**Total Lead Dev effort:** ~5–6 days
**Total Product Manager effort:** ~6 hours
**Total elapsed time (with parallelism):** ~6–7 working days

---

## Reference materials

All implementation files are in the handoff repository at `github.com/IgoRory/empyrean-rory-profitability-workflow`. Start with `README.md` for a full index.

Key files:
- `hooks-spec/hooks.json` — hook definitions (parity with Profitability `.cursor/hooks/hooks.json`)
- `hooks-spec/hook-scripts-spec.md` — full Python script specifications
- `hooks-spec/session-manifest-schema.md` — session manifest structure
- `hooks-spec/workflow-config.json` — workflow configuration (parity with Profitability `.sage/workflow-config.json`)
- `hooks-spec/scripts/` — mirror of Python gate scripts for offline handoff
- `cursor-directory-spec/cursor-directory-spec.md` — full `.cursor/` directory specification
- `cursor-directory-spec/git-worktree-spec.md` — git worktree setup and conventions
- `AGENTS.md` — SAGE agent catalogue (root); `agent-definitions.md` — long-form definitions including model hints; `docs/agents-profitability.md` — Profitability product context
- `webhook/README.md` — webhook receiver setup
- `playwright-spec/playwright-mcp-spec.md` — Playwright MCP configuration
