# PRD Telemetry Schema

**Status:** Authored Phase D of the PRD Pipeline Production-Grade Lift,
25-MAY-2026. Single source of truth for every event appended to the PRD
telemetry stream.

**Telemetry file:** path resolved from `.sage/workflow-config.json` key
`prd.telemetryFile`; default `.sage/prd-interview-telemetry.jsonl`.

**Emitter:** `python .cursor/hooks/scripts/prd_telemetry_append.py '<json>'`.
The script accepts any JSON object — no event-name allow-list — so the
schema is authoritative, not enforced at the script layer. Schema drift
must be caught at code review.

---

## Common envelope

Every event MUST carry the four envelope fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `timestamp` | string (ISO 8601 UTC, e.g. `2026-05-25T11:30:00Z`) | Yes | Emit time |
| `event` | string | Yes | Event name (one of the entries below) |
| `prdRunId` | string (UUID v4) | Yes | Identifies the PRD-run scope; orchestrator generates it at Step 0 and the interviewer reuses it for the matched sub-PRD |
| `workflowKind` | string | Yes | One of `prd_orchestrator`, `prd_interviewer`, `completeness_check`, `prd_stale_check`, `prd_amend`, `prd_walkthrough` |

Most events also carry one or more of these contextual fields when
applicable:

| Field | Type | When present |
|---|---|---|
| `linearIssueId` | string | Orchestrator and interviewer events; identifies the feature work item |
| `featureId` | string | Completeness-check events; identifies the PRD feature folder |
| `subPrdId` | string | Any per-sub-PRD event |
| `phaseId` | string (`pre-Step-0`, `Step 0`, `P1`–`P9`, `Gate`) | Interviewer phase events |

If a payload is missing a field listed as required for that event, the
event is malformed and the effectiveness-evaluator must surface it as a
schema-drift signal.

---

## Event status legend

| Status | Meaning |
|---|---|
| `emitted` | Currently emitted by the named emitter as of Phase D close |
| `planned` | Event documented in the schema but emit-site not yet wired (deferred to a later phase) — the schema is authoritative once a planned event lands |

Phase D wires four `planned` events into `emitted` state via the emit
calls added in Phase D scope item 4 (see §3 below).

---

## 1. Orchestrator events

