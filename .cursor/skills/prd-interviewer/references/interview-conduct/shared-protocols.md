# Interview Conduct — Shared Protocols

Reference for `prd-interviewer`. Self-contained — no external skill
references. This file is the master operating-principles document the
coordinator (`SKILL.md`) loads once at startup. Every per-phase module in
`interview-conduct/` references this file for cross-phase rules; phase
modules never inline these rules.

This file encodes:

- L5 — Inputs & Preconditions (consolidated Step 0 readiness checks;
  hard-stop vs override-eligible matrix).
- L6 — Operating principles — all **14 binding families A–N**, including
  the 8 sub-rules of Family N (handoff-chat read discipline).
- L11 — Failure modes — **5-category taxonomy A–E** with every additive
  row from the L1–L12 lock.
- ABORT path (with the 3 L11 Q2=2b tightenings).
- Re-entry rules after ABORT / REJECT / REDIRECT / pause-resume / PM edit.
- Backfill-on-touch migration policy + pre-lift bundle detection rule.
- Operational scaffolding the coordinator and phase modules invoke:
  context checklist gate, investigation summary, phase tracker, restart
  command, Unified Deferred Items List, recommendation/challenge
  behaviour, comprehensive self-review gates table.

---

## L5 — Inputs & Preconditions (consolidated at Step 0)

Step 0 consolidates **every** readiness check at a single point. No
deferred readiness checks anywhere downstream — if Step 0 passes (or is
overridden with reduced-fidelity markers), the interview proceeds; if it
hard-stops, no further phase runs.

### L5.1 — Hard-stop categories (no override possible)

Each of these hard-stops emits `prd_interview_hard_stopped` with the
matching `hardStopReason` enum value:

- **Breakdown file missing or unparseable** (L11 B1 — widened from
  "missing" to also cover unparseable).
- **Sub-PRD ID not in breakdown** (L11 B2).
- **Not on the required branch** (per `workflow-config.json`; default
  `master`).
- **Git working tree dirty in interviewer-scoped paths**
  (`.sage/prds/[FEATURE_ID]/[sub-prd-id]/` plus this skill's references
  folder).

### L5.2 — Override-eligible categories (PM acknowledges, telemetry logged)

Each override emits `prd_interview_override_applied` with
`{ overrideType, justification, subPrdId }`. If accepted, the PRD carries
a **reduced-fidelity marker** per Family K K2.

- **Component Pattern Summaries empty/thin** (L11 B3) →
  `overrideType: 'thin_pattern_summaries'`.
- **Component manifest stale** (L11 B4) → `overrideType: 'manifest_stale'`.
- **Cited component YAML missing from disk** (L11 B5) →
  `overrideType: 'yaml_missing'`. Affected component falls back to PM-led
  description (no Component Pattern Block delta-questioning for that
  component).
- **Breakdown citations stale en masse** (L11 B9) →
  `overrideType: 'many_citations_stale'`.
- **Telemetry sink unavailable** (L11 D4 / E4) →
  `overrideType: 'telemetry_sink_unavailable'`. Interview continues to
  the fallback path; PM warned at moment of fallback.

### L5.3 — Bound rules

- **Legacy master breakdown fallback is dropped.** Only per-sub-PRD
  breakdown files (`prd-breakdown.[sub-prd-id].md`) are valid.
- **PM session model.** One PM end-to-end; pause-resume allowed; 14-day
  staleness warning on resume (Family L L1).
- **Pre-existing artifact archival policy.** Always archive the prior
  bundle to `_archive/[timestamp]/` before re-interview begins. Never
  delete the prior bundle implicitly.

---

## L6 — Operating principles (14 binding families A–N)

These 14 families are the binding behavioural contract. Every per-phase
module assumes they hold. Each family carries verbatim sub-rules; do not
paraphrase when enforcing.

### Family A — Question discipline

- A1 Predicate-based phrasing (verifiable yes/no or enumerated answer;
  never "is this OK?").
- A2 Batch 2–4 questions per turn; never dump a whole section as a list.
- A3 No redundant questions — check `interview-answers.json` before
  asking.
