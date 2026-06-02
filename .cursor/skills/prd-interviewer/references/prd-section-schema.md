# PRD Section Schema

Reference for prd-interviewer. Self-contained — no external skill references.

This is the **canonical schema for the post-L1–L12 PRD bundle**. Every
downstream consumer (`prd-completeness-check`, `dev-interview`,
`traceability-reviewer`, `orchestrator` TDD-spec gen, `prd-stale-check`,
`prd-amend`, `prd-walkthrough`, `phase-splitter`, `kickoff-dev-review`)
references PRD sections by stable number against this file.

---

## Stability rule (binding)

Once published in this file, section numbers and ID prefixes **do not
change**. Phase D completeness scoring, Phase D.5 consumer wiring, and Phase
E supporting skills cite sections by number and §4 sub-ID prefix against
this schema. A renumber would break every downstream reader silently.

If a future phase needs an additional section, it is appended at the end
with the next available number — never inserted in the middle. If a future
phase needs an additional §4 sub-section, it is appended at §4.15+ with a
new ID prefix.

---

## What lives in the PRD vs siblings

| Lives in `prd.md` | Lives in a sibling file |
|---|---|
| Plain-English feature description, user, problem | Acceptance criteria — `acceptance-criteria.md` |
| Business outcome, success criteria | Component / surface map — `component-spec.md` |
| Detailed business requirements (§4 with stable IDs) | Sample data — `sample-data/*.json` |
| Scope (in / out / boundaries) | Demos — `demos/demo-interactive.html`, `demos/calculation-demo.html` |
| Dependencies (5-subsection breakdown) | Reuse map — `reuse-map-draft.md` |
| Data migration | Bidirectional trace — `traceability.md` |
| Risks & mitigations, open items | Verbatim PM answers — `interview-answers.json` |
| Related artefacts pointers + freshness statuses | Component pattern decisions — `component-pattern-confirmation.md` |
| Version History (binding attribution) | Bundle manifest — `bundle-manifest.json` |

**Hard rule.** No acceptance-criteria text appears in `prd.md`. ACs live in
the sibling `acceptance-criteria.md`. The PRD §4 entries reference AC IDs
indirectly via `linked_requirement_ids` running the other direction (every
AC links to ≥1 §4.NNN); the PRD itself never restates AC Given/When/Then.

**Hard rule.** No internal-mechanism prose in `prd.md`. SP names, return
codes, flag mutations, internal class names, view column names, API
endpoints, and similar implementation constructs are forbidden in PRD text.
Translate every such concept into the observable outcome it produces.
PM-directed SQL is admissible verbatim only when explicitly requested by
the PM (carry-over from L2).

---

## Unnumbered preamble — YAML frontmatter (binding)

Every derivative in the bundle (`prd.md`, `acceptance-criteria.md`,
`reuse-map-draft.md`, `component-pattern-confirmation.md`, `traceability.md`,
all handoff `_summary.md` files) carries a YAML frontmatter block at the
top of the file, terminated by a `---` delimiter. The first non-frontmatter
content begins immediately after.

### Frontmatter for `prd.md`

```yaml
---
title: <sub-PRD title>
subPrdId: sub-prd-N
featureId: PROF-NNN
version: 1.0.0
author: <PM full name>
date: DD-MMM-YYYY
prdHash: <sha256-hex of body content below the closing --- delimiter>
---
```

### Frontmatter for every other derivative

(sibling AC file, traceability, reuse-map, component-pattern-confirmation,
all handoff `_summary.md` files)

```yaml
---
derivativeOf: prd.md
prdHash: <sha256-hex of prd.md body content at the moment this derivative was written>
writtenAt: <ISO 8601 UTC>
producer: <interviewer | handoff:demo | handoff:sample-data | handoff:component-spec>
---
```

### `prdHash` computation rule

SHA-256 of the body content of `prd.md` **after** the closing `---` of the
frontmatter, encoded as lowercase hexadecimal. Implementation chats must
apply byte-for-byte consistency — no leading/trailing whitespace stripping,
no line-ending normalisation, no BOM removal. The `prd-stale-check` skill
applies the same rule when comparing.

**Computation failure:** if SHA-256 computation fails on a derivative write
(per L11 D5), the derivative is written with
`prdHash: '[COMPUTATION_FAILED]'`. `prd-stale-check` treats this exact
string as MISSING and prompts regeneration.

