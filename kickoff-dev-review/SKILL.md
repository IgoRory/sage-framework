---
name: kickoff-dev-review
description: >
  Processes a Teams meeting transcript from the kick-off session developer
  review discussion. Reads the transcript alongside the PRD and component
  specification, identifies and categorises all developer concerns, asks
  targeted follow-up questions for anything unresolved or ambiguous, then
  produces a concern log and PRD delta notes and updates the Notion PRD.
  Use this skill during the kick-off session immediately after the Teams
  recording is stopped and the transcript is available. The team remains
  on the call to answer follow-up questions in real time. Always runs
  before phase-splitter in the kick-off sequence.
---

# Kickoff Dev Review

Captures and structures developer concerns about a PRD during the
kick-off session. The team discusses the PRD verbally on a Teams call.
Once the recording is stopped and the transcript is available, this
skill processes it alongside the PRD and drives a targeted follow-up
exchange to resolve ambiguities — with the team still on the call.

**This skill does not ask pre-scripted questions.** Developer concerns
emerge from their reading of a specific PRD. The skill listens,
categorises, and probes — it does not lead.

---

## When to invoke

After the kick-off discussion concludes and the Teams recording has
been stopped. The transcript should be available within Teams within
1–2 minutes of stopping the recording. The team stays on the call.

The developer running Cursor invokes the skill and provides the Teams
meeting link or meeting ID.

---

## Step 1 — Load all inputs

**Load the PRD and component specification:**
Fetch the PRD and its Component Specification child page from Notion
via MCP. These are the reference documents against which all concerns
will be evaluated.

**Load the Teams transcript:**
Fetch the meeting transcript via the Microsoft 365 MCP using the
meeting link or ID provided by the developer. The transcript should
be speaker-attributed — each line prefixed with the speaker's name.

If the transcript is not yet available (processing delay), wait up to
2 minutes and retry once. If still unavailable after retry, ask the
developer to paste the transcript text directly into the chat.

**Confirm inputs are loaded before proceeding:**
> "I have the PRD ([title]), the component specification, and the
> Teams transcript ([N] lines, [N] speakers). Starting analysis."

---

## Step 2 — Parse the transcript

Read the full transcript. Extract every statement that represents:

- A question about the PRD (explicit: "how does X work?" or implicit:
  "I wasn't sure about...")
- A concern about feasibility, scope, or approach
- A contradiction or inconsistency the developer noticed between the
  PRD and the codebase or existing behaviour
- An assumption the developer is making that isn't confirmed in the PRD
- A missing edge case or error state the developer identified
- A data binding question (what field, what stored procedure, what
  Adjusted_GL attribute)
- A scope boundary question (is X in or out of scope?)
- A dependency or sequencing concern ("this can't be done until...")
- An open question that was raised but not resolved during the discussion

For each extracted item, record:
- Speaker (who raised it)
- Verbatim excerpt (the key sentence(s) from the transcript)
- Your interpretation of the concern in plain language
- Whether it was resolved in the discussion or remains open

Do not extract general discussion, affirmations, or social conversation.
Only extract substantive product or technical concerns.

---

## Step 3 — Cross-reference against PRD

For each extracted concern, check whether the PRD or component
specification already addresses it:

- **Addressed:** The PRD covers this — the developer may not have seen
  it, or their concern is answered by a specific section. Note the
  PRD location.
- **Partially addressed:** The PRD touches on this but incompletely.
  Note what is missing.
- **Not addressed:** The PRD has a genuine gap. This requires either
  a PRD update or an explicit out-of-scope declaration.
- **Out of scope:** The concern is valid but outside this feature's
  boundary. Confirm against the out-of-scope section.
- **Codebase conflict:** The developer identified something in the
  existing codebase that contradicts or complicates the PRD. Flag for
  immediate discussion.

---

## Step 4 — Categorise each concern

Assign each concern to exactly one category:

