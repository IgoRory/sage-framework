---
name: prd-interviewer-effectiveness-evaluator
description: >
  Evaluates prd-interviewer and prd-completeness-check effectiveness using
  PRD interview telemetry (JSONL), optional traceability-review artifacts,
  prd-completeness-check scoring telemetry, and skill-update-history. Proposes
  targeted updates to prd-interviewer SKILL.md and the per-section question-set
  files under references/question-sets/; stages unified diffs for Product
  Manager approval via Linear. Does not apply diffs directly. Invoke manually
  or on a cadence (e.g. every 5 completed PRD interviews). Use when the
  repository maintains .sage/prd-interview-telemetry.jsonl from prd-interviewer
  and prd-completeness-check.
---

# PRD Interviewer Effectiveness Evaluator

Analyses **`prd-interviewer`** outcomes using **PRD-native telemetry** (append-only JSONL aligned with session `workflow-telemetry.jsonl` conventions), plus optional downstream artifacts. When patterns show consistent gaps, drafts a **minimal** unified diff for **`prd-interviewer`** (and the per-section files under **`references/question-sets/`** only when adding or tightening a question). Cannot modify SKILL files directly — stages diffs for PM approval.

---

## Mutual exclusion

When this skill is deployed, **`skill-effectiveness-evaluator`** must **not** evaluate **`prd-interviewer`** — duplicate Linear proposals are avoided. See **`skill-effectiveness-evaluator`** SKILL coordination note.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| PRD telemetry JSONL | Path from `.sage/workflow-config.json` → `prd.telemetryFile` (default `.sage/prd-interview-telemetry.jsonl`) | Yes |
| skill-update-history.jsonl | `.sage/skill-update-history.jsonl` | Yes |
| prd-interviewer SKILL.md | `.cursor/skills/prd-interviewer/SKILL.md` | Yes |
| Per-section question-set files | `.cursor/skills/prd-interviewer/references/question-sets/` (folder — Phase A split) | Yes |
| Telemetry schema | `.cursor/skills/prd-interviewer/references/telemetry-schema.md` (single source of truth for every event) | Yes |
| Traceability reviews (optional) | `phase-*-traceability-review.md` in session folders | No |
| prd-completeness-check telemetry (optional but recommended) | `prd_completeness_score` events on the PRD telemetry JSONL | No |

**Not required:** `performance-report-cycle-*.md` (dev cycle reports).

---

## Step 1 — Eligibility

1. Read **`skill-update-history.jsonl`**. If **`prd-interviewer`** was rejected in the last **2** evaluation runs for this evaluator, **suppress** — log and skip.
2. If a Linear issue (**`skill-update`**, Pending Approval) already exists for **`prd-interviewer`** from this evaluator, **do not duplicate**.
3. Require evidence from **≥ 3** distinct completed interview runs (`prdRunId` or distinct `linearIssueId` with `prd_interview_completed`). Fewer → insufficient data; skip with note.

---

## Step 2 — Signals (underperformance)

Read **`references/prd-interviewer-signals.md`** for detailed patterns and
**`prd-interviewer/references/telemetry-schema.md`** for the authoritative
event catalogue. Summary:

### Phase A / Phase B / pre-Phase-C signals (unchanged)

1. **Preflight discipline** — Repeated `prd_preflight` with `preflightOutcome: fail` followed by `prd_phase_started` for P1–P9 without a documented override → tighten Step 0 gate language or override documentation.
2. **Phase coverage** — Across interviews, specific **`phaseId`** ranges never reach `prd_phase_completed` (e.g. always skip P6/P7) → add or strengthen questions in the mapped per-section question-set file.
3. **Duration / abandonment** — Large timestamp gaps between `prd_phase_started` and `prd_phase_completed`, or low ratio of `prd_interview_completed` to starts → improve parking / flow guidance in SKILL.
4. **Downstream traceability (when artifacts exist)** — S3 Blocker findings referencing PRD section types map to P1–P9 gaps per reference table → targeted question in the corresponding per-section question-set file.

