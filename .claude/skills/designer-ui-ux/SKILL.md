---
name: designer-ui-ux
description: >-
  Reviews a page or component against accessibility, responsive and usability standards — WCAG contrast, semantic markup, every interactive state, touch targets, and layout at four widths — and reports what fails with the fix. Use when the operator says "mockup", "wireframe", "ui design", "accessibility", "responsive", or asks "does this look right" about any page, and before any UI work is handed to QA.
---

# Designer: UI/UX Review

A review, not a vibe check. Name the file, the line, and the fix.

## Step 1 — Scope it

```bash
git diff --name-only origin/main...HEAD -- 'website/**/*.tsx' 'website/**/*.css'
```

No diff (a design question, not a change) → review the component the operator named.
Read the project's palette and typography from `docs/brand/style-guide.md` first; a
contrast failure is judged against the brand's real hex values, not assumed ones.

## Step 2 — Check each item, on the actual markup

**Contrast** — WCAG 2.1 AA: **4.5:1** body text, **3:1** for large text (≥24px, or ≥19px
bold) and for the non-text parts of controls. Compute it, don't estimate:

```bash
python3 - <<'EOF'
def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)
print(ratio('#1A1A1A', '#FFFFFF'))   # text vs background — needs >= 4.5
EOF
```

**Semantics** — one `<h1>` per page and no skipped heading levels; `<button>` for actions
and `<a href>` for navigation (never a `<div onClick>`); every input has an associated
`<label>`; every image has `alt` (`alt=""` if decorative); icon-only controls carry
`aria-label`.

**Interactive states** — hover, focus-visible, active, disabled, loading, and error must
each be styled. A visible focus ring is the one that gets dropped and the one keyboard
users depend on: never `outline: none` without a replacement.

**Responsive** — check 320, 768, 1024 and 1440px. Nothing may scroll horizontally at
320px. Touch targets ≥ 44×44px below 768px.

**Performance and layout stability** — `next/image` with explicit `width`/`height` (or
`fill` plus a sized parent) so images do not shift layout; skeletons rather than spinners
for content areas; no layout-shifting late-loading fonts.

**Consistency** — one button style, one card style, one form pattern. A second variant
needs a reason.

## Step 3 — Report

```
UI REVIEW — {page or component}
FAIL  {file}:{line} — {what} — {fix}
WARN  {file}:{line} — {what} — {why it matters}
PASS  contrast · semantics · states · responsive · targets · consistency
VERDICT: PASS / PASS WITH NOTES / FAIL
```

Any contrast or keyboard-access failure is a **FAIL**, not a note — those lock people out
rather than merely looking wrong. Hand FAILs back to the developer before QA sees the
page.

## If you cannot see the page

You are reading markup, not pixels. Say so, and confine the review to what the markup
proves: contrast from the declared colours, semantics, states, and target sizes. Ask the
operator for a screenshot for anything visual you cannot verify — do not assert a page
"looks right" on a code read.
