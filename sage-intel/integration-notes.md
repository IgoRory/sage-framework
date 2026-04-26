# Capacity Planning — Directory Structure & Integration

---

## Directory structure

```
.sage/
├── capacity/
│   ├── velocity-history.jsonl      ← one record per completed phase
│   ├── release-history.jsonl       ← one record per completed release
│   ├── calibration.json            ← derived empirical estimates (regenerated each cycle)
│   └── metrics-report.md           ← human-readable current state (regenerated each cycle)
│
├── workflow-config.json            ← update capacityPlanningIntegration.enabled = true
├── sessions/
│   └── ...
└── webhook/
    └── ...

.cursor/
└── skills/
    ├── intel-recorder/
    │   ├── SKILL.md
    │   └── references/
    │       ├── metric-definitions.md
    │       └── notion-metrics-template.md
    └── intel-advisor/
        └── SKILL.md
```

---

## workflow-config.json update

After completing setup, update the feature flag:

```json
"capacityPlanningIntegration": {
  "enabled": true,
  "description": "intel-recorder runs after every work cycle. intel-advisor invoked at planning cycle and on-demand for release planning. Historical data in .sage/intel/. Published to Notion Capacity & Metrics page and Linear issue comments."
}
```

---

## Integration with the planning cycle

The intel-advisor integrates with the weekly planning cycle
as follows:

At the planning cycle (the Product Manager and Lead Dev):

1. the Product Manager opens Cursor and invokes intel-advisor
   with the trigger: "planning cycle — what should we pull
   into this work cycle?"

2. The advisor reads:
   - Current in-flight work streams from Linear
   - Ready backlog from Linear
   - Calibration.json for effort estimates
   - Current developer availability

3. The advisor produces the recommendation (Mode 1 output)

4. the Product Manager and Lead Dev review the recommendation and make
   the final pull decision — the advisor informs, it does
   not decide

5. The planning cycle proceeds as normal (mode assignment,
   kick-off scheduling, Linear work cycle creation)

The advisor is a decision-support tool. The planning cycle
governance (the Product Manager and Lead Dev jointly deciding) is unchanged.

---

## Integration with the session-performance-evaluator

intel-recorder runs after session-performance-evaluator completes.
The trigger is the same (all phase issues at Build Complete), but
intel-recorder fires second.

The execution order:
1. session-performance-evaluator runs → posts Notion report + Linear violations
2. intel-recorder runs → writes velocity-history + calibration + publishes metrics

This ordering ensures the session performance report is available
when intel-recorder runs (it reads it for TDD first-pass rate
and rework data).

---

## Notion Release Calendar integration

The Notion Release Calendar page (📅 Release Calendar) is read by
intel-advisor in Mode 2 and Mode 3 for planned release dates and
feature scope.

intel-advisor needs the page URL. Add it to workflow-config.json:

```json
"notionReleaseCalendarUrl": "https://www.notion.so/[release-calendar-page-id]"
```

The page should list releases with:
- Release name (matching the git branch convention: Release/YY.MM/dev-main)
- Planned ship date
- Features assigned (Linear issue links or feature names)

---

## Bootstrapping — first 10 work cycles

For the first ~10 work cycles, the velocity-history dataset is too
small to produce reliable calibration data. During this period:

- intel-recorder still runs and collects data as normal
- intel-advisor uses phase-splitter heuristic estimates as fallback
  when calibration sample count is below threshold (5 samples per layer)
- All estimates include the "⚠ Early dataset" confidence warning
- By ~10 work cycles (roughly 30–40 phases), most layers will have
  enough samples for moderate confidence estimates

The system improves automatically. No manual intervention required.

---

## Adding .sage/intel/ to .gitignore considerations

`.sage/intel/velocity-history.jsonl` and `release-history.jsonl`
should be committed — they are the historical record that improves
estimates over time and must persist across machines.

`calibration.json` and `metrics-report.md` should also be committed —
they are derived but serve as reference points and are readable
by all developers when pulled.

Add nothing from `.sage/intel/` to `.gitignore`.