### Phase B-added signals

5. **`summary_cap_exceeded` with low compression ratio (< 0.5)** — The Component Pattern Summary format is bloated; flag **"Component Pattern Summary format is bloated; tighten."** Target the orchestrator's summary-format rules rather than the interviewer.
6. **`summary_cap_exceeded` with high compression ratio (> 0.5)** — The underlying YAML is genuinely large; flag **"Underlying YAML is large; consider raising the cap from 80 lines."** Target the orchestrator's cap configuration rather than the interviewer.

### Phase C-added signals

7. **`manual_handoff_returned` with `deviationCount > 0`** — The interviewer's brief quality may be inadequate; flag **"Interviewer brief quality may be inadequate; review brief structure."** Target the relevant brief authoring step in `prd-interviewer/SKILL.md` Step 4f. Back-compatibility: telemetry rows on disk under the legacy `sub_agent_*` name (the returned form) are accepted as the same signal.
8. **`reuse_map_confirmed` with `pmOverrideCount` > 30% of `rowCount`** — Default-reuse assumptions may be miscalibrated; flag **"Default-reuse assumptions may be miscalibrated."** Target the default-reuse assumption binding section of `prd-interviewer/SKILL.md`.
9. **`brief_generated` followed by `manual_handoff_returned` with high `ambiguityFlagCount`** — Briefs may be under-specified; flag **"Briefs raising frequent ambiguity flags; brief authoring may be incomplete."**
10. **`component_pattern_confirmation_resolved` with `decisionsPmOverridden` > 30% of `decisionsTotal`** — Pattern detection is too aggressive; flag **"Component Pattern Block detection may be over-matching."**

### Phase D-added signals

11. **`ambiguity_scan_completed` with `unresolvedMarkersCount > 0`** — Flag **"Interviewer is not driving ambiguity to resolution before completing P8."** Target the Step 4a discipline.
12. **`prd_completeness_score` with `passed: false` across N consecutive PRDs (default N = 3; configurable as `prd.effectivenessConsecutiveFailureThreshold` in `.sage/workflow-config.json`)** — Pipeline is producing under-spec PRDs; flag **"Pipeline producing under-spec PRDs; investigate which dimension is failing most often."** Read the `dimensionBreakdown` field across the failing runs and surface the lowest-scoring dimension(s) so the proposed diff targets the right interviewer step or question-set file.

### Schema-drift signal (binding)

13. **Event observed in telemetry not listed in `telemetry-schema.md`, OR event listed in the schema with `status: emitted` not seen on disk after ≥ 3 completed PRD runs** — schema drift. Flag **"Telemetry schema drift detected"** and surface as a Linear issue against the emitting skill (orchestrator, interviewer, or completeness-check).

### L1–L12 signals (Phase 8 — newly consumed event vocabulary)

The L1–L12 overhaul added the following event names to
`telemetry-schema.md` Section 2. This evaluator consumes each one as a
distinct signal source; the patterns named below feed the six metric
families documented at the bottom of this section.

14. **`prd_interview_aborted` rate by `phaseAtAbort`** — abort clustering at a
    specific phase (e.g. always at P5) → propose tightening that phase
    module's gate or its question-bank scope. Feeds **PM friction &
    throughput**.
15. **`prd_interview_hard_stopped` by `hardStopReason`** — repeated
    `breakdown_missing` or `breakdown_malformed` → propose tightening the
    Step 0 readiness language. Repeated `wrong_branch` / `dirty_tree` →
    propose a clearer PM-facing pre-interview checklist. Feeds **Recon
    quality**.
16. **`prd_phase_rejected` rate per `phaseId`** — repeated REJECT at the
    same phase across runs → propose tightening that phase's self-review
    checklist. Feeds **Phase progression**.
