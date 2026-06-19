# SAGE S7 ↔ ADO Test Suite Handoff

This document defines the integration point between the SAGE S7
agent testing step and the Azure DevOps (ADO) test suite managed
by the `2-1-test-plan-creation.mdc` rule.

---

## Two testing paths in Profitability

The Profitability repo has two distinct testing workflows:

| Workflow | Scope | Artifact | Owner |
|---|---|---|---|
| **SAGE S7** | Per-phase, agent-driven | `phase-{N}-test-results.md` | test-runner agent |
| **ADO test plan** | Per-UserStory, human-QA-driven | ADO test run (Test Plans) | Developer + QA |

These are **complementary, not competing**. S7 provides automated
coverage evidence. The ADO test plan provides structured acceptance
test evidence reviewable by stakeholders.

---

## How they map

### One SAGE phase = one ADO UserStory test run segment

A SAGE phase corresponds to a set of tasks that together implement
one slice of a UserStory (or one full UserStory for small features).

```
Linear issue (Approved)
  └── SAGE session
        └── Phase N  ──── maps to ────► ADO UserStory test plan
              ├── S5 TDD results  ──────► ADO test cases (unit)
              ├── S6 Code review  ──────► ADO review evidence
              └── S7 Test results ──────► ADO test run execution
```

### Concrete mapping rules

1. **`phase-{N}-test-results.md` → ADO test run**

   After S7 completes with `STATUS: PASS`, the developer creates
   (or updates) the corresponding ADO test run for the UserStory
   linked to this phase. The test-runner summary section maps to
   the ADO "run summary" notes field.

   Test case IDs in the ADO test suite correspond to the test
   method names in `phase-{N}-test-results.md`. If an ADO test
   case ID is not yet created, the developer creates it per the
   `2-1-test-plan-creation.mdc` rule before marking the run complete.

2. **`tdd-results.md` → ADO unit test cases**

   Each task in `tdd-results.md` should have a corresponding ADO
   test case under the UserStory's test suite. The test method
   name in `tdd-results.md` is the ADO test case title prefix.

3. **`phase-{N}-code-review.md` → ADO review evidence**

   The code review `Critical findings: 0` verdict is the evidence
   that the `code-review-gate` passed. Reference the session path
   in the ADO test run's "attachments" or run notes:
   ```
   Code review: .sage/sessions/{SESSION_ID}/phase-{N}/phase-{N}-code-review.md
   ```

4. **E2E test results → ADO E2E test cases**

   Playwright E2E results from `phase-{N}-test-results.md` (E2E
   section) map to ADO test cases tagged `[E2E]`. Gap-analyzer
   scenarios that are converted to `*.spec.ts` files should have
   a corresponding ADO test case created per `2-1-test-plan-creation.mdc`.

---

## Gate ordering

The `code_review_gate` (S6) passes **before** the
`completion_report_stop_gate` (S8) checks test results. This is
the required sequence:

```
S6 → code_review_gate (Critical findings: 0 required)
S7 → test-runner runs full suite
     phase-{N}-test-results.md: STATUS: PASS required
S8 → completion_report_stop_gate reads phase-{N}-test-results.md
     Only proceeds if STATUS: PASS
```

The ADO test run is updated **after** the S8 gate passes — not
during S7. The S7 results are the source of truth; ADO reflects them.

---

## Does an ADO UserStory test plan satisfy S7?

**No.** An ADO test plan (from `2-1-test-plan-creation.mdc`) is
a human-reviewable artefact. S7 is agent-driven automation. They
serve different audiences:

- S7 gives the orchestrator agent a programmatic PASS/FAIL signal
  to gate the next step.
- The ADO test plan gives stakeholders a structured, traceability-mapped
  view of what was tested.

Both must exist for a phase to be considered done. A passing ADO
test run without a corresponding `phase-{N}-test-results.md: STATUS: PASS`
is incomplete. Conversely, a `STATUS: PASS` in S7 without an ADO
test run updated is incomplete.

---

## Handoff checklist (post-S7)

After `phase-{N}-test-results.md` reaches `STATUS: PASS`:

- [ ] Open the ADO test plan for the linked UserStory
- [ ] Mark unit test cases as Passed (matching `tdd-results.md` task rows)
- [ ] Mark E2E test cases as Passed (matching E2E section of test results)
- [ ] Add run notes referencing the session path and phase number
- [ ] Attach or link `phase-{N}-test-results.md` to the ADO test run
- [ ] Set the ADO test run outcome to "Passed"
- [ ] Proceed to S8 (completion report)

---

## References

- `2-1-test-plan-creation.mdc` — ADO test plan creation rule
- `test-runner.md` — SAGE S7 test-runner agent definition
- `docs/testingStrategy.md` — Profitability overall testing strategy
- `hooks/hooks.json` — `code_review_gate` and `completion_report_stop_gate`
