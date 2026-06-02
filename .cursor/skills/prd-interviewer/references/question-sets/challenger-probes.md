# Challenger Probes Catalogue

Reference for prd-interviewer. Self-contained — no external skill references.

Use these patterns whenever a PM answer feels like a stated preference rather
than a reasoned decision. Pick the most relevant. Apply across any section.

Four probe families: Why-not · Cross-impact · Micro-detail · Rationale ·
Boundary-stretch.

---

## Why-not probes

- "Why this behavior and not [opposite / plausible alternative]? Which
  specific reason rules out the alternative?"
- "Which condition would have to be true for the opposite choice to be
  correct? Name it."
- "If a developer interpreted this as [alternative reading], would that be
  wrong? Yes / No — and if Yes, which specific contradiction makes it wrong?"
- "Was a different approach considered? Yes / No — and if Yes, which
  approach, and which specific reason caused it to be rejected?"
- "Is this behavior matching an existing pattern in the application, or is
  it new? Existing / New — and if New, which specific reason justifies the
  divergence?"

---

## Cross-impact probes

- "When the user does X here, what does someone on [other screen] see the
  next time they open it — unchanged, refreshed, or stale? Which applies?"
- "Which other features depend on the data this changes? List them — and
  for each, what happens to it: unaffected, auto-updates, or breaks?"
- "If [downstream report / dashboard / export] is open during this action,
  which of (a) live-updates, (b) shows a stale-warning, or (c) requires
  manual refresh applies?"
- "On save, where does the user end up — same page in read mode, list page,
  or elsewhere? Which page, and in which state?"
- "Which other screens in the application show this same data? List them —
  and do they all reflect this change? Yes / No, and at which point: live,
  on next open, or after a refresh?"

---

## Micro-detail probes

- "Does the tooltip on [field/button] render the verbatim text [from cited
  YAML]? Yes / different — state the verbatim text."
- "When the field is empty, does the placeholder render the verbatim text
  [from cited YAML]? Yes / different — state the verbatim text."
- "When there are zero items, does the empty-state render the verbatim
  message [from cited YAML]? Yes / different — state the verbatim text."
- "On hover, on focus, and on disabled-hover, does each state render the
  verbatim text [from cited YAML]? Yes / different — state the verbatim
  text per state."
- "Is there a keyboard equivalent for this click? Yes / No — and if Yes,
  name the key combination."
- "Does the button label render the verbatim text [from cited YAML]? Yes /
  different. Does it change state during action (e.g., 'Save' → 'Saving...'
  → 'Saved')? Yes / No — and if Yes, state each label."
- "What is the default sort order? Can the user change it? Yes / No. Is
  the preference persisted? Yes / No."

---

## Rationale probes

- "Who asked for this behavior, and on which date was the decision made?
  Name the requester and the date."
- "Which specific problem does this choice solve that an alternative would
  not? Name the problem."
- "Is there a regulatory, audit, or compliance reason for this behavior?
  Yes / No — and if Yes, name the regulation or policy."
- "If we shipped the opposite behavior, which specific failure would
  occur? Name it."

---

## Boundary-stretch probes

- "If the user does this 100 times in a row, does anything degrade or
  become confusing? Yes / No — and if Yes, which specific degradation?"
- "At the maximum data scale we ever expect, does this behavior still
  hold? Yes / No — and if No, what is the breakpoint and the failure
  mode?"
- "If the user does the opposite of what we expect — wrong order, wrong
  data, skips a step — which of (a) blocked, (b) error message, (c) silent
  acceptance, or (d) corruption applies?"
- "What is the most adversarial action a motivated user could take here?
  Name the action — and what does the user see?"
- "If the feature is partially rolled out — some users have it, some don't
  — does anything break for users who don't have it? Yes / No — and if
  Yes, which specific surface breaks?"
