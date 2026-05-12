# Question Sets -- Probing Guidance and Profitability Examples

Reference for prd-interviewer. Contains probing guidance for each question
and Profitability-specific examples to use when an answer is too vague.

---

## How to use this reference

When a PM gives a vague answer, probe once using the example language below.
If the second answer is still insufficient, park the question and move on.
Do not probe more than once per question.

---

## Section 1 -- Feature and capability definition

### Q1.1 -- Feature name
Probing: if the PM gives a name that is too generic ("FTP update", "allocation
fix"), ask: "Is there a more specific name that distinguishes this from other
FTP or allocation work that has been done before?"

### Q1.2 -- What does this feature do
Vague answer: "It improves the FTP calculation."
Probe: "Can you describe what a user will be able to do or see after this
feature exists that they cannot do today? For example, will they see a new
measure in the output, will the calculation run in a different way, or will
they have a new screen to interact with?"

Vague answer: "It fixes an issue with allocations."
Probe: "When you say 'fixes', do you mean the calculation is producing an
incorrect result today and this brings it into line with the expected
methodology -- or is this a new allocation type being added?"

### Q1.3 -- Primary change type
If the PM selects multiple types: "Which of these is the primary driver --
the others will shape the scope boundaries, but knowing the primary helps
us structure the interview."

### Q1.4 -- Area of the product
Use your codebase recon to offer specific options:
"Based on the codebase, this feature appears to relate to [area you found].
Is that right, or does it also touch [other area you identified]?"

---

## Section 2 -- Calculation logic changes

### Q2.1 -- Affected measures
If the PM is unsure which measures are affected, read them the relevant
subset from the 42-measure output set and ask them to confirm:
"From the output set, the measures most likely affected by an FTP change
are FTP_GrossInterestIncome, FTP_FundingCost, FTP_NetInterestIncome,
FTP_Rate, and FTP_Volume. Does this match your understanding, or are there
others?"

If the PM says "all measures": "Do you mean literally all 42 measures will
change, or that the measures in the FTP group will change and downstream
roll-ups will reflect that?"

### Q2.2 -- Stored procedures
From your recon, name the procedures you found:
"I can see that usp_CalculateFTP and usp_ApplyRevisionDate are the primary
procedures in this area. Are those the ones in scope, or are there others
you know of?"

### Q2.3 -- Current vs. new behaviour
Vague answer: "The calculation is wrong and needs to be fixed."
Probe: "Can you describe what result the current calculation produces for
a specific instrument, and what the correct result should be? Even a
rough example with made-up numbers helps."

### Q2.4 -- FTP and revision dates
If the PM is unsure what a named revision date is:
"A named revision date is a specific date that overrides the default
rate lookup for certain instruments -- for example, when an instrument
was originated before a rate change but should still use the rate that
was in effect at a specific named date rather than the current rate.
Does this feature change how those overrides work?"

### Q2.5 -- Return codes
If the PM is not familiar with return codes:
"Return codes -1 through -8 are signals the stored procedures send back
when a calculation cannot complete -- for example, -3 means the instrument
has not been initialised for this process. Does this feature change what
should happen when one of those codes is returned?"

### Q2.6 -- Instrument flags
"The codebase uses three flags that control which instruments are included
in calculations: NewInstFlag (instruments added this period), ClosedInstFlag
(instruments that closed this period), and PlugInstrumentFlag (plug/balancing
instruments). Does this feature change how any of those flags are used?"

### Q2.7 -- Expected outputs
Vague answer: "The results should be correct."
Probe: "Can you give me a specific example? For a loan with a balance of
X and a rate of Y, what should the FTP_NetInterestIncome output be after
this change?"

---

## Section 3 -- Allocation methodology

### Q3.1 -- Allocation type
If the PM uses terms without defining them: "When you say 'standard
allocation', which of these do you mean -- expense allocation (distributing
costs to instruments), income allocation (distributing fee income), capital
allocation (distributing regulatory capital requirements), or provisions
allocation?"

### Q3.2 -- Current vs. new methodology
Vague answer: "It should use the correct methodology."
Probe: "Can you describe the current rule in a sentence? For example,
'today, expenses are allocated pro-rata based on instrument balance'. Then
tell me what the new rule should be."

### Q3.4 -- Allocation driver
If the PM is unsure: "The allocation driver is the metric that determines
how much each instrument receives. Common examples are: balance, revenue,
headcount, or a fixed percentage table. What should drive the allocation
in this case?"

---

## Section 4 -- Acceptance criteria

### Q4.1 -- Success scenarios
Vague answer: "When the numbers are correct."
Probe: "Can you walk me through one specific scenario? Tell me the starting
conditions -- for example, 'a portfolio with 500 loans, ProcessID 1001,
revision date January 2026' -- and what the output should be."

If the PM gives a scenario without a specific expected output:
"What specific value or condition would tell you this scenario has passed?
For example, 'FTP_NetInterestIncome for instrument XYZ should equal Y'."

### Q4.3 -- Performance requirements
If the PM says "it should be fast": "Do you have a specific threshold in
mind? For example, 'the calculation should complete in under 30 seconds
for a portfolio of 10,000 instruments'."

---

## Section 5a -- Scope boundaries

