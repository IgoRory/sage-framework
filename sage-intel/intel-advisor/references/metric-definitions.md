# Metric Definitions
# Profitability Workflow — Authoritative Standard

This document defines every metric produced by the capacity planning
system. Definitions are precise and implementation-independent —
any team adopting this workflow framework produces the same metrics
from the same raw data.

Status: Profitability-level standard. Promotable to org-level when
other teams adopt the workflow.

---

## Phase-level metrics

### Phase effort accuracy
**Definition:** The ratio of actual phase duration to the phase-splitter's
p50 estimate at kick-off.
**Formula:** `actualHours / estimatedHoursP50`
**Interpretation:**
- 1.0 = estimate was exactly right
- > 1.0 = phase took longer than estimated
- < 1.0 = phase completed faster than estimated
**Aggregation:** Mean across phases in a feature or release.
**Notes:** Measured against p50 (midpoint of low-high range), not the
low or high bound.

### Phase cycle time
**Definition:** Elapsed time from S1 dev interview start to S8 completion
report posted, in hours.
**Formula:** `S8.completedAt - S1.startedAt`
**Source:** Manifest step timestamps.
**Notes:** Includes all time including waits between steps. Does not
include time waiting for Linear approval (that is approval turnaround).

### Agent code ratio
**Definition:** Proportion of lines added to production files that were
written by agent execution rather than human keyboard input.
**Formula:** `agentLinesAdded / (agentLinesAdded + humanLinesAdded)`
**Source:** Git diff analysis. Commits before PR open timestamp = agent.
Commits after PR open timestamp = human.
**Scope:** Production source files only. Excludes: test files, config
files, documentation, `.sage/` artifacts.
**Notes:** A ratio of 0.95 means 95% of production code changes were
agent-written.

### Agent quality rate
**Definition:** Proportion of agent-written code that survived to merge
without human rework.
**Formula:** `1 - (humanLinesAdded / (agentLinesAdded + humanLinesAdded))`
**Notes:** Equivalent to agent code ratio when looking at it from the
quality angle. A quality rate of 0.90 means 90% of the agent's code
needed no human correction before merge.

### Rework rate
**Definition:** Proportion of phases where any build step was re-entered
after initial completion due to a gate failure or correction.
**Formula:** `phasesWithRework / totalPhases`
**Source:** Manifest step status history — steps that transition from
`complete` back to `in-progress`.
**Notes:** A rework event is significant. A rework rate above 20%
suggests upstream artifact quality issues (PRD gaps surfacing during build).

### Hook compliance rate
**Definition:** Proportion of phase runs with zero hook rejection events.
**Formula:** `phasesWithZeroViolations / totalPhases`
**Source:** Telemetry `hook_rejection` events.
**Notes:** A rate of 1.0 means every phase proceeded without the agent
attempting a disallowed action. Lower rates indicate agents are testing
boundaries, which may signal system prompt refinement opportunities.

### TDD first-pass rate
**Definition:** Proportion of TDD RED cycles where the GREEN
implementation passed on the first attempt.
**Formula:** `tasksPassingGreenFirstAttempt / totalTasks`
**Source:** Telemetry afterShellExecution events in the build step.
**Notes:** High first-pass rates indicate the implementation plan
(S2) was well-formed. Low rates suggest the plan did not resolve
enough ambiguity before build.

---

## Feature-level metrics

### Feature cycle time
**Definition:** Elapsed time from the feature's Linear issue reaching
`Ready` status to reaching `Done` status, in calendar days.
**Formula:** `(Done.timestamp - Ready.timestamp) / 86400`
**Source:** Linear issue status transition log.
**Notes:** Measures the full delivery cycle including planning cycle
wait time. Features that sit at `Ready` for multiple planning cycles
before being pulled will have longer cycle times — this is a signal
about backlog management, not execution speed.

### Phase count accuracy
**Definition:** Whether the actual number of phases executed matched
the number planned at kick-off.
**Formula:** Boolean — `actualPhaseCount == plannedPhaseCount`
**Source:** Manifest completion log vs. initial phase breakdown.
**Notes:** Frequent phase count overruns suggest the phase-splitter
is underestimating feature scope at kick-off, which may indicate
PRD quality issues (features that expand once implementation begins).

