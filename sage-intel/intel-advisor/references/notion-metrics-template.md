# Notion Metrics Dashboard Template
# Published by intel-recorder to: [Workflow space] / Capacity & Metrics

This template defines the structure of the Notion page that
intel-recorder maintains after each work cycle. The Head of Product
reads this page for release forecasts and velocity trends.

---

```
# Capacity & Metrics — Profitability

Last updated: [ISO date] after work cycle [LIN-id]

---

## Release forecast

[For each active release in the Notion Release Calendar:]

### [Release name] — Target: [planned date]

| | P50 estimate | P80 estimate |
|---|---|---|
| Estimated ship date | [date] | [date] |
| Delta from target | [+/- N days] | [+/- N days] |
| Status | [🟢 ON TRACK / 🟡 AT RISK / 🔴 DELAYED] | |

**Features in scope ([N] total):**
- ✅ Complete: [N] features
- 🔄 In progress: [N] features ([current step summary])
- 📋 Not started: [N] features ([estimated effort])

[If AT RISK or DELAYED:]
> Risk note: [plain language explanation — e.g. "Phase 2 of Feature X is
> running 40% over estimate. If this pattern continues, the release
> date slips by approximately [N] days."]

---

## Velocity — rolling 4 weeks

**Features completed:** [N] in the last 4 weeks
**Mean feature cycle time:** [N] days
**Mean effort accuracy:** [N]% (actual vs estimated)

[Trend note: "Effort accuracy has improved from [N]% to [N]% over
the last [N] work cycles, indicating the estimation calibration
is converging."]

---

## AI adoption

| Metric | This cycle | Rolling average |
|---|---|---|
| Agent code ratio | [N]% | [N]% |
| Agent quality rate | [N]% | [N]% |
| Hook compliance rate | [N]% | [N]% |
| Rework rate | [N]% | [N]% |

> Agent quality rate measures the proportion of agent-written code
> that reached merge without human correction. A rate above 90%
> indicates the agent is producing code that meets standards on
> the first attempt.

---

## Calibration — current effort estimates

These are empirically derived estimates based on [N] completed phases.
They replace the phase-splitter's initial heuristics as data accumulates.

| Layer | P50 estimate | P80 estimate | Sample count | Confidence |
|---|---|---|---|---|
| Database (stored procedures) | [N] hrs | [N] hrs | [N] | [High/Moderate/Low] |
| API (.NET) | [N] hrs | [N] hrs | [N] | |
| UI (Angular) | [N] hrs | [N] hrs | [N] | |
| Data library (.NET) | [N] hrs | [N] hrs | [N] | |

> P50 = 50% of phases of this type complete within this time.
> P80 = 80% of phases complete within this time.
> Use P80 for conservative release planning.

---

## Release history

| Release | Planned date | Actual date | Delta | Scope delivered |
|---|---|---|---|---|
| [name] | [date] | [date] | [+/- N days] | [N]% |
...

---

## About these metrics

All estimates are derived from measured historical data — no human
estimation input is used. Confidence improves as more work cycles
complete. Metrics flagged with ⚠ have fewer than 5 historical samples
in that layer and should be treated as rough guidance.

[Link to full metric definitions]
```
