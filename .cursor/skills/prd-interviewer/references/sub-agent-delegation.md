# Sub-Agent Delegation — Manual Handoff Contract

Reference for prd-interviewer. Self-contained — no external skill references.

This file is the production pattern for producing the three sub-agent-built
surfaces of a sub-PRD: **demo**, **sample-data**, and **component-spec**.
The pattern is **manual chat handoff**, not programmatic sub-agent spawning.
Phase 0 of the PRD Pipeline Production Lift proved the manual pattern works
and surfaces real defects that programmatic spawning either could not access
(blocked subagent enums) or could not produce (no structured summary contract).

This file governs every brief the prd-interviewer chat writes. The
`handoff-prompt-templates.md` file in the same folder governs the prompts the
PM pastes into the handoff chats.

---

## 1. Why manual handoff is the production pattern

The Cursor `Task` tool's `subagent_type` enum does not currently expose a
general-purpose UI builder in this environment. The plan-permitted fallback
(`generalPurpose`) is admin-blocked. Phase 0 demonstrated that a PM-orchestrated
manual chat handoff — interviewer authors a brief, PM opens a fresh chat and
pastes a standardised prompt pointing at the brief, the handoff chat writes
the artifact plus a structured summary file, the parent chat reads only the
summary — produces a result at parity with or above the previous skill-driven
pattern, with significantly lower context cost in the parent chat.

If a suitable `subagent_type` later becomes available, programmatic spawning
is an **optional optimisation**. The manual pattern remains the contract.

---

## 2. Orchestration sequence (always exactly these steps, in this order)

1. **Interviewer chat writes the brief.** One brief per surface that the
   sub-PRD needs (demo, sample-data, component-spec). Briefs are written to
   the sub-PRD output folder under `_brief.md` suffixes — see Section 5.
2. **Interviewer chat hands every brief to the PM with a paste-ready handoff
   prompt** sourced verbatim from `handoff-prompt-templates.md`. The PM never
   authors prompts.
3. **PM opens one fresh Cursor chat per brief** in the same workspace and
   pastes the corresponding prompt unchanged. The PM does not modify the
   prompt or the brief.
4. **Each handoff chat reads the brief plus every referenced YAML, then
   produces exactly two files** — the artifact and a structured
   `_summary.md` file conforming to the contract in Section 6. The handoff
   chat STOPS after the summary is written. It does not summarise in chat,
   does not propose follow-ups, does not modify any other file.
5. **PM returns to the interviewer chat** and tells it the handoff is
   complete.
6. **Interviewer chat reads only the `_summary.md` files** — never the full
   artifact. It validates the summary's claims against the brief, surfaces
   deviations and open questions to the PM, and iterates if necessary by
   amending the brief and asking the PM to re-run the same handoff prompt in
   the same chat.

This sequence is non-negotiable. The interviewer chat does not read the
full artifact at any step. The handoff chat does not modify any file outside
the declared output paths. The PM does not edit any prompt or brief content.

---

## 3. Three surfaces, one contract

The same delegation pattern applies to three surfaces. Each has a brief, a
handoff-prompt template, and a `_summary.md` contract. The shared spine
(Sections 4–6 below) is identical; the surface-specific brief sections differ
only in what the artifact is.

| Surface | Artifact file(s) | Brief file | Summary file | Handoff-prompt template section |
|---|---|---|---|---|
| Demo | `demos/demo-interactive.html` (and/or `demos/calculation-demo.html`) | `demos/_brief.md` | `demos/_summary.md` | `handoff-prompt-templates.md` § Demo |
| Sample-data | `sample-data/*.json` | `sample-data/_brief.md` | `sample-data/_summary.md` | `handoff-prompt-templates.md` § Sample-data |
| Component-spec | `component-spec.md` | `component-spec/_brief.md` | `component-spec/_summary.md` | `handoff-prompt-templates.md` § Component-spec |

All paths are relative to `.sage/prds/[FEATURE_ID]/[sub-prd-id]/`.

### 3.1 Demo posture classification (L4.3 sub-lock — binding)

Demos are one of four postures. The posture is picked by the interviewer
during P5 and recorded verbatim in the demo brief's Section 4 header.
**The handoff chat has zero discretion to switch postures** — if the
chosen posture is unsuitable, the chat raises an Open Question in the
summary and the brief is amended; the chat does not silently switch.

