---
name: prd-orchestrator
description: >
  Receives a large feature (ADO work item or Linear issue), performs exhaustive
  silent codebase reconnaissance, classifies each sub-area by complexity tier,
  recommends a PRD breakdown that keeps every sub-PRD at Tier 1–2, writes one
  per-sub-PRD breakdown file plus a master index, embeds Component Pattern
  Summaries per matched component, and hands off to prd-interviewer instances.
  Always runs before the first prd-interviewer for a feature. Use when the PM
  says "start a PRD", "run the orchestrator", "split this feature", or provides
  an ADO/Linear reference and asks to begin feature documentation.
---

# PRD Orchestrator

Analyses a feature scope and produces a machine-readable breakdown that drives
one or more focused prd-interviewer sessions. Each sub-PRD interview runs in
its own Cursor chat — smaller context, sharper focus.

---

## Invocation phrases

Treat this skill as invoked when the PM says any of:
- "Start a PRD", "run the orchestrator", "prd-orchestrator"
- "Split this feature", "break this feature into sub-PRDs"
- They provide an ADO work item or Linear issue and ask to begin feature documentation

When invoked, **always execute Step 0 (repo preflight) before Step 1**, then
continue in order.

---

## Step 0 — Repo preflight (mandatory)

**Scope:** The git repository root of the Cursor workspace.

**Configuration:** Read `.sage/workflow-config.json`. Use:
- `prd.requiredInterviewBranch` — branch that must be checked out
- `prd.remoteName` — remote for fetch/compare (default: `origin`)
- `prd.telemetryFile` — JSONL path (default `.sage/prd-interview-telemetry.jsonl`)

**Steps:**
1. Confirm `linearIssueId` or ADO work item ID with PM if not already known.
2. Generate `prdRunId` (UUID v4) for this orchestrator run; store for all telemetry.
3. `git fetch <remoteName>`.
4. Verify current branch equals `prd.requiredInterviewBranch`.
5. Verify `commitsBehind = 0` for `HEAD..<remote>/<requiredInterviewBranch>`.
6. Note dirty working tree as warn-only (does not fail preflight by default).

**Gate:** If branch is wrong or `commitsBehind > 0`, stop and write
`prd_preflight` telemetry with `preflightOutcome: fail`. Explain to PM what
must be resolved. Do not proceed until resolved.

**Exception:** PM may explicitly override for a hotfix branch. Record
`preflightOutcome: pass`, `override: true`, `overrideReason: "<verbatim>"`.

**On success:** Append `prd_preflight` telemetry with `preflightOutcome: pass`
and git summary fields.

---

## Step 1 — Context gathering (interactive)

### Step 1a — Re-use detection

Check whether `.sage/prds/[FEATURE_ID]/prd-breakdown.md` already exists.
Also list any `.sage/prds/[FEATURE_ID]/prd-breakdown.*.md` per-sub-PRD files.
If found: "I found an existing breakdown for this feature. Would you like to
(a) start fresh, or (b) review and update the existing breakdown?"

If the PM chooses (b) and per-sub-PRD breakdown files already exist for
specific sub-PRDs, only the sub-PRDs whose scope is changing need new
per-sub-PRD files written. Unchanged sub-PRDs retain their existing
per-sub-PRD breakdown file.

### Step 1b — Context checklist

Before any silent investigation, confirm the PM has provided everything:

- Has the ADO work item or Linear issue ID been provided?
- Are there any additional context documents (specs, meeting notes, prior PRDs)?
- Are there any HTML mockups or wireframes?
- Are there any related user stories or parent features to reference?
- Is there tribal knowledge or verbal decisions that should be captured now?
- Are there any existing demos or recordings of current application behavior?

**Do not proceed to Step 2 until the PM confirms "I've provided everything"
or equivalent.** If the PM says they have something but has not provided it
yet, wait.

---

## Step 2 — Silent codebase reconnaissance

Perform exhaustive codebase investigation **before** presenting anything to the
PM. Do not narrate this process. This step typically takes 2–4 minutes.

**In-memory discipline.** The findings produced by Step 2 are held as the
`investigation_context` object **in memory** for the lifetime of this
orchestrator run. Steps 2a, 2b, 2c, 2d, 3, 4, 5, and 6 all consume that
in-memory object. **No file is re-read after Step 2 silent recon completes,
except via the Step 2 amendment sub-step below.**

If a downstream step needs information from a file that was not captured in
Step 2, that is a Step 2 completeness defect. Resolve it via a **Step 2
amendment**, not by silently re-reading from a later step.

### Step 2 amendment (when downstream finds a missing read)

