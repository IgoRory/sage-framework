---
name: prd-completeness-check
description: >
  Scores a PRD for machine-readability and sprint-session readiness across
  six dimensions: requirement coverage, AC specificity, edge/empty/error
  state coverage, mockup file completeness, UI component specification, and
  out-of-scope clarity. Produces a dimension-by-dimension remediation report
  and sets the Linear feature issue status to Ready when the score meets
  threshold. Use this skill whenever a PRD needs to be assessed for
  planning-cycle eligibility. Do not proceed to planning-cycle assignment
  without running this skill first.
---

# PRD Completeness Check

Assesses a PRD for readiness to enter the planning cycle. A PRD must score
>= 80/100 across six dimensions before its Linear feature issue can be set
to Ready. Below threshold, the skill produces a remediation report detailing
exactly what must be fixed before re-assessment.

Critical distinction this skill enforces: a mockup shows what a UI looks
like. A component specification defines what it does, what states it can be
in, and how users interact with it. These are separate artifacts with
separate requirements. A passing mockup check does not substitute for a
passing component specification check.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| PRD content | Notion page URL | Yes |
| Component specification | Notion child page linked from PRD | Yes (UI features) |
| Screen inventory | Embedded in PRD | Yes (UI features) |
| Mockup file paths | Repo paths listed in PRD | Yes (UI features) |

---

## Six scoring dimensions

| Dimension | Points | What it assesses |
|-----------|--------|-----------------|
| D1 - Requirement coverage | 15 | All requirements as explicit, testable predicates |
| D2 - AC specificity | 15 | Each requirement has at least one agent-evaluable AC |
| D3 - Edge/empty/error state coverage | 15 | Non-happy-path states for every functional area |
| D4 - Mockup file completeness | 15 | All screens committed to repo at stated paths |
| D5 - UI component specification | 25 | Full spec for every new/affected component |
| D6 - Out-of-scope clarity | 15 | Explicit out-of-scope section preventing scope creep |
| Total | 100 | |

Pass threshold: 80/100. Threshold is auto-calibrated over time by the
skill-effectiveness-evaluator -- do not hardcode 80 in any downstream logic.

---

## Step 1 -- Fetch and read all inputs

Fetch the PRD from Notion using the provided URL.
Fetch the component specification child page (linked from the PRD).
Identify the screen inventory section in the PRD.
Identify all mockup file paths listed in the PRD.

If no component specification page is linked, record D5 = 0/25 immediately
and continue scoring the remaining dimensions.

---

## Step 2 -- Score each dimension

### D1 -- Requirement coverage (15pts)

Read every requirement statement in the PRD. For each:

PASS condition: the requirement is a testable predicate -- it specifies
a precise condition and a precise outcome with no vague qualifiers.

Deductions:
- Vague qualifier (responsive, appropriate, correctly, seamlessly,
  efficiently, properly, well): -2 per instance
- Unstated assumption (references something not defined in this PRD
  or any linked document): -3 per instance
- Missing requirement (screen or function visible in mockup but absent
  from requirements): -5 per missing item

Record the count of each deduction type.

Message text sourcing check:
- User-facing message text (toast messages, error messages, tooltip text,
  dialog titles and body text, validation messages) that is not sourced
  from the codebase with a file reference and is not marked as
  `[TEXT TBD — requires PM decision]`: -2 per instance
- This check applies to all message text in the PRD requirements section,
  acceptance criteria, edge cases section, and component specification

### D2 -- AC specificity (15pts)

For each requirement, verify it has at least one acceptance criterion that
an agent can evaluate as pass/fail without human interpretation.

PASS condition: the AC states an explicit input, an explicit action or
condition, and an explicit measurable output.

Deductions:
- AC that requires human judgment to evaluate (e.g., "looks correct",
  "feels natural"): -3 per AC
- Requirement with no AC at all: -5 per requirement

### D3 -- Edge/empty/error state coverage (15pts)

For every functional area in the PRD, verify that the following states
are specified where applicable:

- Empty state: what the UI or output looks like when there is no data
- Error state: what happens when an operation fails
- Loading/processing state: what is shown while data is being fetched
- Boundary condition: behaviour at input extremes (zero, null, max value)

For Profitability calculation features: also check that return codes
-1 through -8 are handled and that the behaviour for each is specified.

Additionally, for features classified Tier 2 or above (see
prd-interviewer/references/complexity-classifier.md), check that the PRD's
edge cases section covers the applicable edge-case categories:

| Category | Applicable when |
|---|---|
| Interaction sequence | Feature has 2+ user-triggered actions |
| Cascading behaviour | Feature creates or modifies entities referenced by other components |
| Concurrency | Feature modifies shared state (records, configuration, calculations) |
| State boundary | Feature has components with multiple states |
| Cross-component dependency | Feature has upstream or downstream dependencies |
| Data integrity | Feature creates or modifies persistent data |
| Failure and recovery | Feature involves operations that can fail (SP calls, API requests, data writes) |

Deductions:
- Missing empty state for a data-displaying component: -3
- Missing error state for an operation that can fail: -3
- Missing return code handling for a calculation feature: -4 per
  unhandled return code range
