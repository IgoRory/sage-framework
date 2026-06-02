# Section 7 — Edge-case phase

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P7
**Always asked regardless of feature type.**

Seven categories — all asked. Depth determined by complexity tier. Ask
questions grounded in the breakdown's `investigation_context`, translated
into business language. Reference business processes, user workflows, and
data entities — never SP names, return codes, or internal technical
constructs.

These are starting points — generate additional questions grounded in the
breakdown's `investigation_context` for the specific feature. Ask in batches
of 3–5, grouped by category.

Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns.

---

## EC Category 1 — Interaction sequence

- If the user performs action A and then action B before A completes, which
  of (a) B is blocked, (b) B queues, (c) A is cancelled, or (d) both run in
  parallel applies? *(Use specific actions from the interview.)*
- If the user starts an operation and navigates away before it completes, is
  their work preserved? Yes / No — and if Yes, on return does the surface
  resume in the in-progress state or restart?
- On browser refresh during an operation, does the operation continue,
  abort, or resume? Which of continue / abort / resume applies?
- If the user applies a filter and then triggers an operation, does the
  filter persist or reset? Persist / Reset.

> **Depth indicator (D-EC):** At least one interaction sequence scenario has
> a defined expected outcome.
>
> **Challenger probe:** "Why this outcome and not [block / queue / merge]?"

---

## EC Category 2 — Cascading behaviour

- If [entity] is renamed or modified, which other surfaces in the
  application display it? List each surface — and for each, do those
  occurrences auto-update? Yes / No.
- If [entity] is deleted, what happens to other entities that reference it
  — which of (a) deleted, (b) orphaned, or (c) blocked applies?
- If a configuration value is changed, does any existing data become
  invalid? Yes / No — and if Yes, which of (a) auto-migrate, (b) flag, or
  (c) block applies?

> **Depth indicator (D-EC):** At least one cascading scenario has a defined
> outcome (auto-update, block, orphan).
>
> **Challenger probe:** "Why auto-update rather than require manual refresh?"

---

## EC Category 3 — Concurrency

- If two users both modify the same record at the same time, which of (a)
  last-write-wins, (b) optimistic-lock conflict dialog, or (c) one user is
  blocked applies? Which user wins?
- If one user deletes an entity while another user is editing it, which of
  (a) editor sees a conflict dialog, (b) edit is silently discarded, or (c)
  delete is blocked applies?
- If a background calculation or allocation process is running while a user
  modifies data the process is reading, which of (a) user is blocked, (b)
  process is blocked, or (c) both proceed independently applies?
- Are changes made by other users visible in real time, or only after a
  page refresh? Real-time / On-refresh.

> **Depth indicator (D-EC):** At least one concurrency scenario has a defined
> outcome (last-write-wins, optimistic lock, block).

---

## EC Category 4 — State boundary

- When there are zero items, for each action button and display component,
  which of (a) disabled, (b) hidden, or (c) showing a message applies? Name
  the outcome per control.
- Is there a maximum number of [items/entities]? Yes / No — and if Yes,
  what is the limit and which of (a) hard error, (b) warning, or (c) silent
  truncation applies at the limit?
- During state transitions — while data is saving or a calculation is
  starting — which of (a) the surface is locked, (b) controls are disabled,
  or (c) interaction continues applies?
- Can [entity A] be in [state X] while [related entity B] is in [state Y]?
  Valid / Invalid combination.

> **Depth indicator (D-EC):** At least one state-boundary scenario has a
> defined outcome (disabled button text, limit error, invalid combination).

---

## EC Category 5 — Cross-component dependency

- When this feature's data changes, what does [dependent component] show —
  unchanged, refreshed, stale-with-warning, or empty? Which applies?
- When upstream data is incomplete or missing, what does this feature show
  — empty state, error state, partial data, or block? Which applies?
- Are there any circular dependencies between components that could cause
  update loops? Yes / No — and if Yes, name each loop.

> **Depth indicator (D-EC):** At least one cross-component dependency scenario
> has a defined outcome.

---

## EC Category 6 — Data integrity

- For records created before this feature exists, do they need migration or
  do they show a default state? Migrate / Default-state — and if Migrate,
  state the migration rule.
- Is partial data entry allowed? Yes / No — and if Yes, can the user save
  incomplete data? Yes / No.
- For bulk operations where some items succeed and others fail, does the
  user see a partial result? Yes / No — and if Yes, which of (a) per-item
  status list, (b) summary count, or (c) both applies?
- Can every action be undone? Yes / No — and if Yes, does undo restore the
  immediately previous state or the original state? Previous / Original.

> **Depth indicator (D-EC):** At least one data integrity scenario has a
> defined outcome (migration behavior, partial-save result, bulk-failure
> handling).

---

## EC Category 7 — Failure and recovery

- If the user triggers an operation and it fails, what do they see — error
  toast, inline message, or modal? Is their input preserved? Yes / No. Can
  they retry? Yes / No.
- If validation fails on some fields, which fields are highlighted — only
  the failed fields, all fields, or the row? Is valid data preserved? Yes
  / No.
- If a bulk action partially fails, can the user address only the failed
  items without re-processing successful ones? Yes / No.
- If a background process fails, how is the user informed — toast,
  notification centre, email, or none? Which applies, and what is the
  recovery path?

> **Depth indicator (D-EC):** At least one failure scenario has a defined
> outcome: what the user sees, whether input is preserved, and the recovery
> path.
