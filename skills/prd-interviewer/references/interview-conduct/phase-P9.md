# Phase P9 — Handoff briefs + on-return validation + traceability + bundle manifest

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines
only the P9-specific scope: authoring the three handoff briefs with
Family N N8 pre-extraction, handing the PM three paste-ready prompts,
on-return Family N N3 anchor verification + N5 spot-check,
auto-building `traceability.md` from the in-memory AC list + the
three handoff summaries, and finalising `bundle-manifest.json` at
end of phase.

**Phase ID:** `P9`
**Always asked. Runs after P8 PM walkthrough passes
([`phase-P8.md`](./phase-P8.md)).**

P9 is the bundle-closing phase. After P9 exits, the sub-PRD bundle
is complete and `prd-completeness-check` is the next downstream
consumer.

---

## Scope

P9 produces:

1. **Three handoff briefs** authored by the interviewer chat:
   - `demos/_brief.md` (when `requires_ui_demo` or
     `requires_calc_demo` from the breakdown)
   - `sample-data/_brief.md`
   - `component-spec/_brief.md`
2. **Three paste-ready prompts** handed to the PM verbatim from
   [`../handoff-prompt-templates.md`](../handoff-prompt-templates.md).
   The PM opens three fresh Cursor chats and pastes each prompt
   unchanged.
3. **On-return validation** of the three `_summary.md` files
   produced by the handoff chats — Family N N3 anchor verification
   against the YAML files only, N5 spot-check on random artifact
   rows, summary-schema conformance check (six required H2
   headings + `prdHash` frontmatter).
4. **Auto-built `traceability.md`** from the in-memory AC list +
   the three handoff summaries — table-only, deterministic, no
   narration.
5. **`bundle-manifest.json`** — finalised at end of P9; declares
   every file in the bundle with `prdHash`, `writtenAt`,
   `producer`, and `role`. Downstream consumers
   (`prd-stale-check`, `prd-walkthrough`, `kickoff-dev-review`,
   `phase-splitter`) iterate the manifest's `files[]` rather than
   heuristically discovering files on disk.

The heavy artifacts (`demo-interactive.html`,
`calculation-demo.html`, `sample-data/*.json`, `component-spec.md`)
are produced by the manual handoff chats — never by the
interviewer chat. See
[`../sub-agent-delegation.md`](../sub-agent-delegation.md) for the
full handoff contract.

---

## Step 1 — Load handoff references

At P9 entry, the interviewer loads two reference files:

- [`../sub-agent-delegation.md`](../sub-agent-delegation.md) —
  orchestration sequence, §5 brief format (12 mandatory sections
  including Section 3 `{ path, read_mode, expected_anchors }`),
  §6 summary contract (6 required H2 headings including
  `## YAML reads`), Family M application-fidelity hard rule,
  Family N N1–N8 handoff-chat read discipline, §K Tier 1
  inside-chat self-review protocol.
- [`../handoff-prompt-templates.md`](../handoff-prompt-templates.md)
  — three paste-ready prompts (demo / sample-data /
  component-spec) with the Family N Hard rules block reinforced.

These are the only reference files P9 loads beyond what was
already in memory from prior phases. No phase-module cross-reads
(per the L7 read-discipline rule).

---

## Step 2 — Author the three handoff briefs (Family N N8 pre-extraction)

Each brief follows the 12-section format in
`sub-agent-delegation.md` §5. The interviewer **pre-extracts**
the Family N anchor structures captured at P5 closure
([`phase-P5.md`](./phase-P5.md) §"Family N anchor extraction") into
the brief during authoring — the heavy YAML read is paid once, at
P5, by the chat that already has them in memory. The P9 brief
author does not re-open the YAMLs.

### 2a — Brief Section 3 (`{ path, read_mode, expected_anchors }`)

For every cited component YAML, Section 3 of the brief carries
one entry:

```yaml
- path: ".context/components/<component>.yaml"
  read_mode: "full"
  expected_anchors:
    <anchor_key>: "<verbatim value from the P5 anchor structure>"
    <anchor_key>: "..."
```

