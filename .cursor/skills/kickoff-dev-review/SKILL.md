---
name: kickoff-dev-review
description: >
  Processes a Teams meeting transcript from the kick-off session developer
  review discussion. Reads the transcript alongside the PRD and component
  specification, identifies and categorises all developer concerns, asks
  targeted follow-up questions for anything unresolved, then updates the
  PRD at .sage/prds/[FEATURE_ID]/prd.md and produces a concern log and
  phase-splitter briefing note. Use this skill during Step 1 of the Sprint
  or Mob kick-off session immediately after the Teams recording is stopped.
  The team remains on the call to answer follow-up questions in real time.
  Always runs before phase-splitter in the kick-off sequence.
---

# Kickoff Dev Review

Captures and structures developer concerns about a PRD during the
kick-off session. The team discusses the PRD verbally on a Teams call.
When the recording stops, this skill processes the transcript, categorises
every concern, asks targeted follow-ups, and updates the PRD at
`.sage/prds/[FEATURE_ID]/prd.md` for any confirmed gaps.

---

## Inputs required

| Input | Source | Required |
|-------|--------|----------|
| Teams meeting link | Provided by invoker | Yes |
| PRD | `.sage/prds/[FEATURE_ID]/prd.md` | Yes |
| Component specification | `.sage/prds/[FEATURE_ID]/component-spec.md` | Yes (UI features) |

---

## Kick-off sequence

Sprint kick-off Step 1 (~35 min total):
1. Team discusses PRD on Teams call (~20 min)
2. Recording stopped -- transcript available (team stays on call)
3. Skill invoked with meeting link
4. Transcript fetched via Microsoft 365 MCP (~1 min)
5. Skill processes transcript against PRD (~2-3 min)
6. Categorised concerns + follow-up questions surfaced (~10 min with team)
7. PRD updated at `.sage/prds/[FEATURE_ID]/prd.md` for confirmed gaps
8. prd-completeness-check re-run silently against updated PRD
9. Concern log and phase-splitter briefing note produced
10. Hand off to phase-splitter (Step 2)

---

## Step 1 -- Fetch transcript

Use the Microsoft 365 MCP to fetch the transcript from the provided
Teams meeting link.

If the transcript is not yet available (recording still processing):
tell the invoker and pause. Do not proceed without the transcript.

---

## Step 2 -- Read context

Read the PRD from `.sage/prds/[FEATURE_ID]/prd.md` and the component
specification from `.sage/prds/[FEATURE_ID]/component-spec.md`.
Read both documents completely before processing the transcript.

---

## Step 3 -- Process transcript

Read the full transcript. For each distinct concern, question, or
observation raised by a developer:

1. Extract the verbatim quote (or close paraphrase if transcript is
   imperfect)
2. Assign a concern category (see below)
3. Identify whether a follow-up question is needed
4. Note which PRD section (if any) the concern relates to

Process every concern -- do not filter or dismiss any at this stage.

### Seven concern categories

PRD_UPDATE:
  A genuine gap in the PRD that must be fixed before planning.
  The PRD does not cover this scenario, state, or requirement.
  Action: draft a PRD update, confirm with team, apply to `.sage/prds/[FEATURE_ID]/prd.md`.

PHASE_IMPLICATION:
  Does not affect PRD content but affects how the feature should
  be split into phases. For example: a dependency the phase-splitter
  should know about, or a file that is more complex than it appears.
  Action: note in phase-splitter briefing. No PRD change.

CODEBASE_CONFLICT:
  A contradiction between the PRD and the existing codebase.
  Highest priority -- these block implementation if unresolved.
  Action: surface immediately, resolve with team on call.

CLARIFICATION_NEEDED:
  The concern is ambiguous from the transcript -- unclear whether
  it is a PRD gap, a phase implication, or already covered.
  Action: ask a targeted follow-up question, then re-categorise.

ADDRESSED_IN_PRD:
  The PRD already covers this concern. The developer may not have
  seen the relevant section.
  Action: point developer to the specific PRD section. Log as closed.

OUT_OF_SCOPE:
  The concern is valid but outside this feature's boundary.
  Action: confirm with team that it is out of scope. Log.

NO_ACTION:
  Resolved in discussion. No PRD change and no phase implication.
  Action: log only.

---

## Step 4 -- Ask follow-up questions

For each concern categorised as CLARIFICATION_NEEDED:
Ask one targeted question to resolve the ambiguity. Wait for the
answer before proceeding to the next question.

For each CODEBASE_CONFLICT:
Ask the developer to describe the specific conflict. Confirm whether
a PRD update, a codebase decision, or both is needed.

Do not ask more than one follow-up per concern at a time.
Do not ask follow-ups for concerns already categorised as
ADDRESSED_IN_PRD, OUT_OF_SCOPE, or NO_ACTION.

---

## Step 5 -- Apply PRD updates

For each confirmed PRD_UPDATE:
1. Draft the specific change (new requirement, amended AC, added
   edge case, new state, etc.)
2. Present the draft to the team for confirmation
3. Only after confirmation: apply the update to `.sage/prds/[FEATURE_ID]/prd.md`
4. Record what was changed

Do not update the PRD without team confirmation. Do not batch-apply
multiple updates -- confirm each one separately.

---

## Step 6 -- Re-run prd-completeness-check

After all PRD updates are applied, silently re-run prd-completeness-check.

If the score remains >= threshold: note in the concern log.
If the score drops below threshold (an update introduced a new gap):
surface the specific new finding immediately. Do not hand off to
phase-splitter until the new gap is resolved.

---

## Step 7 -- Produce outputs

Write the concern log to [SESSION_ROOT]/kickoff-dev-review-log.md using
the template in references/concern-log-template.md.

Write the phase-splitter briefing to [SESSION_ROOT]/phase-splitter-briefing.md:

``````markdown
# Phase Splitter Briefing -- [Feature title]

Generated by: kickoff-dev-review
Date: [ISO date]

## Concerns with phase implications

[List each PHASE_IMPLICATION concern with the specific implication
for phase splitting -- e.g., "The GL reconciliation stored procedure
is called by three other processes -- the phase touching it must be
Foundation type."]

## Codebase conflicts resolved

[List each CODEBASE_CONFLICT and how it was resolved]

## PRD updates applied

[List each change made to the PRD during this session]

## Updated PRD completeness score

[Score]/100 -- [PASS / FAIL]
``````

---

## Constraints

- Fetch transcript via Microsoft 365 MCP -- do not ask the developer
  to paste transcript text
- Do not update the PRD without explicit team confirmation
  for each change
- Do not hand off to phase-splitter if prd-completeness-check
  drops below threshold after PRD updates
- Operates only on the current session's transcript -- never reads
  prior session transcripts
- If the Teams transcript is unavailable: pause and wait -- do not
  attempt to conduct the review from memory or notes

---

## Reference files

Read references/concern-log-template.md for the output format for
the concern log document.

