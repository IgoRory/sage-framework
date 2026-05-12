---
name: prd-interviewer-effectiveness-evaluator
description: >
  Evaluates prd-interviewer effectiveness using PRD interview telemetry (JSONL),
  optional traceability-review artifacts, and skill-update-history. Proposes targeted
  updates to prd-interviewer SKILL.md and references/question-sets.md; stages unified
  diffs for Product Manager approval via Linear. Does not apply diffs directly.
  Invoke manually or on a cadence (e.g. every 5 completed PRD interviews). Use when
  the repository maintains .sage/prd-interview-telemetry.jsonl from prd-interviewer.
---

# PRD Interviewer Effectiveness Evaluator

Analyses **`prd-interviewer`** outcomes using **PRD-native telemetry** (append-only JSONL aligned with session `workflow-telemetry.jsonl` conventions), plus optional downstream artifacts. When patterns show consistent gaps, drafts a **minimal** unified diff for **`prd-interviewer`** (and **`references/question-sets.md`** only when adding or tightening a question). Cannot modify SKILL files directly — stages diffs for PM approval.

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
| question-sets.md | `.cursor/skills/prd-interviewer/references/question-sets.md` | Yes |
| Traceability reviews (optional) | `phase-*-traceability-review.md` in session folders | No |
| prd-completeness-check outputs (optional) | Linked by `linearIssueId` | No |

**Not required:** `performance-report-cycle-*.md` (dev cycle reports).

---

## Step 1 — Eligibility

1. Read **`skill-update-history.jsonl`**. If **`prd-interviewer`** was rejected in the last **2** evaluation runs for this evaluator, **suppress** — log and skip.
2. If a Linear issue (**`skill-update`**, Pending Approval) already exists for **`prd-interviewer`** from this evaluator, **do not duplicate**.
3. Require evidence from **≥ 3** distinct completed interview runs (`prdRunId` or distinct `linearIssueId` with `prd_interview_completed`). Fewer → insufficient data; skip with note.

---

## Step 2 — Signals (underperformance)

Read **`references/prd-interviewer-signals.md`** for detailed patterns. Summary:

1. **Preflight discipline** — Repeated `prd_preflight` with `preflightOutcome: fail` followed by `prd_phase_started` for P1–P9 without a documented override → tighten Step 0 gate language or override documentation.
2. **Phase coverage** — Across interviews, specific **`phaseId`** ranges never reach `prd_phase_completed` (e.g. always skip P6/P7) → add or strengthen questions in mapped sections.
3. **Duration / abandonment** — Large timestamp gaps between `prd_phase_started` and `prd_phase_completed`, or low ratio of `prd_interview_completed` to starts → improve parking / flow guidance in SKILL.
4. **Downstream traceability (when artifacts exist)** — S3 Blocker findings referencing PRD section types map to P1–P9 gaps per reference table → targeted question in **`question-sets.md`**.

---

## Step 3 — Draft the skill diff

- Unified diff format — target **`prd-interviewer/SKILL.md`** or **`references/question-sets.md`** only.
- One skill update proposal per evaluation cycle for **`prd-interviewer`**.
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

---

## Constraints

- Cannot apply staged diffs directly.
- Minimum **3** completed interviews before proposing changes.
- Targeted changes only — no wholesale rewrite of the question set.

---

## Reference files

Read **`references/prd-interviewer-signals.md`** for signal thresholds and Blocker→phase mapping.
