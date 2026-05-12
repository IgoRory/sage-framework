# Git Worktree Specification
# SAGE Framework — Git Worktree Specification

---

## Overview

The Profitability repository is already hosted on GitHub
(`github.com/your-organisation/Profitability`). GitHub is the
source of truth for code. ADO currently handles work item tracking
and CI/CD pipelines and will continue to run pipelines — the YAML
files at repo root (`profitability-api.yml`, `profitability-web.yml`,
etc.) are ADO pipeline definitions that reference the GitHub repo
and do not need to change.

**The transition this workflow introduces is narrow:**
Work item tracking moves from ADO to Linear.
Code, repo, CI/CD pipelines, and developer git workflows are
unchanged.

Git worktrees provide structural isolation for parallel phase
execution in **Sprint** and **Pair** work streams. They do not apply
to Mob mode (single terminal, no worktrees) or Solo mode (main clone
directly). All references in this document apply to Sprint and Pair
unless explicitly stated otherwise. Each phase lane runs
in its own worktree — a separate working directory pointing to a
different branch of the same repository. Three developers can
build three phases simultaneously with zero risk of writing to
each other's files.

---

## Part 1 — One-time setup (performed by the Lead Dev)

### Step 1 — Add workflow directory structure to the repo

From the main clone on the Lead Dev's machine:

```powershell
cd C:\Users\[the Lead Dev-username]\cursor-prof\Profitability

# Create .sage directory structure
New-Item -ItemType Directory -Path ".sage\sessions" -Force
New-Item -ItemType File -Path ".sage\sessions\active-session.txt" -Force
New-Item -ItemType File -Path ".sage\skill-update-history.jsonl" -Force
New-Item -ItemType File -Path ".sage\current-phase.txt" -Force
New-Item -ItemType File -Path ".sage\workflow-config.json" -Force
# Paste workflow-config.json content from spec into this file

# Create trigger and staging directories
New-Item -ItemType Directory -Path ".skill-update-triggers" -Force
New-Item -ItemType Directory -Path ".skill-update-staging" -Force

# Update .gitignore — runtime files that should NOT be committed
Add-Content .gitignore "`n# SAGE workflow runtime files"
Add-Content .gitignore ".sage/sessions/active-session.txt"
Add-Content .gitignore ".sage/current-phase.txt"
Add-Content .gitignore "manifest.lock"
Add-Content .gitignore ".skill-update-triggers/"

# These ARE committed (not in .gitignore):
# .sage/workflow-config.json         — workflow policy, reviewed by team
# .sage/skill-update-history.jsonl   — audit trail
# .skill-update-staging/            — proposed SKILL.md diffs for review
# .sage/sessions/[FEATURE_ID]/       — session artifacts (permanent record)
```

### Step 2 — Add all .cursor/ files

Copy all files from the `.cursor/` directory spec into the repo:
- `.cursor/hooks/hooks.json` and all Python scripts
- `.cursor/skills/` — all ten skill directories
- `.cursor/agents/` — all fourteen agent definition files
- `.cursor/rules/sage-session.mdc` and `phase-context.mdc`
  (existing `rules.mdc` untouched)
- `.cursor/templates/session-manifest-template.md`

Commit everything:

```powershell
git add .sage/ .cursor/ .skill-update-triggers/ .skill-update-staging/ .gitignore
git commit -m "init: AI-assisted Sprint workflow structure

- .sage/ with workflow-config.json and sessions structure
- .cursor/hooks/ with hooks.json and all Python gate scripts
- .cursor/skills/ with all ten skill SKILL.md files
- .cursor/agents/ with all fourteen agent definitions
- .cursor/rules/ new sage-session.mdc and phase-context.mdc
- .cursor/templates/ session manifest template
- .skill-update-triggers/ and .skill-update-staging/ directories"