Each posture carries its own quality bar (codified in
`production-grade-quality-bar.md`).

1. **AC-driven scenario theater** — dark glass-panel; scenario selector
   plus AC sidebar; each AC has a visible state in the demo; production
   styling but NOT a full replica. Use when AC count is moderate and
   scenarios are discrete.
2. **AC bar atop production page** — full production-fidelity page with
   a collapsible AC overlay bar. Use when the feature is a single page
   with many AC and the PM wants production fidelity.
3. **Production page replica, no AC overlay** — pure production-fidelity
   replica, no AC instrumentation. Use when the demo's job is "show the
   surface" and AC are tracked elsewhere.
4. **Calculation-demo theater** — multi-mode header
   (`Walkthrough | Interactive | Reference Data | Run All`); three-column
   layout (260px scenario sidebar | center main | 340px audit/detail
   panel); real JS engine; worked examples. Ships **in addition to** a
   UI demo when calculation logic is in scope (the calculation-demo and
   the UI-demo are two separate artifacts in the same `demos/` folder).

The demo brief's Section 4 header line is verbatim one of the four
posture names above. The handoff chat reads that line and treats the
posture as a hard constraint.

Demos must cite the appropriate component YAML(s) under
`.context/components/` per the Family M application-fidelity hard rule
(see Section 4 below). No silent gaps.

---

## 4. Application-fidelity hard rule (binding across all three surfaces)

**Hard rule (verbatim, lifted from the Phase 0 dry-run report Section 10):**

> When a UI affordance exists in the production application, the brief MUST
> cite the relevant component YAML file(s) under `.context/components/` (or
> equivalent), and the demo-generation chat has zero discretion to invent a
> different pattern. The brief author is responsible for naming every YAML a
> demo will need before the brief is finalised. Production-grade design
> freedom applies only where there is no application equivalent — those
> affordances must be flagged explicitly in the brief as "no application
> equivalent — generator's choice". No silent gaps.

This rule is **binding on every brief**, not a soft preference. The brief
author (the prd-interviewer chat) bears full responsibility for naming
every YAML the handoff chat will need before the brief is handed over.
A brief that omits a YAML for an existing application affordance is defective
and must be fixed before the PM opens the handoff chat.

### 4.1 Brief-author traceability checklist (walk before finalising the brief)

For every visible affordance the brief's scenario list (demo), sample-data
schema, or component-spec entry will exercise:

- [ ] Is there a production application equivalent for this affordance?
  (Search `.context/components/manifest.yaml` and the relevant component
  YAMLs. If unsure, do the search — do not assume.)
- [ ] If yes: is the relevant YAML file path cited in the brief's
  "Component YAML files you must deep-read" section (or surface-specific
  equivalent)?
- [ ] If no: does the brief contain an explicit
  "no application equivalent — generator's choice" call-out for this
  affordance, including the tone/palette bounds within which the handoff
  chat may exercise design judgement?
- [ ] No silent gaps — every scenario, every sample-data record shape,
  every component-spec entry traces to either a cited YAML or an explicit
  no-equivalent call-out.

A brief that fails any item is not ready to hand off. Fix, then re-walk.

### 4.2 Three surface applications

- **Demo brief.** Every visible affordance in every scenario maps to a
  cited YAML or a no-equivalent call-out. Affordances include grids, buttons,
  toggles, dialogs, toasts, badges, validators, loader overlays, sidebars,
  banners, breadcrumbs, edit-mode cell rendering, disabled-cell rendering,
  scenario rails (no equivalent), debug panes (no equivalent), and inspector
  overlays (no equivalent).
- **Sample-data brief.** Every record shape, field type, and edge-case row
  set traces to a cited schema/YAML or to an explicit "no application
  equivalent — generator's choice" call-out (e.g. for synthetic stress-test
  rows).
- **Component-spec brief.** Every component entry traces to a cited
  application component YAML for matched components, or to a "new component —
  no application equivalent" call-out for genuinely new components. New
  components are still bounded by the brand palette and the surface tone.

### 4.3 Handoff-chat self-review obligations (in the brief's Tier 1 checklist)