### Q5a.1 -- Out of scope
Always prompt with adjacent areas from your codebase recon:
"Based on what I found in the code, [adjacent area] is closely related
to this feature. Is that in scope or explicitly out of scope?"

### Q5a.4 -- Dataverse boundary
If the PM is unsure: "Dataverse holds the GL data, organisation hierarchies,
and reference dimensions that feed into Profitability calculations. If this
feature needs to read from or write to any of those -- for example, reading
a new GL account dimension or writing back a result -- that crosses the
Dataverse boundary and needs explicit permission. Does this feature do any
of that?"

---

## Section 5b -- UI and UX

### Q5b.5 -- Component functional description
If the PM gives a visual description: "Rather than how it looks, can you
describe what it does? For example, 'when the user selects a ProcessID,
it filters the result table to show only instruments associated with that
process'. That kind of description is what the development team needs."

### Q5b.5c -- Data binding
If the PM says "it shows the data": "Which specific data field does it
show? For example, does it display the ProcessID, the Adjusted_GL amount,
the SP parameter value, or a calculated measure from the result set?"

### Q5b.6 -- Component states
If the PM lists only the default state: "What does this component look like
when there is no data to show? What does it look like when it is loading?
What does it look like if an error occurs?"

### Q5b.11 -- Visual references
If the PM tries to share a file or link: "I cannot accept files or links
directly -- please describe what the visual shows in words. For example,
'it shows a table with three columns: instrument ID on the left, FTP rate
in the middle, and a status indicator on the right'. The wireframe-agent
will produce the actual visual from that description."

---

## Section 6 -- Edge cases

### Q6.2 -- Data quality issues
Prompt with specifics from your codebase recon:
"From the code, I can see that [specific edge case you found] is handled
explicitly. Is that still the intended behaviour under this feature, or
does this change how that case should be handled?"

### Q6.5 -- Naming inconsistencies
Share what you found in your recon. For example:
"I noticed that the codebase uses both 'MktRisk' and 'MarketRisk' in
different places -- this appears to be a known inconsistency. Are there
any similar naming issues in the area this feature touches that the build
team should be aware of?"

---

## Section 6 -- Edge-case phase: category question catalogue

Reference for the edge-case phase of the interview. These are starting
points — generate additional questions based on what the codebase
reconnaissance revealed for the specific feature.

### EC Category 1 — Interaction sequence

- "What happens if the user [performs action A] and then [performs action B]
  before the first action completes? For example, from the codebase I can
  see that [specific component/SP] handles [action A] — what if the user
  triggers [action B] while that is still processing?"
- "What happens if the user starts an operation and then navigates away
  before it completes? Is their work preserved?"
- "What happens if the user has unsaved changes and attempts to perform
  another action? Should they be warned?"
- "What happens if the user applies a filter and then triggers an operation
  — does the filter persist, or does the operation reset it?"

### EC Category 2 — Cascading behaviour

- "If [entity name] is renamed or modified, where else in the application
  does this entity appear? Should those occurrences auto-update?"
- "If [entity] is deleted, what happens to other entities that reference
  it? Are they deleted, orphaned, or blocked from deletion?"
- "If a configuration value is changed, does any existing data become
  invalid? What should happen to that data?"
- "From the codebase I can see that [component/view] depends on [entity].
  If the entity changes, should this component reflect the change
  immediately or on next load?"

### EC Category 3 — Concurrency

- "What if two users both attempt to modify the same [entity/record] at
  the same time? Who wins? Is one blocked?"
- "What if one user deletes [entity] while another user is editing it?"
- "What if a background calculation or allocation process is running while
  a user modifies data that the process is reading?"
- "Should changes made by other users be visible in real-time, or only
  after a page refresh?"

### EC Category 4 — State boundary

- "When there are zero items, what should every action button and display
  component do? Are they disabled, hidden, or do they show a message?"
- "Is there a maximum number of [items/entities]? What happens when that
  limit is reached?"
- "What happens during state transitions — for example, while data is
  saving or while a calculation is starting?"
- "Can [entity A] be in [state X] while [related entity B] is in
  [state Y]? Is that a valid combination?"

### EC Category 5 — Cross-component dependency

- "From the codebase I can see that [component B] depends on data from
  this feature. If this feature's data changes, what should [component B]
  show?"
- "What happens to this feature if [upstream component/data source] is
  incomplete or missing?"
- "Are there any circular dependencies between components that could cause
  update loops?"

### EC Category 6 — Data integrity

- "What about records that were created before this feature exists? Do
  they need migration, or do they show a default state?"
- "Is partial data entry allowed? Can the user save incomplete data?"
- "For bulk operations, what happens if some items succeed and others
  fail? Does the user see a partial result?"
- "Can every action be undone? If so, does undo restore the immediately
  previous state or the original state?"

### EC Category 7 — Failure and recovery

- "If the user triggers [operation] and it fails, what do they see? Is
  their input preserved? Can they retry?"
- "If validation fails on some fields, which fields are highlighted? Is
  the valid data preserved?"
- "If a bulk action partially fails, can the user address just the failed
  items without re-processing the successful ones?"
- "If a background process fails, how is the user informed? What is their
  recovery path?"

