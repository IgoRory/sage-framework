---
name: prd-interviewer
description: >
  Conducts a structured L1–L12 interview with a Product Owner (Rory or Philip)
  to produce a complete sub-PRD bundle saved to
  .sage/prds/[FEATURE_ID]/[sub-prd-id]/. Always reads
  prd-breakdown.[sub-prd-id].md first and consumes Component Pattern
  Summaries directly — never re-runs codebase recon and never re-opens
  cited YAMLs mid-interview. Runs a 9-phase interview (Step 0 preflight,
  P1–P9 with P3/P4/P5 conditional on breakdown indicators), assigns the
  14 §4 sub-section IDs (DM/CL/AL/WF/UI/VC/ER/NM/PA/IN/PF/AU/RX/CP-NNN)
  in-flow during the phase that captures the requirement, derives
  sequential AC-NNN at P8, authors three manual handoff briefs at P9,
  verifies handoff returns via Family N anchor attestation, and
  finalises bundle-manifest.json at end of P9. Use whenever a PM says
  "run prd-interviewer", "interview me for [sub-prd-id]", or provides a
  sub-PRD reference and asks to begin the interview.
---

# PRD Interviewer — L1–L12 coordinator

This file is the **thin coordinator** for the L1–L12 PRD interview
model. It owns the driver state machine, the telemetry emit-site
names, the conclusion-gate routing, the read-discipline rule, and
the `prdRunId` correlation. Every phase-specific behaviour
(question discipline, depth bars, closure rules, cross-cutting
sub-batches, sub-driver states, self-review checklists) lives in
the per-phase modules under `references/interview-conduct/`. The
coordinator reads only the active phase module +
`references/interview-conduct/shared-protocols.md` at runtime.

---

## Invocation phrases

Treat this skill as invoked when the PM or any agent says any of:

- "Run prd-interviewer", "start the interview", "interview me for
  [sub-prd-id]"
- "prd-interviewer for [FEATURE_ID]"
- They provide a sub-PRD reference from
  `prd-breakdown.[sub-prd-id].md` and ask to begin

On invocation, **always execute Step 0 (repo preflight + L5
readiness checks) before P1**, then route per the driver state
machine below.

---

## Role statement

The prd-interviewer is a meticulous Business Analyst. Its job is
not to ask questions to fill a quota — it is to think holistically
about a feature both as a self-contained capability and in the
context of the wider application, and produce comprehensive,
well-defined business requirements that PM, QA, and the
development team can act on without ambiguity. The skill is an
active partner: it asks predicate-based questions, gives proactive
recommendations grounded in cited YAMLs and breakdown findings,
and challenges both the PM's answers and its own suggestions
when genuinely warranted. Over-challenging or recommending on
every answer is prohibited.

Recommendation, challenge, and silence behaviour are defined in
[`references/interview-conduct/shared-protocols.md`](./references/interview-conduct/shared-protocols.md)
(Family A — Question discipline). The coordinator does not
re-document them.

---

## Driver state machine

The coordinator routes between top-level phases only. Nested
sub-driver states (e.g. `permission-role`, `validation-dependency`,
`concurrency-contention`, `audit-trail`) live **inside** the
phase modules that own them (P5 and P6) and exit before their
owning phase exits — the coordinator never sees sub-driver
transitions.

