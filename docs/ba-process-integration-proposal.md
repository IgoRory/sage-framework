# SAGE Framework — BA Process Integration Proposal

**Author:** Framework Architecture Review  
**Date:** 2026-05-12  
**Status:** Proposal — awaiting Product Manager and Lead Dev review  
**Source material:** BA Feature Coverage Review v5.0 (five documents)  
**Target:** SAGE Phase 01 (PRD creation through completeness gate)

---

## Preamble — Working Model Summary

### Step 1 Findings: Current SAGE Phase 01

**prd-interviewer** currently:
- Runs a repo preflight (Step 0) verifying branch and sync state
- Conducts silent codebase reconnaissance before asking questions (Step 2)
- Asks questions one-at-a-time across six sections (P1–P7): Feature definition, Calculation logic (conditional), Allocation methodology (conditional), Acceptance criteria, Scope boundaries, UI/UX (conditional), Edge cases and constraints
- Parks unanswered questions and records them as TODO items in the PRD
- Emits structured telemetry per phase boundary (JSONL)
- Generates a PRD draft + Component Specification child page on Notion
- Requires explicit PM APPROVE before generating drafts

**prd-completeness-check** currently scores across six dimensions:
- D1: Requirement coverage (15pts) — testable predicates, no vague qualifiers
- D2: AC specificity (15pts) — agent-evaluable Given/When/Then
- D3: Edge/empty/error state coverage (15pts) — non-happy-path states
- D4: Mockup file completeness (15pts) — file existence at declared paths
- D5: UI component specification (25pts) — six-element check per component
- D6: Out-of-scope clarity (15pts) — explicit exclusion section

Pass threshold: 80/100. On pass, Linear issue status → Ready.

**Hook layer for Phase 01:** There is no Phase 01–specific blocking hook. The `prd_telemetry_append.py` is a utility script for telemetry, not a gate. The `prd.completenessThreshold` in `workflow-config.json` is consumed by the skill, not enforced by a hook. The PRD gate is currently instruction-enforced: the skill refuses to set Ready if the score is below threshold, but no hook structurally blocks a human or agent from setting that status directly in Linear.

**Agent vs. skill distinction:** Skills guide human-facing authoring sessions (interactive, conversational, skill reads reference docs). Agents are autonomous multi-step executors (build, review, test). Phase 01 uses skills; Phase 03+ uses agents.

**Reference doc conventions:** Each skill stores reference files in a `references/` subdirectory within its skill package (e.g., `.cursor/skills/prd-interviewer/references/question-sets.md`).

### Step 1 Findings: Canonical Terminology

