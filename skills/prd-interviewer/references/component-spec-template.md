# Component Specification Template

Reference for prd-interviewer. Self-contained — no external skill references.

Use this template to produce the `component-spec.md` artifact for one
sub-PRD. The file is saved to
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md` and is the
authoritative developer-facing **surface map** for the sub-PRD. It is
referenced from the PRD; it does not duplicate PRD prose.

This file is produced by the component-spec handoff chat (manual-handoff
Surface 3 — see `sub-agent-delegation.md` and `handoff-prompt-templates.md`
Template 3), not by the interviewer chat. Entries describe outcomes —
states, data bindings, interactions, visible affordances — and never
implementation (no SP names, flag names, class names, API endpoints).

ACs live in the sibling artifact at
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md`; the spec
references AC IDs (e.g. "implements AC-007, AC-014") but does **not**
restate AC Given/When/Then text.

Requirements live in `prd.md` §4 as `{PREFIX}-NNN` entries; the spec
references those IDs (e.g. "covers UI-005, VC-001") and does **not**
restate the requirement text.

A requirement that appears only in the component spec is a defect —
every requirement must also be in the PRD. See
`production-grade-quality-bar.md` §3 for the bar this template satisfies.

---

## Entry ordering

One entry per component from the P5 surface inventory. Order by page,
then by component type (new components first, then affected, then
reused).

Mark unresolved parked items with `⚠️ GAP: [description]`.

---

## Template

