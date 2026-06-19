---
name: prd-walkthrough
description: >
  PM-initiated walkthrough of a completed sub-PRD bundle. Presents PRD
  overview, functional surfaces, reuse posture, demo highlights, sample-data
  shape, open ambiguities, and traceability coverage statement in chat without
  reading full artefact files when a _summary.md exists. Read-only. Emits
  prd_walkthrough_run on each invocation.
---

# PRD Walkthrough

Presents a completed sub-PRD bundle to the PM in a structured, readable
format without requiring the PM to open multiple files. Pulls the high-signal
content from each artefact — using `_summary.md` files where they exist —
and surfaces open ambiguities and coverage gaps that need PM attention.

**Read-only.** This skill never modifies any artefact. It presents; the PM
reviews.

**Summary-first discipline.** When a `_summary.md` exists for a surface
(demos, sample-data), read only the summary by default. Deep-read the full
artefact only when the PM challenges a specific item during the walkthrough.
This honours the T2/T6 context-reduction techniques from the PRD Pipeline
Production-Grade Lift.

---

## L1–L12 contract alignment (binding)

This skill consumes prd-interviewer bundles produced against the locked
L1–L12 architectural model. The binding alignment points specific to
walkthrough flow are:

- **Bundle discovery via `bundle-manifest.json`.** The list of files this
  skill walks is taken from
  `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` (finalised
  by the interviewer at end of P9). The manifest's `files[]` array names
  every derivative that belongs to the bundle; this skill iterates that
  array to know which surfaces to present in the walkthrough. Heuristic
  disk discovery is forbidden — if a surface's `_summary.md` is named in
  the manifest but absent on disk, present `[MISSING — declared in
  manifest, file absent on disk]` for that surface. If the manifest
  itself is absent (pre-lift bundle), fall back to the legacy disk-walk
  Inputs table below.
