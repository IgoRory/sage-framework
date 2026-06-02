# Handoff Prompt Templates

Reference for prd-interviewer. Self-contained — no external skill references.

Three paste-ready handoff prompts the prd-interviewer chat hands to the PM
verbatim. The PM opens a fresh Cursor chat for each, pastes the corresponding
prompt unchanged, and waits for the handoff chat to STOP after writing its
summary file. The PM never authors or modifies a prompt.

Shape follows Section 3 of the Phase 0 dry-run report. One template per
surface: demo, sample-data, component-spec.

See `sub-agent-delegation.md` for the orchestration sequence, brief
contract, application-fidelity hard rule (Family M), and handoff-chat
read discipline (Family N) that every prompt enforces.

**Family N — read discipline (binding across all three prompts).** The
brief's Section 3 lists every cited YAML or schema as
`{ path, read_mode, expected_anchors }`. The handoff chat MUST read each
file end-to-end and populate the `## YAML reads` H2 in its `_summary.md`
with verbatim `anchors_extracted` values. Fabricating an anchor is a hard
fail caught by the interviewer chat's Family N N3 post-return
verification (the interviewer opens only the YAMLs, not the artifact, and
matches each anchor verbatim). The hard rules block in every template
restates this discipline — redundancy at the gate is correct (N5).

---

## How to use these templates

1. The prd-interviewer chat completes the brief for one surface.
2. The interviewer chat copies the corresponding template below, substitutes
   the bracketed placeholders for the actual brief path and output paths,
   and presents the resulting prompt to the PM with the instruction:
   "Open a fresh Cursor chat in this workspace and paste the prompt below
   exactly. Do not edit it. When the chat reports `STOP`, return here."
3. The PM opens a fresh chat and pastes verbatim.
4. The handoff chat reads the brief plus every cited YAML, produces exactly
   the declared outputs, walks the brief's Tier 1 self-review checklist,
   writes the summary file, and STOPS.
5. The PM returns to the interviewer chat, which then runs the validation
   protocol in `sub-agent-delegation.md` §7.

---

## Template 1 — Demo handoff prompt

```
You are receiving a self-contained demo brief at:
[REPO-RELATIVE PATH TO demos/_brief.md]

Read that file in full, end-to-end. Read every component YAML it names
in Section 3 (the "Component YAML files you must deep-read" section)
end-to-end, paying particular attention to the `expected_anchors` for
each YAML — these are the read-proof tokens you must report back in
your summary's `## YAML reads` table. You may also read the sibling
acceptance-criteria artifact at
[REPO-RELATIVE PATH TO acceptance-criteria.md] to anchor scenario
coverage to specific AC IDs (sequential `AC-NNN`; the AC's category
lives in its `surface` field, not in the ID prefix). Then read this
prompt to its end before producing anything.

Hard rules for this chat:
1. Produce exactly the files declared in the brief's Section 1.
   They are the only files you write or modify.
2. Do NOT modify any file outside the directory(ies) declared in the
   brief's Section 1.
3. Do NOT touch .cursor/skills/, .cursor/agents/, .cursor/hooks/,
   .sage/workflow-config.json, .context/components/manifest.yaml,
   AGENTS.md, the prd.md, the acceptance-criteria.md (read-only access
   for AC IDs only), or any application source file.
4. Application-fidelity hard rule (Family M, binding — see
   sub-agent-delegation.md §4 for the canonical statement). When a UI
   affordance exists in the production application, you MUST mirror the
   cited YAML's structural and copy fidelity — you have zero discretion
   to invent a different pattern. You have production-grade design
   freedom ONLY for affordances the brief flags explicitly under "no
   application equivalent — generator's choice" in Section 10. Every
   other affordance must trace to a cited YAML.