---

## §1 Feature Definition

- **§1.1 Purpose** — what this sub-PRD delivers in one paragraph of
  business English.
- **§1.2 Business outcome** — the user-observable / customer-visible
  outcome the feature produces. Outcome-only.
- **§1.3 Dependencies** — **locked 5-subsection structure** (every
  subsection always present; empty bodies state `None.`):
  - **§1.3.1 Prerequisite** — work items / data / configuration that must
    exist before this sub-PRD can ship.
  - **§1.3.2 Blocks-Downstream** — what this sub-PRD's completion unblocks.
  - **§1.3.3 Concurrent** — sub-PRDs / work items that ship in the same
    cycle and share surfaces.
  - **§1.3.4 Reference** — external documents, ADRs, prior PRDs the
    reader may need.
  - **§1.3.5 Cross-Sub-PRD** — relationships with other sub-PRDs in the
    same feature; each entry references the related sub-PRD by ID and
    the canonical behaviour entry it points at.
- **§1.4 User Roles** — **role list only**. No permissions matrix here
  (permissions live under §4.9 Permissions & Access Control as `PA-NNN`
  entries).
- **§1.5 User Stories** — finer-grained: each story carries `id`,
  `role`, `goal`, `motivation`, `linked_ac_ids`.

---

## §2 Success Criteria

- **§2.1 Definition of success** — free-form prose describing what
  "successful delivery" looks like for this sub-PRD.
- **§2.2 KPIs** — **no mandatory KPIs**. The PM may add KPIs but the
  schema does not require them. If omitted, the heading still appears
  with body `Not applicable — [reason]`.

---

## §3 Scope

All three subsections are kept separate (PM rejected collapsing to
In-Scope-only). Each subsection always appears; empty bodies state
`Not applicable — [reason]`.

- **§3.1 In Scope** — what the sub-PRD delivers.
- **§3.2 Out of Scope** — what the sub-PRD intentionally does not deliver.
  Each item is specific enough that a developer could not accidentally
  include it.
- **§3.3 Scope Boundaries** — edges and grey areas where in/out is
  non-obvious. Each entry names the boundary and the rule that decides.

---

## §4 Detailed Business Requirements — canonical menu with 14 stable ID prefixes

| Sub-section                              | ID prefix |
|------------------------------------------|-----------|
| §4.1 Data Model & Entities               | `DM-NNN`  |
| §4.2 Calculation & Logic                 | `CL-NNN`  |
| §4.3 Allocation & Distribution           | `AL-NNN`  |
| §4.4 Workflow & State                    | `WF-NNN`  |
| §4.5 UI & Interaction                    | `UI-NNN`  |
| §4.6 Validation & Constraints            | `VC-NNN`  |
| §4.7 Error Handling                      | `ER-NNN`  |
| §4.8 Notifications & Messaging           | `NM-NNN`  |
| §4.9 Permissions & Access Control        | `PA-NNN`  |
| §4.10 Integration & External Surfaces    | `IN-NNN`  |
| §4.11 Performance & Scale                | `PF-NNN`  |
| §4.12 Audit & Telemetry                  | `AU-NNN`  |
| §4.13 Reporting & Export                 | `RX-NNN`  |
| §4.14 Cross-Page Impacts                 | `CP-NNN`  |

### ID assignment rules

- **In-flow assignment.** §4 sub-section IDs are assigned **during the
  phase that captures the requirement**, not at PRD generation. P3
  assigns `CL-NNN`, P4 assigns `AL-NNN`, P5 assigns `UI-NNN` /
  `WF-NNN` / `CP-NNN` / `PF-NNN`, P6 assigns IDs per the edge-case-
  category mapping in `phase-P6.md`, and cross-cutting sub-batches at
  each phase assign the cross-cutting IDs (`VC`, `PA`, `NM`, `AU`, `WF`,
  `IN`, `PF`).
- **Independent sequences.** Each prefix has its own `NNN` sequence,
  zero-padded 3-digit, per sub-PRD.
- **Immutability.** Once assigned and written, a `{PREFIX}-NNN` ID is
  never renumbered. Removed entries leave their ID with an explanatory
  `removed: [reason]` line rather than freeing the ID for reuse.