- **§4 sub-section IDs in functional surfaces section.** Section B of the
  walkthrough names surfaces using the §4 sub-section labels and the
  `{PREFIX}-NNN` IDs that populate each sub-section (e.g. "Edit view —
  UI-001..UI-007, WF-002, VC-003"). Surfaces flagged `Not applicable —
  [reason]` in the PRD are listed with their N/A status, not silently
  omitted.
- **Sequential `AC-NNN` with `surface` field in coverage statement.**
  Section G consumes the bidirectional AC ↔ §4.NNN trace from
  `traceability.md` using the new sequential `AC-NNN` form for
  new-format bundles; the legacy bucketed `AC-{REQ|EC|UI|ERR}-NNN` form
  is honoured for pre-lift bundles during the backfill-on-touch window.

---

## Inputs required

| Input | Source | Required |
|---|---|---|
| PRD | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md` | Yes |
| Bundle manifest (file inventory + per-file `prdHash`) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` | Yes (new-format bundles); legacy disk-walk fallback during the backfill-on-touch window |
| Reuse map | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/reuse-map-draft.md` (or `reuse-map.md` if PM has confirmed it) | Yes |
| Demo behaviour manifest | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-behavior-manifest.md` | Yes (if demo surface exists per manifest) |
| Demo summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_summary.md` | Read in preference to full HTML; if absent, note as MISSING |
| Sample-data summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_summary.md` | Yes (if sample-data surface exists per manifest) |
| Component-spec summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec/_summary.md` | Yes (if component-spec surface exists per manifest) |
| Traceability | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/traceability.md` | Yes (high-level coverage section only by default) |

If any required input is MISSING, name it in the walkthrough output under
the relevant section with the note `[MISSING — not generated yet]`.

---

## Output

**In-chat presentation only.** No file is written by this skill. The
walkthrough is delivered as a structured chat response with the sections
listed below. The PM reads it in the chat window.

The only file-system effect is the telemetry emit (see Telemetry section).

---

## Steps

### Step 1 — Read inputs (summary-first)

1. Read `prd.md` in full. Extract the `prdHash` from the front-matter
   (if present) for the telemetry payload.
2. Read `reuse-map-draft.md` (or `reuse-map.md`).
3. Read `demos/demo-behavior-manifest.md` — the manifest lists named
   scenarios without requiring the full HTML file to be read.
4. Read `demos/_summary.md` if it exists (summary-first). Do NOT read
   `demo-interactive.html` unless the PM challenges a specific scenario
   in the walkthrough.
5. Read `sample-data/_summary.md` — summary only. Do NOT read individual
   `.json` files unless the PM challenges a specific record.
6. Read the high-level coverage section of `traceability.md` only
   (typically the first section or the summary table). Do NOT read the
   full per-requirement trace unless the PM challenges a specific gap.

### Step 2 — Produce the walkthrough in chat

Present the following seven sections in order. Keep each section concise —
the PM is reviewing, not reading a document.

---

**Section A — PRD overview**

One paragraph distilled from PRD §1 (Feature title and context), §2
(Problem statement), and §3 (Scope). Name the feature, the PM-stated
problem it solves, and the declared scope boundary in plain English.

---

**Section B — Functional surfaces**

A brief list derived from PRD §4 (Requirements / functional surfaces).
Name each surface (e.g., "Read view", "Edit view", "Save action",
"Export") with a one-line description of what the user can do on it.
Do not quote full requirements — one line per surface.

---

**Section C — Reuse posture**

A grouped plain-English summary from the reuse map. Group by reuse
decision:

- **Reuse as-is:** [component names] — no changes needed.
- **Reuse with modifications:** [component names] — brief description
  of what changes.
- **New components:** [component names] — brief description.

Cite the file: "Full reuse map at `reuse-map-draft.md`."

Do not reproduce the full table. If `pmOverrideCount` is available from
`reuse_map_confirmed` telemetry, note the override count as context.

---

**Section D — Demo highlights**

Named scenarios from `demos/demo-behavior-manifest.md`. List each
scenario by name and one-line description. If more than six scenarios
exist, list the first six and note "and N more — see manifest."

Cite the demo file: "Full demo at `demos/demo-interactive.html`."

If the demo summary (`_summary.md`) reported any deviations or open
questions, surface them here as a `> Note:` callout.

---

**Section E — Sample-data shape**

From `sample-data/_summary.md`:
- Number of records per entity type.
- Edge cases covered (null values, empty entities, maxima).
- Any schema validation failures or open questions from the summary.

If the summary is MISSING, state: `[MISSING — sample-data not yet
generated. Run the sample-data handoff.]`

---

**Section F — Open ambiguities**

Read PRD §15 (Open items / ambiguities). Surface every unresolved item
as a numbered list. If §15 is absent or empty, state:
"No open ambiguities recorded in PRD §15."

Also surface any unresolved open questions from the demo, sample-data,
or component-spec summaries if they were flagged.

---

**Section G — Coverage statement**

From the high-level coverage section of `traceability.md`:
- Total requirements in PRD.
- Requirements with full forward-trace (demo + sample-data + component-
  spec).
- Requirements flagged as not-demoable or partially covered (name them).
- Any backwards-trace gaps (artefact elements with no PRD requirement).

If `traceability.md` is MISSING, state: `[MISSING — traceability not
yet generated.]`

---

### Step 3 — Emit `prd_walkthrough_run`

After presenting all seven sections, emit:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_walkthrough_run",
  "workflowKind": "prd_walkthrough",
  "prdRunId": "<prdRunId from prd.md front-matter or new UUID v4>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "prdHash": "<SHA-256 of prd.md, or 'not present' if front-matter carries no hash>"
}
```

### Step 4 — Handle PM challenges (on demand)

If after the walkthrough the PM says "show me the full X" or "tell me more
about scenario Y", deep-read the relevant artefact section and respond
in chat. This does not trigger a new telemetry emit.

---

## Telemetry

| Event | Emitted at |
|---|---|
| `prd_walkthrough_run` | Step 3 — once per skill invocation, after all seven sections are presented |

`workflowKind`: `"prd_walkthrough"`.

Event contract defined in
`skills/prd-interviewer/references/telemetry-schema.md` §4.

---

## Constraints

- **Read-only.** Never modifies any artefact, any framework file, or any
  application source file.
- **Summary-first.** Never reads a full surface artefact (HTML, JSON,
  full component-spec) when a `_summary.md` for that surface exists and
  the PM has not challenged a specific item. This is the T2/T6 discipline
  from the PRD Pipeline Production-Grade Lift.
- **One telemetry emit per invocation** — `prd_walkthrough_run` at Step 3.
  No additional events emitted during PM challenge handling (Step 4).
- Inherits the production-grade quality bar from
  `skills/prd-interviewer/references/production-grade-quality-bar.md`.

---

## Reference files

| File | Purpose |
|---|---|
| `skills/prd-interviewer/references/telemetry-schema.md` | Telemetry event contracts |
| `skills/prd-interviewer/references/production-grade-quality-bar.md` | Quality bar inherited by this skill |
| `skills/prd-stale-check/SKILL.md` | Run before walkthrough if PM suspects drift |
| `skills/prd-amend/SKILL.md` | Run after walkthrough if PM decides to amend stale surfaces |
