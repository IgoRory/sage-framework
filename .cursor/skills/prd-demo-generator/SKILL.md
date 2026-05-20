---
name: prd-demo-generator
description: >
  Generates interactive HTML demos from a completed PRD draft. Reads the PRD's
  acceptance criteria (AC-REQ, AC-EC, AC-UI, AC-ERR) and component specification
  to produce self-contained HTML files that visualise every demoable scenario.
  Optional step invoked by the PM between prd-interviewer and
  prd-completeness-check. Regenerate on demand when the PRD changes. Writes to
  .sage/prds/[FEATURE_ID]/demos/. Use this skill when the PM says "generate a
  demo", "create an HTML demo", "visualise the PRD", "show me what this looks
  like", or "regenerate the demo".
---

# PRD Demo Generator

Produces interactive HTML demos from a completed PRD. This is an **optional**
step that the PM invokes between prd-interviewer (PRD draft complete) and
prd-completeness-check (PRD scored for readiness). It can be re-invoked any
time the PRD is edited to regenerate demos from the updated requirements.

---

## Position in pipeline

```
prd-interviewer → PRD Draft → [PM invokes prd-demo-generator] → Demo HTML
                                                                    ↓
                                                              PM reviews demo
                                                                    ↓
                                                         prd-completeness-check
```

The demo is never required for the completeness check to pass. It is a
visualisation aid that helps the PM validate requirements before scoring.

---

## Invocation phrases

Treat this skill as invoked when the PM says any of:
- "generate a demo", "create an HTML demo", "prd-demo-generator"
- "show me what this looks like", "visualise the PRD"
- "regenerate the demo" (when demo exists and PRD has changed)

---

## Prerequisites

Before generating, verify:
1. **Linear issue context:** Confirm the FEATURE_ID corresponds to a Linear
   issue (e.g. `PROF-354`). The FEATURE_ID is derived from the PRD's Linear
   issue reference in Section 1. If no Linear issue is referenced in the PRD,
   ask the PM to provide one before proceeding.
2. PRD exists at `.sage/prds/[FEATURE_ID]/prd.md`
3. PRD contains Section 8 with categorised ACs (AC-REQ, AC-EC, AC-UI, AC-ERR)
4. If the PRD has no Section 8 ACs: tell the PM the PRD is not ready for
   demo generation and suggest running prd-completeness-check first

If a component specification exists at `.sage/prds/[FEATURE_ID]/component-spec.md`,
read it for UI component details.

---

## Step 1 -- Read PRD and component specification

Read the PRD and extract:
- All acceptance criteria from Section 8, grouped by category (AC-REQ, AC-EC,
  AC-UI, AC-ERR)
- Feature title and description (Section 1)
- UI screen inventory (Section 10, if present)
- Edge cases (Section 11)
- Component specification (separate file, if present)

Record the total AC count and which ACs are demoable vs. not demoable.

---

## Step 2 -- Classify demo type

Based on the PRD content, determine which demo files to generate:

| PRD content | Demo file(s) | Decision |
|---|---|---|
| Section 10 present (UI screens/components) | `demo-interactive.html` | Generate |
| Section 6 present (calculation logic) | `calculation-demo.html` | Generate |
| Both UI and calculation | Both files | Generate both |
| Backend-only (no Section 10, no Section 6) | None | Skip -- tell PM no demo needed |

If the classification is unclear, ask the PM: "This PRD has [description].
Should I create an interactive UI demo, a calculation logic demo, or both?"

---

## Step 3 -- Read codebase for styling accuracy

Before generating the demo HTML, read the codebase to ensure visual accuracy:

**For Tier 1 (existing UI modifications):**
- Read `_variables.scss` for exact colours, fonts, spacing
- Read `_common.scss` for shared component styles
- Read relevant component `.html` templates for exact HTML structure
- Read TypeScript prefab/config files for exact button text, icon classes
- Read toast/notification code for exact message text
- Read confirmation dialog code for exact dialog titles, body text, buttons

**For Tier 2 (new UI with no existing counterpart):**
- Read `_variables.scss` for the app's colour palette as baseline
- Design direction is intentional and distinctive (see references/styling-tiers.md)

**Message text sourcing (mandatory):**
All user-facing text in the demo must follow the 3-tier protocol:
1. Codebase-sourced: quote verbatim with source reference
2. Agent-proposed: propose text grounded in patterns, marked `[Proposed]`
3. Undetermined: mark as `[TEXT TBD]`

---

## Step 4 -- Generate demo HTML

Generate a single self-contained HTML file per demo type. Follow the structure
defined in references/demo-structure.md.

**Output location:** `.sage/prds/[FEATURE_ID]/demos/`

**File naming:**
- `demo-interactive.html` (UI demos)
- `calculation-demo.html` (calculation demos)

**Scenario naming:** Use the SAGE AC-ID scheme directly:
- "AC-REQ-001: [AC name from PRD]"
- "AC-EC-003: [AC name from PRD]"
- "AC-UI-005: [AC name from PRD]"
- "AC-ERR-002: [AC name from PRD]"

