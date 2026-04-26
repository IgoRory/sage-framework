# Interview Question Sets — P1 through P9

Full question sets for each phase of the PRD interview. Read the relevant
section before beginning each phase. Questions marked `[CODEBASE]` should
be pre-answered or pre-informed by the codebase reconnaissance in Step 2
of the setup — use your findings to ask a more specific version.

Questions marked `[COMPONENT]` repeat per component during P5.

---

## P1 — Feature overview

Purpose: Understand why this feature exists before defining what it does.
This anchors every subsequent decision.

1. In one or two sentences, what is the core problem this feature solves
   for the user?

2. Who specifically benefits — which user roles, which client types, or
   which workflows does this improve?

3. What is the expected business outcome? (e.g. reduces manual effort,
   eliminates a workaround, unlocks a client use case)

4. Is this feature driven by a specific client request, an internal
   product decision, or a regulatory/compliance need?
   - If client-driven: which client(s), and is it expected to benefit
     others in the portfolio?
   - If compliance-driven: what is the requirement and what is the
     deadline?

5. Is there a related feature already in the product that this extends,
   replaces, or depends on?
   `[CODEBASE]` If reconnaissance found a related feature: "I can see
   [X] in the codebase — is this an extension of that, or separate?"

6. Is there a target release or deadline for this feature?

---

## P2 — Functional scope

Purpose: Define what the feature does at the right level of abstraction
before diving into screens and components.

1. Walk me through what a user does with this feature, step by step,
   from the moment they arrive at the relevant page to the moment they're
   done. Don't worry about UI details yet — just the flow.

2. Are there multiple user flows (e.g. a setup flow and a day-to-day
   usage flow, or an admin flow and a standard user flow)?
   If yes: walk through each one.

3. What does the feature produce or change? (e.g. saves a record,
   updates a calculation, generates a report, triggers a background
   process)

4. Are there any calculations involved?
   If yes:
   - What is being calculated?
   - What are the inputs?
   - Where does the result go — displayed to the user, stored to a
     table, both?
   `[CODEBASE]` If a relevant stored procedure was found: "I can see
   `usp_[name]` which looks related — is this feature using, modifying,
   or replacing that?"

5. Does this feature change how any existing data is processed or stored?
   If yes: which tables or fields are affected, and how?

6. Are there any background processes involved — things that run without
   direct user action (scheduled jobs, triggered recalculations, async
   operations)?

7. What permissions or roles are relevant? Who can do what?

---

## P3 — Affected pages and screens

Purpose: Establish the complete inventory of pages and screens that
change, so nothing is missed in the component and mockup phases.

`[CODEBASE]` Before asking, review the codebase for existing page/view
files related to the feature. Pre-populate a candidate list and confirm
rather than asking cold.

1. Which existing pages in the Profitability application are affected
   by this feature?
   For each page: is it being modified, or is the user navigating to it
   as part of the new flow without any changes?

2. Are any new pages being added?
   If yes: describe each one — what is its purpose and how does the user
   get to it?

3. Are any modal dialogs, drawers, panels, or overlays involved — new
   or modified?

4. Is there a navigation change — any new menu items, links, or
   redirects being added?

5. For each affected page, is the change:
   - Additive only (new components added, nothing existing changes)
   - Modifying existing components (existing components behave differently)
   - Both

6. Confirm the complete screen inventory:
   > "Based on what you've described, the affected screens are:
   > [list]. Is anything missing?"

---

## P4 — Component inventory

Purpose: Identify every new and affected UI component on every affected
page before going into specification detail. Completeness here determines
the scope of P5.

`[CODEBASE]` Before asking, identify existing components in the relevant
page files. Pre-populate a candidate list of components the PM may not
think to mention.

For each affected page identified in P3, ask:

1. What new components are being added to this page?
   For each: what type is it? (dropdown, table, form, button, modal, etc.)

