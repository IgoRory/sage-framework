# PRD Template

Reference for prd-interviewer. Empty PRD scaffold matching the L1–L12
8-section schema exactly. Use this structure when generating the PRD draft
from the interview answer record.

The PRD is the **outcome-only business deliverable**. It describes what
the feature does for the user, the rules it must honour, and the scope of
change — in plain English. It does **not** carry acceptance-criteria text,
internal mechanism prose (SP names, return codes, flag mutations), or
implementation prescription. Those concerns live in sibling artifacts:

| Concern | Sibling artifact |
|---|---|
| Acceptance criteria | `acceptance-criteria.md` |
| Component / surface map (reuse decisions) | `component-spec.md` |
| Sample data | `sample-data/*.json` |
| Demos | `demos/demo-interactive.html` / `demos/calculation-demo.html` |
| Bidirectional trace | `traceability.md` |
| Reuse map (full table) | `reuse-map-draft.md` |
| Component pattern decisions | `component-pattern-confirmation.md` |
| Bundle file inventory | `bundle-manifest.json` |

The PRD references these siblings by path and ID — it never restates
their content.

**Schema authority.** Section numbers, sub-section headings, and §4 ID
prefixes in this template come from
[`prd-section-schema.md`](./prd-section-schema.md). Section numbers and
ID prefixes are **stable** — once published, they do not change.

---

## PRD file path

`.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md`

---

## Plain-English rule (binding)

Every paragraph in the PRD reads like a business analyst wrote it for a
business reader. Translate every technical mechanism into the observable
outcome it produces. Forbidden in PRD body text:

| Forbidden | Reason | Use instead |
|---|---|---|
| Stored procedure names (e.g. `usp_SaveProductCosts`) | Internal mechanism | The user-visible behaviour the SP causes |
| Return code values, error codes | Internal mechanism | The user-visible toast / dialog / banner the code produces |
| Internal flag names (e.g. `isAODDependent`) | Internal mechanism | The condition under which the user observes the resulting behaviour |
| View / column names (e.g. `vw_HierarchyHistory`) | Internal mechanism | The data the user sees and how they see it |
| Class names, selector names | Internal mechanism | The component pattern named in `component-spec.md` |
| AC text inline (Given / When / Then) | Belongs in sibling | A reference to AC IDs in `acceptance-criteria.md` |
| Reuse table inline (component → existing pattern) | Belongs in sibling | A reference to the table in `component-spec.md` |
| API endpoint paths | Internal mechanism | The user-observable behaviour the endpoint enables |

PM-directed SQL is admissible verbatim only when explicitly requested by
the PM (carry-over from L2).

---

## Template

