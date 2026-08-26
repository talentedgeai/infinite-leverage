---
name: designer-design-system
description: >-
  Fills and maintains the designer-owned half of the project's brand guide — colour palette, typography, and visual style — at docs/brand/style-guide.md. One brand identity, not a menu of themes. Leaves voice, vocabulary and content formats to the PM and writer.
  Use when the operator says "design system", "style guide", "brand colors", "visual identity", or when docs/brand/style-guide.md still has placeholder values in the palette, typography, or visual-style sections.
---

# Designer: Design System

`docs/brand/style-guide.md` is the single brand reference every agent reads. It is created
by `/il-project` step 8.7 (from the operator's stated preference, or a DESIGN.md pulled
from getdesign.md) and it describes **one brand**, not a set of interchangeable themes.

**You own three sections of it.** Leave the rest alone:

| Section | Owner |
|---|---|
| Brand identity | PM (`pm-client-interview`) |
| Voice and tone · Vocabulary · Content formats · What to avoid | PM / writer |
| **Colour palette · Typography · Visual style** | **you** |

If the file does not exist, do not invent one — say so and ask the operator to run
`/il-project` step 8.7, or `pm-client-interview` if the project predates it.

## Step 1 — Read what is already there

```bash
sed -n '/^## Color palette/,/^## Content formats/p' docs/brand/style-guide.md
cat docs/brand/DESIGN.md 2>/dev/null   # the reference il-project pulled, if any
```

Anything still showing `#XXXXXX` or a parenthesised `(e.g. …)` is a placeholder and is
yours to fill. A value that is already real is a decision someone made — do not overwrite
it without asking.

## Step 2 — Fill the three sections

**Colour palette** — real hex values for every row (Primary, Secondary, Background, Text,
Muted). Derive them from `DESIGN.md` or the operator's reference brand. Two hard rules:

- Body text on background must clear **4.5:1** contrast, and large text **3:1**
  (`designer-ui-ux`). A palette that fails this is not a style choice, it is a bug.
- Five colours is the whole palette. If a sixth is needed, replace one.

**Typography** — heading, body and monospace fonts with weights, plus line heights. Name
fonts that are actually loadable (a Google Font, or one already in `website/`); do not
name a licensed font the project has no licence for.

**Visual style** — the section the image pipeline consumes. Fill all of:
`Overall mood`, `Image style`, `Composition rules`, `Colour usage in visuals`,
`Reference aesthetics`. Be concrete: "abstract geometric shapes, no stock photos of
people" is usable; "modern and clean" is not.

## Step 3 — Verify

- [ ] no `#XXXXXX` and no `(e.g. …)` left in your three sections
- [ ] contrast checked for text-on-background and large-text-on-background
- [ ] `Reference aesthetics` names something real that the Designer can look at
- [ ] the other sections are byte-identical to before

Then report which sections you filled and which are still the PM's to fill.

## Why one identity, not five presets

An earlier version of this skill described five interchangeable presets. A client project
has one brand — five palettes is how a site ends up looking like five sites. Tone
variation between a technical post and a personal one is handled by
`designer-style-to-photo` choosing a *treatment* within this palette, never by swapping
the palette.