Every brief's embedded self-review checklist must include both of the
following items. Failure on either must be fixed before the summary is
written:

- (a) **For every cited YAML, the rendered affordance matches the YAML's
  structural and copy fidelity.** Spot-check at least one structural element
  (markup shape, layout, state set) and one copy string (label, tooltip,
  message) per cited YAML against the produced artifact.
- (b) **For every uncited affordance, the brief contains an explicit
  no-application-equivalent call-out.** If the produced artifact contains
  an affordance the brief did not flag this way, the brief is defective —
  surface it in the summary's Deviations section AND raise an Open Question
  asking the brief author to amend the brief.

---

## 5. Brief format — required sections (shared spine + surface-specific)

Every brief file (regardless of surface) must contain these top-level
sections in this order. Sections marked **(surface-specific)** vary by
surface; the rest are shared.

| # | Section | Shared | Required | Notes |
|---|---|---|---|---|
| 0 | What this feature is (in 6 sentences) | yes | yes | Plain business language. No SP names, return codes, internal constructs. |
| 1 | Outputs you must produce (exactly N, no more) | yes | yes | Repo-relative paths only. State explicitly that the handoff chat may produce no other file. |
| 2 | Reuse decisions (from component-spec / breakdown) | yes | yes (demo, component-spec) / partial (sample-data) | Table: Surface → Reuse pattern. Cites named components. |
| 3 | Component YAML files you must deep-read | yes | yes | Per-YAML structured entries — each entry is `{ path, read_mode, expected_anchors }`. `path` is repo-relative; `read_mode` defaults to `"full"`; `expected_anchors` is a short list of read-proof tokens the handoff chat must extract verbatim and report in `_summary.md`'s `## YAML reads` H2. See Section 6 (Family N) for the anchor contract. This is the brief author's enforced application-fidelity declaration. |
| 4 | Scenarios / records / entries to demonstrate | surface-specific | yes | Demo: scenario list with `scenario_id` + AC mapping. Sample-data: record list with edge-case coverage. Component-spec: component-entry list with state/data/interaction coverage. |
| 5 | Sample data inline (or schema reference) | yes (demo, component-spec) / surface-defining (sample-data) | yes | Exact rows for demo; canonical schema for sample-data; data binding entries for component-spec. |
| 6 | Verbatim text strings (copy these exactly — do not paraphrase) | yes | yes | All user-facing text in the artifact must be sourced verbatim from this section, the cited YAMLs, or `[TEXT TBD]` markers. |
| 7 | Visual notes (palette, fonts, layout tokens) | yes (demo) / partial (component-spec) / N/A (sample-data) | conditional | Brand palette tokens; layout primitives; tone constraints. |
| 8 | State requirements | yes (demo) / yes (component-spec) / N/A (sample-data) | conditional | Demo: in-memory STATE shape. Component-spec: required state model per component. |
| 9 | Hard constraints | yes | yes | Output containment, no other files modified, no skill/agent/hook edits, no fabricated copy, STOP after summary. |
| 10 | No-application-equivalent call-outs | yes | yes | Explicit list of every affordance / record-shape / entry where the brief grants the handoff chat production-grade design freedom. If empty, write `None — every affordance traces to a cited YAML.` |
| 11 | Required summary file: `_summary.md` (with the 6 H2 schema, see Section 6) | yes | yes | Reiterate the schema inline so the handoff chat does not need to read this file. Section 6 of the brief (Verbatim text strings) is distinct from this Section 11 (which declares the summary file shape); do not collapse them. |
| 12 | Self-review checklist (run BEFORE writing `_summary.md`) | yes | yes | Tier 1 checklist including the two application-fidelity items from Section 4.3 above. |

The brief's Section 3 (YAML reading list) plus Section 10 (no-equivalent
call-outs) together satisfy the application-fidelity hard rule. If either is
missing or empty for a brief whose artifact has visible affordances, the
brief is defective.

---

## 6. Required summary file contract (`_summary.md`)

Every handoff chat must produce exactly one summary file at the path
declared in the brief's Section 1. The summary file must contain exactly
these six H2 headings in this order, with no preamble, no conclusion,
and no other top-level sections. The summary file's first line under the
`# ` H1 is a `<!-- prdHash: <sha256-hex> -->` header (per Family N N2 +
the derivative frontmatter rule).