17. **`prd_phase_redirected` from / to mapping** — repeated REDIRECT from
    P5 → P1 (or similar large rewinds) → propose tightening the P2 §4
    coverage map declaration so scope changes are caught earlier. Feeds
    **Phase progression**.
18. **`prd_handoff_re_run` rate per `surface` and `rerunReason`** — the
    `anchor_mismatch` reason is the most direct Family N quality signal;
    cluster by surface to target the right brief-authoring step. Feeds
    **Handoff quality**.
19. **`prd_anchor_verification_failed` by `mismatchType`** — clustering on
    `structural` → propose tighter brief Section 3 anchor lists; clustering
    on `copy` → propose more verbatim copy strings in brief Section 6;
    clustering on `yaml_vs_pm_contradiction` → escalation pattern, propose
    the orchestrator improve its `investigation_context`. Feeds **Handoff
    quality**.
20. **`prd_interview_override_applied` rate by `overrideType`** — high
    `thin_pattern_summaries` or `manifest_stale` → propose tightening
    orchestrator's preflight; `telemetry_sink_unavailable` → propose
    infrastructure investigation (advisory; not a SKILL.md diff).
    Feeds **Recon quality**.
21. **`prd_self_review_gate_failed` by `gateLevel` and `phaseId`** —
    repeated G1 failure at a phase → propose adding the failing checklist
    item to that phase's exit checklist verbatim. G3 failure clustering →
    propose tightening the pre-write artifact-bar walk. Feeds **Self-review
    discipline**.
22. **`prd_coverage_dimension_blocked` by `dimension` and `phaseId`** —
    repeated blocks on a single dimension → propose adding targeted
    cross-cutting sub-batches to the relevant phase's question bank.
    Feeds **Self-review discipline**.
23. **`prd_pre_write_bar_walk_failed` by `failedPassCondition` and
    `artifact`** — repeated failure on the same Pass Condition → propose
    tightening that Pass Condition's wording in
    `production-grade-quality-bar.md` or adding a pre-check earlier in the
    relevant phase. Feeds **Self-review discipline**.
24. **`prd_breakdown_gap_detected` rate** — high rate signals an
    orchestrator quality issue, not an interviewer issue; propose
    orchestrator skill update with the gap-type clusters. Feeds **Recon
    quality**.
25. **`prd_interview_resumed_with_staleness_warning` with
    `staleConfirmOutcome: phase_restart` clustering** — proportion of
    pauses that triggered restart → propose tighter pause-resume guidance
    (Family L) in `shared-protocols.md`. Feeds **PM friction & throughput**.
26. **`prd_interview_resumed_mid_phase` by `resumeAction`** — high rate of
    `aborted_corrupted` → infrastructure signal (advisory). High rate of
    `from_bundle_manifest` → confirms manifest-driven resume is working;
    no SKILL.md change proposed. Feeds **PM friction & throughput**.
27. **`prd_telemetry_write_failed`, `prd_workflow_config_defaulted`,
    `prd_telemetry_corruption_recovered`** — infrastructure category; no
    SKILL.md diffs proposed by this evaluator. Surface as advisory Linear
    issues against the operator. Feeds **Self-review discipline** only as
    advisory context.
28. **`prd_bundle_manifest_finalised` presence on every completed run** —
    if `prd_interview_completed` appears without a preceding
    `prd_bundle_manifest_finalised` for the same `prdRunId`, surface as a
    schema drift defect against the interviewer (Family N / P9 closure
    discipline broken). Feeds **Handoff quality**.

The full event payload shapes for every event listed above are in
[`prd-interviewer/references/telemetry-schema.md`](../prd-interviewer/references/telemetry-schema.md)
Section 2. Bundle finalisation also writes the per-run file inventory to
`bundle-manifest.json`, which is the canonical record of which derivatives
existed at completion; cross-reference the manifest when investigating
signal 28.

---

## Six effectiveness metric families (binding)

