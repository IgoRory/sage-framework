# Demo Guidelines — Generation

Reference for prd-interviewer. Self-contained — no external skill references.

**Companion file:** `demo-guidelines.intake.md` covers the upstream P0/P1
mockup/recording intake protocol that feeds this file. This file governs
the demo handoff chat's **design contract** (palette, typography, layout
patterns, AC sidebar, toast system, calculation demo). The handoff chat
reads this file via the cited references in its brief.

---

## Phase C reconciliation (binding — supersedes pre-lift conventions)

Phase A preserved this file's pre-lift content verbatim with a note flagging
Phase C as the reconciliation point. Phase C reconciliation locks the
following deltas. Where the body of this file (below this banner) names
older conventions, **the rules in this banner win**.

### R1 — Artifact path reconciliation

The pre-lift body refers to demo artifacts by paths under
`.sage/prds/[FEATURE_ID]/demos/`. The post-lift T5 paths are under
`.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/`. Every artifact reference in
this file is read against the **post-lift T5 paths**:

| Pre-lift reference | Post-lift T5 path |
|---|---|
| `.sage/prds/[FEATURE_ID]/demos/demo-interactive.html` | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-interactive.html` |
| `.sage/prds/[FEATURE_ID]/demos/calculation-demo.html` | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/calculation-demo.html` |
| `.sage/prds/[FEATURE_ID]/demos/demo-behavior-manifest.md` | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-behavior-manifest.md` |
| `.sage/prds/[FEATURE_ID]/demos/demo-coverage.md` | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/demo-coverage.md` |
| (none — pre-lift had no summary contract) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_summary.md` (T5-mandated) |
| (none) | `.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/_brief.md` (T5-mandated) |

### R2 — Inline self-review reconciliation

The pre-lift body contains an "inline self-review protocol" that the
**prd-demo-generator skill** ran after writing each demo file. Post-lift,
the demo handoff chat **owns the self-review** and runs it **inside its
own chat before writing `demos/_summary.md`** — never in the interviewer
chat, never as a Read-after-Write of a just-written file.

The Tier 1 fidelity self-review checklist that the demo handoff chat walks
is defined in:
- `sub-agent-delegation.md` §4.3 (handoff-chat self-review obligations) and §K
  (Tier 1 inside-chat protocol).
- `handoff-prompt-templates.md` Template 1 — Demo handoff prompt embeds the
  Tier 1 self-review items in the prompt body.

Where the body of this file references "self-review after write" or similar
patterns, treat those references as **inputs to the handoff chat's Tier 1
checklist**, not as instructions for the interviewer chat to re-read its
own outputs. The interviewer chat reads only `demos/_summary.md` on return
(per `prd-interviewer/SKILL.md` Step 4h).

### R3 — Delivery order reconciliation

The pre-lift body assumes a sequential delivery order (PRD → component-spec
→ demo-interactive → demo-behavior-manifest → calculation-demo →
demo-coverage), all written by the same agent. Post-lift, the three-surface
T5 manual handoff means:

- The interviewer chat writes `prd.md`, `acceptance-criteria.md`,
  `reuse-map-draft.md`, `interview-answers.json`, the three briefs, and the
  Component Pattern Confirmation Report.
- The demo handoff chat writes `demo-interactive.html`,
  `calculation-demo.html` (if applicable), `demo-behavior-manifest.md`,
  `demo-coverage.md`, and `demos/_summary.md` — in **one** handoff chat,
  in any internal order, with the Tier 1 self-review at the end before the
  summary is written.
- The sample-data and component-spec handoff chats run in **parallel** with
  the demo handoff chat. Sample-data is no longer downstream of the demo;
  component-spec is no longer downstream of the demo. All three are siblings
  of the interviewer's brief authoring step.

The pre-lift sequential delivery order is **superseded**. Where the body
of this file references "after the PRD is written" or similar sequential
language, read it as "after the demo brief is received" within the demo
handoff chat.

### R4 — `prd-demo-generator` ownership reconciliation

The pre-lift body is written assuming the `prd-demo-generator` skill is the
caller. Post-lift, the demo handoff chat is the caller; the
`prd-demo-generator` skill is **deprecated and permanently inert** (marked
deprecated in Phase C; preservation made permanent at Phase E close per
PM ruling — see `docs/cursor/feature-sage-prd-interviewer-enhancements/phase-e-completion-report.md`
§10 for the override of Phase A locked decision A5). The skill file remains
on disk as a historical artefact; no current pipeline invokes it. Where the
body references the skill by name, read it as "the demo handoff chat".

### R5 — Drift hash (`prdHash`) reconciliation

The pre-lift body specifies that the demo embeds a `prdHash` SHA-256 of
the PRD as an HTML comment. Post-lift, the **demo handoff chat** computes
the hash from the brief's cited PRD content and embeds it in the
`demos/_summary.md` header (per
`handoff-prompt-templates.md` Template 1) **and** as an HTML comment in
`demo-interactive.html`. The hash is computed **once**, in the handoff
chat's working context, from the cited PRD content — not by re-reading
the just-written demo HTML.

---

When demo generation is delegated to a manual handoff chat (per
`sub-agent-delegation.md`), the cited brief inherits the content of this
file as the demo's design contract. The handoff prompt template in
`handoff-prompt-templates.md` (Template 1 — Demo handoff prompt) references
this file as the canonical demo styling reference.

The body of this file (below) preserves the design-language content
verbatim from the pre-lift `demo-guidelines.md`. The Phase C reconciliation
rules in the banner above govern any conflict between the body and the
post-lift T5 contract.

Governs the creation of interactive HTML demos from PRD acceptance criteria.
Applies to both UI demos and calculation demos.

---

## When to produce demos

Produce demos based on the `requires_ui_demo` and `requires_calc_demo` flags
in the sub-PRD entry of `prd-breakdown.md`:

| Flag | Demo to produce | File |
|---|---|---|
| `requires_ui_demo: true` | Interactive UI demo | `demos/demo-interactive.html` |
| `requires_ui_demo: true` | Demo behavior manifest | `demos/demo-behavior-manifest.md` |
| `requires_calc_demo: true` | Calculation logic demo | `demos/calculation-demo.html` |

Demos are optional — the prd-completeness-check can pass without them. But
when produced, they must meet the standards in this file. Partial or broken
demos are worse than no demos.

---

## Core principle: fully functional first

The demo is a **complete, independently navigable application** — not just an
AC runner. A user can open it and interact with it naturally: clicking buttons,
filling forms, navigating between states, triggering toasts and dialogs,
without needing to use the AC panel at all.

The AC panel is a layer **on top of** a working demo, not the demo itself.

**Dual usage:** The demo serves two audiences simultaneously:
- A PM or stakeholder can explore the feature naturally, freeform
- A QA engineer can click AC-007 in the AC panel to jump directly to the
  starting state for that scenario and verify it

---

## UI demo — demo-interactive.html

### External dependencies — required

Every demo loads the following CDN resources in the `<head>`. These are
**required**, not optional — the design system depends on these fonts and
icons:

```html
<!-- Font Awesome icons (required for all demos) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<!-- Fonts: Light Application demos -->
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">

