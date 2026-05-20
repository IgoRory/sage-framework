# Complexity Classifier — Feature Complexity Tier Assignment

Reference for prd-interviewer. Use during Step 2 (codebase reconnaissance) to
classify the feature's complexity tier. The tier determines minimum question
thresholds for the main interview and the edge-case interview phase.

---

## How to use

After completing codebase reconnaissance, count the following factors using
the findings from the reconnaissance. Classify using the threshold table.
Record the tier in telemetry and present it to the PM at Step 3 (set
expectations).

---

## Factor Counts

| Factor | How to count |
|---|---|
| Scoped files affected | Count distinct source files (components, services, SPs, views, models) that the feature will create or modify, based on reconnaissance findings |
| Requirements | Count distinct business rules or functional requirements visible in the Linear issue description plus any provided context documents |
| Data entities | Count distinct data models, database tables, stored procedures, and views involved |
| User interactions | Count distinct user-triggered actions (button clicks, form submissions, selections, navigations) visible in the feature scope |
| Stored procedures affected | Count distinct stored procedures that will be created, modified, or whose output is consumed by this feature |
| Cross-component dependencies | Count components outside the feature's primary scope that depend on data produced by this feature, plus components this feature depends on |

---

## Tier Thresholds

| Factor | Tier 1 (Simple) | Tier 2 (Medium) | Tier 3 (Complex) | Tier 4 (Very Complex) |
|---|---|---|---|---|
| Scoped files affected | 1–3 | 4–8 | 9–15 | 16+ |
| Requirements | 1–3 | 4–8 | 9–15 | 16+ |
| Data entities | 1–2 | 3–4 | 5–7 | 8+ |
| User interactions | 1–5 | 6–12 | 13–20 | 21+ |
| Stored procedures affected | 0–1 | 2–3 | 4–6 | 7+ |
| Cross-component dependencies | 0 | 1–2 | 3–5 | 6+ |

**Classification rule:** The feature's tier is the highest tier reached by
any individual factor. If two or more factors reach Tier 3, auto-escalate
to Tier 4.

---

## Minimum Question Thresholds

| Tier | Main interview (P1–P5b) | Edge-case phase (P6) | Total minimum |
|---|---|---|---|
| Tier 1 (Simple) | 10 | 5 | 15 |
| Tier 2 (Medium) | 15 | 8 | 23 |
| Tier 3 (Complex) | 20 | 12 | 32 |
| Tier 4 (Very Complex) | 25 | 15 | 40 |

These thresholds are minimums. The skill should ask as many questions as
needed to fully cover the feature. The thresholds exist to prevent
under-interviewing, not to cap interview depth.

### Minimum Acceptance Criteria Thresholds

The PRD generation step (P9) must produce at least this many ACs per
category. If below threshold after the first generation pass, derive
additional ACs from under-covered areas before finalising.

| Tier | Min AC-REQ | Min AC-EC | Min AC-UI + AC-ERR | Total min |
|------|-----------|-----------|-------------------|-----------|
| Tier 1 (Simple) | 5 | 3 | 2 | 10 |
| Tier 2 (Medium) | 8 | 5 | 5 | 18 |
| Tier 3 (Complex) | 12 | 8 | 8 | 28 |
| Tier 4 (Very Complex) | 15 | 12 | 12 | 39 |

For non-UI features (no Section 5b components), the AC-UI + AC-ERR
column applies only to error/recovery scenarios from Section 6 Category 7.

---

### Mid-interview enforcement

Track questions asked per section throughout the interview. Before
concluding the main interview (P1-P5b) at the conclusion gate, verify
the running total meets the tier minimum for the main interview column.
If the count is below threshold, identify which categories are
under-covered and ask additional questions before proceeding to the
edge-case phase.

Similarly, before concluding the edge-case phase (P7), verify the
edge-case question count meets the tier minimum. If under threshold,
identify which of the 7 edge-case categories have the fewest questions
and expand coverage there.

---

## Telemetry

Record the classification as a `prd_complexity_classified` telemetry event
after Step 2 completes:

```json
{
  "event": "prd_complexity_classified",
  "phaseId": "P2",
  "complexityTier": "tier-3",
  "factors": {
    "scopedFiles": 11,
    "requirements": 9,
    "dataEntities": 6,
    "userInteractions": 14,
    "storedProcedures": 4,
    "crossComponentDependencies": 3
  }
}
```

---

## Recalibration

The tier thresholds and minimum question counts are subject to recalibration
by the skill-effectiveness-evaluator. If the evaluator finds that Tier 2
features consistently produce PRDs that fail completeness check on D3 (edge
cases), it may propose raising the Tier 2 edge-case minimum. Do not hardcode
these values in downstream logic — always read them from this reference file.
