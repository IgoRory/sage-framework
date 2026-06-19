# Styling Tiers -- Demo Visual Accuracy

Reference for prd-demo-generator. Defines how to style demo HTML based on
whether the feature modifies existing UI or introduces new UI.

---

## Classification

Determine the tier during Step 2 (classify demo type) by examining the PRD:

- **Tier 1** -- the PRD modifies existing screens, components, or workflows
  that already exist in the codebase
- **Tier 2** -- the PRD introduces new screens or components with no existing
  counterpart in the codebase
- **Mixed** -- some elements are Tier 1 (existing), others are Tier 2 (new).
  Apply the appropriate tier to each element individually.

---

## Tier 1: Existing UI Modifications

When the PRD modifies existing screens or components, replicate the real
application as closely as possible.

### What to read from the codebase

| Source | What to extract |
|--------|----------------|
| `_variables.scss` | Exact colour values (`$valid`, `$error`, `$invalid`, `$primary_color`, `$navy`) |
| `_common.scss` | Shared component styles, global patterns |
| Component `.html` templates | Exact HTML structure of related components |
| Component `.scss` files | Component-specific styles, box shadows, border-radii |
| Prefab/config `.ts` files | Exact button text, icon classes, status names |
| Toast/notification code | Exact toast message text and styling |
| Confirmation dialog code | Exact dialog titles, body text, button labels |

### Accuracy requirements

| Aspect | Rule |
|--------|------|
| Font | Must match real app font family from SCSS variables |
| Colours | Must use exact hex/RGB values from `_variables.scss` |
| Component structure | Must match real app HTML structure from templates |
| Box shadows, borders, radii | Must match exactly |
| Button styling | Must match app button classes (`.emp-action-button`, `.btn_green`, etc.) |
| Disabled state | Must match real disabled styling (grey text, transparent bg -- NOT opacity) |
| Spacing and padding | Must match real app values |

### After first generation pass

Perform a **styling audit**: compare every CSS property in the demo against
the real app source files. Fix discrepancies before completing Step 5.

---

## Tier 2: New UI (No Existing Counterpart)

When the PRD introduces new screens or components that do not exist in the
codebase, use the app's design language as a foundation but apply intentional,
distinctive design choices.

### Design direction protocol

Before generating Tier 2 elements:

1. **Start from the app's foundation** -- use primary colour palette from
   `_variables.scss` and general font family as baseline
2. **Elevate with intentional choices** -- layer distinctive typography
   pairings, thoughtful spatial composition, purposeful colour accents
3. **Choose a clear aesthetic tone** -- refined/professional,
   data-dense/utilitarian, clean/modern, etc. Commit and execute consistently
4. **Add polish through detail** -- subtle animations (staggered reveals,
   smooth transitions), considered hover states, deliberate spacing

### Design guidelines

| Area | Guideline |
|------|-----------|
| Typography | Start with app font. Consider pairing with a complementary display font for headings. Avoid generic defaults (Arial, Inter, Roboto). |
| Colour | Use app primary palette as dominant base. Add sharp accent colours for emphasis. Dominant + accent outperforms even distribution. Use CSS variables. |
| Layout | Consider asymmetry, grid-breaking elements, generous negative space, or controlled density. Avoid cookie-cutter centered-card-stack layouts. |
| Motion | CSS animations for high-impact moments: staggered entrance reveals, smooth state transitions, purposeful hover effects. |
| Depth and texture | Gradient meshes, subtle noise, layered transparencies, or dramatic shadows over flat backgrounds. Match intensity to tone. |

---

## Anti-Patterns (Both Tiers)

Avoid these regardless of tier:

- Generic purple-on-white gradients
- Predictable symmetrical layouts with no visual hierarchy
- Bland system fonts (Inter, Roboto, Arial) without justification
- Design that lacks any point of view or aesthetic commitment
- Every demo looking the same regardless of feature
- Using opacity for disabled states (use explicit grey text + transparent bg)
- Placeholder or stub styling when real values are available (Tier 1)

---

## Demo Chrome (Presentation Layer)

The demo wrapper (scenario selector sidebar, AC text panel, search bar,
animation controls) is NOT part of application UI -- it is a presentation
layer. Apply thoughtful design:

- Clean, readable typography
- Good spacing and visual hierarchy
- Subtle hover states on interactive elements
- Polished feel that does not compete with the application UI being demoed
- Consistent across all demos (not themed per feature)

The demo chrome should be visually distinct from the application UI so the
PM can clearly distinguish "this is the demo framework" from "this is what
the feature will look like."

---

## Message Text Rules

All user-facing text in the demo must follow the 3-tier message text
sourcing protocol from the PRD:

1. **Codebase-sourced** -- text marked `[Source: path:line]` in the PRD.
   Use the exact text in the demo.
2. **Agent-proposed / PM-provided** -- text marked `[Proposed -- approved by PM]`
   or `[PM-provided]` in the PRD. Use the exact text in the demo.
3. **Undetermined** -- text marked `[TEXT TBD]` in the PRD. Display in the
   demo as: `[TEXT TBD]` with a dashed-border placeholder styling to make
   it visually obvious that this text is not finalised.

Never invent message text that is not in the PRD. The demo visualises the
PRD -- it does not extend it.
