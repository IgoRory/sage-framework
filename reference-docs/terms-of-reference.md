# SAGE Framework — Terms of Reference

**Framework:** SAGE (Semi-Autonomous Guided Execution)
**Team:** Profitability
**Version:** 1.0
**Status:** Approved

---

## 1. Purpose

This document establishes the terms of reference for the adoption of the SAGE (Semi-Autonomous Guided Execution) Framework by the Profitability team. It defines the framework's scope, objectives, roles, governance model, and operating principles.

---

## 2. Background

The Profitability team delivers a complex financial analytics product across a distributed team working across multiple time zones. The team identified a need for a structured approach to AI-assisted development that would:

- Produce consistent, verifiable output quality regardless of who is running a session
- Make the team's distributed structure an asset rather than a constraint
- Replace estimation-based planning with empirical delivery data
- Continuously improve how AI is used based on evidence from real sessions

The SAGE Framework is the team's response to these needs. It takes the core principles of mob programming — shared context before building, structured collaboration, continuous quality — and rebuilds them for distributed teams using AI as the primary execution resource.

---

## 3. Framework overview

SAGE provides a repeatable, enforced path from feature idea to production-ready code. It operates across four workflow modes suited to different team configurations and feature types:

| Mode | Model | Use case |
|---|---|---|
| **Mob** | Single terminal, sequential, co-located or screenshare | Collaborative builds, onboarding, features benefiting from collective judgment |
| **Sprint** | Parallel worktrees, distributed, async after kick-off | Multi-component features where parallel execution reduces delivery time |
| **Pair** | Sequential phases, two developers | Medium complexity work where knowledge transfer adds value |
| **Solo** | Single developer, no kick-off | Hotfixes, minor enhancements, contained work |

The framework has four layers:

**Execution structure** — workflow modes and eight structured build steps (S1–S8) per phase

**Enforcement** — twelve Python hook scripts that gate every step transition; steps cannot be skipped and no agent can instruct its way past a gate

**SAGE Hone** — the self-improving subsystem; observes every session via telemetry, evaluates AI performance, and proposes evidence-backed improvements to AI instructions for human approval

**SAGE Intel** — the delivery intelligence subsystem; records empirical delivery data from every session, powers planning decisions, and publishes metrics to leadership reporting surfaces

---

## 4. Scope

### In scope

- All Profitability feature development conducted by the team after framework activation
- All four workflow modes (Mob, Sprint, Pair, Solo) as appropriate per feature
- PRD authoring and completeness checking for all features entering the Sprint or Pair workflow
- SAGE Intel data collection from every completed work cycle
- SAGE Hone skill evaluation every five work cycles

### Out of scope

- Emergency hotfixes requiring immediate deployment (Solo mode with post-hoc documentation is acceptable in genuine production incidents)
- Infrastructure and DevOps work not related to Profitability feature development
- Third-party integrations owned by other teams

### Phased adoption

The Mob mode will be introduced after the Sprint and Solo modes are operating stably. The Pair mode will be introduced alongside or after Mob. The Feature Walkthrough for Sprint mode is optional initially and will become standard practice once the team is comfortable with the Sprint Kick-off process.

---

## 5. Roles and responsibilities

### Product Manager

- Authors product requirements documents using the prd-interviewer skill
- Runs prd-completeness-check and ensures features reach Ready status before the planning cycle
- Attends and facilitates the Sprint Kick-off and Mob Kick-off sessions
- Approves phase breakdowns in the issue tracker before the build phase begins
- Reviews completion reports and confirms product correctness before Review & Merge
- Approves skill updates for prd-interviewer and prd-completeness-check skills via SAGE Hone
- Runs intel-advisor at the weekly planning cycle and for release forecasting

### Lead Dev

- Owns implementation of the SAGE Framework on the Profitability codebase
- Reviews and merges pull requests in dependency order during Review & Merge
- Approves phase breakdowns in the issue tracker alongside the Product Manager
- Approves skill updates for phase-splitter and execution-layer skills via SAGE Hone
- Reviews SAGE Hone session performance reports and acts on systematic violation flags
- Maintains the framework's technical configuration and hook scripts

### Developers

- Run the S1–S8 build cycle on assigned phases during Sprint and Solo builds
- Act as Driver or Navigator in Mob mode sessions
- Choose Autonomous or Checkpoint build mode at S1
- Confirm the validation mockup at S4 by editing the session manifest
- Post completion reports to phase issues at S8

### QA (optional, pre-live)

