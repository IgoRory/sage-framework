---
name: dev-plan
description: >
  Opt-in replacement for the S1 dev-interview. Instead of a Q&A interview,
  the agent investigates first and publishes findings as a structured,
  layered plan. The developer reviews and corrects the plan rather than
  answering questions the agent could have resolved from code. Produces three
  progressive artifacts: L1 (strategic), L2 (tactical), and the final
  phase-{N}-dev-plan.md (execution-ready S1 artifact). Use when the developer
  says "use dev-plan", "run dev-plan", or "skip the interview, use dev-plan".
  Do not run alongside dev-interview — this replaces it for the current phase.
---

# Dev Plan

Investigation-first replacement for S1 dev-interview. The agent does the
analytical work, publishes its findings as a plan, and the developer corrects
the plan rather than answering questions.

---

## Invocation phrases

Treat this skill as invoked when the developer says any of:

- "use dev-plan"
- "run dev-plan"
- "skip the interview, use dev-plan"
- "dev-plan for phase N"
- "use dev-plan for this phase"

In Mob mode, the orchestrator may invoke this skill instead of dev-interview
at a phase transition if `devPlanMode: true` is present in the session manifest
or workflow-config. Otherwise falls back to dev-interview.

---

## Step 0 — Context resolution

Before doing any investigation, resolve and state the working context.

1. Read `.sage/sessions/active-session.txt` → session ID.
2. Read `.sage/sessions/[session-id]/session-manifest.md` → full manifest,
   PRD path, phase list, scoped files, requiredReferences.
3. Read `SAGE_PHASE_ID` environment variable → phase number. If not set:
   - Scan manifest for the first phase where `currentStep = "dev-interview"`
     and no S1 artifact (`phase-{N}-dev-interview-summary.md` or
     `phase-{N}-dev-plan.md`) exists in the phase directory.
   - If still ambiguous, ask the developer: "Which phase should dev-plan run
     for? (e.g. phase 1, 2, ...)"
4. Check the phase directory for existing level artifacts:
   - `phase-{N}-dev-plan-L1.md` exists → resume from L2
   - `phase-{N}-dev-plan-L2.md` exists → resume from L3
   - Neither exists → start from L1
5. State what was found before acting:

> "Dev-plan — Phase [N]: [Title]
> Session: [session-id]
> Resume point: [L1 / L2 / L3]
> Scoped files: [list from manifest]
> PRD: [path]"

Do not proceed until Step 0 is complete and stated.

---

## Step 1 — Codebase investigation (feeds L1)

Launch a `feature-explorer` subagent with the following prompt, substituting
the phase's scope from the manifest:

```
Explore the feature area related to: [phase title / PRD feature name]

First classify the scoped implementation shape:
- API V1 / legacy Profitability stack
- ProfitabilityAPI.V2 / Clean Architecture
- Angular frontend
- SQL-only or stored-procedure-heavy
- Mixed V1/V2/frontend/data scope

Trace only the layers that apply to the scoped files and PRD.

For each layer, identify:
- SQL / stored procedures: all SPs, functions, tables, views, or seed scripts
- API V1 / legacy: DAL classes, service classes, controllers
- ProfitabilityAPI.V2 / Clean Architecture: Domain entities/value objects/
  policies, Application commands/queries/handlers/ports, Infrastructure
  repositories/EF/Dapper, Presentation endpoints, Contracts wire models,
  Shared utilities
- Angular frontend: components, services, routes, state, templates, styles,
  tests

Also identify:
- Configuration or settings objects related to this feature
- Shared utilities or helpers used across the feature area
- Existing patterns or conventions specific to this domain

For ProfitabilityAPI.V2 scope, apply the clean architecture guidance:
- If `.cursor/skills/clean-arch-guide/SKILL.md` is available, read it first.
- Fallback: Domain owns business rules; Application orchestrates use cases,
  transactions, ports, and mapping; Infrastructure owns EF Core, Dapper, SQL,
  repositories; Presentation owns endpoints, HTTP, auth, OpenAPI, Contracts
  mapping; Contracts are public wire models only.

Output a layer-by-layer table: file path | class/method/component | what it does
```