<!-- Fonts: Dark Glass demos -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
```

All other assets (CSS, JavaScript, inline SVG, inline data) must be
**self-contained within the file**. No application logic, no relative
imports, no network calls beyond the CDN fonts and icons above.

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  HEADER (full width) — title, sub-title badge, right controls│
├────────────────┬─────────────────────────────────────────────┤
│  AC Scenario   │  Main application area                      │
│  Panel         │  (fully functional interactive UI)          │
│  (~280–380px)  │                                             │
│                │                                             │
│  Sidebar is    │  Center/right fills remaining viewport      │
│  LEFT column   │                                             │
└────────────────┴─────────────────────────────────────────────┘
```

---

## Design language selection

There are **two prescribed design languages** for demos. Choose based on the
feature type.

---

### Design Language A — Light Application

**Use for:** Administration pages, grid-based configuration screens, rule
management pages, forms, and any feature that represents the production
application's daytime working UI.

**Examples:** Rule Assignment page, Cost Pools allocation screen, any
Kendo-style data grid feature.

#### Core CSS tokens

```css
:root {
  --font: 'Source Sans Pro', Helvetica, sans-serif;
  --navy:    #2b495e;
  --primary: #51738b;
  --primary-l: #8CA7BA;
  --grid-hd: #56738a;
  --green:   #72bf44;
  --green-h: #5fa636;
  --red:     #d75363;
  --red-l:   #fce8eb;
  --orange:  #f07d23;
  --yellow:  #ffcd40;
  --blue-s:  #00B0F0;
  --blue:    #5e91dd;
  --modified:    #d9e1f2;
  --modified-alt:#cdd7eb;
  --invalid-bg:  rgba(255,38,0,0.13);
  --warn-bg:     rgba(255,205,64,0.13);
  --row-hover:   rgba(43,73,94,0.08);
  --row-selected:rgba(43,73,94,0.18);
  --alt-row:     #f8f9fb;
  --grid-bdr:    rgb(236,238,243);
  --txt:  #505050;
  --txt-d:#2b495e;
  --bdr:  #eceef3;
  --bg:   #f2f5f8;
  --shd:  rgba(0,0,0,0.12);
  --r:    4px;
  --fs:   14px;
  --btn-shd:    2px 2px 3px 0 rgba(43,73,94,0.4);
  --btn-shd-dis:2px 2px 3px 0 rgba(43,73,94,0.2);
}
html { font-size: var(--fs); line-height: 1.5; }
body {
  font-family: var(--font);
  color: var(--txt);
  background: #eef1f6;
  display: flex;
  height: 100vh;
  overflow: hidden;
}
```

