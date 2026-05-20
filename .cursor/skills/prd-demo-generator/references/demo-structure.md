# Demo HTML Structure

Reference for prd-demo-generator. Defines the required structure for all
generated demo HTML files.

---

## Interactive Demo (demo-interactive.html)

### Required Components

| Component | Required | Description |
|-----------|----------|-------------|
| **Scenario Selector** | Yes | Left sidebar with collapsible groups organised by AC category. Each scenario shows AC-ID and name. |
| **AC Text Sidebar** | Yes | Right panel showing Given/When/Then/Expected Result for the active scenario. |
| **Scenario Search** | Yes | Filter box at top of selector to search by AC-ID, name, or keyword. |
| **Interactive Buttons** | If applicable | Clickable buttons that trigger state transitions matching PRD requirements. |
| **Confirmation Dialogs** | If applicable | HTML modal overlays with exact title, body text, and button labels. |
| **Toast Notifications** | If applicable | Toast messages matching exact text and styling (success=green, error=red, warning=orange). |
| **Animation Engine** | If applicable | For multi-step workflows: frame-by-frame playback with Play/Pause/Resume/Reset controls. |
| **Action Log Panel** | If applicable | Toggleable panel showing log entries matching audit/action requirements. |

### Scenario Selector Structure

Organise scenarios into collapsible groups by AC category:

```
▼ Requirements (AC-REQ)
    AC-REQ-001: [Name from PRD]
    AC-REQ-002: [Name from PRD]
    AC-REQ-003: [Name from PRD]
▼ Edge Cases (AC-EC)
    AC-EC-001: [Name from PRD]
    AC-EC-002: [Name from PRD]
▼ UI States (AC-UI)
    AC-UI-001: [Name from PRD]
▼ Error/Recovery (AC-ERR)
    AC-ERR-001: [Name from PRD]
```

Each scenario entry must:
- Show the full AC-ID as a prefix
- Show the AC name from the PRD
- Highlight when selected
- Show a brief category badge (REQ/EC/UI/ERR)

### AC Text Sidebar

When a scenario is selected, the right panel shows:

```
┌─────────────────────────────┐
│ AC-REQ-001                  │
│ [Full AC name]              │
│                             │
│ Given:                      │
│   [precondition text]       │
│                             │
│ When:                       │
│   [action text]             │
│                             │
│ Then:                       │
│   [outcome text]            │
│                             │
│ Category: Requirements      │
│ Edge case: [ref if AC-EC]   │
│ Component: [name if AC-UI]  │
└─────────────────────────────┘
```

Pull Given/When/Then text directly from the PRD Section 8 -- do not
paraphrase or summarise.

### Scenario Search

- Filter box at the top of the scenario selector
- Searches across: AC-ID, scenario name, Given/When/Then text
- Updates the visible scenario list in real time
- Clear button to reset the filter

### Interactive Elements

For scenarios that involve user interactions:

**Buttons:** Render clickable buttons that trigger state transitions.
Match the button styling to the real app (Tier 1) or design system (Tier 2).
On click, transition to the expected state described in the AC's "Then" clause.

**Confirmation dialogs:** Modal overlay with:
- Title (exact text from PRD or codebase)
- Body text (exact text from PRD or codebase)
- Action buttons (exact labels from PRD or codebase)
- Cancel/close button

**Toast notifications:** Appear after actions complete:
- Success: green background
- Error: red background
- Warning: orange background
- Text must be exact (codebase-sourced or marked [TEXT TBD])
- Auto-dismiss after 3 seconds with fade animation

### Animation Engine

For multi-step workflows (e.g., calculation process with multiple phases):

- Frame-by-frame playback
- Controls: Play / Pause / Resume / Reset
- Frame counter showing current/total
- Each frame represents one step in the workflow
- Transitions between frames use smooth CSS animations

### Scenario Switching

When the user selects a different scenario:
- Clear all previous state (toasts, dialogs, animations, log entries)
- Reset interactive elements to their initial state
- Load the new scenario's content
- No residual state from previous scenarios

---

## Calculation Demo (calculation-demo.html)

### Required Components

| Component | Required | Description |
|-----------|----------|-------------|
| **Scenario Selector** | Yes | Same as interactive demo -- list of calculation scenarios by AC-ID |
| **Input Panel** | Yes | Shows input parameters for the selected scenario |
| **Step-by-Step Panel** | Yes | Shows calculation progression with intermediate results |
| **Result Panel** | Yes | Shows final output with expected values |
| **AC Text Sidebar** | Yes | Same as interactive demo |

### Calculation Step Display

For each calculation scenario:

```
┌─ Input Data ─────────────────┐
│ Parameter A: [value]          │
│ Parameter B: [value]          │
│ Parameter C: [value]          │
└───────────────────────────────┘

┌─ Calculation Steps ──────────┐
│ Step 1: [action] → [result]  │
│ Step 2: [action] → [result]  │
│ Step 3: [action] → [result]  │
└───────────────────────────────┘

┌─ Expected Result ────────────┐
│ Output: [final value]         │
│ Status: [pass condition]      │
└───────────────────────────────┘
```

Include colour coding:
- Input values: neutral
- Intermediate results: highlighted
- Final result: emphasised (bold, larger)
- Rules/conditions that apply: annotated inline

---

## Technical Requirements

- Single self-contained HTML file with embedded `<style>` and `<script>`
- Only external dependencies: FontAwesome + Google Fonts via CDN
- Must work offline after initial CDN load (CDN resources cached)
- No build tools, no server, no frameworks -- pure vanilla JS
- Clean, well-structured, readable code
- Responsive layout (works on screens 1024px and wider)
- No accessibility violations (proper ARIA labels, keyboard navigation)

### HTML Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Feature Name] - Interactive Demo</title>
    <!-- prdHash: [SHA-256] -->
    <!-- Generated from: .sage/prds/[FEATURE_ID]/prd.md -->
    <!-- Generated at: [ISO UTC timestamp] -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <style>
        /* All styles embedded here */
    </style>
</head>
<body>
    <div class="demo-container">
        <aside class="scenario-selector">
            <!-- Search box -->
            <!-- Collapsible category groups -->
        </aside>
        <main class="demo-content">
            <!-- Active scenario content -->
        </main>
        <aside class="ac-sidebar">
            <!-- Given/When/Then for active scenario -->
        </aside>
    </div>
    <script>
        // All logic embedded here
    </script>
</body>
</html>
```

---

## Coverage Rules

- Every demoable AC from the PRD must have a scenario in the demo
- ACs that cannot be demoed are documented in demo-coverage.md
- Scenario names must match AC-IDs exactly (no renaming or paraphrasing)
- Scenarios within each category group are ordered by AC number
- The demo must not contain scenarios that are not in the PRD