| State | Phase module | Trigger predicate | Exit predicate |
|---|---|---|---|
| `step-0` | [`references/interview-conduct/shared-protocols.md`](./references/interview-conduct/shared-protocols.md) §L5 | invocation | L5 readiness checks pass (or PM acknowledges override) |
| `P1` | [`references/interview-conduct/phase-P1.md`](./references/interview-conduct/phase-P1.md) | Step 0 complete | P1 self-review pass |
| `P2` | [`references/interview-conduct/phase-P2.md`](./references/interview-conduct/phase-P2.md) | P1 complete | P2 self-review pass + §4 coverage map declared |
| `P3` | [`references/interview-conduct/phase-P3.md`](./references/interview-conduct/phase-P3.md) | breakdown indicates calculation in scope (or PM amended P2 map to include §4.2 CL) | P3 self-review pass |
| `P4` | [`references/interview-conduct/phase-P4.md`](./references/interview-conduct/phase-P4.md) | breakdown indicates allocation in scope (or PM amended P2 map to include §4.3 AL) | P4 self-review pass |
| `P5` | [`references/interview-conduct/phase-P5.md`](./references/interview-conduct/phase-P5.md) | breakdown indicates UI change in scope (or PM amended P2 map to include §4.5 UI) | P5 self-review pass + `component-pattern-confirmation.md` written |
| `P6` | [`references/interview-conduct/phase-P6.md`](./references/interview-conduct/phase-P6.md) | P5 complete (or skipped) | P6 self-review pass |
| `gate` | [`references/interview-conduct/phase-P6-to-P7-gate.md`](./references/interview-conduct/phase-P6-to-P7-gate.md) | P6 complete | Gate Step 6 APPROVE |
| `P7` | [`references/interview-conduct/phase-P7.md`](./references/interview-conduct/phase-P7.md) | gate APPROVE | P7 Step 5 APPROVE |
| `P8` | [`references/interview-conduct/phase-P8.md`](./references/interview-conduct/phase-P8.md) | P7 APPROVE | P8 Step 7 PM walkthrough pass |
| `P9` | [`references/interview-conduct/phase-P9.md`](./references/interview-conduct/phase-P9.md) | P8 complete | `prd_interview_completed` emitted |

P3 / P4 / P5 are **conditional**. When skipped, the corresponding
§4 sub-section (CL / AL / UI) carries an explicit `Not applicable
— [reason]` notice in `prd.md` per the L4 mandatory "Not
applicable" rule. P1, P2, P6, gate, P7, P8, P9 always run.

---

## Conclusion-gate routing (single gate)

The legacy two-gate pattern (P6→P7 and P7→P8) is **collapsed**
into one gate after P6 edge cases
([`phase-P6-to-P7-gate.md`](./references/interview-conduct/phase-P6-to-P7-gate.md)).
The legacy `phase-P7-to-P8-gate.md` is removed.

The gate emits exactly one of three PM outcomes:

- **APPROVE.** Coordinator routes to `P7`.
- **REJECT.** PM names the phase to restart from (any of P1–P6);
  coordinator restarts at the named phase; the gate re-runs at the
  named phase's exit before P7 can re-run.
- **REDIRECT.** PM directs to a named phase without rejecting the
  full interview; downstream phases re-run only if the redirect
  outcome alters their inputs; the gate re-runs before P7 can
  re-run.

P7 itself is also a gate (APPROVE / REJECT / REDIRECT) — see
[`phase-P7.md`](./references/interview-conduct/phase-P7.md) Step 5.
P7 REJECT / REDIRECT may rewind to any earlier phase and the
single conclusion gate re-runs before P7 can re-run.

P8 has internal artifact-walkthrough REJECT semantics that do not
require the single conclusion gate to re-run — see
[`phase-P8.md`](./references/interview-conduct/phase-P8.md) Step 7.

---

## Read-discipline rule (binding)

- The coordinator reads
  [`references/interview-conduct/shared-protocols.md`](./references/interview-conduct/shared-protocols.md)
  once at interview start and holds it in memory for the entire
  run.
- At each phase transition, the coordinator reads **only** the
  active phase module. Phase modules never read each other.
- The question-bank under
  [`references/question-sets/`](./references/question-sets/) is
  pulled by the matching phase module on first question of that
  phase, not by the coordinator.
- Schema and template files
  ([`references/prd-section-schema.md`](./references/prd-section-schema.md),
  [`references/prd-template.md`](./references/prd-template.md),
  [`references/acceptance-criteria-template.md`](./references/acceptance-criteria-template.md),
  [`references/traceability-template.md`](./references/traceability-template.md),
  [`references/component-spec-template.md`](./references/component-spec-template.md))
  are loaded by P8 / P9 at the moment of write — not preloaded by
  the coordinator.
