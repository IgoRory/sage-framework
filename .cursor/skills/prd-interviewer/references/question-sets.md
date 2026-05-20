# Question Sets -- Adaptive Category Catalogue

Reference for prd-interviewer. Questions are organised into **categories**
with **example questions** per section. These are starting points -- generate
as many questions as needed within each category to fully cover the feature.
Do not stop at the canonical set. Expand, adapt, and add questions based on
what the codebase reconnaissance revealed.

---

## How to use this reference

1. Use the canonical Q-IDs (Q1.1, Q2.3, etc.) as the baseline question set
2. Within each category, generate additional questions grounded in recon
   findings -- assign IDs as Q[section].DYN-1, Q[section].DYN-2, etc.
3. When a PM gives a vague answer, probe once using the example language
4. If the second answer is still insufficient, defer the question and move on
5. Track questions asked per category to ensure coverage

---

## Section 1 -- Feature and capability definition

### Category: Feature Identity

**Canonical questions:** Q1.1, Q1.2

**Q1.1** -- What is the name of this feature as it should appear in the PRD?

Probing: if the PM gives a name that is too generic ("FTP update", "allocation
fix"), ask: "Is there a more specific name that distinguishes this from other
FTP or allocation work that has been done before?"

**Q1.2** -- In one or two sentences, what does this feature do for the user?

Vague answer: "It improves the FTP calculation."
Probe: "Can you describe what a user will be able to do or see after this
feature exists that they cannot do today? For example, will they see a new
measure in the output, will the calculation run in a different way, or will
they have a new screen to interact with?"

Vague answer: "It fixes an issue with allocations."
Probe: "When you say 'fixes', do you mean the calculation is producing an
incorrect result today and this brings it into line with the expected
methodology -- or is this a new allocation type being added?"

**Expand as needed:** If the feature description is complex or touches
multiple areas, generate follow-up questions to disambiguate scope (e.g.,
"You mentioned both X and Y -- are both part of this feature, or is Y a
separate future piece of work?").

### Category: Change Classification

**Canonical questions:** Q1.3, Q1.4

**Q1.3** -- Which of the following best describes the primary change?

If the PM selects multiple types: "Which of these is the primary driver --
the others will shape the scope boundaries, but knowing the primary helps
us structure the interview."

**Q1.4** -- Which area of the product does this primarily affect?

Use your codebase recon to offer specific options:
"Based on the codebase, this feature appears to relate to [area you found].
Is that right, or does it also touch [other area you identified]?"

**Expand as needed:** If recon revealed multiple affected areas, ask about
each explicitly to confirm scope boundaries early.

### Category: User Roles and Urgency

**Canonical questions:** Q1.5, Q1.6

**Q1.5** -- Which user roles will interact with this feature?

**Q1.6** -- Is there a deadline or regulatory driver for this feature?

**Expand as needed:** If multiple roles are identified, ask about
permission differences per role. If a deadline exists, ask about phasing
priorities.

---

## Section 2 -- Calculation logic changes

### Category: Measure Scope

**Canonical questions:** Q2.1

**Q2.1** -- Which specific measures in the output set does this change affect?

If the PM is unsure which measures are affected, read them the relevant
subset from the 42-measure output set and ask them to confirm:
"From the output set, the measures most likely affected by an FTP change
are FTP_GrossInterestIncome, FTP_FundingCost, FTP_NetInterestIncome,
FTP_Rate, and FTP_Volume. Does this match your understanding, or are there
others?"

If the PM says "all measures": "Do you mean literally all 42 measures will
change, or that the measures in the FTP group will change and downstream
roll-ups will reflect that?"

**Expand as needed:** For each affected measure, ask whether the change is
to the calculation formula, the input data, or both. Generate questions
for any measure with complex dependencies discovered in recon.

### Category: SP Impact

**Canonical questions:** Q2.2

**Q2.2** -- Which stored procedures will this change touch?

From your recon, name the procedures you found:
"I can see that usp_CalculateFTP and usp_ApplyRevisionDate are the primary
procedures in this area. Are those the ones in scope, or are there others
you know of?"

**Expand as needed:** For each SP identified in recon, ask whether it is
read-only consumed or requires modification. Ask about SP dependencies
(SP A calls SP B -- does the change cascade?).

### Category: Behaviour Delta

**Canonical questions:** Q2.3, Q2.7, Q2.8

**Q2.3** -- What is the current behaviour, and what should the new behaviour be?

Vague answer: "The calculation is wrong and needs to be fixed."
Probe: "Can you describe what result the current calculation produces for
a specific instrument, and what the correct result should be? Even a
rough example with made-up numbers helps."

**Q2.7** -- What are the expected outputs for the happy path?

Vague answer: "The results should be correct."
Probe: "Can you give me a specific example? For a loan with a balance of
X and a rate of Y, what should the FTP_NetInterestIncome output be after
this change?"

**Q2.8** -- Are there any instrument types or portfolio segments that should
be excluded from this calculation change?

**Expand as needed:** Ask for multiple worked examples covering different
instrument types. For each exclusion, ask what the excluded instruments
should show instead.

### Category: FTP Logic

**Canonical questions:** Q2.4

**Q2.4** -- Does this change affect FTP calculations?

If the PM is unsure what a named revision date is:
"A named revision date is a specific date that overrides the default
rate lookup for certain instruments -- for example, when an instrument
was originated before a rate change but should still use the rate that
was in effect at a specific named date rather than the current rate.
Does this feature change how those overrides work?"

**Expand as needed:** If FTP is affected, ask about each sub-area (named
revision dates, rate source, instrument type scope) individually.

### Category: Error Handling

**Canonical questions:** Q2.5, Q2.6

**Q2.5** -- Does this change affect how return codes -1 through -8 are handled?

If the PM is not familiar with return codes:
"Return codes -1 through -8 are signals the stored procedures send back
when a calculation cannot complete -- for example, -3 means the instrument
has not been initialised for this process. Does this feature change what
should happen when one of those codes is returned?"

**Q2.6** -- Does this change affect any of the instrument flags?

"The codebase uses three flags that control which instruments are included
in calculations: NewInstFlag (instruments added this period), ClosedInstFlag
(instruments that closed this period), and PlugInstrumentFlag (plug/balancing
instruments). Does this feature change how any of those flags are used?"

**Expand as needed:** For each affected return code, ask about the desired
UI behaviour and recovery path. For flag changes, ask about backward
compatibility with existing data.

---

## Section 3 -- Allocation methodology

### Category: Allocation Type and Methodology

**Canonical questions:** Q3.1, Q3.2

**Q3.1** -- Which allocation type does this change affect?

If the PM uses terms without defining them: "When you say 'standard
allocation', which of these do you mean -- expense allocation (distributing
costs to instruments), income allocation (distributing fee income), capital
allocation (distributing regulatory capital requirements), or provisions
allocation?"

**Q3.2** -- What is the current allocation methodology, and what should it
be after this change?

Vague answer: "It should use the correct methodology."
Probe: "Can you describe the current rule in a sentence? For example,
'today, expenses are allocated pro-rata based on instrument balance'. Then
tell me what the new rule should be."

**Expand as needed:** Ask for representative test cases with specific
numbers to validate understanding of the methodology change.

### Category: Driver and Scope

**Canonical questions:** Q3.3, Q3.4, Q3.6, Q3.7

**Q3.3** -- Which cost pools or income streams are affected?

**Q3.4** -- What is the allocation driver?

If the PM is unsure: "The allocation driver is the metric that determines
how much each instrument receives. Common examples are: balance, revenue,
headcount, or a fixed percentage table. What should drive the allocation
in this case?"

**Q3.6** -- Are there any instruments, entities, or periods that should be
excluded from this allocation change?

**Q3.7** -- What are the expected allocation outputs for a representative
test case?

**Expand as needed:** For complex allocations with multiple drivers, ask
about priority and conflict resolution between drivers.

### Category: Log and Schema Impact

**Canonical questions:** Q3.5

**Q3.5** -- Does this change affect the GLAllocationLog?

**Expand as needed:** If the log is affected, ask about schema changes,
backward compatibility with existing log entries, and reporting impact.

---

## Section 4 -- Acceptance criteria

### Category: Success Scenarios

**Canonical questions:** Q4.1, Q4.2

**Q4.1** -- What does success look like for this feature?

Vague answer: "When the numbers are correct."
Probe: "Can you walk me through one specific scenario? Tell me the starting
conditions -- for example, 'a portfolio with 500 loans, ProcessID 1001,
revision date January 2026' -- and what the output should be."

If the PM gives a scenario without a specific expected output:
"What specific value or condition would tell you this scenario has passed?
For example, 'FTP_NetInterestIncome for instrument XYZ should equal Y'."

**Q4.2** -- How will you verify this feature is working in UAT?

**Expand as needed:** Ask for at least 2-3 scenarios. For each scenario,
probe until you have explicit input, action, and measurable output.
Generate additional scenario questions for edge conditions discovered in
recon (e.g., "What about a portfolio with zero instruments matching the
filter?").

### Category: Performance and Test Scope

**Canonical questions:** Q4.3, Q4.4

**Q4.3** -- Are there any performance requirements?

If the PM says "it should be fast": "Do you have a specific threshold in
mind? For example, 'the calculation should complete in under 30 seconds
for a portfolio of 10,000 instruments'."

**Q4.4** -- Are there any existing tests that this feature must not break?

**Expand as needed:** From recon, name specific test files and ask the PM
to confirm scope. Ask about regression risk for adjacent features.

---

## Section 5a -- Scope boundaries

### Category: Explicit Exclusions

**Canonical questions:** Q5a.1, Q5a.2

**Q5a.1** -- What is explicitly out of scope for this feature?

Always prompt with adjacent areas from your codebase recon:
"Based on what I found in the code, [adjacent area] is closely related
to this feature. Is that in scope or explicitly out of scope?"

**Q5a.2** -- Is there anything that looks related but should NOT be changed?

**Expand as needed:** For each adjacent component or feature discovered in
recon, generate a specific in/out scope question. Do not rely on the PM
to enumerate -- present them with specific options to confirm or deny.

### Category: Downstream Impact and Boundaries

**Canonical questions:** Q5a.3, Q5a.4

**Q5a.3** -- Are there any downstream systems or consumers that must not
be affected?

**Q5a.4** -- Does this feature touch the Dataverse boundary?

If the PM is unsure: "Dataverse holds the GL data, organisation hierarchies,
and reference dimensions that feed into Profitability calculations. If this
feature needs to read from or write to any of those -- for example, reading
a new GL account dimension or writing back a result -- that crosses the
Dataverse boundary and needs explicit permission. Does this feature do any
of that?"

**Expand as needed:** If downstream consumers exist, ask about notification
or versioning requirements. For Dataverse boundary crossings, ask about
write permissions and data validation.

---

## Section 5b -- UI and UX

### Category: Screen Inventory

**Canonical questions:** Q5b.1, Q5b.2, Q5b.3, Q5b.4

**Q5b.1-Q5b.4** cover screen listing, new vs. modified classification,
purpose, and navigation triggers.

**Expand as needed:** For each screen identified, ask about its
relationship to other screens (navigation flow, data passing between
screens). Generate layout composition questions for complex screens.

### Category: Component Inventory

**Canonical questions:** Q5b.5

**Q5b.5** -- For each component: name, type, function, and data binding.

If the PM gives a visual description: "Rather than how it looks, can you
describe what it does? For example, 'when the user selects a ProcessID,
it filters the result table to show only instruments associated with that
process'. That kind of description is what the development team needs."

If the PM says "it shows the data": "Which specific data field does it
show? For example, does it display the ProcessID, the Adjusted_GL amount,
the SP parameter value, or a calculated measure from the result set?"

**Expand as needed:** For complex screens with many components, ask about
each component individually. For each component, ensure all three sub-parts
(name/type, functional description, data binding) are captured before
moving on.

### Category: State Models

**Canonical questions:** Q5b.6, Q5b.7, Q5b.8, Q5b.9

**Q5b.6** -- Component states and transition triggers.

If the PM lists only the default state: "What does this component look like
when there is no data to show? What does it look like when it is loading?
What does it look like if an error occurs?"

**Q5b.7** -- Empty states for data-displaying components.
**Q5b.8** -- Error states for components that can fail.
**Q5b.9** -- Loading states for components that fetch data.

**Expand as needed:** For every component identified, systematically ask
about empty, loading, error, and disabled states. Do not accept "same as
other components" -- get specifics for each.

### Category: Interaction Model

**Canonical questions:** Q5b.10, Q5b.11

**Q5b.10** -- Non-standard user interactions.
**Q5b.11** -- Visual references (verbal description only).

If the PM tries to share a file or link: "I cannot accept files or links
directly -- please describe what the visual shows in words. The
plan-preview-generator agent will produce the actual visual from that
description during S4."

**Expand as needed:** For each non-standard interaction, ask about
keyboard shortcuts, accessibility, and mobile/responsive considerations.

---

## Section 6 -- Edge-case phase: category question catalogue

These are starting points -- generate additional questions based on what
the codebase reconnaissance revealed for the specific feature. Ask
questions in batches of 3-5, grouped by category. Reference specific
codebase findings.

### EC Category 1 -- Interaction sequence

- "What happens if the user [performs action A] and then [performs action B]
  before the first action completes? For example, from the codebase I can
  see that [specific component/SP] handles [action A] -- what if the user
  triggers [action B] while that is still processing?"
- "What happens if the user starts an operation and then navigates away
  before it completes? Is their work preserved?"
- "What happens if the user has unsaved changes and attempts to perform
  another action? Should they be warned?"
- "What happens if the user applies a filter and then triggers an operation
  -- does the filter persist, or does the operation reset it?"

**Expand as needed:** Generate a question for every pair of user actions
identified in Sections 1-5b that could interact. Reference specific
component names from recon.

### EC Category 2 -- Cascading behaviour

- "If [entity name] is renamed or modified, where else in the application
  does this entity appear? Should those occurrences auto-update?"
- "If [entity] is deleted, what happens to other entities that reference
  it? Are they deleted, orphaned, or blocked from deletion?"
- "If a configuration value is changed, does any existing data become
  invalid? What should happen to that data?"
- "From the codebase I can see that [component/view] depends on [entity].
  If the entity changes, should this component reflect the change
  immediately or on next load?"

**Expand as needed:** Ask about every entity identified in recon that this
feature modifies. For each entity, trace its downstream references.

### EC Category 3 -- Concurrency

- "What if two users both attempt to modify the same [entity/record] at
  the same time? Who wins? Is one blocked?"
- "What if one user deletes [entity] while another user is editing it?"
- "What if a background calculation or allocation process is running while
  a user modifies data that the process is reading?"
- "Should changes made by other users be visible in real-time, or only
  after a page refresh?"

**Expand as needed:** Ask about every action that modifies shared state.
Reference specific tables or SPs that multiple processes access.

### EC Category 4 -- State boundary

- "When there are zero items, what should every action button and display
  component do? Are they disabled, hidden, or do they show a message?"
- "Is there a maximum number of [items/entities]? What happens when that
  limit is reached?"
- "What happens during state transitions -- for example, while data is
  saving or while a calculation is starting?"
- "Can [entity A] be in [state X] while [related entity B] is in
  [state Y]? Is that a valid combination?"

**Expand as needed:** Ask about every component's empty state, maximum
capacity, and invalid state combinations.

### EC Category 5 -- Cross-component dependency

- "From the codebase I can see that [component B] depends on data from
  this feature. If this feature's data changes, what should [component B]
  show?"
- "What happens to this feature if [upstream component/data source] is
  incomplete or missing?"
- "Are there any circular dependencies between components that could cause
  update loops?"

**Expand as needed:** Ask about every dependency relationship identified
in recon. Trace both upstream and downstream.

### EC Category 6 -- Data integrity

- "What about records that were created before this feature exists? Do
  they need migration, or do they show a default state?"
- "Is partial data entry allowed? Can the user save incomplete data?"
- "For bulk operations, what happens if some items succeed and others
  fail? Does the user see a partial result?"
- "Can every action be undone? If so, does undo restore the immediately
  previous state or the original state?"

**Expand as needed:** Ask about every data entity this feature creates or
modifies. Ask about historical data, partial saves, and undo/redo.

### EC Category 7 -- Failure and recovery

- "If the user triggers [operation] and it fails, what do they see? Is
  their input preserved? Can they retry?"
- "If validation fails on some fields, which fields are highlighted? Is
  the valid data preserved?"
- "If a bulk action partially fails, can the user address just the failed
  items without re-processing the successful ones?"
- "If a background process fails, how is the user informed? What is their
  recovery path?"

**Expand as needed:** Ask about every operation that involves a stored
procedure call, API request, or data write. For each, cover the user's
visibility into the failure and their recovery options.
