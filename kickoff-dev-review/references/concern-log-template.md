# Concern Log Template

Output format for `kickoff-dev-review`. Written to
`[SESSION_ROOT]/kickoff-dev-review-log.md`.

---

```
Kickoff Dev Review — Concern Log
=================================
Feature:     [feature title]
PRD:         [Notion link]
Meeting:     [Teams meeting link]
Processed:   [ISO datetime]
Participants: [speaker names from transcript]

SUMMARY
-------
PRD updates applied:          [N]
Phase implications noted:     [N]
Codebase conflicts:           [N]  (should be 0 before proceeding)
Addressed in PRD (no action): [N]
Out of scope (confirmed):     [N]
Persistent gaps:              [N]

PRD completeness score after updates: [N]/100 — [PASS / FAIL]

─────────────────────────────────────────────────────
CONCERNS — FULL LOG
─────────────────────────────────────────────────────

[For each concern:]

#[N] — [Concern title]
Category:    [PRD_UPDATE / PHASE_IMPLICATION / CODEBASE_CONFLICT /
              ADDRESSED_IN_PRD / OUT_OF_SCOPE / NO_ACTION]
Raised by:   [Speaker name]
Excerpt:     "[verbatim excerpt from transcript]"
Concern:     [Plain-language interpretation]
Resolution:  [What was decided or what action was taken]
PRD change:  [If PRD_UPDATE: exactly what was added/changed and where]
             [If no change: "None"]

─────────────────────────────────────────────────────
PRD DELTA NOTES
─────────────────────────────────────────────────────

[Summary of all changes applied to the PRD, grouped by section.
Each entry states: section, what was added/changed, concern reference.]

Requirements section:
  - REQ-[N] added: [requirement text] (from concern #[N])
  ...

Acceptance criteria:
  - REQ-[N] AC added: [AC text] (from concern #[N])
  ...

Edge/error states:
  - [Functional area]: [what was added] (from concern #[N])
  ...

Component specifications:
  - [Component name]: [element added/updated] (from concern #[N])
  ...

Out-of-scope section:
  - [Item added] (from concern #[N])
  ...

[If no PRD changes: "No PRD changes — all concerns were either
already addressed, out of scope, or no-action items."]

─────────────────────────────────────────────────────
PHASE SPLITTER BRIEFING
─────────────────────────────────────────────────────

[Appended to session manifest skeleton. Read by phase-splitter.]

[See Step 8 of SKILL.md for format.]

─────────────────────────────────────────────────────
PERSISTENT GAPS
─────────────────────────────────────────────────────

[Any concerns that could not be resolved during the session.
These must be resolved before proceeding to phase-splitter
if they are PRD_UPDATE or CODEBASE_CONFLICT category.]

[If none: "None — all concerns resolved."]

⚠️ GAP #[N]: [description]
  Raised by: [speaker]
  Why unresolved: [reason]
  Required action: [what needs to happen before proceeding]
```
