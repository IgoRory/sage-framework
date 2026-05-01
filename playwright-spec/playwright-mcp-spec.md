# Playwright MCP Setup Specification
# Profitability — AI-Assisted Sprint Workflow

---

## Overview

Playwright is already installed in the Profitability repo
(`playwright 1.56` via Vitest + `@analogjs/vitest-angular`).
This document specifies how to configure the Playwright MCP server
for use by the S7 agent testing step, specifically the gap-analyzer
sub-agent.

### Important 2026 context: MCP vs CLI

Microsoft now recommends Playwright CLI over MCP for coding agents.
CLI is approximately 4x more token-efficient because it writes
snapshots to disk as YAML files that agents read selectively,
rather than streaming full accessibility trees into the context
window at every step.

**This workflow uses a hybrid approach:**

| Use case | Method | Why |
|---|---|---|
| Running existing test suite (S7 main) | Shell commands (`npx playwright test`) | Token-efficient, deterministic, no MCP overhead |
| Gap-analyzer exploratory testing | `@playwright/mcp@latest` MCP tools | Agent needs to observe live app state and react |

The test-runner agent runs the existing Playwright E2E tests via
shell. The gap-analyzer uses MCP tools when it needs to navigate
the live application to generate and verify additional test scenarios.

---

## Part 1 — Add Playwright MCP to .cursor/mcp.json

Add the `playwright` entry to the existing `.cursor/mcp.json`
alongside the Linear, Notion, and Microsoft 365 entries:

```json
{
  "mcpServers": {
    "linear": {
      "type": "url",
      "url": "https://mcp.linear.app/mcp",
      "name": "linear",
      "description": "Linear MCP — issue tracking, phase status, skill update approvals",
      "headers": {
        "Authorization": "Bearer ${LINEAR_API_KEY}"
      }
    },
    "notion": {
      "type": "url",
      "url": "https://mcp.notion.com/mcp",
      "name": "notion",
      "description": "Notion MCP — PRD access, documentation writes, session reports",
      "headers": {
        "Authorization": "Bearer ${NOTION_API_KEY}"
      }
    },
    "microsoft365": {
      "type": "url",
      "url": "https://microsoft365.mcp.claude.com/mcp",
      "name": "microsoft365",
      "description": "Microsoft 365 MCP — Teams transcript retrieval for kickoff-dev-review",
      "headers": {
        "Authorization": "Bearer ${M365_ACCESS_TOKEN}"
      }
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser", "chromium",
        "--headless",
        "--base-url", "${PROFITABILITY_BASE_URL}"
      ],
      "description": "Playwright MCP — browser automation for gap-analyzer exploratory testing in S7",
      "env": {
        "PLAYWRIGHT_BASE_URL": "${PROFITABILITY_BASE_URL}"
      }
    }
  }
}
```

---

## Part 2 — Environment variable

Add `PROFITABILITY_BASE_URL` to developer machine environment variables:

```powershell
# Local development server URL for the Angular app
[System.Environment]::SetEnvironmentVariable(
  "PROFITABILITY_BASE_URL",
  "https://localhost:4200",
  "User")
```

This is the URL the gap-analyzer agent navigates to when running
exploratory tests. Set it to the local dev server URL on each
developer machine. If the team uses a shared dev environment, set
it to that URL instead.

---

## Part 3 — Install Playwright browsers

The Playwright MCP server needs browser binaries installed. The
MCP server auto-installs them on first use, but pre-installing
avoids a delay at the start of the first S7 session:

```powershell
# From the repo root
npx playwright install chromium
```

Chromium only — the Profitability app is a business application
tested on Chrome/Edge. No need for Firefox or WebKit unless the
testing strategy doc specifies otherwise.

Run this once per developer machine.

---

## Part 4 — Playwright configuration for the Profitability app

The existing Playwright config lives at:
`Web/ProfitabilityWeb/playwright.config.ts`

The gap-analyzer reads this file to understand how the app is
configured for E2E testing. No changes to the existing config
are required for MCP to work.

**Authentication handling:**

The Profitability app uses OIDC (`oidc-client`). Playwright E2E
tests need to handle the OIDC auth flow before testing protected
routes. Check the existing Playwright test for the established
auth approach:

```powershell
# Find existing E2E test files
Get-ChildItem -Path "Web\ProfitabilityWeb" -Recurse -Filter "*.spec.ts" |
  Where-Object { $_.FullName -notmatch "node_modules" }
```

The gap-analyzer agent reads the existing E2E test file to
understand the established auth pattern before writing new
gap scenarios. It does not re-implement auth — it reuses the
existing pattern.

---

## Part 5 — How S7 uses Playwright

### Test-runner agent — existing test suite