- Attends Mob sessions as QA Observer (optional role)
- Reviews completion reports asynchronously after the build phase
- A formal QA gate will be defined before the framework goes live in a production release cycle

---

## 6. Operating principles

**Structural enforcement over agent instruction**
Quality gates are implemented as hook scripts that reject tool calls at the execution layer. They do not rely on agent compliance with instructions. An agent cannot skip a step or declare work complete without verifiable evidence.

**Artifact quality determines pipeline quality**
The highest-leverage quality investment is at PRD creation and phase breakdown — before any code is written. A feature cannot enter the build phase without a PRD scoring 80/100 or above. The component specification is a required artifact, not a best-effort addition.

**Async-first, synchronous by exception**
Synchronous sessions (Kick-offs, Feature Walkthroughs) are reserved for decisions that genuinely benefit from real-time discussion. Everything else flows asynchronously so that no team member's execution is blocked by another's schedule.

**Evidence over estimation**
No human estimation is used at any stage of planning. All effort estimates and release forecasts are derived from the SAGE Intel empirical dataset, which grows with every completed work cycle.

**Self-improvement is automatic, approval is human**
SAGE Hone proposes improvements to AI instructions based on evidence from real sessions. Every proposed change is staged for human review before being applied. The framework improves from the bottom up — no manual tuning required.

---

## 7. Governance

### Framework changes

Changes to the framework's enforcement layer (hook scripts, workflow-config.json) require approval from the Lead Dev. Changes to PRD-layer skills (prd-interviewer, prd-completeness-check) require approval from the Product Manager. These approvals are managed through SAGE Hone's skill update workflow in the issue tracker.

### Skill update approval

| Skill | Approver |
|---|---|
| prd-interviewer | Product Manager |
| prd-completeness-check | Product Manager |
| phase-splitter | Lead Dev |
| All other skills | Lead Dev |

### Violation handling

When SAGE Hone identifies a systematic violation (the same gate firing repeatedly against the same agent behaviour in a session), a Linear issue is created in the Violation workflow. The Lead Dev reviews and closes within one work cycle. Patterns that persist across multiple sessions trigger a SAGE Hone skill update proposal rather than a repeated violation flag.

### Framework review

A framework review is conducted after every ten work cycles, or after any significant change to the Profitability codebase that may affect the hook scripts or agent configurations. The review is led by the Lead Dev with input from the Product Manager.

---

## 8. Success criteria

### Adoption milestones

| Milestone | Target |
|---|---|
| First Sprint session completed | Within 2 weeks of framework activation |
| All developers running S1–S8 independently | Within 4 weeks |
| SAGE Intel calibration at Moderate confidence | After 5–9 completed phases per layer type |
| First skill update proposed and applied by SAGE Hone | Within 10 work cycles |

### Quality indicators

| Indicator | Target at steady state |
|---|---|
| Hook compliance rate | > 90% (few gate rejections) |
| TDD first-pass rate | > 70% (agent passes tests on first GREEN attempt) |
| Agent quality rate | > 80% (AI-written code survives to merge without human correction) |
| PRD completeness score at kick-off | ≥ 80/100 on first submission |
| Phase effort accuracy | Within ±20% of SAGE Intel estimate |

These targets are indicative for the first operational quarter. SAGE Intel will recalibrate based on actual delivery data.

---

## 9. Constraints and dependencies

### Technical constraints

- The framework requires Python 3.12.x on all developer machines for hook script execution
- Node.js v24.x is required for the Playwright MCP agent testing layer
- Microsoft 365 MCP access is required for the kickoff-dev-review skill to fetch Teams transcripts
- All developers must have Cursor, Linear MCP, Notion MCP, and Microsoft 365 MCP configured before the first session

### ADO transition

Work item tracking for Profitability features moves from ADO to Linear at framework activation. The transition follows a clean cut:

- Features in active ADO development: complete in ADO
- Features not yet in active development: enter the new workflow via the Linear planning cycle
- No feature splits across both systems
- CI/CD pipelines remain in ADO and are unaffected by this transition

### QA integration

The framework currently treats human QA as an optional, non-gated role. A formal QA gate will be designed and added to the workflow configuration before the framework is used in a production release cycle. This is an architectural extension, not a rebuild — the configuration supports adding a QA gate without structural changes.

---

## 10. Document control

| Version | Date | Summary of changes |
|---|---|---|
| 1.0 | 2026 | Initial version — SAGE Framework adoption for Profitability team |

All subsequent changes to this document follow the governance process in Section 7.
