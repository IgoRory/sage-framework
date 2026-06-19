# Question Sets — Index

Reference for prd-interviewer. Self-contained — no external skill references.

The question catalogue is split into one file per interview section, plus a
shared how-to-use file and a shared challenger probes catalogue. The
prd-interviewer reads the section file for the section it is conducting and
references this index when it needs to switch sections.

## Files in this folder

| File | Purpose |
|---|---|
| [`how-to-use.md`](./how-to-use.md) | Framework: question discipline, business-language rule, batching rule, depth-vs-count gate. Read once at interview start. |
| [`section-1-feature-definition.md`](./section-1-feature-definition.md) | P1 — Feature identity, change classification, user roles and urgency. |
| [`section-2-scope-boundaries.md`](./section-2-scope-boundaries.md) | P2 — Explicit exclusions, downstream impact and boundaries. |
| [`section-3-calculation.md`](./section-3-calculation.md) | P3 — Affected output metrics, calculation process impact, behaviour delta, FTP logic, incomplete instrument and error handling. |
| [`section-4-allocation.md`](./section-4-allocation.md) | P4 — Allocation type and methodology, driver and scope, allocation audit log impact. |
| [`section-5-ui-and-ux.md`](./section-5-ui-and-ux.md) | P5 — Screen inventory, component inventory, state models, micro-detail, interaction model, cross-page impact check. |
| [`section-6-acceptance-criteria.md`](./section-6-acceptance-criteria.md) | P6 — Success scenarios, performance and test scope. |
| [`section-7-edge-cases.md`](./section-7-edge-cases.md) | P7 — Seven edge-case categories (interaction sequence, cascading, concurrency, state boundary, cross-component dependency, data integrity, failure and recovery). |
| [`challenger-probes.md`](./challenger-probes.md) | Reusable probe patterns (why-not, cross-impact, micro-detail, rationale, boundary-stretch). Applied across any section. |

## Section ↔ phase mapping

| File | Phase ID |
|---|---|
| section-1-feature-definition.md | P1 |
| section-2-scope-boundaries.md | P2 |
| section-3-calculation.md | P3 (conditional) |
| section-4-allocation.md | P4 (conditional) |
| section-5-ui-and-ux.md | P5 (conditional) |
| section-6-acceptance-criteria.md | P6 |
| section-7-edge-cases.md | P7 |

P3/P4/P5 are skipped when conditions are false — see prd-interviewer
SKILL.md for the conditional rules.

## Reading discipline

- Read `how-to-use.md` once at interview start to load the framework rules.
- Read the active section's file at the start of that section. Do not
  preload all section files — they are independent.
- Read `challenger-probes.md` lazily, when a probe is warranted, rather
  than on every batch.
