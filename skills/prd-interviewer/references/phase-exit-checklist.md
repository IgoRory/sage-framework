# Phase Exit Checklist

Reference for the PRD Pipeline Production-Grade Lift. Reusable across every
phase of the lift (A–E) and any future multi-phase work that follows the
same Profitability-only / sage-framework-mirror pattern.

This checklist defines the "done" bar for any single phase of a phase-gated
lift. The checklist is non-negotiable — a phase is not done until every item
passes. The PM signs off the gate after walking the checklist with the
phase-completion report.

---

## When to run

- Immediately before writing the phase's completion report.
- After every item below has been satisfied in the working tree.
- Once per phase. Re-walk only when an item changes status (e.g. a missed
  mirror path is added).

---

## 1. Per-phase done definition

A phase is done when ALL of the following are true:

### 1.1 Artifact completeness

- [ ] Every file declared in the phase plan's write paths has been written
  to the Profitability repo at the declared path. Modified vs new is
  correctly stated.
- [ ] No file was written outside the phase plan's declared write paths.
  Out-of-scope writes are recorded as Deviations or reverted.
- [ ] Every file marked "audit-and-keep" or "audit-and-modify" in the
  phase plan was read in full and its targeted edits applied. Retained
  legacy assumptions are surfaced under Deviations.

### 1.2 AGENTS.md and skill-reference list parity

- [ ] AGENTS.md updates required by the phase plan have landed in
  `AGENTS.md` at the Profitability repo root.
- [ ] Every skill whose `Reference files` section is affected by the phase
  has had that section updated to list the new or restructured references
  (no behavioural changes unless the phase plan explicitly permits them).
- [ ] No skill SKILL.md was edited beyond what the phase plan explicitly
  permits. Read-after-Write audit findings are documented for the phase
  the audit targets, not fixed in the audit phase.

### 1.3 Sync handoff log entry

- [ ] `docs/cursor/feature-sage-prd-interviewer-enhancements/
  sage-framework-mirror-log.md` has a new entry for this phase listing every
  Profitability path that needs to land in sage-framework on Rory's bulk sync
  post-Phase-E.
- [ ] The entry's mirrored-paths list matches the mapping table in
  `rules/dual-repo-sync.mdc` for every file the phase touched.
- [ ] Files not listed in the mapping table (e.g. Profitability-only docs)
  are explicitly called out as `not mirrored` with a one-line reason.

### 1.4 Hard-stop discipline

- [ ] None of the phase plan's "Hard stops" were violated. Verified by
  re-reading the Hard stops block and matching it against the working tree
  diff.
- [ ] No hooks, no `.sage/workflow-config.json`, no
  `.context/components/manifest.yaml` changes were made unless the phase
  plan explicitly authorises them.
- [ ] No downstream-consumer paths were updated unless the phase plan
  explicitly authorises them (consumer wiring is reserved for the phase
  that owns it — typically Phase D.5).

### 1.5 Completion report

- [ ] Completion report exists at the phase plan's declared path
  (typically `docs/cursor/feature-sage-prd-interviewer-enhancements/
  phase-[X]-completion-report.md`).
- [ ] The report has the required H2 sections in the order declared by the
  phase plan.
- [ ] The Files Written table lists every Profitability row concretely and
  every mirrored sage-framework row as `Pending bulk sync`.
- [ ] Deviations section is populated (or "None") with a one-line reason
  per deviation.
- [ ] Open questions for the PM gate are surfaced explicitly.

### 1.6 PM walkthrough

- [ ] PM walkthrough is scheduled (or asynchronously requested) with the
  completion report attached or linked.
- [ ] PM gate checklist is included in the completion report so the PM can
  sign off item-by-item.
- [ ] PM sign-off is recorded in the completion report (or in a successor
  artifact when sign-off arrives) before the next phase begins.

---

## 2. Per-phase rollback procedure

Every phase ships on a feature branch. A phase is rolled back by reverting
all commits that contributed to the phase's diff on that branch and
re-opening the phase for re-execution.

### 2.1 Rollback triggers

- The PM rejects the phase at the gate with `REJECT: [reason]`.
- A defect surfaces post-gate that is severe enough to block the next phase
  (e.g. a misplaced edit that breaks a hook, an AGENTS.md update that
  contradicts a locked decision).
- A subsequent phase discovers the current phase's outputs are incompatible
  with the next phase's plan and the conflict cannot be reconciled forward.

### 2.2 Rollback steps

1. **Identify the phase's commit range.** Use `git log` to find the first
   and last commits authored under this phase on the feature branch.
2. **Revert the range.** `git revert --no-edit [first]^..[last]` creates
   inverse commits without rewriting history. This preserves the audit
   trail of what was done and what was rolled back.
3. **Re-open the phase.** Update the phase's todos to `pending`. Update
   the completion report (or write a successor) noting the rollback,
   the trigger, the commit range reverted, and the corrective plan.
4. **Re-walk from the phase's first authoring step.** Apply the corrective
   plan. Re-run this checklist before re-writing the completion report.
5. **Remove the rolled-back paths from the sync-handoff log.** Edit
   `sage-framework-mirror-log.md` to strike through the rolled-back entry
   (do not delete — the strike-through preserves the bulk-sync diff
   history).
6. **Notify the PM** in the same channel that received the original
   completion report. Include the rollback report.

### 2.3 What rollback does NOT do

- Rollback does NOT touch sage-framework — the deferred-sync convention
  means no sage-framework commit has been made for the rolled-back phase
  in the first place. The sync-handoff log entry is amended.
- Rollback does NOT delete the original commits. The revert chain preserves
  the audit trail.
- Rollback does NOT re-run subsequent phases unless they read the
  rolled-back outputs as inputs. If they did, those phases are also
  reverted under the same procedure, in reverse order.

---

## 3. Reusability across phases

This checklist is reusable as-is for any phase of the current lift (A–E)
and any future multi-phase work that follows the same Profitability-only /
end-of-lift-mirror convention. Per-phase variations (specific Hard stops,
specific declared write paths) live in the phase plan; this checklist
governs the bar every phase clears regardless.

If a future phase introduces a new gate dimension (e.g. a perf budget, a
backward-compat constraint), append a new section to this file rather than
forking it.
