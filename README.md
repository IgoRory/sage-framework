# sage-framework

**SAGE** (Semi-Autonomous Guided Execution) — framework specifications, handoff assets, and documentation for AI-assisted delivery on the Profitability codebase.

## Repository layout

| Path | Purpose |
|------|---------|
| [`AGENTS.md`](AGENTS.md) | **SAGE Framework Agent Catalogue** — mirrors the Profitability repo root file of the same name: agent roles, modes, and constraints. Cursor reads root `AGENTS.md` by convention. |
| [`docs/agents-profitability.md`](docs/agents-profitability.md) | **Profitability product context** — domain, architecture, coding conventions, and “what agents must not do” for the application. Keep this in sync with [`profitability-repo-files/AGENTS.md`](profitability-repo-files/AGENTS.md) (duplicate for zip handoffs). |
| [`docs/sage-reference.html`](docs/sage-reference.html) | **SAGE Reference** — offline interactive reference (tabs: Team Introduction, Sprint Reference, Tech Map, Dev Workflow, SAGE Intel, **PRD Creation**). Sync from Netlify when updating the hosted copy. |

| [`agent-definitions.md`](agent-definitions.md) | Long-form agent definitions (includes model hints); supplements `AGENTS.md`. |
| [`cursor-directory-spec/`](cursor-directory-spec/) | Expected `.cursor/` and `.sage/` directory trees for the product repo. |
| [`hooks-spec/`](hooks-spec/) | `hooks.json`, `workflow-config.json` (parity with Profitability `.sage/workflow-config.json`), [`scripts/`](hooks-spec/scripts/) mirror of **14** Python modules under `.cursor/hooks/scripts/`, and narrative hook behaviour in `hook-scripts-spec.md`. |
| [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md) | Phased rollout checklist for the Lead Dev. |
| [`webhook/`](webhook/) | Linear webhook receiver for skill-update triggers. |

## Aligning with Profitability

The **Profitability** Git repository is the deployed source of truth for `.cursor/`, `.sage/workflow-config.json`, and root `AGENTS.md` (catalogue). When those change, update this repo’s mirrored files and specs so the handoff package does not drift.

## Related

- Implementation tracker: [`implementation-tracker.md`](implementation-tracker.md)
- Implementation plan: [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md)
