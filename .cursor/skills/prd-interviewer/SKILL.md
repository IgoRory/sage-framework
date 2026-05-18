---
name: prd-interviewer
description: >
  Conducts a structured interview with a Product Owner (Rory or Philip) to
  produce a complete PRD and companion Component Specification, both saved to
  .sage/prds/[FEATURE_ID]/ and structured to pass prd-completeness-check.
  Always starts from a Linear feature issue or ADO work item reference.
  Enforces Step 0 repo preflight (correct branch and up-to-date with remote
  per .sage/workflow-config.json) on the open workspace, appends PRD lifecycle
  telemetry to .sage/prd-interview-telemetry.jsonl, and maps interview progress
  to phase IDs P1–P9. Has read access to the Profitability codebase to ask
  informed questions about existing components, stored procedures, and data
  structures. Use this skill whenever a PM says "lets write a PRD", "help me
  spec this feature", "start a PRD for [feature]", or provides a Linear or ADO
  reference and asks to begin feature documentation. Do not begin writing a PRD
  without running this interview first.
---

# PRD Interviewer

Conducts a structured interview to produce two output artifacts:

1. PRD -- saved to `.sage/prds/[FEATURE_ID]/prd.md`, structured to pass
   prd-completeness-check
2. Component specification -- saved to `.sage/prds/[FEATURE_ID]/component-spec.md`,
   linked explicitly from the PRD

Both artifacts are drafts until the PM runs prd-completeness-check. They are
not submitted to prd-completeness-check automatically -- the PM reviews and
refines them first, then runs the check manually when they believe the PRD
is ready.

The handoff to prd-writer (if used) requires human approval in the format:
APPROVE / REJECT: [reason] / REDIRECT: [direction]

---

## Invocation phrases

Treat this skill as invoked when the PM or agent says any of:
- "Let's write a PRD", "start a PRD", "run the PRD interview", "prd-interviewer"
- "Help me spec this feature", "interview me for the PRD"
- They provide a Linear issue id (`LIN-####`) or ADO work item and want feature documentation

When invoked, **always execute Step 0 (repo preflight) before Step 1**, then continue in order.

---

## Interview phase IDs (P1–P9) — telemetry and traceability

These IDs map interview sections to **`phaseId`** in PRD telemetry and to downstream traceability reviews. Use them when emitting `prd_phase_started` / `prd_phase_completed`.

| phaseId | Interview content |
|---------|-------------------|
| **P1** | Section 1 — Feature and capability definition |
| **P2** | Section 2 — Calculation logic (conditional) |
| **P3** | Section 3 — Allocation methodology (conditional) |
| **P4** | Section 4 — Acceptance criteria |
| **P5** | Section 5a — Scope boundaries |
| **P6** | Section 5b — UI and UX (conditional) |
| **P7** | Section 6 — Edge cases and constraints |
| **P8** | After the interview — parked review, verbatim answer record, APPROVE gate |
| **P9** | PRD / component-spec generation and handoff |

Sections skipped because conditions are false still omit P2/P3/P6 — do not emit phase events for skipped sections.

---

## PRD telemetry (append-only JSONL)

**Enforcement:** Append **one JSON object per line** to the file given by `prd.telemetryFile` in **`.sage/workflow-config.json`** (default: `.sage/prd-interview-telemetry.jsonl` relative to repository root). Create `.sage/` if missing. **Never fail the interview** if a telemetry line cannot be written — log the failure and continue.

**Convention:** Same style as session `workflow-telemetry.jsonl`: UTC ISO `timestamp`, string `event`, optional payloads.

**Required on every line:** `timestamp` (ISO UTC), `event`, `workflowKind` (`"prd_interview"`), `phaseId` (`preflight` \| `P1`–`P9` \| `none`), `linearIssueId` (e.g. `LIN-1234`).

**Correlation:** Generate a **`prdRunId`** (UUID v4) at the **start** of each interview run and reuse it for every event in that run (including multi-chat resumes). Optionally set `sessionId` to the same value as `prdRunId` when no SAGE session exists.

**Preflight optional fields:** `branch`, `headSha`, `originSha`, `commitsBehind`, `commitsAhead`, `workingTreeClean` (boolean), `preflightOutcome` (`pass` \| `fail`).

