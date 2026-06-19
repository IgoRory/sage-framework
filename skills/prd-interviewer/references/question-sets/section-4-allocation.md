# Section 4 — Allocation methodology changes

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P4
**Conditional — ask if feature type includes allocation.**

Three categories: Allocation Type and Methodology · Driver and Scope ·
Allocation Audit Log Impact.

Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns.

---

## Category: Allocation Type and Methodology

**Example questions:**

- Which allocation type does this change affect? Which of: (a) expense
  allocation, (b) income allocation, (c) capital allocation, (d) provisions,
  or (e) a combination? Name each affected type.
- What is the current allocation methodology, and what is the new
  methodology after this change? State each as a specific before/after rule.
  *(Require a specific rule: "today, expenses are allocated pro-rata based
  on instrument balance — which specific rule replaces it?")*
- Is the methodology changing because of (a) a regulatory requirement, (b) a
  client request, or (c) an error correction? Which of (a), (b), (c)
  applies?

> **Depth indicator:** Old and new methodology rules stated as specific
> sentences with a worked numeric example for each.

---

## Category: Driver and Scope

**Example questions:**

- Which cost pools or income streams are affected? List each affected pool
  or stream.
- What is the allocation driver — the metric that determines how much each
  instrument receives? Which of: balance, revenue, headcount, fixed
  percentage table, or other? If other, name it.
- Are there any instruments, entities, or periods that should be excluded?
  Yes / No — and if Yes, list each exclusion with its stated outcome.
- For a representative test case, what are the expected allocation outputs?
  State specific numbers or ratios.
- Do any BI reports or dashboards display allocation results that will
  change? Yes / No — and if Yes, which reports or dashboards?

> **Depth indicator:** Every cost pool has a named driver. Every exclusion
> has a stated outcome. Worked numeric example exists.

---

## Category: Allocation Audit Log Impact

**Example questions:**

- Does this change affect what is recorded in the allocation audit log — the
  record of what was allocated, to whom, and when? Yes / No.
- If Yes, which additional or changed information should be recorded, and
  are existing log entries affected? Affected / Not affected — and if
  Affected, how?
- Which downstream reports or review processes read from the audit log, and
  for each one, what happens when the log changes — unaffected, needs
  update, or needs reissue?

> **Depth indicator:** Audit log impact confirmed in or out of scope. If in
> scope, additional information and backward compatibility defined.
