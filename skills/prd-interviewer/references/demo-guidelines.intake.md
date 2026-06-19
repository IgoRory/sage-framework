# Demo Guidelines — Intake (P0/P1 mockup and recording protocol)

Reference for prd-interviewer. Self-contained — no external skill references.

This file governs **intake-time** decisions made before the demo brief is
written. Its companion file `demo-guidelines.generation.md` governs the
downstream demo handoff chat's design contract. Together they map intake
materials (mockups, recordings, work-item references) onto the demo brief
sections defined in `sub-agent-delegation.md` §5 and onto the PRD section
numbers in `prd-section-schema.md`.

The application-fidelity hard rule in
[`sub-agent-delegation.md`](./sub-agent-delegation.md) §4 governs intake
across all three surfaces — the brief author always cites the relevant
component YAML(s) when an application equivalent exists. This file's
intake protocol is how the interviewer reaches that citation list.

---

## P0 — Work-item references (always)

Before any interview question is asked, the interviewer confirms the work-item
references the PM has on hand:

| Reference | What it provides | PRD section it feeds |
|---|---|---|
| Linear issue / ADO work item | Feature title, business problem, scope outline | §1 (description), §2 (triggers), §5 (scope) |
| Linked design docs (Figma, Notion, etc.) | Visual reference (intake-time only — never linked from the PRD) | §4 (user-facing flows), demo brief Section 6 (verbatim text) |
| Linked tickets (blocked-by / blocks) | Dependencies | §8 (dependencies) |
| Per-sub-PRD breakdown file | `investigation_context`, `matched_components`, Component Pattern Summaries, surface enumeration | All sections; especially §6 (reuse decisions) and the demo brief |

**Rule.** External links are recorded in the interviewer's working context
only. The PRD itself never carries external links — visual references are
internalised at intake by extracting the affordance list and citing the
matching application YAMLs. This satisfies the
"never-accept-file-attachments-or-external-links" constraint while still
using PM-provided references productively at intake.

---

## P1 — Mockup file ingestion

When the PM provides HTML mockups, wireframes, Figma exports, or any visual
file alongside the work item, run the **mockup intake checklist** below
before the first feature-definition question.

### Mockup intake checklist

- [ ] **Receive the mockup** as part of the P0 context-checklist gate. Record
  the file name and the PM's stated purpose (final UX / draft for discussion
  / redesign proposal) in the working context.
- [ ] **Classify the mockup** into one of three categories:
  - **(a) New screen — no application equivalent.** The mockup represents a
    page or affordance that does not exist in the production application.
    The demo brief grants the handoff chat production-grade design freedom,
    bounded by the brand palette and tone (per `demo-guidelines.generation.md`).
    The brief lists this affordance under "no application equivalent —
    generator's choice" per `sub-agent-delegation.md` §10.
  - **(b) Modification of an existing screen.** The mockup amends a page that
    exists in the application. The cited application YAMLs govern fidelity
    for unchanged affordances; the diffs are documented in the brief's
    Section 4 and Section 6.
  - **(c) Redesign proposal of an existing screen.** The mockup proposes a
    different visual pattern for an affordance that already has an
    application equivalent. **Stop and ask the PM** which wins: the existing
    YAML or the mockup's proposal. The PM's ruling becomes a Locked Decision
    in the working context, and the brief documents the decision explicitly.
- [ ] **Extract the affordance list** from the mockup. Every visible
  affordance (buttons, dialogs, toasts, badges, validators, loaders,
  toolbars, scenario rails, debug panes, banners, breadcrumbs, edit-mode
  cells, disabled-cell rendering) is enumerated.
- [ ] **For each extracted affordance, cite the matching component YAML or
  flag no-equivalent.** Use the orchestrator's per-sub-PRD breakdown
  Component Pattern Summaries (Phase B T2 output) and the manifest alias
  layer (Phase B Step 2d) as primary sources. If a candidate phrase yields
  zero alias matches AND no Component Pattern Summary covers it, flag it
  as `no application equivalent — generator's choice`.
- [ ] **Map the extracted copy strings** to either the cited YAML's
  `copy_strings_verbatim` block (Phase B Step 3 read path) or to a
  `[TEXT TBD — requires PM decision]` marker per the three-tier message
  text sourcing protocol.
- [ ] **No silent gaps.** Every affordance traces to either a cited YAML or
  to an explicit no-equivalent flag — never to nothing.

### Brief-input mapping (mockup)

The mockup intake outputs feed the demo brief sections as follows:

| Mockup intake output | Demo brief section (per `sub-agent-delegation.md` §5) |
|---|---|
| Cited YAMLs (matched component list) | Section 3 — Component YAML files you must deep-read |
| Extracted scenario list (per affordance) | Section 4 — Scenarios to demonstrate (with `scenario_id` + AC mapping) |
| Verbatim copy strings | Section 6 — Verbatim text strings |
| Visual notes (palette, fonts, layout tokens) | Section 7 — Visual notes |
| State requirements per affordance | Section 8 — State requirements |
| No-equivalent affordances | Section 10 — No-application-equivalent call-outs |