- Applicable edge-case category with zero edge cases documented: -2
  per category (Tier 2+ features only)
- Feature classified Tier 3+ with fewer than 3 applicable categories
  addressed: -5

### D4 -- Mockup file completeness (15pts)

Read the screen inventory from the PRD. For each screen listed:

Check that a mockup file path is specified in the PRD.
Check that the file exists at that path in the repository.

Deductions:
- Screen listed in inventory but no mockup path specified: -5
- Mockup path specified but file does not exist at that path: -5
- Screen visible in a mockup but absent from the screen inventory: -3

Note: this dimension checks existence only. Visual quality and annotation
are not assessed here -- that is covered in D5.

### D5 -- UI component specification (25pts)

Read the component specification Notion child page. For every new or
affected UI component on every affected page:

Each component must document all six elements:

1. Component name and type (e.g., "ProcessSelector -- multi-select dropdown")
2. Functional description in predicate form -- what it does, not what
   it looks like. FAIL example: "A blue dropdown that shows options."
   PASS example: "Filters the result set to the selected ProcessIDs.
   When no ProcessID is selected, all instruments are shown."
3. All states with transition triggers. Minimum requirements by type:
   - Dropdown/select: default, open, selected, disabled, error
   - Table/grid: populated, empty, loading, error
   - Button: default, hover, active, disabled, loading
   - Form field: default, focused, filled, error, disabled
   - Modal/panel: hidden, visible, loading, error
4. User interactions: every action the user can take and what it does
5. Selectable options: for any component with selectable values, list
   all options or the data source they are populated from
6. Data binding: which specific data fields populate this component.
   For Profitability components: name the Adjusted_GL field, ProcessID,
   or stored procedure (SP) explicitly by name -- generic references
   like "the calculation result" do not pass.

Scoring:
Each component is worth (25 / total component count) points, rounded.
For each component, score 0-6 elements present. Partial credit applies:
each missing element reduces that component's share proportionally.

Special cases:
- If no component specification page exists: D5 = 0/25 automatically.
  Record finding: "No component specification page linked from PRD."
- If the page exists but contains no entries: D5 = 0/25.
  Record finding: "Component specification page is empty."
- Reused components (not modified by this feature): skip D5 check.
  Only new or modified components are assessed.

### D6 -- Out-of-scope clarity (15pts)

Verify the PRD contains an explicit out-of-scope section that:
- Lists at least one item that is explicitly out of scope
- Uses language precise enough that a build agent would not implement it
- Covers any adjacent functionality that might be confused with in-scope

Deductions:
- No out-of-scope section at all: -15 (full deduction)
- Out-of-scope section present but vague (e.g., "performance is out of
  scope"): -7
- Missing entry for an obvious adjacent feature visible in the mockup
  but not covered by requirements: -5

---

## Step 3 -- Calculate total score

Sum all dimension scores. Apply the pass/fail threshold.

Current threshold: 80/100. This threshold is calibrated by the
skill-effectiveness-evaluator and may change over time. Read the current
threshold from .sage/workflow-config.json field prd.completenessThreshold
if available -- fall back to 80 if not set.

---

## Step 4 -- Update Linear and produce report

If score >= threshold:
  Update the Linear feature issue status to Ready via Linear MCP.

Write the assessment report using this exact format:

``````
PRD COMPLETENESS ASSESSMENT
Feature: [Linear issue ID] -- [Feature title]
Date: [ISO date]
Assessed by: prd-completeness-check

SCORE: [total]/100  [PASS / FAIL]
Threshold: [N]/100

DIMENSION SCORES
D1 Requirement coverage      [N]/15   [OK / N findings]
D2 AC specificity            [N]/15   [OK / N findings]
D3 Edge/empty/error states   [N]/15   [OK / N findings]
D4 Mockup completeness       [N]/15   [OK / N findings]
D5 UI component spec         [N]/25   [OK / N findings]
D6 Out-of-scope clarity      [N]/15   [OK / N findings]

FINDINGS
[Dimension] -- [Finding description] -- [Points deducted]
...

MOCKUP FILE CHECK
[Screen name]   [expected path]   [EXISTS / MISSING]
...

COMPONENT SPECIFICATION COVERAGE
[Component]   [Elements present N/6]   [Missing elements]
...

[If PASS:]
Linear issue status updated to Ready.
This PRD is eligible for the next planning cycle.

[If FAIL:]
Linear issue status NOT updated.
Resolve all findings above and re-run prd-completeness-check.
[N] finding(s) require attention before this PRD can reach Ready.

[If re-assessment, append:]
Prior score: [N]/100 ([date of prior assessment])
Delta: [+N / -N] points
Resolved since last assessment: [list]
Still open: [list]
``````

---

## Reference files

Read references/scoring-rubric.md when you need:
- Detailed sub-criteria and worked examples for each dimension
- Minimum state requirements by component type (D5)
- Profitability-specific data binding examples (Adjusted_GL, ProcessID,
  stored procedures, Pyramid data model)
- How to handle reused components, non-UI features, absent screen
  inventories, and re-assessments

