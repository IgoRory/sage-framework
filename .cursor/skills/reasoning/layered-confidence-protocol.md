# Layered Confidence Protocol

Reference document for skills and agents that use a layered planning funnel
(L1 → L2 → L3) or produce review findings. Skills read this file to apply
consistent back-revision, deferral, confidence classification, and false-positive
filter behaviour. Do not invoke this file directly — it is a protocol reference,
not a skill.

Skills and agents using this protocol:
- `.cursor/skills/dev-plan/SKILL.md`
- `.cursor/skills/phase-splitter/SKILL.md`
- `.cursor/agents/traceability-reviewer.md`
- `.cursor/agents/code-reviewer.md`
- `.cursor/agents/security-reviewer.md`

---

## Confidence classification

Use this three-level scheme to classify any finding, dependency claim, or
challenge at any level of the funnel.

| Confidence | Meaning |
|---|---|
| verified-in-code | Traced to a specific file, method, data contract, or schema element in the codebase. The agent can cite the exact path and line or signature. |
| inferred | Derived from PRD language or design intent. No direct code trace found, but the PRD section that implies it is documented. |
| assumption | Based on domain knowledge or prior experience. No PRD section or code evidence supports it. |

**Usage rules:**

- `verified-in-code` and `inferred` findings may drive decisions at the current
  level, provided the source is cited.
- `assumption` findings must be listed separately in an "Unverified" or
  "Unverified dependencies" section. They do not drive decisions until confirmed
  by the developer/team or verified in code.
- Before listing a challenge or dependency as `inferred` or `assumption`, the
  agent must first search scoped files and requiredReferences for a code
  trace. If found, the classification upgrades to `verified-in-code`.

---

## Level interaction model

Each level in the funnel (L1, L2, L3) is presented for review before the next
begins. The reviewer responds with one of three actions:

| Response | Meaning | Funnel behaviour |
|---|---|---|
| **Approve** | Accept the level as written | Proceed to the next level |
| **Correct [item]** | A specific item is wrong | Patch that item only; re-present the affected section; do not re-run the whole level |
| **Defer [item] — unblocks when [condition]** | Decision parked with a named trigger | Mark item as deferred; carry it forward; proceed to the next level |

Do not proceed to the next level until the current level has received an explicit
Approve, or Approve-with-corrections-and-deferrals. Silence is not approval.

If a back-revision is needed at the current level (a prior level decision was
found to be wrong), surface it before presenting the current level for review.
See Back-revision rules below.

---

## Back-revision rules

Back-revision handles the case where work at a later level reveals that a prior
level decision was wrong. The funnel goes forward by default, but any level can
trigger a targeted patch to a prior level.

**How to trigger:**

Surface the back-revision explicitly before continuing. State:
- Which prior level item is wrong
- Why it is wrong (what the current level revealed)
- What the patch should be

Never silently contradict a prior level or work around an incorrect decision.

**Scope of the patch:**

The revision is scoped to the specific item that changed — not a full re-run of
the prior level. If L1 has ten decisions and one is wrong, only that one is
patched.

**Approval:**

The developer/team approves the patch before the current level resumes.
Approval can be a single-line confirmation if the revision is unambiguous.

**Artifact update:**

After approval, update the prior level artifact in place. Append the following
change note to the patched item:

`[Revised during L{N} — {reason}]`

where `{N}` is the level that triggered the revision and `{reason}` is a
one-line description of what changed.

**Downstream recheck:**

Identify all decisions at intermediate levels that were built on the patched
item. Mark each one `needs-recheck` before continuing. Only `needs-recheck`
items are revisited — other intermediate decisions are preserved.

**Level counter:**

A back-revision does not reset the level counter. If L2 triggers a back-revision
to L1, L2 groupings already approved are not discarded.

---

## Deferral rules

Deferral is distinct from escalation.

- **Escalation** — the agent cannot resolve this; the developer/team decides now.
- **Deferral** — the decision is parked; here is the named condition that will
  unblock it.

**Condition requirement:**

Every deferred item must name its unblocking condition. An item without a
condition is an escalation, not a deferral. Examples:

- Valid: "This unblocks when the Phase 2 DAL interface is finalised."
- Valid: "This unblocks when the PM confirms the empty-state requirement."
- Invalid: "We'll decide later."
- Invalid: "TBD."

**Carry-forward:**

Deferred items carry forward into every subsequent level explicitly. They do not
silently disappear. At each level, the agent lists all open deferrals (from prior
levels and the current level) in a dedicated `## Deferred items` or
`## Open deferrals` section.

**Final artifact:**

The final L3 artifact must include an `## Open deferrals` section listing all
items that remain unresolved at conclusion. Write "None" if all items are
resolved. This section is for the developer/team to see exactly what is
unresolved before the next stage begins.

**Downstream treatment:**

Skills that consume the final artifact (e.g. `implementation-planner` reading a
`dev-plan`) treat documented deferrals as acknowledged gaps, not missing
content. Gate artifacts that check for completeness (e.g. `traceability-reviewer`)
do not raise Blocker findings for items documented in `## Open deferrals` with
named conditions.

---

## Review agent integration

Review agents (traceability-reviewer, code-reviewer, security-reviewer) apply
the confidence classification and false positive filter from this protocol to
findings before writing them to their artifact.

### Pre-raise check (required before writing any finding)

Before writing a finding at any severity, the agent must:

1. Classify confidence:
   - verified-in-code — specific file, line/procedure, and reproducible scenario
   - inferred — pattern or design implies the issue; no direct code path confirmed
   - assumption — theoretical concern with no file or code evidence

2. Check acknowledged deferrals: if the issue relates to a scenario or
   decision documented in the phase's `## Open deferrals` section (from the
   dev-plan or interview summary), it is an acknowledged gap — do not raise
   it as a finding.

3. Check existing mitigations: search scoped files for an existing pattern
   that already addresses the concern. If found, cite it and do not raise
   the finding.

Only after passing all three checks write the finding, with its confidence
level stated.

### Confidence-to-severity mapping for review agents

| Confidence | Maximum severity |
|---|---|
| verified-in-code | Critical / Blocker |
| inferred | Major |
| assumption | Filtered out — do not write |
