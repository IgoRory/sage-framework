# Section 2 — Scope boundaries

Reference for prd-interviewer. Self-contained — no external skill references.

**Phase ID:** P2
**Always asked. Asked immediately after P1, before any detailed requirement
sections.**

Two categories: Explicit Exclusions · Downstream Impact and Boundaries.
Read `how-to-use.md` and `challenger-probes.md` (in this folder) for the
framework rules and reusable probe patterns.

---

## Category: Explicit Exclusions

**Example questions:**

- Which items are explicitly out of scope for this feature? List each
  out-of-scope item.
  *(Always prompt with adjacent areas from recon: "Based on what I found,
  [adjacent area] is closely related. Is [adjacent area] in scope or
  explicitly out of scope? In / Out.")*
- Is there anything that looks related but should NOT be changed as part of
  this work? Yes / No — and if Yes, which items?
- For each adjacent component or feature from recon, is it in scope or out
  of scope? *(Present them as specific options — In / Out per item — do not
  rely on the PM to enumerate.)*

> **Depth indicator:** Every adjacent area from recon has an explicit in/out
> decision. Out-of-scope list specific enough a developer could not
> accidentally include it.

---

## Category: Downstream Impact and Boundaries

**Example questions:**

- Are there any downstream systems or consumers of this data that must not
  be affected? Yes / No — and if Yes, which specific consumers (e.g., named
  BI reports, Dataverse entities, external exports)?
- Does this feature touch the Dataverse boundary? Yes / No.
  *(If Yes: which Dataverse entities are read or written, and is any new
  write permission required? Yes / No — and if Yes, which permission?)*

> **Depth indicator:** Every downstream consumer named with expected behavior
> (unaffected / needs update / needs notification). Dataverse boundary
> explicitly confirmed in or out of scope.
