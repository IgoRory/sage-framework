---
name: intel-recorder
description: >
  Runs automatically after every completed work cycle alongside
  session-performance-evaluator. Collects phase-level and feature-level
  metrics, writes to velocity-history.jsonl and release-history.jsonl,
  regenerates the calibration dataset, and publishes the updated metrics
  report to Notion and Linear. Background, automated. Never invoked
  manually. The data this skill collects is the foundation for all
  capacity planning queries.
---

# Intel Recorder

Collects metrics after every completed work cycle and maintains the
historical dataset that powers capacity planning. Publishes updated
reports to Notion (Head of Product view) and Linear (CTO/dev view).

**Operating constraints:**
- Background agent — runs after session-performance-evaluator completes
- Never blocks active work
- Only write operations: `.sage/intel/` files, Notion pages, Linear
  issue comments
- Trigger: same as session-performance-evaluator — all phase issues
  at `Build Complete` status

---

## Step 1 — Load work cycle data

Read all inputs. If any are missing, note the gap and continue —
never fail silently without recording the data gap.

**From the file system:**
- Session manifest: `[SESSION_ROOT]/session-manifest.md`
- All phase completion reports: `[SESSION_ROOT]/phase-N/phase-N-completion-report.md`
- Session performance report (written by session-performance-evaluator)
- Existing velocity history: `.sage/intel/velocity-history.jsonl`
- Existing release history: `.sage/intel/release-history.jsonl`
- Existing calibration: `.sage/intel/calibration.json`

**From Linear (via MCP):**
- Feature issue: actual timestamps for all status transitions
  (Ready → Planned → Build Complete → Done)
- Phase issues: created_at, approved_at, in_progress_at, build_complete_at
- Current release cycle the feature belongs to (if any)

**From GitHub (via git log):**
- PR for each completed phase: diff stats (lines added, lines removed)
- Commit timestamps: pre-PR commits (agent) vs post-PR commits (human)
- Use the PR open timestamp as the dividing line:
  - Commits before PR open = agent-written
  - Commits after PR open = human review fixes

---

## Step 2 — Calculate phase metrics

For each completed phase, calculate:

```
phaseEffortAccuracy     = actualHours / estimatedHoursP50
                          (1.0 = perfect, >1 = over, <1 = under)

phaseCycleTimeHours     = S8 completedAt - S1 startedAt
                          (from manifest stepTimestamps)

agentLinesAdded         = lines added in commits before PR open
humanLinesAdded         = lines added in commits after PR open
agentCodeRatio          = agentLinesAdded / (agentLinesAdded + humanLinesAdded)
                          (null if no PR yet — Solo phases may skip)

reworkOccurred          = any step where stepStatus was set to
                          "blocked" and then "complete" more than once

hookViolationCount      = from session performance report
tddFirstPassRate        = from session performance report
refactorCompletionRate  = from session performance report
```

Determine `layer` from the phase's `scopedFiles`:
- Any files under `Database/` → `database`
- Any files under `Libraries/` → `data-library`
- Any files under `Services/ProfitabilityAPI/` → `api`
- Any files under `Web/ProfitabilityWeb/` → `ui`
- Mixed layers → `full-stack`

---

## Step 3 — Calculate feature metrics

```
featureCycleTimeDays    = (Done timestamp - Ready timestamp) / 86400
                          (from Linear status transition log)

plannedPhaseCount       = phases in manifest at kick-off
actualPhaseCount        = phases in completion log
phaseCountAccuracy      = plannedPhaseCount == actualPhaseCount

approvalTurnaround      = mean of (Approved timestamp - Pending Approval timestamp)
                          across all phases in this feature
                          (team-only metric — not published to leadership)

parallelEfficiency      = criticalPathHours / sum(all phase actualHours)
                          (1.0 = perfect parallelism, lower = serialisation)
```

---

## Step 4 — Write velocity history record

Append one record per completed phase to `.sage/intel/velocity-history.jsonl`:

```json
{
  "recordId": "[uuid]",
  "recordedAt": "[ISO datetime]",
  "workflowVersion": "1.0.0",
  "sessionId": "[LIN-feature-id]",
  "phaseId": "[phase number]",
  "featureLinearId": "[LIN-feature-id]",
  "phaseLinearId": "[LIN-phase-id]",
  "mode": "hive | pair | solo",
  "layer": "database | api | ui | data-library | full-stack",
  "developerProfile": "[from manifest phase definition]",
  "prdCompletenessScore": "[from manifest header]",
  "estimatedHoursLow": "[from manifest]",
  "estimatedHoursHigh": "[from manifest]",
  "estimatedHoursP50": "[midpoint of low-high range]",
  "actualHours": "[calculated]",
  "effortAccuracy": "[calculated]",
  "cycleTimeHours": "[calculated]",
  "stepDurations": {
    "dev-interview": "[hours]",
    "implementation-plan": "[hours]",
    "traceability-review": "[hours]",
    "plan-validation": "[hours]",
    "build": "[hours]",
    "code-review": "[hours]",
    "agent-testing": "[hours]",
    "completion-report": "[hours]"
  },
  "reworkOccurred": "[boolean]",
  "hookViolationCount": "[integer]",
  "tddFirstPassRate": "[0.0-1.0]",
  "refactorCompletionRate": "[0.0-1.0]",
  "agentLinesAdded": "[integer | null]",
  "humanLinesAdded": "[integer | null]",
  "agentCodeRatio": "[0.0-1.0 | null]",
  "tier": "[0 | 1 | 2]",
  "upstreamDependencies": "[phase IDs]",
  "scopedFileTypes": "[array of extensions]"
}
```