#### Header

```css
.hd-banner {
  background: linear-gradient(135deg, var(--navy), var(--primary));
  color: #fff;
  padding: 7px 16px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.4px;
  border-bottom: 3px solid var(--green);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

#### Buttons (`emp-btn` — matches production `emp-action-button`)

```css
.emp-btn {
  min-width: 7rem; height: 2rem;
  font: 600 12.5px/2rem var(--font);
  text-transform: uppercase;
  display: inline-flex; align-items: center; justify-content: center;
  gap: 0.3rem; border: none;
  border-right: 1px solid #fff; border-bottom: 1px solid #fff;
  border-radius: 0.25rem;
  box-shadow: var(--btn-shd);
  cursor: pointer; padding: 0 0.8rem; transition: all 0.12s;
}
.emp-btn.green { background: var(--green); color: #fff; }
.emp-btn.green:hover { background: var(--green-h); }
.emp-btn.blue  { background: var(--primary); color: #fff; }
.emp-btn.blue:hover  { background: #3C5567; }
.emp-btn:disabled {
  color: var(--grey); background: rgba(0,0,0,0.05);
  box-shadow: var(--btn-shd-dis); cursor: not-allowed;
}
```

#### Grid (`g` — matches production `emp-kendo-grid`)

```css
.gw { overflow-x: auto; border: 1px solid var(--grid-bdr); border-radius: 0.25rem; }
table.g { width: 100%; border-collapse: collapse; font-size: 12.5px; color: var(--txt-d); }
.g thead th {
  background: var(--grid-hd); color: #fff; font-weight: 600;
  padding: 8px 10px; text-align: left; white-space: nowrap;
  font-size: 12px; position: sticky; top: 0; z-index: 1;
  border-bottom: 2px solid #4a6578;
}
.g tbody td { padding: 7px 10px; border-bottom: 1px solid var(--grid-bdr); vertical-align: middle; }
.g tbody tr:hover { background: var(--row-hover); }
.g tbody tr:nth-child(even) { background: var(--alt-row); }
.g tbody tr.modified  { background: var(--modified); }
.g tbody tr.invalid   { background: var(--invalid-bg); }
.g tbody tr.warn      { background: var(--warn-bg); }
```

#### AC scenario sidebar (Light Application)

```css
.sb {
  width: 260px; min-width: 260px;
  background: var(--navy); color: #fff;
  display: flex; flex-direction: column; overflow: hidden;
}
.sb-top {
  padding: 10px 12px; display: flex; align-items: center;
  justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.12);
}
.sb-top h2 { font-size: 13px; font-weight: 700; letter-spacing: 0.3px; }
.sb-search { padding: 8px 12px; position: relative; }
.sb-search input {
  width: 100%; padding: 6px 8px 6px 28px;
  border: 1px solid rgba(255,255,255,0.2); border-radius: var(--r);
  background: rgba(255,255,255,0.07); color: #fff;
  font: 12px var(--font); outline: none;
}
.sb-search input::placeholder { color: rgba(255,255,255,0.4); }
/* Group headers */
.sg-label {
  padding: 5px 12px; font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.7px;
  color: rgba(255,255,255,0.38);
  cursor: pointer; display: flex; align-items: center; gap: 5px;
}
/* Scenario items */
.si {
  padding: 5px 12px 5px 20px; font-size: 11.5px;
  cursor: pointer; color: rgba(255,255,255,0.7);
  border-left: 3px solid transparent; transition: background 0.12s;
}
.si:hover { background: rgba(255,255,255,0.07); }
.si.on {
  background: rgba(255,255,255,0.12); color: #fff;
  font-weight: 600; border-left-color: var(--green);
}
.si b { color: var(--green); font-weight: 700; margin-right: 3px; font-size: 10.5px; }
```

---

### Design Language B — Dark Glass

**Use for:** Workflow orchestration screens, home page dashboard features,
navigation/access-control features, and any feature that benefits from a
dramatic, high-information-density presentation. Used when the demo presents
a process or state machine rather than a data management screen.

**Examples:** Home Page Workflow demos, Story 7 Navigation Access Logic,
any workflow status visualization.

#### Core CSS tokens

```css
:root {
  --bg-base:   #0b1015;
  --bg-mesh-1: #0d1520;
  --bg-mesh-2: #0f1a2a;
  --bg-mesh-3: #0a1018;
  --surface-0: rgba(14, 22, 33, 0.75);
  --surface-1: rgba(18, 28, 42, 0.82);
  --surface-2: rgba(24, 36, 52, 0.85);
  --surface-raised: rgba(28, 42, 60, 0.9);
  --glass-border:       rgba(255,255,255,0.07);
  --glass-border-hover: rgba(255,255,255,0.14);
  --glass-glow:         rgba(255,255,255,0.03);
  --text-primary:   #dce4ec;
  --text-secondary: #9aacbe;
  --text-muted:     #7d94ab;
  --text-bright:    #f0f4f8;
  --accent:     #d4a24e;
  --accent-dim: rgba(212,162,78,0.15);
  --accent-glow:rgba(212,162,78,0.25);
  --clr-valid:   #72bf44;
  --clr-error:   #d73a3a;
  --clr-invalid: #f07d23;
  --radius-sm:   6px;
  --radius-md:   10px;
  --radius-lg:   14px;
  --radius-pill: 100px;
  --header-h:    56px;
  --sidebar-w:   290px;   /* adjust per demo: 290–380px */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg-base);
  color: var(--text-primary);
  height: 100vh; overflow: hidden; font-size: 14px;
  -webkit-font-smoothing: antialiased;
}
```

#### Animated mesh background (mandatory for Dark Glass)

```css
.bg-mesh {
  position: fixed; inset: 0; z-index: 0;
  background: linear-gradient(
    135deg,
    var(--bg-mesh-1) 0%, var(--bg-mesh-2) 35%,
    var(--bg-base) 55%, var(--bg-mesh-3) 80%, var(--bg-mesh-1) 100%
  );
  background-size: 400% 400%;
  animation: meshDrift 25s ease infinite;
}
@keyframes meshDrift {
  0%   { background-position: 0% 50%; }
  25%  { background-position: 100% 25%; }
  50%  { background-position: 50% 100%; }
  75%  { background-position: 25% 0%; }
  100% { background-position: 0% 50%; }
}
/* Noise overlay */
.bg-mesh::before {
  content: ''; position: absolute; inset: 0; z-index: 1;
  opacity: 0.025; mix-blend-mode: overlay; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 128px 128px;
}
```

Add `<div class="bg-mesh"></div>` as the first child of `<body>`. All other
content must have `position: relative; z-index: 1` (or higher) to appear
above the background.

#### Header

```css
.demo-header {
  position: relative; z-index: 50;
  height: var(--header-h);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
  background: linear-gradient(135deg, rgba(10,16,24,0.92) 0%, rgba(16,26,40,0.92) 100%);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
/* Story accent line across bottom of header */
.demo-header::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(var(--story-rgb), 0.2) 30%,
                rgba(212,162,78,0.1) 70%, transparent 100%);
}
.demo-header h1 {
  font-family: 'Outfit', sans-serif;
  font-size: 17px; font-weight: 700;
  color: var(--text-bright); letter-spacing: -0.02em;
  display: flex; align-items: center; gap: 10px;
}
.header-badge {
  font-family: 'Outfit', sans-serif;
  font-size: 10px; font-weight: 700;
  letter-spacing: 1.5px; text-transform: uppercase;
  padding: 4px 14px; border-radius: var(--radius-pill);
  border: 1px solid; /* set border and color to story accent */
}
```

#### Glass card / surface

```css
.glass-panel {
  background: var(--surface-1);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 0 0 1px var(--glass-glow);
}
/* Subtle breathing animation for key panels */
@keyframes stageBreathing {
  0%, 100% { box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 1px var(--glass-border); }
  50%       { box-shadow: 0 8px 32px rgba(0,0,0,0.35), 0 0 20px rgba(var(--story-rgb),0.02), 0 0 0 1px rgba(255,255,255,0.09); }
}
```

#### Scrollbar (Dark Glass)

```css
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }
```

#### Story accent colours

Each sub-PRD has a story colour. Apply it to group headers, active states,
and the header accent line. Define it as a CSS variable:

```css
:root {
  /* Example — set to the sub-PRD's story colour */
  --story: #5cc6d0;          /* hex value */
  --story-rgb: 92, 198, 208; /* separate R G B for rgba() usage */
}
```

---

## AC scenario sidebar — detailed pattern (both design languages)

The AC scenario sidebar is the same structural pattern in both design
languages, styled to match the respective language's tokens.

### Structure

```html
<aside class="scenario-sidebar">
  <h3>Scenarios</h3>                          <!-- uppercase, accent-coloured -->

  <div class="scenario-search-wrap">
    <i class="fa-solid fa-magnifying-glass search-icon"></i>
    <input id="scenarioSearch" type="text" placeholder="Filter scenarios…">
    <button class="search-clear-btn" id="searchClear">×</button>
  </div>

  <!-- One group per AC category -->
  <div class="scenario-group">
    <div class="scenario-group-header" onclick="toggleGroup(this)">
      <span class="group-label">
        <i class="fa-solid fa-circle-check"></i>
        Happy Path
      </span>
      <span class="group-count">3</span>
      <i class="fa-solid fa-chevron-down chevron"></i>
    </div>
    <div class="scenario-group-items">
      <div class="scenario-item" onclick="loadScenario('AC-001')">
        <span class="ac-tag">AC-001</span> Rules load on page open
      </div>
      …
    </div>
  </div>
  …