| Category | Meaning |
|---|---|
| `PRD_UPDATE` | PRD must be updated to address this — missing requirement, missing AC, missing edge/error state, insufficient component spec detail |
| `PHASE_IMPLICATION` | Does not change the PRD but affects how phases should be split — dependency, sequencing, or scope boundary that changes the phase breakdown |
| `CLARIFICATION_NEEDED` | Concern is ambiguous from the transcript — follow-up question required before categorising further |
| `CODEBASE_CONFLICT` | Developer identified a conflict between the PRD and existing codebase behaviour — requires immediate team discussion |
| `ADDRESSED_IN_PRD` | PRD already covers this — point the developer to the specific section |
| `OUT_OF_SCOPE` | Concern is outside this feature's boundary — confirm and note |
| `NO_ACTION` | Concern was resolved in discussion with no PRD change needed — log for record only |

---

## Step 5 — Ask targeted follow-up questions

Present all `CLARIFICATION_NEEDED` items to the team first. These must
be resolved before the concern log can be finalised.

For each clarification needed, ask one targeted question. Reference
the speaker and the specific excerpt to give context:

> "[Speaker] raised a concern about [topic] — specifically: '[excerpt]'.
> Can you clarify: [targeted question]?"

After each answer, re-categorise the concern. If the answer reveals
a PRD gap, move to `PRD_UPDATE`. If it reveals a phase implication,
move to `PHASE_IMPLICATION`. If resolved with no action, move to
`NO_ACTION`.

Then present any `CODEBASE_CONFLICT` items. These are highest priority
— they may affect whether the feature can proceed as specified.

Do not ask about `ADDRESSED_IN_PRD` concerns unless the developer
disputes that the PRD covers it.

Maximum one follow-up per concern. If the answer to a follow-up is
itself ambiguous, flag it as a persistent gap in the concern log
rather than looping.

---

## Step 6 — Produce the concern log

Write `[SESSION_ROOT]/kickoff-dev-review-log.md` using the format
in `references/concern-log-template.md`.

The concern log contains:
- Summary counts by category
- Full list of concerns with: speaker, excerpt, plain-language
  interpretation, category, and resolution/action
- PRD delta notes: exactly what needs to change in the PRD and where
- Phase breakdown implications: exactly what the phase-splitter should
  be aware of when generating the breakdown

---

## Step 7 — Update the PRD in Notion

For each `PRD_UPDATE` concern, apply the required change to the Notion
PRD page via MCP:

- Missing requirement → add to requirements section with REQ-N
  identifier
- Missing AC → add to acceptance criteria for the relevant requirement
- Missing edge/error state → add to the relevant functional area in
  the edge/error states section
- Missing component spec detail → add to the Component Specification
  child page
- Scope boundary gap → add to the out-of-scope section

After all updates are applied, run `prd-completeness-check` silently
against the updated PRD to confirm the score has not dropped. If the
score drops below 80, flag the specific dimension and finding
immediately — do not proceed to phase-splitter until resolved.

If the score holds or improves: confirm to the team.

---

## Step 8 — Brief the phase-splitter

Produce a handoff note for the `phase-splitter` skill covering all
`PHASE_IMPLICATION` concerns. This note is appended to the session
manifest skeleton and read by the phase-splitter as an additional
input alongside the PRD.

Format:

```
KICKOFF DEV REVIEW — PHASE SPLITTER BRIEFING
=============================================
Feature: [feature title]
Date:    [ISO date]

Phase implications identified:

1. [Concern title]
   Raised by: [speaker]
   Implication: [exactly what the phase-splitter should know]
   Suggested handling: [if the team reached a conclusion]

2. ...
```

---

## Step 9 — Confirm and hand off

Tell the team:

> "Dev review complete. [N] concerns processed: [N] PRD updates
> applied, [N] phase implications noted for the phase breakdown,
> [N] no-action items logged.
> [If any persistent gaps:] [N] items remain flagged as gaps in
> the concern log — these need resolution before prd-completeness-
> check is re-run.
> Ready to proceed to phase breakdown."

The call continues directly into the `phase-splitter` step.

---

## What this skill does NOT do

- It does not re-interview the team about the feature from scratch
- It does not ask pre-scripted questions about requirements
- It does not duplicate what prd-completeness-check has already scored
- It does not replace the prd-interviewer — that produces the PRD,
  this refines it from developer perspective
- It does not produce a new PRD — it updates the existing one

---

## Reference files

- `references/concern-log-template.md` — output format for the
  concern log document
