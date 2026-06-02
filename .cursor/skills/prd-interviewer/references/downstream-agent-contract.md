# Downstream Agent Contract

Reference for prd-interviewer. Self-contained — no external skill references.

Every artifact the prd-interviewer (and its delegated handoff chats) produces
is consumed by a downstream agent or gate. This file is the contract for what
each downstream consumer expects to read, which keys they parse, and which
paths they assume. The contract is anchored to the locked L1–L12 architectural
model; consumers that change behaviour must update this file first and then
realign to it.

**Schema authority.** PRD section references in this file are anchored to
[`prd-section-schema.md`](./prd-section-schema.md). The schema is the 8-section
layout (§1 Feature Definition, §2 Success Criteria, §3 Scope, §4 Detailed
Business Requirements — 14 sub-sections with stable ID prefixes, §5 Data
Migration, §6 Risks & Mitigations, §7 Open Items & Ambiguities, §8 Related
Artefacts). Legacy 15-section layouts are handled via the back-compat dual-
layout read window documented in §3 below.

**Bundle authority.** Every consumer that needs to know "what files belong to
this sub-PRD bundle?" reads `bundle-manifest.json` (finalised by the interviewer
at end of P9). Heuristic discovery of bundle files on disk is forbidden — the
manifest is the canonical list.

---

## 1. Per-consumer contract table