---

## Step 5 — Write release history record (if feature is part of a release)

Check the feature's Linear issue for a release cycle assignment.
If the feature belongs to a named release AND the release is now
complete (all features Done), append a record to
`.sage/intel/release-history.jsonl`:

```json
{
  "recordId": "[uuid]",
  "recordedAt": "[ISO datetime]",
  "releaseName": "[e.g. Release/26.03/dev-main]",
  "plannedDate": "[from Notion Release Calendar]",
  "actualDate": "[date last feature merged to main]",
  "dateDeltaDays": "[positive = late, negative = early]",
  "featuresPlanned": ["[LIN-ids]"],
  "featuresShipped": ["[LIN-ids actually merged]"],
  "featuresDeferred": ["[LIN-ids deferred to next release]"],
  "scopeDeliveryRate": "[featuresShipped / featuresPlanned]",
  "totalPhaseCount": "[sum across all features]",
  "totalActualHours": "[sum of actualHours across all phases]",
  "totalCalendarDays": "[actualDate - first feature Ready date]",
  "avgFeatureCycleTimeDays": "[mean featureCycleTimeDays]",
  "avgEffortAccuracy": "[mean effortAccuracy across all phases]"
}
```

If the feature's release is not yet complete, skip this step.

---

## Step 6 — Regenerate calibration dataset

Read the full `velocity-history.jsonl` and recalculate empirical
estimates by layer. Write to `.sage/intel/calibration.json`:

```json
{
  "lastUpdatedAt": "[ISO datetime]",
  "totalSampleCount": "[N]",
  "dataQualityNote": "[if < 10 samples: 'Early dataset — estimates have wide variance']",
  "byLayer": {
    "database": {
      "sampleCount": "[N]",
      "meanHours": "[value]",
      "stdDevHours": "[value]",
      "p50Hours": "[median]",
      "p80Hours": "[80th percentile]",
      "p95Hours": "[95th percentile]",
      "effortAccuracyMean": "[mean of effortAccuracy across samples]",
      "effortAccuracyStdDev": "[std dev — measures how reliable estimates are]"
    },
    "api": { "...": "same structure" },
    "ui": { "...": "same structure" },
    "data-library": { "...": "same structure" },
    "full-stack": { "...": "same structure" }
  },
  "approvalTurnaround": {
    "sampleCount": "[N]",
    "meanHours": "[value]",
    "p50Hours": "[value]",
    "p80Hours": "[value — use this for conservative estimates]"
  },
  "agentCodeRatioMean": "[mean across all phases with data]",
  "agentQualityRateMean": "[mean of 1 - (humanLinesAdded / (agentLinesAdded + humanLinesAdded))]",
  "hookComplianceRate": "[phases with zero violations / total phases]",
  "reworkRate": "[phases with reworkOccurred=true / total phases]"
}
```

**Minimum sample threshold:** Do not calculate p80 or p95 for layers
with fewer than 5 samples — use the phase-splitter heuristic estimates
instead. Note this explicitly in the calibration file.

---

## Step 7 — Publish to Notion

Fetch the Notion metrics dashboard page. Create it if it doesn't exist
under the workflow documentation space at:
`[SESSION_ROOT workflow space] / Capacity & Metrics`

Update the page with the following sections. See
`references/notion-metrics-template.md` for the full page structure.

**Sections always updated:**
- Current velocity (rolling 4-week feature throughput)
- Effort accuracy trend (is estimation improving over time?)
- AI adoption metrics (agent code ratio, agent quality rate,
  hook compliance rate)
- Calibration summary (current p50 estimates by layer)

**Sections updated when release data changes:**
- Release forecast (estimated dates for active releases)
- Release history (accuracy of past releases)

**What is NOT published to Notion (team-only):**
- Approval turnaround data — stays in calibration.json only

---

## Step 8 — Publish to Linear

On the completed feature's Linear issue, add a comment with the
feature-level metrics summary. On the work cycle's Linear cycle
(if applicable), update the cycle description with aggregate metrics.

Format for the Linear issue comment:

```
📊 Capacity Metrics — [Feature title]

Feature cycle time:   [N] days (Ready → Done)
Phases completed:     [N] ([N] planned)
Effort accuracy:      [N]% (actual vs estimated)
Parallel efficiency:  [N]% of theoretical maximum
Agent code ratio:     [N]%
Agent quality rate:   [N]% (survived to merge without rework)
Hook compliance:      [N violations across all phases]

Session: [LIN-feature-id] | Mode: [mode]
```

---

## Reference files

- `references/notion-metrics-template.md` — full Notion page
  structure for the Capacity & Metrics dashboard
- `references/metric-definitions.md` — authoritative definitions
  for all metrics (the organisational standard)
