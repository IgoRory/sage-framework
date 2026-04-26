---
name: prd-completeness-check
description: >
  Scores a PRD for machine-readability and hive-session readiness across six
  dimensions: requirement coverage, AC specificity, edge/empty/error state
  coverage, mockup file completeness, UI component specification, and
  out-of-scope clarity. Produces a dimension-by-dimension remediation report
  and sets the Linear feature issue status to Ready when the score meets
  threshold. Use this skill whenever a PRD needs to be assessed for
  planning-cycle eligibility, whenever a developer or PM asks "is this PRD
  ready?", or whenever a feature issue is being proposed for an upcoming work
  cycle. Do not proceed to planning-cycle assignment without running this
  skill first.
---

# PRD Completeness Check

Assesses a PRD for readiness to enter the planning cycle. A PRD must score
≥ 80/100 across six dimensions before its Linear feature issue can be set
to `Ready`. Below threshold, the skill produces a remediation report
detailing exactly what must be fixed before re-assessment.

**Critical distinction this skill enforces:**
A mockup (interactive HTML file) shows what a UI looks like. A component
specification defines what it does, what states it can be in, and how users
interact with it. These are separate artifacts with separate requirements.
A passing mockup check does not substitute for a passing component
specification, and vice versa.

---

## Inputs required

Before scoring, confirm you have access to all four inputs. If any are
missing, request them before proceeding — do not estimate or assume.

| Input | Source | Required |
|---|---|---|
| PRD content | Notion page URL | Yes |
| Component specification | Notion child page linked from PRD | Yes |
| Screen inventory | Embedded in PRD (explicit list of all screens) | Yes |
| Mockup file paths | Repo paths listed in PRD or provided separately | Yes |

---

## Step 1 — Load the PRD and linked artifacts

Fetch the full PRD content via the Notion MCP. Retrieve all child blocks
and follow any linked child pages. Confirm the following structural elements
are present before scoring. If any are absent, record them as automatic
failures in the relevant dimension — do not proceed to scoring that dimension
without attempting to locate the content first.

- [ ] Requirements section (numbered or bulleted list of functional requirements)
- [ ] Acceptance criteria (per requirement or grouped — may be inline or in a child page)
- [ ] Screen inventory (explicit list of all screens with names and mockup paths)
- [ ] Mockup file references (repo path for each screen)
- [ ] Component specification (Notion child page, explicitly linked from PRD)
- [ ] Out-of-scope section

If the component specification child page is absent or not linked, record
D5 = 0/25 automatically and note it prominently in the report. All other
dimensions continue scoring normally.

---

## Step 2 — Verify mockup files

Before scoring Dimension 4, check each path listed in the screen inventory
against the repository. Use the file system to confirm existence. Do not
assume a file exists based on the PRD text alone.

For each screen in the inventory:
- Record the screen name
- Record the expected file path
- Record: EXISTS or MISSING

Record all results — this checklist appears in the report under
MOCKUP FILE CHECK.

---

## Step 3 — Score each dimension

Score each dimension independently. Record the score and the specific
finding(s) that caused any deduction. Findings must be actionable — they
must tell the author exactly what to add, fix, or remove, with the specific
location in the PRD or component spec (requirement number, screen name,
component name, or section heading).

Use `references/scoring-rubric.md` for sub-criteria, deduction amounts,
Profitability-specific examples, and edge cases.

---

### Dimension 1 — Requirement coverage (0–15)

**What it assesses:** Are all functional requirements present and stated as
explicit, testable predicates?

**Start at 15. Deduct for:**
- Vague language: "should feel", "may include", "handles gracefully",
  "user-friendly", "performant" — deduct 2 per instance
- Requirement depends on unstated assumptions (references behaviour not
  defined in this PRD or any linked document) — deduct 3 per instance
- Requirement references adjacent feature behaviour without explicit
  scope boundary — deduct 2 per instance
- Requirement entirely absent but implied by other requirements or
  mockups — deduct 4 per instance

**Floor: 0.**

---

### Dimension 2 — Acceptance criteria specificity (0–15)

**What it assesses:** Does each requirement have at least one AC that an
agent can evaluate without human interpretation?

**Start at 15. Deduct for:**
- Requirement with no AC at all — deduct 4 per instance
- AC with subjective language: "looks correct", "behaves as expected",
  "feels responsive" — deduct 2 per instance