</aside>
```

### Required behaviour

- **Search box** filters scenario items in real time by AC number or title
- **Clear button** appears when there is text in the search box; clears it
- **Collapsible groups** — clicking the group header collapses/expands items;
  chevron rotates to indicate state
- **Group count badge** shows the number of visible (not filtered-out) items
- **Active item** — `.scenario-item.active` has a left-border accent, accent
  background, and the `accentPulse` animation
- **Fade-in animation** — scenario items animate in with `fadeSlideIn` when
  a group is expanded
- **AC tag** — rendered in `JetBrains Mono`, story accent colour, small size
- **No results message** — shown when the search filter produces zero results

### Required CSS animations

```css
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateX(-6px); }
  to   { opacity: 1; transform: translateX(0); }
}
.scenario-group-items .scenario-item {
  animation: fadeSlideIn 0.25s var(--ease-out-expo) both;
}
.scenario-group-items .scenario-item:nth-child(1) { animation-delay: 0.02s; }
.scenario-group-items .scenario-item:nth-child(2) { animation-delay: 0.04s; }
.scenario-group-items .scenario-item:nth-child(3) { animation-delay: 0.06s; }
.scenario-group-items .scenario-item:nth-child(4) { animation-delay: 0.08s; }

@keyframes accentPulse {
  0%, 100% { border-left-color: var(--accent); box-shadow: inset 0 0 24px rgba(212,162,78,0.06); }
  50%       { border-left-color: #e8b960;       box-shadow: inset 0 0 32px rgba(212,162,78,0.10); }
}
.scenario-item.active { animation: accentPulse 3s ease-in-out infinite; }
```

### AC scenario panel groups

Organise scenarios into named groups that correspond to AC categories in the
PRD (e.g., "Happy Path", "Empty States", "Validation Errors", "Edge Cases",
"Error Recovery"). Do not use a flat list — always group.

Group headers in Dark Glass demos use a story-accented left border:

```css
.scenario-group-header {
  border-left: 3px solid var(--story);
}
```

---

## Toast notification system (both design languages)

Every demo must have a toast system. Toasts are the primary feedback
mechanism for save/error/warning operations.

### Toast variants

| Variant | Left border | Icon colour | Use for |
|---|---|---|---|
| `toast-success` | `--clr-valid` / `--green` | Same | Successful save, apply, confirm |
| `toast-error` | `--clr-error` / `--red` | Same | Operation failed, permission denied |
| `toast-warning` | `--clr-invalid` / `--orange` | Same | Partial success, data warning |
| `toast-info` | `#4ea8de` | Same | Informational confirmation |

### Toast pattern (Dark Glass)

```css
.toast-area {
  position: fixed; top: calc(var(--header-h) + 12px); right: 20px;
  z-index: 1000; display: flex; flex-direction: column; gap: 10px;
  pointer-events: none;
}
.toast {
  position: relative; overflow: hidden;
  background: var(--surface-2); color: var(--text-bright);
  padding: 12px 16px 12px 42px; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 500;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 0 1px var(--glass-border);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  pointer-events: auto; max-width: 380px;
  opacity: 0; transform: translateY(-8px) scale(0.96);
  transition: opacity 0.35s var(--ease-spring), transform 0.4s var(--ease-spring);
}
.toast.show  { opacity: 1; transform: translateY(0) scale(1); }
.toast.toast-exit { opacity: 0; transform: translateY(8px) scale(0.96); }
.toast .toast-icon {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  font-size: 14px; width: 18px; text-align: center;
}
/* Progress bar auto-dismiss countdown */
.toast .toast-progress {
  position: absolute; bottom: 0; left: 0; height: 2px;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  animation: toastCountdown 5s linear forwards;
}
@keyframes toastCountdown { from { width: 100%; } to { width: 0%; } }
/* Per-variant colour */
.toast.toast-success { border-left: 3px solid var(--clr-valid); }
.toast.toast-success .toast-icon, .toast.toast-success .toast-progress { color: var(--clr-valid); background: var(--clr-valid); }
.toast.toast-error   { border-left: 3px solid var(--clr-error); }
.toast.toast-error   .toast-icon, .toast.toast-error   .toast-progress { color: var(--clr-error);   background: var(--clr-error); }
.toast.toast-warning { border-left: 3px solid var(--clr-invalid); }
.toast.toast-warning .toast-icon, .toast.toast-warning .toast-progress { color: var(--clr-invalid); background: var(--clr-invalid); }
.toast.toast-info    { border-left: 3px solid #4ea8de; }
.toast.toast-info    .toast-icon, .toast.toast-info    .toast-progress { color: #4ea8de; background: #4ea8de; }
```

### Toast helper function

```javascript
function showToast(message, type = 'success', duration = 5000) {
  const icons = {
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    warning: 'fa-triangle-exclamation',
    info:    'fa-circle-info'
  };
  const area = document.querySelector('.toast-area');
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `
    <i class="toast-icon fa-solid ${icons[type]}"></i>
    ${message}
    <div class="toast-progress"></div>`;
  area.appendChild(t);
  requestAnimationFrame(() => { t.classList.add('show'); });
  setTimeout(() => {
    t.classList.add('toast-exit');
    t.addEventListener('transitionend', () => t.remove(), { once: true });
  }, duration);
}
```

---

## Keyboard hint display (Dark Glass header — optional but preferred)

When the demo supports keyboard shortcuts, display them in the header:

```html
<div class="kbd-hints">
  <span><kbd>←</kbd><kbd>→</kbd> navigate</span>
  <span><kbd>Space</kbd> confirm</span>
  <span><kbd>Esc</kbd> cancel</span>
</div>
```

```css
.kbd-hints { display: flex; gap: 12px; font-size: 10px; color: var(--text-muted); }
.kbd-hints kbd {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; font-weight: 500;
  background: rgba(255,255,255,0.06); color: var(--text-secondary);
  padding: 1px 5px; border-radius: 3px;
  border: 1px solid rgba(255,255,255,0.08);
  margin-right: 2px;
}
```

---

## AC scenario panel — behaviour

### AC scenario execution

When a scenario is selected from the panel:
1. Reset demo to a clean state
2. Pre-populate any required inputs or context for that scenario
3. Execute the scenario automatically or step the user through it
4. Show the expected outcome with a visual indicator (pass/fail annotation)

### ACs not in the panel

ACs that cannot be demoed are **not** listed in the panel — document them in
the PRD's Section 7 Mockup Reference with the reason they are not demoable.

---

## Tier guidance — which design language for which feature

| Feature type | Design Language |
|---|---|
| Data grid, form, configuration, administration | Light Application (A) |
| Workflow orchestration, dashboard, home page | Dark Glass (B) |
| Navigation / access control | Dark Glass (B) |
| Calculation proof (standalone) | Light Application (A) |
| Any Kendo-style grid feature | Light Application (A) |
| Multi-state process visualization | Dark Glass (B) |

When unsure: if the primary content is a grid or form, use Light Application.
If the primary content is a workflow, status board, or access-control matrix,
use Dark Glass.

---

## No-fabrication rule (absolute)

Every piece of user-facing text in the demo must come from one of:
1. The component YAML (exact quote — source documented)
2. The interview (PM-confirmed text)
3. The `[TEXT TBD — requires PM decision]` marker

**Never invent:**
- Tooltip text
- Button labels
- Toast messages
- Error messages
- Dialog titles or body text
- Empty-state messages
- Validation messages

A demo with fabricated text is worse than a demo with `[TEXT TBD]` markers.
Fabricated text creates false confidence — the PM reviews the demo and
approves copy they never actually confirmed.

---

## UI demo — inline self-review protocol

After generating `demo-interactive.html`, run this self-review before
proceeding to the next deliverable. **Do not skip or batch — run it immediately
after generation.**

### Freeform interaction path

1. Open the demo from a clean state (no scenario pre-selected)
2. Navigate through every screen and component in the freeform flow
3. Click every button and interactive element
4. Trigger every state transition (loading → loaded, data → empty, enabled →
   disabled, etc.)
5. Trigger every toast and dialog
6. Verify every disabled condition activates and shows the correct reason text

For each failure: fix immediately, do not proceed.

### AC scenario panel walk-through

For each AC listed in the scenario panel:
1. Click the AC entry to jump to its starting state
2. Execute the scenario
3. Verify the outcome matches the PRD exactly:
   - State transitions correct
   - Toast text matches PRD exactly
   - Dialog titles and bodies match PRD exactly
   - Disabled conditions and reason text match PRD
   - Empty states show the correct messages
   - Error paths show the correct error messages and recovery paths

For each failure: fix immediately, do not proceed.

### Checklist before marking complete

- [ ] Every demoable AC from the PRD has an entry in the panel
- [ ] AC scenario panel has a working search box that filters in real time
- [ ] AC scenario panel uses collapsible groups, not a flat list
- [ ] Every freeform interaction works correctly
- [ ] Toast system present and fires on all save/error/warning operations
- [ ] Every toast message is an exact PRD quote or [TEXT TBD]
- [ ] Every dialog title and body is an exact PRD quote or [TEXT TBD]
- [ ] Every disabled button shows the correct reason text on hover
- [ ] Every empty state shows the correct message
- [ ] Every error state shows the correct message and recovery path
- [ ] State transitions are visually correct
- [ ] Design language matches the feature type (Light Application vs Dark Glass)
- [ ] CDN font and icon links are present in `<head>`
- [ ] No placeholder styling — matched components use exact production tokens

---

## Demo behavior manifest — demo-behavior-manifest.md

The demo behavior manifest is a developer-facing behavioral contract. It
documents every interactive element in the demo and cross-references it to
the PRD.

**File path:** `demos/demo-behavior-manifest.md`

### Format

```
# [Story Title] — Demo Behavior Manifest

## Purpose

This manifest is a developer-facing behavioral contract for every interactive
element in the UI demo. Every element is cross-referenced to the PRD acceptance
criteria it validates.

---

## Interactive elements

### [Element name — e.g., "Save button on rules form"]

| Property | Value |
|---|---|
| Element type | [button / dropdown / grid / form / toast / dialog / …] |
| Location | [Page name → section → position] |
| AC references | [AC-001, AC-007] |
| States | [enabled / disabled / loading / hidden] |
| Enabled when | [condition from PRD] |
| Disabled when | [condition from PRD] |
| Click behavior | [what happens — exact description] |
| Success outcome | [toast text / navigation / state change — exact PRD quote] |
| Error outcome | [error message text — exact PRD quote] |
| Disabled tooltip | [exact text — PRD quote or TEXT TBD] |

---
```

### Cross-check (run after manifest is written)

- Every interactive element in the demo has an entry in the manifest
- Every entry in the manifest corresponds to an element that exists in the demo
- No orphaned elements in either direction
- Every AC that has a demoable scenario is referenced by at least one manifest
  entry
- Every message text in the manifest is an exact PRD quote or `[TEXT TBD]`

---

## Calculation demo — calculation-demo.html

The calculation demo is a self-contained interactive proof page for sub-PRDs
that involve calculation or allocation logic. Use **Light Application** design
language unless the feature uses Dark Glass throughout.

### Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [AC Scenario Panel — left sidebar]                          │
│  AC-001  Happy path — standard FTP calculation               │
│  AC-005  Edge case — instrument excluded from calculation     │
│  AC-009  Edge case — zero balance instrument                 │
│  …                                                           │
├─────────────────────────────────────────────────────────────┤
│  [INPUTS zone]                                               │
│  User enters or adjusts input values                         │
│  Pre-populated by scenario panel selections                  │
├─────────────────────────────────────────────────────────────┤
│  [LOGIC zone]                                                │
│  Calculation steps in plain business language                │
│  Each step numbered and mapped to a PRD requirement          │
│  Updates in real time as inputs change                       │
├─────────────────────────────────────────────────────────────┤
│  [OUTPUTS zone]                                              │
│  Calculated results                                          │
│  Pass/fail indicator vs. AC expected result                  │
│  (visible when a scenario is selected from panel)            │
└─────────────────────────────────────────────────────────────┘
```

### Worked examples

- Every key calculation scenario from the PRD's ACs has a pre-loaded worked
  example in the AC scenario panel
- Each example pre-populates the inputs, runs the logic, and shows the expected
  output with a pass/fail indicator
- Edge case scenarios are included — zero values, null values, maximum
  thresholds, boundary conditions, excluded instrument types, and any scenario
  that produces a different result than the happy path

### Formula transparency

The Logic zone shows calculation steps in **plain business language** — not
code. Each step maps to a numbered requirement in the PRD so the reader can
trace from input to output to requirement.

Example:
```
Step 1: Determine applicable rate period
  "The FTP rate is sourced from the period matching the instrument's
   pricing date. Per AC-003: when a historical pricing date applies,
   the rate from that period is used, not today's rate."
  Result: Rate period = [calculated value]

Step 2: Apply FTP rate to outstanding balance
  "FTP Funding Cost = Outstanding Balance × FTP Rate"
  Result: [calculated value]
```

### Rounding and precision

Where the PRD specifies rounding rules or precision requirements, the demo
must reflect them exactly — not approximate.

### No fabricated numbers

All worked example values are drawn from the PRD's ACs or stated requirements.
If a representative example is needed that the PRD does not supply, mark it:
`[EXAMPLE — confirm with PM]`

### Inline self-review protocol

After generating `calculation-demo.html`, run this self-review before
proceeding to the next deliverable.

**For each AC in the scenario panel:**
1. Select the scenario
2. Verify inputs pre-populate correctly
3. Execute the calculation (click Calculate or observe real-time update)
4. Verify the output exactly matches the PRD's expected result for that AC
5. Verify the pass/fail indicator is correct

**General checks:**
- [ ] Every calculation AC from the PRD has an entry in the scenario panel
- [ ] AC panel uses collapsible groups with a search box
- [ ] Every worked example produces the correct output against the PRD
- [ ] All 7 edge case categories from the PRD have corresponding scenarios
  where applicable
- [ ] Logic zone steps map to numbered PRD requirements
- [ ] Rounding and precision rules are applied correctly
- [ ] No fabricated numbers — all values from PRD or marked [EXAMPLE]
- [ ] The freeform input mode (no scenario selected) works correctly and
  produces sensible outputs for arbitrary inputs

---

## File locations

```
.sage/prds/[FEATURE_ID]/[sub-prd-id]/demos/
  demo-interactive.html        (UI demo)
  demo-behavior-manifest.md    (behavioral contract)
  calculation-demo.html        (calculation proof)
```

---

## Delivery order

Demos are always produced after the PRD is written and self-reviewed:

1. Write PRD → self-review PRD
2. Write component spec → self-review component spec
3. Generate `demo-interactive.html` → run inline self-review immediately
4. Generate `demo-behavior-manifest.md` → run cross-check immediately
5. Generate `calculation-demo.html` → run inline self-review immediately

Never produce demos before the PRD is finalised — the AC panel contents are
derived from the PRD, so a changing PRD invalidates any demo produced from it.