When a downstream step (2a, 2b, 2c, 2d, 3, 4, 5, or 6) detects that
`investigation_context` is missing a finding it needs:

1. Pause the downstream step.
2. Read the missing file(s) — and only those file(s).
3. Append the new findings to the in-memory `investigation_context` object
   under the appropriate field, marking each new entry with
   `added_via: step_2_amendment` and the step id that triggered the
   amendment (e.g. `triggered_by: step_3a`).
4. Re-emit `prd_investigation_manifest` telemetry covering only the
   amended files, with `event_qualifier: amendment`.
5. Resume the downstream step.

A full re-run of silent recon is **not** required for a targeted amendment.
A full re-run is required only when the amendment scope grows beyond a
handful of files (heuristic: more than five files added via amendment in a
single orchestrator run), at which point the orchestrator stops the
amendment chain and re-runs Step 2 from scratch.

### What to read

- `.context/components/manifest.yaml` — full component inventory **including
  the natural-language alias layer** (see Step 2d)
- Every component YAML for components plausibly in scope (matched by feature
  area, page name, component type, **or natural-language alias match** — see
  Step 2d)
- Angular components (`.ts`, `.html`, `.scss`) for affected pages/features
- Angular services and models/interfaces for the feature area
- Routing config and guards relevant to the affected pages
- Stored procedures (`usp_*`) related to the feature area
- Views (`vw_*`) consumed by the feature area
- Configuration and reference tables
- Test files in the feature area (to understand current coverage)
- DAL files and API controllers for the feature area

### What to record internally

Findings are stored as a structured `investigation_context` object. This object
is **never shown to the PM in raw form** — it is:
1. Written into per-sub-PRD breakdown files so prd-interviewer reads it and
   does not re-run recon from scratch
2. Used internally to formulate precise business questions
3. Used to generate Component Pattern Summaries written into the per-sub-PRD
   breakdown file (see Step 6 and the Component Pattern Summaries section)

The `investigation_context` block records:

```yaml
investigation_context:
  feature_area_summary: "[2-3 sentences in business language]"
  affected_pages: []            # page/screen names (business names)
  product_surfaces: []          # see Step 2c — enumerated surfaces this feature touches
  matched_components: []        # IDs from manifest.yaml (exact + alias matches)
  alias_matched_components: []  # IDs that matched only via the alias layer (Step 2d)
  new_components: []            # areas with no matching pattern; closest component_type noted
  affected_sps: []              # inferred SP names — internal only, never surfaced to PM or PRD
  affected_views: []            # inferred view names — internal only
  identified_vd_pages: []       # pages with known validation dependency impact
  cross_page_relationships: []  # entity/action chains across pages
  consistency_issues: []        # contradictions between work item and codebase
  files_read: []                # structured manifest: {file, layer, summary}
```

**Technical details stay silent.** SP names, return codes, view column names,
class names, flag names — none of these are ever shown to the PM or written
into PRD output. They inform business questions only.

### Step 2a — Emit investigation manifest telemetry

After reconnaissance completes, emit a `prd_investigation_manifest` telemetry
event containing the full `files_read` list grouped by layer (frontend
components, services, models/interfaces, stored procedures, views, tests).
This event is constructed entirely from the in-memory `investigation_context`
object — **no file is re-opened** to build the manifest.

### Step 2b — Context consistency validation

Cross-validate the work item description against codebase findings, working
**exclusively from the in-memory `investigation_context` object produced by
Step 2**. No file is re-read in this step.

1. **Scope contradictions** — work item describes a component that does not
   exist or exists differently
2. **Missing references** — context documents reference components/SPs/views
   not found in codebase
3. **Incomplete context** — work item mentions N requirements but defines fewer
4. **Cross-document inconsistencies** — multiple sources disagree on scope

For each issue: add a `consistency_issue` entry to the in-memory object and a
priority question to ask the PM at the start of Step 3.

### Step 2c — Feature surface enumeration gate (mandatory)

**Before any breakdown reasoning, enumerate every product surface the feature
touches.** A surface is any externally observable artefact a user, downstream
consumer, or operator interacts with. The required surface categories:

