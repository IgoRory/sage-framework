# Component Matching — Protocol

Reference for prd-interviewer. Self-contained — no external skill references.

Governs how the prd-interviewer uses `.context/components` YAML data to
eliminate redundant interview questions and generate realistic demos.

---

## Purpose

The Profitability application has a mature component library documented in
`.context/components/`. When a feature introduces a new page or modifies an
existing one, many of the UI components involved already exist in the codebase
with fully defined states, copy, styling, and behaviors.

The prd-interviewer reads these YAMLs **before** asking any UI questions and
uses the data to:

1. **Eliminate redundant questions** — if the component pattern is already
   established, do not ask the PM to describe it from scratch. Present a
   Component Pattern Block instead and ask only about differences.
2. **Pre-populate demo fidelity** — demos use exact colors, states, copy, and
   behaviors from the YAML rather than generic AI aesthetics (Tier 1 styling).
3. **Formulate precise business questions** — knowing what a component does
   today allows the interviewer to ask targeted questions about deviations and
   new behaviors rather than open-ended "what does this do?" questions.

**The component context never enters the PRD.** It is for internal interview
intelligence and demo generation only. It does not direct developers on what
to reuse or change.

---

## Step 1 — Read the manifest

Read `.context/components/manifest.yaml`.

This file lists every component with:
- `id` — unique identifier
- `name` — Angular component class name
- `component_type` — the pattern type (e.g., `workflow-process-card`,
  `allocation-rules-list`, `settings-grid`)
- `file` — path to the component's YAML specification

Index the manifest by `id` and by `component_type` for lookup.

---

## Step 2 — Match components to sub-PRD scope

Use the `matched_components[]` list from the sub-PRD entry in `prd-breakdown.md`
as the primary match list. These are the component IDs the orchestrator
identified as relevant during recon.

Additionally, scan for potential matches the orchestrator may have missed:

1. **By page/screen name** — for each page listed in the breakdown's
   `affected_pages`, look for components whose name or selector includes the
   page's business area (e.g., a page about "Allocation Rules" → look for
   `allocation-rules`, `edit-allocation-rule`, etc.)

2. **By component type** — for each action type in the sub-PRD's scope
   (CRUD operations, grid display, form editing, workflow tiles), look for
   existing components of the corresponding `component_type`

3. **By feature area** — if the sub-PRD involves a known feature area
   (hierarchy management, allocation rules, workflow process cards, reporting),
   look for all components in that area

For each candidate: check `status: active` before reading the YAML. Skip
components with `status: dormant`.

---

## Step 3 — Consume Component Pattern Summaries from the per-sub-PRD breakdown

**Primary read path (Phase B onwards).** The prd-orchestrator writes one
**Component Pattern Summary** per matched component into the sub-PRD's
per-sub-PRD breakdown file at
`.sage/prds/[FEATURE_ID]/prd-breakdown.[sub-prd-id].md` under the `## Component
Pattern Summaries` heading. The interviewer **consumes those summaries
directly** — it does not re-read the component YAMLs in the general case.

Each summary the orchestrator emits carries:

```yaml
- component_id: [id]
  component_name: [Angular class name]
  selector: [Angular selector]
  component_type: [pattern type]
  yaml_file: [full path to the component's YAML, e.g. .context/components/view-only.yaml]
  state_set:
    - [state name]: [one-line description]
  copy_strings_verbatim:
    labels: [verbatim button / column / field labels]
    tooltips: [verbatim tooltip text]
    empty_state_messages: [verbatim empty-state copy]
    error_messages: [verbatim error copy]
    toast_messages: [verbatim toast copy]
  interactions:
    - [user action] → [outcome]
  behaviour_summary: >
    [2–4 sentence business-language description of what the component
    does and when.]
```

This is the Tier 1 source material — every copy string is verbatim from the
source YAML by orchestrator construction.

### When to read the YAML directly

Three cases only:

1. **`summary_status: see_full_yaml` pointer.** When a component's full
   summary exceeded the orchestrator's 80-line hard cap, the orchestrator
   emits a pointer block instead of the full summary. The interviewer reads
   `yaml_file` directly for that component during P2.
2. **Drift suspicion.** If the interviewer detects a contradiction between
   the summary and PM-confirmed behaviour (the PM describes a state or copy
   string that conflicts with the summary), the interviewer reads the source
   YAML to determine which is current. The orchestrator's drift rule
   (regenerate when YAML mtime > breakdown mtime) prevents most of this; the
   YAML read is a safety net.
3. **Missing per-sub-PRD breakdown file.** Per the fallback rule (see
   below), if no per-sub-PRD breakdown file exists for an in-flight PRD that
   predates Phase B, the interviewer falls back to reading the master
   breakdown plus the component YAMLs directly. This is the legacy read
   path; new PRDs always use the per-sub-PRD path.

### Read-path fallback rule (in-flight PRDs predating Phase B)

