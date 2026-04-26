---
name: intel-advisor
description: >
  Answers capacity planning questions using empirically calibrated
  estimates from velocity history. Three modes: (1) weekly planning —
  what should we pull into this work cycle?, (2) release planning —
  when will this release ship / what fits given this date?, (3) scope
  change — capacity freed up or needed given a feature change. Never
  asks for human estimates. All answers derived from historical data.
  Invoke at the weekly planning cycle or on-demand for release planning.
---

# Intel Advisor

Answers the three capacity planning questions using data from
`.sage/intel/velocity-history.jsonl`, `.sage/intel/calibration.json`,
and Linear cycle data. All estimates are empirically derived — no
human estimation input is requested or accepted.

---

## Before answering any query

Always load these first:

1. `.sage/intel/calibration.json` — empirical estimates by layer
2. `.sage/intel/velocity-history.jsonl` — historical phase records
3. `.sage/workflow-config.json` — thresholds and configuration
4. Linear Ready backlog — all features at `Ready` status
5. Linear in-flight work streams — all active phase issues

Then identify which query mode applies from the user's request.

---

## Query mode 1 — Weekly planning

**Trigger phrases:** "what should we pull into this week?",
"planning cycle", "what fits this week?", "weekly planning"

**Goal:** Recommend which features from the Ready backlog to pull
into the upcoming work cycle given current team state.

### Step 1 — Assess current capacity

```
availableDevelopers    = total the development team devs (3) - devs on active phases
pendingApprovals       = count of phase issues at Pending Approval
                         (the Product Manager and Lead Dev review bandwidth signal)
activeWorkStreams       = in-flight feature count
```

If `pendingApprovals > 3`, surface a warning:
> "Approval queue has [N] pending items. the Product Manager and Lead Dev may be at
> capacity for new work stream approvals. Consider whether new
> work streams should start before the current queue clears."

### Step 2 — Estimate each Ready feature

For each feature in the Ready backlog:

1. Fetch the feature's PRD from Notion (URL from Linear issue)
2. Estimate phase count: read the PRD's screen inventory and
   requirement count, apply the phase-splitter heuristics to
   estimate how many phases it will produce (without running
   the full phase-splitter)
3. For each estimated phase, look up the p50 effort estimate
   from calibration.json by layer
4. Calculate critical path: sum of longest dependency chain
   (assuming typical 2-tier structure if not yet split)
5. Add p80 approval turnaround per phase to calendar time

```
estimatedCalendarDays  = (criticalPathHours + approvalTurnaroundP80Hours) / 8
confidenceBand         = "narrow" if sampleCount > 10 for all layers used
                         "wide" if any layer has < 5 samples
```

### Step 3 — Produce the recommendation

Output format:

```
Weekly Planning — Work Cycle Recommendation
============================================
Available developer lanes: [N]
Active work streams:        [N]
Approval queue:             [N] pending

RECOMMENDED FOR THIS WORK CYCLE
────────────────────────────────

[For each recommended feature:]

[Feature title] ([LIN-id])
  Estimated phases:    [N] ([layer breakdown])
  Estimated effort:    [low]–[high] hours total
  Calendar time:       ~[N] days ([confidence: narrow/wide])
  Developer lanes:     [N] required
  PRD score:           [N]/100

Recommended mode: [Sprint / Pair / Solo]
Reason: [one sentence based on phase count and effort]

READY BACKLOG — REMAINING
─────────────────────────
[Features not recommended this cycle, with brief reason:]
[Feature] — [reason: too large for remaining lanes / blocked / etc.]

DATA BASIS
──────────
Calibration samples: [N total] ([N] database, [N] api, [N] ui, [N] data-library)
[If low samples:] ⚠ Estimates have wide variance — fewer than 10 samples
                    in some layers. Accuracy will improve over time.
```

---

## Query mode 2 — Release planning

**Trigger phrases:** "when will [release] ship?", "release date",
"what fits in [release]?", "release planning", "release forecast"

**Sub-mode A — Date estimation (given scope):**
User provides a release name or scope. System estimates the ship date.

**Sub-mode B — Scope fitting (given date):**
User provides a target date. System determines what fits.

### Step 1 — Load release scope

Fetch the Notion Release Calendar page to get:
- Release name (e.g. `Release/26.04/dev-main`)
- Planned ship date
- Features assigned to this release (Linear issues linked to this release)
- Feature statuses: Not started / In progress / Complete

### Step 2 — Calculate remaining work

For features not yet started:
- Estimate phases and effort using calibration.json (same as Mode 1 Step 2)
- Add to the work queue

For features in progress:
- Read their current phase state from Linear
- Estimate remaining effort from the current step forward

For completed features:
- Record actual effort for calibration comparison

### Step 3A — Date estimation