The PRD file begins with a YAML frontmatter block (see "Frontmatter for
`prd.md`" in [`prd-section-schema.md`](./prd-section-schema.md)). The
frontmatter is terminated by a `---` delimiter. The body content begins
immediately after.

````markdown
---
title: [Feature Title]
subPrdId: [sub-prd-N]
featureId: [PROF-NNN]
version: 1.0.0
author: [PM full name]
date: [DD-MMM-YYYY]
prdHash: [sha256-hex of body content below the closing --- delimiter]
---

# [Feature Title] — Business Requirements

**Status:** Draft
**Repository:** Profitability
**Applies To:** [Both FP and OP / FP only / OP only]

---

## §1 Feature Definition

### §1.1 Purpose

[One paragraph of business English describing what this sub-PRD delivers.
Who uses it, what problem it solves, what the user can do after this
feature exists that they cannot do today.]

### §1.2 Business outcome

[The user-observable or customer-visible outcome the feature produces.
Outcome-only — no implementation steps.]

### §1.3 Dependencies

#### §1.3.1 Prerequisite
[Work items / data / configuration that must exist before this sub-PRD can
ship. If none: `None.`]

#### §1.3.2 Blocks-Downstream
[What this sub-PRD's completion unblocks. If none: `None.`]

#### §1.3.3 Concurrent
[Sub-PRDs / work items that ship in the same cycle and share surfaces. If
none: `None.`]

#### §1.3.4 Reference
[External documents, ADRs, prior PRDs the reader may need. If none:
`None.`]

#### §1.3.5 Cross-Sub-PRD
[Relationships with other sub-PRDs in the same feature. Each entry
references the related sub-PRD by ID and the canonical behaviour entry it
points at (e.g. `sub-prd-2 §4.2 CL-007`). If none: `None.`]

### §1.4 User Roles

[Role list only — no permissions matrix. Permissions live under §4.9.
Example:
- Profitability Admin
- Rule Creator
- Read-only Reviewer]

### §1.5 User Stories

[Each story carries `id`, `role`, `goal`, `motivation`, `linked_ac_ids`.

Example:
- **US-001**
  - **role:** Profitability Admin
  - **goal:** Update leaf-level Unit Costs without leaving the page
  - **motivation:** Reduce edit friction during quarterly review
  - **linked_ac_ids:** AC-007, AC-008, AC-012]

---

## §2 Success Criteria

### §2.1 Definition of success

[Free-form prose describing what "successful delivery" looks like for
this sub-PRD.]

### §2.2 KPIs

[KPIs are optional. If the PM does not specify any, write
`Not applicable — [reason]`.]

---

## §3 Scope

### §3.1 In Scope

[Explicit bulleted list. Each bullet is specific enough that a developer
could not accidentally include something out-of-scope.]

### §3.2 Out of Scope

[Explicit bulleted list of adjacent areas that are intentionally excluded,
each with a one-line reason. If the PM provided none, write
`Not applicable — [reason]`.]

### §3.3 Scope Boundaries

[Edges and grey areas where in/out is non-obvious. Each entry names the
boundary and the rule that decides. If none: `Not applicable — [reason]`.]

---

## §4 Detailed Business Requirements

Every §4 sub-section below appears in the document. Sub-sections in the
P2 coverage map carry one or more `{PREFIX}-NNN` entries; unused sub-
sections carry an explicit `Not applicable — [reason]` notice. **No
silent omissions.**

### §4.1 Data Model & Entities (`DM-NNN`)

[Per-entity entries. Each entry carries an outcome-only description of
the entity from the user's perspective: what it represents, what
relationships it has to other entities, what state it can be in. No SP
names, no view columns, no class names.

Example:
- **DM-001 — Product Unit Cost**
  - The dollar cost the business has assigned to a single leaf product at
    a specific As-Of Date. Relates one-to-one to a leaf node in the
    Product hierarchy.]

### §4.2 Calculation & Logic (`CL-NNN`)

[Per-calculation entries. Each entry carries inputs (named in business
language), transformation (PM-stated formula), outputs, and at least one
boundary case. Verbatim numeric worked example required where PM supplied
numbers; otherwise `[NUMBERS TBD — DI-NNN]`.

If not applicable: `Not applicable — [reason]`.]

### §4.3 Allocation & Distribution (`AL-NNN`)

[Per-allocation-rule entries. Each entry names driver / scope / source-
pool / target-pool / exclusions / fractional-remainder / ordering.

If not applicable: `Not applicable — [reason]`.]

### §4.4 Workflow & State (`WF-NNN`)

[Per-state-transition entries. Each entry names the precondition, the
trigger, the resulting state, and the user-observable signal.

If not applicable: `Not applicable — [reason]`.]

### §4.5 UI & Interaction (`UI-NNN`)

[Per-surface entries. Each entry names the affordance, the visible
states, and the user-observable interactions. Detailed component-by-
component states / interactions / data bindings live in
`component-spec.md`; §4.5 names what the user is asked to do.

If not applicable: `Not applicable — [reason]`.]

### §4.6 Validation & Constraints (`VC-NNN`)

[Per-validation-rule entries. Each entry names the input predicate, the
violation outcome, and the recovery path.

If not applicable: `Not applicable — [reason]`.]

### §4.7 Error Handling (`ER-NNN`)

[Per-failure-mode entries. Each entry names the trigger, the user-
observable signal (toast, banner, dialog), and the recovery path.

If not applicable: `Not applicable — [reason]`.]

### §4.8 Notifications & Messaging (`NM-NNN`)

[Per-notification entries. Each entry names the trigger, the channel
(toast / email / in-app banner / alert), the recipient role, and the
verbatim copy if PM-provided.

If not applicable: `Not applicable — [reason]`.]

### §4.9 Permissions & Access Control (`PA-NNN`)

[Per-permission entries. Each entry names the role, the affordance the
role can or cannot access, and the user-observable signal when access is
denied.

If not applicable: `Not applicable — [reason]`.]

### §4.10 Integration & External Surfaces (`IN-NNN`)

[Per-integration entries. Each entry names the external system, the
direction (this sub-PRD reads / writes / both), and the user-observable
behaviour.

If not applicable: `Not applicable — [reason]`.]

### §4.11 Performance & Scale (`PF-NNN`)

[Per-performance-budget entries. Each entry names the metric (load time,
render time, max-rows, throughput) and the budget threshold.

If not applicable: `Not applicable — [reason]`.]

### §4.12 Audit & Telemetry (`AU-NNN`)

[Per-audit-entry entries. Each entry names what is recorded, the trigger,
and the consumer.

If not applicable: `Not applicable — [reason]`.]

### §4.13 Reporting & Export (`RX-NNN`)

[Per-report-or-export entries. Each entry names the report, the trigger,
the format, and the recipient.

If not applicable: `Not applicable — [reason]`.]

### §4.14 Cross-Page Impacts (`CP-NNN`) — relationship pointer register

#### Outbound impacts

[Per-outbound-impact entry. Each entry references a canonical behaviour
entry in the originating sub-PRD by sub-PRD ID + requirement ID. Never
duplicates behaviour text.

Example:
- **CP-001 → sub-prd-3 §4.5 UI-014** — this sub-PRD updates the Product
  Unit Cost data shape; sub-prd-3 §4.5 UI-014 consumes it on the
  Allocation Rules page.

If none: `None.`]

#### Inbound impacts

[Per-inbound-impact entry. Same format.

If none: `None.`]

---

## §5 Data Migration

[Default: `Not applicable — [reason]`.

When triggered (the feature touches existing data, records, or
calculation results), address explicitly:
- **Existing data:** What happens to records created before this feature
  is deployed?
- **Calculation results:** If any calculations or allocations are already
  stored, do they remain valid after this change, or do they need to be
  recalculated?
- **Migration step:** Is there a one-time data migration step required as
  part of deployment?
- **Historical records:** Are any historical records affected by how the
  new feature categorises or displays data?]

---

## §6 Risks & Mitigations

[Free-form prose. PM authors risks and mitigations.

Example:
- **Risk:** Concurrent edits from two Admins could overwrite each other's
  Unit Cost changes.
- **Mitigation:** Concurrency dialog surfaces the conflict and offers
  three resolutions (Cancel / Load Latest / Save Anyway). See AC-014.]

---

## §7 Open Items & Ambiguities

[Free-form. Captures Deferred Items (DI-NNN) that remained `Accepted` at
the single conclusion gate plus any ambiguity-scan deferrals.

Example:
- **DI-007:** PM to confirm refresh cadence for the daily-rate input.
  Tracked-as-DI from the ambiguity scan ("as needed").
- **DI-012:** Concurrency dialog copy `[TEXT TBD — requires PM decision]`.

If none: `None — no open items.`]

---

## §8 Related Artefacts

Each pointer carries a freshness status (`FRESH` / `STALE` / `MISSING`)
derived from `prd-stale-check`. A FRESH status means the derivative's
`prdHash` header matches the current SHA-256 of `prd.md` body content.

| Artefact | Path | Freshness |
|---|---|---|
| Acceptance criteria | `./acceptance-criteria.md` | [status] |
| Component spec | `./component-spec.md` | [status] |
| Reuse map (full) | `./reuse-map-draft.md` | [status] |
| Component pattern decisions | `./component-pattern-confirmation.md` | [status] |
| Traceability | `./traceability.md` | [status] |
| Interactive demo | `./demos/demo-interactive.html` | [status] |
| Calculation demo | `./demos/calculation-demo.html` | [status or `Not produced`] |
| Demo behaviour manifest | `./demos/demo-behavior-manifest.md` | [status] |
| Demo coverage report | `./demos/demo-coverage.md` | [status] |
| Demo handoff summary | `./demos/_summary.md` | [status] |
| Sample data | `./sample-data/` | [status] |
| Sample-data summary | `./sample-data/_summary.md` | [status] |
| Component-spec handoff summary | `./component-spec/_summary.md` | [status] |
| Verbatim PM answers | `./interview-answers.json` | [status] |
| Bundle manifest | `./bundle-manifest.json` | [status] |
| PRD breakdown | `../prd-breakdown.[sub-prd-id].md` | [status or `N/A`] |

---

## Version History

Every entry carries `Date | Author (full name) | Change summary (concrete
delta — not "updated file")`. PM edits and agent edits MUST be
distinguishable from the author field alone. No anonymous entries, no
"various" authorship, no placeholder authors.

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DD-MMM-YYYY] | [PM full name] | Initial PRD authored from interview |
| 1.1 | [DD-MMM-YYYY] | [agent name, e.g. `prd-amend`] | [concrete delta — e.g. "Regenerated demo brief after PM edit to §4.5 UI-007 copy strings"] |

````

---

## Generation order

1. **P8 PRD drafting** writes the body of `prd.md` against the §1–§8
   structure above, populating §4 sub-sections from the in-flow
   `{PREFIX}-NNN` IDs assigned during P3 / P4 / P5 / P6.
2. **Pre-write artifact-bar walk** (Family G G3) runs against
   `production-grade-quality-bar.md` Pass Conditions for the PRD bar.
   Failure: do not write. Surface failing Pass Condition. Resolve gap.
   Retry.
3. **prdHash computation** runs once the body content is finalised. The
   computed hash is written into the YAML frontmatter `prdHash` field.
   On computation failure (Family L11 D5), the field carries
   `'[COMPUTATION_FAILED]'`.
4. **Sibling derivatives** (`acceptance-criteria.md`, `reuse-map-draft.md`,
   `component-pattern-confirmation.md`) are written next, each carrying
   the unnumbered preamble's derivative frontmatter with the computed
   `prdHash` value.
5. **P9 handoff briefs** are authored next; the heavy handoff-chat outputs
   (`demos/*.html`, `sample-data/*.json`, `component-spec.md`) are
   produced by the three manual handoff chats and return through the
   interviewer's Family N anchor verification.
6. **`traceability.md`** is auto-built at P9 from the in-memory AC list
   plus the three handoff `_summary.md` files — table-only, deterministic.
7. **`bundle-manifest.json`** is finalised at end of P9 and emits
   `prd_bundle_manifest_finalised` immediately before
   `prd_interview_completed`.

The PRD is the outcome-only deliverable. The sibling artifacts are the
implementation-facing deliverables. Together they form the post-lift
bundle for one sub-PRD.
