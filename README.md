# sage-framework

**SAGE** (Semi-Autonomous Guided Execution) — framework specifications, handoff assets, and documentation for AI-assisted delivery on the Profitability codebase.

## Plugin install (no build)

This repo *is* the plugin. Both IDEs read the same files in place — there is no build step or
generated output. Components live at the repo root by convention: `agents/`, `skills/`, `rules/`,
`hooks/`, `.mcp.json`. Dual manifests live in `.claude-plugin/` and `.cursor-plugin/`.

**Claude Code** (local marketplace):
```
/plugin marketplace add <path-or-git-url to this repo>
/plugin install sage@empyrean-sage
```

**Claude Desktop** (zip upload): build a lean zip (docs/specs excluded via `.gitattributes`), then
upload it via Claude Desktop's plugin install:
```
bash scripts/package-desktop.sh        # writes sage.zip
```
Add the MCP servers via **Settings → Connectors** (Linear `https://mcp.linear.app/mcp`, Notion
`https://mcp.notion.com/mcp`).

**Cursor**: loads `agents/`/`skills/`/`rules/` from the repo root by convention; `hooks/` and
`.mcp.json` are declared in `.cursor-plugin/plugin.json`.

> Agent files carry **`name` + `description` frontmatter only** — the one form both IDEs accept in a
> shared file. Per-agent tool/model behaviour is enforced by the `hooks/` layer, not frontmatter.
> Hooks are currently Cursor-schema only; a Claude-schema hook port is a separate phase.

## Repository layout

| Path | Purpose |
|------|---------|
| [`AGENTS.md`](AGENTS.md) | **SAGE Framework Agent Catalogue** — mirrors the Profitability repo root file of the same name: agent roles, modes, and constraints. Cursor reads root `AGENTS.md` by convention. |
| [`docs/agents-profitability.md`](docs/agents-profitability.md) | **Profitability product context** — domain, architecture, coding conventions, and “what agents must not do” for the application. Keep this in sync with [`profitability-repo-files/AGENTS.md`](profitability-repo-files/AGENTS.md) (duplicate for zip handoffs). |
| [`docs/sage-reference.html`](docs/sage-reference.html) | **SAGE Reference** — offline interactive reference (tabs: Team Introduction, Sprint Reference, Tech Map, Dev Workflow, SAGE Intel, **PRD Creation**). Sync from Netlify when updating the hosted copy. |

| [`agent-definitions.md`](agent-definitions.md) | Long-form agent definitions (includes model hints); supplements `AGENTS.md`. |
| [`cursor-directory-spec/`](cursor-directory-spec/) | Expected `.cursor/` and `.sage/` directory trees for the product repo. |
| [`hooks-spec/`](hooks-spec/) | `hooks.json`, `workflow-config.json` (parity with Profitability `.sage/workflow-config.json`), [`scripts/`](hooks-spec/scripts/) mirror of **14** Python modules under `hooks/scripts/`, and narrative hook behaviour in `hook-scripts-spec.md`. |
| [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md) | Phased rollout checklist for the Lead Dev. |
| [`webhook/`](webhook/) | Linear webhook receiver for skill-update triggers. |

## Aligning with Profitability

The **Profitability** Git repository is the deployed source of truth for `.cursor/`, `.sage/workflow-config.json`, and root `AGENTS.md` (catalogue). When those change, update this repo’s mirrored files and specs so the handoff package does not drift.

## Related

- Implementation tracker: [`implementation-tracker.md`](implementation-tracker.md)
- Implementation plan: [`reference-docs/implementation-plan.md`](reference-docs/implementation-plan.md)