- A4 No leading questions.

### Family B — Verbatim recording

- B1 PM answers recorded verbatim in `interview-answers.json`.
- B2 Never summarise during interview.
- B3 Interviewer interpretation goes into the PRD only, never into
  `interview-answers.json`.

### Family C — Deferred Items List

- C1 Single Unified Deferred Items List per interview (DI-NNN sequential
  across the whole interview).
- C2 Statuses: `Open` / `Accepted` / `Closed`.
- C3 No `Open` items past the single conclusion gate.

### Family D — Conclusion gates

- D1 Every phase has a conclusion gate (self-review then PM gate where
  applicable).
- D2 PM responses at the **single conclusion gate** and at the **P7
  final approval**: APPROVE / REJECT / REDIRECT.
- D3 REJECT triggers restart-of-phase.
- D4 REDIRECT can rewind to any earlier phase (with restart of dependent
  phases).

### Family E — No mid-interview recon

- E1 Interviewer NEVER re-opens YAML files mid-interview.
- E2 Only `prd-orchestrator` runs recon.
- E3 Recon gaps are recorded as DI with category `breakdown-defect`. At
  the single conclusion gate, PM decides: accept into §7 Open Items,
  hard-stop and re-run orchestrator, or PM supplies missing information
  with tracking entry.

### Family F — Three-tier message text sourcing

- F1 Tier 1: exact text from cited YAML / source.
- F2 Tier 2: PRD outcome phrasing, PM-approved.
- F3 Tier 3: interviewer-drafted, marked as such, PM-approved before
  write.

### Family G — Self-review gates

- G1 (L1) Self-review after each phase before PM sees the conclusion
  gate. Emits `prd_self_review_gate_failed` on failure with
  `gateLevel: 'L1'`.
- G2 (L3) Coverage-dimension blocking — no required coverage dimension
  below 100% without DI tracking. Failure emits
  `prd_coverage_dimension_blocked`.
- G3 (L5) Pre-write artifact-bar walk — every Pass Condition in
  `production-grade-quality-bar.md` met BEFORE any file write. On
  failure: interviewer does NOT write; surfaces failing condition;
  resolves gap; retries. Emits `prd_pre_write_bar_walk_failed`.

### Family H — Closure & thoroughness

- H1 No phase exits with unanswered required questions.
- H2 No silent skipping of edge cases.
- H3 No quitting early to save tokens.

### Family I — Telemetry resilience

- I1 Telemetry write failure NEVER fails the interview.
- I2 Fallback path is `.sage/prd-interview-telemetry.local.jsonl`. PM
  warned at moment of fallback. Emits `prd_telemetry_write_failed`.

### Family J — Anti-hallucination

- J1 No invented patterns from training data.
- J2 Every UI / data assertion traceable to a cited YAML or a PM answer.
- J3 If unsure: ask PM, never assume.

### Family K — Production-grade bar

- K1 Bundle MUST pass `production-grade-quality-bar.md` Pass Conditions
  BEFORE any final `prd.md` write (enforced by G3).
- K2 Reduced-fidelity markers REQUIRED when an L5 override was applied.
  The marker appears in PRD §6 (Risks) and §8 (Related Artefacts version
  history).

### Family L — Pause-resume staleness

- L1 If interview pauses >14 days, on resume confirm context still fresh
  with the PM. Emits `prd_interview_resumed_with_staleness_warning`.
- L2 Stale context triggers phase restart.

### Family M — Application-fidelity (cross-cuts handoffs)

- M1 When a production UI affordance exists, the brief MUST cite the
  relevant component YAML(s) under `.context/components/`.
- M2 Brief author enumerates EVERY YAML the handoff will need BEFORE the
  brief is finalised.
- M3 "No application equivalent" must be flagged explicitly in the brief
  as `no application equivalent — generator's choice`, with palette/tone
  bounds.

### Family N — Handoff-chat read discipline (8 sub-rules)

