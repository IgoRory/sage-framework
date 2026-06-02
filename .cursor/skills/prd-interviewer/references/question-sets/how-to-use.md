# Question Sets — How to use this reference

Reference for prd-interviewer. Self-contained — no external skill references.

The per-section files in this folder are organised as **categories with
example questions and probing guidance**. These are starting points —
generate as many questions as needed within each category to fully cover
the feature. Never use question counts as a proxy for completeness.

---

## The gate is comprehensive understanding, not question count

A category is done when you can state a testable predicate for every
requirement it covers, every observable detail is captured, and every
non-obvious design choice has a documented rationale. A short category that
achieves this is finished. A long category that does not is not.

---

## Question discipline

1. **Ask only when needed** — a question is asked when the answer cannot be
   inferred from the breakdown's `investigation_context`, when a
   recommendation needs confirming, or when a challenge is warranted.
2. **No repetition** — never re-ask what has already been answered,
   explicitly or implicitly earlier in the conversation.
3. **No obvious questions** — if the answer is clearly derivable from recon
   or component context, state it and move on unless the PM corrects it.
4. **No category lock-in** — a question that advances understanding is
   valid even if it does not fit neatly into one category.
5. **No edge case leakage** — edge cases belong in Section 7. Note them
   internally and defer them.
6. **Batching** — ask 2–4 related questions per batch. Wait for all answers.
   Drop any that become unnecessary after a batch answer.

---

## Business language only

All questions are asked in business terms. SP names, return codes, view
column names, class names, flag names, and any other internal technical
construct are translated to plain business language before asking. The PM
must never be asked to confirm or correct any implementation-layer concept.

---

## Where probes live

Reusable probe patterns are in `challenger-probes.md` in this folder. Apply
them across any section when a PM answer feels like a stated preference
rather than a reasoned decision, or when a deviation from an established
application pattern needs confirming.