The test-runner agent runs the existing Playwright E2E tests via
shell command (not MCP). This is the token-efficient path:

```powershell
# From Web/ProfitabilityWeb/
npx playwright test --reporter=json > playwright-results.json
```

Results are written to a JSON file, parsed, and incorporated into
`phase-N-test-results.md` alongside the unit test results.

If there are no existing Playwright E2E tests for the feature
being built, the test-runner notes this in the results file and
the gap-analyzer handles exploratory coverage.

### Gap-analyzer agent — exploratory testing via MCP

The gap-analyzer uses the Playwright MCP tools to:
1. Navigate to the feature's URL in the running app
2. Observe the page structure via accessibility snapshots
3. Interact with components to verify states match the component spec
4. Check error states by providing invalid inputs
5. Verify empty states by filtering to produce no results

**Gap-analyzer MCP tool usage pattern:**

```
1. browser_navigate to the feature page
2. browser_snapshot to observe the accessibility tree
3. browser_click / browser_type to interact with components
4. browser_snapshot again to observe state changes
5. Compare observed behaviour to the component specification
6. Write new test scenarios for any gaps found
7. Execute the new scenarios via browser_run_code for automatable ones
```

**What the gap-analyzer looks for:**

- Component states not covered by the TDD spec
  (loading states, disabled states, empty option dropdowns)
- Validation behaviour under invalid input
  (percentages > 100%, negative values, empty required fields)
- Cross-component interactions
  (does filtering one component correctly update another?)
- Permission boundary behaviour
  (if testable with the auth setup available)
- Profitability-specific edge cases:
  - ProcessID not found in dropdown
  - Allocation weights not summing to 100%
  - AsOfDate outside valid range
  - GL code boundary values

---

## Part 6 — Headed vs headless

The MCP config above uses `--headless`. For most S7 gap analysis
this is appropriate — the agent doesn't need to see the browser
to interact with it via the accessibility tree.

**Override to headed for debugging:**

If a gap-analyzer run produces unexpected results and a developer
wants to observe what the agent is seeing:

```powershell
# Start a headed Playwright MCP server manually for debugging
npx @playwright/mcp@latest --browser chromium --base-url https://localhost:4200
```

Then invoke the gap-analyzer agent in Cursor — it will use the
already-running MCP server in headed mode.

---

## Part 7 — Per-developer machine setup checklist

Add to the existing developer machine setup checklist:

- [ ] `npx playwright install chromium` (run from repo root)
- [ ] Set `PROFITABILITY_BASE_URL` environment variable
- [ ] Restart Cursor to pick up updated `mcp.json`
- [ ] Confirm Playwright MCP appears in Cursor Settings → MCP

**Verify the MCP is working:**

In a Cursor agent chat:
```
Use the playwright MCP to navigate to ${PROFITABILITY_BASE_URL}
and take a snapshot of the page.
```

If the accessibility snapshot comes back correctly, the MCP is
configured and working.

---

## Part 8 — The featureFlag connection

Playwright operations in S7 are gated by `featureFlags.playwrightE2E`
in `workflow-config.json`:

```json
"featureFlags": {
  "playwrightE2E": false
}
```

The test-runner and gap-analyzer agents check this flag before
attempting any Playwright operation. If `featureFlags.playwrightE2E`
is `false`, S7 runs unit tests only and skips all Playwright steps.

**After completing this setup, flip the flag to `true`:**

```json
"featureFlags": {
  "playwrightE2E": true
}
```

> Note: `workflow-config.json` already has `"playwrightE2E": true`
> set after the initial SAGE setup. Confirm this is correct before
> the first S7 session.

---

## Part 9 — Local dev server requirement

The gap-analyzer navigates the live running application.
This requires the Angular dev server to be running before S7
starts.

**The dev server is the developer's responsibility** — the workflow
does not automatically start it. Before the build sprint (S1),
the developer running the Angular phase should confirm the dev
server is running:

```powershell
cd Web\ProfitabilityWeb
ng serve
# or: npm start
```

The dev server must be running on port 4200 (or wherever
`PROFITABILITY_BASE_URL` points) throughout the build sprint.

If the Angular phase is not in the current work stream (e.g. the
current phase only touches `Database/` and `Services/`), the
gap-analyzer skips browser-based testing and relies on unit and
stored procedure tests only.

---

## Summary of changes to existing files

| File | Change |
|---|---|
| `.cursor/mcp.json` | Add `playwright` server entry |
| `workflow-config.json` | Set `featureFlags.playwrightE2E = true` after setup |
| Agent definitions | `test-runner.md` and `gap-analyzer.md` already reference Playwright — no changes needed |
| Developer machine setup checklist | Add `npx playwright install chromium` and `PROFITABILITY_BASE_URL` |