**MCP optional fields (same as hook telemetry):** `mcpServer`, `mcpTool` when calling Linear MCP.

**Minimal `event` vocabulary:** `prd_preflight`, `prd_phase_started`, `prd_phase_completed`, `prd_parked`, `prd_mcp`, `prd_interview_completed`.

**Implementation:** If the repo script **`prd_telemetry_append.py`** exists at `.cursor/hooks/scripts/`, use it: pass a single JSON object as the first argument (shell-escaped). Otherwise, append one minified JSON object per line to the telemetry file using file tools.

**At each phase boundary:** Emit `prd_phase_started` before the first question of that phase and `prd_phase_completed` after the last question of that phase (or when parking ends that phase). For **P8**, start after Section 6 ends; for **P9**, start when generating drafts.

---

## Step 0 — Connected repo preflight (mandatory)

**Scope:** The **git repository root of the Cursor workspace** where this interview runs (the PM's open repo). Do not assume a path outside the workspace.

**Configuration:** Read **`.sage/workflow-config.json`** at the repo root. Use:

- `prd.requiredInterviewBranch` — branch that must be checked out (e.g. `develop`)
- `prd.remoteName` — remote for fetch/compare (e.g. `origin`)
- `prd.telemetryFile` — JSONL path (default `.sage/prd-interview-telemetry.jsonl`)

**Steps (run via terminal in repo root):**

1. Confirm **`linearIssueId`** with the PM if not already known (Linear `LIN-####` from the ticket driving this PRD).
2. Generate **`prdRunId`** (UUID) for this interview run; store it for all subsequent telemetry events.
3. `git fetch <remoteName>` for the configured remote.
4. Verify **current branch** equals `prd.requiredInterviewBranch` (`git branch --show-current` or equivalent).
5. Verify **not behind** the remote tracking branch: e.g. after fetch, `commitsBehind` = 0 for `HEAD..<remote>/<requiredInterviewBranch>` (no incoming commits you have not merged). Document `commitsAhead` if local is ahead (usually allowed).
6. Optionally note **dirty** working tree (`workingTreeClean`); a dirty tree does **not** automatically fail preflight unless your team policy says otherwise — default is **warn only**.

**Gate:** If branch is wrong or `commitsBehind > 0`, **do not** emit `prd_phase_started` for P1–P9 until resolved. **Stop** after writing `prd_preflight` with `preflightOutcome: fail` and explain what the PM must do (checkout branch, pull/rebase, etc.). **Exception:** If the PM explicitly authorises an override for this run (e.g. hotfix branch), record one line: `preflightOutcome: pass`, `override: true`, `overrideReason: "<verbatim>"` in the telemetry payload and proceed — note the override in the session summary.

**On success:** Append telemetry event **`prd_preflight`** with `preflightOutcome: pass`, `phaseId: preflight`, `linearIssueId`, `prdRunId`, and git summary fields; then proceed to **Before the interview — Step 1**.

---

## Before the interview begins

### Step 1 -- Load the work item

Read the Linear feature issue or ADO work item provided by the PM.
Extract:
- Feature title and description
- Any acceptance criteria or notes already written
- Any linked documents or attachments

If the work item is empty or too vague to begin: tell the PM what
information is needed before the interview can start. Do not proceed
with a blank work item.

### Step 2 -- Silent codebase reconnaissance

Before asking the first question, silently read the codebase to understand
what already exists that is relevant to this feature. This takes 2-3 minutes
and should happen without narrating the process to the PM.

What to read:
- Stored procedures (usp_*) related to the feature area
- Views affected: vw_BI_AllInstruments, Global_Result (for calculation features)
- Existing UI components related to the feature (for UI features)
- Any configuration tables or reference data relevant to the feature
- Test files in the feature area to understand current coverage

What to record internally (do not show to PM yet):
- Which components already exist vs. need to be created
- Which stored procedures will be affected
- Which of the 42 output measures are in scope
- Any existing constraints or edge cases visible in the code
- Any naming inconsistencies relevant to this feature area

This reconnaissance shapes which questions you ask and how specific your
probing can be. A question like "does this affect the FTP calculation for
named revision dates?" is only possible because you read the code first.

### Step 2a -- Classify feature complexity

After reconnaissance, classify the feature's complexity tier using the
classifier in references/complexity-classifier.md. Count the six factors
from the reconnaissance findings and apply the threshold table.

Record the classification tier. It determines the minimum question
thresholds for the main interview and the edge-case phase.

Emit a `prd_complexity_classified` telemetry event with the tier and
factor counts.

### Step 2b -- Context consistency validation

Cross-validate the Linear issue description and any user-provided context
against the codebase reconnaissance findings. Check for:

1. **Scope contradictions** — the Linear issue describes a component or
   feature that does not exist in the codebase, or exists differently than
   described
2. **Missing references** — context documents reference components, SPs,
   or views that do not exist in the codebase
3. **Incomplete context** — the Linear issue mentions N requirements but
   the description only defines fewer than N
4. **Cross-document inconsistencies** — if multiple context sources were
   provided, they disagree on scope or behaviour

For each issue found, generate a **priority interview question** that will
be asked at the start of Section 1. Priority questions are asked before
category-based questions.

If no issues are found, note "Context consistency: no issues" and proceed.

### Step 3 -- Set expectations

Tell the PM:
- What you found in the codebase (brief summary -- 3-4 sentences)
- The feature's complexity tier and what it means for interview depth
  (e.g., "This is a Tier 3 feature — I will ask at least 32 questions
  across the main interview and edge-case phase")
- Any context consistency issues found (priority interview questions)
- How the interview is structured (sections, conditional sections)
- That you will park unanswered questions and flag them clearly
- Approximately how long it will take (typically 20-40 minutes)
- That the output will be a Notion PRD draft for their review

---

## Interview structure

The interview has six sections. Sections 1, 4, 5a, and 6 are always asked.
Sections 2, 3, and 5b are conditional.

**Telemetry:** Before starting Section 1, emit **`prd_phase_started`** with `phaseId: P1`. After finishing Section 1, emit **`prd_phase_completed`** with `phaseId: P1`. Repeat for each section with its **P2–P7** mapping from the table above (emit started/completed only for sections you actually run).

Ask questions one at a time. Wait for the answer before proceeding.
Do not present a list of questions -- this is a conversation, not a form.

If an answer is vague, probe once with a specific example from the codebase
before accepting it. Example: if the PM says "it should handle the standard
FTP calculation", ask "do you mean the existing usp_CalculateFTP logic, or
is there a change to how named revision dates are applied?"

If the PM cannot answer a question: park it using the pattern below and move on.

### Park-it pattern

When parking a question:
"I will note that [question topic] is unresolved and flag it as a gap in
the PRD draft. You can fill it in before running the completeness check."

Record the parked question by question ID (e.g. Q2.3 -- parked). Parked
questions appear as explicit TODO items in the PRD draft.

---

## Section 1 -- Feature and capability definition (always ask)

Q1.1 -- What is the name of this feature as it should appear in the PRD?

Q1.2 -- In one or two sentences, what does this feature do for the user?
(Probe if vague: who is the user, and what can they do after this feature
exists that they cannot do today?)

Q1.3 -- Which of the following best describes the primary change this
feature makes? (Select all that apply)
  a) New user-facing screen or UI change
  b) Change to how calculations are performed
  c) Change to how costs or income are allocated
  d) Change to reporting or BI output
  e) Configuration or administration change
  f) Data model or schema change

