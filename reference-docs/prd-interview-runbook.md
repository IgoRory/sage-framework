# PRD interview runbook (PM)

Operational guide for **`prd-interviewer`**, repo preflight, PRD telemetry, and **`prd-interviewer-effectiveness-evaluator`**.

---

## Before you start

1. Open the **product repository** in Cursor (the repo where the PRD-driven feature will land).
2. Confirm **Linear** feature issue id (`LIN-####`) for this PRD.
3. Ensure **`.sage/workflow-config.json`** contains:
   - `prd.requiredInterviewBranch` — branch you must use during the interview (default in template: `develop`).
   - `prd.remoteName` — usually `origin`.
   - `prd.telemetryFile` — append-only JSONL path (default: `.sage/prd-interview-telemetry.jsonl`).

---

## Step 0 — Repo gate (SKILL-enforced)

The agent runs **git** in the **current workspace** (your open repo):

- `git fetch <remoteName>`
- Current branch must equal **`prd.requiredInterviewBranch`**.
- **Not behind** remote: no incoming commits on that branch you have not integrated (`commitsBehind == 0`).

If you cannot satisfy the gate (wrong branch, behind remote), fix checkout/sync **before** continuing the interview.

**Override:** If you must proceed on another branch (e.g. emergency hotfix lane), state an explicit override with a short reason. The agent records it in telemetry and proceeds — use sparingly.

---

## Telemetry

- **File:** Resolved from `prd.telemetryFile` (repo-relative).
- **Format:** One JSON object per line (JSONL), UTC timestamps, `workflowKind: "prd_interview"`.
- **Correlation:** Each run uses a **`prdRunId`** (UUID) across chats.
- **Helper:** `prd_telemetry_append.py` in `.cursor/hooks/scripts/` (see `hooks-spec/hook-scripts-spec.md` in sage-framework).

Do not delete or hand-edit JSONL except for incident response; analytics and the PRD evaluator consume this file.

---

## When to run `prd-interviewer-effectiveness-evaluator`

- **Cadence:** Prefer **manual** until several interviews have completed; then optionally every **5** `prd_interview_completed` events in the JSONL, or on a monthly PM review.
- **Inputs:** PRD JSONL path (same as above), `.sage/skill-update-history.jsonl`, optional traceability review artifacts keyed by `linearIssueId`.
- **Approver:** Product Manager for proposed **`prd-interviewer`** SKILL updates (Linear label `skill-update`, Pending Approval).

The general **`skill-effectiveness-evaluator`** defers **`prd-interviewer`** evaluation to this dedicated evaluator when both exist — avoid duplicate Linear proposals.

---

## Smoke checklist

1. Workflow-config has `prd.*` keys.
2. On correct branch and synced, start interview → at least one `prd_preflight` line with `preflightOutcome: pass`.
3. After a phase, confirm `prd_phase_started` / `prd_phase_completed` lines exist for the active **P1–P9** mapping.
4. Optional: dry-run read of JSONL path from repo root for **`prd-interviewer-effectiveness-evaluator`**.

---

## References

- Skill: `.cursor/skills/prd-interviewer/SKILL.md`
- Evaluator: `.cursor/skills/prd-interviewer-effectiveness-evaluator/SKILL.md`
- Workflow config: `.sage/workflow-config.json`