From the subagent findings, classify each TDD scenario:

| Classification | Meaning |
|---|---|
| Already exists | Current code satisfies this without changes |
| Needs extending | Existing code must be modified |
| Net new | No existing code serves this need |

Also identify duplication opportunities: existing SPs, DAL methods, services,
or Angular components that could be reused or extended rather than duplicated.

---

## Step 2 — Write L1 (Strategic)

Write `phase-{N}-dev-plan-L1.md` to `[SESSION_ROOT]/phase-{N}/`.

### L1 false positive filter

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the confidence
classification scheme (verified-in-code / inferred / assumption) and usage rules.

Apply before writing any challenge or risk:

- Only list a challenge if `confidence = verified-in-code` or `inferred`
  with the exact PRD section documented. `assumption` items go in the
  separate **Unverified** section.
- Before listing a challenge, search scoped files and requiredReferences for
  an existing solution. If found, record it in the "Existing solution found"
  column and classify the challenge as `extend`, not `net-new`.
- Do not list a risk without citing the specific code, PRD section, or
  cross-phase dependency that creates it.

### L1 artifact structure

```markdown
# Dev Plan L1 — Phase [N]: [Phase Title]

**Generated:** [ISO date]
**Session:** [session-id]
**Inputs reviewed:** [PRD path], [TDD spec path], [requiredReferences listed]

---

## Work groupings

| Grouping | TDD scenarios | Purpose |
|----------|--------------|---------|
| [Name] | [N.1, N.2] | [1-line purpose] |

---

## Delta analysis

| Scenario | Classification | Existing code reference |
|----------|---------------|------------------------|
| [N.1 title] | Already exists / Needs extending / Net new | [file path or "—"] |

---

## Technical challenges

| Challenge | Confidence | Existing solution found |
|-----------|------------|------------------------|
| [description] | verified-in-code / inferred-from-PRD | [file/pattern ref or "none found"] |

---

## Key risks

| Risk | Likelihood | Blast radius | Priority rank |
|------|-----------|-------------|---------------|
| [description] | high / med / low | phase / cross-phase / session | 1..N |

---

## Simplification opportunities

[Each entry: specific proposed change + the tradeoff if adopted]

---

## Planning priority order

[Work groupings ordered by uncertainty × blast radius.
High uncertainty + cross-phase blast radius = plan first.]

---

## Unverified items — developer input needed

[Only items with confidence = assumption. For each: what was checked,
what was not found, and the specific question or decision needed.]

---

## Deferred items

[Only if any. For each: what is deferred, why it cannot be resolved now,
named unblocking condition.]
```

### After writing L1

Present L1 to the developer and ask for one of:

- **Approve** — proceed to L2
- **Correct [item]** — patch that specific item and re-present L1
- **Defer [item] — unblocks when [condition]** — mark as deferred and proceed
- **Back-revision not applicable at L1** (L1 is the first level)

Do not proceed to L2 until the developer has explicitly approved L1 or approved
with documented corrections and deferrals.

---

## Step 3 — Write L2 (Tactical)

Generated only after L1 is approved. Drills into each work grouping in
priority order from L1.

### L2 false positive filter

- Do not raise an "Unresolvable" scenario unless the agent has checked the
  PRD, TDD spec, scoped files, and requiredReferences and the ambiguity
  genuinely cannot be resolved from those sources.
- For each potential escalation, first run a reconciliation subagent:

```
Reconcile the following open item using only these sources:
- PRD: [path]
- TDD scenario: [scenario text]
- Scoped files: [list]
- requiredReferences: [list]

Open item: [description]

Return: RESOLVED with source evidence, or UNRESOLVABLE with what was checked
and the specific decision the developer must make.
```

