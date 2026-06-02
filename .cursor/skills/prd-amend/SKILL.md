---
name: prd-amend
description: >
  PM-initiated amendment flow. When the PM edits prd.md, prd-amend runs or
  consumes a prd-stale-check report, generates a diff brief per STALE
  surface, and re-runs each surface via the Phase C three-surface manual
  handoff. Updates prdHash headers in each regenerated derivative. Emits
  prd_amend_initiated, prd_amend_brief_generated, and prd_amend_completed.
---

# PRD Amend

Orchestrates re-generation of derivative artefacts that have drifted from
an amended `prd.md`. The PM edits the PRD; this skill determines which
derivatives are STALE, generates a targeted **diff brief** for each STALE
surface, and guides the PM through re-running the corresponding manual
handoff chat. FRESH surfaces are never re-run.

**The PM is the sole PRD author.** This skill never edits `prd.md`. It
amends derivatives only.

**Three-surface handoff discipline applies.** Each STALE surface is
regenerated via the same paste-ready manual handoff pattern established in
Phase C of the PRD Pipeline Production-Grade Lift. One fresh Cursor chat
per surface; the handoff chat reads the amend brief, regenerates the
artefact, writes a `_summary.amend.md`, and STOPS. This skill reads the
summary on return.

---

## L1–L12 contract alignment (binding)

This skill inherits the locked L1–L12 contract from
[`prd-interviewer/references/downstream-agent-contract.md`](../prd-interviewer/references/downstream-agent-contract.md).
The binding alignment points specific to amend flow are:

- **Bundle discovery via `bundle-manifest.json`.** The list of derivative
  surfaces eligible for amendment is taken from
  `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` (consumed via
  the stale-check report in `auto` mode). The amend brief's Section 1
  cites the manifest entry for each amended file along with its current
  `prdHash` and the new PRD hash.
- **Family N anchor extraction discipline (inherited from interviewer P9).**
  Every amend brief carries the same Section 3 read-list shape used in the
  fresh-interview briefs: `{ path, read_mode, expected_anchors }` per cited
  YAML. The handoff chat's `_summary.amend.md` MUST carry a `## YAML reads`
  H2 table with `anchors_extracted` populated verbatim from each YAML. On
  return, this skill verifies each anchor by reading only the cited YAML
  files (not the heavy artifact). Anchor mismatches route through L11 C2:
  - Structural mismatch → tighter brief, re-handoff.
  - Copy mismatch → re-handoff with brief amendment.
  - YAML-vs-PM contradiction → escalate to `prd-orchestrator`.
  - Cosmetic → accept into PRD §7 Open Items via the PM.
- **N5 spot-check on return.** As with the interviewer's P9 validation,
  the amend skill randomly opens one or more rows of the regenerated
  artifact and confirms against the YAML in addition to the anchor table
  read.
- **Sequential `AC-NNN` with `surface` field.** Amend briefs reference
  AC IDs in the new sequential `AC-NNN` form for new-format bundles; the
  legacy bucketed `AC-{REQ|EC|UI|ERR}-NNN` form is honoured for pre-lift
  bundles during the backfill-on-touch window.
- **`prdHash` update.** After the handoff chat returns and the summary is
  accepted, this skill (or the handoff chat itself, verified on return)
  updates the `prdHash` header in each regenerated derivative to the
  current SHA-256 of `prd.md`'s body content. The bundle-manifest entry
  for each amended file is updated with the new hash, the new `writtenAt`
  timestamp, and the producer (`handoff:demo` / `handoff:sample-data` /
  `handoff:component-spec`).

---

## Invocation modes

| Mode | How to invoke | Behaviour |
|---|---|---|
| `auto` | `prd-amend` / `run prd-amend` | Runs prd-stale-check internally first, then amends all STALE surfaces |
| `targeted` | `prd-amend --surface demo` / `prd-amend --surface sample-data` / `prd-amend --surface component-spec` | PM names a specific surface; prd-amend skips the stale-check and regenerates only the named surface |

In `targeted` mode the PM is asserting the surface needs regeneration —
prd-amend does not validate this assertion against the hash. It trusts
the PM.

---

## Inputs required

| Input | Source | Required |
|---|---|---|
| PRD | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md` | Yes |
| Stale-check report (`auto` mode) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/stale-check.md` | Yes in `auto` mode; generated internally if absent |
| Component specification | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md` | When component-spec surface is STALE |
| Acceptance criteria | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md` | When referenced by STALE surfaces |
| Demo summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_summary.md` | When demo surface is STALE |
| Demo behaviour manifest | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-behavior-manifest.md` | When demo surface is STALE |
| Sample-data summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_summary.md` | When sample-data surface is STALE |

---

## Outputs

| Output | Path | Written when |
|---|---|---|
| Demo amend brief | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_brief.amend.md` | Demo surface is STALE or targeted |
| Sample-data amend brief | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_brief.amend.md` | Sample-data surface is STALE or targeted |
| Component-spec amend brief | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec-brief.amend.md` | Component-spec surface is STALE or targeted (note: component-spec.md is a single file, not a folder; the brief lives at the sub-PRD root) |