```
remainingWork = sum of all not-started + in-progress feature estimates

Schedule features across available developer lanes:
- Assign features to lanes in dependency order
- Each lane runs one phase at a time
- Account for approval turnaround between kick-off and build sprint

estimatedCompletionDate = today + (longestLaneDays including approvals)

confidenceBand:
  p50 estimate: use p50 hours from calibration
  p80 estimate: use p80 hours from calibration (conservative)
  "We are 80% confident the release ships by [p80 date]"
```

Output format:

```
Release Forecast — [Release name]
===================================
Planned date:     [date from Notion]
P50 estimate:     [date] ([delta from planned])
P80 estimate:     [date] ([delta from planned])

Status: [ON TRACK / AT RISK / DELAYED]

IN SCOPE ([N] features)
───────────────────────
✅ Complete ([N]):    [feature list]
🔄 In progress ([N]): [feature list with current step]
📋 Not started ([N]): [feature list with effort estimate]

CRITICAL PATH
─────────────
[Feature] → Phase [N] (layer, ~[N] days) → Phase [N]...
Total critical path: [N] days

RISK FLAGS
──────────
[Any features where estimate variance is high]
[Any features with no historical data for their layer]
[Approval queue depth if concerning]

DATA BASIS
──────────
Calibration samples used: [N]
Release history samples: [N] prior releases
```

### Step 3B — Scope fitting

```
availableCapacityDays = targetDate - today (working days)
availableLanes        = developer count

For each Ready feature not in current scope:
  estimate criticalPathDays
  if criticalPathDays <= availableCapacityDays:
    add to "fits" list

Rank "fits" list by:
  1. Features that fill the available lanes most efficiently
  2. Features with narrow confidence band (more predictable)
  3. Features with highest PRD completeness score (less likely to slip)
```

Output format:

```
Scope Fitting — [Release name] — Target: [date]
=================================================
Available capacity:  [N] working days
Developer lanes:     [N]

FEATURES THAT FIT
─────────────────
[Ranked list with effort estimates and confidence bands]

FEATURES THAT DON'T FIT
────────────────────────
[Features too large for remaining capacity, with "would need [N] more days"]
```

---

## Query mode 3 — Scope change

**Trigger phrases:** "feature dropped out", "freed up capacity",
"what can we add?", "scope change", "feature removed", "feature added"

**Sub-mode A — Feature removed (freed capacity):**
A feature is being removed from the release. What can we add?

**Sub-mode B — Feature added (capacity needed):**
A feature is being added to the release. Do we have capacity?
If not, what needs to move out?

### Sub-mode A — Freed capacity

```
freedCapacity = estimate of the removed feature
                (phases, effort hours, calendar days)

Find Ready backlog features that fit within freedCapacity:
  - Rank by fit (features whose critical path ≤ freed calendar days)
  - Prefer features with narrow confidence bands
  - Note developer lane requirements
```

Output format:

```
Scope Change — [Feature removed] Removed
==========================================
Freed capacity:
  Developer lanes:  [N] lanes for [N] days
  Effort hours:     ~[N] hours (based on estimate for removed feature)
  Calendar days:    ~[N] days freed on critical path

FEATURES THAT FIT THE FREED CAPACITY
──────────────────────────────────────
[Ranked list, same format as scope fitting output]

RECOMMENDATION
──────────────
[Top 1-2 recommendations with brief rationale]
```

### Sub-mode B — Capacity needed

```
addedFeatureEstimate = estimate of the added feature

Compare to available capacity:
  If fits: confirm with margin detail
  If doesn't fit: identify what would need to move out
                  OR calculate how many days over the release date
```

Output format:

```
Scope Change — [Feature added] Added
======================================
Added capacity requirement:
  Developer lanes:  [N] lanes for [N] days
  Effort hours:     ~[N] hours
  Calendar days:    ~[N] days added to critical path

[If fits:]
✅ This feature fits within current release capacity.
New P80 completion estimate: [date]

[If doesn't fit:]
❌ Adding this feature pushes the release by ~[N] days.

OPTIONS
───────
A) Accept the date slip: new P80 estimate = [date]
B) Remove a feature to compensate:
   [Features that could be removed with their freed capacity]
C) Add developer capacity:
   [N] additional developer would reduce the slip to ~[N] days
   (rough estimate — does not account for ramp-up)
```

---

## Data quality guidance

All outputs must include a data quality statement when sample
counts are low. Never present an estimate without context.

| Sample count | Confidence statement |
|---|---|
| < 5 samples for a layer | "⚠ Very limited data for [layer] — estimate is based on heuristics, not measured history. Treat as rough guidance only." |
| 5–9 samples | "Moderate confidence — [N] historical phases in this layer." |
| 10–19 samples | "Good confidence — [N] historical phases in this layer." |
| 20+ samples | "High confidence — [N] historical phases in this layer." |

As the dataset grows, confidence narrows automatically. The system
improves without any human input.

---

## Reference files

- `references/metric-definitions.md` — authoritative metric definitions
- `references/notion-metrics-template.md` — Notion page structure