- Only raise items the reconciliation subagent marks `UNRESOLVABLE` as
  developer escalations.
- Escalations are a short evidence-backed list, not open-ended questions.
  Each must state: what was checked, what was found, and the specific decision
  needed (binary where possible).

### L2 artifact structure

Write `phase-{N}-dev-plan-L2.md` to `[SESSION_ROOT]/phase-{N}/`.

```markdown
# Dev Plan L2 — Phase [N]: [Phase Title]

**Generated:** [ISO date]
**Based on L1 approved:** [ISO date]

---

## Grouping [N]: [Name]

### Approach decision

[Chosen approach with justification. References existing pattern in codebase
where one exists — cite the file and pattern name.]

**Status:** Decided / Deferred — unblocks when [condition]

### Test strategy

[Which test layers apply and why. References existing test conventions from
scoped files — cite the test file pattern used.]

| Behaviour | Test layer | Test file pattern |
|-----------|-----------|------------------|
| [scenario N.X] | unit / integration / E2E / architecture guard | [path pattern] |

### Key constraints

[Performance, backward compatibility, data migration, cross-phase contracts —
only if verified from PRD or scoped code.]

### TDD scenario assessment

For each scenario in this grouping:

**Scenario [N.X]: [title]**
- Status: Confirmed / Needs refinement / Unresolvable / Deferred
- Evidence: [source file/section reference]
- Refinement: [specific proposed change, if status = Needs refinement]
- Escalation: [what was checked + binary decision needed, if Unresolvable]
- Deferral condition: [named trigger, if Deferred]

---

[Repeat for each grouping in priority order]

---

## Escalations requiring developer decision

[Consolidated list of all Unresolvable items across groupings.
Format: item ID | what was checked | decision needed]

---

## Deferred items carried from L1

[Any L1 deferrals still open, with their conditions.]

---

## New deferrals at L2

[Any items deferred during L2, with named unblocking conditions.]
```

### After writing L2

Present L2 and ask for one of:

- **Approve** — proceed to L3
- **Correct [item]** — patch and re-present the affected grouping only
- **Defer [item] — unblocks when [condition]** — mark deferred and proceed
- **Back-revision: [L1 item] needs changing because [reason]** — see Back-revision pathway

Resolve all escalations before proceeding. If the developer answers an
escalation, update the relevant scenario status to `Confirmed` or
`Needs refinement` with the developer's answer as evidence.

Do not proceed to L3 until L2 is approved (escalations resolved or explicitly
deferred with conditions).

---

## Step 4 — Write L3 (Execution — final S1 artifact)

Generated only after L2 is approved. This is the artifact `implementation-planner`
reads at S2.

Ask build mode once, at the start of L3 generation (not as part of an interview):

> "Before I write the final plan: Autonomous or Checkpoint build mode?
> - **Autonomous** (default): build runs end-to-end, you review at S6.
> - **Checkpoint**: pauses after each batch for your confirmation."
>
> If Checkpoint: "What batch boundary — database, api, ui, or full-stack?"

Write `phase-{N}-dev-plan.md` to `[SESSION_ROOT]/phase-{N}/`.

### L3 artifact structure