2. What existing components on this page are changing?
   `[CODEBASE]` "I can see the following components on this page:
   [list]. Which of these are affected?"
   For each affected component: what specifically is changing about it?

3. Is any component on this page being removed?
   If yes: what replaces it, if anything?

4. For each new component — is it similar or identical to a component
   that already exists elsewhere in the product?
   `[CODEBASE]` "I can see a [component type] on [other page] — is this
   the same component being reused, or a new one?"
   If reused: what differs from the existing component?
   If new: confirm it needs a full specification from scratch.

5. Are there any components that are shared across multiple pages that
   will be affected by this change?
   `[CODEBASE]` Flag any shared components identified in reconnaissance.
   "This component appears on [N] pages — is the change applying to all
   instances or only this page?"

6. Confirm the component inventory:
   > "The components I have for [page name] are: [list — new/affected/
   > reused for each]. Is anything missing?"

Repeat for every affected page before moving to P5.

---

## P5 — Component specification

Purpose: Capture the complete specification for every component in the
inventory. This is the most detailed phase — take one component at a time.

For each component in the P4 inventory, work through all six elements.
If a component is marked as reused with no differences, confirm once and
move on. If it has differences, specify only the delta.

**[COMPONENT] Element 1 — Name and type**

Already captured in P4. Confirm:
- "I have this as [name] — [type]. Is that right?"

**[COMPONENT] Element 2 — Functional description**

1. In one sentence, what does this component do — not what it looks like,
   but what it does?
   Follow-up if visual: "That describes the appearance. What does
   interacting with it cause to happen?"

2. Does interacting with this component immediately affect anything else
   on the page — another component's state, a visible calculation, a
   filter applied to a table?

**[COMPONENT] Element 3 — States**

1. Walk me through every state this component can be in.
   After their answer, check against the minimum state list for this
   component type (see `prd-completeness-check/references/scoring-rubric.md`
   → D5 minimum state table) and ask about any missing states:
   "What about [missing state] — can this component be in that state?"

2. For each state: what causes the component to enter that state?
   (user action, data condition, system event, role/permission)

3. Are there any states that are deliberately not applicable for this
   component? If yes, why?
   (This prevents a D5 deduction for intentionally omitted states.)

**[COMPONENT] Element 4 — User interaction options**

1. What can a user do with this component?
   For each interaction: what is the action, what element do they
   interact with, and what happens as a result?

2. Are there any interactions that are only available in certain states
   or for certain roles?

3. Are there any keyboard interactions (tab focus, enter to submit,
   escape to close) that need to be specified?

**[COMPONENT] Element 5 — Selectable options (if applicable)**

Ask only if the component type can present choices (dropdown, multi-select,
radio group, tab set, etc.).

1. What are the options available in this component?

2. Are the options static (hardcoded) or dynamic (loaded from an API
   or stored procedure)?
   If dynamic: which endpoint or stored procedure provides them?

3. Is there a default selection? What is it?

4. Are there any conditions under which certain options are hidden,
   disabled, or grouped differently?

5. Is there a maximum number of selectable items (for multi-select)?

**[COMPONENT] Element 6 — Data binding**

1. What data does this component display or operate on?

2. Where does that data come from specifically?
   Follow-up if vague: "Which stored procedure, view, or Adjusted_GL
   field provides this data?"
   `[CODEBASE]` "I can see `usp_[name]` / `vw_[name]` in the codebase
   — is this component reading from that?"

3. Does this component write data anywhere?
   If yes: where — which table, field, or stored procedure?

4. Does this component's data depend on another component's state
   (e.g. a table that re-queries when a filter changes)?
   If yes: which component and what state change triggers the re-query?

5. Is there a ProcessID or GL code involved in how this data is
   filtered, categorised, or stored?

---

## P6 — Edge / empty / error states

Purpose: Define non-happy-path behaviour at the functional-area level.
Component-level states were covered in P5. P6 covers what happens to
the feature as a whole.