5. Demo posture (binding — see sub-agent-delegation.md §3.1). The
   brief's Section 4 header names ONE of the four locked postures:
   AC-driven scenario theater · AC bar atop production page ·
   Production page replica, no AC overlay · Calculation-demo theater.
   You have zero discretion to switch postures. If the chosen posture
   is unsuitable, raise it in `## Open questions` and continue
   honouring the brief's posture — the interviewer chat will amend
   the brief if needed.
6. All user-facing text in the artifact must be either (a) verbatim
   from the brief's Section 6 "Verbatim text strings" section,
   (b) verbatim from a cited YAML's `copy_strings_verbatim` block, or
   (c) a `[TEXT TBD — requires PM decision]` marker. Do NOT paraphrase,
   do NOT translate, do NOT abbreviate.
7. Family N — read discipline (binding, sub-agent-delegation.md §6.1).
   You MUST read every file listed in the brief's Section 3
   end-to-end. No summarisation, no skimming, no inferring from file
   names. The `expected_anchors` block under each Section 3 entry
   names the read-proof tokens you must extract verbatim from the
   YAML (state names, copy strings, counts, header values) and report
   in the `## YAML reads` H2 table of your `_summary.md`. Fabricating
   an anchor (writing a plausible value without opening the YAML) is a
   hard fail — the interviewer chat's Family N N3 verification opens
   ONLY the YAMLs (not your demo HTML) and matches each
   `anchors_extracted` value verbatim against the YAML. A mismatch
   triggers re-handoff under L11 C2.
8. Tier 1 self-review runs INSIDE this chat, BEFORE you write the
   summary file (per sub-agent-delegation.md §K). Walk every item in
   the brief's Section 12 Tier 1 self-review checklist, including:
   - For every cited YAML, the demo's rendered affordance matches the
     YAML's structural fidelity AND copy fidelity (spot-check at least
     one structural element and one copy string per cited YAML).
   - For every uncited affordance in the demo, the brief contains an
     explicit no-application-equivalent call-out (Section 10).
   - Every brief Section 4 scenario is rendered or explicitly skipped
     with a one-sentence reason.
   - Every AC ID referenced in the brief Section 4 maps to a
     selectable scenario in the AC sidebar (AC IDs are sequential
     `AC-NNN`).
   - The `prdHash` SHA-256 in the summary header matches the brief's
     cited PRD content.
   - Single-file constraint: no external assets except CDN fonts/icons.
   - N6 read-completeness: for every Section 3 entry, every named
     anchor in `expected_anchors` has a verbatim value in the
     `## YAML reads` table. No skimmed reads. No guessed anchors.
   If any item fails, fix the demo and re-walk. If an item still
   fails after fixing, record it under `## Deviations from the brief`
   with a one-sentence reason.
9. The summary file uses exactly these six H2 headings in this order
   (sub-agent-delegation.md §6):
   `## Files written`,
   `## YAML reads`,
   `## Scenario coverage`,
   `## Deviations from the brief`,
   `## Ambiguities noticed in the brief`,
   `## Open questions`.
   The summary's first line under the H1 is the
   `<!-- prdHash: <sha256> -->` header for drift detection. No
   preamble. No conclusion. No other top-level sections.
   - `## YAML reads` is a markdown table with columns
     `| path | read_mode | anchors_extracted |`. One row per entry in
     the brief's Section 3. Every `expected_anchor` named in Section 3
     must appear in the corresponding row's `anchors_extracted` cell
     with the value extracted verbatim from the YAML.
   - `## Scenario coverage` columns: `scenario_id | AC | status | notes`.
     `status` is one of `rendered`, `partial`, `skipped`. `skipped`
     requires a one-sentence reason in `notes`. Every brief Section 4
     scenario must appear in table order. `AC` cites sequential
     `AC-NNN` IDs.
10. Once both files are written and the Tier 1 self-review has passed,
    STOP. Do not summarise the work in chat. Do not propose follow-ups.
    Do not start any other phase. The parent orchestrator will read
    the summary file to validate the output and return with next steps
    if needed.

