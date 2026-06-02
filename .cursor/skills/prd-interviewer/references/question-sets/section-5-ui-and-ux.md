# Section 5 — UI and UX

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P5
**Conditional — ask if feature type includes UI change, or if recon found UI
components in scope.**

Five categories plus a mandatory Cross-page impact check: Screen Inventory ·
Component Inventory · State Models · Micro-Detail (D-DETAIL) ·
Interaction Model · Cross-page impact check (D-CROSS).

Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns. Apply Component Pattern Blocks
from `component-matching.md` (in the parent references folder) before asking
component questions — ask only delta questions for matched components.

---

## Category: Screen Inventory

**Example questions:**

- Which screens or pages does this feature add or change? List each one.
- For each screen, is it a new screen or a modification to an existing one?
  New / Modified per screen.
- For each screen, what is its purpose? State the purpose in one sentence
  per screen.
- For each screen, which of these triggers navigation to it: (a) a menu
  item, (b) a button on another screen, (c) a URL, or (d) other? Name the
  specific trigger.
- For each screen, which screen does the user come from before arriving,
  and which screen do they go to after completing an action? Name both.

> **Depth indicator:** Every screen classified (new vs. modified) with a
> stated purpose and defined navigation trigger. Full navigation flow traced.

---

## Category: Component Inventory

*Apply Component Pattern Blocks from component-matching.md before asking
component questions. Ask only delta questions for matched components.*

**Example questions (for unmatched / new components):**

- For each unmatched component, what is its name and type?
  *(e.g., "a multi-select dropdown", "a data grid with row-level expand")*
- For each component, which specific functional behavior applies — when the
  user does X, does the component do Y? State the trigger and the response.
- For each component, which specific field or business entity does it
  display or capture? Name the field or entity.

> **Depth indicator:** Each component has all 6 spec elements captured:
> name/type, functional description, data binding, all states,
> empty/loading/error behavior, and interactions.

---

## Category: State Models

*For matched components, present known states and ask only for differences.*

**Example questions (for unmatched / new components or unknown states):**

- For each component, which of these states applies: default, loading,
  selected, error, disabled, empty? List every state the component can be
  in.
- For each state pair, which specific event causes the transition between
  them? Name the trigger per transition.
- For the empty state, which specific message or visual is shown when there
  is no data? State the verbatim copy.
- For each component that can fail, which specific error-state visual and
  copy applies? State the verbatim copy.
- For each component that fetches data, which specific loading-state visual
  applies? Name it.

> **Depth indicator:** Every component has all state transitions defined with
> explicit triggers and specific copy/behavior for each state.

---

## Category: Micro-Detail (D-DETAIL — mandatory for every UI surface)

**These questions must be asked for every UI surface, even matched components
where the YAML does not provide the specific text:**

- For [field/button], does the tooltip render the verbatim text [from cited
  YAML]? Yes / different — state the verbatim text.
- When the field is empty, does the placeholder render the verbatim text
  [from cited YAML]? Yes / different — state the verbatim text.
- For the empty-state message, does the surface render the verbatim text
  [from cited YAML]? Yes / different — and is the empty case "no data at
  all" or "filtered-empty where data exists but the filter hides it"? Which
  applies, and what verbatim copy applies to each?
- For the disabled-state tooltip, does hovering a disabled control render
  the verbatim text [from cited YAML]? Yes / different — state the verbatim
  text.
- Does the button label render the verbatim text [from cited YAML]? Yes /
  different. Does the label change state during action (e.g., "Save" →
  "Saving..." → "Saved")? Yes / No — and if Yes, state each label.
- What is the default sort order? Can the user change it? Yes / No. Is the
  preference persisted across sessions? Yes / No.
- Is there a keyboard equivalent for this interaction? Yes / No — and if
  Yes, name the key combination.

---

## Category: Interaction Model

**Example questions:**

- Are there any user interactions beyond the standard click and type? Yes /
  No — and if Yes, which of: drag-and-drop, inline editing, bulk selection,
  keyboard shortcuts, or other? Name each non-standard interaction.
- Do you have any existing sketches, mockups, or visual references? Yes /
  No — and if Yes, describe each one in words. *(intake question — open-ended
  by design; predicate phrasing does not apply. Do not share files or links —
  describe verbally.)*

> **Depth indicator:** Every non-standard interaction named and described.
> Visual reference description contains enough detail for a developer to
> reproduce.

---

## Cross-page impact check (D-CROSS — mandatory before exiting Section 5)

Before concluding Section 5, for every entity this feature displays or
modifies, explicitly trace where else in the application that entity appears:

- Which other screens show this data? List each screen.
- Which dashboards or reports roll it up? List each dashboard or report.
- Which exports include it? List each export.
- Which downstream calculations consume it? List each calculation.
- For each traced occurrence, what happens when this feature's data changes
  — unaffected, auto-updates, requires manual refresh, or breaks? Which
  outcome applies?

Record each traced relationship.