- AC that cannot be expressed as a pass/fail test — deduct 3 per instance
- AC that restates the requirement rather than defining a testable
  outcome — deduct 2 per instance

**Positive signal (no points added, note in report):** ACs with explicit
values, thresholds, or state conditions are well-formed. Acknowledge these.

**Floor: 0.**

---

### Dimension 3 — Edge / empty / error state coverage (0–15)

**What it assesses:** Are non-happy-path states explicitly documented for
every functional area?

Note: component-level states are assessed in D5. D3 covers functional-area
states — what happens to the feature as a whole when things go wrong or
data is absent.

**For each functional area in the PRD, check for:**
- Empty state: what renders when there is no data
- Error state: what happens on failure (API error, validation failure,
  timeout, permission denied)
- Boundary conditions: min/max values, character limits, zero-value handling
- Permission/access edge cases: what a user without the required role sees

**Start at 15. Deduct for:**
- Functional area with no error state defined — deduct 3 per area
- Functional area with no empty state defined (where data display is
  involved) — deduct 2 per area
- Missing boundary condition where numeric or character input is
  accepted — deduct 2 per instance
- Missing permission/access edge case where role-based behaviour is
  relevant — deduct 2 per instance

**Floor: 0.**

---

### Dimension 4 — Mockup file completeness (0–15)

**What it assesses:** Are all screens in the screen inventory committed to
the repository at the stated paths?

This dimension checks file existence only. Annotation quality, visual
fidelity, and accuracy of representation belong to D5 and the kick-off
BA interview — not here.

**Start at 15. Deduct for:**
- File not found at the path listed in the screen inventory — deduct 3
  per missing file

**Floor: 0.** If screen inventory is absent: 0/15.

---

### Dimension 5 — UI component specification (0–25)

**What it assesses:** For every new or affected UI component on every
affected page, is there a complete written specification that an agent
can implement from without referencing the mockup?

**Critical principle:** The component spec is the authoritative definition
of what a component does. The mockup shows what it looks like. An agent
with only the mockup will make assumptions about behaviour, states, and
interactions. An agent with the component spec should not need to make
any assumptions.

**Prerequisite check:**
If the component specification child page is absent or not linked from
the PRD: D5 = 0/25. Record finding and stop scoring this dimension.
Do not infer specs from the mockup or requirements.

**If the spec page exists, score as follows:**

For each new or affected UI component, the spec must document all six
required elements. Score per component, then aggregate.

**The six required elements per component:**

1. **Component name and type**
   Name matches PRD requirement language exactly. Type is explicit:
   dropdown, multi-select, table, form field, button, modal, tooltip,
   toggle, date picker, tab set, etc.

2. **Functional description**
   What the component does, as a predicate. Not a visual description.
   "Displays a list" fails. "Filters the allocation results table by
   the selected department, re-querying immediately on selection" passes.

3. **All states with transition triggers**
   Every state the component can be in, with the condition that causes
   the transition into that state.

   Minimum expected states by type — see `references/scoring-rubric.md`
   for the full table. A component spec listing fewer states than the
   minimum for its type is incomplete unless the PRD explicitly excludes
   certain states with a rationale.

4. **User interaction options**
   Every action a user can take on this component. Each interaction
   states: the action (click, type, select, hover, drag), the trigger
   element, and the outcome.

5. **Selectable options (if applicable)**
   Full list of options, their underlying values, any conditional
   display logic (which options appear under which conditions), and
   the default selection if any. If not applicable, state explicitly.

6. **Data binding**
   What the component reads from and writes to. For Profitability
   features: name the Adjusted_GL field, ProcessID, stored procedure,
   or Pyramid data model attribute explicitly. "Reads from the API"
   is not sufficient. If a component's data comes from another
   component's state (derived/dependent), name that dependency.

**Scoring per component:**
- All six elements present and specific: full share
- One element missing or insufficiently specific: deduct 40% of share
- Two or more elements missing: deduct 70% of share
- Component present in mockup or requirements but absent from spec
  entirely: deduct 100% of share

Each component's share = 25 / total component count (rounded to 0.5).

**Reused components:**
If a component is identical to one used elsewhere in the product, the
spec may reference the existing definition by name and page. However,
any differences from the existing component must be explicitly documented.
"Same as X" with no delta noted scores as missing functional description
and states (elements 2 and 3).

**Floor: 0.**

---

### Dimension 6 — Out-of-scope clarity (0–15)

**What it assesses:** Is there an explicit out-of-scope section that
prevents an agent from implementing adjacent behaviour?