```markdown
# Dev Plan — Phase [N]: [Phase Title]

**Date:** [ISO date]
**Session:** [session-id]
**Build mode:** [autonomous | checkpoint]
[If checkpoint: **Batch boundary:** database | api | ui | full-stack]

---

## Scoped files

### Confirmed in scope
[List — may differ from manifest if additions/removals agreed during review]

### Read-only dependencies
[Files referenced but not modified]

---

## Codebase exploration findings

### Delta analysis
[Already exists / Needs extending / Net new per scenario — from L1]

### Reuse opportunities
[Specific SP/DAL/service/component that can be reused or extended — with paths]

---

## Work groupings and approach decisions

### Grouping [N]: [Name]
**Approach:** [decided approach — from L2]
**Test strategy:** [test layers and file patterns — from L2]
**Constraints:** [from L2]

---

## TDD scenario refinements

### Scenario [N.X]: [title]
**Status:** Confirmed | Refined | Deferred
**Changes:** [what changed, or "None"]
**Refined scenario (if changed):**
Given: ...
When: ...
Then: ...
**Deferral condition:** [if deferred — named unblocking trigger]

[Repeat for every scenario in the TDD spec]

---

## Implementation notes

[Bullet list of constraints, patterns, decisions, and cross-phase dependencies
consolidated from L1 and L2 review]

---

## Domain specifics

[Verified measures, source views, result tables, return codes, flags,
component states — only references with verified-in-code or inferred-from-PRD
confidence. No assumption-confidence references.]

---

## Open deferrals

[All items deferred across L1, L2, and L3 that are still unresolved.
Format: item | level deferred | unblocking condition]

[Write "None" if all items are resolved.]
```

### After writing L3

Tell the developer:

> "Dev Plan complete — `phase-{N}-dev-plan.md` written to the phase directory.
>
> S1 is complete. Invoke `implementation-planner` to begin S2.
> Note: implementation-planner can skip its own codebase exploration — the
> feature-explorer findings are already in this plan.
> [If open deferrals exist: N open deferral(s) are listed in the artifact.
> These become deferred tasks in the implementation plan.]"

---

## Back-revision pathway

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the full
back-revision protocol (how to trigger, patch scope, change note format,
needs-recheck propagation, level counter preservation).

**Trigger conditions specific to dev-plan:**

- L2 discovers an L1 priority ranking is wrong (a grouping ranked low is
  cross-phase blocking)
- L2 discovers an L1 challenge was misclassified (confidence level wrong,
  or referenced file does not support the claim)
- L2 discovers an L1 simplification opportunity is blocking a key approach
  decision, not optional
- L3 reveals a flawed L2 approach decision for a specific grouping

---

## Deferral pathway

Read `.cursor/skills/reasoning/layered-confidence-protocol.md` for the full deferral
protocol (condition requirement, carry-forward rules, open-deferrals section,
escalation vs deferral distinction).

**dev-plan-specific downstream treatment:**

- A deferred TDD scenario in L3 carries `status: deferred` with its condition.
  The `implementation-planner` converts it to a deferred task. The
  `traceability-reviewer` (S3) treats documented deferrals as acknowledged
  gaps, not Blocker findings.

---

## Constraints

- **Investigation before questions.** Never ask a question answerable from
  the codebase. Questions arise only from `confidence = assumption` items
  that the reconciliation subagent cannot resolve.
- **One correction pass per level.** Developer corrects L1, then L2. Not a
  conversation — a document review.
- **Solutions before problems.** Every challenge must include an "Existing
  solution found" check. If a solution exists, cite the file and pattern.
- **Priority drives order.** L2 drills into high-uncertainty +
  high-blast-radius groupings first.
- **Build mode asked once.** At the start of L3 generation only.
- **Defer with a condition or escalate.** The agent must distinguish these
  explicitly — never park an item without naming what unblocks it.
- **No product/source/config edits.** This skill is investigation and planning
  only. Writes only `phase-{N}-dev-plan-L1.md`, `phase-{N}-dev-plan-L2.md`,
  and `phase-{N}-dev-plan.md` to the phase directory.
- **Artifact-write only.** Do not modify the session manifest, TDD spec, PRD,
  or any file outside the active phase directory.

---

## Migration note

This skill currently runs without hook enforcement or gate recognition. It is
opt-in and self-enforcing. The long-term path is to promote it to a full SAGE
agent with:

- `plan-mode-enforcer` recognising `currentStep = dev-plan`
- `manifest-step-gate` accepting `phase-{N}-dev-plan.md` as a valid S1 artifact
- `devPlanMode` flag in the session manifest runtime
- Entry in `AGENTS.md` with artifact-write-only scope

This migration is deferred until the skill has been validated in practice.
