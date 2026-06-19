---
name: prd-stale-check
description: >
  Detects drift between a sub-PRD and its derivative artefacts
  (component-spec, acceptance-criteria, traceability, demos, sample-data)
  by comparing embedded prdHash headers against the current SHA-256 of
  prd.md. Writes a stale-check report to the sub-PRD folder. Read-only —
  never regenerates artefacts. Use before prd-amend or before planning.
---

# PRD Stale Check

Detects drift between a sub-PRD (`prd.md`) and every derivative artefact
that carries an embedded `prdHash` header. When the PM edits the PRD after
derivatives have been generated, the derivative hashes no longer match the
current PRD — those derivatives are **STALE** and may misrepresent the
amended requirements. This skill surfaces exactly which derivatives are
stale so the PM can decide whether to invoke `prd-amend`.

**Read-only.** This skill never edits or regenerates any artefact. It
diagnoses; the PM decides.

---

## Inputs required

| Input | Source | Required |
|---|---|---|
| PRD | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/prd.md` | Yes |
| Bundle manifest (derivative inventory + per-file `prdHash`) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/bundle-manifest.json` | Yes (new-format bundles); legacy disk-walk fallback during the backfill-on-touch window |
| Component specification | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/component-spec.md` | Yes (check `prdHash` header) |
| Acceptance criteria | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/acceptance-criteria.md` | Yes (check `prdHash` header) |
| Traceability | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/traceability.md` | Yes (check `prdHash` header) |
| Demo summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_summary.md` | Yes (check `prdHash` header) |
| Demo behaviour manifest | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-behavior-manifest.md` | Yes (check `prdHash` header) |
| Sample-data summary | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/sample-data/_summary.md` | Yes (check `prdHash` header) |

**L1–L12 contract — bundle discovery via `bundle-manifest.json`.** For
new-format bundles (post-lift), the derivative inventory that this skill
walks is taken from `bundle-manifest.json` (finalised by the interviewer
at end of P9). The manifest's `files[]` array names every derivative
that belongs to the bundle along with the `prdHash` it was written
against. This skill iterates that array — it does not heuristically
discover files on disk. If a file is listed in the manifest but absent
on disk, classify it as **MISSING**; if a file is present on disk but
absent from the manifest, surface as an advisory at the bottom of the
stale-check report (do not score) — the manifest is the authoritative
file list per the L10 contract.

**Legacy layout (backfill-on-touch fallback):** For pre-lift bundles
where `bundle-manifest.json` does not exist, accept the legacy disk-walk
of the Inputs table above (`.sage/prds/[FEATURE_ID]/prd.md` and sibling
derivatives in the same folder) and apply the same per-file `prdHash`
comparison logic. Dual-layout reads remain available until every active
sub-PRD has been touched once post-lift; once the last legacy bundle
migrates the disk-walk path may be removed.

---

## Outputs

One file written per run:

| Output | Path |
|---|---|
| Stale-check report | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/stale-check.md` |

The report lists every derivative with one of three statuses:

- **FRESH** — the derivative's embedded `prdHash` matches the current
  SHA-256 of `prd.md`. No action needed for this derivative.
- **STALE** — the hash mismatches. The PRD was edited after the
  derivative was generated. Section delta information is included where
  computable (see Step 3).
- **MISSING** — the derivative file does not exist at its expected path.

---

## Steps

### Step 1 — Read inputs and emit `prd_stale_check_started`

1. Confirm the `featureId` and `subPrdId` (or ask the PM if not provided
   in the invocation phrase).
2. Read `prd.md` in full.
3. Read all seven derivative artefacts listed in the Inputs table.
   For each: if the file does not exist, record it as **MISSING** and
   do not attempt to read it.
4. Emit telemetry `prd_stale_check_started`:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_stale_check_started",
  "workflowKind": "prd_stale_check",
  "prdRunId": "<reuse the prdRunId embedded in the PRD front-matter if present; otherwise generate a new UUID v4>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "prdPath": ".sage/prds/<FEATURE_ID>/<sub-prd-id>/prd.md"
}
```

### Step 2 — Compute the SHA-256 of prd.md

Compute the SHA-256 digest of the full content of `prd.md` as a
lowercase hex string. This is the **current hash**.

> **Implementation note for the AI:** You cannot execute shell commands
> during a chat turn. Derive the SHA-256 conceptually from the full
> file content you have already read. Document in the report that the
> hash is computed at read-time and is valid for the exact file content
> read in Step 1. If the PM later modifies `prd.md`, a new stale-check
> run is required.

### Step 3 — Compare derivative hashes; classify each artefact