git push origin main
```

### Step 3 — Confirm branch protection on main

In GitHub repository settings → Branches → Branch protection rules.
If a rule for `main` already exists, confirm these settings are active.
If not, add a new rule:

| Setting | Required value |
|---|---|
| Require pull request before merging | ✅ |
| Required approvals | 1 (Lead Dev) |
| Dismiss stale reviews on new commits | ✅ |
| Require status checks to pass | ✅ (existing ADO pipeline checks carry over) |
| Restrict push to main | Lead Dev only |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

### Step 4 — Configure Linear ↔ GitHub integration

In Linear Settings → Integrations → GitHub:
- Connect the `your-organisation` GitHub organisation
- Enable: auto-link commits to Linear issues via `LIN-[id]` in
  commit messages
- Enable: auto-link PRs to Linear issues
- Enable: update Linear issue status when PR merges to main

This means `LIN-4822` in a commit message or PR title automatically
appears on issue LIN-4822 in Linear — no manual linking required.

### Step 5 — Install filelock on all developer machines

The manifest file lock uses `filelock` for cross-platform
compatibility (Python's built-in `fcntl` is Unix-only;
Windows machines require `filelock` instead).

```powershell
pip install filelock
```

Run on every developer machine before the first SAGE session.

### Step 6 — Set environment variables on all developer machines

Each machine needs three environment variables before Cursor starts.
Run once in PowerShell (persists across restarts):

```powershell
[System.Environment]::SetEnvironmentVariable(
  "LINEAR_API_KEY", "lin_api_...", "User")
[System.Environment]::SetEnvironmentVariable(
  "NOTION_API_KEY", "secret_...", "User")
[System.Environment]::SetEnvironmentVariable(
  "M365_ACCESS_TOKEN", "...", "User")
```

Restart Cursor after setting environment variables.

> **M365 token note:** OAuth access tokens expire (typically 1 hour).
> Configure a service account with token refresh or use a long-lived
> token. The `kickoff-dev-review` skill will fail to fetch the Teams
> transcript if this token has expired.

---

## Part 2 — Worktree directory conventions

### Where worktrees live

Main clone (each developer's working copy):
```
C:\Users\[developer]\cursor-prof\Profitability\
```

Phase worktrees (all developers use the same `C:\Sage\worktrees\` root):
```
C:\Sage\worktrees\[FEATURE_ID]\phase-[N]\
```

Example for feature LIN-4821 with three phases:
```
C:\Sage\worktrees\LIN-4821\phase-1\   ← Developer 1
C:\Sage\worktrees\LIN-4821\phase-2\   ← Developer 2
C:\Sage\worktrees\LIN-4821\phase-3\   ← Developer 3
```

Each worktree is a full working copy of the repository checked out
to its own phase branch. They share the same git object store —
no disk duplication of history — but have completely independent
working directories. A file modified in `phase-1/` is invisible
to `phase-2/` until merged.

### Scope mapping to the Profitability repo structure

Four architectural layers drive phase splitting:

```
Database/
└── [Domain Folder]/               ← Stored procedure phases
    ├── usp_GetXxx.sql
    ├── usp_UpdateXxx.sql
    └── ...

Libraries/
├── Empyrean.Data/                 ← Data library phases
└── Empyrean.WS/                   ← Web services library phases

Services/
└── ProfitabilityAPI/              ← .NET API phases
    ├── Controllers/
    ├── Services/
    └── Models/

Web/
└── ProfitabilityWeb/              ← Angular UI phases
    └── src/app/features/[domain]/
```

**Typical Sprint phase breakdown for a domain feature:**

| Phase | Scope | Tier | Typical effort |
|---|---|---|---|
| 1 | `Database/[Domain]/` | 0 (starts immediately) | 2–4 hrs |
| 2 | `Libraries/Empyrean.Data/` + `Services/ProfitabilityAPI/` | 1 (after Phase 1) | 3–5 hrs |
| 3 | `Web/ProfitabilityWeb/src/app/features/[domain]/` | 1 (after Phase 1) | 3–5 hrs |

Phases 2 and 3 are both Tier 1 — both wait for Phase 1's stored
procedures to merge — but are independent of each other and run
in parallel during the build sprint.

The `phase-splitter` skill scans the actual repo at kick-off
to generate specific file paths for `scopedFiles` in the manifest.

---

## Part 3 — Worktree lifecycle

### Stage 1 — Create (automated by phase-splitter at kick-off)

After the team confirms the phase breakdown, `phase-splitter`
creates all worktrees:

```powershell
# Parameters from the phase breakdown (example)
$featureLinearId = "LIN-4821"
$phaseLinearId   = "LIN-4822"
$phaseNum        = "1"
$objective       = "expense-allocation-database"
$branchName      = "$phaseLinearId-phase-$phaseNum-$objective"
$worktreePath    = "C:\Sage\worktrees\$featureLinearId\phase-$phaseNum"