Family N is the major Phase 5 addition. It is the binding contract that
prevents summarised reads, fabricated content, and silent gaps inside the
three manual handoff chats (demo, sample-data, component-spec).

- N1 Brief Section 3 (the YAML reading list) is structured as
  `{ path, read_mode, expected_anchors }` per YAML. Default
  `read_mode: "full"`. `expected_anchors` is a short list of read-proof
  data points the handoff chat must extract verbatim (e.g. "third state
  name", "empty-state copy string verbatim", "count of action buttons",
  "YAML `version:` header value"). Anchors are read-proof tokens — they
  cannot be guessed without actually opening the YAML.
- N2 Every handoff `_summary.md` carries a new `## YAML reads` H2 with a
  table of the form:

  ```
  | path | read_mode | anchors_extracted |
  | .context/components/grid-edit-mode.yaml | full | states: [read, edit, dirty]; empty_copy: "..."; action_buttons_count: 4 |
  ```

- N3 Interviewer post-return verification opens **only the YAML files**
  (NOT the heavy artifact) and matches each `anchors_extracted` value
  against the YAML text. Mismatch → re-handoff with brief amendment.
  Emits `prd_anchor_verification_failed` with `mismatchType`.
- N4 Brief Section 9 (Hard constraints) explicitly prohibits summarised
  reads: "You MUST read every file in Section 3 end-to-end. No
  summarisation, no skimming, no inferring."
- N5 Handoff prompts in `handoff-prompt-templates.md` restate the read
  discipline in their Hard rules block (redundancy at the gate is
  correct). Plus a **random spot-check on PM return**: the interviewer
  randomly opens one or more artifact rows to confirm against the cited
  YAML.
- N6 The Tier 1 inside-chat self-review checklist in every brief gains
  this item per surface: "(c) For every file in Section 3, you have read
  it end-to-end and extracted every anchor named in `expected_anchors`.
  The anchors table in `_summary.md` is populated with verbatim values."
- N7 Read discipline applies to all three surfaces. Sample-data handoff
  chats verify schemas; component-spec handoff chats verify YAMLs; demo
  handoff chats verify both.
- N8 Brief pre-extraction discipline: the interviewer **pre-extracts**
  cited YAML content into brief Sections 6 / 7 / 8 during authoring at
  P9, using the in-memory YAML state captured at P5 closure. The handoff
  chat reads brief end-to-end + targeted anchor confirmations only. The
  heavy YAML read is paid ONCE, by the chat that already has them in
  memory.

---

## L11 — Failure modes (5-category taxonomy A–E)

Every failure mode below is additive — pre-existing rows are preserved,
new rows are inserted. Categories are: A PM-side · B Recon-side ·
C Handoff-chat-side · D Interviewer-side · E Infrastructure.

### Category A — PM-side

- A1 PM cannot answer → defer to Unified DI list with status `Open`.
- A2a PM disagrees with breakdown, recon wrong → hard-stop, PM re-runs
  `prd-orchestrator`.
- A2b PM understanding updated mid-interview → record verbatim in
  `interview-answers.json` and continue.
- A3 Contradictory PM answers across phases → flag inline at the moment
  of contradiction, PM picks which stands, record resolution verbatim.
- A4 PM silent >14 days during pause-resume → on resume confirm context
  fresh (Family L L1). Stale → restart phase per L2.
- A5 PM REJECT at conclusion gate or final approval → identify scope to
  revisit. Restart command runs.
- A6 PM REDIRECT → may require restart from P1 (scope changed) or named
  phase (scope unchanged).
- A7 PM answer breaches `production-grade-quality-bar.md` → interviewer
  surfaces the failing Pass Condition, asks PM to refine or mark as DI
  with reason.

### Category B — Recon-side

- B1 Breakdown file missing or unparseable → hard-stop at Step 0.
- B2 Sub-PRD ID not in breakdown → hard-stop at Step 0.
- B3 Component Pattern Summaries empty/thin → override-eligible at
  Step 0; PRD carries reduced-fidelity marker (Family K K2).