### Mockup intake also feeds the PRD

The mockup intake is **only** internalised — the mockup file itself is never
referenced from the PRD. Intake outputs feed:

| PRD section | What the intake provides |
|---|---|
| §1 (Plain-English description) | The user goal the mockup illustrates |
| §2 (Triggering conditions) | The entry point shown in the mockup |
| §4 (User-facing flows) | The flow the mockup walks through |
| §11 (Demo reference) | A pointer to the to-be-produced demo HTML (handoff chat output) |

---

## P1 — Recording intake

When the PM provides a screen recording of current application behaviour,
the recording is a **visual reference for the interviewer's working
context only**. The recording is never linked from the PRD or the demo
brief. The interviewer uses the recording to:

### Recording intake checklist

- [ ] **Receive the recording** as part of the P0 context-checklist gate.
  Record the file name and the PM's stated scope (which feature areas it
  covers) in the working context.
- [ ] **Classify the recording** as either (a) current production behaviour
  the feature must preserve, or (b) current production behaviour the
  feature is changing. The category determines whether the recording's
  affordances trace to "preserve" rules in PRD §3 or "change" rules.
- [ ] **Extract the affordance list and copy strings** from the recording.
  For every observed affordance, locate its component YAML in the
  per-sub-PRD breakdown and cite it. The cited YAML is the source of
  truth for fidelity per the application-fidelity hard rule — even if the
  recording shows different copy than the YAML, the YAML wins (this is
  a recording-vs-application drift signal the interviewer should raise as
  an Open Question or DI item).
- [ ] **Cross-check against component-matching.md Step 3 read path.** If the
  recording surfaces an affordance whose YAML is missing from the
  per-sub-PRD breakdown, the breakdown is incomplete — escalate by asking
  the PM to re-run the orchestrator (per the SKILL.md "no file re-read
  after the breakdown is consumed" discipline; the interviewer does not
  patch the breakdown by reading additional YAMLs).

### Brief-input mapping (recording)

Recording intake outputs feed the demo brief identically to mockup intake
outputs (see the table above). The recording itself is **not** cited from
the brief — only the YAMLs the recording's affordances trace to.

---

## Application-equivalent reconciliation flow

This flow runs whenever the interviewer is unsure whether an intake material
represents a new affordance or an existing one.

```
Intake material received
    │
    ▼
Extract affordance list
    │
    ▼
For each affordance:
    │
    ├── Found in per-sub-PRD breakdown's matched_components? ── yes ──► cite the YAML; record as REUSE
    │                                                                     │
    │                                                                     ▼
    │                                                              proceed to next affordance
    │
    └── no ──► run alias-layer search against .context/components/manifest.yaml
                │
                ├── alias match found? ── yes ──► cite the matched YAML; record as REUSE-via-alias
                │                                  ask PM to confirm the match
                │
                └── no ──► flag as "no application equivalent — generator's choice"
                          record under brief Section 10
```

### Mandatory intake questions

When a mockup or recording is provided, the interviewer asks the PM the
following questions before P1 begins. Answers are recorded in the working
context:

1. **Mockup status.** "Is this mockup the final UX or a draft for
   discussion?" If draft, every affordance is recorded provisionally and
   the brief flags it for PM re-confirmation at the Component Pattern
   Confirmation Report stage.
2. **Wording precedence.** "If a cited YAML's wording differs from the
   mockup's wording, which wins?" Default: YAML wins (application-fidelity
   hard rule). If the PM rules the mockup wins, the decision is locked and
   the brief explicitly documents the override under §10
   (no-equivalent or override call-outs).
3. **State-set completeness.** "Does the mockup omit any state we should
   expect to see?" The interviewer enumerates the YAML's state set and the
   mockup's depicted states; any gap is either confirmed-omitted (the
   feature genuinely doesn't need that state) or flagged as a missing state
   to ask about in P5.
4. **Recording scope.** "Does this recording capture every flow we need to
   preserve, or only one path?" Determines whether additional flows must
   surface during the interview.
5. **Redesign vs amendment.** "Is this a redesign of the existing screen,
   or an amendment that adds new capability?" Drives the
   application-equivalent classification (a/b/c above).

---

## Phase C scope note

Phase A authored this file as a stub reserving the structural home. Phase C
(this revision) wrote the full intake protocol against the New PRD Section
Schema and the Phase B orchestrator outputs (per-sub-PRD breakdown,
Component Pattern Summaries, manifest alias layer). The intake protocol
references PRD section numbers and brief section numbers stably; future
phases extend the protocol additively.