**Start at 15. Deduct for:**
- No out-of-scope section present — deduct 8 immediately
- Out-of-scope section exists but only lists non-technical or obvious
  items — deduct 3
- Any requirement implies adjacent behaviour without an explicit
  boundary — deduct 3 per instance
- Feature shares a data model or UI component with an adjacent feature
  but the out-of-scope section does not name the data boundary — deduct 4

For Profitability features: if this feature writes to or reads from
Adjusted_GL, GLAllocationLog, or any stored procedure also used by
another feature, the out-of-scope section must name exactly what this
feature touches and does not touch in those shared structures.

**Floor: 0.**

---

## Step 4 — Size signal (not scored)

Advisory only. Helps the Product Manager and Lead Dev set expectations for kick-off session
length and phase-splitter complexity.

- Requirement count: [N]
- Screen count: [N]
- Component count: [N]
- Signal: `normal` | `large` | `very large`
  - normal: ≤ 40 requirements, ≤ 8 screens, ≤ 12 components
  - large: 41–60 requirements or 9–12 screens or 13–20 components
  - very large: > 60 requirements or > 12 screens or > 20 components

For `large` or `very large` append to report:
> "Phase breakdown at kick-off will require additional time. Consider
> whether this PRD should be split into two separate PRDs before
> proceeding."

---

## Step 5 — Calculate total and determine outcome

```
Total = D1 + D2 + D3 + D4 + D5 + D6
Pass threshold = 80 / 100
```

**If Total ≥ 80:**
- Update the Linear feature issue status to `Ready`
- Write report to `[PRD_ROOT]/prd-completeness-report.md`
- Post a comment on the Linear issue confirming Ready status and the
  report path

**If Total < 80:**
- Do NOT update Linear status
- Write report to `[PRD_ROOT]/prd-completeness-report.md`
- Every finding in the report must be actionable

---

## Step 6 — Write the completeness report

Use exactly this format. Do not summarise or abbreviate findings.

```
PRD Completeness Report
=======================
PRD:        [PRD name or Notion page title]
Assessed:   [ISO datetime]
Assessor:   prd-completeness-check skill

SCORE: [total]/100 — [PASS / FAIL] (threshold: 80)

Dimension 1  Requirement coverage            [score]/15
Dimension 2  AC specificity                  [score]/15
Dimension 3  Edge/error state coverage       [score]/15
Dimension 4  Mockup file completeness        [score]/15
Dimension 5  UI component specification      [score]/25
             └─ Components assessed:         [N]
             └─ Components fully specified:  [N]
             └─ Components with gaps:        [N]
             └─ Components absent from spec: [N]
Dimension 6  Out-of-scope clarity            [score]/15

Size signal  [N] requirements · [N] screens · [N] components
             [normal / large / very large]

─────────────────────────────────────────────────────
FINDINGS
─────────────────────────────────────────────────────

D[N] — [Finding title]
  Location:  [Requirement / screen / component name / section]
  Issue:     [What is wrong]
  Fix:       [Exactly what the author must do to resolve this]
  Deduction: [N] points

[If no deductions in a dimension:]
D[N] — No findings.

─────────────────────────────────────────────────────
MOCKUP FILE CHECK
─────────────────────────────────────────────────────

[Screen name]     [expected path]     [EXISTS / MISSING]
...

─────────────────────────────────────────────────────
COMPONENT SPECIFICATION COVERAGE
─────────────────────────────────────────────────────

[Component name]  [Page]  [Type]  [Elements present]  [Missing elements]
...

─────────────────────────────────────────────────────
[If PASS:]
Linear issue status updated to Ready.
This PRD is eligible for the next planning cycle.

[If FAIL:]
Linear issue status NOT updated.
Resolve all findings above and re-run prd-completeness-check.
[N] finding(s) require attention before this PRD can reach Ready.

[If re-assessment, append:]
Prior score: [N]/100 ([date of prior assessment])
Delta: [+N / −N] points
Resolved since last assessment: [list]
Still open: [list]
─────────────────────────────────────────────────────
```

---

## Reference files

Read `references/scoring-rubric.md` when you need:
- Detailed sub-criteria and worked examples for each dimension
- Minimum state requirements by component type (D5)
- Profitability-specific data binding examples (Adjusted_GL, ProcessID,
  stored procedures, Pyramid data model)
- How to handle reused components, non-UI features, absent screen
  inventories, and re-assessments