- B4 Component manifest stale → override-eligible.
- B5 Cited YAML missing from disk → override-eligible; affected
  component falls back to PM-led description (no Component Pattern
  Block delta-questioning for that component).
- B6 Mid-interview recon gap discovered (interviewer does NOT patch by
  re-reading — Family E E1) → record as DI category `breakdown-defect`.
  At the single conclusion gate, PM decides: accept into §7 Open Items,
  hard-stop and re-run orchestrator, or PM supplies missing information
  with a tracking entry.
- B7 Genuinely new concept doesn't fit any §4 sub-section → interviewer
  flags inline. At the single conclusion gate, PM picks: fold into the
  closest existing sub-section, add a custom requirement section, or
  mark out-of-scope. Recurring patterns trigger future L4 schema
  amendment.
- B9 Breakdown citations stale en masse → override-eligible at Step 0;
  PRD carries reduced-fidelity marker.

(B8 is intentionally absent in the L11 numbering; do not back-fill.)

### Category C — Handoff-chat-side

- C1 Deviations PM rejects → re-handoff per
  `sub-agent-delegation.md` §8 with brief amendment in place.
  Interviewer re-runs Family N anchor verification. Emits
  `prd_handoff_re_run` with `rerunReason: 'deviation_rejected'`.
- C2 Family N anchor verification fails on PM return — decision
  criterion:
  - **Structural mismatch** → tighter brief, re-handoff.
  - **Copy mismatch** → re-handoff with brief amendment (verbatim copy
    added to Section 6).
  - **YAML-vs-PM contradiction** → escalate to orchestrator.
  - **Cosmetic** → accept into PRD §7 Open Items.
  Emits `prd_anchor_verification_failed` with the matching `mismatchType`
  and the chosen `resolution`.
- C3 Invented content not in any cited YAML / brief Section 6 → Family N
  anchors catch some; the N5 spot-check catches the rest. Re-handoff
  with brief amendment flagging invented content as out-of-bounds.
- C4 Extra files outside declared outputs → brief Section 9 forbids;
  interviewer detects extra files in the surface directory, surfaces as
  a deviation, re-handoffs. Emits `prd_handoff_re_run` with
  `rerunReason: 'extra_files'`.
- C5 Handoff times out / PM never opens chat → no event detection; PM
  returns and reports. If PM forgets, no progress. After the staleness
  threshold, PM is prompted; if not done, PM is responsible for either
  running the handoff or aborting the bundle.
- C6 Handoff proposes follow-ups in chat rather than STOP-ping →
  recorded in the summary's `## Open questions` H2, ignored in chat.
- C7 Handoff summary schema non-conforming (missing required H2,
  malformed YAML reads table, missing `prdHash`) → re-handoff with a
  brief amendment that pastes the summary contract verbatim. Emits
  `prd_handoff_re_run` with `rerunReason: 'summary_schema_invalid'`.
- C8 Recurring re-handoffs (same surface > 2 re-handoffs) → escalate to
  `prd-orchestrator`; investigate breakdown defect; PM may accept
  deviation into PRD §7 with stated reason.

### Category D — Interviewer-side

- D1 L6 G1 self-review gate fails → surface failure to PM with the
  failed item. PM provides input (gate re-runs) or accepts as DI.
- D2 L6 G2 coverage-dimension blocking gate fails → targeted questions
  to close dimension. If PM cannot close, dimension shortfall becomes
  DI with status `Accepted`; PRD §7 reflects it.
- D3 L6 G3 pre-write artifact-bar walk fails → interviewer does NOT
  write. Surfaces failing Pass Condition. PM resolves underlying gap.
  Retry.
- D4 Telemetry sink unavailable → never fail the interview. Log to
  `.sage/prd-interview-telemetry.local.jsonl`, warn PM, continue.
- D5 `prdHash` computation fails on derivative write → derivative
  written with `prdHash: '[COMPUTATION_FAILED]'` header.
  `prd-stale-check` treats this exact string as MISSING and prompts
  regeneration.
- D6 Family J anti-hallucination breach detected (interviewer asserted
  something not in YAML or PM answer) → interviewer retracts the
  assertion, asks PM, records resolution.