| Surface category | Examples |
|---|---|
| UI page | Page or screen the user navigates to |
| UI affordance | Toolbar action, button, dialog, toast, side panel, modal |
| API route | HTTP endpoint exposed by the API |
| Calculation engine | Allocation, FTP, profitability, or other engine entry point |
| Storage table | Persisted table the feature reads or writes |
| Storage column | Column added or modified on an existing table |
| Stored procedure | SP that owns business logic for the feature |
| View | Read view consumed by the feature |
| Telemetry event | Event emitted to the telemetry log |
| Configuration key | Workflow-config or other configuration value the feature reads |
| Background job | Scheduled or queued task |
| Integration | Outbound call, Dataverse sync, file export, etc. |
| Permission / role | A new permission, role gating, or access-control rule the feature introduces or relies on (e.g. "Profitability-Admin-only") |
| Validation dependency | A cross-page "when X changes, Y becomes invalid until reconciled" chain with its own state machine and user-visible signal (warning banner, blocked-calc prompt). Distinct from per-field validation rules, which are properties of UI affordances, not surfaces |
| Concurrency contention | A multi-user collision-handling protocol with its own UI, copy, and state machine (e.g. "another admin saved while you were editing" → 3-button dialog with Cancel / Load Latest / Save Anyway). Distinct from the underlying locking strategy, which is a property of a save action, not a surface |
| Audit trail / activity log | A user-visible record of who changed what when, with its own query model and access controls |

Record the enumerated surfaces in the `product_surfaces` field of
`investigation_context`. Each entry carries:

```yaml
product_surfaces:
  - surface_category: [ui-page|ui-affordance|api-route|...]
    business_name: [name a PM would recognise]
    technical_reference: [internal identifier — kept off PM-facing output]
    sub_prd_candidate: [sub-prd-id this surface belongs to]
```

**Gate (binding):** A breakdown that does not list enumerated surfaces per
sub-PRD is rejected at the Step 5 self-review gate. Every recommended sub-PRD
must carry its own subset of `product_surfaces` entries via the
`sub_prd_candidate` field. Coverage check: every surface in `product_surfaces`
must be assigned to exactly one sub-PRD; the union of all sub-PRD surface
lists must equal `product_surfaces` exactly.

### Step 2d — Semantic / fuzzy component discovery

Exact-name component matching is **insufficient** before declaring a feature
has no application equivalent. Before Step 3, perform a semantic / fuzzy pass
against `.context/components/manifest.yaml` using the **natural-language alias
layer** (see the manifest's top-level `aliases` block and per-component
`aliases:` fields).

**Algorithm:**

1. Extract the candidate vocabulary from the work item, the PM's context
   documents, and the affected pages list — every noun phrase a PM might use
   to refer to a UI affordance (e.g. "read view", "edit grid", "rule list",
   "workflow tile").
2. For each candidate phrase, normalise to lowercase and strip punctuation,
   then match against the manifest's alias layer. A match is recorded when
   the candidate phrase equals any alias verbatim **or** when the candidate
   phrase contains any alias as a substring after normalisation.
3. For each matched component id, register the component in
   `alias_matched_components` with the matching alias and the candidate
   phrase that triggered the match.
4. Promote every `alias_matched_components` entry into `matched_components`
   for downstream Step 3 / Step 4 reasoning, so the breakdown reasoning sees
   a single unified match list.

**Binding rule:** Before any sub-PRD is recommended with an `application
equivalent: none` finding for a UI affordance, Step 2d must have run and
produced zero matches for the candidate phrases describing that affordance.
A non-empty `alias_matched_components` list for any candidate phrase means
the affordance has an application equivalent — the brief author and the
interviewer must cite the matched component YAML when reaching the demo
brief.

**Manifest defect detection.** Every component in `.context/components/manifest.yaml`
must carry an `aliases:` field with at least one alias (binding manifest rule
— see the manifest header). If Step 2d encounters a component whose `aliases:`
field is missing or empty, surface it as a `consistency_issue` with
`priority_question` text such as "Component `[id]` is missing its alias
layer — recall may be degraded for features touching this component." Do
not silently degrade the alias-layer recall.

**Worked example.** A work item describes "the read-only display of the
allocation rules". Candidate phrases include "read-only display", "display
mode", and "rules list". The alias layer matches `view-only` (aliases
include "read view", "display mode", "read-only grid") and `allocation-rules`
(aliases include "rules list", "rules grid"). Both ids are added to
`alias_matched_components`. Declaring "no application equivalent" for either
is no longer permitted.

---

## Step 3 — Intelligent breakdown reasoning

Reason **entirely from the in-memory `investigation_context` object**. No file
is re-read in this step.

Before recommending any split, think holistically about the feature:

- What pages/screens are involved? What is the user trying to accomplish on each?
- What are all the user actions available? (add, edit, delete, view, filter,
  export, bulk operations, configuration toggles…)
- What similar existing pages already implement comparable patterns? What can be
  inferred from those rather than re-asked?
- Are there validation dependencies (VDs) in scope? Where do they surface?
- Are there cross-page impacts — does an action on this page affect data shown
  elsewhere?
