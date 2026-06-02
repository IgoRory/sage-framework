# Phase P2 — Scope boundaries and §4 coverage map

Reference for `prd-interviewer`. Self-contained — no external skill
references. Cross-phase rules live in
[`shared-protocols.md`](./shared-protocols.md). This module inlines only
the P2-specific scope, the six-category downstream check, the §4
coverage map declaration, and the P2 self-review.

**Phase ID:** `P2`
**Always asked. Runs immediately after P1, before any detailed
requirements phases (P3 / P4 / P5 / P6).**
**Question catalogue:** [`../question-sets/section-2-scope-boundaries.md`](../question-sets/section-2-scope-boundaries.md)

---

## Why P2 runs before any detailed requirements phase

Scope boundaries are established before any detailed requirement is
captured. If the interviewer asks calculation, allocation, or UI
questions about an area that will be declared out of scope, those
captured requirements are wasted work, pollute the PRD, and create
downstream confusion. The P2 §4 coverage map declaration further pins
which §4 sub-sections are even allowed to be populated for this
interview, so the conditional phases (P3 / P4 / P5) know whether they
trigger at all.

---

## Scope

P2 covers three categories:

1. **Entity in / out scoping.** Every data entity surfaced at P1
   (DM-NNN seeds) and every adjacent entity surfaced by the breakdown is
   explicitly scoped in or out. No silent omissions.
2. **Adjacent-area in / out scoping.** Every page, screen, dashboard,
   report, export, scheduled job, calculation surface, or external
   system surfaced by `breakdown.investigation_context` has an explicit
   in / out decision recorded.
3. **§4 sub-section coverage map declaration.** At P2 exit, the
   interviewer states which §4 sub-sections will be active for this
   interview and which will carry `Not applicable — [reason]`. PM
   confirms before the coordinator transitions to P3.

---

## Entity scope confirmation (DM-NNN reconciliation)

Every DM-NNN seed assigned at P1 is reconciled at P2:

- **In scope.** DM-NNN entry carries an in-scope flag; phase modules
  downstream may add behaviour against it.
- **Out of scope.** DM-NNN entry is moved to PRD §3.2 with the PM's
  stated reason. The entry is retained (not deleted) so the trace from
  P1 → P2 is auditable.