# Create the worktree on a new branch from main
git worktree add -b $branchName $worktreePath main

# Verify
git worktree list
```

Repeat for each phase. After all worktrees are created,
phase-splitter commits the initialised session manifest:

```powershell
git add .sage\sessions\$featureLinearId\
git commit -m "init: session manifest for [feature title] ($featureLinearId)

Phases: [N] | Tiers: [tier structure] | Mode: sprint"
git push origin main
```

Each developer pulls before starting S1:
```powershell
cd C:\Sage\worktrees\LIN-4821\phase-[N]
git pull origin main
```

### Stage 2 — Assign (verbal at kick-off, recorded in Linear + manifest)

Worktrees are created by phase-splitter. Developer assignment is
confirmed verbally at kick-off and recorded in:
- Linear phase issue assignee field
- `manifest.phases[N].runtime.assignedDeveloper`

Each developer opens their assigned worktree as a new Cursor window:
```
File → Open Folder → C:\Sage\worktrees\LIN-4821\phase-[N]
```

All build sprint activity happens in the worktree window.
The main clone is not used for phase work.

### Stage 3 — Build (S1–S8)

All file writes stay within the worktree's branch and scoped files.

**How hooks resolve paths from a worktree:**
`hooks_utils.find_repo_root()` walks up from `cwd` until it finds
`.git`. In a git worktree, this resolves to the main repo's `.git`
directory (worktrees share the object store). `get_session_root()`
then reads `.sage/sessions/active-session.txt` from the repo root.

This means `.sage/` manifest updates written from any worktree are
immediately visible to all other worktrees without a git pull.
The `manifest.lock` file prevents concurrent write corruption.

### Stage 4 — PR (after S8 completion report is posted)

```powershell
cd C:\Sage\worktrees\LIN-4821\phase-1

# Commit all phase artifacts
git add .
git commit -m "LIN-4822: phase 1 complete — expense allocation database

- usp_GetExpenseAllocationRules: retrieves active rules by department
- usp_UpdateExpenseAllocationRule: updates rule with audit logging
- usp_DeleteExpenseAllocationRule: soft delete with dependency check
- 26 TDD scenarios passing, 0 regressions
- Code review: 0 Critical, 1 Major (resolved)

Closes LIN-4822"

