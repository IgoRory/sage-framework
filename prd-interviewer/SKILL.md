---
name: prd-interviewer
description: >
  Conducts a structured interview with a Product Owner (the Product Manager) to
  produce a complete PRD draft and companion Component Specification child
  page, both structured to pass prd-completeness-check. Always starts from
  a Linear feature issue or ADO work item reference. Has read access to the
  Profitability codebase to ask informed questions about existing components,
  stored procedures, and data structures. Use this skill whenever a PM says
  "let's write a PRD", "help me spec this feature", "start a PRD for [feature]",
  or provides a Linear or ADO reference and asks to begin feature documentation.
  Do not begin writing a PRD without running this interview first.
---

# PRD Interviewer

Conducts a structured interview to produce two output artifacts:

1. **PRD draft** — saved as a new Notion page, structured to pass
   `prd-completeness-check`
2. **Component specification draft** — saved as a Notion child page of
   the PRD, linked explicitly from the PRD

Both artifacts are drafts. They are not submitted to `prd-completeness-check`
automatically — the PM reviews and refines them first, then runs the check
manually when they believe the PRD is ready.

---

## Before the interview begins

### Step 1 — Load the work item

Read the Linear feature issue or ADO work item provided by the PM.
Extract and confirm:
- Feature title
- Description or summary (however brief)
- Any linked client requests, feedback threads, or prior discussion
- Any acceptance criteria or requirements already noted
- Labels, priority, or cycle assignment

If the work item has very little content, note this and proceed — the
interview will surface what's needed. Do not ask the PM to fill out the
work item before starting.

### Step 2 — Codebase reconnaissance

Before asking the first question, scan the codebase to build context.
This allows the interview to ask informed questions rather than generic
ones. Do this silently — do not narrate the scan to the PM.

Look for:
- Existing UI components related to the feature area (by file name,
  component name, or directory structure)
- Stored procedures, views, or functions likely related to the feature
  (search by feature keyword in `usp_`, `vw_`, `fn_` prefixes)
- Affected tables likely involved (Adjusted_GL, GLAllocationLog, or
  feature-specific tables)
- Any existing PRD, spec, or design document for this or a related feature
  (search Notion via MCP)
- Related ProcessIDs in the ProcessID reference framework

Record your findings internally. Use them to:
- Pre-populate assumptions in interview questions ("I can see there's an
  existing DepartmentFilter component — is that being modified?")
- Skip questions where the answer is already clear from the codebase
- Flag components or data structures the PM may not have considered

### Step 3 — Set expectations

Before the first question, tell the PM:

> "I've loaded [work item title] and scanned the relevant parts of the
> codebase. The interview has [N] phases and typically takes 30–45 minutes.
> I'll ask questions one phase at a time. If you're unsure of an answer,
> say 'park it' and I'll flag it as a gap in the draft — it won't block us.
> At the end I'll produce a PRD draft and a Component Specification page
> in Notion for your review."

---

## Interview phases

Run phases in order. Do not skip phases. Complete all questions in a phase
before moving to the next. At the end of each phase, summarise what was
captured and confirm with the PM before proceeding.

Full question sets for each phase are in `references/question-sets.md`.
Read the relevant section before beginning each phase.

| Phase | Name | Purpose |
|---|---|---|
| P1 | Feature overview | Why this feature exists, who benefits, what problem it solves |
| P2 | Functional scope | What the feature does — high level before detail |
| P3 | Affected pages and screens | Which pages change, which are new |
| P4 | Component inventory | Every new and affected component on every affected page |
| P5 | Component specification | Per-component: states, interactions, data binding, options |
| P6 | Edge / empty / error states | Functional-area level non-happy-path behaviour |
| P7 | Acceptance criteria | Per-requirement testable outcomes |
| P8 | Out-of-scope boundaries | Explicit exclusions, data boundaries, adjacent features |
| P9 | Mockup confirmation | What mockups will be created and what they must show |

---

## Handling parked questions

When the PM says "park it" or cannot answer a question:
- Record the question and the phase it belongs to in a PARKED list
- Continue the interview without blocking
- At the end of the interview, present all parked items as a numbered
  list and ask the PM to work through them before the PRD is submitted
  to `prd-completeness-check`
- In the PRD draft, mark every section with a parked gap using:
  `⚠️ GAP: [question that was parked]`
- In the component spec draft, mark affected components similarly

A PRD with parked gaps can still be drafted and reviewed — it simply
cannot pass the completeness check until all gaps are resolved.

---

## Follow-up discipline

For every answer that contains vague language, ask one follow-up before
moving on. Do not accept and record the following without probing:

| Vague answer | Required follow-up |
|---|---|
| "It should be fast / responsive" | "What's the acceptable response time in milliseconds or seconds?" |
| "Standard error handling" | "What specifically should the user see when the operation fails?" |
| "Same as the existing [X]" | "Are there any differences in behaviour, states, or data binding from the existing [X]?" |
| "The usual validation" | "Which specific fields need validation, and what are the rules for each?" |
| "It follows the existing pattern" | "Which existing screen or component are we following, and are there any deviations?" |
| "We'll handle that later" | "Park it — I'll flag it as a gap in the draft." |
| "The API will provide it" | "Which endpoint or stored procedure, and what specific field?" |
| "It depends" | "Walk me through the conditions — what does it depend on?" |

One follow-up per vague answer. If the second answer is also vague,
park it and move on — do not loop.

---

## Phase summary and confirmation

At the end of each phase, present a bulleted summary of what was captured.
Example format:

> **P3 summary — Affected pages and screens:**
> - Allocation Rules page: modified (new filter panel, updated results table)
> - Rule Detail modal: new component
> - Export function: affected (new columns)
> - No new pages
>
> Is this correct before we move on?

Wait for confirmation before starting the next phase. If the PM corrects
something, update the summary and re-confirm.

---

## After the interview

### Step 1 — Resolve parked items

Present the parked list. Work through each item with the PM. If any
remain unresolved after one pass, note them as persistent gaps — the PM
will need to resolve these before submitting to `prd-completeness-check`.

### Step 2 — Produce the PRD draft

Use `references/prd-template.md` to structure the output. Fill every
section from the interview responses. Mark any persistent gaps with
`⚠️ GAP: [description]`.

Save as a new Notion page:
- Parent: the Profitability PRD database (ask PM for parent page if unsure)
- Title: `[Feature title] — PRD`
- Link the Linear or ADO work item in the Properties section

### Step 3 — Produce the component specification draft

Use `references/component-spec-template.md` to structure the output.
Create one entry per component captured in P4 and P5. Mark gaps.

Save as a Notion child page of the PRD:
- Title: `Component Specifications`
- Linked explicitly from the PRD (add a "Component Spec" property or
  inline link in the PRD header section)

### Step 4 — Confirm and hand off

Tell the PM:

> "Both drafts are saved in Notion. Review them and fill in any remaining
> gaps marked with ⚠️. When you're satisfied, run `prd-completeness-check`
> to assess readiness for the planning cycle. The check will tell you
> exactly what needs fixing if the score is below 80."

Do not run `prd-completeness-check` automatically — the PM reviews first.

---

## Reference files

- `references/question-sets.md` — full question sets for P1–P9
- `references/prd-template.md` — PRD output structure
- `references/component-spec-template.md` — component specification
  output structure