Handoff chats produce these artefacts (read-only to prd-amend after
return):

| Output | Path |
|---|---|
| Amended demo HTML (and calculation demo if applicable) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-interactive.html` (overwritten) |
| Amended demo behaviour manifest | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-behavior-manifest.md` (overwritten) |
| Demo amend summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_summary.amend.md` |
| Amended sample-data JSON files | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/*.json` (overwritten) |
| Sample-data amend summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_summary.amend.md` |
| Amended component specification | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md` (overwritten) |
| Component-spec amend summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec/_summary.amend.md` |

---

## Steps

### Step 1 — Determine stale surfaces; emit `prd_amend_initiated`

**In `auto` mode:**

1. Check whether `.sage/prds/[FEATURE_ID]/[sub-prd-id]/stale-check.md`
   exists and was generated after the most recent edit to `prd.md`.
   - If yes, read it to extract the list of STALE surfaces.
   - If no (or the report is older than the PRD), run prd-stale-check
     in-session (follow `prd-stale-check/SKILL.md` Steps 1–4) before
     proceeding. Read the resulting `stale-check.md`.
2. Collect `staleSurfaces` — the list of surfaces whose status was
   STALE or MISSING.

**In `targeted` mode:**

1. Treat the PM-named surface as the sole member of `staleSurfaces`.

After determining `staleSurfaces`, emit `prd_amend_initiated`:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_amend_initiated",
  "workflowKind": "prd_amend",
  "prdRunId": "<prdRunId from prd.md front-matter or new UUID v4>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "mode": "auto" | "targeted",
  "staleSurfaces": ["demo", "sample-data", "component-spec"]
}
```

If `staleSurfaces` is empty in `auto` mode, tell the PM all derivatives
are FRESH and STOP. Do not emit `prd_amend_completed` for a no-op run.

### Step 2 — Generate a diff brief per STALE surface; emit `prd_amend_brief_generated`

For each surface in `staleSurfaces`, write a diff brief. The diff brief
extends the standard Phase C brief format with an **Amend-mode addendum**
section.

**Diff brief structure (each surface):**