### §4.14 Cross-Page Impacts — relationship pointer register

§4.14 is a **relationship pointer register**, not a behaviour duplicator.
Structure:

- **Outbound impacts** — this sub-PRD changes something another page
  consumes.
- **Inbound impacts** — another sub-PRD changes something this page
  consumes.

Each entry references a **canonical behaviour entry** in the originating
sub-PRD by sub-PRD ID + requirement ID (e.g. `sub-prd-2 §4.2 CL-007`).
**Never duplicates** the behaviour text. This prevents fragmentation
across sub-PRDs.

### Mandatory "Not applicable" rule

Every unused §4 sub-section MUST appear in the document with an explicit
`Not applicable — [reason]` notice. No silent omissions. This applies even
to backend-heavy sub-PRDs where §4.5 UI may be N/A.

The §4 coverage map is declared at P2 exit (which sub-sections will be
active for the interview) and reconciled at the single conclusion gate
(declared map vs what was actually captured).

---

## §5 Data Migration — conditional (Option 5b)

- The heading **always appears**.
- Default body: `Not applicable — [reason]`.
- When triggered (the feature touches existing data, records, or
  calculation results), the body is free-form prose addressing:
  existing-data behaviour, calculation-result validity, one-time
  migration steps, historical-record categorisation.

---

## §6 Risks & Mitigations

Free-form, no fixed schema. PM authors risks and mitigations in prose.

---

## §7 Open Items & Ambiguities

Free-form, no fixed entry schema. Captures Deferred Items (DI-NNN) that
remained `Accepted` at the single conclusion gate plus any ambiguity-scan
deferrals.

---

## §8 Related Artefacts — each pointer carries a freshness status

Pointers carry a `FRESH` / `STALE` / `MISSING` status derived from
`prd-stale-check`. The pointer table includes:

- `acceptance-criteria.md`
- `component-spec.md`
- `demos/demo-interactive.html` (and `demos/calculation-demo.html` if
  applicable)
- `demos/demo-behavior-manifest.md`, `demos/demo-coverage.md`,
  `demos/_summary.md`
- `sample-data/*.json`, `sample-data/_summary.md`
- `reuse-map-draft.md`
- `traceability.md`
- `component-pattern-confirmation.md`
- `bundle-manifest.json`
- the prd-breakdown reference (`prd-breakdown.[sub-prd-id].md`)

A FRESH status means the derivative's `prdHash` header matches the current
SHA-256 of `prd.md` body content. STALE means it does not. MISSING means
the file does not exist (or carries `[COMPUTATION_FAILED]`).

---

## Version History — binding attribution rules

Every entry MUST carry:

- **Date** in `DD-MMM-YYYY` format.
- **Author** — full name. PM name for PM-authored edits; agent name
  (e.g. `prd-interviewer`, `prd-amend`) for agent-authored deltas.
- **Change summary** — a concrete delta, not "updated file".

PM edits and agent edits MUST be distinguishable from the author field
alone. No anonymous entries, no "various" authorship, no placeholder
authors.

---

## L4 sub-lock 1 — Acceptance Criteria sibling

- AC lives in `acceptance-criteria.md` as a **sibling file**. No AC text
  inline in `prd.md`.
- AC ID format: **sequential `AC-NNN` (zero-padded 3-digit). No buckets.**
  The legacy bucketed format `AC-{REQ|EC|UI|ERR}-NNN` is **explicitly
  retired** (PM rejected). Category lives in the `surface` field of each
  AC entry.
- Each AC carries: `id`, `linked_requirement_ids` (one or more §4.NNN),
  Given/When/Then/eXample (GWTX), `surface` (`UI` / `calc` / `data` /
  `error`), `demoable` flag.
- **Bidirectional invariant:** every AC links to ≥1 §4.NNN; every §4.NNN
  links to ≥1 AC. Validated at P8 derivation and again by
  `traceability-reviewer` downstream.
- Appendix B (terminology / glossary) lives in `acceptance-criteria.md`,
  not in `prd.md`.
- `prdHash` header at top of `acceptance-criteria.md` per the unnumbered
  preamble rule above.

### Legacy bucketed AC backfill-on-touch