Begin by reading [REPO-RELATIVE PATH TO demos/_brief.md].
```

---

## Template 2 — Sample-data handoff prompt

```
You are receiving a self-contained sample-data brief at:
[REPO-RELATIVE PATH TO sample-data/_brief.md]

Read that file in full, end-to-end. Read every schema reference or YAML
it names in Section 3 end-to-end, paying particular attention to the
`expected_anchors` for each entry — these are the read-proof tokens you
must report back in your summary's `## YAML reads` table. You may also
read the sibling acceptance-criteria artifact at
[REPO-RELATIVE PATH TO acceptance-criteria.md] to anchor edge-case row
sets to specific sequential `AC-NNN` IDs (the AC's surface lives in its
`surface` field — filter to `surface: data` or `surface: error` for
edge-case rows). Then read this prompt to its end before producing
anything.

Hard rules for this chat:
1. Produce exactly the files declared in the brief's Section 1
   (one or more JSON files under .sage/prds/[FEATURE_ID]/[sub-prd-id]/
   sample-data/, plus the summary file). They are the only files you
   write or modify.
2. Do NOT modify any file outside the brief's declared output directory.
3. Do NOT touch .cursor/skills/, .cursor/agents/, .cursor/hooks/,
   .sage/workflow-config.json, .context/components/manifest.yaml,
   AGENTS.md, the prd.md, the acceptance-criteria.md (read-only access
   for AC IDs only), or any application source file.
4. Application-fidelity hard rule (Family M, binding — see
   sub-agent-delegation.md §4). Every record shape, field type, and
   edge-case row set traces either to a cited schema/YAML (you mirror
   it exactly) or to an explicit "no application equivalent —
   generator's choice" call-out in the brief Section 10 (you exercise
   judgement within the brief's stated bounds). No silent gaps.
5. Every record must conform to the cited schema — field types,
   required fields, enums. For new components, the brief defines the
   schema; honour it exactly.
6. The brief's Section 4 record list is exhaustive. Do NOT add records
   that are not requested unless the brief's no-equivalent call-outs
   allow stress-test synthetic rows AND each synthetic row is marked
   `_invented: true` in the JSON.
7. No fabricated business meaning. Realistic invented values (e.g.
   counts in the low thousands for niche products) must be marked
   `_invented: true` so a developer does not seed production data from
   them.
8. Family N — read discipline (binding, sub-agent-delegation.md §6.1).
   You MUST read every file listed in the brief's Section 3
   end-to-end. No summarisation, no skimming, no inferring from file
   names. The `expected_anchors` block under each Section 3 entry
   names the read-proof tokens you must extract verbatim from the
   schema or YAML (field names, enum values, required-field counts,
   schema version headers) and report in the `## YAML reads` H2 table
   of your `_summary.md`. Fabricating an anchor is a hard fail — the
   interviewer chat's Family N N3 verification opens ONLY the
   schemas/YAMLs (not your JSON data files) and matches each
   `anchors_extracted` value verbatim. A mismatch triggers re-handoff
   under L11 C2.