```markdown
# [Surface] Amend Brief — [FEATURE_ID] / [sub-prd-id]

**Type:** amend
**Timestamp:** <ISO 8601 UTC>
**New PRD hash:** <current SHA-256 of prd.md>
**Old derivative hash:** <prdHash from the stale derivative, or "absent">

## Section 1 — What changed in prd.md

<Quote the exact sections of prd.md that changed since the derivative
was generated. If the revision history identifies the changed sections,
name them. If not, quote all sections that touch the surface being
regenerated.>

## Section 2 — What the old derivative contained

<Quote the relevant section text from the existing derivative that is now
stale: the specific scenarios, data records, or component entries that
need to change. Cross-reference to the new PRD section above.>

## Section 3 — Named delta

<A plain-English list of exactly what must change in the regenerated
artefact. Each item names a scenario, data record, or component entry
and describes the change: add / remove / modify.>

## Section 4 — Regeneration instruction

<Surface-specific instruction for the handoff chat:>

For **demo**: Re-generate `demos/demo-interactive.html` (and
`calculation-demo.html` if applicable) and `demos/demo-behavior-manifest.md`
to reflect the named delta. Update the prdHash comment to
`<!-- prdHash: <new PRD hash> -->`. Write a `_summary.amend.md` at
`demos/_summary.amend.md` using the same structure as the original
`_summary.md`. STOP when done.

For **sample-data**: Re-generate the affected `sample-data/*.json`
files to reflect the named delta. Update the prdHash front-matter
in each affected file to `prdHash: <new PRD hash>`. Write a
`_summary.amend.md` at `sample-data/_summary.amend.md`. STOP when done.

For **component-spec**: Re-generate the affected sections of
`component-spec.md` to reflect the named delta. Update the prdHash
header at the top of `component-spec.md` to `prdHash: <new PRD hash>`.
Write a `_summary.amend.md` at `component-spec/_summary.amend.md`.
STOP when done.

## Section 5 — Hard rules (binding)

1. Produce only the files listed in Section 4.
2. Do not touch prd.md, acceptance-criteria.md, traceability.md,
   or any application source file.
3. Do not touch .cursor/skills/, .cursor/agents/, AGENTS.md, or any
   framework file.
4. Application-fidelity hard rule: any affordance that exists in the
   production application must mirror the cited component YAML exactly.
   No silent substitution.
5. Write `_summary.amend.md` and STOP. Do not proceed further.
```

After writing the brief, emit `prd_amend_brief_generated`:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_amend_brief_generated",
  "workflowKind": "prd_amend",
  "prdRunId": "<same as Step 1>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "surface": "demo" | "sample-data" | "component-spec",
  "briefPath": "<repo-relative path to the amend brief>"
}
```

### Step 3 — Present paste-ready handoff prompt to the PM

For each STALE surface, present the PM with a paste-ready handoff prompt.
Use the matching template from
`.cursor/skills/prd-interviewer/references/handoff-prompt-templates.md`
(Template 1 for demo, Template 2 for sample-data, Template 3 for
component-spec) with the following **amend-mode addendum** appended
before the closing line:

```
AMEND MODE. You are not building from scratch — you are amending an
existing artefact. Read the amend brief at:
  <repo-relative path to _brief.amend.md or component-spec-brief.amend.md>

Section 3 of that brief names the exact delta. Change only what the
delta specifies. Do not remove or restructure content that is not in
the delta. After amending, update the prdHash header in the artefact
to the new PRD hash listed in the brief. Write `_summary.amend.md`
(not `_summary.md`) to record changes made, deviations if any, and
open questions if any. Then STOP.
```

Instruct the PM:
> "Open a fresh Cursor chat and paste the prompt below exactly.
> Do not edit it. Return here when the chat reports `STOP`."

Process surfaces sequentially, waiting for the PM to confirm each
handoff chat has stopped before presenting the next prompt.

### Step 4 — Read summary on return; update prdHash header

When the PM confirms a handoff chat has stopped:

1. Read the `_summary.amend.md` the handoff chat wrote.
2. Validate that the declared artefact changes cover the named delta
   from the diff brief. If a delta item is missing from the summary,
   surface it to the PM and ask whether to re-run the handoff.
3. After the PM accepts the summary (or after resolving open questions),
   update the `prdHash` header in the regenerated artefact to the
   current SHA-256 of `prd.md` (the same hash embedded in the diff
   brief's Section 1).

   **prdHash update locations by surface:**
   - Demo: first `<!-- prdHash: ... -->` comment in `demo-interactive.html`
     (and `calculation-demo.html` if it exists).
   - Sample-data: `prdHash:` front-matter line at the top of each
     regenerated `.json` file.
   - Component-spec: `prdHash:` line in the first 10 lines of
     `component-spec.md`.

   The handoff chat is instructed to do this — verify it was done.
   If the handoff chat did not update the header, update it now.

4. Proceed to the next surface.

### Step 5 — Emit `prd_amend_completed`

After all surfaces are processed, emit:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_amend_completed",
  "workflowKind": "prd_amend",
  "prdRunId": "<same as Step 1>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "surfacesRegenerated": ["demo", "component-spec"],
  "surfacesSkipped": ["sample-data"]
}
```

`surfacesSkipped` lists surfaces that were FRESH (auto mode) or not
targeted (targeted mode). Tell the PM which surfaces were regenerated
and recommend running prd-stale-check again to confirm all derivatives
are now FRESH.

---

## Telemetry

| Event | Emitted at |
|---|---|
| `prd_amend_initiated` | Step 1 close — after stale surfaces are determined |
| `prd_amend_brief_generated` | Step 2 — once per surface, after brief is written |
| `prd_amend_completed` | Step 5 — after all surfaces are processed |

`workflowKind` for all events: `"prd_amend"`.

Event contracts defined in
`.cursor/skills/prd-interviewer/references/telemetry-schema.md` §4.

---

## Constraints

- **Never regenerates FRESH surfaces** (in `auto` mode). Only STALE or
  MISSING derivatives are processed.
- **Never edits `prd.md`.** The PM is the sole PRD author.
- **Never edits `acceptance-criteria.md` or `traceability.md`** directly.
  These may need to be regenerated separately by the PM or the
  prd-interviewer skill if the PRD change is substantial.
- **One handoff chat per surface** — inherits the Phase C three-surface
  handoff discipline. Paste-ready prompt per surface. PM orchestrates.
  Interviewer reads `_summary.amend.md` only.
- Inherits the production-grade quality bar from
  `.cursor/skills/prd-interviewer/references/production-grade-quality-bar.md`.
- Inherits the application-fidelity hard rule from
  `.cursor/skills/prd-interviewer/references/sub-agent-delegation.md` §4.
- Does not update `traceability.md` — a traceability re-run is a separate
  PM-initiated step after all surface amendments are complete.

---

## Reference files

| File | Purpose |
|---|---|
| `.cursor/skills/prd-stale-check/SKILL.md` | Prerequisite — run before prd-amend in auto mode |
| `.cursor/skills/prd-interviewer/references/handoff-prompt-templates.md` | Base templates for paste-ready handoff prompts |
| `.cursor/skills/prd-interviewer/references/sub-agent-delegation.md` | Three-surface handoff discipline and application-fidelity rule |
| `.cursor/skills/prd-interviewer/references/telemetry-schema.md` | Telemetry event contracts |
| `.cursor/skills/prd-interviewer/references/production-grade-quality-bar.md` | Quality bar inherited by this skill |