Group scenarios in the selector by AC category (Requirements, Edge Cases,
UI States, Error/Recovery).

**Technical requirements:**
- Single self-contained HTML file with embedded `<style>` and `<script>`
- Only external dependencies: FontAwesome + Google Fonts via CDN
- Must work offline after initial CDN load
- No build tools, no server, no frameworks -- pure vanilla JS
- Clean, well-structured code

---

## Step 5 -- Self-review

After generating the demo, perform a functional review:

1. Verify every demoable AC has a scenario in the selector
2. Verify scenario names match AC-IDs from the PRD exactly
3. Verify the AC text sidebar shows correct Given/When/Then for each scenario
4. Verify interactive elements (buttons, state transitions) work correctly
5. Verify toast messages and dialogs use exact text (codebase-sourced or marked)
6. Verify switching between scenarios clears previous state cleanly
7. Verify the scenario search/filter works

If any issue is found, fix it before proceeding.

---

## Step 6 -- Write drift hash

Compute the SHA-256 hash of the PRD file content and embed it in the HTML
file as an HTML comment in the first 5 lines:

```html
<!-- prdHash: [SHA-256 hex string] -->
<!-- Generated from: .sage/prds/[FEATURE_ID]/prd.md -->
<!-- Generated at: [ISO UTC timestamp] -->
```

This allows prd-completeness-check to detect when the demo is stale relative
to the current PRD.

---

## Step 7 -- Write demo-coverage.md

Write a companion file to `.sage/prds/[FEATURE_ID]/demos/demo-coverage.md`:

```markdown
# Demo Coverage Report

**Feature:** [Feature title]
**Generated:** [ISO date]
**PRD hash:** [SHA-256]

## Scenarios Demoed

| AC ID | Name | Demo File | Status |
|-------|------|-----------|--------|
| AC-REQ-001 | [name] | demo-interactive.html | Demoed |
| AC-EC-003 | [name] | demo-interactive.html | Demoed |
| ... | | | |

## Scenarios Not Demoed

| AC ID | Name | Reason |
|-------|------|--------|
| AC-REQ-005 | [name] | Requires backend execution -- not visualisable |
| AC-EC-007 | [name] | Multi-browser concurrency -- cannot simulate in single HTML |
| ... | | |

## Summary

- Total ACs: [N]
- Demoed: [N] ([%])
- Not demoed: [N] ([%])
```

---

## Step 8 -- Emit telemetry

Append a telemetry event to the PRD telemetry file (configured in
`.sage/workflow-config.json`, default `.sage/prd-interview-telemetry.jsonl`):

```json
{
  "timestamp": "[ISO UTC]",
  "event": "prd_demo_generated",
  "workflowKind": "prd_demo",
  "linearIssueId": "[FEATURE_ID]",
  "prdHash": "[SHA-256]",
  "demoType": "interactive|calculation|both",
  "scenariosDemoed": [N],
  "scenariosSkipped": [N],
  "outputPath": ".sage/prds/[FEATURE_ID]/demos/"
}
```

---

## Step 9 -- Present to PM

Tell the PM:
"Demo generated and saved to `.sage/prds/[FEATURE_ID]/demos/`:
- [list files created]
- [N] of [total] acceptance criteria demoed ([%] coverage)
- [N] ACs could not be demoed (see demo-coverage.md for reasons)

Open the HTML file in any browser to review. If you edit the PRD after
this point, invoke prd-demo-generator again to regenerate."

---

## Regeneration behaviour

When invoked and a demo already exists:
1. Check prdHash in existing demo vs current PRD hash
2. If they match: "The demo is up to date with the current PRD. Regenerate
   anyway?" (wait for PM confirmation)
3. If they differ: "The PRD has changed since the demo was generated.
   Regenerating now." (proceed immediately)
4. On regeneration: overwrite existing demo files and update demo-coverage.md

---

## Constraints

- **Path containment:** FEATURE_ID must be validated before any filesystem
  write. Reject any FEATURE_ID containing path separators (`/`, `\`),
  traversal sequences (`..`), or characters outside `[A-Za-z0-9_-]`.
  Resolve the output path to an absolute path and verify it is within
  `.sage/prds/` before writing. Abort with an error if validation fails.
- Read-only access to codebase (SCSS, templates, message text) -- never
  modify application source code
- Write access only to `.sage/prds/[FEATURE_ID]/demos/`
- Never modifies the PRD or component specification
- Must read the PRD's Section 8 ACs as the authoritative scenario list --
  do not invent scenarios that are not in the PRD
- All user-facing text follows the 3-tier message text sourcing protocol
- Styling follows the two-tier strategy (see references/styling-tiers.md)
- Demo HTML structure follows references/demo-structure.md

---

## Reference files

Read references/demo-structure.md for:
- Complete demo HTML structure specification
- Scenario selector, AC sidebar, search, interactive elements
- Animation engine and action log panel requirements

Read references/styling-tiers.md for:
- Tier 1 vs Tier 2 classification rules
- Styling accuracy requirements per tier
- Anti-patterns to avoid