Pre-lift sub-PRDs continue with their existing bucketed layout until next
touched. On next touch, the bundle migrates fully: PRD rewritten against
the 8-section schema; AC IDs renumbered from `AC-{REQ|EC|UI|ERR}-NNN` to
sequential `AC-NNN` with `surface` field added; `prdHash` headers added
to every derivative. Downstream consumers carry dual-layout read logic
(old bucketed vs new sequential) until every active sub-PRD has been
touched once post-lift, then dual-logic is removed. Migration recorded
in PRD §8 Related Artefacts version history.

---

## L4 sub-lock 2 — Demo posture classification

Four distinct postures, each with its own quality bar. Posture is picked
by the interviewer flow and recorded in the demo brief; the handoff chat
has **zero discretion** to switch.

1. **AC-driven scenario theater** — dark glass-panel; scenario selector +
   AC sidebar; each AC has a visible state in the demo; production styling
   but not a production-page replica. Use when AC count is moderate and
   scenarios are discrete.
2. **AC bar atop production page** — full production-fidelity page with a
   collapsible AC overlay bar. Use when the feature is a single page with
   many AC and PM wants production fidelity.
3. **Production page replica, no AC overlay** — pure production-fidelity
   replica, no AC instrumentation. Use when the demo's job is "show the
   surface" and AC are tracked elsewhere.
4. **Calculation-demo theater** — multi-mode header
   (`Walkthrough | Interactive | Reference Data | Run All`); three-column
   layout (260px scenario sidebar | center main | 340px audit/detail
   panel); real JS engine; worked examples. Ships **in addition to** a UI
   demo when calculation is in scope.

Demos MUST cite the appropriate component YAML(s) under
`.context/components/` per the application-fidelity hard rule (Family M).
"No application equivalent — generator's choice" surfaces MUST be flagged
explicitly in the brief. No silent gaps.

---

## Section-number stability map (consumers — informational)

The numbers and §4 ID prefixes above are referenced by:

| Consumer | Reads | Wired in |
|---|---|---|
| `prd-completeness-check` | §1–§8 + every §4 sub-ID prefix + Anchor Attestation dimension | Phase D (9 scoring dimensions) |
| `dev-interview` Step 0 | `acceptance-criteria.md` (AC-NNN), `component-spec.md`, `demos/demo-interactive.html`, `demos/_summary.md` — via `bundle-manifest.json` | Phase 8 |
| `traceability-reviewer` Step 1 | `acceptance-criteria.md`, `prd.md` §4, `traceability.md`; bidirectional invariant | Phase 8 |
| `orchestrator` TDD-spec gen | `acceptance-criteria.md` (primary AC source) | Phase 8 |
| `prd-stale-check` | All derivative `prdHash` headers vs current `prd.md` SHA-256; reads `bundle-manifest.json` for derivative list | Phase 8 |
| `prd-amend` | `stale-check.md`, `prd.md`, affected briefs; inherits Family N anchor extraction | Phase 8 |
| `prd-walkthrough` | Three `_summary.md` files + spot-reads on PM challenge; reads `bundle-manifest.json` | Phase 8 |
| `kickoff-dev-review` | `prd.md`, `acceptance-criteria.md`, `component-spec.md`, `bundle-manifest.json` | Phase 8 (new in contract) |
| `phase-splitter` | `prd.md`, `acceptance-criteria.md`, `component-spec.md`, `traceability.md`, `bundle-manifest.json`; uses §4.NNN coverage to score candidates | Phase 8 (new in contract) |

When any consumer changes its read path, this table is updated; the
section numbers and ID prefixes remain stable.

---

## Legacy 15-section schema — historical

This schema **supersedes** the pre-L1–L12 numbered 1..15 layout (Plain-
English Description, Triggering Conditions, Business Rules, User-Facing
Flows, Scope, Reuse Decisions, Related Sub-PRDs, Dependencies, Data
Migration, AC Reference, Demo Reference, Sample Data Reference, Risks &
Assumptions, Open Items, Ambiguity Scan Results). Pre-lift sub-PRDs
continue under the legacy schema until next touched (backfill-on-touch);
downstream consumers carry dual-layout read logic during the migration
window. See "Legacy bucketed AC backfill-on-touch" above for the full
migration policy.

The legacy 1..15 numbering is retained here as a back-compat reference
only and MUST NOT be cited by new artefacts. New sub-PRDs use the
8-section + 14 §4 prefix schema exclusively.