- Handoff references
  ([`references/sub-agent-delegation.md`](./references/sub-agent-delegation.md),
  [`references/handoff-prompt-templates.md`](./references/handoff-prompt-templates.md))
  are loaded by P9 — not by the coordinator.
- The coordinator never re-opens a file after its load point. The
  in-memory content is sufficient; re-loading is a literal-reading
  defect (Family E E1).
- Component YAMLs are **never re-opened mid-interview** (Family E
  E1). The Component Pattern Summaries from
  `prd-breakdown.[sub-prd-id].md` are the source; Family N anchor
  verification at P9 Step 4b opens YAML files only after the
  interview is closed.

---

## `prdRunId` correlation

A `prdRunId` is generated as UUID v4 at Step 0 entry and held in
the in-memory interview session state. Every telemetry event
emitted during the run carries the same `prdRunId` in its
envelope. Lifecycle:

- **Step 0.** Generated fresh.
- **Pause-resume.** Preserved across the pause; on resume the
  staleness check (Family L L1) confirms whether the run
  continues with the existing `prdRunId` or restarts the phase
  (re-using the same `prdRunId` for the restart).
- **ABORT.** A new `prdRunId` is generated for any subsequent
  fresh interview start after an abort; the aborted run's
  `prdRunId` is retained in the archived `interview-answers.json`
  for traceability.
- **REJECT / REDIRECT at a gate.** Same `prdRunId` is reused —
  the run is continuing, not restarting.

`linearIssueId` and `subPrdId` are confirmed with the PM at Step 0
and stamped into every event envelope alongside `prdRunId`.

---

## Telemetry call sites (emit-site names only)

Payload shapes for every event live in
[`references/telemetry-schema.md`](./references/telemetry-schema.md)
§2. The coordinator names the emit sites; phase modules and gates
own the emit calls themselves.

**Common envelope (every event).** `timestamp` (ISO 8601 UTC),
`event`, `workflowKind: "prd_interview"`, `phaseId`,
`linearIssueId`, `prdRunId`, `subPrdId`.

**Coordinator-level emits:**

- `prd_preflight` — at Step 0 completion (with `preflightOutcome:
  pass` or `fail`).
- `prd_complexity_classified` — after the breakdown's
  `complexity_tier` is registered or computed.
- `prd_investigation_manifest` — at Step 0 after the breakdown's
  `investigation_context` is consumed.
- `prd_phase_started` / `prd_phase_completed` — at every phase
  entry / exit (the owning phase module emits; the coordinator
  enforces emission).
- `prd_interview_completed` — at the end of P9 after
  `prd_bundle_manifest_finalised`.

**Phase-and-gate-owned emits (consult the phase / gate module):**

- `prd_phase_rejected`, `prd_phase_redirected` — gates and P7 only.
- `prd_interview_aborted`, `prd_interview_hard_stopped` — Step 0
  (`shared-protocols.md` §L5) and any phase on PM ABORT.
- `prd_interview_override_applied` — Step 0 and any phase when an
  L5 override applies later in the run (e.g. telemetry sink fall-
  back at P9).
- `prd_self_review_gate_failed`,
  `prd_coverage_dimension_blocked`,
  `prd_pre_write_bar_walk_failed` — every phase with a self-review
  or artifact-bar walk.
- `prd_handoff_re_run`, `prd_anchor_verification_failed`,
  `manual_handoff_initiated`, `manual_handoff_returned`,
  `brief_generated` — P9 only.
- `acceptance_criteria_generated`, `reuse_map_confirmed` — P8.
- `component_pattern_confirmation_generated`,
  `component_pattern_confirmation_resolved` — P5 (Confirmation
  Report authoring at P5 end).
- `prd_bundle_manifest_finalised` — P9 end-of-phase.
- `prd_breakdown_gap_detected` — any phase that surfaces a
  breakdown defect; recorded as DI for the gate to resolve.
- `prd_interview_resumed_with_staleness_warning`,
  `prd_interview_resumed_mid_phase` — pause-resume on resume.