1. **`## Files written`** — bullet list of every file produced, with
   repo-relative paths. The list length must equal the number of outputs
   declared in the brief's Section 1.
2. **`## YAML reads`** — Family N N2 anchor attestation. A markdown
   table with columns `| path | read_mode | anchors_extracted |`. One
   row per entry in the brief's Section 3. Every `expected_anchor` named
   in the brief's Section 3 must appear in the corresponding row's
   `anchors_extracted` cell, with the value extracted verbatim from the
   YAML. This table is the read-proof the handoff chat actually read
   every cited YAML end-to-end. Fabricating an anchor (writing a
   plausible value without opening the YAML) is a hard fail caught by
   the interviewer chat's Family N N3 post-return verification.
3. **`## Scenario coverage`** (demo) / **`## Record coverage`**
   (sample-data) / **`## Component coverage`** (component-spec) — a
   markdown table with columns appropriate to the surface:
   - Demo: `scenario_id | AC | status | notes` — `status` one of
     `rendered`, `partial`, or `skipped`. `skipped` requires a
     one-sentence reason in `notes`. Every brief Section 4 entry must
     appear in table order. `AC` references the sequential `AC-NNN` IDs
     from `acceptance-criteria.md`.
   - Sample-data: `record_id | shape | edge_case | status | notes` —
     `status` one of `written`, `partial`, `skipped`. `edge_case` cites
     the linked `AC-NNN` where the brief declares the linkage.
   - Component-spec: `component_id | page | type | status | notes` —
     `status` one of `specified`, `partial`, `skipped`.
4. **`## Deviations from the brief`** — bulleted list of every place
   the handoff chat knowingly diverged from the brief, with a
   one-sentence reason per deviation. If none, write `None.`
5. **`## Ambiguities noticed in the brief`** — bulleted list of every
   place the handoff chat found the brief unclear or contradictory. If
   none, write `None.`
6. **`## Open questions`** — bulleted list of questions for the PM
   (and indirectly the interviewer chat). If none, write `None.`

The summary file is the **only** thing the interviewer chat reads on
return. Every claim in the summary must be verifiable against the
artifact without the interviewer chat needing to open the artifact —
except (a) the Family N N3 anchor verification, which opens the cited
YAMLs (not the artifact) to confirm `anchors_extracted`, and (b) the
Family N N5 spot-check, which opens a random row of the artifact to
confirm against the YAML.

### 6.1 Family N — Handoff-chat read discipline (8 sub-rules, binding)

Family N is the binding read-discipline contract that prevents
summarised reads, fabricated content, and silent gaps inside the three
manual handoff chats. The eight sub-rules are transcribed verbatim from
`interview-conduct/shared-protocols.md` (L6 Family N) — both files agree;
this section restates them here so the brief author has Family N at
hand without leaving this file.

- **N1** Brief Section 3 (the YAML reading list) is structured as
  `{ path, read_mode, expected_anchors }` per YAML. Default
  `read_mode: "full"`. `expected_anchors` is a short list of read-proof
  data points the handoff chat must extract verbatim (e.g. "third state
  name", "empty-state copy string verbatim", "count of action buttons",
  "YAML `version:` header value").
- **N2** Every handoff `_summary.md` carries the `## YAML reads` H2
  defined above with the anchor attestation table.
- **N3** Interviewer post-return verification opens **only the YAML
  files** (NOT the heavy artifact) and matches each `anchors_extracted`
  value verbatim against the YAML text. Mismatch triggers re-handoff
  with brief amendment per Section 8.
- **N4** Brief Section 9 (Hard constraints) explicitly prohibits
  summarised reads.
- **N5** Handoff prompts in `handoff-prompt-templates.md` restate the
  read discipline in their Hard rules block; plus the random spot-check
  on PM return — the interviewer randomly opens one or more artifact
  rows to confirm against the cited YAML.
- **N6** Tier 1 inside-chat self-review checklist in every brief gains
  the read-completeness item per surface (see §K.3 below).
- **N7** Read discipline applies to all three surfaces.
- **N8** Brief pre-extraction discipline: the interviewer pre-extracts
  cited YAML content into brief Sections 6 / 7 / 8 during authoring at
  P9, using the in-memory YAML state captured at P5. The heavy YAML
  read is paid once by the chat that already has them in memory.