### Parallel execution efficiency
**Definition:** How efficiently the parallel execution model was used.
A value of 1.0 means the team achieved the theoretical minimum calendar
time given the dependency structure.
**Formula:** `criticalPathHours / sum(allPhaseActualHours)`
**Source:** Phase start/end timestamps from telemetry.
**Notes:** Values well below 1.0 indicate phases that could have run
in parallel did not — possibly due to developer availability, coordination
friction, or dependency ordering issues.

### Approval turnaround
**Definition:** Mean elapsed time between a phase issue being created
at kick-off (status: Pending Approval) and reaching Approved status.
**Formula:** `mean(Approved.timestamp - PendingApproval.timestamp)`
across all phases in the feature.
**Notes:** **Team-only metric — not published to Head of Product or CTO.**
Surfacing this externally could be interpreted as measuring individual
performance (the Product Manager or Lead Dev). Used internally to understand the approval
bandwidth constraint on delivery speed.

---

## Release-level metrics

### Release date accuracy
**Definition:** How closely the actual release date matched the planned
date recorded in the Notion Release Calendar.
**Formula:** `actualDate - plannedDate` in calendar days.
Positive = late. Negative = early.
**Source:** Notion Release Calendar (planned date) + date last feature
merged to main (actual date).

### Scope delivery rate
**Definition:** Proportion of features planned for a release that were
actually shipped in that release.
**Formula:** `featuresShipped / featuresPlanned`
**Notes:** Features deferred to a later release count against this metric.
A rate of 1.0 means every planned feature shipped. Features added to the
release after initial planning that also shipped are included in both
numerator and denominator.

### Release velocity
**Definition:** Total effort hours invested across all phases in a release.
**Formula:** `sum(actualHours)` across all phases across all features
in the release.
**Notes:** Not a productivity measure on its own. Most useful in
combination with scope delivery rate and feature count to understand
the cost of a release. Trends over multiple releases indicate whether
releases are growing or shrinking in scope.

---

## Organisation-level metrics (for future rollup)

These metrics are calculated at Profitability level today. When
promoted to org standard, they aggregate across all teams using
the workflow.

### Workflow adoption rate
**Definition:** Proportion of work streams using the AI-assisted Sprint
workflow vs. any other workflow.
**Formula:** `workStreamsUsingWorkflow / totalWorkStreams`
**Source:** Linear label tracking — work streams using the workflow
have `mode` custom field set.
**Notes:** Tracked at team level currently. Org-level aggregation
requires a shared Linear workspace view or a cross-team reporting
layer.

### Cross-team effort accuracy
**Definition:** Mean phase effort accuracy across all teams using
the workflow. Measures whether the estimation system is calibrated
consistently across different products and codebases.
**Formula:** `mean(effortAccuracy)` across all phases across all
teams.
**Notes:** If different teams show systematically different accuracy
patterns, it may indicate that the phase-splitter heuristics need
team-specific calibration rather than universal defaults.

---

## Metric ownership

| Metric | Published to | Owner |
|---|---|---|
| Phase effort accuracy | Notion + Linear | intel-recorder |
| Phase cycle time | Notion + Linear | intel-recorder |
| Agent code ratio | Notion + Linear | intel-recorder |
| Agent quality rate | Notion + Linear | intel-recorder |
| Rework rate | Notion + Linear | intel-recorder |
| Hook compliance rate | Notion + Linear | intel-recorder |
| TDD first-pass rate | Linear only | intel-recorder |
| Feature cycle time | Notion + Linear | intel-recorder |
| Phase count accuracy | Linear only | intel-recorder |
| Parallel execution efficiency | Linear only | intel-recorder |
| Approval turnaround | Internal (.sage/intel/) only | intel-recorder |
| Release date accuracy | Notion + Linear | intel-recorder |
| Scope delivery rate | Notion + Linear | intel-recorder |
| Release velocity | Notion + Linear | intel-recorder |
| Workflow adoption rate | Notion | intel-recorder |

---

## Data retention

`velocity-history.jsonl` — retained indefinitely. Every phase record
is permanent. This is the historical dataset that improves estimates
over time.

`release-history.jsonl` — retained indefinitely.

`calibration.json` — regenerated after every work cycle. Previous
versions are not retained (it is always derived from velocity-history).

`metrics-report.md` — regenerated after every work cycle. Not versioned.
