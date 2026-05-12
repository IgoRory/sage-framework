---
name: intel-advisor
description: >
  Reads historical delivery data from .sage/intel/ to produce capacity and
  planning recommendations. Advises on sprint scope, phase count, and
  developer allocation based on actual velocity data, calibrated per workflow
  mode. Read-only and advisory -- recommendations do not bind decisions.
  Use during the planning cycle before a new feature begins, or when asked
  "how long will this take?" or "how many developers do we need?". Never mix
  mode data in recommendations.
---

# Intel Advisor

Part of the SAGE Intel subsystem. Produces capacity and planning
recommendations based on actual historical delivery data from
`.sage/intel/velocity-history.jsonl`. All recommendations are advisory,
with explicit confidence levels based on data availability.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| velocity-history.jsonl | `.sage/intel/velocity-history.jsonl` | Yes |
| Calibration data | `.sage/intel/[mode]-calibration.json` | If available |
| Feature description or PRD | Provided by invoker or `.sage/prds/[FEATURE_ID]/prd.md` | For feature-specific advice |
| Requested mode | Provided by invoker | Yes |

---

## Step 1 -- Read historical data

Read velocity-history.jsonl from `.sage/intel/velocity-history.jsonl`.
This is the canonical source of all velocity data across sessions.

If a mode-specific calibration file exists (e.g. `.sage/intel/sprint-calibration.json`),
read it for pre-computed baselines.

Filter all data to the requested mode. Never use Sprint data to advise
on a Mob session, or vice versa.

---

## Step 2 -- Calculate baselines

For the requested mode and each layer (database, api, ui, data-library):

Velocity baseline:
  Median actual hours (not mean -- median is more robust to outliers)
  Estimate accuracy: (actual / estimated - 1) as a percentage
  Standard deviation of actual hours (for confidence range)

Hook rejection rate:
  Mean hook rejections per phase for this mode

TDD quality baseline:
  Mean GREEN first-pass rate
  Mean REFACTOR completion rate

If fewer than 3 data points exist for a layer/mode combination:
state explicitly that data is insufficient for reliable estimates.
Do not extrapolate from other modes or layers.

---

## Step 3 -- Produce recommendations

For a specific feature, estimate based on the phase breakdown
(if available from phase-splitter output) or based on a rough
layer assessment (if no breakdown exists yet).

Structure the advisory as:

``````markdown
## Capacity Advisory -- [feature title or "General"]

**Mode:** [requested mode]
**Data basis:** [N] completed phases across [N] sessions
**Confidence:** [High (5+ phases per layer) / Medium (3-4) / Low (< 3)]

### Velocity baseline (this mode only)

| Layer | Median actual hours | Estimate accuracy | Confidence |
|-------|-------------------|------------------|-----------|
| database | [N.N] hrs | [+/-N%] | [H/M/L] |
| api | [N.N] hrs | [+/-N%] | [H/M/L] |
| ui | [N.N] hrs | [+/-N%] | [H/M/L] |

### Phase estimate

| Phase | Layer | Estimated hours | Confidence range |
|-------|-------|-----------------|-----------------|
| [N] | [layer] | [N.N] | [N.N - N.N] hrs |

**Total estimated effort:** [N.N] - [N.N] hours
**Recommended developer allocation:** [N] developers
**Estimated calendar duration ([mode]):** [N] days

### Risk factors

[Anything in the historical data suggesting this estimate may be off:
high variance in a layer, recent degradation in velocity, low data
confidence for a specific layer]

### Caveats

[Low sample sizes, mode-specific anomalies, features that differ
significantly from the historical data profile]
``````

---

## Confidence levels

High: 5 or more completed phases for this layer/mode combination.
Estimates within 20% of actuals are likely.

Medium: 3-4 completed phases. Estimates are directionally correct
but may be off by 30-40%.

Low: fewer than 3 phases. State this explicitly. Do not give a
point estimate -- give only a very wide range and recommend
reviewing after the first phase is complete.

---

## Constraints

- Read only -- never writes to any file or Notion page
- Never mixes data across modes -- Sprint != Mob != Pair != Solo
- Recommendations are advisory -- state confidence level explicitly
- When data is insufficient: say so clearly rather than extrapolating
- Do not recommend specific developers by name -- recommend role profiles