- D7 Family E mid-interview recon breach detected (interviewer
  re-opened a YAML mid-interview) → halt phase, log telemetry, ask PM
  whether to continue with the recon result accepted or restart phase
  clean.

### Category E — Infrastructure

- E1 Branch state changes mid-interview → detect, prompt PM to restore
  branch (continue) or accept override (continue with new context).
- E2 File write fails (disk, permissions) → surface with affected
  path; no silent retry; PM resolves.
- E3 `.sage/workflow-config.json` missing or malformed → fall back to
  documented defaults, warn PM. Emits `prd_workflow_config_defaulted`.
- E4 Telemetry JSONL corrupted → rename to
  `.sage/prd-interview-telemetry.[timestamp].corrupt.jsonl`, start
  fresh, log `prd_telemetry_corruption_recovered`.
- E5 File permissions changed mid-interview → surface affected paths,
  PM resolves before write attempts continue.

---

## ABORT path (with 3 tightenings from L11 Q2=2b)

When the PM (or the coordinator on PM direction) aborts an interview:

1. Emit `prd_interview_aborted` telemetry with
   `{ subPrdId, prdRunId, reason, phaseId_at_abort, deferredItemsCount }`.
2. Move the partial bundle — **including `interview-answers.json`** —
   to `.sage/prds/[FEATURE_ID]/[sub-prd-id]/_archive/aborted_[timestamp]/`.
3. **Delete the sub-PRD folder afterwards** (not just leave it empty)
   so a fresh interview begins from a clean slate. The `_archive`
   subdirectory survives at the parent feature level — the deletion
   target is the per-sub-PRD working directory whose contents were just
   archived.
4. **Pre-Step-0 abort exception.** A pre-Step-0 abort (the interview
   never reached the L5 readiness checks) emits the event with
   `phaseId_at_abort: 'pre-Step-0'` but skips the archive move and the
   folder delete (nothing was written yet; nothing to archive).
5. PM is told the abort reason, the archive location (when applicable),
   and what would need to change before re-attempting.

The three tightenings (relative to the legacy ABORT path) are:

- The archive move explicitly captures `interview-answers.json` so
  that the verbatim PM answer record is preserved across the abort.
- The sub-PRD folder is **deleted** (not just emptied) after the
  archive move, so a fresh re-interview begins from a clean slate.
- Pre-Step-0 aborts are handled distinctly — event emitted, archive
  skipped — so the telemetry signal for "abort before readiness
  checks" is captured cleanly.

---

## Re-entry rules

- **After ABORT** → fresh interview from Step 0. The archived bundle is
  not consulted unless the PM explicitly restores it.
- **After REJECT at the single conclusion gate** → restart named
  phase(s); downstream phases re-run if dependent on the rejected
  scope.
- **After REJECT at P7 final approval** → restart any/all phases; PM
  may choose to restart from P1.
- **After PM pause >14 days** → staleness confirmation on resume
  (Family L L1). PM may continue or restart any/all phases.
- **After post-completion PM edit to `prd.md`** → `prd-amend` flow
  takes over (not the interviewer); `prd-stale-check` classifies each
  derivative; `prd-amend` writes diff briefs only for STALE surfaces.

---

## Backfill-on-touch migration policy

- Pre-lift sub-PRDs continue with their existing layout until next
  touched.
- On next touch, the bundle migrates fully: PRD rewritten against the
  8-section schema; AC IDs renumbered from `AC-{REQ|EC|UI|ERR}-NNN` to
  sequential `AC-NNN` with the `surface` field added; `prdHash` headers
  added to all derivatives; `bundle-manifest.json` written.
- Downstream consumers carry dual-layout read logic (old bucketed vs new
  sequential) until every active sub-PRD has been touched once
  post-lift; then the dual-logic is removed.
- Migration is recorded in PRD §8 Related Artefacts version history with
  full-name author + date + "backfill-on-touch migration" change
  summary.
- The migration itself emits `prd_interview_override_applied` with
  `overrideType: 'pre_lift_migration'` and
  `justification: 'backfill_on_touch'`.

