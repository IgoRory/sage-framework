# Production-Grade Quality Bar

Reference for prd-interviewer. Self-contained — no external skill references.

The yardstick every sub-PRD's deliverables are measured against. Every
artifact (PRD, acceptance-criteria, component-spec, demo, sample-data,
traceability) is held to one of the bars below. Failing a bar means the
artifact is not production-grade — fix it, do not ship.

The application-fidelity hard rule (Family M, see `sub-agent-delegation.md`
§4) is binding across every artifact in this file. Where this file
references "the application", the citation discipline of
`sub-agent-delegation.md` §4.1 applies.

---

## L6 binding — K1, K2, and G3

This file is **the gating contract** behind Family K and Family G G3.

- **K1 — Bundle gating.** The full bundle MUST pass the bars below
  before any final `prd.md` write. The interviewer's pre-write artifact-
  bar walk (Family G G3) enforces this by walking the relevant bar's
  Pass Conditions for each artifact before any file write. If any Pass
  Condition is unmet, the interviewer **does NOT write** — it surfaces
  the failing Pass Condition, resolves the gap (PM clarifies, brief is
  amended, handoff is re-run, or the PM accepts the gap as a DI), then
  retries.
- **K2 — Reduced-fidelity markers.** When an L5 readiness check was
  overridden at Step 0 (override-eligible categories — thin Component
  Pattern Summaries, manifest stale, cited YAML missing, breakdown
  citations stale en masse, telemetry sink unavailable), the resulting
  PRD bundle MUST carry an explicit **reduced-fidelity marker** in the
  PRD §7 Open Items and in the bundle-manifest top-level
  `reducedFidelity` field. The marker names which override was applied
  and quotes the PM's justification verbatim. Downstream consumers
  (`prd-completeness-check`, `dev-interview`, `phase-splitter`) read the
  marker and adjust their expectations — e.g. completeness-check
  reduces score expectations on dimensions that depend on the missing
  input rather than failing the bundle.
- **G3 — Pre-write artifact-bar walk.** Before ANY interviewer-authored
  artifact is written (`prd.md`, `acceptance-criteria.md`,
  `reuse-map-draft.md`, `component-pattern-confirmation.md`,
  `traceability.md`, plus each handoff brief), the interviewer walks
  the matching bar's Pass Conditions inline and records the result.
  Failure emits `prd_pre_write_bar_walk_failed` with the failing
  `failedPassCondition` and `artifact` enum. The artifact is not
  written until every Pass Condition is met (or accepted as a DI with
  explicit reduced-fidelity marker per K2).

---

## 1. PRD bar — plain English outcomes only

A production-grade PRD describes **what the user observes**, not what
the system does internally. The reader is a Business Analyst, QA
engineer, or Product reviewer — not a developer reading implementation
steps.

**Pass Conditions:**

- **PRD-PC1.** Every requirement is stated as an outcome the user, the
  data, or a downstream consumer can observe.
- **PRD-PC2.** No SP names, no return-code values, no class / flag /
  view-column names, no API endpoints. Every technical construct is
  translated to its business equivalent. PM-directed SQL is admissible
  verbatim only when explicitly requested by the PM.
- **PRD-PC3.** No implementation steps. Phrases like "the system calls
  X then Y" are rewritten as "after the user does X, the next thing
  they see is Y".
- **PRD-PC4.** Every non-obvious design choice has a stated rationale
  ("we chose A rather than B because …").
- **PRD-PC5.** §5 Data Migration is addressed explicitly — even when
  the answer is `Not applicable — [reason]`.
- **PRD-PC6.** Every §4 sub-section in the P2 coverage map carries one
  or more `{PREFIX}-NNN` entries OR an explicit `Not applicable —
  [reason]` notice. No silent omissions.
- **PRD-PC7.** §4.14 Cross-Page Impacts entries reference a canonical
  behaviour entry in the originating sub-PRD (sub-PRD ID + requirement
  ID). No behaviour-text duplication.