`expected_anchors` carries 3–8 entries per YAML, sourced verbatim
from the in-memory anchor structures captured at P5 closure.
Anchors are read-proof tokens — short, low-cost data points the
handoff chat must extract end-to-end and attest in its
`_summary.md` `## YAML reads` table.

If a cited YAML's anchor structure is thin (fewer than 3 anchors
captured at P5), the interviewer surfaces this to the PM at brief
authoring and either accepts the L5.2 thin-pattern override
(already emitted at Step 0) or escalates back to
`prd-orchestrator` for a re-run. No invented anchors.

### 2b — Brief Sections 4 / 6 / 7 / 8 (pre-extracted content)

Section 4 — the scenario list (demos) / record-set list
(sample-data) / six-element entry list (component-spec) — is
pre-extracted from `acceptance-criteria.md`, the §4 entries in
`prd.md`, the matched-component list, and the
Component Pattern Confirmation Report.

Section 6 — verbatim copy strings the handoff chat must use — is
pre-extracted from the P5 in-memory state: empty-state copy
strings, validation message strings, success toast strings,
disabled-state reason strings, label text. Every copy string
carries a Family F tier marker (Tier 1 verbatim YAML / Tier 2
PM-approved phrasing / Tier 3 interviewer-drafted
PM-approved-before-write).

Section 7 — schema / shape references for sample-data (record
schemas, enum lists, required-field lists, FK references) — is
pre-extracted from the breakdown's `investigation_context`
schema notes plus the §4.1 DM-NNN entries.

Section 8 — application-fidelity citations under Family M.
Every cited YAML path is named here so the handoff chat can
verify it has covered every cited surface before writing its
`_summary.md`.

The handoff chat reads the brief end-to-end + targeted anchor
confirmations from the cited YAMLs only. The heavy YAML read is
paid once, by the chat (P5) that already had them in memory.

### 2c — Brief Section 9 (Hard constraints — Family N N4)

Section 9 of every brief explicitly prohibits summarised reads:

> "You MUST read every file in Section 3 end-to-end. No
> summarisation, no skimming, no inferring. The `expected_anchors`
> in Section 3 are read-proof tokens. Your `_summary.md` MUST
> carry a `## YAML reads` H2 table with `anchors_extracted`
> matching the `expected_anchors` verbatim. Fabricating an
> anchor is a hard fail."

Section 9 also enumerates the surface-specific Tier 1 inside-chat
self-review items per `sub-agent-delegation.md` §K.3, including
the new N6 read-completeness item.

### 2d — Pre-write artifact-bar walk (L6 G3) per brief

Before writing each brief, run the L6 G3 walk against the
quality bar's brief Pass Conditions:

- All 12 §5 sections are present.
- Section 3 has at least one `{ path, read_mode,
  expected_anchors }` entry per matched-component YAML cited by
  the surface.
- Every `expected_anchors` value sources verbatim from the P5
  in-memory anchor structures — no invented anchors.
- Section 6 verbatim copy strings each carry a Family F tier
  marker.
- Section 8 cites every YAML the surface depends on (Family M
  hard rule — no silent gaps; "no application equivalent"
  flagged explicitly when applicable).
- Section 9 carries the Family N N4 hard-constraints text and
  the surface-specific Tier 1 checklist including N6.
- The sibling-derivative YAML frontmatter is present with
  `derivativeOf: prd.md`, `prdHash` (matching `prd.md` body),
  `writtenAt`, and `producer: interviewer`.

Failure emits `prd_pre_write_bar_walk_failed` with `artifact`
set to the affected brief (`demo-brief` / `sample-data-brief` /
`component-spec-brief`). The write does not proceed until the
failing Pass Condition is resolved.

On all Pass Conditions met, write each brief:

- `demos/_brief.md` (if `requires_ui_demo` or
  `requires_calc_demo`)
- `sample-data/_brief.md`
- `component-spec/_brief.md`

Emit `brief_generated` once per surface, payload `{ subPrdId,
prdRunId, surface, briefPath, citedYamlCount, expectedAnchorCount }`.

---

## Step 3 — Hand three paste-ready prompts to the PM