### Pre-lift bundle detection rule (Step 0 routes correctly)

A bundle is treated as **pre-lift (legacy)** if ANY of these are true:

1. `prd.md` has no YAML frontmatter block (no `---` delimiters at top),
   OR
2. `prd.md` frontmatter is present but does not contain a `prdHash`
   key, OR
3. `acceptance-criteria.md` does not exist as a sibling file (legacy
   bundles embedded AC inside `prd.md`), OR
4. `acceptance-criteria.md` contains any AC ID matching the legacy
   bucketed pattern `AC-(REQ|EC|UI|ERR)-\d+`, OR
5. `bundle-manifest.json` does not exist.

A bundle is treated as **new-format (post-lift)** ONLY if **all** of the
above are false.

Step 0 detects bundle format BEFORE the L5 readiness checks run. If
pre-lift is detected AND the PM has invoked `prd-interviewer` for
amendment, the interviewer first runs the migration (rewrite PRD against
8-section schema, extract AC into sibling, renumber AC IDs, add prdHash
headers, write `bundle-manifest.json`) and emits the
`pre_lift_migration` override event. After migration succeeds, the
new-format bundle is the entry state for the rest of the interview.

---

## Context checklist gate

Before any silent investigation, confirm the PM has provided everything.
Present this checklist explicitly and wait for confirmation before
proceeding to Step 0's L5 readiness checks.

**Present to the PM:**

> "Before I begin, I want to make sure I have everything relevant. Please
> confirm whether you have any of the following:
>
> 1. The ADO work item or Linear issue ID for this sub-PRD — provided?
> 2. Any additional context documents (specs, meeting notes, prior PRDs)?
> 3. Any HTML mockups, wireframes, or visual references?
> 4. Any related user stories or parent feature references?
> 5. Any tribal knowledge or verbal decisions that should be captured now?
> 6. Any existing demos or recordings of current application behavior?
> 7. Anything that has changed since the orchestrator ran the breakdown?
>
> Please confirm 'I've provided everything' when ready, or share anything
> you haven't yet."

**Rules:**

- Do NOT proceed to component matching or interview until the PM
  confirms.
- If the PM says they have something but has not provided it yet, wait.
- Store all provided materials in the running context for use during the
  interview.

---

## Investigation summary

After reading the breakdown and running component intelligence matching,
present a structured investigation summary to the PM **before** the first
interview question. This replaces showing raw technical findings —
everything is translated into business language.

**Format:**