| Consumer | Reads | Key contract items |
|---|---|---|
| **dev-interview** | `acceptance-criteria.md`, `component-spec.md`, `demos/demo-interactive.html`, `demos/_summary.md` | Sequential `AC-NNN`; `surface` field replaces ID prefix for filtering (`UI` / `calc` / `data` / `error`); each AC carries `linked_requirement_ids` referencing §4.NNN; demo `scenario_id`s; component IDs from spec |
| **traceability-reviewer** | `acceptance-criteria.md`, `prd.md`, implementation plan, `traceability.md` | Sequential `AC-NNN`; §4.NNN sub-section IDs; bidirectional invariant — every AC maps to ≥1 §4.NNN, every §4.NNN maps to ≥1 AC; blocker on any missing link |
| **orchestrator (TDD-spec gen)** | `acceptance-criteria.md` | Sequential `AC-NNN`; GWTX clauses (Given/When/Then/eXample); `surface` field groups test types |
| **prd-completeness-check** | Full bundle via `bundle-manifest.json` | 9 scoring dimensions against the 8-section schema + 14 §4 sub-sections; Anchor Attestation completeness is its own scored dimension; AC IDs follow sequential `AC-NNN` with dual-layout support during the backfill-on-touch window |
| **prd-amend** | `stale-check.md`, `prd.md`, affected briefs | `prdHash` headers; STALE / FRESH / MISSING classifications; diff brief inherits Family N anchor extraction discipline; emits new event names per `telemetry-schema.md` |
| **prd-stale-check** | All derivative `prdHash` headers vs current `prd.md` SHA-256 | Reads `bundle-manifest.json` for the derivative list — never heuristically discovers files on disk; classifies each derivative `FRESH` / `STALE` / `MISSING` |
| **prd-walkthrough** | Three `_summary.md` files + spot-reads on PM challenge | Reads `bundle-manifest.json` to know what to walk through; summary-first read discipline; deep-reads only on PM challenge to a specific item |
| **demo handoff chat** | `demos/_brief.md`, every Section 3 YAML, `acceptance-criteria.md` | Family N: brief Section 3 carries `{ path, read_mode, expected_anchors }` per cited YAML (N1); `_summary.md` carries `## YAML reads` H2 with `anchors_extracted` (N2); Tier 1 self-review N6 read-completeness item; brief Section 6 verbatim copy strings; scenario list with `scenario_id` ↔ `AC-NNN` mapping; `prdHash` header in `_summary.md` |
| **sample-data handoff chat** | `sample-data/_brief.md`, cited schemas/YAMLs, `acceptance-criteria.md` | Same Family N rules (N1–N8); record IDs; edge-case row sets keyed by `AC-NNN` (with the AC's `surface` field disambiguating category) |
| **component-spec handoff chat** | `component-spec/_brief.md`, cited YAMLs, `acceptance-criteria.md`, `reuse-map-draft.md` | Same Family N rules; six-element entries per `component-spec-template.md`; `AC-NNN` cross-references back to the sibling AC file |
| **kickoff-dev-review** *(new in contract)* | `prd.md`, `acceptance-criteria.md`, `component-spec.md`, `bundle-manifest.json` | Reads manifest to confirm all expected files are present and `FRESH`; loads PRD + AC + reuse-map + demo `_summary.md` + component-spec `_summary.md` as pre-read for the dev review session |
| **phase-splitter** *(new in contract)* | `prd.md`, `acceptance-criteria.md`, `component-spec.md`, `traceability.md`, `bundle-manifest.json` | Uses §4.NNN sub-section coverage to score phase candidates; sequential `AC-NNN`; component IDs; cross-page impacts via §4.14 `CP-NNN` entries |
| **prd-demo-generator** | DEPRECATED — permanently inert per PM ruling at Phase E close (25-MAY-2026) | No pipeline reads from or invokes this skill; preserved as historical artefact only; re-activation requires PM approval and a fresh evaluation against the current pipeline. Functional replacement is the three-surface manual handoff (demo handoff chat row above) |

---

## 2. Conventions (binding across consumers)

### 2.1 AC IDs

- Format: **sequential `AC-NNN`** (zero-padded 3-digit integer). No buckets.
  The legacy bucketed `AC-{REQ|EC|UI|ERR}-NNN` is retired — category lives in
  the `surface` field on each AC (`UI` / `calc` / `data` / `error`).
- AC IDs are string-equal across `acceptance-criteria.md`, `demos/_summary.md`,
  `traceability.md`, and the implementation plan.
- AC IDs are assigned at write-time in `acceptance-criteria.md` and immutable
  thereafter. Never renumber on edit — append new IDs.

### 2.2 §4 sub-section IDs

- Format: `{PREFIX}-NNN` where prefix is one of 14:
  `DM` (Data Model & Entities), `CL` (Calculation & Logic), `AL` (Allocation
  & Distribution), `WF` (Workflow & State), `UI` (UI & Interaction), `VC`
  (Validation & Constraints), `ER` (Error Handling), `NM` (Notifications &
  Messaging), `PA` (Permissions & Access Control), `IN` (Integration &
  External Surfaces), `PF` (Performance & Scale), `AU` (Audit & Telemetry),
  `RX` (Reporting & Export), `CP` (Cross-Page Impacts).
- Assigned **in-flow** during the phase that captures the requirement (P1
  seeds DM/PA, P3 owns CL, P4 owns AL, P5 owns UI/WF/CP/PF, P6 produces
  edge-case-driven entries per the §4 mapping in `phase-P6.md`). Never
  assigned at PRD generation time.
- Sequences are independent per prefix per sub-PRD.
- Every AC's `linked_requirement_ids` field references §4.NNN IDs.

### 2.3 `scenario_id`s

- Format: lowercase kebab-case stable identifier (e.g. `prod-read-load`).
- Stable across re-handoffs so test files and `demo-behavior-manifest.md`
  references do not break.
- Every `scenario_id` appears in the demo's `_summary.md` Scenario coverage
  table and (where applicable) in `traceability.md`.

### 2.4 Component IDs

- Sourced from `.context/components/manifest.yaml` for matched components.
- New components get stable IDs assigned in the brief; the same ID appears in
  the component-spec entry, the traceability table, and any sample-data or
  demo brief that references it.

### 2.5 File paths

- Every consumer reads from `.sage/prds/[FEATURE_ID]/[sub-prd-id]/` or its
  subfolders. The pre-lift convention without the sub-PRD subdirectory is
  fully superseded.
- Demo, sample-data, and component-spec briefs each live in their surface's
  subfolder (`demos/`, `sample-data/`, `component-spec/`) as `_brief.md`.
- Summary files share the same surface subfolder as `_summary.md`.

### 2.6 `prdHash` headers

- Every derivative carries a YAML-frontmatter `prdHash:` field. The value is
  the SHA-256 (lowercase hex) of `prd.md`'s body content (the bytes after the
  closing `---` of the PRD's own frontmatter) at the moment the derivative
  was written.
- `prd-stale-check` reads these headers to classify each derivative as
  `FRESH` (hash matches current `prd.md`), `STALE` (hash mismatches), or
  `MISSING` (no header / header `[COMPUTATION_FAILED]` / derivative absent).
- A computation failure surfaces as the literal string `prdHash:
  '[COMPUTATION_FAILED]'` and is treated as `MISSING`.

### 2.7 Family N anchor tables

- Every handoff `_summary.md` carries a `## YAML reads` H2 section with a
  table of the form:

  ```
  | path | read_mode | anchors_extracted |
  | ... | full | states: [read, edit, dirty]; empty_copy: "..."; action_buttons_count: 4 |
  ```

- The interviewer's post-return validation reads only the cited YAML files
  (not the heavy artifact) and matches each `anchors_extracted` value
  verbatim against the YAML text. Mismatch routes through L11 C2 (structural
  → tighter brief and re-handoff; copy → re-handoff with brief amendment;
  yaml-vs-pm contradiction → escalate to orchestrator; cosmetic → accept into
  PRD §7 Open Items).
- N5 spot-check: the interviewer randomly opens one or more artifact rows on
  return to confirm against the YAML in addition to anchor verification.

---

## 3. Pre-lift migration policy (backfill-on-touch)

The new schema (8-section PRD, sequential `AC-NNN`, 14 §4 prefixes, `prdHash`
headers, `bundle-manifest.json`) is the post-lift contract. Pre-lift bundles
remain in their existing layout until next touched.

- On next touch (re-interview, AC amendment, demo regeneration, or any
  PM-initiated action against that sub-PRD), the bundle migrates fully:
  PRD rewritten against the 8-section schema; AC IDs renumbered from
  `AC-{REQ|EC|UI|ERR}-NNN` to sequential `AC-NNN` with the `surface` field
  added; `prdHash` headers added to all derivatives; `bundle-manifest.json`
  written.
- The migration is recorded in PRD §8 Related Artefacts version history.
- Downstream consumers carry **dual-layout read logic** (old bucketed vs new
  sequential) until every active sub-PRD has been touched once post-lift.
  Once the last legacy bundle migrates, dual-logic is removed.
- In-flight sub-PRDs (`.sage/prds/PROF-354/sub-prd-1`, `sub-prd-2`) are
  explicitly **not** migrated as part of the L1–L12 overhaul — backfill-on-
  touch handles them on first PM amendment.

---

## 4. Post-return escalation (Family N anchor verification failure)

When the interviewer's Family N anchor verification fails on a returned
handoff, the response routes through L11 C2:

1. The interviewer surfaces which anchor mismatched, with the YAML path and
   the expected vs. actual values, in the Deviations report to the PM.
2. The PM chooses:
   - **Structural mismatch** → tighter brief (more anchors, narrower Section
     6 verbatim) and re-handoff.
   - **Copy mismatch** → re-handoff with brief amendment.
   - **YAML-vs-PM contradiction** → escalate to `prd-orchestrator` (the
     breakdown's `investigation_context` may be defective).
   - **Cosmetic** → accept the deviation into PRD §7 Open Items with stated
     reason.
3. Handoff chats never amend interviewer outputs directly — read-only
   discipline as for other consumers.

---

## 5. Read-only access discipline

Downstream consumers are read-only with respect to the prd-interviewer's
outputs. They may produce sibling artifacts (test files, traceability
reports, completion reports, stale-check reports) but never modify the PRD,
AC sibling, component spec, sample-data, demo, or `bundle-manifest.json`.

If a consumer needs to amend an interviewer artifact, the path is:

1. The consumer surfaces the gap or defect in its own output.
2. The PM returns to the prd-interviewer chat (or opens a new one) and
   amends the brief or re-handoffs as needed (via `prd-amend` when the PM
   has already edited `prd.md`).
3. The consumer reruns against the updated artifacts.

The artifacts are produced by one owner per surface — never by the consumer
of those artifacts. This keeps responsibility for the PRD's outcome with the
PM and interviewer, not with downstream agents.

---

## 6. Effectiveness metric families (six families)

The L12 contract names six effectiveness metric families that the evaluator
skills (`prd-interviewer-effectiveness-evaluator`,
`session-performance-evaluator`) compute from telemetry. They are listed
here so every consumer that emits or aggregates telemetry knows which
family its events feed:

1. **Question discipline** — DI rate per phase (from
   `prd_phase_completed.deferredCount`), DI category distribution,
   deferral-to-acceptance rate.
2. **Phase progression** — phase duration distribution (envelope
   timestamps), phase rejection rate per phase, phase redirect rate, phase
   restart count.
3. **Handoff quality** — re-handoff rate per surface, anchor mismatch rate
   by `mismatchType`, deviation count distribution (from
   `manual_handoff_returned.deviationCount`), ambiguity flag rate per
   surface.
4. **Self-review discipline** — self-review gate failure rate by gate level
   (`L1` / `L3` / `L5`), coverage block rate per dimension, pre-write bar
   walk failure rate per Pass Condition.
5. **Recon quality** — override frequency by `overrideType`, breakdown gap
   detection rate, hard-stop rate by `hardStopReason`.
6. **PM friction & throughput** — abort rate by `phaseAtAbort`,
   time-to-completion (interview started → completed envelope spread),
   staleness-resumption rate, mid-phase resume rate, completeness-check
   pass rate on first submission.

The full event vocabulary, payload shapes, and consumer assignments live in
[`telemetry-schema.md`](./telemetry-schema.md). This file names which
metrics are derived — `telemetry-schema.md` names which events feed them.

---

## 7. PM-gate decisions (locked)

The following gate questions are locked across L1–L12. Consumers updating
their read paths must respect them.

- **AC scheme — LOCKED (sequential).** Sequential `AC-NNN` with the
  `surface` field replaces the legacy bucketed `AC-{REQ|EC|UI|ERR}-NNN`
  scheme. Dual-layout read logic carries downstream consumers through the
  backfill-on-touch window only.
- **§4 sub-section prefixes — LOCKED (14 prefixes).** The 14 listed in §2.2
  are stable. New patterns that do not fit any of them are flagged at the
  single conclusion gate; PM picks fold-into-closest, custom-section, or
  out-of-scope. Recurring novel patterns trigger future L4 schema
  amendment.
- **Pre-lift artifact migration — LOCKED (backfill-on-touch).** See §3.
- **prd-demo-generator deprecation — LOCKED (permanently inert).** The
  Phase E close PM ruling (25-MAY-2026) preserves the skill file as a
  historical artefact only. No pipeline reads from or invokes it.
  Re-activation requires PM approval and a fresh evaluation.
- **`bundle-manifest.json` finalisation — LOCKED.** The interviewer
  finalises the manifest at end of P9, immediately before
  `prd_interview_completed`. Downstream consumers that iterate bundle
  files MUST read the manifest — heuristic disk discovery is forbidden.
