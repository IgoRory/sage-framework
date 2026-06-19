# Section 1 — Feature and capability definition

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P1
**Always asked.**

Three categories: Feature Identity · Change Classification · User Roles and
Urgency. Read `how-to-use.md` and `challenger-probes.md` (in this folder)
for the framework rules and reusable probe patterns.

---

## Category: Feature Identity

**Example questions:**

- What is the name of this feature as it should appear in the PRD?
  *(intake question — open-ended by design; predicate phrasing does not apply)*
  *(Probe if too generic: "Is the proposed name specific enough to distinguish
  this from adjacent past or planned work? Yes / No — and if No, which
  alternative name disambiguates it?")*
- In one or two sentences, what does this feature do for the user?
  *(intake question — open-ended by design; predicate phrasing does not apply)*
  *(Probe if vague: "Which specific user capability exists after this feature
  that does not exist today? Name the capability.")*
- Is this change one of: (a) correcting an error in existing behavior, (b)
  adding a new capability, or (c) changing how an existing capability works?
  Which of (a), (b), (c) applies?

> **Depth indicator:** Can you state in one sentence what the user can do
> after this feature exists that they cannot do today? Is the name specific
> enough to distinguish it from adjacent past or planned work?
>
> **Comprehensiveness checklist:** Have you captured the rationale for why
> this capability is being added now? Have you confirmed whether it aligns
> with an existing product pattern or deliberately diverges?

---

## Category: Change Classification

**Example questions:**

- Which of the following best describes the primary change? (Select all that
  apply): (a) New user-facing screen or UI change, (b) Change to calculation
  logic, (c) Change to allocation methodology, (d) Reporting or BI output
  change, (e) Configuration or administration change, (f) Data model or
  schema change
- Which area of the product does this primarily affect? *(Use findings from
  the breakdown to offer specific options: "Based on what I found, this
  appears to relate to [area]. Is that correct? Yes / No — and if No, which
  area applies, and does it also touch [other area]? Yes / No.")*
- If multiple areas are in scope, which one of those areas is the primary
  driver?

> **Depth indicator:** Primary change type agreed. Product area confirmed
> against breakdown findings. Every area from recon has an explicit in/out
> decision.
>
> **Comprehensiveness checklist:** Have you applied the challenger posture —
> "why this area and not [adjacent area]?" — for any non-obvious scope
> boundary?

---

## Category: User Roles and Urgency

**Example questions:**

- Which user roles will interact with this feature? List each role.
- For each role, which specific actions are permitted to that role and not
  to others? *(Probe: "Is the role read-only or write-enabled? Are any actions
  admin-only? Yes / No for each.")*
- Is there a deadline or regulatory driver for this feature? Yes / No.
  *(If Yes: must the full scope ship by that date, or would a subset satisfy
  the constraint? Full scope / subset — and if subset, which subset?)*

> **Depth indicator:** Every role has a defined interaction. Permission
> differences between roles are explicit.
