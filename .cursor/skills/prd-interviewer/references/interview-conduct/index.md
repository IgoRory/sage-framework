# Interview Conduct — Index

Reference for `prd-interviewer`. Self-contained — no external skill
references.

This folder holds the operating-principles file and the per-phase
modules for the L1–L12 interview model. The `prd-interviewer` SKILL.md
coordinator loads `shared-protocols.md` once at startup, then loads
only the active phase module at each transition. Phase modules never
read each other.

---

## Canonical phase sequence (L8 lock)

```text
Step 0  Repo preflight + L5 readiness checks (consolidated)
P1      Feature & capability                            — always
P2      Scope boundaries + §4 coverage map declaration  — always
P3      Calculation                                     — conditional (trigger: breakdown indicates calculation)
P4      Allocation                                      — conditional (trigger: breakdown indicates allocation)
P5      UI & UX + Performance + Family N anchors        — conditional (trigger: breakdown indicates UI)
P6      Edge cases (7 categories, mandatory challenger) — always
Gate    Single conclusion gate                          — 6-step protocol, §4 coverage reconciliation
P7      Final approval (plain-language summary by §4)   — always
P8      PRD draft + AC derivation + reuse map           — always
P9      Handoff briefs + on-return validation + traceability + bundle-manifest.json finalisation
```

Step 0 lives in `shared-protocols.md` (L5 — Inputs & Preconditions) and
is invoked by the coordinator before P1; the P1 module's preamble
references the L5 gate explicitly. The single conclusion gate
**collapses** the legacy P6→P7 and P7→P8 two-gate pattern into one
gate after P6 (file: `phase-P6-to-P7-gate.md`); the legacy
`phase-P7-to-P8-gate.md` is removed.

---

## Files in this folder

| File | Phase / Gate | Summary |
|---|---|---|
| [`shared-protocols.md`](./shared-protocols.md) | All phases | L5 Step 0 preconditions · L6 Families A–N (with Family N N1–N8 handoff read discipline) · L11 5-category failure taxonomy · ABORT path · re-entry rules · backfill-on-touch migration · pre-lift bundle detection · context checklist · investigation summary · Unified Deferred Items List · comprehensive self-review gates table. |
| [`phase-P1.md`](./phase-P1.md) | P1 — Feature & capability | Step 0 preamble pointer · feature identity · change-type enumeration (multi-classification) · role baseline delta question · DM-NNN + PA-NNN in-flow seeds · one-sentence capability statement hard depth-bar · 4-item P1 self-review. |
| [`phase-P2.md`](./phase-P2.md) | P2 — Scope boundaries | Entity in/out scoping (DM-NNN reconciliation) · adjacent-area in/out · six-category downstream consumer check · CP-NNN in-flow · **§4 sub-section coverage map declared at P2 exit** (locks which conditional phases trigger) · 4-item P2 self-review. |
| [`phase-P3.md`](./phase-P3.md) | P3 — Calculation (conditional) | Trigger predicate: breakdown indicates calculation. Worked-example mandate (4 parts) · five pre-enumerated exclusion classes · CL-NNN in-flow with breakdown closure check · seven cross-cutting sub-batches (VC/PA/NM/AU/WF/IN/PF predicate triggers) · closure-rule walk per metric. |
| [`phase-P4.md`](./phase-P4.md) | P4 — Allocation (conditional) | Trigger predicate: breakdown indicates allocation. Worked-example mandate (6 parts including driver, scope, source/target pools, exclusions, fractional-remainder) · four pre-enumerated allocation patterns · AL-NNN in-flow with breakdown closure check · seven cross-cutting sub-batches calibrated for allocation · closure-rule walk per allocation rule. |
| [`phase-P5.md`](./phase-P5.md) | P5 — UI & UX (conditional) | Trigger predicate: breakdown indicates UI. Full surface map (D-COMP / D-DETAIL / D-CROSS) · performance budget questions absorbed here (PF-NNN) · CP-NNN per cross-page impact · WF-NNN per state transition · Family N anchor extraction at P5 closure · Component Pattern Confirmation Report authored at end of P5. |
| [`phase-P6.md`](./phase-P6.md) | P6 — Edge cases (always) | Seven categories (interaction sequence · cascading · concurrency · state boundary · cross-component · data integrity · failure & recovery) · each outcome maps to §4 sub-section ID · **mandatory challenger pattern per category** · 4-item P6 self-review. |
| [`phase-P6-to-P7-gate.md`](./phase-P6-to-P7-gate.md) | Gate | **Single conclusion gate** — 6-step protocol: structured P1–P6 summary · vague-answer flag · open-ended coverage check · §4 coverage map reconciliation · deferred items final review · APPROVE / REJECT / REDIRECT. |
| [`phase-P7.md`](./phase-P7.md) | P7 — Final approval | Plain-language summary structured by §4 sub-section · pre-APPROVE walk of L6 closure rules · interview statistics · `interview-answers.json` written · APPROVE / REJECT / REDIRECT. |
| [`phase-P8.md`](./phase-P8.md) | P8 — PRD draft + AC derivation | PRD generated against 8-section schema · sequential `AC-NNN` derivation with `surface` field · reuse map finalisation · pre-write artifact-bar walk (L6 G3) per artifact · loads `prd-section-schema.md`, `prd-template.md`, `acceptance-criteria-template.md`. |
| [`phase-P9.md`](./phase-P9.md) | P9 — Handoff + traceability + bundle manifest | Three handoff briefs authored with Family N N8 pre-extraction · paste-ready prompts handed to PM · on-return Family N anchor verification + N5 spot-check · auto-built `traceability.md` · **`bundle-manifest.json` finalised at end of P9** · loads `sub-agent-delegation.md` and `handoff-prompt-templates.md`. |

---

## Reading discipline

- Coordinator reads `shared-protocols.md` once at interview start.
- At each phase transition, coordinator reads the active phase file
  ONLY. Phase modules never read each other.
- The single conclusion gate file is read at the end of P6, before P7.
- Question-bank files under `../question-sets/` are pulled by the
  matching phase module on first question of that phase.

## Conditional triggers (summary)

| Phase | Trigger predicate (sourced from P2 §4 coverage map) | When skipped |
|---|---|---|
| P3 | breakdown indicates calculation logic in scope (or PM amended P2 map to include §4.2 CL) | §4.2 carries `Not applicable — [reason]` |
| P4 | breakdown indicates allocation logic in scope (or PM amended P2 map to include §4.3 AL) | §4.3 carries `Not applicable — [reason]` |
| P5 | breakdown indicates UI change in scope (or PM amended P2 map to include §4.5 UI) | §4.5 carries `Not applicable — [reason]` |

P1, P2, P6, P7, P8, P9 always run. The single conclusion gate always
runs (between P6 and P7).
