# Component Specification Template

Use this template to produce the Component Specification file after
the interview. This file is saved to `.sage/prds/[FEATURE_ID]/component-spec.md`
and linked explicitly from the PRD.

One entry per component from the P4 inventory. Order by page, then by
component type (new components first, then affected, then reused).

Mark unresolved parked items with `⚠️ GAP: [description]`.

---

```
# Component Specifications

**Parent PRD:** [link to PRD page]
**Feature:** [feature title]
**Date:** [ISO date]

---

## Page: [Page name]

---

### [Component name] — [Component type] — [NEW / AFFECTED / REUSED]

[If REUSED with no differences:]
Same as [component name] on [page name]. No differences.
[Link to that component's spec if it exists.]

[If REUSED with differences, or NEW or AFFECTED, complete all six elements:]

#### 1. Name and type
**Name:** [must match PRD requirement language exactly]
**Type:** [dropdown / multi-select / table / form field / button / modal /
          toggle / date picker / tab set / tooltip / filter panel /
          progress indicator / other: specify]

#### 2. Functional description
[What the component does, as a predicate. Not a visual description.
One to three sentences. Must answer: what does interacting with this
component cause to happen?]

[Does it affect any other component on the page? If yes: which component
and what changes?]

#### 3. States and transition triggers

| State | Trigger condition | Notes |
|---|---|---|
| [state name] | [what causes entry into this state] | [any notes] |
...

[Minimum states required by component type — see prd-completeness-check
scoring rubric D5. Any intentionally omitted states must include a reason.]

**Intentionally omitted states (if any):**
- [state]: [reason]

#### 4. User interaction options

| Action | Trigger element | Outcome |
|---|---|---|
| [click / type / select / hover / drag] | [element] | [what happens] |
...

**Role-conditional interactions (if any):**
[Which interactions are only available to certain roles, and which roles]

**Keyboard interactions (if any):**
[Tab focus, enter, escape, arrow keys — what each does]

#### 5. Selectable options
[Complete this section only if the component presents choices to the user.
If not applicable, write: "Not applicable — this component does not
present selectable options."]

**Source:** [Static (hardcoded) / Dynamic (loaded from [SP / endpoint])]

**Options:**
| Display label | Underlying value | Condition (if conditional) |
|---|---|---|
| [label] | [value] | [always / only when [condition]] |
...

**Default selection:** [label / value, or "none"]
**Maximum selections:** [N, or "unlimited" for multi-select]
**Empty state (no options available):** [what the component shows]

#### 6. Data binding

**Reads from:**
| Source | Field / SP / view | Filtered by | Notes |
|---|---|---|---|
| [Adjusted_GL / GLAllocationLog / SP / view / other component state] | [name] | [filter condition if any] | |
...

**Writes to:**
| Target | Field / SP | Triggered by | Notes |
|---|---|---|---|
| [table / SP / other] | [name] | [user action or event] | |
...

[If read-only, write: "Read-only — no write operation."]

**Dependencies on other components:**
[If this component's data or state depends on another component's state:
which component, what state change, and what this component does in response.]

**ProcessID / GL code involvement:**
[Name any ProcessID category, GL code range, or field from the ProcessID
reference framework that affects how this component's data is filtered,
grouped, or stored. If none: "None."]

---

[Repeat the component entry block for every component on this page]

---

## Page: [Next page name]

[Repeat as above]

---

## Components with open gaps

[List of all components with at least one ⚠️ GAP marker, for easy scanning.
These must be resolved before prd-completeness-check D5 can pass.]

| Component | Page | Gap description |
|---|---|---|
| [name] | [page] | [what is missing] |
...

[If no gaps: "None — all components fully specified."]
```