For each functional area identified in P2:

1. What does the user see if there is no data to display?
   (Empty state — message text, any available actions)

2. What happens if the operation fails?
   - API or stored procedure returns an error
   - Network timeout
   - Data integrity error (e.g. ProcessID not found, GL code invalid)
   For each: what does the user see, and can they retry?

3. Are there boundary conditions on any inputs?
   - Numeric fields: what are the min and max values, and what happens
     at and beyond those limits?
   - Text fields: are there character limits?
   - Percentage or weight fields: what happens if inputs don't sum to
     the expected total?
   - Date fields: are there valid date ranges?

4. What does a user without the required role or permission see?
   - Is the page hidden entirely, or is it visible with controls
     disabled or absent?
   - Is there an explanatory message?

5. If the feature involves a background process or async operation:
   - What does the user see while it's running?
   - What happens if it fails partway through?
   - Is there a way to cancel it?

---

## P7 — Acceptance criteria

Purpose: Define testable, pass/fail outcomes for every functional
requirement surfaced in P2.

1. For each requirement identified in P2, ask:
   "How would you know this requirement has been met? What would you
   test?"

   After their answer, check:
   - Is it testable without human interpretation?
   - Is there a specific value, threshold, or state condition?
   - If not, ask: "Can you give me a specific threshold or condition?
     For example, 'saves within [N] seconds' or 'returns [HTTP code]
     when [condition]'."

2. For any calculation requirements:
   "What is the expected output for a known set of inputs? Walk me
   through a specific example."
   (This becomes the basis for a test case in the TDD spec.)

3. For any permission requirements:
   "Which role should be able to do this, and which role should not?
   What exactly do they see differently?"

4. For any performance requirements:
   "What is the acceptable response time, and at what data volume?"

---

## P8 — Out-of-scope boundaries

Purpose: Define what this feature explicitly does not do. This prevents
agents from implementing adjacent behaviour and sets clear handoff points.

1. Are there any related features or capabilities that someone might
   reasonably expect this feature to include, but that are deliberately
   excluded?

2. Does this feature touch any shared data structures (Adjusted_GL,
   GLAllocationLog, any stored procedure used by other features)?
   If yes: what specifically does this feature read, and what does it
   write? What does it explicitly not touch?

3. Does this feature affect the Pyramid Analytics data model or IMDB?
   If no: confirm that Pyramid model updates are out of scope and add
   explicitly.

4. If the feature modifies an existing component that is shared across
   multiple pages: does the change apply to all instances or only this
   page? If only this page, the other instances must be called out as
   out of scope.

5. Are there any future enhancements that are intentionally deferred
   from this version? Name them explicitly so agents don't implement
   them speculatively.

6. Are there any integrations, exports, notifications, or audit trail
   requirements that are not in scope for this version?

---

## P9 — Mockup confirmation

Purpose: Confirm what mockup files will be created and what they must
show, so the screen inventory is complete and the D4 check will pass.

1. For each screen in the inventory, confirm that an interactive HTML
   mockup will be created.
   "I have [N] screens in the inventory. Will there be a mockup for
   each? Are there any that won't have one?"

2. For each mockup, confirm:
   - The file name and repo path it will be committed to
     (this becomes the path in the screen inventory)
   - Whether it will show the happy-path state only, or also edge/
     empty/error states

3. Are there any screens where the mockup already exists and is being
   reused or only slightly modified?
   If yes: confirm whether the existing file will be updated in place
   or a new file created.

4. Remind the PM:
   > "The mockup files need to be committed to the repo at the paths
   > we've agreed before `prd-completeness-check` is run — the check
   > verifies file existence at those paths. The mockup shows what the
   > UI looks like; the Component Specification defines what it does.
   > Both are required."

5. Confirm the final screen inventory:
   > "The screen inventory is: [list with paths]. Is this complete and
   > accurate?"