---

## 7. Interviewer-chat validation protocol (on PM return)

After the PM confirms the handoff chats are complete:

1. **Read every `_summary.md` file** for each surface produced. Do not
   open the artifacts at this step.
2. **Verify schema conformance.** Every summary has the six H2 headings
   in order (`## Files written`, `## YAML reads`, `## Scenario coverage`
   / `## Record coverage` / `## Component coverage`, `## Deviations from
   the brief`, `## Ambiguities noticed in the brief`, `## Open
   questions`). The `## Files written` list length matches the brief's
   Section 1 output count. The `prdHash` header line is present
   immediately under the H1. Schema non-conformance is L11 C7 — emit
   `prd_handoff_re_run` with `rerunReason: 'summary_schema_invalid'`.
3. **Family N N3 anchor verification.** For every row in `## YAML reads`,
   open ONLY the cited YAML (not the artifact) and confirm each
   `anchors_extracted` value matches the YAML text verbatim. Any
   mismatch is L11 C2 — classify and route per the decision criterion
   below. Emit `prd_anchor_verification_failed` with the matching
   `mismatchType` and chosen `resolution`.
4. **Verify completeness.** Every entry in the brief's Section 4
   appears in the coverage table. Any `partial` or `skipped` status has
   a stated reason.
5. **Family N N5 spot-check.** Pick one or more rows at random (or all
   rows for very small surfaces) from the coverage table and open the
   artifact to confirm the claim is supported. If any claim is
   unsupported, treat the summary as untrusted and re-handoff with an
   amended brief (L11 C3 — invented content).
6. **Surface Deviations and Open Questions to the PM** for decision. The
   PM either (a) accepts each item and the deviation is recorded in the
   PRD's §7 Open Items, (b) amends the brief and re-runs the handoff in
   the same chat (L11 C1), or (c) rewrites the affected scope.

### 7.1 L11 C2 decision criterion (Family N anchor verification failures)

When Family N N3 anchor verification fails on PM return, classify the
mismatch and route per this fixed criterion. The interviewer chat picks
one of the four resolutions; PM ratifies. The chosen resolution is
recorded in the telemetry event `prd_anchor_verification_failed.resolution`.

| Mismatch type | Meaning | Resolution |
|---|---|---|
| `structural` | Anchor describes structure (state set, action button count, layout block) and the value disagrees with the YAML | Tighter brief — re-author Section 3 to list more anchors covering the structural facets the chat got wrong; re-handoff. |
| `copy` | Anchor describes a verbatim copy string (label, tooltip, message) and the value disagrees with the YAML | Re-handoff with brief amendment — paste the verbatim YAML copy into brief Section 6; tighten Section 3 anchor for that string. |
| `yaml_vs_pm_contradiction` | The cited YAML and the PM's prior P5 answer disagree; the chat reported the YAML value while the brief encoded the PM answer (or vice versa) | Escalate to `prd-orchestrator` — the breakdown's `investigation_context` likely needs re-running for that component. |
| `cosmetic` | Anchor mismatch is presentation-only (whitespace, casing) with no functional consequence | Accept into PRD §7 Open Items with stated reason; no re-handoff. |

The interviewer chat does not propose fixes to the artifact directly. It
amends the brief and re-runs (L11 C1). The brief is the contract; the
artifact is the output.

---

## 8. Re-handoff discipline

When a handoff produces an artifact with deviations the PM does not accept,
the brief is amended and the same handoff chat is asked to regenerate. Rules:

- The same chat is reused so the handoff agent retains context on prior
  decisions. The PM pastes a short prompt asking it to re-read the brief
  and produce the same two outputs.
- The brief's revision is timestamped in a `## Revision history` footer so
  the handoff agent can detect what changed.
- The handoff chat must overwrite the prior artifact and summary in place —
  never append.
- The interviewer chat re-runs Section 7 validation on the new summary.

If a re-handoff fails a second time on the same item, the interviewer chat
escalates to the PM with a written diagnosis: brief defect vs handoff-chat
defect vs ambiguous requirement. The PM rules on the path forward.

---

## K. Tier 1 inside-chat protocol (binding — Phase C addition)