The interviewer hands the PM three paste-ready prompts at a
single handoff point. The prompts are sourced verbatim from
`handoff-prompt-templates.md` with bracketed placeholders
substituted (`[FEATURE_ID]`, `[sub-prd-id]`, `[brief path]`).

The PM opens three fresh Cursor chats (chats may run in
parallel) and pastes each prompt unchanged. Each handoff chat:

1. Reads its brief end-to-end.
2. Reads every file in brief Section 3 end-to-end and extracts
   every anchor (Family N N4 — no summarisation).
3. Walks the surface-specific Tier 1 inside-chat self-review
   per `sub-agent-delegation.md` §K.3 (including the new N6
   read-completeness item).
4. Produces its artifact(s) and its `_summary.md` with the six
   required H2 headings including `## YAML reads` populated
   with `anchors_extracted` verbatim values.
5. STOPS — never amends the interviewer's outputs; never
   proposes follow-ups (any open questions go under the
   summary's `## Open Questions` H2 and are read on return).

Tier 1 self-review **never runs in the interviewer chat
post-return**. The self-review is the handoff chat's
responsibility — that preserves the T5 context-saving intent.

Emit `manual_handoff_initiated` once per surface, payload
`{ subPrdId, prdRunId, surface, mode: "manual_handoff",
briefPath }`.

---

## Step 4 — On PM return, validate the three summaries

When the PM returns and reports all three handoff chats have
STOPPED, the interviewer executes the validation protocol per
`sub-agent-delegation.md` §7. **The interviewer does not open
the full heavy artifacts (`demo-interactive.html`,
`sample-data/*.json`, `component-spec.md`).** It opens only:

1. The three `_summary.md` files.
2. The YAML files in brief Section 3 (for Family N N3 anchor
   verification — see Step 4b below).
3. Random artifact rows (for the N5 spot-check — see Step 4c
   below) only when the spot-check protocol designates them.

### 4a — Summary-schema conformance check

For each `_summary.md`, verify:

- The sibling-derivative YAML frontmatter is present with
  `derivativeOf: prd.md`, `prdHash` (the value matches `prd.md`
  body hash — drift here means the handoff chat read a stale
  PRD or there was a PRD write between brief and return),
  `writtenAt`, and `producer` (one of `handoff:demo`,
  `handoff:sample-data`, `handoff:component-spec`).
- All six required H2 headings are present:
  - `## Coverage`
  - `## Deviations`
  - `## Open Questions`
  - `## YAML reads`
  - `## Application Fidelity Attestation`
  - `## Tier 1 self-review`
- The `## YAML reads` table is populated with one row per
  brief Section 3 entry, with `path`, `read_mode`, and
  `anchors_extracted`.

A summary that fails schema conformance (L11 C7) triggers a
re-handoff with brief amendment that pastes the summary contract
explicitly. The interviewer emits `prd_handoff_re_run` with
`rerunReason: summary_schema_invalid`.

### 4b — Family N N3 anchor verification (YAML-only reads)

For every row in `## YAML reads`, the interviewer opens the named
YAML file (not the heavy artifact) and matches each
`anchors_extracted` value against the YAML text verbatim.

- **Match.** Continue to the next row.
- **Mismatch.** Classify per L11 C2:
  - **Structural mismatch** (the YAML structure does not contain
    the anchor key the brief named) → tighter brief, re-handoff.
    Emit `prd_anchor_verification_failed` with `mismatchType:
    structural`, `resolution: tighter_brief`.
  - **Copy mismatch** (the anchor key exists but the value
    differs from the YAML's actual value) → re-handoff with
    brief amendment naming the correct value. Emit with
    `mismatchType: copy`, `resolution: tighter_brief`.
  - **YAML-vs-PM contradiction** (the YAML says X but a PM
    answer captured in `interview-answers.json` says Y, and the
    handoff chat picked Y) → escalate to `prd-orchestrator` for
    breakdown investigation; PM may pick which side stands.
    Emit with `mismatchType: yaml_vs_pm_contradiction`,
    `resolution: orchestrator_escalate`.
  - **Cosmetic mismatch** (trivial difference like trailing
    whitespace, capitalisation in a non-binding location) →
    accept into PRD §7 Open Items with a stated reason. Emit
    with `mismatchType: cosmetic`, `resolution:
    accept_as_open_item`.

Anchor verification is the structural gate Family N N3 protects.
The interviewer never reads the heavy artifact during anchor
verification — only the YAML files. This is the read-discipline
gain Family N exists to deliver.

### 4c — Family N N5 spot-check

After anchor verification passes (or after the resolution path
for any mismatches is recorded), the interviewer performs a
randomised spot-check on the heavy artifact:

- For demo: open 2–3 random scenario rows in
  `demo-interactive.html` and confirm the visible copy / state
  / interaction matches the cited YAML(s).
- For sample-data: open 2–3 random JSON records and confirm
  the schema / enum / FK references match the cited
  schemas / YAMLs.
- For component-spec: open 2–3 random six-element entries and
  confirm the state list / interaction list / data binding
  match the cited YAMLs and §4 entries.

A spot-check failure routes via the same L11 C2 decision matrix
as anchor verification — most spot-check failures classify as
"copy mismatch" or "structural mismatch" and trigger a
re-handoff with brief amendment.

### 4d — Deviations and Open Questions surfacing

The interviewer surfaces every entry from `## Deviations` and
`## Open Questions` (across all three summaries) to the PM. The
PM decides per item:

- (a) Accept the deviation into PRD §7 Open Items with a stated
  reason — interviewer updates `prd.md` §7 in memory and emits
  the bar walk for the §7 amendment.
- (b) Reject the deviation — interviewer amends the affected
  brief and the PM re-runs the corresponding handoff chat in
  the same chat session (re-handoff inherits the same
  `subPrdId` and `surface`).
- (c) Escalate to `prd-orchestrator` (used when the deviation
  reveals a breakdown defect).

Open Questions are treated the same way — the PM may resolve
them in chat (interviewer captures the answer into `prd.md` §7),
defer with a documented reason, or escalate.

A re-handoff after PM rejection emits `prd_handoff_re_run` with
`rerunReason: deviation_rejected`. Repeated re-handoffs for the
same surface (more than 2) emit `prd_handoff_re_run` with
`rerunReason` retained but the escalation to orchestrator
(L11 C8) becomes the next step — the interviewer surfaces this
to the PM at the second re-handoff.

Emit `manual_handoff_returned` once per surface, payload
`{ subPrdId, prdRunId, surface, summaryPath, ambiguityFlagCount,
deviationCount, anchorMismatchCount }`.

---

## Step 5 — Auto-build `traceability.md`

Once all three summaries pass validation (Steps 4a–4d) and the
PM accepts deviations (or re-handoffs are complete), the
interviewer builds `traceability.md` per
[`../traceability-template.md`](../traceability-template.md).

The artifact is constructed from:

- The in-memory AC list held since P8 Step 4 (not re-opened from
  disk).
- The `## Coverage` table from each of the three `_summary.md`
  files.

Output is a single bidirectional table:

| AC-NNN | linked §4.NNN | surface | demo coverage | sample-data coverage | component-spec coverage |
|---|---|---|---|---|---|

The table is **deterministic and table-only — no narrative
prose**. Auto-built means the interviewer constructs the table
mechanically from the inputs; no PM input is solicited here.

### 5a — Pre-write artifact-bar walk (L6 G3) for `traceability.md`

Before writing, verify:

- Every AC-NNN from the in-memory AC list appears as a row.
- Every row's `linked §4.NNN` matches the AC's
  `linked_requirement_ids` field.
- Every row's `surface` matches the AC's `surface` field.
- Every demoable AC (`demoable: true`) has a populated demo
  coverage cell from `demos/_summary.md`'s coverage table.
- Every backend AC (`demoable: false`) carries `(not demoable)`
  in the demo coverage cell.
- The sibling-derivative YAML frontmatter is present.

Failure emits `prd_pre_write_bar_walk_failed` with `artifact:
traceability`. The write does not proceed until the failing
condition is resolved.

On all Pass Conditions met, write `traceability.md` to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/traceability.md`.

---

## Step 6 — Finalise `bundle-manifest.json`

`bundle-manifest.json` declares every file in the bundle plus
its `prdHash`, write timestamp, and producing actor. Downstream
consumers iterate `files[]` rather than heuristically discovering
files on disk.

### 6a — Manifest schema

```json
{
  "schemaVersion": "1.0.0",
  "subPrdId": "<sub-prd-id>",
  "featureId": "<PROF-NNN>",
  "prdHash": "<sha256-hex of prd.md body at finalisation time>",
  "finalisedAt": "<ISO 8601 UTC>",
  "finalisedBy": "interviewer",
  "files": [
    {
      "path": "prd.md",
      "prdHash": "<sha256-hex of prd.md body>",
      "writtenAt": "<ISO 8601 UTC>",
      "producer": "interviewer",
      "role": "primary"
    },
    {
      "path": "acceptance-criteria.md",
      "prdHash": "<sha256-hex referenced from prd.md>",
      "writtenAt": "<ISO 8601 UTC>",
      "producer": "interviewer",
      "role": "sibling"
    }
    /* one entry per file in the bundle */
  ]
}
```

### 6b — Required `files[]` entries (minimum)

Every bundle MUST declare:

- `prd.md` — role `primary` (exactly one entry; the bundle's
  primary deliverable).
- `acceptance-criteria.md` — role `sibling`.
- `reuse-map-draft.md` — role `sibling`.
- `interview-answers.json` — role `sibling`.
- `traceability.md` — role `sibling`.
- `component-pattern-confirmation.md` — role `sibling`.
- `demos/_brief.md` — role `sibling` (when demos in scope).
- `sample-data/_brief.md` — role `sibling`.
- `component-spec/_brief.md` — role `sibling`.

Plus every handoff-authored file from each surface — role
`derivative`:

- `demos/demo-interactive.html` (when produced).
- `demos/calculation-demo.html` (when `requires_calc_demo`).
- `demos/demo-behavior-manifest.md` (when produced).
- `demos/demo-coverage.md` (when produced).
- `demos/_summary.md`.
- `sample-data/*.json` (every JSON file the sample-data handoff
  wrote).
- `sample-data/_summary.md`.
- `component-spec.md`.
- `component-spec/_summary.md`.

### 6c — Producer enum

- `interviewer` — every file written by the interviewer chat.
- `handoff:demo` — every file written by the demo handoff chat.
- `handoff:sample-data` — every file written by the sample-data
  handoff chat.
- `handoff:component-spec` — every file written by the
  component-spec handoff chat.

### 6d — Role enum

- `primary` — used by exactly one file (`prd.md`).
- `sibling` — interviewer-authored alongside the primary.
- `derivative` — handoff-authored from a brief.

### 6e — Pre-write artifact-bar walk (L6 G3) for `bundle-manifest.json`

Before writing, verify:

- Every required `files[]` entry (per Step 6b above) is
  present.
- Every entry's `path` is a real file on disk in the sub-PRD
  folder.
- Every entry's `producer` matches the producer-enum value.
- Every entry's `role` matches the role-enum value.
- Exactly one entry has `role: primary` (and it is `prd.md`).
- Every entry's `prdHash` matches `prd.md` body hash at
  finalisation time (or `[COMPUTATION_FAILED]` per L11 D5 if
  the handoff chat's hash computation failed).
- `schemaVersion`, `subPrdId`, `featureId`, `finalisedAt`,
  `finalisedBy` are all populated.

Failure emits `prd_pre_write_bar_walk_failed` with `artifact:
bundle-manifest`. The write does not proceed until the failing
condition is resolved.

On all Pass Conditions met, write `bundle-manifest.json` to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json`.

Emit `prd_bundle_manifest_finalised` with payload `{ subPrdId,
manifestPath, fileCount }`.

---

## Step 7 — Hand off to `prd-completeness-check`

After the bundle manifest is written, the interviewer emits the
phase-completion telemetry and tells the PM:

> "The sub-PRD bundle has been written to
> `.sage/prds/[FEATURE_ID]/[sub-prd-id]/`. The bundle is declared
> in `bundle-manifest.json`. Review the PRD,
> `acceptance-criteria.md`, the demo summary, the sample-data
> summary, and the component-spec summary. When you are
> satisfied, run `prd-completeness-check` against the bundle."

The interview ends after this handoff. Any further PRD edits
are handled by `prd-amend` (post-completion flow); `prd-amend`
reads `bundle-manifest.json` plus a `prd-stale-check` report to
identify STALE surfaces and re-runs only those handoffs.

---

## Telemetry

P9-scoped emit sites only:

- `prd_phase_started` — `phaseId: P9` at Step 1 entry.
- `brief_generated` — once per surface at Step 2d, payload
  carries `briefPath`, `citedYamlCount`, `expectedAnchorCount`.
- `manual_handoff_initiated` — once per surface at Step 3.
- `manual_handoff_returned` — once per surface at Step 4d.
- `prd_anchor_verification_failed` — emitted at Step 4b per
  mismatched anchor row with `mismatchType` and `resolution`.
- `prd_handoff_re_run` — emitted when a surface is re-handed off
  with `rerunReason` (one of `deviation_rejected`,
  `anchor_mismatch`, `summary_schema_invalid`,
  `handoff_self_stopped`, `extra_files`).
- `prd_pre_write_bar_walk_failed` — emitted whenever the L6 G3
  walk fails for any brief, `traceability.md`, or
  `bundle-manifest.json`.
- `prd_bundle_manifest_finalised` — emitted at Step 6e on
  successful write. **End-of-phase event before
  `prd_interview_completed`.**
- `prd_phase_completed` — `phaseId: P9` immediately after
  `prd_bundle_manifest_finalised`.
- `prd_interview_completed` — final event of the interview run,
  payload `{ subPrdId, prdRunId, linearIssueId, manifestPath,
  fileCount }`. Marks the end of the run.

Payload shapes for every event live in
[`../telemetry-schema.md`](../telemetry-schema.md) §2. P8/P9
phase-numbering alignment: every bundle-write event labels
`phaseId: P9` if emitted from this module;
`acceptance_criteria_generated` and `reuse_map_confirmed` are
P8 events (see [`phase-P8.md`](./phase-P8.md)).

---

## Cross-cutting protocols invoked (pointer only)

P9 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family E — No mid-interview recon.** YAML files are opened
  at P9 only during Step 4b Family N N3 anchor verification —
  this is **not** mid-interview recon (the interview is closed);
  the open is bounded by the in-memory anchor structures and
  reads only the cited YAMLs the brief named.
- **Family M — Application-fidelity.** Brief Section 8 cites
  every YAML the surface depends on; "no application equivalent"
  is flagged explicitly. The handoff chat's
  `## Application Fidelity Attestation` summary section attests
  the citations were honoured.
- **Family N — Handoff-chat read discipline (the heaviest
  binder at P9).** N1 brief Section 3 format · N2 summary
  `## YAML reads` table · N3 interviewer post-return YAML-only
  anchor verification · N4 Section 9 hard constraints · N5
  spot-check on PM return · N6 Tier 1 inside-chat read-
  completeness · N7 read discipline across all three surfaces ·
  N8 pre-extraction at brief authoring.
- **Family G — Self-review gates.** G3 pre-write artifact-bar
  walks run for every brief, `traceability.md`, and
  `bundle-manifest.json`.
- **Family J — Anti-hallucination.** No invented anchors, no
  invented coverage cells in `traceability.md`, no invented
  manifest entries.
- **Family K — Production-grade bar.** K1 — the bundle must
  pass the quality bar before bundle manifest finalisation.
  K2 — any L5 override applied at Step 0 surfaces in PRD §8
  Related Artefacts as a reduced-fidelity marker; the marker is
  visible in `bundle-manifest.json` indirectly via the §8
  freshness column on the affected derivative pointer.

---

## Next phase

P9 is the terminal phase of the interview run. On Step 7
handoff message + `prd_interview_completed` emitted, the
interview is complete and `prd-completeness-check` is the next
downstream consumer (invoked manually by the PM).

Post-completion PM edits to `prd.md` route to the `prd-amend`
flow (not the interviewer); `prd-amend` reads
`bundle-manifest.json` plus a `prd-stale-check` report and
re-runs only STALE surfaces via diff briefs.