The L12 contract names six metric families. Every signal above maps to
one of these families; the evaluator's Linear proposals should name the
family the proposal is intended to improve.

1. **Question discipline** — DI rate per phase, DI category distribution,
   deferral-to-acceptance rate.
2. **Phase progression** — phase duration distribution, phase rejection
   rate, phase redirect rate, phase restart count.
3. **Handoff quality** — re-handoff rate per surface, anchor mismatch
   rate by `mismatchType`, deviation count distribution, ambiguity flag
   rate per surface.
4. **Self-review discipline** — self-review gate failure rate by gate
   level, coverage block rate per dimension, pre-write bar walk failure
   rate per Pass Condition.
5. **Recon quality** — override frequency by `overrideType`, breakdown
   gap detection rate, hard-stop rate by `hardStopReason`.
6. **PM friction & throughput** — abort rate by `phaseAtAbort`,
   time-to-completion, staleness-resumption rate, mid-phase resume rate,
   completeness-check pass rate on first submission.

The metric family roll-up is documented authoritatively in
[`prd-interviewer/references/downstream-agent-contract.md`](../prd-interviewer/references/downstream-agent-contract.md)
§6 and in `telemetry-schema.md` Section 6 (settled decisions log).

---

## Step 3 — Draft the skill diff

- Unified diff format — target **`prd-interviewer/SKILL.md`**, any file under **`prd-interviewer/references/question-sets/`** (the per-section files split by Phase A), or **`prd-completeness-check/SKILL.md`** when the underperformance is on the completeness-check side (signal 12).
- One skill update proposal per evaluation cycle for **`prd-interviewer`**; one separate proposal per evaluation cycle for **`prd-completeness-check`** when signal 12 fires.
- Write diff to **`.skill-update-staging/[LINEAR_ISSUE_ID].diff`** (placeholder id until Linear issue exists).

---

## Step 4 — Linear issue

- Label: **`skill-update`**
- Status: **Pending Approval**
- Title: **`Skill update — prd-interviewer — PRD eval [date or cycle]`**
- Approver: **Product Manager**
- Description must cite **specific JSONL patterns** or traceability excerpts as evidence.

Optional **`evaluatorId`**: `"prd-interviewer-effectiveness-evaluator"` in skill-update-history append.

---

## Step 5 — Append skill-update-history.jsonl

Append one JSON line per proposal:

```json
{
  "timestamp": "[ISO UTC]",
  "skillName": "prd-interviewer",
  "action": "proposed",
  "linearIssueId": "[id]",
  "diffPath": ".skill-update-staging/[id].diff",
  "evidenceSummary": "[one sentence]",
  "evaluatorId": "prd-interviewer-effectiveness-evaluator"
}
```

---

## Cadence

- **Default:** Manual PM review until JSONL volume is stable.
- **Optional:** Every **5** `prd_interview_completed` events in the PRD JSONL (count distinct `prdRunId` or `linearIssueId` as appropriate).

**Cadence is itself a candidate for effectiveness evaluation.** If the
evaluator runs at the every-5 cadence and consistently produces zero
actionable signals (or, conversely, consistently produces signals that
the PM rejects), the cadence may be too aggressive or too lax. This is
a self-referential recursion — the evaluator evaluating its own
trigger — but the data is there in `skill-update-history.jsonl`. A
human (Lead Dev or PM) reviews cadence appropriateness on demand; the
evaluator does not auto-adjust its own cadence.

---

## Constraints

- Cannot apply staged diffs directly.
- Minimum **3** completed interviews before proposing changes.
- Targeted changes only — no wholesale rewrite of the question set.

---

## Reference files

- Read **`references/prd-interviewer-signals.md`** for signal thresholds and Blocker→phase mapping.
- Read **`prd-interviewer/references/telemetry-schema.md`** for the authoritative event catalogue (envelope, payloads, statuses). Schema-drift detection (signal 13) keys off this file.