The component-spec file begins with a YAML derivative frontmatter block
(see [`prd-section-schema.md`](./prd-section-schema.md) — "Frontmatter
for every other derivative"). The frontmatter is terminated by a `---`
delimiter.

````markdown
---
derivativeOf: prd.md
prdHash: [sha256-hex of prd.md body content at the moment this file was written]
writtenAt: [ISO 8601 UTC]
producer: handoff:component-spec
---

# Component Specifications — [Feature Title] — [sub-prd-id]

**Parent PRD:** [link to `prd.md`]
**Acceptance criteria:** [link to `acceptance-criteria.md`]
**Date:** [DD-MMM-YYYY]

---

## Page: [Page name]

---

### [Component name] — [Component type] — [NEW / AFFECTED / REUSED]

**Covers PRD requirements:** [comma-separated §4.NNN IDs, e.g. `UI-005, WF-003, PA-002`]
**Implements ACs:** [comma-separated AC IDs, e.g. `AC-002, AC-005`]

[If REUSED with no differences:]
Same as [component name] on [page name]. No differences.
[Link to that component's spec if it exists.]

[If REUSED with differences, or NEW or AFFECTED, complete all six elements:]

#### 1. Name and type

**Name:** [must match PRD §4 requirement language exactly]
**Type:** [dropdown / multi-select / table / form field / button / modal /
          toggle / date picker / tab set / tooltip / filter panel /
          progress indicator / other: specify]
**Cited YAML(s):** [comma-separated paths under `.context/components/` per
                    Family M application-fidelity. If no application
                    equivalent, write `No application equivalent — see
                    Family M flag in brief Section 10.`]

#### 2. Functional description

[What the component does, as a predicate. Not a visual description.
One to three sentences. Must answer: what does interacting with this
component cause to happen?

Cross-reference the §4.NNN requirement(s) this functional description
implements — do not restate the requirement text.

Does it affect any other component on the page? If yes: which component
and what changes?]

#### 3. States and transition triggers

| State | Trigger condition | Notes |
|---|---|---|
| [state name] | [what causes entry into this state] | [any notes] |
| ... | ... | ... |

[Minimum states required by component type — see `prd-completeness-check`
scoring rubric. Any intentionally omitted states must include a reason.]

**Intentionally omitted states (if any):**
- [state]: [reason]

#### 4. User interaction options

| Action | Trigger element | Outcome | §4 ID |
|---|---|---|---|
| [click / type / select / hover / drag] | [element] | [what happens] | [§4.NNN that defines the action] |
| ... | ... | ... | ... |

**Role-conditional interactions (if any):**
[Which interactions are only available to certain roles, and which
roles. Cross-reference `PA-NNN` entries from §4.9.]

**Keyboard interactions (if any):**
[Tab focus, enter, escape, arrow keys — what each does.]

#### 5. Selectable options

[Complete this section only if the component presents choices to the
user. If not applicable, write: "Not applicable — this component does
not present selectable options."]

**Source:** [Static (hardcoded) / Dynamic (loaded from [named data
source described in PM-facing language; no SP / endpoint names])]

**Options:**

| Display label | Underlying value | Condition (if conditional) |
|---|---|---|
| [label] | [value] | [always / only when [condition]] |
| ... | ... | ... |

**Default selection:** [label / value, or "none"]
**Maximum selections:** [N, or "unlimited" for multi-select]
**Empty state (no options available):** [what the component shows —
verbatim copy strings sourced from the cited YAML or marked
`[TEXT TBD — requires PM decision]`]

#### 6. Data binding

**Reads from:**

| Source (business name) | Filtered by | Notes |
|---|---|---|
| [business-language data source name] | [filter condition if any] | |
| ... | ... | ... |

**Writes to:**

| Target (business name) | Triggered by | Notes |
|---|---|---|
| [business-language target name] | [user action or event] | |
| ... | ... | ... |

[If read-only, write: "Read-only — no write operation."]

**Dependencies on other components:**
[If this component's data or state depends on another component's
state: which component, what state change, and what this component
does in response.]

**Cross-page impact:**
[If this component's behaviour creates a cross-page impact, reference
the matching `CP-NNN` entry in PRD §4.14. If none, write `None.`]

---

[Repeat the component entry block for every component on this page]

---

## Page: [Next page name]

[Repeat as above]

---

## Components with open gaps

[List of all components with at least one ⚠️ GAP marker, for easy
scanning. These must be resolved before `prd-completeness-check` can
pass the Component-spec dimension.]

| Component | Page | Gap description |
|---|---|---|
| [name] | [page] | [what is missing] |
| ... | ... | ... |

[If no gaps: "None — all components fully specified."]
````

---

## Six-element structure (binding)

Every NEW, AFFECTED, or REUSED-with-differences entry MUST populate all
six elements:

1. **Name and type** — with cited YAML(s) per Family M.
2. **Functional description** — predicate form; cross-references §4
   requirements; does not restate them.
3. **States and transition triggers** — table; intentional omissions
   listed with reasons.
4. **User interaction options** — table; each row carries the §4 ID
   that defines the action; role-conditional / keyboard interactions
   listed.
5. **Selectable options** — table if applicable; `Not applicable —
   [reason]` if the component presents no choices.
6. **Data binding** — reads / writes in business-language names;
   dependencies on other components; cross-page impact reference.

A REUSED-with-no-differences entry may collapse to a single line
referencing the canonical component's spec; otherwise all six elements
appear.

---

## Anti-patterns

- **AC duplication.** Restating Given/When/Then text from
  `acceptance-criteria.md`. Hard fail — the spec references AC IDs, not
  AC text.
- **Requirement duplication.** Restating §4 requirement prose from
  `prd.md`. Hard fail — the spec references §4 IDs, not §4 text.
- **Internal mechanism leakage.** Naming SPs, view columns, class
  names, API endpoints, internal flags. Hard fail — translate to the
  observable outcome.
- **Silent omission of a state.** Omitting a state without a stated
  reason. Hard fail — every intentional omission carries an explicit
  rationale.
- **Missing YAML citation for an application-equivalent surface.**
  Hard fail per Family M — every NEW / AFFECTED entry that has an
  application equivalent cites the YAML(s); a no-equivalent entry
  carries the explicit Family M flag.

---

## Notes for the handoff chat

- The component-spec handoff chat reads
  `skills/prd-interviewer/references/sub-agent-delegation.md`
  and the component-spec brief at
  `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec/_brief.md`.
- Family N read discipline applies: every file named in brief Section 3
  is read end-to-end; every `expected_anchor` is extracted verbatim;
  the `_summary.md` `## YAML reads` H2 table is populated.
- Pre-write artifact-bar walk (Family G G3) runs against
  `production-grade-quality-bar.md` §3 (Component-spec bar) before the
  file is written. Failure: do not write. Surface failing Pass
  Condition. Resolve gap. Retry.
- The handoff chat returns `component-spec/_summary.md` with the
  required H2 sections (including `## YAML reads`) and STOPS. The
  interviewer reads only `_summary.md` on return and runs Family N
  anchor verification.