The Phase 0 dry-run proved the brief-in / summary-out pattern works **only**
when the Tier 1 fidelity self-review runs **inside the handoff chat**, before
that chat writes its `_summary.md`. Phase C makes this the binding contract
for all three surfaces.

### K.1 — Where Tier 1 self-review runs

Tier 1 self-review runs **inside the handoff chat**. The interviewer chat
**never** runs Tier 1 self-review post-return — that defeats the T5
context-saving intent because it forces the interviewer chat to read the
full artifact (the very thing T5 exists to avoid).

| Surface | Tier 1 self-review location | Tier 1 self-review timing |
|---|---|---|
| Demo | Inside the demo handoff chat | After the demo HTML and behavior manifest are written, **before** `demos/_summary.md` is written |
| Sample-data | Inside the sample-data handoff chat | After the JSON file(s) are written, **before** `sample-data/_summary.md` is written |
| Component-spec | Inside the component-spec handoff chat | After `component-spec.md` is written, **before** `component-spec/_summary.md` is written |

### K.2 — Brief carries the Tier 1 checklist

Every brief embeds its surface's Tier 1 self-review checklist in its
Section 12 (per Section 5 above). The handoff chat reads the checklist
from the brief — never from this file directly. This keeps the brief
self-contained per the brief-as-contract rule.

The handoff prompts in `handoff-prompt-templates.md` reinforce the rule by
restating the Tier 1 walk in their hard-rules sections. The prompt body and
the brief's Section 12 say the same thing in slightly different words by
design — redundancy at the gate is correct.

### K.3 — What the Tier 1 self-review covers (per surface)

The Tier 1 checklist always includes the two application-fidelity items
from Section 4.3 (cited-YAML structural-and-copy fidelity AND
no-application-equivalent flagging) plus surface-specific items:

**Demo Tier 1 items (in addition to the two application-fidelity items):**

- Every brief Section 4 scenario is rendered or explicitly skipped with a
  one-sentence reason in `_summary.md`.
- Every verbatim copy string in the demo matches either the brief Section 6
  verbatim list, the cited YAML's `copy_strings_verbatim` block, or a
  `[TEXT TBD]` marker.
