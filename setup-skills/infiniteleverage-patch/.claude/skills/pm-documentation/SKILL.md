---
name: pm-documentation
description: Create and maintain exactly 4 product documentation files with strict formats. Scaffolded once from client interview, updated continuously.
---

# PM: Product Documentation

Manage exactly 4 files. Each has a strict format — never deviate.

## File 1: `docs/product/product.md`

Header: `{product name} · Written by {Owner} · Draft v0.1 · {date}`

Framing sentence (first line): *"If you can read this whole document and not be able to tell a stranger why we'd be sad if this product didn't exist, I've failed at writing it."*

Sections in this exact order:

1. `## 1. The problem` — two paragraphs: first states the problem with numbers/evidence; second names the broken assumption. End with "If we're wrong about this, no amount of feature work saves us."
2. `## 2. What we deliver` — N bold verb-noun phrases (max 6), each with a one-sentence explanation
3. `## 3. Who this is for` — 3-paragraph narrative: (a) vivid portrait of the specific person, (b) what they've tried and rejected, (c) 3 anti-personas
4. `## 4. The job they're hiring us for` — two paragraphs: JTBD in behavioral terms; what they go back to if product vanishes
5. `## 5. The wedge` — one feature/mechanism in bold + 3 bullets on why it's specific/deterministic/compounds
6. `## 6. 12 months out` — 3–5 paragraphs walking through the mature product
7. `## 7. What we are explicitly not building` — 4–6 bold categories with one-sentence explanations
8. `## 8. Differentiation table` — Competitor | What they do well | Where they fall short | Our angle (≥3 rows)
9. `## 9. Market and timing` — TAM/SAM/SOM + why now
10. `## 10. Business model` — pricing, unit economics
11. `## 11. What I believe but can't yet prove` — 2–4 load-bearing assumptions, each with falsification test
12. `## 12. How we know it's working` — 2 metrics only: Leading metric + Trailing metric
13. `## 13. Next 90 days` — 3 bets in "end-state, not roadmap" format
14. `## 14. Open decisions` — bulleted: what's undecided + who decides + deadline
15. Close: `---` then *"What this doc deliberately does not do: feature backlog, integration list, P&L."*

## File 2: `docs/product/epics.md`

Opening paragraph (verbatim): *"These are thematic bundles of work. Each epic makes a bet on user behavior — a specific problem that, if solved, unlocks a meaningful outcome. Epics are not a sprint backlog."*

Blockquoted user-problem statements from interview, then each epic:

```
## E{N} · {Name}

**The problem:** {One sentence}
**The mechanism:** {One sentence: causal chain}
**What it bundles:**
- {Feature 1}
- {Feature 2}
**What success looks like:** {Measurable — number + date}
**Why it goes first:** {Dependency, risk reduction, or fastest learning}
```

Then: `## What we are not bundling` + `## How epics map to phases` + `## The sequence argument`

## File 3: `docs/product/epic-status.md`

Header: `{product name} · Epic Status · Last updated: {date} · Phase in flight: {phase}`

Pipeline stages block (verbatim):
```
| Stage | Gate question |
|-------|---------------|
| 1 · Specified | Is there a written spec with acceptance criteria? |
| 2 · In flight | Is active development underway? |
| 3 · Feature-complete | Does it meet every acceptance criterion? |
| 4 · Tested | Have all tests passed? |
| 5 · Shipped | Is it deployed and measurably impacting users? |
```

Status glyphs: 🔄 in flight · ✅ done · ⏳ partially done · ☐ planned · 🛑 paused

`## At a glance` — table: Epic | Status | % done (est) | Pipeline (5 dots ●/○) | Open bugs | Closed bugs | Notes

`## Drilldown` — one H3 per epic with shipped/outstanding/done/closed bugs

`## Obsolete / won't fix` — table of dropped items

## File 4: `docs/product/01-product-timeline.md`

One section per phase: `## Phase {N} — {Name}` with Goal, Primary epics, Done-when exit criterion.

## Output Paths

| File | Path |
|------|------|
| Product strategy | `docs/product/product.md` |
| Epics | `docs/product/epics.md` |
| Epic status | `docs/product/epic-status.md` |
| Timeline | `docs/product/01-product-timeline.md` |