For each derivative artefact that exists (status not MISSING):

1. Parse the embedded `prdHash` header. The header convention (locked
   Phase C) is a comment or front-matter line in the first 10 lines
   of the file in one of these forms:
   - `<!-- prdHash: <hex> -->` (HTML artefacts)
   - `prdHash: <hex>` (Markdown front-matter or first-line comment)
   - `# prdHash: <hex>` (leading comment)
   If no `prdHash` header is found, classify the artefact as **STALE**
   with the note `prdHash header absent — treat as stale`.

2. Compare the extracted hash to the current hash from Step 2:
   - Match → **FRESH**
   - Mismatch → **STALE**

3. For **STALE** artefacts, produce a section delta note:
   - If you can identify which sections of `prd.md` differ from the
     version that produced the old hash (e.g., the PRD carries a
     revision history or the derivative's summary references specific
     PRD sections), name those sections explicitly in the report.
   - If a section-level delta cannot be determined from the available
     context, record only the artefact-level mismatch:
     `Section delta: unable to compute — prd.md revision history
      not present or PRD sections not cited in derivative`.

### Step 4 — Write stale-check.md and emit `prd_stale_check_completed`

Write `.sage/prds/[FEATURE_ID]/[sub-prd-id]/stale-check.md` using the
template below. Then emit telemetry.

**Report template:**

```markdown
# PRD Stale Check Report

**Feature:** <FEATURE_ID>
**Sub-PRD:** <sub-prd-id>
**Run timestamp:** <ISO 8601 UTC>
**Current PRD hash (SHA-256):** <hex>

## Summary

| Derivative | Status | Note |
|---|---|---|
| component-spec.md | FRESH / STALE / MISSING | <section delta or hash-absent note> |
| acceptance-criteria.md | FRESH / STALE / MISSING | <note> |
| traceability.md | FRESH / STALE / MISSING | <note> |
| demos/_summary.md | FRESH / STALE / MISSING | <note> |
| demos/demo-behavior-manifest.md | FRESH / STALE / MISSING | <note> |
| sample-data/_summary.md | FRESH / STALE / MISSING | <note> |

**Fresh:** N  **Stale:** N  **Missing:** N

## Stale derivative details

<For each STALE derivative, a subsection with the derivative path,
the stored prdHash, the current PRD hash, and the section delta
note. Omit this section entirely if all derivatives are FRESH.>

## Recommended action

<If staleCount > 0 or missingCount > 0: suggest the PM run
`prd-amend` to regenerate affected derivatives, naming exactly
which surfaces are affected. If all FRESH: state no action needed.>
```

After writing the report, emit telemetry `prd_stale_check_completed`:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "event": "prd_stale_check_completed",
  "workflowKind": "prd_stale_check",
  "prdRunId": "<same as Step 1>",
  "featureId": "<FEATURE_ID>",
  "subPrdId": "<sub-prd-id>",
  "freshCount": <N>,
  "staleCount": <N>,
  "missingCount": <N>,
  "derivatives": [
    { "path": "component-spec.md", "status": "fresh" },
    { "path": "acceptance-criteria.md", "status": "stale" },
    ...
  ]
}
```

Status values in the `derivatives` array are lowercase: `"fresh"`,
`"stale"`, `"missing"`.

---

## Telemetry

This skill appends to the PRD telemetry stream. Emitter and event
contracts are defined in
`skills/prd-interviewer/references/telemetry-schema.md` §4
(Supporting-skill events). The two events this skill emits are:

| Event | Emitted at |
|---|---|
| `prd_stale_check_started` | Step 1 entry, after inputs are read |
| `prd_stale_check_completed` | Step 4 close, after `stale-check.md` is written |

`workflowKind` for both events: `"prd_stale_check"`.

---

## Constraints

- **Read-only.** Never modifies `prd.md`, any derivative artefact, or
  any application source file.
- **Never regenerates derivatives.** Diagnosis only. To regenerate STALE
  derivatives, the PM invokes `prd-amend`.
- **One run per invocation.** After writing `stale-check.md` and emitting
  `prd_stale_check_completed`, STOP. Do not proceed to `prd-amend`
  automatically — the PM decides.
- Inherits the production-grade quality bar from
  `skills/prd-interviewer/references/production-grade-quality-bar.md`.

---

## Reference files

| File | Purpose |
|---|---|
| `skills/prd-interviewer/references/telemetry-schema.md` | Telemetry event contracts |
| `skills/prd-interviewer/references/production-grade-quality-bar.md` | Quality bar inherited by this skill |
| `skills/prd-amend/SKILL.md` | Skill to invoke for regenerating STALE derivatives |
