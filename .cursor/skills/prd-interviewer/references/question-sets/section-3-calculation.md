# Section 3 — Calculation logic changes

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P3
**Conditional — ask if feature type includes calculation.**

Five categories: Affected Output Metrics · Calculation Process Impact ·
Behaviour Delta · FTP Logic · Incomplete Instrument and Error Handling.

Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns.

---

## Category: Affected Output Metrics

**Example questions:**

- Which output values or business metrics will this change affect? List each
  affected metric.
  *(Offer the business names of metrics your recon identified as likely in
  scope: "This looks like it may affect [metric A] and [metric B]. Does that
  match? Yes / No — and if No, which others apply?")*
- For each affected metric, is the change to (a) the calculation logic, (b)
  the input data, or (c) both? Which of (a), (b), (c) applies per metric?
- Which downstream reports, dashboards, or exports display these metrics,
  and for each one, what happens when the metric changes — unaffected,
  needs update, or needs republishing?

> **Depth indicator:** Every affected business metric is named with an
> explicit before/after direction. Downstream consumers traced.

---

## Category: Calculation Process Impact

**Example questions:**

- Which calculation processes will this change affect? List each affected
  process by business name.
  *(Ask in business terms: "the monthly FTP calculation", "the income
  allocation that distributes interest income to products")*
- For each affected process, which of these applies: (a) inputs change, (b)
  logic changes, (c) outputs change, or (d) a combination? Name the specific
  before/after behavior per process.
- Are there downstream processes that depend on the output of these
  calculations? Yes / No — and if Yes, what happens to each one?

> **Depth indicator:** Every affected calculation process described in plain
> language with a specific before/after behavior statement.

---

## Category: Behaviour Delta

**Example questions:**

- For each affected process, what is the current behavior and what is the
  new behavior? State each as a specific before/after pair.
  *(Probe if vague: "Can you give a worked example — for an instrument with
  balance X and rate Y, which specific value changes from V1 to V2?")*
- For the happy path, what is the expected output value or condition?
  *(Require a specific value or condition — not "correct results".)*
- Are there any instrument types or portfolio segments that should be
  excluded from this calculation change? Yes / No — and if Yes, for each
  excluded group, what should those instruments show instead?

> **Depth indicator:** Specific before/after behavior statement for every
> affected process. At least one worked numeric example. Every exclusion group
> has a defined outcome.

---

## Category: FTP Logic

*(Ask only if FTP calculation is involved)*

**Example questions:**

- Does this change affect how the pricing date is applied when looking up
  the funding rate for certain products? Yes / No.
  *(Probe: "Some products use a specific historical date rather than today's
  rate — does this feature change that lookup behavior? Yes / No — and if
  Yes, which products and which new date rule?")*
- Does this change affect which rate source is used to determine the funding
  rate? Yes / No — and if Yes, which source replaces which?
- Does this change affect which product types or instrument categories the
  calculation applies to? Yes / No — and if Yes, which products move in or
  out of scope?

> **Depth indicator:** Each FTP sub-area (pricing date, rate source, product
> scope) explicitly confirmed in or out of scope.

---

## Category: Incomplete Instrument and Error Handling

**Example questions:**

- Are there scenarios where this calculation cannot run for a specific
  instrument — for example, the instrument hasn't been set up for this
  process, it falls outside the applicable date range, or required data is
  missing? Yes / No — and if Yes, list each scenario.
  *(Use recon to make this specific: "For [business scenario your recon
  identified], does the calculation skip, flag, or halt? Skip / Flag / Halt.")*
- For each such scenario, which of (a) skip the instrument and continue, (b)
  flag with a warning, or (c) halt the entire run applies?
- Should this change apply to (a) instruments added during the current
  period, (b) instruments that closed or matured during the current period,
  and (c) balancing or plug instruments? Yes / No per category.

> **Depth indicator:** Every identified incompleteness scenario has a defined
> outcome (skip, flag, or halt) and a user-facing message or TBD marker.
