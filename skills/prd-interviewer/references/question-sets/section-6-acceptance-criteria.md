# Section 6 — Acceptance criteria

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P6
**Always asked. Asked last among the requirements sections, after all
behaviour, calculation, allocation, and UI detail is captured.**

Two categories: Success Scenarios · Performance and Test Scope.

Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns. Use
`acceptance-criteria-template.md` (in the parent references folder) for the
artifact this section produces.

---

## Category: Success Scenarios

**Example questions:**

- For each success scenario — happy path, failure path, and boundary
  condition — state the starting condition, the action, and the exact
  expected output. List each scenario.
  *(Probe per scenario: "Which specific value or condition would tell you
  this scenario has passed? Name it.")*
- For UAT verification, which specific data and which specific steps will
  you use? Name them.
- Can you describe at least 3 scenarios in detail right now? Yes / No — and
  if Yes, list each scenario.
  *(Tier 1 minimum; see complexity-classifier.md for thresholds.)*

> **Depth indicator:** Every scenario has explicit input, action, and
> measurable output — not "correct result" but a specific value or condition.

---

## Category: Performance and Test Scope

**Example questions:**

- Are there any performance requirements? Yes / No — and if Yes, state the
  specific threshold.
  *(Probe if vague: "Is there a specific threshold — for example, the
  calculation must complete in under 30 seconds for a portfolio of 10,000
  instruments? Yes / No — and if Yes, what is the threshold?")*
- Are there any existing areas of the product that this feature must not
  break? Yes / No — and if Yes, list each at-risk area.
  *(Use recon to identify at-risk areas — ask the PM to confirm in business
  terms: In risk / Not at risk per area.)*

> **Depth indicator:** Performance requirements either defined with specific
> thresholds or explicitly marked not applicable. Existing test areas
> confirmed.