- **PRD-PC8.** YAML frontmatter is present with all required keys
  (`title`, `subPrdId`, `featureId`, `version`, `author`, `date`,
  `prdHash`). `prdHash` is computed from the body content after the
  closing `---` (or carries `'[COMPUTATION_FAILED]'` if computation
  failed per Family L11 D5).
- **PRD-PC9.** Version History entries carry full-name author and
  concrete change summary. PM edits and agent edits are distinguishable
  from the author field alone.

**Anti-patterns (fail):**

- "The save handler calls `usp_SaveProductCosts` which returns 1 on
  success." *(Rewrite: "When the user clicks Save, the row counters
  reset to clean and a success toast appears.")*
- "Set the `isAODDependent` flag to true." *(Rewrite: "The page
  refreshes when the global As-Of Date changes.")*
- "Implement validation in the cell editor." *(Rewrite: "When the user
  enters an invalid value, the cell highlights red and the Save button
  disables.")*
- §4.5 UI subsection silently omitted on a backend sub-PRD. *(Fail
  PRD-PC6 — write `Not applicable — backend-only sub-PRD with no UI
  surface` explicitly.)*

---

## 2. Acceptance criteria bar — outcome-only, sequential `AC-NNN`

A production-grade AC describes a testable outcome in Given / When /
Then / eXample form. The AC is independent of the PRD section it lives
in and independent of the component that implements it. The AC names
what is observed, not how it is produced.

**Pass Conditions:**

- **AC-PC1.** Each AC has explicit `given`, `when`, `then`, `example`,
  and `expected_result` clauses.
- **AC-PC2.** The Then clause is a single observable outcome — "the
  toast `Success` / `Product Unit Costs saved successfully` appears",
  not "the save succeeds".
- **AC-PC3.** ACs do not duplicate PRD prose — they live in
  `acceptance-criteria.md` as a sibling artifact and are referenced
  from the PRD only via the bidirectional invariant.
- **AC-PC4.** Edge cases, error paths, and empty states each have their
  own AC entries rather than being smuggled in as PRD prose. Surface
  determines categorisation, not the ID.
- **AC-PC5.** Every AC carries `id` (sequential `AC-NNN`, no buckets),
  `linked_requirement_ids` (one or more §4.NNN), `surface` (`UI` /
  `calc` / `data` / `error`), `demoable` (boolean).
- **AC-PC6.** Bidirectional invariant: every §4.NNN in `prd.md` is
  linked from ≥1 AC. Coverage check pre-write at P8.
- **AC-PC7.** Verbatim user-facing strings (toast copy, dialog body,
  validation messages, button labels) are quoted exactly with one of
  the four sourcing markers: `[Source: path/to/file:lineN]`,
  `[Proposed — approved by PM]`, `[PM-provided]`, `[TEXT TBD —
  requires PM decision]`.
- **AC-PC8.** YAML derivative frontmatter is present with
  `derivativeOf`, `prdHash`, `writtenAt`, `producer: interviewer`.
- **AC-PC9.** Appendix B (terminology / glossary) is populated or
  carries `Not applicable — all AC clauses use widely-understood
  business language.`

**Anti-patterns (fail):**

- "AC: The system handles the case where the data is empty." *(Vague
  — rewrite as observable state: "Given the Product hierarchy is
  empty, When the read view loads, Then the empty-state message
  `No products configured. Click the edit button to set up your
  Product Unit Costs` is displayed and the switch-view button is
  disabled with the tooltip `This page is locked for editing as other
  pages must be set up first`.")*
- AC ID `AC-REQ-005` on a freshly-authored sub-PRD. *(Fail AC-PC5 —
  the legacy bucketed format is retired; use sequential `AC-NNN` with
  `surface` field. Legacy IDs appear only in pre-lift bundles awaiting
  backfill-on-touch.)*

See `acceptance-criteria-template.md` for the canonical AC structure.

---

## 3. Component-spec bar — developer-facing surface map (no AC duplication)

A production-grade component spec is a **surface map** for the
developer. Each component entry describes states, data bindings,
interactions, and visible affordances — not the user requirements
(those live in `prd.md` §4) and not the test assertions (those live in
`acceptance-criteria.md`).

**Pass Conditions:**

- **CS-PC1.** One entry per component from the P5 inventory, ordered
  by page then by type (new → affected → reused).
- **CS-PC2.** Every NEW / AFFECTED / REUSED-with-differences entry has
  all six elements from `component-spec-template.md`: name/type
  (with cited YAML(s)), functional description, states + triggers,
  interactions (each row carrying the §4.NNN ID that defines the
  action), selectable options (or N/A), data binding.
- **CS-PC3.** Every entry's `Covers PRD requirements` line lists one
  or more `{PREFIX}-NNN` IDs. Every entry's `Implements ACs` line lists
  one or more `AC-NNN` IDs.
- **CS-PC4.** States are described as predicates, not as
  implementation flags.
- **CS-PC5.** No requirement, edge case, or error message lives only
  in the component spec. Every requirement is in `prd.md` §4; every
  AC is in `acceptance-criteria.md`. The spec references them — it
  does not re-author them.
- **CS-PC6.** Every entry that has an application equivalent cites
  the matching YAML(s) under `.context/components/` (Family M). No-
  equivalent entries carry the explicit Family M flag.
- **CS-PC7.** YAML derivative frontmatter is present with
  `producer: handoff:component-spec`.

**Anti-patterns (fail):**

- "When `_isAODDependent === true`, refresh on AOD change."
  *(Implementation flag — rewrite as predicate: "Page refreshes when
  the global As-Of Date changes.")*
- A new AC introduced in the component spec that does not also appear
  in `acceptance-criteria.md`. *(Hard fail CS-PC5 — every AC must
  appear in the AC sibling; the spec is a surface map, not a
  requirements doc.)*
- A NEW entry with no cited YAML on a surface that obviously has an
  application equivalent. *(Hard fail CS-PC6 / Family M.)*

See `component-spec-template.md` for the canonical structure.

---

## 4. Demo bar — application-faithful, scenario-complete

A production-grade demo lets a PM or QA reviewer click any scenario
tile and immediately observe the documented outcome without reading the
brief or PRD. Every visible affordance either mirrors the production
application (per a cited YAML — Family M hard rule) or is explicitly
flagged as "no application equivalent — generator's choice" in the
demo brief.

**Pass Conditions:**

- **DM-PC1.** Every `demoable: true` AC from `acceptance-criteria.md`
  has a clickable scenario tile with a stable `scenario_id` and the
  AC ID rendered in the tile.
- **DM-PC2.** Every cited YAML's structural and copy fidelity is
  honoured. Tooltip text, button labels, dialog wording, empty-state
  messages, validation errors, and toast copy match the YAML / brief
  Section 6 character-for-character.
- **DM-PC3.** Every uncited affordance has an explicit no-equivalent
  call-out in the brief. The demo's `_summary.md` Deviations section
  calls out any no-equivalent surface that emerged during build.
- **DM-PC4.** Self-contained: single HTML file, CDN-only external
  assets (Font Awesome, Google Fonts), no build step, no real network
  calls.
- **DM-PC5.** The demo serves both audiences in
  `demo-guidelines.generation.md` § Core principle: freeform
  exploration AND AC-panel-driven verification.
- **DM-PC6.** Demo posture (one of the four L4 sub-lock 2 postures) is
  recorded in the brief and honoured exactly by the handoff chat. No
  posture-switching mid-build.
- **DM-PC7.** Family N read discipline applied — every file named in
  the demo brief Section 3 is read end-to-end; the `_summary.md`
  `## YAML reads` H2 table is populated with verbatim
  `anchors_extracted` values.

**Anti-patterns (fail):**

- A scenario tile that fires no observable change — silent click.
  *(Hard fail DM-PC1 — every tile must reset state and drive a
  documented outcome.)*
- Fabricated copy. Tooltip text invented because the YAML did not
  surface it. *(Hard fail DM-PC2 — fabricated text creates false PM
  confidence.)*
- Application affordance silently substituted with a generator's
  choice. *(Hard fail Family M.)*
- Handoff chat switches posture mid-build (e.g. brief said Posture 2
  AC bar atop production page, chat ships Posture 1 scenario theater).
  *(Hard fail DM-PC6.)*

---

## 5. Sample-data bar — schema-conformant, edge-case-covering

Production-grade sample data is what the demo runs against and what
the developer seeds tests against. The data is schema-conformant,
covers the edge cases the AC list will exercise, and represents NULL /
empty / maxima explicitly.

**Pass Conditions:**

- **SD-PC1.** Every record matches the source schema (field types,
  required fields, enums). For matched components, "source schema" is
  the cited YAML or the underlying data shape it implies. For new
  components, the brief defines the schema.
- **SD-PC2.** The data set includes the boundary rows the ACs
  exercise: at least one NULL where NULL is meaningful, at least one
  empty / zero-count entity, at least one maxima (large-number,
  long-string, deepest-hierarchy) where maxima matter.
- **SD-PC3.** Every record has a stable ID the demo / tests can
  address by name.
- **SD-PC4.** No fabricated business meaning. Realistic invented
  values (counts in the low thousands for niche products) are
  explicitly marked as `"_invented": true` so a developer does not
  seed production data from them.
- **SD-PC5.** Every record set listed in `_summary.md` Record coverage
  table is keyed by AC ID(s) — the bidirectional invariant for sample-
  data → AC mapping.
- **SD-PC6.** Family N read discipline applied — every file named in
  the sample-data brief Section 3 (schema YAMLs, cited components) is
  read end-to-end; the `_summary.md` `## YAML reads` H2 table is
  populated.

**Anti-patterns (fail):**

- Sample rows that pass the schema but exercise none of the AC edge
  cases. *(Hard fail SD-PC2.)*
- Hidden assumptions — implicit ordering, implicit non-null defaults
  — that the production schema does not guarantee. *(Hard fail SD-PC1
  / SD-PC4.)*

---

## 6. Traceability bar — bidirectional, deterministic, table-only

Production-grade traceability is a bidirectional mapping. Every AC
traces forward to at least one element in each applicable surface;
every element in each surface traces back to at least one AC; every
§4.NNN traces back to ≥1 AC.

**Pass Conditions:**

- **TR-PC1.** Section 1 (AC → §4 → surfaces) contains every AC ID
  from `acceptance-criteria.md` in AC ID order. The `§4 IDs` column
  matches the AC entry's `linked_requirement_ids` character-for-
  character.
- **TR-PC2.** Section 2 (§4 → AC) contains every §4.NNN ID from
  `prd.md`. Each row carries ≥1 mapped AC (bidirectional invariant).
- **TR-PC3.** Every `demoable: true` AC has at least one mapped
  `scenario_id` in Section 1; every demo `scenario_id` from
  `demos/_summary.md` appears in Section 3.1 mapped to ≥1 AC.
- **TR-PC4.** Every sample-data record set from
  `sample-data/_summary.md` appears in Section 3.2 mapped to ≥1 AC
  that exercises it.
- **TR-PC5.** Every component-spec entry from `component-spec.md`
  appears in Section 3.3 mapped to ≥1 AC whose Then clause that
  component renders.
- **TR-PC6.** Gaps are surfaced in Section 4 — an AC with no mapped
  demo scenario is flagged either as `demoable: false` with reason or
  as a coverage gap to fix. Cosmetic-only gap entries (`TBD`) are
  forbidden.
- **TR-PC7.** Table-only. No narrative prose outside the prescribed
  table headings.
- **TR-PC8.** YAML derivative frontmatter is present with
  `producer: interviewer`.

See `traceability-template.md` for the canonical structure.

---

## 7. Cross-artifact consistency bar

A production-grade sub-PRD has internally consistent artifacts.
Failures here are bugs in the interview process, not in any single
artifact.

**Pass Conditions:**

- **XA-PC1.** Every §4.NNN in `prd.md` has at least one AC in
  `acceptance-criteria.md`. No PRD requirement is silently uncovered.
- **XA-PC2.** Every AC's Then clause is exercised by at least one
  demo scenario OR is explicitly flagged as `demoable: false` in the
  AC entry and in `traceability.md` Section 4.
- **XA-PC3.** Every component named in `prd.md` §4.5 (UI) appears in
  `component-spec.md` with all six elements populated.
- **XA-PC4.** Every user-facing string used in the demo, the AC, or
  the component spec matches the PRD's verbatim text section
  character-for-character (or is marked `[TEXT TBD]` with the same
  marker text in every artifact).
- **XA-PC5.** Every cited YAML in any brief actually exists at the
  cited path under `.context/components/`. Broken citations are a
  brief defect (Family M).
- **XA-PC6.** Every derivative's `prdHash` header matches the current
  SHA-256 of `prd.md` body content. STALE derivatives surface in §8
  Related Artefacts and trigger `prd-amend` per the post-completion
  amendment flow.
- **XA-PC7.** `bundle-manifest.json` `files[]` array enumerates every
  artifact present in the bundle with `prdHash`, `writtenAt`,
  `producer`, `role`. Files on disk not in the manifest, or manifest
  entries with no file on disk, are a Family C C7 defect.

---

## 8. Failure mode

If any artifact fails its bar (Family G G3 pre-write walk):

1. The interviewer chat **does NOT write** the failing artifact.
2. The interviewer surfaces the failure to the PM with a one-line
   diagnosis (which Pass Condition failed, which anti-pattern, which
   resolution path).
3. Telemetry emits `prd_pre_write_bar_walk_failed` with the
   `failedPassCondition` and `artifact` enum.
4. The PM decides:
   - **(a)** amend the brief and re-handoff (for handoff-authored
     artefacts);
   - **(b)** answer the missing question (for interviewer-authored
     artefacts);
   - **(c)** accept the gap into `prd.md` §7 Open Items with a stated
     reason and add the matching reduced-fidelity marker per Family
     K K2;
   - **(d)** escalate to the orchestrator if the failure suggests
     `prd-breakdown.[sub-prd-id].md` was defective.
5. After resolution, the interviewer retries the bar walk. No artifact
   ships to `prd-completeness-check` with an unresolved bar failure.

---

## 9. Pass Condition catalogue (consumers — informational)

`prd-completeness-check` references the Pass Condition IDs above as
its scoring dimensions:

| Dimension | Pass Conditions |
|---|---|
| D1 — PRD quality | PRD-PC1 .. PRD-PC9 |
| D2 — AC quality | AC-PC1 .. AC-PC9 |
| D3 — Component spec | CS-PC1 .. CS-PC7 |
| D4 — Demo quality | DM-PC1 .. DM-PC7 |
| D5 — Sample data | SD-PC1 .. SD-PC6 |
| D6 — Traceability | TR-PC1 .. TR-PC8 |
| D7 — Cross-artifact consistency | XA-PC1 .. XA-PC7 |
| D8 — Anchor Attestation completeness (Family N) | Family N N1–N8 enforced via brief Section 3 + `_summary.md` `## YAML reads` H2 |
| D9 — Reduced-fidelity marker discipline (Family K K2) | When an L5 override applied at Step 0, the reduced-fidelity marker is present in PRD §7 and `bundle-manifest.json` |

Dimensions D1–D7 map one-to-one onto §§1–7 of this file. D8 and D9
are enforced by Family N (handoff read discipline) and Family K K2
(reduced-fidelity marker) respectively, both authoritative in
`shared-protocols.md`.