Q1.4 -- Which area of the Profitability product does this feature primarily
affect? (Reference your codebase recon to offer specific options relevant
to this feature.)

Q1.5 -- Which user roles will interact with this feature?

Q1.6 -- Is there a deadline or regulatory driver for this feature?

---

## Section 2 -- Calculation logic changes (ask if Q1.3 includes b)

Q2.1 -- Which specific measures in the output set does this change affect?
(Reference the 42-measure set. If the PM is unsure, read them the relevant
measure names from vw_BI_AllInstruments and ask them to confirm.)

Q2.2 -- Which stored procedures will this change touch?
(From your recon, name the specific procedures you identified. Ask the PM
to confirm or correct.)

Q2.3 -- What is the current behaviour, and what should the new behaviour be?
(Require a specific before/after -- not "it should work correctly".)

Q2.4 -- Does this change affect FTP calculations? If yes:
  a) Does it affect named revision dates? If so, which ones?
  b) Does it affect the rate source (which rate table is used)?
  c) Does it affect which instrument types are in scope?

Q2.5 -- Does this change affect how return codes -1 through -8 are handled?
If yes, which codes and what should the new behaviour be?

Q2.6 -- Does this change affect any of the instrument flags?
(NewInstFlag, ClosedInstFlag, PlugInstrumentFlag)
If yes, how?