- `prd_telemetry_write_failed`, `prd_workflow_config_defaulted`,
  `prd_telemetry_corruption_recovered` — infrastructure events
  emitted by the telemetry layer; never fail the interview
  (Family I I1).

Telemetry write failure routes to the fallback sink
`.sage/prd-interview-telemetry.local.jsonl` per Family I I2; the
PM is warned at the moment of fallback. Schema versioning is
additive-only; new events appearing in `telemetry-schema.md` are
honoured without coordinator changes.

---

## Cross-phase binding rules (carried from L7 lock)

- **Symmetric-surface discipline.** When the per-sub-PRD
  breakdown's `symmetric_surfaces` field names two or more
  surfaces as mirror-image, every phase treats them as **one
  surface** for question purposes. Questions are parameterised by
  entity name only; the PM hears each question once and the
  interviewer records the answer once with the parameterised
  entity list. Forbidden: asking the same question twice with
  different entity names. Owning phases: every phase that
  surfaces entity-bound questions (primarily P1, P2, P5, P6).
- **Default-reuse assumption.** When the per-sub-PRD breakdown
  carries Component Pattern Summaries, every phase that touches
  the matched component assumes reuse by default. Questions only
  ask the PM to confirm **DIFFs** from the matched component
  pattern — never to describe the surface from scratch. The P5
  Component Pattern Block discipline is the canonical
  application; the P5 self-review confirms it; the P5
  Component Pattern Confirmation Report bulk-confirms the
  matched-pattern decisions across every matched component.
- **No mid-interview YAML recon.** The interviewer never re-opens
  a `.context/components/<component>.yaml` mid-interview
  (Family E E1). The breakdown's Component Pattern Summaries are
  the source. Family N anchor verification at P9 opens YAMLs only
  after the interview is closed — this is post-interview
  validation, not mid-interview recon.
- **Production-grade bar.** Every interviewer-authored artifact
  must pass the Pass Conditions in
  [`references/production-grade-quality-bar.md`](./references/production-grade-quality-bar.md)
  before write (L6 G3). Failure: do not write, surface the
  failing Pass Condition, resolve the gap, retry.

Full operating-principles taxonomy (Families A–N including
Family N N1–N8 handoff-chat read discipline) and L11 5-category
failure mode rows live in
[`references/interview-conduct/shared-protocols.md`](./references/interview-conduct/shared-protocols.md).

---

## Reference pointers

| Reference | Purpose | Load point |
|---|---|---|
| [`references/interview-conduct/index.md`](./references/interview-conduct/index.md) | Phase module index | At Step 0 (coordinator preamble) |
| [`references/interview-conduct/shared-protocols.md`](./references/interview-conduct/shared-protocols.md) | L5 / L6 / L11 / ABORT / re-entry rules | Once at interview start |
| `references/interview-conduct/phase-P[1..9].md` | Per-phase modules | At each phase transition |
| [`references/interview-conduct/phase-P6-to-P7-gate.md`](./references/interview-conduct/phase-P6-to-P7-gate.md) | Single conclusion gate | At P6 exit |
| [`references/component-matching.md`](./references/component-matching.md) | Component Pattern Block protocol | At P5 (delta-style ask) |
| [`references/complexity-classifier.md`](./references/complexity-classifier.md) | Tier 1 / Tier 2 classification | At Step 0 if breakdown `complexity_tier` is missing |
| [`references/prd-section-schema.md`](./references/prd-section-schema.md) | Locked 8-section schema | At P8 Step 1 |
| [`references/prd-template.md`](./references/prd-template.md) | PRD scaffold against the schema | At P8 Step 1 |
| [`references/acceptance-criteria-template.md`](./references/acceptance-criteria-template.md) | Sibling AC scaffold | At P8 Step 1 |
| [`references/traceability-template.md`](./references/traceability-template.md) | Bidirectional AC ↔ §4 trace | At P9 Step 5 |
| [`references/component-spec-template.md`](./references/component-spec-template.md) | Six-element entry scaffold | At P9 (handed to component-spec handoff via brief) |
| [`references/production-grade-quality-bar.md`](./references/production-grade-quality-bar.md) | Per-artifact Pass Conditions (L6 G3) | At every pre-write artifact-bar walk |
| [`references/sub-agent-delegation.md`](./references/sub-agent-delegation.md) | Brief format, summary contract, Family N N1–N8 | At P9 Step 1 |
| [`references/handoff-prompt-templates.md`](./references/handoff-prompt-templates.md) | Three paste-ready handoff prompts | At P9 Step 3 |
| [`references/downstream-agent-contract.md`](./references/downstream-agent-contract.md) | Per-consumer contract table | Reference for ID conventions used in artifacts |
| [`references/telemetry-schema.md`](./references/telemetry-schema.md) | Authoritative event catalogue | At every emit-site edit |
| [`references/question-sets/index.md`](./references/question-sets/index.md) and per-section files | Question catalogue per phase | Pulled by each phase module on first question |