> "Here is what I found about this sub-PRD before we begin:
>
> **Feature area:** [2–3 sentences in plain business language — which areas
> are affected, what kind of change this is, which user workflows are
> touched.]
>
> **Complexity:** This is a Tier [N] sub-PRD — [plain language meaning:
> e.g., 'a focused change with a small number of business rules and one
> affected workflow; the interview will be 15–25 minutes.']
>
> **Existing patterns I'll assume apply:** [For each matched component: one
> sentence describing the pattern the interviewer will treat as the default.
> E.g., 'The allocation rules grid follows the standard
> empty/loading/data-loaded pattern with row-level expand.']
>
> **Questions I need to ask before we start:** [List any context consistency
> issues from the breakdown as explicit pre-interview questions.]
>
> Any corrections to the above before we begin?"

The PM's corrections at this stage are recorded and update the internal
context before the first phase.

---

## Phase tracker

Maintain and display phase completion status on demand.

### Status display format

When the PM requests status (triggers: "where are we", "show progress",
"interview status", "phase status", "what section are we on"), respond
with:

```
Step 0  Repo preflight                       [DONE]
P1      Feature & capability                 [DONE]
P2      Scope boundaries + §4 coverage map   [DONE]
P3      Calculation                          [SKIPPED — not applicable]
P4      Allocation                           [SKIPPED — not applicable]
P5      UI & UX + anchor extraction          [IN PROGRESS]  <-- current
P6      Edge cases                           [NOT STARTED]
Gate    Single conclusion gate               [NOT STARTED]
P7      Final approval                       [NOT STARTED]
P8      PRD draft + AC derivation            [NOT STARTED]
P9      Handoff briefs + on-return validation [NOT STARTED]

Coverage status:
  §4 sub-section coverage map (declared at P2):
    DM 2/2 | CL N/A | AL N/A | WF 1/1 | UI 3/5 | VC 2/2 | ER 1/2
    NM N/A | PA 1/1 | IN N/A | PF 0/1 | AU 1/1 | RX N/A | CP 1/2
  D-EC        Edge-case categories:    0/7 (not yet started)
  D-SCOPE     Out-of-scope explicit:   satisfied
Deferred items: [N] open
Next gate: [description]
```

Mark each phase: `[DONE]`, `[IN PROGRESS]`, `[SKIPPED — not applicable]`,
or `[NOT STARTED]`. Indicate current with `<-- current`.

---

## Restart command protocol

**Triggers:** "restart this section", "redo Section [N]", "start this
section over", "restart P[N]"

**Protocol:**

1. **Confirm:** "Restart [Phase name]? This discards all answers
   captured during this phase."

2. **Check downstream:** If any phases AFTER the requested phase have
   been started, warn:
   > "Phases [list] were built using context from this phase. Would you
   > like to:
   > (a) Reset only this phase — downstream phases keep their current
   >     data
   > (b) Reset this phase and all after it
   > (c) Cancel"

3. **On confirm:** Reset phase status to `[NOT STARTED]`. Discard that
   phase's answers from the running record. Re-enter from its first
   question batch.

4. **Telemetry:** Emit `prd_phase_started` again for the restarted
   `phaseId`. Emit `prd_phase_rejected` with `restartPhaseId` if the
   restart was driven by a REJECT at the single conclusion gate.

---

## Unified Deferred Items List

When the PM cannot or chooses not to answer a question, add it to the
Deferred Items List with structured tracking.

**Fields:**

| Field | Value |
|-------|-------|
| ID | `DI-001`, `DI-002`, … (sequential across the entire interview) |
| Original question | The category and text of the question |
| Phase deferred from | Step 0 / P1–P9 |
| Category | `feature-definition` / `scope` / `calculation` / `allocation` / `ui` / `edge-case` / `ac` / `breakdown-defect` |
| PM reason | Verbatim reason given (or "No reason given") |
| Status | `Open` / `Accepted` / `Closed` |

**When deferring, say:**

> "I'm recording this as deferred item DI-[N]: [topic]. I'll surface it
> again at the conclusion gate. You can resolve it then or accept it as
> a gap in the PRD draft."

**Status definitions:**

- **Open** — not yet addressed; will be surfaced at the next conclusion
  gate.
- **Accepted** — PM acknowledges the gap and accepts it will appear in
  PRD §7 Open Items & Ambiguities.
- **Closed** — PM provided the answer; the item is recorded against the
  appropriate §4.NNN entry and removed from the open list.

**Rule (Family C C3):** After the single conclusion gate, no items may
remain `Open`. Every item must have a terminal status (`Accepted` or
`Closed`).

---

## Recommendation and challenge behaviour

### When to recommend

- A requirement is stated but an existing pattern already satisfies it —
  surface the pattern (from the breakdown's Component Pattern Summary)
  and ask for confirmation rather than re-asking the PM to describe it
  from scratch.
- A genuine gap is identified that the PM may not have considered —
  offer a concrete suggestion grounded in existing application
  behaviour (cited via the breakdown).
- Example: "Based on other grids in the application, I'd expect this to
  support an empty-state message when no rules are configured and a
  separate filtered-empty message when the filter hides all results.
  I'll capture that as the default — let me know if you want it to
  behave differently."

### When to challenge

- The PM's answer deviates from an established pattern and no reason
  has been given — ask why (mandatory challenger pattern at P6
  per-category — see `phase-P6.md`).
- An answer would likely cause a cross-page issue or data integrity
  problem.
- The PM confirms something should match an existing pattern, but that
  pattern has a known limitation captured in the breakdown.
- Example: "That would behave differently from how this is handled on
  the Allocation Rules page — is that intentional, or would you like
  consistency?"

### When to stay silent

- The answer is clear and consistent with existing patterns.
- The recommendation is trivial or obvious.
- The challenge is pedantic rather than substantive.

**Frequency rule:** Do not challenge or recommend on every answer.
Over-use frustrates the PM and slows the interview. Apply judgment: the
bar for challenging is "would this cause a genuine problem?" and for
recommending is "does the app already provide the answer?"

---

## Comprehensive self-review gates

Every step and deliverable has a mandatory self-review gate before
proceeding. Gates are enforced by Family G (G1 / G2 / G3). There are no
exceptions.

| Step | What is reviewed before proceeding |
|---|---|
| After reading `investigation_context` from breakdown | Verify context is sufficient to begin. If any required area is missing, record as DI with category `breakdown-defect` (per Family E E3) — do NOT re-open YAMLs to patch the gap. |
| After context checklist with PM | Verify all PM-provided materials have been read and reconciled with breakdown findings. |
| After presenting investigation summary | Verify the business-language summary is accurate, does not contain technical terms (SP names, view columns, class names), and reflects the breakdown context correctly. |
| After each interview phase (G1 — L1) | Verify no requirement area in that phase was left vague or deferred without a DI tracking entry. Every answer that was short, unclear, or covered a topic known to be relevant must have either been probed to sufficient depth or deferred to the list. Emit `prd_self_review_gate_failed` on failure with `gateLevel: 'L1'`. |
| Coverage-dimension blocking (G2 — L3) | No required coverage dimension below 100% without a DI tracking entry. Emit `prd_coverage_dimension_blocked` on failure. |
| At the single conclusion gate | Run the full 6-step protocol from `phase-P6-to-P7-gate.md`. Verify the §4 coverage map declared at P2 reconciles against what was actually captured P1–P6. Do not proceed with any required dimension unsatisfied or any DI item still `Open` (Family C C3). |
| At P7 final approval | Walk the L6 closure rules (calculation closure for CL-NNN, allocation closure for AL-NNN, state closure for WF-NNN, permission/validation closure for PA/VC). Plain-language §4-structured summary presented to PM. APPROVE / REJECT / REDIRECT. |
| Pre-write artifact-bar walk (G3 — L5) | Before each interviewer-authored artifact (`prd.md`, `acceptance-criteria.md`, `reuse-map-draft.md`, `component-pattern-confirmation.md`) is written, walk every Pass Condition in `production-grade-quality-bar.md`. On failure: do NOT write; surface the failing Pass Condition; resolve the gap; retry. Emit `prd_pre_write_bar_walk_failed`. |
| After PRD draft is written | Self-check against the 8-section schema. Every §4 sub-section in the P2 coverage map either has at least one §4.NNN entry OR carries `Not applicable — [reason]`. Every AC links to ≥1 §4.NNN; every §4.NNN links to ≥1 AC. Fix all failures before proceeding to handoff briefs. |
| After component spec is written (handoff return) | Verify no requirement appears only in the component spec — every requirement must also be in the PRD. Verified by reading the component-spec `_summary.md` only (full artifact spot-checked per Family N N5). |
| After demo handoff returns | Family N N3 anchor verification: open ONLY the cited YAMLs (not the demo HTML); match each `anchors_extracted` value verbatim. Family N N5 spot-check: randomly open one or more artifact rows to confirm against the YAML. Emit `prd_anchor_verification_failed` on mismatch. |
| After sample-data handoff returns | Same Family N N3 + N5 protocol applied to cited schemas / YAMLs. |
| After component-spec handoff returns | Same Family N N3 + N5 protocol applied to cited component YAMLs. |
| Final check before bundle finalisation (end of P9) | Confirm every deliverable for this sub-PRD has been produced. Confirm no PRD section has placeholder text, TBD sections without DI tracking entries, or blank sub-sections. Finalise `bundle-manifest.json`. Emit `prd_bundle_manifest_finalised` then `prd_interview_completed`. |
