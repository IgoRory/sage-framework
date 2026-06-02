# Traceability Template

Reference for prd-interviewer. Self-contained — no external skill references.

Use this template to produce the `traceability.md` artifact for one
sub-PRD. The file is saved to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/traceability.md` and is read by
`traceability-reviewer`, `prd-completeness-check`, `dev-interview`,
`phase-splitter`, and `kickoff-dev-review`.

A production-grade traceability artifact is a **bidirectional mapping**.
This template adds the L1–L12 requirement that the file is **auto-built
at P9** from the in-memory AC list plus the three handoff `_summary.md`
files. The output is **table-only, deterministic, no narrative prose**.

See `production-grade-quality-bar.md` §6 for the Pass Conditions this
template satisfies.

---

## When to write

- Auto-built at P9 immediately before `bundle-manifest.json` is
  finalised. The interviewer reads the AC list from in-memory state and
  the three handoff `_summary.md` files (demo, sample-data, component-
  spec) to build every row deterministically.
- Re-built after any handoff re-run that adds, removes, or renames an
  AC, a `scenario_id`, a sample-data record set, or a component-spec
  entry.
- Re-built by `prd-amend` after any PM amendment that touches §4 or AC
  content.

The interviewer **does not narrate** during the build — every cell is a
verbatim cross-reference from the source artefact. Empty cells are
`—`. Genuinely-inapplicable cells are `n/a` with a one-line reason in
the Notes column.

---

## Template

The traceability file begins with a YAML derivative frontmatter block
(see [`prd-section-schema.md`](./prd-section-schema.md) — "Frontmatter
for every other derivative"). The frontmatter is terminated by a `---`
delimiter.

````markdown
---
derivativeOf: prd.md
prdHash: [sha256-hex of prd.md body content at the moment this file was written]
writtenAt: [ISO 8601 UTC]
producer: interviewer
---

# Traceability — [Feature Title] — [sub-prd-id]

**Parent PRD:** [link to `prd.md`]
**Acceptance criteria:** [link to `acceptance-criteria.md`]
**Component spec:** [link to `component-spec.md`]
**Demos:** [list demo file links]
**Sample data:** [link to `sample-data/` folder]
**Date:** [DD-MMM-YYYY]
**Version:** [v1.0 | v1.1 | …]

---

## 1. Forward trace — AC → §4 → surfaces

Every AC ID from `acceptance-criteria.md` appears in this table, in
AC ID order. The `§4 IDs` column lists every `linked_requirement_ids`
value from the AC entry. Surface columns mark each cell as a comma-
separated list of references or `n/a` (with a one-line reason in the
Notes column when an AC is genuinely not exercisable on a surface).

| AC ID | surface | §4 IDs | Demo `scenario_id`(s) | Sample-data record IDs | Component-spec entries | Notes |
|---|---|---|---|---|---|---|
| AC-001 | UI | UI-001, PA-002 | nav-admin | — | SideNav.UnitCosting | |
| AC-002 | UI | UI-005, WF-003 | prod-filtered-empty | RetailProducts.allNull | ProductReadGrid (filtered-empty state) | Seed inversion documented in demo `_summary.md` Deviations |
| AC-003 | error | VC-001, ER-002, UI-007 | prod-validation | RetailProducts.dirty.invalidValue | ProductEditGrid, ValidationToast | |
| AC-004 | UI | WF-002, UI-008, NM-003 | prod-save | RetailProducts.dirty.autoLoan7yr, RetailProducts.dirty.mortArm | ProductEditGrid, SaveToast | |
| … | … | … | … | … | … | |

---

## 2. Reverse trace — §4 → AC

Every §4 sub-section ID from `prd.md` appears in this table. The
bidirectional invariant requires every §4.NNN to link to ≥1 AC.

| §4 ID | §4 sub-section | AC ID(s) | Notes |
|---|---|---|---|
| DM-001 | §4.1 Data Model & Entities | AC-006, AC-007 | |
| CL-001 | §4.2 Calculation & Logic | AC-009 | |
| UI-001 | §4.5 UI & Interaction | AC-001 | |
| UI-005 | §4.5 UI & Interaction | AC-002 | |
| VC-001 | §4.6 Validation & Constraints | AC-003 | |
| ER-002 | §4.7 Error Handling | AC-003, AC-014 | |
| WF-002 | §4.4 Workflow & State | AC-004 | |
| WF-003 | §4.4 Workflow & State | AC-002 | |
| PA-002 | §4.9 Permissions & Access Control | AC-001 | |
| NM-003 | §4.8 Notifications & Messaging | AC-004 | |
| … | … | … | |

Any §4.NNN row with no mapped AC is a **bidirectional invariant
violation** and is surfaced in Section 4 (Coverage gaps).

---

## 3. Reverse trace — surface element → AC

One subsection per surface. Every element in that surface (every demo
`scenario_id`, every sample-data record set, every component-spec
entry) appears mapped to at least one AC.

### 3.1 Demo scenarios → AC

| `scenario_id` | AC ID(s) | Demo file | Notes |
|---|---|---|---|
| nav-admin | AC-001 | demo-interactive.html | |
| prod-filtered-empty | AC-002 | demo-interactive.html | |
| prod-validation | AC-003 | demo-interactive.html | |
| prod-save | AC-004 | demo-interactive.html | |
| concurrency | AC-014 | demo-interactive.html | |
| … | … | … | |

### 3.2 Sample-data record sets → AC

| Record set | AC ID(s) | File | Notes |
|---|---|---|---|
| RetailProducts.* (default) | AC-005, AC-006, AC-007, AC-008 | sample-data/retail-products.json | |
| RetailProducts.allNull | AC-002 | sample-data/retail-products-all-null.json | Edge case — every leaf NULL Unit Cost |
| RetailProducts.empty | AC-011 | sample-data/retail-products-empty.json | Empty hierarchy |
| RetailProducts.dirty.invalidValue | AC-003 | sample-data/retail-products-dirty.json | Pre-seeded dirty leaf for validation scenario |
| RetailProducts.dirty.autoLoan7yr | AC-004 | sample-data/retail-products-dirty.json | Pre-seeded dirty leaf for Save scenario |
| RetailProducts.dirty.mort30yrFixed | AC-014 | sample-data/retail-products-concurrency.json | Pre-seeded dirty leaf for concurrency scenario |
| … | … | … | |

### 3.3 Component-spec entries → AC

| Component ID | AC ID(s) | Page | Notes |
|---|---|---|---|
| SideNav.UnitCosting | AC-001 | (global) | |
| ProductReadGrid | AC-002, AC-005, AC-006, AC-007, AC-011 | Product Unit Costs | |
| ProductEditGrid | AC-003, AC-004, AC-008 | Product Unit Costs | |
| ValidationToast | AC-003 | (global toaster) | |
| SaveToast | AC-004 | (global toaster) | |
| ConcurrencyDialog | AC-014 | (global modal) | |
| … | … | … | |

---

## 4. Coverage gaps

List every AC with no mapped element in an applicable surface, every
§4.NNN with no mapped AC, and every surface element with no mapped AC.
Each gap has a stated resolution.

| Gap | Direction | Resolution |
|---|---|---|
| AC-019 has no demo `scenario_id` | AC → demo | `demoable: false`. Multi-browser timing condition cannot be simulated in a single HTML file. Flagged in PRD §7 Open Items. |
| `scenario_id: debug-state-inspector` has no mapped AC | demo → AC | Demo-rail furniture (no application equivalent per Family M flag). Documented in demo brief Section 10 no-equivalent call-outs. Acceptable. |
| Sample-data set `RetailProducts.maximalDepth` has no mapped AC | sample-data → AC | Synthetic stress-test set — flagged for developer use only. Acceptable. |

If a gap has no acceptable resolution, surface it as an Open Item in
`prd.md` §7 and do not ship the traceability artifact as passing.

[If no gaps: `None — full bidirectional coverage achieved.`]

---

## 5. Build provenance

| Field | Value |
|---|---|
| Built at | [ISO 8601 UTC — same as `writtenAt` in frontmatter] |
| Built from | `acceptance-criteria.md` (in-memory AC list), `demos/_summary.md`, `sample-data/_summary.md`, `component-spec/_summary.md` |
| AC count | [N] |
| §4 ID count | [N] |
| Demo scenario count | [N] |
| Sample-data record-set count | [N] |
| Component-spec entry count | [N] |
| Coverage gap count | [N] |

---

## Appendix — Self-review checklist (auto-applied by the interviewer at P9)

- [ ] Every AC ID from `acceptance-criteria.md` appears in Section 1 in
  AC ID order.
- [ ] Every Section 1 row's §4 IDs match the AC entry's
  `linked_requirement_ids` value character-for-character.
- [ ] Every Section 1 row's `scenario_id` reference appears in the
  demo's `_summary.md` Scenario coverage table.
- [ ] Every Section 1 row's sample-data record ID appears in the
  sample-data `_summary.md` Record coverage table.
- [ ] Every Section 1 row's component-spec entry appears in
  `component-spec.md` with all six elements populated.
- [ ] Every §4.NNN in `prd.md` appears in Section 2 with at least one
  mapped AC (bidirectional invariant). Violations surface as Section 4
  gaps.
- [ ] Every Section 3.x table includes every element from its surface
  (no orphans).
- [ ] Every Section 4 gap has either a stated resolution or an Open Item
  reference in `prd.md` §7.
- [ ] No AC ID, §4 ID, `scenario_id`, record ID, or component ID is
  misspelled vs its source artefact (character-for-character match).
- [ ] `prdHash` derivative header matches the SHA-256 of the current
  `prd.md` body content.
````

---

## Anti-patterns

- **Surface stub.** Listing surfaces as headings without populating
  their reverse-trace rows. Hard fail — the surface is undocumented and
  the contract is broken.
- **Self-referential AC.** An AC that traces to itself ("AC-005 →
  AC-005"). Hard fail — at least one external surface must exercise the
  AC, or it belongs in the not-demoable gap list with a stated reason.
- **Cosmetic-only gap entry.** A gap row that says "TBD" or "to be
  addressed". Hard fail — every gap has a resolution or an Open Item
  reference at write time.
- **Narrative prose.** Any paragraph outside the prescribed tables.
  The traceability artifact is **table-only**. Narrative belongs in
  `prd.md` §8 (pointer prose) or the AC entries themselves.

---

## Notes for the interviewer

- The interviewer **does not author** traceability rows manually. The
  rows are deterministic projections of the AC list (with their
  `linked_requirement_ids`, `surface`, `demoable` fields), the demo
  `_summary.md` Scenario coverage table, the sample-data `_summary.md`
  Record coverage table, and the component-spec entry list.
- If the AC list or any handoff `_summary.md` is missing required
  fields, the build halts and the failure surfaces as a Family C C7
  failure (summary schema non-conforming) — re-handoff per
  `sub-agent-delegation.md` §8.
- `prdHash` derivative header is computed at write time from the
  current `prd.md` body content.
- Pre-write artifact-bar walk (Family G G3) runs against
  `production-grade-quality-bar.md` §6 (Traceability bar) before the
  file is written. Failure: do not write. Surface failing Pass
  Condition. Resolve gap. Retry.