- Every AC referenced in the brief Section 4 has a matching scenario
  selectable in the AC sidebar. AC IDs are sequential `AC-NNN` (the
  surface category lives in the AC's `surface` field, not in the ID).
- The `prdHash` value in the `demos/_summary.md` header matches the
  SHA-256 of the brief's cited PRD content.
- The single-file constraint holds: no external assets except CDN fonts/icons.
- **N6 read-completeness (new — Family N).** For every entry in the
  brief's Section 3, the handoff chat has read the YAML end-to-end and
  extracted every anchor named in `expected_anchors`. The `## YAML
  reads` H2 table in `demos/_summary.md` is populated with the
  verbatim `anchors_extracted` values. A skimmed read, a guessed
  anchor, or an empty cell in the anchors table is a hard fail.

**Sample-data Tier 1 items (in addition to the two application-fidelity items):**

- Every brief Section 4 record set is written or explicitly skipped with a
  one-sentence reason.
- Every record conforms to the cited schema (field types, required fields,
  enums).
- Every invented value is marked `_invented: true`.
- Edge-case rows trace to specific sequential `AC-NNN` IDs from the AC
  sibling (where the brief declares the linkage). Legacy bucketed
  `AC-EC-NNN` references are retired — only present in pre-lift bundles
  during the dual-layout backfill-on-touch window.
- **N6 read-completeness (new — Family N).** For every entry in the
  brief's Section 3, the handoff chat has read the cited schema / YAML
  end-to-end and extracted every anchor named in `expected_anchors`.
  The `## YAML reads` H2 table in `sample-data/_summary.md` is
  populated with the verbatim `anchors_extracted` values. A skimmed
  read or a guessed anchor is a hard fail.

**Component-spec Tier 1 items (in addition to the two application-fidelity items):**

- Every brief Section 4 entry is specified or explicitly skipped with a
  one-sentence reason.
- Every six-element entry has all six elements (name/type, functional
  description, states + triggers, interactions, selectable options, data
  binding) for new and affected entries.
- No AC text appears inline in the spec — only AC ID cross-references to
  `acceptance-criteria.md` (sequential `AC-NNN`).
- Every requirement that would otherwise live only in the spec is flagged
  in the `_summary.md` Deviations section as a brief defect.
- **N6 read-completeness (new — Family N).** For every entry in the
  brief's Section 3, the handoff chat has read the cited YAML
  end-to-end and extracted every anchor named in `expected_anchors`.
  The `## YAML reads` H2 table in `component-spec/_summary.md` is
  populated with the verbatim `anchors_extracted` values. A skimmed
  read or a guessed anchor is a hard fail.

### K.4 — Failure handling inside the handoff chat

If the Tier 1 walk surfaces a failing item:

1. The handoff chat **fixes the artifact in place**, then re-walks the full
   checklist. Partial fixes are not allowed.
2. If the failure is unrecoverable from the brief (e.g. the brief's
   verbatim copy contradicts a cited YAML and the chat cannot decide which
   wins), the chat records the failure under Deviations and Open Questions
   in the summary, leaves the artifact in its best-effort state, writes the
   summary, and STOPS.
3. The handoff chat does **not** open a separate chat or escalate
   programmatically — escalation is the PM's job once the interviewer chat
   reads the summary.

### K.5 — Why this is the right place for Tier 1

The Phase 0 dry-run report §10 root-cause framing established that
fidelity gaps are **brief defects**, not handoff-chat defects. Running
Tier 1 inside the handoff chat catches application-fidelity gaps **before**
the summary is written, which means the deviation is recorded as a brief
defect (the right framing) rather than as a handoff failure. The
interviewer chat then amends the brief on return; the handoff chat does
not need to be re-run unless the brief amendment is non-trivial.

If Tier 1 ran in the interviewer chat post-return, it would force the
interviewer to load the full artifact, defeating T5's context savings, and
it would frame fidelity gaps as handoff defects rather than brief defects.
Both consequences degrade the pattern.

---

## 9. Anti-patterns (forbidden in every brief)

- **Silent gap.** A scenario, record, or component entry whose visible
  affordance traces to neither a cited YAML nor an explicit no-equivalent
  call-out. Hard fail — fix the brief before handoff.
- **Paraphrased copy.** A user-facing string in the brief that does not
  match the source codebase string or carry a `[TEXT TBD]` marker.
- **Implementation instruction.** A brief that tells the handoff chat *how*
  to build the artifact rather than *what* outcomes it must produce. The
  brief describes outcomes, scenarios, and references; the handoff chat
  decides implementation within the cited-YAML constraints.
- **Hidden YAML reading list.** Citing YAMLs scattered through the brief
  rather than in a single Section 3 list with `{ path, read_mode,
  expected_anchors }` entries. The handoff chat's Tier 1 self-review
  checks the Section 3 list character-for-character — scattered
  references will be missed.
- **Section 3 without anchors.** A Section 3 entry that names a YAML
  path but omits `expected_anchors`. Without anchors there is no
  read-proof in the `## YAML reads` summary table; the handoff chat
  can claim to have read the file without doing so. Every Section 3
  entry MUST carry at least one anchor.
- **Open-ended STOP.** A brief that does not explicitly state STOP after
  the summary. Without it, handoff chats start proposing next-phase work,
  burning context the interviewer chat cannot recover.
- **Programmatic-spawn assumption.** A brief that assumes the handoff
  agent is a `Task` subagent and uses subagent-only constructs. Briefs are
  paste-ready for a human-driven fresh chat — they do not assume anything
  about how the handoff is invoked.
- **Summary schema non-conformance (L11 C7).** A summary that omits any
  of the six required H2 headings, malforms the `## YAML reads` table,
  or omits the `prdHash` header line under the H1. The interviewer
  chat treats the summary as untrusted, emits `prd_handoff_re_run` with
  `rerunReason: 'summary_schema_invalid'`, amends the brief to paste
  the §6 summary contract verbatim, and re-handoffs.
- **Recurring re-handoffs (L11 C8).** When the same surface re-handoffs
  more than twice, the interviewer chat escalates to `prd-orchestrator`
  — the breakdown's `investigation_context` for that surface is
  probably defective. The PM may accept the deviation into PRD §7 Open
  Items with a stated reason rather than escalating.