Q2.7 -- What are the expected outputs for the happy path?
(Require specific measure values or conditions -- not "correct results".)

Q2.8 -- Are there any instrument types or portfolio segments that should
be excluded from this calculation change?

---

## Section 3 -- Allocation methodology changes (ask if Q1.3 includes c)

Q3.1 -- Which allocation type does this change affect?
(Expense allocation, income allocation, capital allocation, provisions,
or a combination?)

Q3.2 -- What is the current allocation methodology, and what should it
be after this change?
(Require a specific description -- not "the standard methodology".)

Q3.3 -- Which cost pools or income streams are affected?

Q3.4 -- What is the allocation driver? (What determines how much each
instrument or entity receives?)

Q3.5 -- Does this change affect the GLAllocationLog? If yes, what
changes to the log schema or content are required?

Q3.6 -- Are there any instruments, entities, or periods that should be
excluded from this allocation change?

Q3.7 -- What are the expected allocation outputs for a representative
test case? (Ask for specific numbers or ratios if possible.)

---

## Section 4 -- Acceptance criteria (always ask)

Q4.1 -- What does success look like for this feature? Describe 2-3
specific scenarios where you would say "this is working correctly."
(For each scenario, probe: what is the input, what is the action, what
is the exact expected output?)

Q4.2 -- How will you verify this feature is working in UAT?
What specific data or steps will you use?

Q4.3 -- Are there any performance requirements?
(e.g., "the calculation must complete within 30 seconds for a portfolio
of 10,000 instruments")

Q4.4 -- Are there any existing tests that this feature must not break?
(From your codebase recon, name the test files in the area and ask the
PM to confirm which test suites are in scope.)

---

## Section 5a -- Scope boundaries (always ask)

Q5a.1 -- What is explicitly out of scope for this feature?
(Prompt with adjacent areas from your codebase recon: "Is [adjacent feature]
in scope or out of scope?")

Q5a.2 -- Is there anything that looks related to this feature but should
NOT be changed as part of this work?

Q5a.3 -- Are there any downstream systems or consumers of this data that
must not be affected? (e.g., specific BI reports, Dataverse entities,
external exports)

Q5a.4 -- Does this feature touch the Dataverse boundary?
If yes: which Dataverse entities are read or written, and is any new
write permission required?

---

## Section 5b -- UI and UX (ask if Q1.3 includes a, or if codebase recon
## identified UI files in scope)

Q5b.1 -- Which screens or pages does this feature add or change?
List each one.

Q5b.2 -- For each screen: is it a new screen or a modification to an
existing one?

Q5b.3 -- For each new or modified screen: what is its purpose in one
sentence?

Q5b.4 -- What triggers navigation to this screen?
(A menu item, a button on another screen, a URL, etc.)

Q5b.5 -- For each new or modified UI component on each affected screen:
  a) What is the component name and type?
     (e.g., "ProcessSelector -- multi-select dropdown")
  b) What does it do? (functional description, not visual description)
  c) What data does it display or capture?
     (Name the specific field -- Adjusted_GL, ProcessID, SP, etc.)

Q5b.6 -- For each component: what are all the states it can be in?
(e.g., default, loading, selected, error, disabled, empty)
What causes each transition?

Q5b.7 -- What does the empty state look like for each data-displaying
component? (What message or visual is shown when there is no data?)

Q5b.8 -- What happens when an operation fails?
(Describe the error state for each component that can fail.)

Q5b.9 -- What happens while data is loading?
(Describe the loading state for each component that fetches data.)

Q5b.10 -- Are there any user interactions beyond the standard ones?
(e.g., drag-and-drop, inline editing, bulk selection, keyboard shortcuts)