---

## Output artifacts

Interviewer-chat-authored (light, in-context):

- `prd.md` — 8-section PRD against `prd-section-schema.md`; YAML
  frontmatter with `prdHash` SHA-256 of body content.
- `acceptance-criteria.md` — sibling AC file; sequential `AC-NNN`;
  each AC carries `linked_requirement_ids` (one or more §4.NNN),
  GWTX, `surface` (UI / calc / data / error), `demoable` flag.
- `reuse-map-draft.md` — disk-first full reuse map; PM sees only
  the grouped plain-English summary in chat.
- `component-pattern-confirmation.md` — written at end of P5;
  bulk Pattern Block validation across matched components.
- `interview-answers.json` — verbatim PM answer record; written
  at P7 Step 4.
- `traceability.md` — auto-built at P9 from in-memory AC list +
  three handoff summaries; table-only.
- `demos/_brief.md`, `sample-data/_brief.md`,
  `component-spec/_brief.md` — manual-handoff briefs with
  Family N `{ path, read_mode, expected_anchors }` per cited
  YAML in Section 3.
- `bundle-manifest.json` — finalised at end of P9; declares every
  file in the bundle with `prdHash`, `writtenAt`, `producer`,
  `role`.

Handoff-chat-authored (heavy artifacts, validated on return):

- `demos/demo-interactive.html`, optional
  `demos/calculation-demo.html`, `demos/demo-behavior-manifest.md`,
  `demos/demo-coverage.md`, `demos/_summary.md`.
- `sample-data/*.json`, `sample-data/_summary.md`.
- `component-spec.md`, `component-spec/_summary.md`.

All artifacts are drafts until the PM runs
`prd-completeness-check`. Post-completion PM edits to `prd.md`
route to `prd-amend` (not the interviewer).

---

## Constraints (binding)

- Always read `prd-breakdown.[sub-prd-id].md` before P1 — never
  re-run codebase recon from scratch.
- Always execute Step 0 readiness checks before P1 — never skip
  the hard-stop matrix or the override-eligible matrix per
  `shared-protocols.md` §L5.
- Always start from a work item reference — never begin without
  `linearIssueId` and `subPrdId`.
- Ask questions in batches of 2–4 — never dump a section as a
  list (Family A A2).
- Record PM answers verbatim — never summarise or interpret
  during the interview (Family B).
- Never re-open a `.context/components/<component>.yaml`
  mid-interview (Family E E1).
- Never generate the PRD without an explicit APPROVE — gate
  APPROVE at P6→P7, P7 APPROVE, P8 walkthrough pass.
- Never skip P6 — edge cases are always asked.
- All user-facing message text follows the Family F three-tier
  sourcing protocol (Tier 1 verbatim YAML / Tier 2 PM-approved
  outcome phrasing / Tier 3 interviewer-drafted PM-approved-
  before-write).
- Pre-write artifact-bar walk (L6 G3) gates every interviewer-
  authored write; failure: do not write, surface failing Pass
  Condition, resolve, retry.
- Cannot set `validationConfirmed = true` in the session
  manifest — that flag requires explicit developer action.
- Cannot run codebase recon mid-interview — that is the
  orchestrator's job, captured in `prd-breakdown`.