- Are there calculation or allocation processes involved that need a separate
  calculation demo?
- What is the natural grouping of these areas that keeps each sub-PRD coherent
  and independently reviewable?

### Step 3a — Symmetric-surfaces detection (mandatory)

**Before recommending a split, detect symmetric (mirror-image) surfaces and
group them into a single sub-PRD rather than splitting into two.**

**Detection criterion (all three must hold):**

1. **Same component patterns.** The two surfaces match the same set of
   `component_type` values in `.context/components/manifest.yaml` (or the
   same set of `matched_components` ids from Step 2d's alias layer).
2. **Same workflow shape.** The user-visible workflow on each surface
   follows the same shape end-to-end — same entry points, same intermediate
   states, same exits. The surfaces differ only in **which entity** the
   workflow operates on.
3. **Parameterised by entity name only.** The only material difference
   between the two surfaces is the entity name (e.g. "Product" vs
   "Transaction Type", "Income" vs "Expense", "Retail" vs "Commercial").
   Copy strings, dialog structure, toolbar composition, state machine, and
   storage shape are otherwise identical.

   **"Storage shape" means same logical shape, not same physical table.**
   Two surfaces are parameterised by entity if they each add the same kind
   of column (e.g. a `UnitCost` decimal column) to the same kind of table
   (e.g. a leaf-level hierarchy table) — even when the underlying physical
   tables differ (e.g. Product table vs Transaction Type table). The
   physical-table difference is itself the entity parameterisation, not a
   reason to split. (Locked decision — PROF-354 Unit Costs is the canonical
   worked example.)

When all three hold, **group the two surfaces into one sub-PRD**. The sub-PRD
scope sentence names both entities. The Component Pattern Summary section
covers the shared component pattern once. Sample data covers both entities.
Acceptance criteria are written once and parameterised by entity.

**Worked example — PROF-354 (Unit Costing).** The Product Unit Costs page
and the Transaction Unit Costs page in PROF-354 are mirror images:

- **Same component patterns:** both pages compose the same `view-only-hierarchy`
  (read view) and `spreadsheet-editor` (edit view) over a hierarchical grid,
  with the same toolbar (`emp-switch-view-button`, `emp-export-button`, hide-
  leaves toggle), the same Kendo discard dialog, and the same SweetAlert2
  guard dialog.
- **Same workflow shape:** Admin navigates → reads grid → toggles to edit →
  edits leaf cells → saves atomically (or discards via dialog) → returns to
  read view. State machine and validation flow are identical.
- **Parameterised by entity name only:** the only material differences are
  the entity name ("Product Unit Costs" vs "Transaction Unit Costs"), the
  underlying hierarchy (Product vs Transaction Type), and the storage table
  the saved value lands on. Copy strings reuse a single `pageLabel()` helper.

These two surfaces **must be grouped into one sub-PRD** (PROF-354 sub-prd-1),
not split into two. The orchestrator would reject a split that produced
"sub-prd: Product Unit Costs page" and "sub-prd: Transaction Unit Costs page"
as separate entries.

**Asymmetric-surfaces counter-example.** Two pages that share a
`spreadsheet-editor` component pattern but differ in workflow shape (e.g.
one is read-only, the other is editable; one feeds a calculation, the other
feeds a report) are **not** symmetric — they fail criterion (2). Group only
when all three criteria hold.

### Self-review gate — after silent recon

Before proceeding to the breakdown recommendation, verify (against the
in-memory `investigation_context` object only — no file re-reads):

| Check | Pass condition |
|---|---|
| Every relevant codebase area was investigated | No plausible-scope area was skipped without a documented reason |
| Files that could not be read are flagged | `files_read` entries include `status: could_not_read` for any blocked file |
| `investigation_context` block is complete | All fields populated or explicitly `null` with reason |
| `investigation_context` is consistent with the ADO/Linear scope | No field contradicts the work item without a documented consistency issue |
| `product_surfaces` is populated | Step 2c gate satisfied — every surface enumerated |
| Alias-layer pass has run | Step 2d completed; `alias_matched_components` is populated or explicitly empty |
| Symmetric surfaces grouped | Step 3a applied — no mirror-image surfaces are in separate sub-PRD candidates |

Fix any failures before presenting to the PM.

---

## Step 4 — Breakdown calibration rules

The split is governed by these principles:

1. **Target Tier 1–2 complexity per sub-PRD.** Use the complexity classifier
   thresholds from `references/complexity-classifier.md` (in prd-interviewer
   references). If a candidate sub-PRD hits Tier 3+, split it further until
   every sub-PRD is Tier 1 or 2. A breakdown that contains any Tier 3+
   sub-PRD is invalid and must not be presented to the PM.

2. **Every sub-PRD must carry an enumerated surface list and a tier
   classification.** Per the Step 2c gate, every recommended sub-PRD lists
   its assigned subset of `product_surfaces` entries and an explicit
   `complexity_tier` field (1 or 2). A sub-PRD recommendation that omits
   either is rejected at the Step 5 self-review gate.

3. **Split at natural feature boundaries**, not at individual action level:
   - A single page with standard CRUD + filtering is one sub-PRD, not four
   - A page with complex rule-building logic plus a separate reporting view
     may be two
   - Cross-page dependency impacts may be a separate sub-PRD from the primary
     page changes
   - Calculation or allocation logic that requires a dedicated worked example
     demo is a strong split indicator

4. **Mirror-image surfaces are one sub-PRD, never two.** Symmetric-surfaces
   detection per Step 3a is mandatory; group symmetric surfaces.

5. **Minimum 2 sub-PRDs only when genuinely independent.** A small feature
   may produce a single sub-PRD. Never split artificially.

6. **Each sub-PRD must be independently reviewable** — a reviewer reading it
   should understand the full business requirements for that area without
   needing to read the other sub-PRDs (except for explicit cross-references).

7. **`dependency_order` is explicit.** Every sub-PRD entry states its
   prerequisites so sprint sequencing is understood before the first interview.

---

## Step 5 — PM confirmation

**Self-review gate (pre-presentation).** All sub-PRD-independence and
breakdown-quality checks happen here, **before** presenting to the PM. The
Step 6 self-review gate covers only write success and in-memory YAML
well-formedness — there is no duplicate validation of sub-PRD independence
or Tier or surface-coverage at Step 6.

Verify (against the in-memory breakdown plus `investigation_context` — no
file re-reads):

| Check | Pass condition |
|---|---|
| Each sub-PRD is genuinely independently reviewable | A reviewer could read it without needing the others |
| No sub-PRD hits Tier 3+ complexity | Every sub-PRD scores Tier 1 or 2 on the classifier |
| Every sub-PRD carries an enumerated surface list | Per Step 2c — `product_surfaces` subset assigned via `sub_prd_candidate` |
| Surface coverage is exhaustive and non-overlapping | The union of all sub-PRD surface lists equals `product_surfaces`; no surface assigned twice |
| Symmetric surfaces are grouped | Step 3a applied — no mirror-image surfaces in separate sub-PRDs |
| `dependency_order` is explicit and accurate | No circular dependencies; all prerequisites correctly identified |
| No major feature area is uncovered | The full scope of the work item is accounted for across all sub-PRDs |
| Alias-layer pass produced no orphan affordances | Every `alias_matched_components` entry is assigned to a sub-PRD |

Fix any failures before presenting.

### Presentation to PM

Present the breakdown recommendation to the PM with:

1. **Brief business-language summary** of what was found in the codebase
   (3–4 sentences: which areas are affected, what kind of change it is, which
   user workflows are touched). No SP names, no class names, no internal
   technical constructs.

2. **Complexity classification** for the overall feature and the rationale
   for the proposed split.

3. **Any context consistency issues** found (priority questions to resolve).

4. **Proposed sub-PRDs**, each with:
   - `id` (e.g. `sub-prd-1`)
   - `title` (e.g. "Rules Grid — CRUD Operations")
   - `scope` — 2–3 sentences in business language
   - `complexity_tier` — 1 or 2 (mandatory)
   - `enumerated_surfaces` — business-named list (the PM-facing form of the
     `product_surfaces` subset assigned to this sub-PRD)
   - `requires_calc_demo` — true/false
   - `requires_ui_demo` — true/false
   - `dependency_order` — which sub-PRDs must complete before this one
     (e.g. "none" or "depends on sub-prd-1")

5. **Dependency order diagram** (text-based if mermaid is not available) so
   sprint sequencing is clear.

6. Ask the PM to:
   - Adjust any sub-PRD scope
   - Add or remove sub-PRDs
   - Confirm the dependency order
   - Say "confirmed" when satisfied

**The PM must explicitly confirm before Step 6.**

---

## Step 6 — Write breakdown files

On PM confirmation, write:

1. **One per-sub-PRD breakdown file per recommended sub-PRD:**
   `.sage/prds/[FEATURE_ID]/prd-breakdown.[sub-prd-id].md`
2. **A master breakdown INDEX file** pointing at every per-sub-PRD file:
   `.sage/prds/[FEATURE_ID]/prd-breakdown.md`

Create `.sage/prds/[FEATURE_ID]/` if it does not exist.

### Master breakdown file — INDEX format

The master `prd-breakdown.md` is an **index file**, not the full breakdown.
It carries the feature-level YAML front-matter and a list of per-sub-PRD
breakdown files. It does **not** contain the per-sub-PRD bodies or the
`investigation_context` block — those live in the per-sub-PRD files.

```yaml
---
feature_id: "[FEATURE_ID]"
linear_issue_id: "[LIN-####]"
prd_run_id: "[UUID]"
created: "[ISO date]"
status: confirmed
breakdown_layout: per-sub-prd-files
---

# PRD Breakdown — [Feature Title]

[2–4 sentence business-language summary of the feature and the split.]

## Sub-PRDs

| id | title | complexity_tier | dependency_order | breakdown_file |
|---|---|---|---|---|
| sub-prd-1 | [title] | [1\|2] | none | `prd-breakdown.sub-prd-1.md` |
| sub-prd-2 | [title] | [1\|2] | depends on sub-prd-1 | `prd-breakdown.sub-prd-2.md` |
```

### Per-sub-PRD breakdown file format

Each `prd-breakdown.[sub-prd-id].md` carries the full sub-PRD entry, the
sub-PRD's slice of `investigation_context`, and one Component Pattern
Summary per matched component (see the Component Pattern Summaries section
below).

```yaml
---
feature_id: "[FEATURE_ID]"
sub_prd_id: "[sub-prd-id]"
linear_issue_id: "[LIN-####]"
prd_run_id: "[UUID]"
created: "[ISO date]"
status: confirmed
---

# Sub-PRD Breakdown — [sub-prd-id]: [title]

## Sub-PRD entry

- **title**: [title]
- **scope**: [2–3 sentence business description]
- **complexity_tier**: [1|2]
- **enumerated_surfaces**:
  - [business-named surface 1]
  - [business-named surface 2]
- **matched_components**: [[component-id-1], [component-id-2]]
- **alias_matched_components**: [[component-id-3]]
- **new_components**: [[component_type: [type], area: [business area description]]]
- **affected_sps**: [[sp-name-1]]      # internal only — never surfaced to PM or PRD
- **requires_calc_demo**: [true|false]
- **requires_ui_demo**: [true|false]
- **dependency_order**: [none | depends on [sub-prd-id]]
- **output_path**: .sage/prds/[FEATURE_ID]/[sub-prd-id]/

## investigation_context (sub-PRD slice)

feature_area_summary: >
  [2–3 sentence business summary scoped to this sub-PRD]

affected_pages:
  - [page/screen name]

product_surfaces:
  - surface_category: [ui-page|ui-affordance|api-route|...]
    business_name: [name a PM would recognise]
    technical_reference: [internal identifier — internal only]

matched_components:
  - id: [component-id]
    name: [component name]
    component_type: [type]
    file: [yaml file path]
    matched_via: [exact|alias]
    matched_alias: [alias phrase, if matched_via=alias]

new_components:
  - area: [business area description]
    closest_component_type: [type]

affected_sps:
  - [sp-name]                          # internal only

affected_views:
  - [view-name]                        # internal only

identified_vd_pages:
  - [page name]

cross_page_relationships:
  - source: [page/entity]
    target: [page/entity]
    relationship: [description]

consistency_issues:
  - issue: [description]
    priority_question: [the question to ask at interview start]

files_read:
  - file: [path]
    layer: [frontend-component|service|model|stored-procedure|view|test|config]
    summary: [one-line summary]

## Component Pattern Summaries

[One summary per matched component — see the Component Pattern Summaries
section of this SKILL.md for the required fields, size budget, and drift rule.]
```

### Self-review gate — after writing breakdown files

This gate validates **only write success and in-memory YAML well-formedness**.
All sub-PRD-independence, Tier, surface-coverage, and symmetric-grouping
checks happened at the Step 5 self-review gate; **this gate does not
re-validate them**.

**Belt-and-braces — no file re-read.** This gate explicitly does not re-open
either the just-written `prd-breakdown.md` master index or any per-sub-PRD
breakdown file. The Step 2 in-memory discipline (see Step 2) is the primary
statement of this rule; this gate restates it as a safety net for any
literal-reading agent that loads Step 6 in isolation.

YAML well-formedness is validated **in memory** before writing the file —
the orchestrator constructs the YAML payload as a string in memory, parses
it (e.g. via an in-process YAML parser) to confirm well-formedness, and only
then writes. The just-written file is **not re-opened** to validate.

| Check | Pass condition |
|---|---|
| Master index file written | `prd-breakdown.md` exists at the expected path; write returned success |
| One per-sub-PRD file written per sub-PRD | Every confirmed sub-PRD has `prd-breakdown.[sub-prd-id].md`; writes returned success |
| YAML well-formed (in memory) | The YAML payload parsed cleanly in memory before write |
| Per-sub-PRD `output_path` values are distinct and non-overlapping | No two per-sub-PRD files declare the same `output_path` |

### Fallback rule — missing per-sub-PRD file (in-flight PRDs predating Phase B)

For sub-PRDs whose interviews were started before per-sub-PRD breakdown files
existed (the in-flight set predating this lift), the per-sub-PRD file may be
missing. The expected read-path is documented in
`skills/prd-interviewer/references/component-matching.md` and will be
wired into `prd-interviewer/SKILL.md` in Phase C of this lift:

- **Primary read path:** prd-interviewer Step 1 reads
  `.sage/prds/[FEATURE_ID]/prd-breakdown.[sub-prd-id].md`.
- **Fallback read path:** if the per-sub-PRD file is missing, prd-interviewer
  falls back to the master `.sage/prds/[FEATURE_ID]/prd-breakdown.md`. The
  master breakdown, in the legacy single-file layout, carries the full
  sub-PRD entries inline.

Back-fill of per-sub-PRD files for existing sub-PRDs happens **on next
touch** — the next time a sub-PRD is re-interviewed, regenerated, or amended,
the orchestrator writes the per-sub-PRD file at that point. No big-bang
back-fill.

---

## Component Pattern Summaries

For every component recorded in a sub-PRD's `matched_components` (exact match
or alias match), the orchestrator writes a compressed Component Pattern
Summary in that sub-PRD's per-sub-PRD breakdown file under the `## Component
Pattern Summaries` heading.

### Required fields

Per matched component:

```yaml
- component_id: [id from manifest.yaml]
  component_name: [Angular component class name]
  selector: [Angular selector]
  component_type: [pattern type]
  yaml_file: [full path to the component's YAML, e.g. .context/components/view-only.yaml]
  state_set:
    - [state name]: [one-line description of what the state looks like / does]
    - [state name]: [...]
  copy_strings_verbatim:
    labels: [exact button / column / field labels, verbatim from the YAML]
    tooltips: [exact tooltip text, verbatim]
    empty_state_messages: [exact empty-state copy, verbatim]
    error_messages: [exact error copy, verbatim]
    toast_messages: [exact toast copy, verbatim]
  interactions:
    - [user action] → [outcome]
    - [user action] → [outcome]
  behaviour_summary: >
    [2–4 sentence business-language description of what the component
    does and when. No class names, no internal field names.]
```

### Size budget

- **Target:** 40 lines per summary.
- **Hard cap:** 80 lines per summary.

When a summary would exceed the hard cap, **do not** truncate the summary
silently. Instead, write a pointer block:

```yaml
- component_id: [id]
  component_name: [name]
  yaml_file: [path]
  summary_status: see_full_yaml
  reason: >
    Full Component Pattern Summary exceeds the 80-line hard cap. The
    interviewer must read [yaml_file] directly during P2 for this component.
```

When a pointer block is emitted instead of a full summary, **also emit a
`summary_cap_exceeded` telemetry event** (see Telemetry section).

### Drift rule

A Component Pattern Summary becomes stale when the underlying YAML changes.
The orchestrator regenerates a summary when:

```
mtime(source YAML file) > mtime(per-sub-PRD breakdown file the summary lives in)
```

Drift is checked at the start of any orchestrator run that touches a sub-PRD
whose breakdown file already exists (Step 1a re-use detection branch). For
every matched component in the affected sub-PRD, compare the source YAML
mtime against the per-sub-PRD breakdown file mtime; if the YAML is newer,
regenerate that component's summary block in the per-sub-PRD file.

The orchestrator's mtime check works **without re-reading the YAML content**
— `stat`-equivalent metadata is sufficient. Re-reading the YAML happens only
when regeneration is required.

### Read-path expectation for prd-interviewer (documented here for Phase C wiring)

Phase C of this lift wires `prd-interviewer/SKILL.md` to consume Component
Pattern Summaries from the per-sub-PRD breakdown file at interview Step 1.
The component-matching reference doc
(`skills/prd-interviewer/references/component-matching.md` Step 3)
already documents this consumption pattern; the SKILL.md wiring is reserved
for Phase C per the lift plan. The orchestrator's contract is to produce
the summaries in the per-sub-PRD breakdown file in a format the interviewer
can consume verbatim — no further translation is needed.

---

## Step 7 — Confirm and hand off

Tell the PM:

"Breakdown confirmed. The master index has been written to:
`.sage/prds/[FEATURE_ID]/prd-breakdown.md`

Per-sub-PRD breakdown files have been written to:
- `.sage/prds/[FEATURE_ID]/prd-breakdown.sub-prd-1.md`
- `.sage/prds/[FEATURE_ID]/prd-breakdown.sub-prd-2.md`
- [...]

To run the interviews, open a new Cursor chat for each sub-PRD and invoke the
`prd-interviewer` skill. Start with:

> 'Run prd-interviewer for [sub-prd-id] of feature [FEATURE_ID].'

The interviewer will read the per-sub-PRD breakdown file automatically and
start the interview without re-running recon. If a per-sub-PRD file is
missing for an in-flight PRD that predates Phase B of the PRD pipeline lift,
the interviewer falls back to the master breakdown.

Interview in this order: [list dependency order]."

---

## Strict separation of concerns

Component and SP data in the breakdown manifest is used **solely** to:
- Make the prd-interviewer smarter (avoid re-asking what can be inferred from
  existing patterns)
- Make demos look and behave like the real application (authentic states, exact
  copy, real colors)

It does **not** appear in any PRD output, does not direct the dev team on what
to reuse or change, and is never presented to the PM as implementation guidance.
The PRD's job is business requirements. The development team determines
implementation from those requirements.

---

## Telemetry

Append to `.sage/prd-interview-telemetry.jsonl` (or the path in
`prd.telemetryFile`). All events carry: `timestamp` (ISO UTC), `event`,
`workflowKind: "prd_orchestrator"`, `linearIssueId`, `prdRunId`.

| Event | When |
|---|---|
| `prd_preflight` | Step 0 outcome |
| `prd_investigation_manifest` | After Step 2 completes |
| `prd_breakdown_proposed` | When breakdown is presented to PM |
| `prd_breakdown_confirmed` | When PM confirms |
| `summary_cap_exceeded` | When a Component Pattern Summary exceeds the 80-line hard cap and a `see_full_yaml` pointer is emitted instead. Payload includes `sub_prd_id`, `component_id`, `yaml_file`, `attempted_line_count`, `source_yaml_line_count`, and `compression_ratio` (= `attempted_line_count / source_yaml_line_count`). The extra two fields let the effectiveness-evaluator distinguish "summary format is bloated" (low compression ratio + cap exceeded → tighten the format) from "underlying YAML is huge" (high compression ratio + cap exceeded → raise the cap). Reserved for the prd-interviewer-effectiveness-evaluator to consume after the first three sub-PRDs are produced, so the cap can be tuned with real data. |

Never fail the orchestrator if telemetry cannot be written — log and continue.

---

## Constraints

- Always complete Step 0 repo preflight before Step 1
- Always confirm context checklist (Step 1b) before silent investigation
- Step 2 builds an in-memory `investigation_context` object; Steps 2a, 2b,
  2c, 2d, 3, 4, 5, and 6 consume the in-memory object only — **no file is
  re-read after Step 2 silent recon completes**
- Never narrate the recon process to the PM
- Never show SP names, return codes, view column names, class names, flag names,
  or any internal technical construct to the PM
- Step 2c feature-surface enumeration gate is binding: a sub-PRD recommendation
  without enumerated surfaces is rejected at the Step 5 self-review gate
- Step 2d semantic / fuzzy component discovery must run before any sub-PRD
  is recommended with an "application equivalent: none" finding for a UI
  affordance
- Step 3a symmetric-surfaces detection is mandatory: mirror-image surfaces
  are grouped into one sub-PRD, never split into two
- Every recommended sub-PRD carries an enumerated surface list **and** a
  complexity tier classification (Tier 1 or Tier 2). Tier 3+ sub-PRDs must
  be split further until every sub-PRD is Tier 1 or 2
- Never write component/SP data into PRD output files
- The master `prd-breakdown.md` is an index; per-sub-PRD bodies live in
  `prd-breakdown.[sub-prd-id].md`
- The Step 6 self-review gate validates only write success and in-memory
  YAML well-formedness; all sub-PRD-independence / Tier / surface-coverage /
  symmetric-grouping checks happen at the Step 5 self-review gate (no
  duplicate validation across Steps 5 and 6)
- YAML well-formedness is validated **in memory** before writing; the
  just-written file is never re-opened to validate
- Component Pattern Summaries respect the 40-line target / 80-line hard cap;
  over the hard cap, emit a `see_full_yaml` pointer plus a
  `summary_cap_exceeded` telemetry event
- A Component Pattern Summary is regenerated when the source YAML's mtime
  is newer than the per-sub-PRD breakdown file's mtime
- The PM must explicitly confirm before any breakdown file is written