| Situation | Interviewer behaviour |
|---|---|
| Per-sub-PRD breakdown file exists | Read summaries from the per-sub-PRD file; do not re-read component YAMLs unless one of the three cases above applies |
| Per-sub-PRD file missing; master breakdown carries the sub-PRD entry inline | Fall back to reading the master `prd-breakdown.md` and the component YAMLs directly (legacy path) |
| Both missing | Stop and ask the PM to re-run prd-orchestrator |

All copy is recorded verbatim — never paraphrased. This becomes Tier 1 demo
source material.

---

## Step 4 — Identify new components

For items in `new_components[]` from the breakdown, or for feature areas where
no matching component exists:

1. Note the business area (e.g., "a new rules configuration form").
2. Find the closest `component_type` in the manifest that resembles the
   needed pattern (e.g., `allocation-rule-editor` for a form-based editor,
   `settings-grid` for a tabular settings interface).
3. Record the closest type for demo styling guidance (Tier 2 — production-grade
   distinctive design rather than generic placeholder).

Do not fabricate behaviors or copy for new components. Their states, copy, and
behaviors are determined through the interview.

---

## Step 5 — Generate Component Pattern Blocks

For each matched component, prepare a **Component Pattern Block** — a concise
business-language summary of the component's established pattern.

**Format:**

> "The [business name for this component] looks like it follows the same
> [pattern type] pattern as [reference to what it's similar to]. Based on the
> existing application, I'd expect it to:
> - Show a [loading / empty / data-loaded] state depending on data availability
> - Display [key behaviors derived from the YAML]
> - Support [known interactions]
>
> Are there any differences from what you'd expect, or anything that should
> work differently here?"

**Rules for Component Pattern Blocks:**
- Written in business language — no class names, selector names, YAML field
  names, or SCSS variables
- State only what is actually known from the YAML — do not extrapolate
- Focused: 3–5 bullet points maximum per block
- Present as "I'll assume this applies — correct me if not" rather than as a
  question about what the PM wants
- Each block generates **one confirmation question** (do you agree?) and then
  **delta questions only** (what should be different?)

---

## Step 6 — Delta questions only

After presenting a Component Pattern Block, the interviewer asks only questions
about deviations or additions — not about behaviors already established in
the YAML.

**Interview discipline:**

| Situation | What to do |
|---|---|
| Behavior is in the YAML and PM has not indicated any change | State it as assumed behavior, do not ask |
| PM confirms "same as existing" | Move on, no further questions about this behavior |
| PM says "slightly different" or hesitates | Ask targeted delta question: "How should it differ?" |
| Behavior is NOT in the YAML for this component | Ask the full question as normal |
| New component with no match | Ask the full question set for that component |

**Specific behaviors NOT to ask about if they are in the YAML:**
- Component states (loading, empty, error, data-loaded) — state them as
  assumed and ask for corrections
- Tooltip text that is quoted verbatim in the YAML — treat as confirmed unless
  PM changes it
- Empty-state messages that are quoted in the YAML — treat as confirmed
- Button labels that are quoted in the YAML — treat as confirmed
- Sort and filter defaults documented in the YAML — treat as confirmed

**What to always ask regardless of YAML:**
- Whether a new interaction or state is needed that the existing component
  does not have
- Whether the PM wants any established behavior to work differently in this
  context
- Cross-page impacts specific to this feature that cannot be derived from the
  component YAML alone
- The rationale for any deviation from the established pattern

---

## Step 7 — Demo source data

After the interview, use the registered component data to generate demos:

**Tier 1 — existing component pattern:**
- Use exact CSS classes and SCSS color tokens from the YAML
- Use exact copy (labels, tooltips, empty states, errors) from the YAML
- Render all states documented in the YAML
- Any text the YAML does not provide must be sourced from the interview or
  marked `[TEXT TBD — requires PM decision]`

**Tier 2 — new component (no match):**
- Use the closest `component_type` as a styling reference for design language
- Produce production-grade, distinctive design — not a generic placeholder
- All copy comes from the interview or is marked `[TEXT TBD]`

**No-fabrication rule:** Every piece of user-facing text in the demo must
come from one of:
1. The component YAML (exact quote)
2. The interview (PM-confirmed text)
3. The `[TEXT TBD — requires PM decision]` marker

Never invent tooltip text, button labels, toast messages, or error messages.

---

## YAML field reference

Component YAMLs in `.context/components/` follow the schema in
`.context/components/component-schema.yaml`. Key fields used by this protocol:

| Field | Used for |
|---|---|
| `id` | Matching against breakdown manifest |
| `name` | Component Pattern Block identification |
| `component_type` | Tier 1/Tier 2 classification; new component styling |
| `status` | Only read `active` components; skip `dormant` |
| `states` | State enumeration for Component Pattern Block |
| `copy` / `labels` / `tooltips` | Demo text sourcing |
| `interactions` | Interaction enumeration for Component Pattern Block |
| `css_classes` / `color_tokens` | Tier 1 demo styling |