Q5b.11 -- Do you have any existing sketches, mockups, or visual references
for how this should look? If yes, describe what each one shows in words.
Do not share files or links -- describe it verbally. The
plan-preview-generator agent will produce visual confirmation artifacts
from the completed PRD during S4.

---

## Section 6 -- Edge-case phase (always ask)

This is a dedicated interview phase, not a single section. It systematically
covers seven edge-case categories. The minimum number of questions is set
by the feature's complexity tier (see references/complexity-classifier.md).

Ask questions grounded in the codebase reconnaissance findings. For each
category, reference specific components, stored procedures, or data
structures found during recon.

### Telemetry

Emit `prd_phase_started` with `phaseId: P7` (Edge-case phase start) before
the first edge-case question. Emit `prd_phase_completed` with `phaseId: P7`
after the conclusion gate completes.

### EC Category 1 -- Interaction sequence

What happens when a user performs action A then action B? What happens when
actions overlap? What happens when the user navigates away during an
operation? What happens on browser refresh?

Ask about every pair of user actions identified in Sections 1-5b that could
interact.

### EC Category 2 -- Cascading behaviour

For every entity that can be modified or deleted: what happens to other
entities that reference it? Do downstream displays auto-update? What about
derived names or calculated values?

Ask about every entity identified in the codebase recon that this feature
modifies.

### EC Category 3 -- Concurrency

What happens when two users perform the same action simultaneously? What
happens when a background process (calculation, allocation) is running
while a user modifies source data?

Ask about every action that modifies shared state.

### EC Category 4 -- State boundary

What does every action button do when there are zero items? Is there a
maximum number of items? What happens at state transitions? Are there
invalid state combinations?

Ask about every component's empty state, maximum capacity, and transition
states.

### EC Category 5 -- Cross-component dependency

What happens to downstream components when this feature's data changes?
What happens to this feature when upstream data is incomplete? Are there
circular dependencies?

Ask about every dependency relationship identified in the codebase recon.

### EC Category 6 -- Data integrity

What about records that exist before this feature? Is partial data entry
allowed? What happens with bulk operations where some items succeed and
others fail? Can actions be undone?

Ask about every data entity this feature creates or modifies.

### EC Category 7 -- Failure and recovery

For every operation that can fail: what does the user see? Is their work
preserved? Can they retry? What is the recovery path?

Ask about every operation identified in the interview that involves a
stored procedure call, API request, or data write.

### Edge-case phase conclusion gate

Before concluding the edge-case phase, verify that all seven edge-case
categories have been addressed (at least one question asked and answered
per applicable category). Present the coverage summary to the PM. The PM
must explicitly confirm coverage is sufficient before proceeding to P8.

---

## After the interview

Before **P8** telemetry: ensure **`prd_phase_completed`** has been written for **P7** (Section 6). Emit **`prd_phase_started`** with `phaseId: P8` before reviewing parked questions; **`prd_phase_completed`** for P8 after the PM responds to the APPROVE / REJECT / REDIRECT prompt (or when stopping).

### Step 1 -- Post-interview verification protocol

Before reviewing parked questions, execute this protocol:

1. **Present structured summary** — present everything captured during
   the interview, organised by section. For the edge-case phase, organise
   by the seven categories.

2. **Flag vague answers** — list every answer that was short, unclear, or
   accepted without a specific example. Ask the PM if they can elaborate
   on any of these now.

3. **Open-ended coverage check** — ask: "Is there anything about this
   feature that concerns you — anything you are worried we have not
   covered?"

4. **Confirm minimum question count** — state the complexity tier, the
   minimum threshold, and the actual count. If the count is below
   threshold, explain which categories are under-covered and ask
   additional questions before concluding.

5. **Review parked questions** — present all parked questions. Ask if any
   can be answered now. For those that remain parked, confirm they will
   appear as TODO items in the PRD draft.

6. **Explicit confirmation** — only after steps 1–5: ask the PM to
   confirm with APPROVE / REJECT / REDIRECT.

### Step 2 -- Write the answer record

Write a structured JSON answer record to:
`.sage/prds/[FEATURE_ID]/interview-answers.json`

Create the `.sage/prds/[FEATURE_ID]/` directory if it does not exist.
The record must use question IDs as keys (Q1.1, Q2.3, etc.) with verbatim
answers as values. Parked questions are recorded as null with a "parked": true
flag.