- **Boundary.** DM-NNN entry is moved to PRD §3.3 Scope Boundaries with
  the boundary condition stated (e.g. "in scope for read, out of scope
  for write").

Any entity surfaced by breakdown investigation but NOT named by the PM
at P1 is surfaced at P2 with a delta question per Family A:

> "The breakdown indicates entity [X] is adjacent to this feature. In
> scope or out?"

Out-of-scope decisions are recorded with enough specificity that a
developer reading §3.2 cannot accidentally include the entity in
implementation.

---

## Downstream consumer check — six categories (mandatory, all six asked)

Every PRD passes through a six-category downstream impact check. For
each category, the PM either confirms "no impact on category X" or names
specific consumers. Silent skipping is forbidden (Family H H2). The six
categories:

1. **Other pages** — other screens in the application that read or
   render the affected entities.
2. **Dashboards / reports** — dashboards, fixed reports, ad-hoc report
   templates that consume the affected entities or calculations.
3. **Exports** — file exports, scheduled exports, on-demand exports
   (CSV / Excel / PDF).
4. **Downstream calculations** — calculation surfaces (e.g. FTP, cost
   allocation, profitability roll-up) whose inputs include the affected
   entities.
5. **Scheduled jobs** — overnight jobs, intra-day jobs, scheduled
   recalculations that touch the affected entities.
6. **External systems** — Dataverse, downstream BI, regulatory feeds,
   any system outside the Profitability product boundary.

Each category's answer feeds either §3 Scope (if confirmed in or out)
or §4.14 Cross-Page Impacts (`CP-NNN` IDs created in-flow when an impact
is named). The Dataverse boundary specifically is explicitly confirmed
in or out — Dataverse remains a recurring product-boundary edge.

---

## §4 sub-section coverage map declared at P2 exit

This is the safety net the single conclusion gate reconciles against.
At P2 exit, before transitioning to P3, the interviewer states the §4
sub-section coverage map and asks the PM to confirm:

> "Based on what we've established so far, this PRD will populate §4.1
> Data Model, §4.5 UI & Interaction, §4.6 Validation, §4.9 Permissions,
> §4.12 Audit. The other nine sub-sections (§4.2 Calculation, §4.3
> Allocation, §4.4 Workflow, §4.7 Error Handling, §4.8 Notifications,
> §4.10 Integration, §4.11 Performance, §4.13 Reporting, §4.14
> Cross-Page Impacts) will carry `Not applicable — [reason]` notices.
> Confirm or amend."

The 14 §4 sub-section IDs (full list in `prd-section-schema.md` §4):

`DM` · `CL` · `AL` · `WF` · `UI` · `VC` · `ER` · `NM` · `PA` · `IN` ·
`PF` · `AU` · `RX` · `CP`

PM responses:

- **Confirm.** The declared map is locked. The single conclusion gate
  later reconciles captured items against this map.
- **Amend — add.** PM names sub-sections to add (typically because the
  PM realises a category was missed). The interviewer updates the map
  verbatim and reconfirms.
- **Amend — remove.** PM names sub-sections to remove. The interviewer
  updates and reconfirms.

The locked map also pre-determines which conditional phases trigger:

- §4.2 CL in scope → P3 (Calculation) will trigger.
- §4.3 AL in scope → P4 (Allocation) will trigger.
- §4.5 UI in scope → P5 (UI & UX) will trigger.

If none of CL / AL / UI is in the map, the coordinator skips P3 / P4 /
P5 and jumps from P2 directly to P6 (Edge cases). P6 always runs.

---

## In-flow ID continuation

P2 continues the DM-NNN seed from P1 (any new entities surfaced via the
adjacent-area scope question get DM-NNN IDs at capture). P2 also seeds:

- **CP-NNN — Cross-Page Impacts.** Every outbound or inbound impact
  surfaced by the six-category downstream check gets a `CP-NNN` ID at
  capture. Entry carries: `inbound | outbound`,
  `consumer-sub-PRD-or-page`, `consumed-behaviour-reference`. CP-NNN
  entries are relationship pointers — they reference canonical
  behaviour entries in the originating sub-PRD by sub-PRD ID +
  requirement ID. They NEVER duplicate behaviour text.

---

## Depth bar

P2 is complete when **all** of the following are true:

- Every entity surfaced at P1 (DM-NNN) has an in / out / boundary
  decision recorded.
- Every adjacent area surfaced by breakdown investigation has an in / out
  decision recorded.
- The out-of-scope list (§3.2) is specific enough that a developer
  reading it could not accidentally include an out-of-scope item.
- Every one of the six downstream-consumer categories has been asked and
  answered (either "no impact" or specific consumers named).
- The Dataverse boundary is explicitly confirmed in or out of scope.
- The §4 sub-section coverage map is declared and PM-confirmed.
- Conditional-phase trigger flags (`P3_active`, `P4_active`,
  `P5_active`) are derivable from the declared coverage map.

---

## P2-specific self-review (4 items) — phase exit checklist

P2-specific L6 G1 self-review, run by the interviewer before the PM
sees P3 (or P4 / P5 / P6 if P3 is skipped). REPLACES the generic
checklist for P2. Four items, evaluated as yes/no predicates:

1. **Every adjacent area from breakdown has in / out decision.** No
   adjacent area surfaced in `breakdown.investigation_context` is left
   undecided.
2. **Out-of-scope list is specific.** §3.2 entries are concrete enough
   that a developer reading them could not accidentally include an
   out-of-scope item.
3. **§4 sub-section coverage map declared and PM-confirmed.** The map
   is recorded in interview state with PM's verbatim
   confirmation / amendment. Conditional-phase trigger flags are set.
4. **Downstream consumer check completed across all six categories.**
   Each of the six categories (other pages, dashboards/reports,
   exports, downstream calculations, scheduled jobs, external systems)
   has an answer recorded — either "no impact" or specific consumers
   named with associated CP-NNN entries.

Self-review failure emits `prd_self_review_gate_failed` with
`gateLevel: L1`, `phaseId: P2`, and `failedChecklistItem` naming which
of the four items failed.

---

## Telemetry

P2-scoped emit sites only:

- `prd_phase_started` — `phaseId: P2`.
- `prd_phase_completed` — `phaseId: P2`. Coverage dimension `D-SCOPE`
  is evaluated at this point.
- `prd_self_review_gate_failed` — emitted if the P2 self-review fails.
- `prd_coverage_dimension_blocked` — emitted with
  `dimension: D-SCOPE` if the coverage dimension cannot be closed at
  P2.

---

## Cross-cutting protocols invoked (pointer only)

P2 applies all 14 Families A–N from
[`shared-protocols.md`](./shared-protocols.md). Heaviest binders:

- **Family A — Question discipline.** Six-category check uses one
  predicate-style question per category, never a list-dump.
- **Family E — No mid-interview recon.** Adjacent-area surfacing runs
  against `breakdown.investigation_context` only; interviewer never
  opens YAMLs.
- **Family J — Anti-hallucination.** Out-of-scope items reflect PM
  decisions verbatim; the interviewer never invents an "implied" scope
  decision.
- **Family C — Deferred Items List.** Items the PM cannot decide at P2
  (e.g. "we need to ask Compliance whether this touches the regulatory
  feed") become DI entries with status `Open` and resolve at the single
  conclusion gate.

---

## Next phase

On P2 exit, the coordinator routes per the declared §4 coverage map:

- §4.2 CL in scope → [`phase-P3.md`](./phase-P3.md) (Calculation).
- Else §4.3 AL in scope → [`phase-P4.md`](./phase-P4.md) (Allocation).
- Else §4.5 UI in scope → [`phase-P5.md`](./phase-P5.md) (UI & UX).
- Else → [`phase-P6.md`](./phase-P6.md) (Edge cases — always runs).