9. Tier 1 self-review runs INSIDE this chat, BEFORE you write the
   summary file (per sub-agent-delegation.md §K). Walk every item in
   the brief's Section 12 Tier 1 self-review checklist, including:
   - For every cited schema/YAML, every record conforms structurally
     (field types, required fields, enums) and semantically
     (realistic values within the schema's stated bounds).
   - For every uncited record shape (synthetic stress-test rows),
     the brief's Section 10 contains an explicit
     no-application-equivalent call-out and the rows are marked
     `_invented: true`.
   - Edge-case rows trace to specific sequential `AC-NNN` IDs from
     the AC sibling where the brief declares the linkage (legacy
     bucketed `AC-EC-NNN` references are retired — only present in
     pre-lift bundles during the dual-layout backfill-on-touch
     window).
   - N6 read-completeness: for every Section 3 entry, every named
     anchor in `expected_anchors` has a verbatim value in the
     `## YAML reads` table. No skimmed reads. No guessed anchors.
   If any item fails, fix the data and re-walk.
10. The summary file uses exactly these six H2 headings in this order
    (sub-agent-delegation.md §6):
    `## Files written`,
    `## YAML reads`,
    `## Record coverage`,
    `## Deviations from the brief`,
    `## Ambiguities noticed in the brief`,
    `## Open questions`.
    The summary's first line under the H1 is the
    `<!-- prdHash: <sha256> -->` header for drift detection.
    - `## YAML reads` is a markdown table with columns
      `| path | read_mode | anchors_extracted |`. One row per entry
      in the brief's Section 3.
    - `## Record coverage` columns:
      `record_id | shape | edge_case | status | notes`. One row per
      record set in the brief's Section 4, in brief order. `status`
      is one of `written`, `partial`, `skipped`. `skipped` requires
      a one-sentence reason.
11. Once all files are written and the Tier 1 self-review has passed,
    STOP. Do not summarise the work in chat. Do not propose
    follow-ups. The parent orchestrator will read the summary file
    to validate the output.

Begin by reading [REPO-RELATIVE PATH TO sample-data/_brief.md].
```

---

## Template 3 — Component-spec handoff prompt

```
You are receiving a self-contained component-spec brief at:
[REPO-RELATIVE PATH TO component-spec/_brief.md]

Read that file in full, end-to-end. Read every component YAML it names
in Section 3 end-to-end, paying particular attention to the
`expected_anchors` for each YAML — these are the read-proof tokens you
must report back in your summary's `## YAML reads` table. You may also
read the sibling artifacts:
- [REPO-RELATIVE PATH TO acceptance-criteria.md] — AC IDs you
  cross-reference in component entries (read-only). AC IDs are
  sequential `AC-NNN`; the AC's category lives in its `surface` field.
- [REPO-RELATIVE PATH TO reuse-map-draft.md] — the full reuse map (the
  interviewer chat's disk-first artifact). Use this to anchor every
  entry's reuse decision.
Then read this prompt to its end before producing anything.

Hard rules for this chat:
1. Produce exactly the files declared in the brief's Section 1
   (component-spec.md plus the summary file). They are the only files
   you write or modify.
2. Do NOT modify any file outside the brief's declared output directory
   (component-spec.md lives at .sage/prds/[FEATURE_ID]/[sub-prd-id]/
   component-spec.md; the summary lives at component-spec/_summary.md).
3. Do NOT touch .cursor/skills/, .cursor/agents/, .cursor/hooks/,
   .sage/workflow-config.json, .context/components/manifest.yaml,
   AGENTS.md, the PRD, the acceptance-criteria.md (read-only access for
   AC IDs only), the reuse-map-draft.md (read-only), or any application
   source file.
4. Application-fidelity hard rule (Family M, binding — see
   sub-agent-delegation.md §4). For every matched component, the
   entry's states, interactions, and data-binding patterns mirror the
   cited YAML exactly. For new components (no application equivalent —
   generator's choice), the brief defines the structure; you bound
   design judgement to the cited brand palette and tone. Every entry
   traces to either a cited YAML (matched component) or to a Section 10
   "no application equivalent" call-out.
5. Outcome-only framing. Every entry describes what the component does
   (states, data bindings, interactions, visible affordances) — not how
   it is implemented. No internal flag names, no SP names, no class
   names.
6. No acceptance-criteria duplication. The component spec is a
   developer-facing surface map; it references AC IDs (from
   acceptance-criteria.md) using the locked sequential `AC-NNN` scheme,
   but does NOT restate AC Given/When/Then text. Every requirement
   lives in the PRD; every AC lives in acceptance-criteria.md. If a
   requirement would otherwise appear only in the component spec, that
   is a brief defect — call it out in the `## Deviations from the
   brief` section.
7. Use the six-element entry structure from component-spec-template.md
   (name/type · functional description · states + triggers ·
   interactions · selectable options · data binding) for every NEW or
   AFFECTED entry. REUSED entries with no differences may use the short
   form.
8. Family N — read discipline (binding, sub-agent-delegation.md §6.1).
   You MUST read every file listed in the brief's Section 3
   end-to-end. No summarisation, no skimming, no inferring from file
   names. The `expected_anchors` block under each Section 3 entry
   names the read-proof tokens you must extract verbatim from the
   YAML (state names, interaction names, data-binding field names,
   header values, copy strings) and report in the `## YAML reads` H2
   table of your `_summary.md`. Fabricating an anchor is a hard fail
   — the interviewer chat's Family N N3 verification opens ONLY the
   YAMLs (not your component-spec.md) and matches each
   `anchors_extracted` value verbatim. A mismatch triggers re-handoff
   under L11 C2.
9. Tier 1 self-review runs INSIDE this chat, BEFORE you write the
   summary file (per sub-agent-delegation.md §K). Walk every item in
   the brief's Section 12 Tier 1 self-review checklist, including:
   - For every matched-component entry, the entry's state set,
     interactions, and data binding mirror the cited YAML's
     `state_set`, `interactions`, and `copy_strings_verbatim` blocks
     (spot-check at least one element per cited YAML).
   - For every new-component entry, the brief's Section 10 carries a
     no-application-equivalent call-out for that component.
   - No AC text appears inline in any entry — only AC ID
     cross-references (sequential `AC-NNN`).
   - Every requirement that would otherwise live only in the spec is
     called out in the summary's `## Deviations from the brief`
     section.
   - N6 read-completeness: for every Section 3 entry, every named
     anchor in `expected_anchors` has a verbatim value in the
     `## YAML reads` table. No skimmed reads. No guessed anchors.
   If any item fails, fix the spec and re-walk.
10. The summary file uses exactly these six H2 headings in this order
    (sub-agent-delegation.md §6):
    `## Files written`,
    `## YAML reads`,
    `## Component coverage`,
    `## Deviations from the brief`,
    `## Ambiguities noticed in the brief`,
    `## Open questions`.
    The summary's first line under the H1 is the
    `<!-- prdHash: <sha256> -->` header for drift detection.
    - `## YAML reads` is a markdown table with columns
      `| path | read_mode | anchors_extracted |`. One row per entry
      in the brief's Section 3.
    - `## Component coverage` columns:
      `component_id | page | type | status | notes`. One row per
      component-spec entry, in entry order. `status` is one of
      `specified`, `partial`, `skipped`. `skipped` requires a
      one-sentence reason.
11. Once both files are written and the Tier 1 self-review has passed,
    STOP. Do not summarise the work in chat. Do not propose
    follow-ups. The parent orchestrator will read the summary file to
    validate the output.

Begin by reading [REPO-RELATIVE PATH TO component-spec/_brief.md].
```

---

## Substitution rules

- `[REPO-RELATIVE PATH TO …]` is replaced with the actual brief path under
  `.sage/prds/[FEATURE_ID]/[sub-prd-id]/[surface]/_brief.md`. No quoting,
  no backticks — paste the path as-is.
- `[FEATURE_ID]` and `[sub-prd-id]` are substituted everywhere they appear.
- No other placeholders exist. Every other instruction is identical across
  every handoff and must remain verbatim — the interviewer chat does not
  edit prompt body text.

---

## Why these prompts are paste-ready

Phase 0 demonstrated that the PM's only role in the handoff is to (a) open
a fresh chat and (b) paste a prompt unchanged. Removing prompt-authoring
from the PM removes the most common failure mode of programmatic-spawn
patterns: prompts that drift in subtle ways between handoffs and produce
inconsistent artifacts. The interviewer chat does the prompt authoring once,
per-feature; the PM operates the orchestration loop with a clipboard and a
chat-open shortcut.