Emitter: `.cursor/skills/prd-orchestrator/SKILL.md`. All carry
`workflowKind: "prd_orchestrator"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `prd_preflight` | emitted | Step 0 outcome — repo preflight pass / fail | `linearIssueId`, `preflightOutcome: "pass" \| "fail"`, `failureReasons?: string[]` | prd-interviewer-effectiveness-evaluator (preflight discipline pattern) |
| `prd_investigation_manifest` | emitted | After Step 2 silent recon completes; **also re-emitted** after a Step 2 amendment (Phase B Ruling 9) with `event_qualifier: "amendment"` | `linearIssueId`, `filesRead: { frontend: string[], services: string[], models: string[], sps: string[], views: string[], tests: string[] }`, `event_qualifier?: "amendment"` | prd-interviewer-effectiveness-evaluator (read-coverage signal); out-of-band PM audit |
| `prd_complexity_classified` | emitted | Per sub-PRD after the breakdown classifier scores it | `linearIssueId`, `subPrdId`, `complexityTier: 1\|2\|3+`, `factors: object` | prd-interviewer-effectiveness-evaluator (tier-3+ should never reach interview) |
| `prd_breakdown_proposed` | emitted | When breakdown is presented to PM | `linearIssueId`, `subPrdCount: number`, `surfaceCount: number` | out-of-band PM audit |
| `prd_breakdown_confirmed` | emitted | When PM confirms the breakdown | `linearIssueId`, `subPrdCount: number` | out-of-band PM audit |
| `summary_cap_exceeded` | emitted | When a Component Pattern Summary exceeds the 80-line hard cap and a `see_full_yaml` pointer is emitted instead (Phase B T2) | `subPrdId`, `componentId: string`, `yamlFile: string`, `attemptedLineCount: number`, `sourceYamlLineCount: number`, `compressionRatio: number` | prd-interviewer-effectiveness-evaluator (low ratio → format bloated; high ratio → raise cap) |

The `prd_complexity_classified` event is listed in Phase B's Ruling
table only by reference; the orchestrator's classifier is the emit
site. If a future audit finds the event absent at the emit site, that
is an orchestrator gap, not a schema gap.

---

## 2. Interviewer events

Emitter: `.cursor/skills/prd-interviewer/SKILL.md`. All carry
`workflowKind: "prd_interviewer"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `prd_preflight` | emitted | Step 0 interviewer-side preflight (distinct from the orchestrator's preflight; both carry the same event name with different `workflowKind`) | `linearIssueId`, `subPrdId`, `preflightOutcome: "pass" \| "fail"`, `failureReasons?: string[]` | prd-interviewer-effectiveness-evaluator (preflight discipline pattern) |
| `prd_phase_started` | emitted | At the start of each interview phase P1..P9 | `linearIssueId`, `subPrdId`, `phaseId: "P1"..."P9"` | prd-interviewer-effectiveness-evaluator (phase coverage; duration) |
| `prd_phase_completed` | emitted | At the close of each interview phase P1..P9 | `linearIssueId`, `subPrdId`, `phaseId: "P1"..."P9"`, `questionCount?: number`, `deferredCount?: number` | prd-interviewer-effectiveness-evaluator (phase coverage; duration; abandonment) |
| `prd_interview_completed` | emitted | End of P9 — emitted after the bundle-manifest is finalised and on-return handoff verification is complete (L12 Q2=2a phase renumbering) | `linearIssueId`, `subPrdId`, `phaseSummary: object`, `deferredItemsFinalCount: number` | prd-interviewer-effectiveness-evaluator (eligibility — ≥ 3 distinct interviews) |
| `acceptance_criteria_generated` | emitted | P8 — after the sibling `acceptance-criteria.md` is written (L12 Q2=2a renumbering: was Step 4c P9) | `subPrdId`, `counts: { REQ: number, EC: number, UI: number, ERR: number }` (legacy bucketed counts during dual-layout backfill window; post-migration the payload carries `{ total: number, bySurface: { UI: number, calc: number, data: number, error: number } }`) | prd-interviewer-effectiveness-evaluator (AC coverage); prd-completeness-check (informational) |
| `reuse_map_confirmed` | emitted | P8 — after the disk-first `reuse-map-draft.md` is written (L12 Q2=2a renumbering: was Step 4d P9) | `subPrdId`, `rowCount: number`, `groupedSummaryShown: true`, `pmOverrideCount?: number` | prd-interviewer-effectiveness-evaluator (default-reuse calibration). `pmOverrideCount` is the count of rows where the PM rejected the default-reuse pattern; emitted as `0` when the PM accepted the grouped summary verbatim |
| `brief_generated` | emitted | Once per surface, end of P8 — three events per sub-PRD (L12 Q2=2a renumbering: was Step 4f P9) | `subPrdId`, `surface: "demo" \| "sample-data" \| "component-spec"`, `briefPath: string`, `citedYamlCount: number` | prd-interviewer-effectiveness-evaluator (brief-quality signal) |
| `manual_handoff_initiated` | emitted | End-of-P8 / start-of-P9 — when the paste-ready prompt is handed to the PM. **NOTE:** The mechanism is a manual chat handoff. The event name reflects this directly. The payload's `mode: "manual_handoff"` is retained as a payload-level confirmation. | `subPrdId`, `surface: "demo" \| "sample-data" \| "component-spec"`, `mode: "manual_handoff"`, `briefPath: string` | prd-interviewer-effectiveness-evaluator (handoff initiation signal) |
| `manual_handoff_returned` | emitted | Mid-P9 — each handoff returns separately when the interviewer reads the corresponding `_summary.md` after the PM confirms the handoff chat stopped. **NOTE:** The mechanism is a manual chat handoff. The event name reflects this directly. The payload's `mode: "manual_handoff"` is retained as a payload-level confirmation. | `subPrdId`, `surface: "demo" \| "sample-data" \| "component-spec"`, `summaryPath: string`, `ambiguityFlagCount: number`, `deviationCount: number` | prd-interviewer-effectiveness-evaluator (`deviationCount > 0` → brief quality signal) |
| `ambiguity_flag_raised` | emitted | Once per ambiguity flag in any of the three `_summary.md` files (zero or more per surface) | `subPrdId`, `surface: "demo" \| "sample-data" \| "component-spec"`, `flag: string` | prd-interviewer-effectiveness-evaluator (ambiguity surfacing pattern) |
| `component_pattern_confirmation_generated` | emitted | End of P5 — after `component-pattern-confirmation.md` is written (L8 lock moved this artefact from P9 to end-of-P5) | `subPrdId`, `decisionsCount: number`, `filePath: string` | prd-interviewer-effectiveness-evaluator (volume of pattern decisions per sub-PRD) |
| `component_pattern_confirmation_resolved` | emitted | Immediately after the PM bulk-confirms the Component Pattern Confirmation Report (or finishes resolving DIFFs) — at end of P5 closure | `subPrdId`, `decisionsTotal: number`, `decisionsPmConfirmedAsIs: number`, `decisionsPmOverridden: number`, `filePath: string` | prd-interviewer-effectiveness-evaluator (default-pattern miscalibration: high override rate → pattern detection too aggressive) |
| `ambiguity_scan_completed` | emitted | P8 — immediately before PRD draft generation (L12 Q2=2a renumbering: previously "end of Step 4a P9"; now firmly inside P8 after the single conclusion gate) | `subPrdId`, `qualifiersFoundCount: number`, `qualifiersResolvedCount: number`, `unresolvedMarkersCount: number`, `qualifiers: { qualifier: string, resolution: "clarified" \| "confirmed-acceptable" \| "tracked-as-DI-NNN" }[]` | prd-interviewer-effectiveness-evaluator (unresolved markers > 0 → interviewer not driving ambiguity to resolution) |

---

## 2.A New interviewer events (L11 / L12 — 16 events + bundle-finalisation)

The events below extend Section 2's interviewer-event catalogue. Each
is presented as a structured block rather than a markdown table because
several payload enums contain pipe characters that would conflict with
table syntax.

Common envelope (`timestamp`, `event`, `prdRunId`, `workflowKind`)
applies to all events below. `workflowKind` is always
`"prd_interviewer"`.

### Event 1 — `prd_interview_aborted`

- **Status:** emitted
- **Trigger:** ABORT path (Family L11 ABORT) — interview cannot continue;
  partial bundle is archived and the sub-PRD folder is deleted.
- **Payload:** `subPrdId`, `phaseAtAbort` (enum: `pre-Step-0`, `P1`,
  `P2`, `P3`, `P4`, `P5`, `P6`, `Gate`, `P7`, `P8`, `P9`), `reason`,
  `deferredItemsCount`, `archivePath?` (omitted for pre-Step-0 aborts —
  nothing to archive)
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (abort rate);
  `session-performance-evaluator` (systemic patterns)

### Event 2 — `prd_interview_hard_stopped`

- **Status:** emitted
- **Trigger:** Step 0 hard-stop categories (no override possible) —
  breakdown missing/unparseable, sub-PRD ID not in breakdown, wrong
  branch, dirty tree.
- **Payload:** `subPrdId?`, `hardStopReason` (enum: `breakdown_missing`,
  `subprd_not_in_breakdown`, `wrong_branch`, `dirty_tree`,
  `breakdown_malformed`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (Step 0
  discipline pattern)

### Event 3 — `prd_phase_rejected`

- **Status:** emitted
- **Trigger:** PM responds REJECT at a per-phase conclusion gate
  (Family D D3).
- **Payload:** `subPrdId`, `phaseId`, `rejectionReason`,
  `restartPhaseId`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (per-phase
  REJECT rate)

### Event 4 — `prd_phase_redirected`

- **Status:** emitted
- **Trigger:** PM responds REDIRECT at a per-phase conclusion gate or
  the single conclusion gate (Family D D4).
- **Payload:** `subPrdId`, `fromPhaseId`, `toPhaseId`, `redirectReason`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (phase
  ordering signal)

### Event 5 — `prd_handoff_re_run`

- **Status:** emitted
- **Trigger:** Interviewer re-runs a handoff per Family C C1, C2, C4,
  C6, C7, or C8 (deviations rejected, anchor mismatch, extra files,
  handoff self-stopped, summary-schema non-conforming, recurring
  re-handoff).
- **Payload:** `subPrdId`, `surface` (enum: `demo`, `sample-data`,
  `component-spec`), `rerunReason` (enum: `deviation_rejected`,
  `anchor_mismatch`, `summary_schema_invalid`,
  `handoff_self_stopped`, `extra_files`), `briefPath`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (handoff
  stability)

### Event 6 — `prd_anchor_verification_failed`

- **Status:** emitted
- **Trigger:** Family N anchor verification on PM return finds at
  least one `anchors_extracted` value that does not match the cited
  YAML.
- **Payload:** `subPrdId`, `surface`, `mismatchType` (enum:
  `structural`, `copy`, `yaml_vs_pm_contradiction`, `cosmetic`),
  `resolution` (enum: `tighter_brief`, `orchestrator_escalate`,
  `accept_as_open_item`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (brief
  defect rate)

### Event 7 — `prd_interview_override_applied`

- **Status:** emitted
- **Trigger:** Step 0 override-eligible category applied per Family L5,
  OR pre-lift bundle migration triggered per the backfill-on-touch
  rule.
- **Payload:** `subPrdId`, `overrideType` (enum:
  `thin_pattern_summaries`, `manifest_stale`, `yaml_missing`,
  `telemetry_sink_unavailable`, `many_citations_stale`,
  `pre_lift_migration`), `justification`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (recon
  weakness); `session-performance-evaluator` (systemic)

### Event 8 — `prd_self_review_gate_failed`

- **Status:** emitted
- **Trigger:** Family G self-review gate fails (G1 L1 per-phase
  self-review, G2 L3 coverage-dimension blocking, or G3 L5 pre-write
  artifact-bar walk).
- **Payload:** `subPrdId`, `gateLevel` (enum: `L1`, `L3`, `L5`),
  `phaseId`, `failedChecklistItem`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (gate
  calibration)

### Event 9 — `prd_coverage_dimension_blocked`

- **Status:** emitted
- **Trigger:** Coverage-dimension blocking gate (Family G G2) fails —
  a required dimension cannot reach 100% without DI tracking.
- **Payload:** `subPrdId`, `dimension`, `phaseId`
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (which
  dimensions block most often)

### Event 10 — `prd_pre_write_bar_walk_failed`

- **Status:** emitted
- **Trigger:** Pre-write artifact-bar walk (Family G G3) fails — a
  Pass Condition in `production-grade-quality-bar.md` is unmet.
- **Payload:** `subPrdId`, `failedPassCondition`, `artifact` (enum:
  `prd`, `ac`, `reuse-map`, `component-pattern-confirmation`,
  `traceability`, `demo-brief`, `sample-data-brief`,
  `component-spec-brief`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (which Pass
  Conditions breach most often)

### Event 11 — `prd_breakdown_gap_detected`

- **Status:** emitted
- **Trigger:** Mid-interview recon gap discovered (Family B B6) — the
  breakdown is missing a fact the interviewer needs. Family E E1
  forbids patching by re-reading YAMLs; the gap is recorded as a DI
  with category `breakdown-defect`.
- **Payload:** `subPrdId`, `gapType`, `recordedAs` (string of the form
  `DI-NNN`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator`
  (orchestrator quality signal)

### Event 12 — `prd_interview_resumed_with_staleness_warning`

- **Status:** emitted
- **Trigger:** Pause-resume per Family L — interview was paused >14
  days. On resume, the interviewer confirms context freshness with
  the PM (Family L1).
- **Payload:** `subPrdId`, `pauseDurationDays`, `staleConfirmOutcome`
  (enum: `fresh_context`, `phase_restart`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator` (staleness
  pattern)

### Event 13 — `prd_interview_resumed_mid_phase`

- **Status:** emitted
- **Trigger:** Resume of an interview that was previously interrupted
  mid-phase — the interviewer re-hydrates state from
  `interview-answers.json` or `bundle-manifest.json`.
- **Payload:** `subPrdId`, `lastCompletedPhaseId`, `resumeAction`
  (enum: `from_answers_log`, `from_bundle_manifest`,
  `aborted_corrupted`)
- **Consumer:** `prd-interviewer-effectiveness-evaluator`
  (involuntary-loss rate)

### Event 14 — `prd_telemetry_write_failed`

- **Status:** emitted (writes to fallback sink — see §5.A)
- **Trigger:** Telemetry append to the primary sink fails (Family I I1
  / L11 D4). The event itself is written to the fallback sink
  `.sage/prd-interview-telemetry.local.jsonl`.
- **Payload:** `attemptedEventName`, `fallbackPath`
- **Consumer:** `session-performance-evaluator` (infrastructure
  signal)

### Event 15 — `prd_workflow_config_defaulted`

- **Status:** emitted
- **Trigger:** `.sage/workflow-config.json` is missing or malformed
  (Family L11 E3); the interviewer falls back to documented defaults
  and warns the PM.
- **Payload:** `missingKey`, `defaultUsed`
- **Consumer:** `session-performance-evaluator`

### Event 16 — `prd_telemetry_corruption_recovered`

- **Status:** emitted
- **Trigger:** Telemetry JSONL file detected as corrupted (Family L11
  E4); file is renamed to
  `.sage/prd-interview-telemetry.[timestamp].corrupt.jsonl` and a
  fresh JSONL is started.
- **Payload:** `corruptedPath`, `archivedAs`
- **Consumer:** `session-performance-evaluator`

### Bundle-finalisation event — `prd_bundle_manifest_finalised`

- **Status:** emitted
- **Trigger:** End of P9, immediately before `prd_interview_completed`
  — `bundle-manifest.json` has been written with every file in the
  bundle, each carrying `prdHash`, `writtenAt`, `producer`, and
  `role`.
- **Payload:** `subPrdId`, `manifestPath`, `fileCount`
- **Consumer:** `prd-interviewer-effectiveness-evaluator`;
  `session-performance-evaluator`

---

## 3. Completeness-check events

Emitter: `.cursor/skills/prd-completeness-check/SKILL.md`. All carry
`workflowKind: "completeness_check"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `completeness_check_started` | emitted | Start of Step 1 (before reading any inputs) | `linearIssueId`, `featureId`, `prdPath: string` | out-of-band PM audit |
| `completeness_check_completed` | emitted | End of Step 4 (after assessment report written and Linear updated) | `linearIssueId`, `featureId`, `score: number`, `passThreshold: number`, `passed: boolean`, `dimensionScores: { D1: number, ... }`, `findingCount: number`, `linearStatusSet: "Ready" \| null` | out-of-band PM audit |
| `prd_completeness_score` | planned → emitted (Phase D scope item 4d) | End of Step 4 — emitted alongside `completeness_check_completed`; structured payload optimised for the effectiveness evaluator's "repeatedly below threshold" pattern | `featureId`, `subPrdId?: string \| null`, `totalScore: number`, `dimensionBreakdown: { D1: number, D2: number, D3: number, D4: number, D5: number, D6: number, D7: number, D8: number, D9: number }`, `passThreshold: number`, `passed: boolean` | prd-interviewer-effectiveness-evaluator (under-spec pattern: N consecutive PRDs below threshold → investigate which dimension fails most) |

The `prd_completeness_score` event duplicates two fields from
`completeness_check_completed` (`score`, `passed`) but uses a more
structured payload keyed by the post-Phase-D nine-dimension scheme
(D1..D9). Consumers should prefer `prd_completeness_score` when scoring
dimension-level patterns; `completeness_check_completed` remains the
canonical run-completion event for out-of-band audit.

---

## 4. Supporting-skill events

### prd-stale-check events

Emitter: `.cursor/skills/prd-stale-check/SKILL.md`. All carry
`workflowKind: "prd_stale_check"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `prd_stale_check_started` | emitted | Step 1 entry — after inputs are read | `featureId`, `subPrdId`, `prdPath: string` | prd-interviewer-effectiveness-evaluator (stale-check discipline) |
| `prd_stale_check_completed` | emitted | Step 4 close — after `stale-check.md` is written | `featureId`, `subPrdId`, `freshCount: number`, `staleCount: number`, `missingCount: number`, `derivatives: { path: string, status: "fresh" \| "stale" \| "missing" }[]` | prd-interviewer-effectiveness-evaluator (drift rate signal) |

### prd-amend events

Emitter: `.cursor/skills/prd-amend/SKILL.md`. All carry
`workflowKind: "prd_amend"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `prd_amend_initiated` | emitted | Start of skill — after stale surfaces are determined | `featureId`, `subPrdId`, `mode: "auto" \| "targeted"`, `staleSurfaces: string[]` | prd-interviewer-effectiveness-evaluator (amendment frequency signal) |
| `prd_amend_brief_generated` | emitted | Once per surface — after the diff brief is written | `featureId`, `subPrdId`, `surface: "demo" \| "sample-data" \| "component-spec"`, `briefPath: string` | prd-interviewer-effectiveness-evaluator (brief quality signal) |
| `prd_amend_completed` | emitted | End of skill — after all surfaces are processed | `featureId`, `subPrdId`, `surfacesRegenerated: string[]`, `surfacesSkipped: string[]` | out-of-band PM audit |

### prd-walkthrough events

Emitter: `.cursor/skills/prd-walkthrough/SKILL.md`. All carry
`workflowKind: "prd_walkthrough"`.

| Event | Status | Trigger | Payload (beyond envelope) | Consumer |
|---|---|---|---|---|
| `prd_walkthrough_run` | emitted | Once per skill invocation — after all seven sections are presented | `featureId`, `subPrdId`, `prdHash: string` | out-of-band PM audit |

---

## 5. Field naming convention

- Envelope fields use camelCase: `timestamp`, `event`, `prdRunId`,
  `workflowKind`, `linearIssueId`, `featureId`, `subPrdId`, `phaseId`.
- Payload fields use camelCase by convention.
- The Phase B-emitted `summary_cap_exceeded` event carries
  `attempted_line_count`, `source_yaml_line_count`, and
  `compression_ratio` in snake_case in the live SKILL.md text. The
  schema-authoritative camelCase forms (`attemptedLineCount`,
  `sourceYamlLineCount`, `compressionRatio`) are listed above. The
  effectiveness-evaluator must accept either form for back-compatibility
  with telemetry already on disk; new emit sites use camelCase.

---

## 6. Sink resolution and rotation (L12 Q4=4a)

- **Primary sink:** path resolved from `.sage/workflow-config.json` key
  `prd.telemetryFile`; default `.sage/prd-interview-telemetry.jsonl`.
- **Fallback sink:** `.sage/prd-interview-telemetry.local.jsonl`. Used
  when the primary sink is unavailable (disk full, permission denied,
  workflow-config malformed). The PM is warned at the moment of
  fallback. `prd_telemetry_write_failed` is itself written to the
  fallback sink so the fallback is auditable.
- **Corruption recovery:** if the JSONL is detected as corrupted on
  read, the file is renamed to
  `.sage/prd-interview-telemetry.[timestamp].corrupt.jsonl` and a fresh
  JSONL is started; `prd_telemetry_corruption_recovered` is emitted.
- **Rotation:** no automatic rotation. Manual rotation only at operator
  discretion (rename to `.YYYY-MM.jsonl`).
- **Schema versioning (L12 Q3=3c):** no version field. Rely on
  additive-only changes + the maintenance rule (Section 9) +
  effectiveness-evaluator schema-drift detection (events appearing on
  disk but not in this schema, or vice versa, after ≥ 3 PRD runs).

---

## 7. Six effectiveness metric families (L12 Q5=5a)

The contract between telemetry events and the effectiveness evaluators.
Every event in §1–§4 plus §2.A maps to at least one metric family below.

1. **Question discipline** — DI rate per phase (from
   `prd_phase_completed.deferredCount`), DI category distribution,
   deferral-to-acceptance rate.
2. **Phase progression** — phase duration distribution (envelope
   timestamps), phase rejection rate per phase
   (`prd_phase_rejected`), phase redirect rate
   (`prd_phase_redirected`), phase restart count.
3. **Handoff quality** — re-handoff rate per surface
   (`prd_handoff_re_run`), anchor mismatch rate by `mismatchType`
   (`prd_anchor_verification_failed`), deviation count distribution
   (from `manual_handoff_returned.deviationCount`), ambiguity flag rate
   per surface (`ambiguity_flag_raised`).
4. **Self-review discipline** — self-review gate failure rate by gate
   level (`prd_self_review_gate_failed`), coverage block rate per
   dimension (`prd_coverage_dimension_blocked`), pre-write bar walk
   failure rate per Pass Condition (`prd_pre_write_bar_walk_failed`).
5. **Recon quality** — override frequency by `overrideType`
   (`prd_interview_override_applied`), breakdown gap detection rate
   (`prd_breakdown_gap_detected`), hard-stop rate by `hardStopReason`
   (`prd_interview_hard_stopped`).
6. **PM friction & throughput** — abort rate by `phaseAtAbort`
   (`prd_interview_aborted`), time-to-completion (interview started →
   `prd_interview_completed` envelope spread), staleness-resumption
   rate (`prd_interview_resumed_with_staleness_warning`), mid-phase
   resume rate (`prd_interview_resumed_mid_phase`),
   completeness-check pass rate on first submission.

The catalog is the binding contract for evaluator implementations.
Adding a new metric family requires a schema update here plus the
matching event payload changes.

---

## 8. Settled decisions log

### 8.1 Settled: event names are `manual_handoff_initiated` / `manual_handoff_returned`

Ruled by PM Philip McSweeney at Phase D close (25-MAY-2026). Source of
truth: `docs/cursor/feature-sage-prd-interviewer-enhancements/phase-d-completion-report.md`
§11 ruling 1.

The legacy `sub_agent_*` event names (the spawned and returned pair)
were renamed to `manual_handoff_initiated` and `manual_handoff_returned`
at every emit site, every consumer reference, and the schema rows in
§2 above. Rationale: event names are the primary downstream index for
the effectiveness-evaluator and any future analytics; the existing
`sub_agent_*` names were semantically misleading because there is no
programmatic sub-agent in this environment — the production mechanism
is a manual chat handoff orchestrated by the PM. Aligning the event
name with the actual mechanism removes a permanent reading-cost tax
on every downstream consumer.

Back-compatibility: on-disk telemetry rows under the legacy
`sub_agent_*` names are accepted, and the
effectiveness-evaluator's schema-drift signal accepts either form so
historical telemetry remains valid without a migration script.

### 8.2 Settled: `ambiguity_scan_completed` emit-site placement is end of Step 4a

Ruled by PM Philip McSweeney at Phase D close (25-MAY-2026). Source of
truth: `docs/cursor/feature-sage-prd-interviewer-enhancements/phase-d-completion-report.md`
§11 ruling 2.

The emit-site fires when the ambiguity scan completes. Per the L12
Q2=2a phase-numbering migration the scan is now firmly inside P8
(immediately before PRD draft generation), which is the same semantic
position as the original Phase D wiring at "end of Step 4a (P9
ambiguity scan completion)" — the Step 4a label is retired in favour of
the P8 label. Rationale: the payload data (`qualifiersFoundCount`,
resolutions list) is only available at scan completion; firing earlier
would emit an incomplete payload.

### 8.3 Settled: L11 5-category failure taxonomy is additive

Ruled at L11 lock (carry-forward from the L1–L12 architectural model).

The 5-category L11 failure taxonomy in `shared-protocols.md`
(`A` PM-side, `B` Recon-side, `C` Handoff-chat-side, `D`
Interviewer-side, `E` Infrastructure) is **additive**. New failure
modes are inserted as new row IDs within an existing category (the
`B9` row is the canonical example — added after `B7`, deliberately
skipping `B8` to preserve historical row reservation). Row IDs are
immutable once published; renumbering would break every
effectiveness-evaluator query that aggregates by row ID.

The 16 new events in §2.A plus `prd_bundle_manifest_finalised` cover
the L11 row IDs as follows:

- `prd_interview_aborted` — Family L11 ABORT path (all categories).
- `prd_interview_hard_stopped` — B1, B2, plus E-category branch
  state.
- `prd_phase_rejected` — A5 (PM REJECT).
- `prd_phase_redirected` — A6 (PM REDIRECT).
- `prd_handoff_re_run` — C1, C4, C6, C7, C8.
- `prd_anchor_verification_failed` — C2 (Family N anchor mismatch).
- `prd_interview_override_applied` — B3, B4, B5, B9 (override-eligible
  Step 0 categories) plus pre-lift bundle migration.
- `prd_self_review_gate_failed` — D1, D2, D3 (Family G gates).
- `prd_coverage_dimension_blocked` — D2 (coverage-dimension blocking).
- `prd_pre_write_bar_walk_failed` — D3 (pre-write artifact-bar walk).
- `prd_breakdown_gap_detected` — B6 (mid-interview recon gap, Family
  E E1 forbids patching).
- `prd_interview_resumed_with_staleness_warning` — A4 (PM >14-day
  pause) and Family L L1.
- `prd_interview_resumed_mid_phase` — Family L pause-resume
  involuntary-loss path.
- `prd_telemetry_write_failed` — D4 / Family I I1 (telemetry sink
  unavailable).
- `prd_workflow_config_defaulted` — E3 (workflow-config malformed).
- `prd_telemetry_corruption_recovered` — E4 (JSONL corruption).
- `prd_bundle_manifest_finalised` — end-of-P9 manifest finalisation
  (precedes `prd_interview_completed`).

### 8.4 Settled: L12 phase-numbering migration (Q2=2a)

Ruled at L12 lock. The bundle-write events (`acceptance_criteria_generated`,
`reuse_map_confirmed`, `brief_generated`,
`component_pattern_confirmation_generated`,
`component_pattern_confirmation_resolved`, `ambiguity_scan_completed`)
are relabelled in §2 above from the legacy "Step 4X (P9)" labels to the
correct phase boundaries per the L8 lock:

- AC derivation, reuse-map finalisation, brief authoring, ambiguity
  scan, and pre-write artifact-bar walks — all **P8**.
- `manual_handoff_initiated` — end-of-P8 / start-of-P9 (PM about to run
  handoffs).
- `manual_handoff_returned` — mid-P9 (each handoff returns separately).
- `prd_interview_completed` — **end of P9** (post-handoff verification
  + bundle-manifest finalisation complete).
- `prd_bundle_manifest_finalised` — end of P9, immediately before
  `prd_interview_completed`.
- `component_pattern_confirmation_generated` and `_resolved` — moved
  to **end of P5** per the L8 lock (Component Pattern Confirmation
  Report is bulk-validated at P5 closure, not at P9).

This is a pure relabel; event names, payloads, and consumers are
unchanged for back-compatibility.

### 8.5 Settled: telemetry vocabulary additive-only (L12 Q3=3c)

Ruled at L12 lock. No schema version field on telemetry rows. Events
are added by extending §2.A (or the corresponding consumer section);
removed events are marked `deprecated` rather than deleted from the
schema. The effectiveness-evaluator surfaces drift between disk and
schema as Linear issues per the Section 9 maintenance rule.

### 8.6 Settled: six effectiveness metric families (L12 Q5=5a)

Ruled at L12 lock. The six-family catalogue in §7 above is the binding
contract between telemetry and evaluators. Adding a new family requires
a schema update plus a coordinated evaluator change.

---

## 9. Maintenance rule (binding)

When a new event is added to any emitter, the emit-site SKILL.md and
this schema doc MUST be updated in the same change. A divergence between
the two is a schema-drift defect. The effectiveness-evaluator surfaces
schema-drift defects (events on disk not listed here, or events listed
here not seen on disk after ≥ 3 PRD runs) as Linear issues against
the relevant emitter skill.

**Emitters bound by this rule (all six skill files are emit-site and
schema-doc binding points):**

- `.cursor/skills/prd-orchestrator/SKILL.md` (§1 events)
- `.cursor/skills/prd-interviewer/SKILL.md` (§2 events)
- `.cursor/skills/prd-completeness-check/SKILL.md` (§3 events)
- `.cursor/skills/prd-stale-check/SKILL.md` (§4 — supporting-skill events)
- `.cursor/skills/prd-amend/SKILL.md` (§4 — supporting-skill events)
- `.cursor/skills/prd-walkthrough/SKILL.md` (§4 — supporting-skill events)
