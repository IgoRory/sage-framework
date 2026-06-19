# Complexity Classifier — Feature Complexity Tier Assignment

Reference for prd-interviewer. Use during Step 2 (codebase reconnaissance) to
classify the feature's complexity tier. The tier determines expected interview
depth, the coverage dimensions required, and the time estimate to set with the PM.

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

## Coverage Dimensions per Tier

The coverage dimensions replace count-based thresholds as the calibration
mechanism. At each conclusion gate, the interviewer self-assesses against
the required dimensions for the feature's tier. Every required dimension
must be satisfied before proceeding.

**Dimension definitions:**
- **D-PRED** — Every requirement area has a testable predicate (GIVEN / WHEN / THEN) the interviewer can state without PM help
- **D-SP** — Every affected stored procedure has a defined before/after behavior delta
- **D-COMP** — Every UI component has all 6 specification elements (name/type, function, data, states, empty/loading/error, interactions)
- **D-DETAIL** — For every UI surface, the micro-detail layer is captured: label text, tooltip text, placeholder text, validation messages, empty-state copy, hover/focus behavior, disabled-state reason text, sort/filter defaults, and keyboard behavior
- **D-CROSS** — For every entity or action this feature touches, the cross-page/cross-feature impact is explicitly stated: which other screens display this data, which dashboards roll it up, which exports include it, which downstream calculations consume it, and what happens to each when this feature's data changes
- **D-RATIONALE** — For every non-obvious design choice, the PM has stated WHY, and at least one alternative was explicitly considered and rejected with reasoning
- **D-EC** — Every applicable edge-case category (of the 7) has at least one scenario with a defined outcome
- **D-SCOPE** — Out-of-scope boundary is explicit for every adjacent area surfaced in recon

**Required dimensions per tier:**

- **Tier 1 (Simple):** D-PRED, D-SCOPE, D-EC, D-RATIONALE. D-SP applies if SPs are affected. D-DETAIL and D-CROSS apply if the feature touches UI or shared data.
- **Tier 2 (Medium):** D-PRED, D-SCOPE, D-EC, D-RATIONALE, plus D-SP / D-COMP / D-DETAIL / D-CROSS as applicable to the feature's surface area.
- **Tier 3 (Complex):** All eight dimensions required.
- **Tier 4 (Very Complex):** All eight dimensions required, with D-DETAIL and D-CROSS explicitly enumerated per UI surface and per entity (umbrella statements are not acceptable — every surface and every entity must be individually traced).

---

### Minimum Acceptance Criteria Thresholds

> **Note:** This table is consumed by prd-completeness-check as an output
> quality metric for the generated PRD. It is **NOT** an interview question
> target. The interviewer never asks questions to hit these AC counts;
> ACs are derived from understanding captured during the interview, and
> this table only governs the completeness-check pass/fail at P9.

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

The tier thresholds and coverage dimension requirements are subject to
recalibration by the skill-effectiveness-evaluator. If the evaluator finds
that Tier 2 features consistently produce PRDs that fail completeness check
on D3 (edge cases), it may propose adding D-EC as a required dimension at
Tier 1, or tightening the D-EC definition. Do not hardcode these values in
downstream logic — always read them from this reference file.