| SAGE Term | BA Document Equivalent |
|---|---|
| Linear feature issue | ADO work item / US##### |
| PRD (Product Requirements Document) | Business Requirements Document |
| Component Specification (Notion child page) | Demo-Behavior-Manifest.md |
| prd-interviewer (skill) | BA Feature Coverage Review (skill) |
| prd-completeness-check (skill) | Phase 8 Final Self-Review |
| Product Manager (PM) | Business Analyst (BA) |
| Lead Dev | No direct equivalent |
| Linear issue ID (LIN-####) | ADO work item ID (US#####) |
| Phase 01 (PRD creation) | Phases 0–9 of BA review |
| Session manifest | No equivalent (BA process is pre-pipeline) |
| Hook / gate | No equivalent (BA process is instruction-enforced) |
| Park-it pattern | Unified Deferred Items List |
| Validation mockup (S4 artifact) | Demo-Interactive.html |
| Calculation proof (S4 artifact) | Calculation-Logic-Demo.html |
| Codebase reconnaissance (Step 2) | Pre-Interview Investigation (Phase 2) |
| Feature issue status: Ready | Development Readiness: Ready |
| Completeness score (0-100) | PRD Readiness Score (1-5 per area) |
| TODO items in PRD | Deferred Items List |
| Telemetry (JSONL) | No equivalent |
| Notion (PRD storage) | Local markdown files |
| Scoring rubric (reference doc) | Self-review checklists |

### Step 2 Findings: BA Document Deconstruction

**Document 1: SKILL.md (BA master skill)**
- Actually contains: the orchestrating skill definition for a 10-phase BA review process
- Purpose: coordinates the full review lifecycle from context gathering through deliverable creation
- Genuine gap components: complexity classification, context consistency validation, interview conclusion gates, dedicated edge-case interview phase, no-fabrication rule for user-facing text
- Product-specific components: ADO integration, Validation Dependencies protocol (PROF_XXX), `docs/cursor/BA Requirements/` folder structure, re-review detection
- Complexity without enforcement value: Phase tracker with restart commands (session management overhead), sequential deliverable creation order (irrelevant — SAGE generates from interview, not sequentially)
- Duplicates SAGE: codebase reconnaissance, question categories, park-it mechanism

**Document 2: pre-investigation.md**
- Actually contains: exhaustive pre-interview codebase investigation protocol
- Purpose: ensures the interviewer has full codebase context before asking questions
- Genuine gap components: codebase investigation manifest (structured output of what was read), context consistency validation (cross-checking user-provided docs vs. codebase), complexity classification with explicit thresholds, investigation summary presented to user before interview
- Product-specific: Angular/C#/SQL file structure, SCSS variables, Kendo dialogs, VD protocol
- Complexity without enforcement: re-review detection logic, tier 1/tier 2 styling classification
- Duplicates SAGE: the concept of codebase recon (already in prd-interviewer Step 2)

**Document 3: interview-questions.md**
- Actually contains: adaptive question catalogue organised by categories, with dynamic minimum question thresholds and a dedicated edge-case interview phase
- Purpose: ensures interview depth scales with feature complexity and edge cases are systematically covered
- Genuine gap components: dynamic minimum question thresholds tied to complexity classification, seven-category edge-case taxonomy with dedicated interview phase, interview conclusion gate protocol (structured summary + vague answer flagging + minimum count confirmation), cascading impact questions
- Product-specific: VD-specific interview category, specific Angular/page-based questions
- Complexity without enforcement: question tracking summary table (tracking overhead)
- Duplicates SAGE: business requirement validation questions, UI/UX questions, completeness check questions (already in question-sets.md)

**Document 4: demo-guidelines.md**
- Actually contains: HTML demo creation guidelines with styling tiers, production readiness gate
- Purpose: produces interactive demos for stakeholder review and developer reference
- Genuine gap components: the no-fabrication rule for user-facing message text (exact codebase text or [TEXT TBD])
- Product-specific: Tier 1/Tier 2 styling strategy (SCSS variables, Kendo styling), FontAwesome/Google Fonts, scenario selector UI spec, animation engine
- Complexity without enforcement: demo styling anti-patterns (design guidance, not framework concern)
- Duplicates SAGE: validation mockup concept (already exists as S4 validation-generator artifact)

**Document 5: self-review-and-checklists.md**
- Actually contains: inline self-review checklists per deliverable type, coverage validation checklists, completeness pressure test
- Purpose: systematic quality verification before presenting deliverables
- Genuine gap components: the completeness pressure test concept ("for EACH UI element — are ALL states documented?"), no-fabrication audit as a cross-cutting check, coverage heat map concept
- Product-specific: VD coverage checklist, demo HTML functional testing
- Complexity without enforcement: operational business coverage checklist items that SAGE handles at the build layer (S6 code review, S7 testing)
- Duplicates SAGE: prd-completeness-check already covers D1–D6 scoring

**Document 6: deliverable-templates.md**
- Actually contains: templates for all BA deliverables — Edge-Case-Analysis, Business Requirements, Demo-Behavior-Manifest, Scope Assessment, Work Item Assessment, BA Review Summary
- Purpose: standardised output format for each deliverable
- Genuine gap components: Edge-Case-Analysis template structure (seven-category taxonomy with unique IDs), the Demo-Behavior-Manifest concept (element-by-element behavioural specification with downstream impacts)
- Product-specific: ADO work item references, VD impact assessment section, story points
- Duplicates SAGE: PRD template (already exists), component specification template (already exists)

---

## Section 1: What to Adopt

### Addition 1: Complexity Classification with Dynamic Interview Depth

**What it is:** A structured complexity classifier that scores the feature across six factors before the interview begins, producing a complexity tier (Simple / Medium / Complex / Very Complex) that sets minimum question count thresholds for the interview.

**Which layer:** Skill (prd-interviewer) + Reference doc (new)

**Which existing file it extends:** `.cursor/skills/prd-interviewer/SKILL.md` (Step 2 — Silent codebase reconnaissance) and a new reference file `.cursor/skills/prd-interviewer/references/complexity-classifier.md`

**Justification:** The current prd-interviewer Step 2 reconnaissance has no structured output and no mechanism to scale interview depth based on what it finds. A feature that touches 7 pages, 16 business rules, and 8 entity types gets the same interview depth as a single-page config change. The BA documents' complexity classifier addresses this by providing explicit thresholds that determine minimum question counts. This prevents under-interviewing complex features — a gap that currently manifests as incomplete PRDs reaching completeness check and failing.

The minimum effective implementation is a reference document (complexity-classifier.md) consumed by the prd-interviewer skill. The skill's Step 2 emits a complexity classification as part of its telemetry. No new agent. No new hook. The classification feeds the skill's own behaviour and is recorded for the prd-interviewer-effectiveness-evaluator to track.

**Complexity cost:** Low. One new reference file. One addition to the existing skill's Step 2 output. One new telemetry field (`complexityTier`). The classifier thresholds will need recalibration as the team builds more features — the skill-effectiveness-evaluator already handles this.

---

### Addition 2: Context Consistency Validation

**What it is:** A structured check after codebase reconnaissance that cross-validates the Linear issue description and any user-provided context against what was actually found in the codebase. Contradictions, missing references, and incomplete sections are flagged as priority interview questions.

**Which layer:** Skill (prd-interviewer)

**Which existing file it extends:** `.cursor/skills/prd-interviewer/SKILL.md` — new Step 2b between current Step 2 (codebase recon) and Step 3 (set expectations)

**Justification:** The current prd-interviewer reads the codebase (Step 2) and reads the Linear issue (Step 1) but never cross-validates them. If the Linear issue says "modify Cost Pools page" but no Cost Pools component exists in the codebase, the interviewer asks the PM about Cost Pools without flagging the contradiction. This is a genuine gap: the interviewer has the data to detect the problem but no instruction to do so.

The BA process addresses this with an explicit Context Consistency Validation step (Phase 2, Step 10) that produces a Consistency Report with priority interview questions. The minimum effective implementation is a new step in the existing skill — no new file, no new agent, no hook.

**Complexity cost:** Minimal. One additional step in the skill instructions. No new files. The step is self-contained — if the validation finds no issues, it emits a clean telemetry line and moves on.

---

### Addition 3: Dedicated Edge-Case Interview Phase with Structured Taxonomy

**What it is:** A separate, named interview phase after the main business interview that systematically walks through seven edge-case categories: interaction sequence, cascading behaviour, concurrency, state boundary, cross-phase dependency, data integrity, and failure/recovery. Each category generates targeted questions grounded in the codebase reconnaissance findings.

**Which layer:** Skill (prd-interviewer) + Reference doc (update existing)

**Which existing file it extends:** `.cursor/skills/prd-interviewer/SKILL.md` — Section 6 is currently a single edge-case section. This addition restructures Section 6 into a dedicated phase with the seven-category taxonomy. Also updates `.cursor/skills/prd-interviewer/references/question-sets.md` with the edge-case question catalogue.

**Justification:** The current prd-interviewer has a single Section 6 ("Edge cases and constraints") with seven questions (Q6.1–Q6.7). These questions are domain-specific (instrument types, ProcessIDs, naming inconsistencies) but lack the systematic taxonomy that ensures all categories of edge case are covered. A feature that involves concurrent user scenarios, cascading entity modifications, or interaction sequence edge cases may never have those questions asked because Section 6 doesn't prompt for them.

The BA process dedicates an entire interview phase (Phase 4) to edge cases, organised into seven categories with example questions per category. This is the single highest-value addition from the BA documents: edge-case gaps in the PRD are the primary cause of rework during the build sprint.

The minimum effective implementation extends the existing Section 6 into a structured phase rather than a flat question list. The seven categories are added to `question-sets.md` as a new section. No new agent, no new skill, no new hook. A new phase ID (P6b or equivalent) is added to the telemetry mapping.

**Complexity cost:** Moderate. The question-sets.md reference doc grows significantly. The interview takes longer for complex features (which is the correct trade-off — complex features currently get under-interviewed). The added time is bounded by the complexity classification from Addition 1: Simple features get a shorter edge-case phase.

---

### Addition 4: Interview Conclusion Gate Protocol

**What it is:** A structured six-step protocol that must execute before the interview can conclude: present structured summary, flag vague answers, ask the open-ended coverage question, confirm minimum question count was met, review parked items, and get explicit PM confirmation to proceed.

**Which layer:** Skill (prd-interviewer)

**Which existing file it extends:** `.cursor/skills/prd-interviewer/SKILL.md` — "After the interview" section. The current post-interview steps are: review parked questions, write answer record, present summary, get APPROVE. This addition inserts a structured gate between the last interview question and the APPROVE prompt.

**Justification:** The current prd-interviewer can conclude the interview without verifying that the interview was thorough enough. It reviews parked questions and asks for APPROVE, but doesn't flag vague answers, doesn't confirm question count met the complexity threshold, and doesn't ask the open-ended "anything that keeps you up at night?" question that surfaces concerns the structured questions missed.

The BA process requires a six-step conclusion gate at the end of each interview phase. The minimum effective implementation adds this protocol to the existing "After the interview" section. It is instruction-enforced (the skill follows the protocol), not hook-enforced — this is acceptable because the PM is present and can observe whether the protocol was followed.

**Complexity cost:** Low. The protocol is six explicit steps added to the skill instructions. No new files. The protocol self-documents in the telemetry (P8 phase boundary captures whether the gate was reached).

---

### Addition 5: No-Fabrication Rule for User-Facing Message Text

**What it is:** A constraint that all user-facing message text in the PRD (toast messages, error messages, tooltip text, dialog text, validation messages) must either be quoted verbatim from the codebase with a source file reference, or — when no existing text can be identified — proposed by the agent with explicit PM approval. The prd-interviewer must never silently invent message text and write it into the PRD as though it were sourced.

**Which layer:** Skill (prd-interviewer) + Skill (prd-completeness-check)

**Which existing files it extends:**
- `.cursor/skills/prd-interviewer/SKILL.md` — new constraint in the Constraints section
- `.cursor/skills/prd-completeness-check/SKILL.md` — new sub-criterion under D1 (requirement coverage) or D3 (edge/empty/error state coverage)

**Justification:** The current prd-interviewer has no constraint on how user-facing message text is sourced. When the interviewer generates the PRD draft, it may invent plausible-sounding message text that doesn't match the existing codebase patterns. This creates a downstream problem: the build agent implements the invented text, then code review or testing discovers it doesn't match existing patterns, causing rework.

The BA documents' no-fabrication rule addresses this directly. However, marking every missing message as `[TEXT TBD]` without a proposal creates a large backlog of undefined text that the PM must author from scratch before the PRD can pass completeness check. The more useful behaviour is for the agent to propose text grounded in existing codebase patterns and present each proposal for explicit PM decision.

**Three-tier message text sourcing protocol:**

1. **Codebase-sourced** — text exists verbatim in the codebase. Quote it with a source reference: `[Source: path/to/file.ext:lineN]`. No PM action required.

2. **Agent-proposed** — no matching text exists in the codebase, but the agent can infer appropriate text from existing codebase patterns (similar messages in the same component, adjacent features, established tone and format). The agent proposes text and presents it to the PM during the interview with two explicit options:
   - **(a) Approve proposed text** — the agent's proposed text is written into the PRD, marked as `[Proposed — approved by PM]`
   - **(b) PM-provided text** — the PM provides their own text, which is written into the PRD, marked as `[PM-provided]`

   The agent must present each proposed message individually — not as a batch at the end. Each proposal must explain why no codebase source exists and what codebase patterns informed the proposal.

3. **Undetermined** — neither codebase text nor a reasonable proposal can be constructed (e.g., the feature introduces an entirely new interaction pattern with no precedent). Mark as `[TEXT TBD — requires PM decision]` with a note explaining what kind of text is needed and where it will appear.

The minimum effective implementation is a constraint in the prd-interviewer skill and a scored check in prd-completeness-check. This is enforceable at the completeness check gate: D1 or D3 deducts points for any user-facing message text that lacks one of the three markers (source reference, approved/PM-provided, or TBD).

**Complexity cost:** Low for the skill constraint. Moderate for the completeness check: the scorer must now verify that every message text instance carries one of the three markers. The agent-proposed workflow adds interview time proportional to the number of new messages the feature introduces, but this is time well spent — unresolved message text is a leading cause of S6 code review findings.

---

### Addition 6: Codebase Investigation Manifest

**What it is:** A structured output from the prd-interviewer's codebase reconnaissance (Step 2) that lists every file read during investigation, grouped by layer (frontend components, services, models, stored procedures, tests), with a one-line summary per file. This manifest is recorded in the interview telemetry and available to downstream agents.

**Which layer:** Skill (prd-interviewer)

**Which existing file it extends:** `.cursor/skills/prd-interviewer/SKILL.md` — Step 2 currently says "silently read the codebase" and "record internally". This addition specifies a structured manifest format for what was read.

**Justification:** The current Step 2 reconnaissance is silent with no structured output. This has two consequences: (1) there is no way to verify what the interviewer actually read during recon, and (2) downstream agents (orchestrator, phase-splitter) cannot reuse the recon findings — they must duplicate the investigation. The BA process produces a Codebase Investigation Manifest (Phase 2, Step 4) for exactly this purpose.

The minimum effective implementation adds a manifest format specification to the existing skill's Step 2. The manifest is emitted as a telemetry event (not a file — it is consumed by the skill itself and by downstream telemetry consumers). No new agent, no new hook.

**Complexity cost:** Low. The manifest format is added to the skill instructions. The telemetry event is one additional JSONL line. The main cost is that Step 2 takes slightly longer because the skill must structure its findings rather than storing them informally.

---

### Addition 7: Edge-Case Coverage as a Scored Dimension in prd-completeness-check

**What it is:** An enhancement to the existing D3 dimension (Edge/empty/error state coverage) that explicitly scores against the seven edge-case categories from the structured taxonomy (Addition 3). Currently D3 checks for empty, error, loading, and boundary states. The enhancement adds: interaction sequence, cascading behaviour, concurrency, cross-phase dependency, data integrity, and failure/recovery — assessed at the PRD level, not the component level.

**Which layer:** Skill (prd-completeness-check) + Reference doc (scoring-rubric.md)

**Which existing file it extends:**
- `.cursor/skills/prd-completeness-check/SKILL.md` — D3 section
- `.cursor/skills/prd-completeness-check/references/scoring-rubric.md` — D3 detailed guidance

**Justification:** The current D3 assesses non-happy-path states at the component level (empty, error, loading, boundary). But PRD-level edge cases — what happens when two users edit the same entity, what happens when entity A is deleted and entity B references it, what happens when a calculation runs while a user is editing source data — are not assessed. The PRD can score well on D3 today while having zero concurrency or cascading-behaviour edge cases documented.

The BA documents' seven-category edge-case taxonomy provides the assessment framework. The minimum effective implementation extends D3's deduction criteria to check for the presence of edge cases in each category that applies to the feature (not all seven apply to every feature). The scoring rubric reference doc is updated with per-category guidance.

**Complexity cost:** Moderate. The D3 assessment becomes more complex. The scorer must understand which edge-case categories apply to the feature being assessed (a pure database feature has no UI interaction sequences). The scoring rubric must provide clear applicability rules. The skill-effectiveness-evaluator can recalibrate the D3 deduction values over time.

---

## Section 2: What to Adapt

### Adaptation 1: Complexity Classifier Thresholds

**Source:** BA SKILL.md — "Complexity Classifier Thresholds" table and pre-investigation.md Step 9

**What needs to change:**
- Replace "Pages affected" with "Scoped files affected" (SAGE scopes by file, not by Angular page)
- Replace "User actions" with "User interactions" (SAGE component spec counts interactions, not page-level actions)
- Replace "Cross-page dependencies" with "Cross-phase dependencies" (SAGE organises by phase, not by page)
- Remove "Integration points" as a standalone factor — SAGE captures this in the phase-splitter's dependency analysis at kick-off, not at PRD time
- Add a Profitability-specific factor: "Stored procedures affected" (SP count is a stronger complexity signal in this codebase than generic entity types)

**SAGE equivalent terminology:**

| BA Term | SAGE Term |
|---|---|
| Pages affected | Scoped files affected |
| Business rules | Requirements (Section 5 of PRD) |
| Entity types | Data entities (models, tables, SPs) |
| User actions | User interactions (component spec) |
| Integration points | Cross-phase dependencies |
| Cross-page dependencies | Downstream/upstream phase dependencies |
| Simple / Medium / Complex / Very Complex | Tier 1 / Tier 2 / Tier 3 / Tier 4 |

### Adaptation 2: Seven Edge-Case Categories

**Source:** BA interview-questions.md — Phase 4 edge-case categories

**What needs to change:**
- "Cross-Page Dependency Edge Cases" → "Cross-Phase Dependency Edge Cases" (SAGE organises work by phase, not by page; but at PRD time, "cross-component dependency" is more accurate since phases haven't been defined yet)
- All example questions must be de-coupled from Angular/page terminology and restated in terms of SAGE's domain language: stored procedures, views, Adjusted_GL fields, ProcessIDs
- VD-specific examples removed (Validation Dependencies are a Profitability implementation detail, not a framework concept — they belong in a product-specific reference doc if needed)
- "What happens if the user navigates away" → reframed as state persistence edge case
- "What happens if the user refreshes the browser" → reframed as state recovery edge case

**SAGE equivalent terminology:**

| BA Category | SAGE Category |
|---|---|
| Interaction Sequence | Interaction Sequence |
| Cascading Behavior | Cascading Behaviour |
| Concurrency | Concurrency |
| State Boundary | State Boundary |
| Cross-Page Dependency | Cross-Component Dependency |
| Data Integrity | Data Integrity |
| Failure & Recovery | Failure and Recovery |

### Adaptation 3: Interview Conclusion Gate Steps

**Source:** BA interview-questions.md — "Interview Conclusion Gate" protocol

**What needs to change:**
- "Confirm minimum question count" references the complexity-driven thresholds from Adaptation 1 — the counts must use SAGE's tier naming
- "Review Deferred Items List" → "Review parked questions" (SAGE uses "park-it pattern", not "deferred items")
- "Shall I proceed to the edge-case interview?" → "Shall I proceed to the edge-case phase?" (SAGE terminology)
- The six-step protocol must be stated in SAGE predicate language, not as a numbered checklist with emoji status markers

### Adaptation 4: No-Fabrication Rule — Three-Tier Protocol

**Source:** BA demo-guidelines.md and self-review-and-checklists.md

**What needs to change:**
- The original BA rule is binary: verbatim codebase text or `[TEXT TBD]`. SAGE adopts a three-tier protocol (see Addition 5):
  - Tier 1 (Codebase-sourced) uses `[Source: path/to/file.ext:lineN]`
  - Tier 2 (Agent-proposed) presents proposed text individually to the PM with two options: approve proposed text or PM provides their own text. Approved proposals are marked `[Proposed — approved by PM]`, PM-provided text is marked `[PM-provided]`
  - Tier 3 (Undetermined) uses `[TEXT TBD — requires PM decision]`
- `[TEXT TBD — requires BA/Dev decision]` → `[TEXT TBD — requires PM decision]` (SAGE uses "Product Manager", not "BA/Dev")
- The rule must reference SAGE's codebase access patterns: stored procedure messages, Angular component toast/dialog text, error response bodies from API controllers
- The codebase source reference format must specify: `[Source: path/to/file.ext:lineN]` rather than a freeform reference

---

## Section 3: What to Exclude

### Exclusion 1: Phase Tracker with Restart Commands

**What it is:** An interactive phase status system where the PM can ask "what phase am I on" or "restart Phase 3" at any point, with full cascade-reset logic.

**Why excluded:** Complexity cost exceeds benefit. SAGE Phase 01 is a single-skill single-session interaction. The prd-interviewer already emits telemetry per phase boundary, and the PM can see progress through the conversation. Adding restart infrastructure with cascade-reset logic is over-engineering for a conversational skill. If the PM wants to revisit a section, they can simply say so — the skill's existing park-it pattern and interview structure handle this. The BA process needed this because it spans multiple phases across potentially multiple sessions; SAGE's prd-interviewer runs in one session.

### Exclusion 2: Interactive HTML Demo Creation (Demo-Interactive.html)

**What it is:** A self-contained HTML file with scenario selector, AC sidebar, interactive buttons, animation engine, and styled to match the real application's SCSS variables.

**Why excluded:** Duplicates existing coverage. SAGE already produces validation artifacts at S4 (validation-generator agent): HTML mockups for UI phases and calculation proof documents for calculation phases. The BA demo system is more elaborate (scenario selector, AC sidebar, animation engine) but this elaboration serves a different purpose — stakeholder presentation in a non-SAGE pipeline. In SAGE, the S4 mockup is confirmed by the developer setting `validationConfirmed = true`, and the build agent uses the component specification and PRD as its blueprint, not the demo. The demo's complexity (Tier 1/Tier 2 styling, production readiness gate, demo-specific self-review) is significant maintenance overhead for a presentation artifact that SAGE's pipeline does not consume.

### Exclusion 3: Demo-Behavior-Manifest.md

**What it is:** A separate developer-facing document mapping every interactive element to its complete behavioural contract (states table, click behaviour, downstream impacts, edge case references).

**Why excluded:** Duplicates existing coverage. SAGE's Component Specification (Notion child page) already covers the same six elements per component: name/type, functional description, states with triggers, user interactions, selectable options, and data binding. The Demo-Behavior-Manifest adds downstream impacts and edge case cross-references, but these are addressed by the proposed Addition 3 (edge-case taxonomy in the PRD itself) and Addition 7 (edge-case coverage scoring). Creating a parallel document to the Component Specification would violate the "maintain the existing layer model" principle — the Component Specification is SAGE's single source of truth for component behaviour.

### Exclusion 4: Validation Dependencies Impact Assessment

**What it is:** A mandatory protocol for cross-referencing all affected pages against 41 known validation dependencies (PROF_XXX), with UI impact assessment for navigation panel, home page tiles, and tab headers.

**Why excluded:** Product-specific (not generalisable). Validation Dependencies are a Profitability application feature, not a SAGE framework concept. The 41 PROF_XXX dependencies, the navigation panel impact, the home page calculation tiles — all of these are implementation details of the current application. If the team needs a VD impact check, it should live in a product-specific reference document consumed by the prd-interviewer as an optional extension, not baked into the framework-level skill. This is the correct isolation boundary per Guiding Principle 5 (maintain the layer model) and Test 5 (is it stable enough to maintain — VD lists change as the product evolves).

### Exclusion 5: Work Item Assessment (Story Points, Risk Level)

**What it is:** A deliverable that assigns complexity scores, story point recommendations, risk levels, and AI assistance assessments per work item.

**Why excluded:** Violates guiding principles. SAGE explicitly replaces estimation with empirical delivery data (Terms of Reference, Section 6: "Evidence over estimation — no human estimation is used at any stage of planning"). Story point estimation is antithetical to SAGE Intel's evidence-based approach. Complexity classification (Addition 1) is adopted because it drives interview depth, not because it drives effort estimation.

### Exclusion 6: Scope Assessment Deliverable

**What it is:** A standalone document with dependency map, PRD splittability analysis, and readiness scores (1-5 per area).

**Why excluded:** Duplicates existing coverage. SAGE's phase-splitter skill already performs dependency analysis, independence scoring, and phase sequencing at kick-off. SAGE's prd-completeness-check already produces a scored readiness assessment (0-100 with per-dimension breakdowns). The BA Scope Assessment exists because the BA process does not have these downstream skills — it needs to package the analysis for handoff to a separate planning process. SAGE's pipeline is continuous, so the analysis happens at the right point without a separate deliverable.

### Exclusion 7: Sequential Deliverable Creation Order

**What it is:** A mandatory creation sequence (Edge cases → BR → Demo → Manifest → Calc Demo → Scope → Assessment → Summary) with inline self-review after each deliverable.

**Why excluded:** Architecture mismatch. SAGE generates the PRD and Component Specification from the interview answer record in a single generation step (P9). The BA process generates multiple separate deliverables in sequence because it serves multiple audiences (QA, stakeholders, developers) with separate documents. SAGE's PRD is a single document consumed by the build pipeline. The sequential creation logic adds complexity without adding quality — the quality comes from the interview depth and the completeness check, not from the generation order.

### Exclusion 8: Tier 1 / Tier 2 Demo Styling Strategy

**What it is:** A two-tier styling classification for HTML demos: Tier 1 replicates exact SCSS variables for existing features, Tier 2 uses intentional distinctive design for new features.

**Why excluded:** Product-specific (not generalisable). The styling strategy references specific SCSS files, Kendo component libraries, and CSS class names. It is a design guideline for HTML demo creation, which is excluded (Exclusion 2). If demo creation is ever adopted, the styling strategy would belong in a product-specific reference document, not in the framework.

### Exclusion 9: Coverage Validation Checklists (Phase 6 + Phase 8)

**What it is:** Extensive checklists covering functional, data, integration, non-functional, UI/UX, validation dependency, edge case, and operational coverage, applied both inline (per deliverable) and as a final cross-cutting review.

**Why excluded:** Duplicates existing coverage with unnecessary complexity. SAGE's prd-completeness-check already provides a six-dimension scored assessment. The proposed Addition 7 (edge-case coverage scoring) strengthens D3 to cover the edge-case gap. Adding a separate checklist layer on top of the scored assessment creates two parallel quality systems — one that produces a score (prd-completeness-check) and one that produces checkmarks (checklists). The scored system is superior because it integrates with the Linear status gate and the skill-effectiveness-evaluator's calibration loop. The checklist items that are genuinely missing from prd-completeness-check (no-fabrication audit, edge-case category coverage) are adopted as scored additions to the existing dimensions.

### Exclusion 10: Re-Review Detection

**What it is:** Automatic detection of prior deliverables for the same feature, with update-mode workflow that focuses on changed areas.

**Why excluded:** Premature for current framework maturity. SAGE's prd-completeness-check already supports re-assessment (the scoring rubric has explicit re-assessment guidance with delta tracking). The prd-interviewer does not currently support resume-from-prior-interview, and adding that capability is a separate engineering effort unrelated to the BA process integration. If interview resume is needed, it should be designed as a first-class prd-interviewer feature, not backported from the BA process's re-review mechanism.

---

## Section 4: Terminology Normalisation Reference

Every term below must be substituted before any BA document content is written into SAGE files.

| BA Document Term | SAGE Canonical Term |
|---|---|
| Business Analyst (BA) | Product Manager (PM) |
| ADO work item | Linear feature issue |
| US##### | LIN-#### |
| Business Requirements Document (BRD) | PRD (Product Requirements Document) |
| User story | Feature |
| Story | Feature (or phase, depending on scope) |
| Acceptance Criteria (AC-001 format) | Acceptance criteria (numbered in PRD Section 8) |
| Feature coverage review | PRD interview |
| Deferred Items / Deferred Items List | Parked questions / park-it pattern |
| DI-001 (deferred item ID) | Q[section].[number] — parked |
| Phase 0–9 (BA workflow phases) | Steps in the prd-interviewer skill |
| Phase 2 (Pre-Investigation) | Step 2 — Silent codebase reconnaissance |
| Phase 3 (Business Interview) | Sections 1–5b of prd-interviewer |
| Phase 4 (Deep Edge-Case Interview) | Section 6 — Edge-case phase |
| Phase 5 (Scope Assessment) | prd-completeness-check |
| Phase 7 (Create Deliverables) | Step 4 — Generate PRD draft (P9) |
| Phase 8 (Final Self-Review) | prd-completeness-check assessment |
| Context Gathering | Step 1 — Load the work item |
| Investigation Summary | Step 3 — Set expectations |
| Consistency Report | Context consistency validation output |
| Complexity Classification | Complexity tier |
| Simple / Medium / Complex / Very Complex | Tier 1 / Tier 2 / Tier 3 / Tier 4 |
| Minimum Questions | Minimum question threshold |
| Interview Conclusion Gate | Post-interview verification protocol |
| Demo-Interactive.html | Validation mockup (S4 artifact) |
| Demo-Behavior-Manifest.md | Component Specification (Notion child page) |
| Calculation-Logic-Demo.html | Calculation proof (S4 artifact) |
| Edge-Case-Analysis.md | PRD Section 11 — Edge cases and constraints |
| Scope-Assessment.md | prd-completeness-check report |
| No-Fabrication Rule | Three-tier message text sourcing protocol |
| [TEXT TBD — requires BA/Dev decision] | [TEXT TBD — requires PM decision] (Tier 3) |
| (no BA equivalent) | [Proposed — approved by PM] (Tier 2a) |
| (no BA equivalent) | [PM-provided] (Tier 2b) |
| (no BA equivalent) | [Source: path/to/file.ext:lineN] (Tier 1) |
| Validation Dependencies (VD) | (product-specific — not a SAGE term) |
| PROF_XXX | (product-specific — not a SAGE term) |
| Kendo dialog | (product-specific — not a SAGE term) |
| SCSS variables | (product-specific — not a SAGE term) |
| Tier 1 / Tier 2 styling | (product-specific — not a SAGE term) |
| ADO MCP tools | Linear MCP tools |
| `docs/cursor/BA Requirements/` | Notion PRD space |
| Work Item Assessment | (excluded — SAGE uses empirical data) |
| Ready / Ready with Risks / Not Ready | Score >= threshold / Score < threshold |

---

## Section 5: Proposed File Changes

### Overview

| # | File | Action | Corresponds to | Execution order |
|---|---|---|---|---|
| 1 | `.cursor/skills/prd-interviewer/references/complexity-classifier.md` | CREATE | Addition 1 | 1 |
| 2 | `.cursor/skills/prd-interviewer/SKILL.md` | UPDATE | Additions 1, 2, 3, 4, 5, 6 | 2 |
| 3 | `.cursor/skills/prd-interviewer/references/question-sets.md` | UPDATE | Addition 3 | 3 |
| 4 | `.cursor/skills/prd-completeness-check/SKILL.md` | UPDATE | Additions 5, 7 | 4 |
| 5 | `.cursor/skills/prd-completeness-check/references/scoring-rubric.md` | UPDATE | Addition 7 | 5 |

No new agents. No new hooks. No new hook scripts. No changes to `hooks.json`, `workflow-config.json`, or the session manifest schema.

---

### Change 1: CREATE `.cursor/skills/prd-interviewer/references/complexity-classifier.md`

```markdown
# Complexity Classifier — Feature Complexity Tier Assignment

Reference for prd-interviewer. Use during Step 2 (codebase reconnaissance) to
classify the feature's complexity tier. The tier determines minimum question
thresholds for the main interview and the edge-case interview phase.

---

## How to use

After completing codebase reconnaissance, count the following factors using
the findings from the reconnaissance. Classify using the threshold table.
Record the tier in telemetry and present it to the PM at Step 3 (set
expectations).

---

## Factor Counts

| Factor | How to count |
|---|---|
| Scoped files affected | Count distinct source files (components, services, SPs, views, models) that the feature will create or modify, based on reconnaissance findings |
| Requirements | Count distinct business rules or functional requirements visible in the Linear issue description plus any provided context documents |
| Data entities | Count distinct data models, database tables, stored procedures, and views involved |
| User interactions | Count distinct user-triggered actions (button clicks, form submissions, selections, navigations) visible in the feature scope |
| Stored procedures affected | Count distinct stored procedures that will be created, modified, or whose output is consumed by this feature |
| Cross-component dependencies | Count components outside the feature's primary scope that depend on data produced by this feature, plus components this feature depends on |

---

## Tier Thresholds

| Factor | Tier 1 (Simple) | Tier 2 (Medium) | Tier 3 (Complex) | Tier 4 (Very Complex) |
|---|---|---|---|---|
| Scoped files affected | 1–3 | 4–8 | 9–15 | 16+ |
| Requirements | 1–3 | 4–8 | 9–15 | 16+ |
| Data entities | 1–2 | 3–4 | 5–7 | 8+ |
| User interactions | 1–5 | 6–12 | 13–20 | 21+ |
| Stored procedures affected | 0–1 | 2–3 | 4–6 | 7+ |
| Cross-component dependencies | 0 | 1–2 | 3–5 | 6+ |

**Classification rule:** The feature's tier is the highest tier reached by
any individual factor. If two or more factors reach Tier 3, auto-escalate
to Tier 4.

---

## Minimum Question Thresholds

| Tier | Main interview (P1–P5b) | Edge-case phase (P6) | Total minimum |
|---|---|---|---|
| Tier 1 (Simple) | 10 | 5 | 15 |
| Tier 2 (Medium) | 15 | 8 | 23 |
| Tier 3 (Complex) | 20 | 12 | 32 |
| Tier 4 (Very Complex) | 25 | 15 | 40 |

These thresholds are minimums. The skill should ask as many questions as
needed to fully cover the feature. The thresholds exist to prevent
under-interviewing, not to cap interview depth.

---

## Telemetry

Record the classification as a `prd_complexity_classified` telemetry event
after Step 2 completes:

```json
{
  "event": "prd_complexity_classified",
  "phaseId": "preflight",
  "complexityTier": "tier-3",
  "factors": {
    "scopedFiles": 11,
    "requirements": 9,
    "dataEntities": 6,
    "userInteractions": 14,
    "storedProcedures": 4,
    "crossComponentDependencies": 3
  }
}
```

---

## Recalibration

The tier thresholds and minimum question counts are subject to recalibration
by the skill-effectiveness-evaluator. If the evaluator finds that Tier 2
features consistently produce PRDs that fail completeness check on D3 (edge
cases), it may propose raising the Tier 2 edge-case minimum. Do not hardcode
these values in downstream logic — always read them from this reference file.
```

---

### Change 2: UPDATE `.cursor/skills/prd-interviewer/SKILL.md`

Six insertions into the existing file. Each is specified by its insertion point.

**Insertion 2a — Step 2 output (Addition 1: Complexity Classification)**

Insert after the line `This reconnaissance shapes which questions you ask and how specific your probing can be.` (end of current Step 2), before `### Step 3 -- Set expectations`:

```markdown
### Step 2a -- Classify feature complexity

After reconnaissance, classify the feature's complexity tier using the
classifier in references/complexity-classifier.md. Count the six factors
from the reconnaissance findings and apply the threshold table.

Record the classification tier. It determines the minimum question
thresholds for the main interview and the edge-case phase.

Emit a `prd_complexity_classified` telemetry event with the tier and
factor counts.
```

**Insertion 2b — Step 2b (Addition 2: Context Consistency Validation)**

Insert after the new Step 2a, before `### Step 3 -- Set expectations`:

```markdown
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
```

**Insertion 2c — Step 3 update (Addition 1: Present complexity tier)**

In the existing Step 3 content, insert after the bullet `- What you found in the codebase (brief summary -- 3-4 sentences)`:

```markdown
- The feature's complexity tier and what it means for interview depth
  (e.g., "This is a Tier 3 feature — I will ask at least 32 questions
  across the main interview and edge-case phase")
- Any context consistency issues found (priority interview questions)
```

**Insertion 2d — Section 6 restructuring (Addition 3: Edge-case taxonomy)**

Replace the entire Section 6 block (from `## Section 6 -- Edge cases and constraints (always ask)` through `Q6.7`) with:

```markdown
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

Before concluding the edge-case phase, execute the post-interview
verification protocol (see "After the interview" section). All seven
categories must have been addressed. The PM must explicitly confirm before
proceeding.
```

**Insertion 2e — After the interview update (Addition 4: Conclusion gate)**

Replace the current "After the interview" Step 1 content (from `### Step 1 -- Review parked questions` through `For those that remain parked:`) with:

```markdown
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
```

**Insertion 2f — Constraints section update (Addition 5: No-fabrication rule + Addition 6: Investigation manifest)**

Insert into the existing `## Constraints` section, after the line `- Parked questions must appear as explicit TODO items in the PRD draft, not be silently omitted`:

```markdown
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
```

---

### Change 3: UPDATE `.cursor/skills/prd-interviewer/references/question-sets.md`

Insert a new section at the end of the file, after the existing `## Section 6 -- Edge cases` section:

```markdown
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
```

---

### Change 4: UPDATE `.cursor/skills/prd-completeness-check/SKILL.md`

**Insertion 4a — D3 enhancement (Addition 7: Edge-case category coverage)**

In the existing D3 section, after the line `For Profitability calculation features: also check that return codes -1 through -8 are handled and that the behaviour for each is specified.`, insert:

```markdown
Additionally, for features classified Tier 2 or above (see
prd-interviewer/references/complexity-classifier.md), check that the PRD's
edge cases section covers the applicable edge-case categories:

| Category | Applicable when |
|---|---|
| Interaction sequence | Feature has 2+ user-triggered actions |
| Cascading behaviour | Feature creates or modifies entities referenced by other components |
| Concurrency | Feature modifies shared state (records, configuration, calculations) |
| State boundary | Feature has components with multiple states |
| Cross-component dependency | Feature has upstream or downstream dependencies |
| Data integrity | Feature creates or modifies persistent data |
| Failure and recovery | Feature involves operations that can fail (SP calls, API requests, data writes) |

Deductions:
- Applicable category with zero edge cases documented: -2 per category
- Feature classified Tier 3+ with fewer than 3 applicable categories
  addressed: -5
```

**Insertion 4b — No-fabrication check (Addition 5)**

In the existing D1 section (Requirement coverage), after the deductions list, insert:

```markdown
Message text sourcing check:
- User-facing message text (toast messages, error messages, tooltip text,
  dialog titles and body text, validation messages) that is not sourced
  from the codebase with a file reference and is not marked as
  `[TEXT TBD — requires PM decision]`: -2 per instance
- This check applies to all message text in the PRD requirements section,
  acceptance criteria, edge cases section, and component specification
```

---

### Change 5: UPDATE `.cursor/skills/prd-completeness-check/references/scoring-rubric.md`

Insert a new section after the existing `## D3 -- Return code handling (Profitability-specific)` section:

```markdown
---

## D3 -- Edge-case category coverage (Tier 2+ features)

For features classified at Tier 2 (Medium) or above by the prd-interviewer's
complexity classifier, the PRD's edge cases section (Section 11) must contain
edge cases from each applicable category.

### Applicability rules

Determine which categories apply by examining the feature scope:

**Interaction sequence** applies when the feature has two or more
user-triggered actions that could interact (e.g., filter + operation,
save + navigate, edit + delete).

**Cascading behaviour** applies when the feature creates or modifies an
entity that is referenced by other components, views, or stored procedures
identified in the codebase.

**Concurrency** applies when the feature modifies state that is shared
across users or processes (database records, configuration tables,
calculation results).

**State boundary** applies when the feature includes components that can
be in multiple states (populated/empty, enabled/disabled, running/idle).

**Cross-component dependency** applies when the feature has upstream
data sources or downstream consumers identified in the prd-interviewer's
codebase reconnaissance.

**Data integrity** applies when the feature creates or modifies persistent
data (database writes, configuration changes).

**Failure and recovery** applies when the feature involves operations
that can fail (stored procedure calls, API requests, data writes,
background calculations).

### Scoring

Count the applicable categories and the categories with at least one
documented edge case.

PASS: every applicable category has at least one edge case documented.

Deductions:
- Applicable category with no edge cases: -2 per category
- Tier 3+ feature with fewer than 3 applicable categories addressed: -5 (additional)

### Examples

PASSES D3 edge-case category check:
- A Tier 3 UI feature with documented edge cases in: interaction sequence
  (filter + save), cascading behaviour (entity rename propagation),
  concurrency (simultaneous edit), state boundary (empty grid, disabled
  buttons), cross-component dependency (downstream view refresh), failure
  and recovery (save failure, retry). Six of seven categories addressed.

FAILS D3 edge-case category check:
- A Tier 3 UI feature with three edge cases documented, all in the
  "state boundary" category. Five applicable categories have zero
  edge cases. Deduction: -10 (5 categories × -2) + -5 (Tier 3+ with
  fewer than 3 categories) = -15, which exhausts D3.

---

## D1 -- Message text sourcing (applies to all features)

All user-facing message text in the PRD must either:
(a) be quoted verbatim from the codebase with a source file reference
    in the format `[Source: path/to/file.ext:lineN]`, or
(b) be marked as `[TEXT TBD — requires PM decision]`

Message text includes: toast/notification messages, error messages, tooltip
text, dialog titles and body text, validation messages, status labels.

PASSES:
- "When the save operation fails, the system displays 'Failed to save
  changes. Please try again.' [Source: cost-pools.service.ts:142]"
- "When the allocation completes, the system displays a success message.
  [TEXT TBD — requires PM decision]"

FAILS:
- "When the save operation fails, the system displays 'An error occurred
  while saving your data. Please check your input and try again.'"
  (No source reference and no TBD marker — this text may be fabricated.)

Deductions: -2 per instance of unsourced, un-marked message text.
```

---

## Section 6: Hook Correctness Check

**No hooks are proposed.** All additions in this proposal are at the skill and reference doc layers. No changes to `hooks.json`, no new hook scripts, no modifications to existing hook scripts.

The following structural enforcement question was evaluated and deferred:

**Considered and deferred: A PRD gate hook that blocks the Linear feature issue status transition to Ready unless prd-completeness-check has been run and the score meets threshold.**

Currently, the PRD → Ready transition is instruction-enforced: prd-completeness-check sets the status via Linear MCP only if the score passes. But nothing structurally prevents a human or another agent from setting the status directly.

A hook could enforce this by intercepting the Linear MCP call and verifying the completeness assessment artifact exists and contains a passing score. However:

- The `afterMCPExecution` event type exists in the hook infrastructure (used by telemetry-logger)
- But a blocking hook on `afterMCPExecution` would need to inspect the MCP tool name and arguments to determine whether the call is setting a Linear issue status — this level of MCP payload inspection is not demonstrated in any existing hook script
- The existing hooks operate on file-system state (artifact existence, manifest fields), not on MCP call content
- Adding MCP content inspection to the hook layer is a design extension that should be evaluated as a separate framework capability, not as a side effect of this integration

**Recommendation:** Defer the PRD gate hook until the framework has a demonstrated pattern for MCP-content-aware hooks. The current instruction enforcement is adequate for the team's scale, and the prd-completeness-check skill has strong self-enforcement (it only sets Ready on pass, and its behaviour is observable in telemetry).

---

## Uncertainty Flags

**Flag 1 — Complexity tier naming.** This proposal uses Tier 1–4 instead of Simple/Medium/Complex/Very Complex. The BA documents use the word-based names. SAGE does not have an established convention. The tier numbering is proposed because it is machine-readable and unambiguous, but the team may prefer word-based names. This is a cosmetic decision with no structural impact — either works.

**Flag 2 — Edge-case category D3 weighting.** The proposed D3 deductions (-2 per missing category, -5 for Tier 3+ under-coverage) are initial estimates. The first few PRDs assessed under this rubric will reveal whether these values are too aggressive or too lenient. The skill-effectiveness-evaluator should be allowed to recalibrate within the first 3-5 assessments.

**Flag 3 — Investigation manifest scope.** The proposed investigation manifest lists every file read during recon. For large features, this list could be very long (50+ files). The telemetry event may need a size limit or summarisation strategy. This is a practical concern that should be resolved during the first implementation, not specified in advance.

**Flag 4 — No-fabrication enforcement depth.** The proposed no-fabrication check in prd-completeness-check requires the scorer to read codebase files to verify that quoted text matches the source. This is feasible (the skill has codebase read access) but adds execution time. If this proves too slow in practice, the check could be relaxed to verify only that the source reference format is present (not that the text matches), with full verification deferred to the traceability reviewer at S3.