Do not summarize or interpret answers -- record verbatim.

### Step 3 -- Present for human review

Tell the PM:
"The interview is complete. Here is a summary of what was captured:"

Print a plain-language summary (not the raw JSON) covering:
- Feature title and primary change type
- Measures/procedures in scope (if applicable)
- Acceptance criteria captured (count and brief description)
- UI screens and components in scope (if applicable)
- Parked questions (list by topic)
- Anything flagged as a constraint or edge case

Then say:
"Please review this summary. When you are satisfied it accurately reflects
your intent, respond with:
  APPROVE -- to proceed to PRD draft generation
  REJECT: [reason] -- to restart or revise specific answers
  REDIRECT: [direction] -- to continue the interview in a different direction"

Do not proceed to PRD generation without an explicit APPROVE.

### Step 4 -- Generate the PRD draft (on APPROVE)

Emit **`prd_phase_started`** with `phaseId: P9` before draft generation. After files are written, emit **`prd_phase_completed`** with `phaseId: P9`, then **`prd_interview_completed`** with summary fields (e.g. `parkedCount`, `linearIssueId`, `prdRunId`).

Generate the PRD draft from the answer record using the PRD template
in references/prd-template.md.

Write the PRD to: `.sage/prds/[FEATURE_ID]/prd.md`

For every UI component identified in Section 5b: create a Component
Specification entry. Write the component specification to:
`.sage/prds/[FEATURE_ID]/component-spec.md`

Link the component spec from the PRD with a relative path reference.

### Step 5 -- Confirm and hand off

Tell the PM:
"PRD and component specification have been written to:
- `.sage/prds/[FEATURE_ID]/prd.md`
- `.sage/prds/[FEATURE_ID]/component-spec.md`

Review both documents. When you are satisfied, run prd-completeness-check
against the PRD to assess readiness for the planning cycle."

---

## Constraints

- Always complete **Step 0 repo preflight** (or documented PM override) before **Section 1 / P1**
- Append PRD telemetry for **`prd_preflight`**, phase boundaries (**`prd_phase_started` / `prd_phase_completed`** for P1–P9 as applicable), and **`prd_interview_completed`** when the interview ends (after summary or when stopping without draft)
- Always start from a Linear or ADO work item -- do not begin without one (after preflight)
- Always conduct codebase recon before the first question
- Ask questions one at a time -- never present a list
- Record answers verbatim -- never summarize or interpret during interview
- Never generate the PRD without an explicit APPROVE from the PM
- Never accept file attachments or external links for visual references (Q5b.11)
- Never skip Section 6 -- edge cases are always asked regardless of feature type
- Parked questions must appear as explicit TODO items in the PRD draft,
  not be silently omitted
- All user-facing message text in the PRD draft (toast messages, error
  messages, tooltip text, dialog text, validation messages) must follow the
  three-tier message text sourcing protocol:
  1. **Codebase-sourced** — quote verbatim with
     `[Source: path/to/file.ext:lineN]`.
  2. **Agent-proposed** — when no codebase text exists, propose text
     grounded in existing codebase patterns and present it to the PM with
     two options: (a) Approve proposed text, (b) PM provides their own
     text. Mark approved proposals as `[Proposed — approved by PM]` and
     PM-provided text as `[PM-provided]`. Present each proposal
     individually during the interview — not as a batch.
  3. **Undetermined** — when no reasonable proposal can be constructed,
     mark as `[TEXT TBD — requires PM decision]` with a note explaining
     what kind of text is needed.
  Never silently invent user-facing message text. Every message text
  instance in the PRD draft must carry one of the three markers.
- Step 2 (codebase reconnaissance) must produce a structured investigation
  manifest listing every file read, grouped by layer (frontend components,
  services, models/interfaces, stored procedures, views, tests), with a
  one-line summary per file. The manifest is emitted as a
  `prd_investigation_manifest` telemetry event and presented to the PM at
  Step 3.

---

## Reference files

Read references/question-sets.md for:
- The complete question set with probing guidance and Profitability-specific
  examples for each question

Read references/prd-template.md for:
- The PRD structure the output must follow
- Section-by-section instructions for the PRD draft generation step

