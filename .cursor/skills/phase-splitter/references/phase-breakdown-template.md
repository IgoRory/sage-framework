# Phase Breakdown Template

Use this template to produce the phase breakdown document. Save as
`[SESSION_ROOT]/phase-breakdown.md`. This document feeds the session
manifest and becomes the source of truth for Linear issue creation
and worktree setup.

---

```
# Phase Breakdown
# [Feature title]

**PRD:** [Notion link]
**Linear feature issue:** [issue ID and link]
**Generated:** [ISO datetime]
**Status:** [Draft — awaiting team confirmation / Confirmed]

---

## Summary

**Phase count:** [N]
**Tier structure:** [N] phases in Tier 0 · [N] in Tier 1 · [N] in Tier 2
**Total effort estimate:** [low]–[high] hours across [N] phases
**Calendar time estimate:** [low]–[high] hours
  (based on critical path: [Phase N → Phase N → Phase N])
**Recommended mode confirmation:** [Sprint / Pair]
  [If mode recommendation differs from planning cycle assignment, explain why]

**Independence flags:** [N phases flagged — see below]
  [If none: "None — all phases score ≥ 60"]

---

## Phase definitions

---

### Phase 1: [Objective name]

**Tier:** 0 (starts immediately)
**Effort estimate:** [low]–[high] hours
**Developer profile:** [UI-heavy / Backend-heavy / Full-stack / Data-only / Any]
**Independence score:** [0–100]
**Linear issue:** [to be created]
**Worktree branch:** `LIN-[id]-phase-1-[kebab-objective]`

**Objective:**
[One sentence. What will exist after this phase that didn't exist before?]

**Scope — files owned by this phase:**

UI files:
- [file path] — [new / modified] — [brief description]
...

Backend / API files:
- [file path] — [new / modified] — [brief description]
...

Data / schema files:
- [file path] — [new / modified] — [brief description]
...

Test files:
- [file path] — [new / modified] — [brief description]
...

**Dependencies:**
Upstream (must complete before this phase starts):
- None (Tier 0)

Downstream (phases that depend on this phase):
- Phase [N]: [what it depends on from this phase]

**Interface contract (if downstream phases exist):**
[What exactly this phase will produce for downstream consumers:
 function signatures, return types, data shapes, field names, error codes.
 Downstream phases build against this contract.]

[If no downstream dependencies: "None required."]

**TDD spec notes:**
[Any specific test scenarios the TDD spec must cover — edge cases,
 error conditions, or calculation verifications specific to this phase]

---

### Phase 2: [Objective name]

**Tier:** [0 / 1 / 2]
**Effort estimate:** [low]–[high] hours
**Developer profile:** [UI-heavy / Backend-heavy / Full-stack / Data-only / Any]
**Independence score:** [0–100]
[If score < 60: ⚠️ FLAG — see Independence flags section below]
**Linear issue:** [to be created]
**Worktree branch:** `LIN-[id]-phase-2-[kebab-objective]`

**Objective:**
[One sentence.]

**Scope — files owned by this phase:**
[Same structure as Phase 1]

**Dependencies:**
Upstream:
- Phase [N]: [specifically what is needed — SP name, field name, component]

Downstream:
- [Phase N: what it depends on from this phase, or "None"]

**Interface contract:**
[If upstream dependencies exist: what this phase expects to receive,
 and what it will produce.]

**TDD spec notes:**
[Phase-specific test scenarios]

---

[Repeat for each phase]

---

## Dependency map

[Visual or tabular representation of the execution tiers]

Tier 0 (parallel start):
  Phase 1: [name]
  Phase 3: [name]

Tier 1 (unlocks when upstream Tier 0 completes):
  Phase 2: [name] — depends on Phase 1
  Phase 4: [name] — depends on Phase 3

Tier 2 (unlocks when upstream Tier 1 completes):
  Phase 5: [name] — depends on Phases 2 and 4

Critical path: Phase 1 → Phase 2 → Phase 5
Critical path duration: [low]–[high] hours

---

## Independence flags

[Only present if any phase scored below 60. List flagged phases with
resolution options.]

⚠️ Phase [N] — Independence score: [score]

Reason: [What dependency causes the low score]

Resolution options:
A) [Re-split option — if a clean boundary exists]
B) [Accept with explicit interface contract — describe the contract]
C) [Run sequentially rather than in parallel — impact on timeline]

Team decision: [to be confirmed at kick-off]

---

## Files not yet in codebase

[List of files in phase scopes that do not currently exist —
 they will be created during the build sprint. These cannot be
 validated by the manifest but are expected new files.]

- [file path] — Phase [N] — [description]
...

[If none: "All scoped files exist in the codebase."]

---

## Pyramid / shared work stream items excluded

[If any PRD scope was excluded from the breakdown due to being a
 separate work stream — e.g. Pyramid model updates, reporting
 data model changes — list them here with the responsible party.]

- [item]: [separate work stream / owner]
...

[If none: "None — all PRD scope is covered in the phase breakdown."]

---

## Team confirmation

[Completed at kick-off after team review]

Confirmed by: [names]
Date: [ISO date]
Changes from recommended breakdown: [list any adjustments made, or "None"]

Status: CONFIRMED — ready for Linear issue creation and worktree setup.
```