git push origin LIN-4822-phase-1-expense-allocation-database
```

Open PR on GitHub:
- **Base branch:** `main`
- **Title:** `[LIN-4822] Phase 1: Expense allocation database`
- **Description:** Link to phase completion report (`phase-{N}-completion-report.md`) + 2-sentence summary
- **Reviewer:** Lead Dev (required)
- **Labels:** `phase-complete`

Linear automatically links the PR to issue LIN-4822.

The existing ADO CI/CD pipelines trigger on the PR as normal:
- `profitability-db.yml` fires on changes to `Database/**`
- `profitability-api.yml` fires on changes to `Services/**`
  and `Libraries/**`
- `profitability-web.yml` fires on changes to `Web/**`

All status checks must pass before the Lead Dev merges.

### Stage 5 — Merge (in dependency order from manifest)

Merge order follows `manifest.sessionState.mergeOrder` established
at kick-off from the tier structure.

**Tier 0 phases merge first.** Tier 1 phases wait until all their
upstream Tier 0 PRs are merged.

Before merging a Tier 1+ phase, the developer incorporates upstream:

```powershell
cd C:\Sage\worktrees\LIN-4821\phase-2

# Pull main (now contains Phase 1 merged changes)
git fetch origin main
git merge origin/main
# Resolve any conflicts — minimal due to worktree isolation
git push origin LIN-4823-phase-2-allocation-api

# Re-run tests to confirm no regressions after incorporating Phase 1
```

**Merge strategy: Squash and merge.**
Keeps main history clean — one commit per phase.

Squash commit message format:
```
[LIN-XXXX] Phase N: [objective] (#PR-number)

[2-3 sentence summary of what was built]
Tests: [N] passing, 0 regressions
```

The Lead Dev performs all merges to `main`.

### Stage 6 — Prune (after all phases merged)

```powershell
cd C:\Users\[developer]\cursor-prof\Profitability
git fetch --prune

# Commit and archive session artifacts first
git add .sage\sessions\LIN-4821\
git commit -m "archive: session LIN-4821 complete — [feature title]"
git push origin main

# Remove worktrees
git worktree remove C:\Sage\worktrees\LIN-4821\phase-1 --force
git worktree remove C:\Sage\worktrees\LIN-4821\phase-2 --force
git worktree remove C:\Sage\worktrees\LIN-4821\phase-3 --force

# Delete remote branches
git push origin --delete LIN-4822-phase-1-expense-allocation-database
git push origin --delete LIN-4823-phase-2-allocation-api
git push origin --delete LIN-4824-phase-3-allocation-ui

# Clean up local worktree directories
Remove-Item -Recurse -Force C:\Sage\worktrees\LIN-4821

# Clear active session pointer
Clear-Content .sage\sessions\active-session.txt
```

`.sage/sessions/LIN-4821/` stays in the repo permanently as a
record of the session. It is not deleted.

---

## Part 4 — Branch naming

### Convention
```
LIN-[phase-issue-id]-phase-[N]-[kebab-objective]
```

| Component | Source | Example |
|---|---|---|
| `LIN-` | Always literal | `LIN-` |
| `[phase-issue-id]` | Linear phase issue ID | `4822` |
| `-phase-[N]` | Phase number | `-phase-1` |
| `-[kebab-objective]` | Objective in kebab-case, max 4 words | `-expense-allocation-database` |

**Full example:** `LIN-4822-phase-1-expense-allocation-database`

**Good objectives:** `allocation-rules-stored-procs` ·
`allocation-results-ui` · `expense-type-api` · `adjusted-gl-schema`

**Bad:** Too long · PascalCase · Too vague (`fix`, `update`)

---

## Part 5 — Commit message conventions

### During build
```
LIN-[phase-issue-id]: [brief description]
```

### Phase completion commit
```
LIN-[phase-issue-id]: phase [N] complete — [objective]

[2-3 sentences: what was built]
Tests: [N] passing, 0 regressions

Closes LIN-[phase-issue-id]
```

### Manifest updates (from main clone)
```
manifest(LIN-[feature-id]): [what changed]
```

### Workflow infrastructure
```
init: [description]
config: [description]
skill-update([skill]): [description]
hooks: [description]
```

---

## Part 6 — ADO to Linear transition

### What changes
Work item tracking moves from ADO to Linear.
Code, repo, CI/CD pipelines, and git workflows are unchanged.

### Clean cut

- Features in active ADO development: complete in ADO
- Features not yet in active development: get a Linear issue
  and enter the new workflow via the planning cycle
- No feature splits across both systems
- From the first new-workflow planning cycle: no new ADO work
  items created for Profitability development

### Legacy session artifacts

Any prior session artifact directories in `docs/` are historical reference only. All new session
artifacts go to `.sage/sessions/[FEATURE_ID]/`.

---

## Part 7 — Developer machine setup checklist

Complete before the first new-workflow session.

**All developers:**
- [ ] Confirm main clone at `C:\Users\[name]\cursor-prof\Profitability`
- [ ] Confirm `C:\Sage\worktrees\` directory exists (create if not)
- [ ] Pull latest `main` — confirm `.sage/` and updated `.cursor/` present
- [ ] `pip install filelock` in Cursor terminal
- [ ] Set `LINEAR_API_KEY` env var (PowerShell, User scope)
- [ ] Set `NOTION_API_KEY` env var
- [ ] Set `M365_ACCESS_TOKEN` env var
- [ ] Restart Cursor after setting environment variables
- [ ] Confirm Linear MCP connected in Cursor settings
- [ ] Confirm Notion MCP connected in Cursor settings
- [ ] Confirm Microsoft 365 MCP connected in Cursor settings
- [ ] `python --version` confirms 3.12.x
- [ ] `node --version` confirms v24.x

**Product Manager:** Same checklist. Primary use: prd-interviewer, prd-completeness-check, kickoff-dev-review, intel-advisor, planning cycle. Not running build phase lanes.

**Lead Dev:** Same checklist, plus:
- [ ] GitHub admin access confirmed on the organisation
- [ ] Branch protection rule on `main` confirmed
- [ ] Linear ↔ GitHub integration configured and tested
