---
name: pm-epic-writing
description: Write epics in Dan Shipper style — problem statement first, then mechanism, bundles, success criterion, and sequencing rationale. Strict format enforcement.
---

# PM: Epic Writing (Dan Shipper Style)

Every epic must pass this test: *"If you read only the title and the problem statement, you know exactly what bet we're making."*

## Structure (strict — no deviations)

Each epic in `docs/product/epics.md`:

```
## E{N} · {Epic Name}

**The problem:** {One sentence: the specific user frustration or gap this epic addresses}
**The mechanism:** {One sentence: the causal chain — how solving this produces the outcome}
**What it bundles:**
- {Feature or component 1}
- {Feature or component 2}
**What success looks like:** {Specific, measurable — number + date or behaviour threshold}
**Why it goes first:** {One sentence: dependency, risk reduction, or fastest learning}
```

## What NOT to include in epics.md

Never use these fields in epics.md — they belong in task plans:
- Thesis
- Hypothesis
- Acceptance criteria
- Definition of done
- Priority signal
- Bundle (as a heading — use "What it bundles")

## Product Thinking (Dan Shipper)

As code becomes cheaper to write, deciding *what* to write becomes the most valuable work. Your job:
- **Eliminate busywork**: status updates, scheduling, tracking — handle these automatically
- **Amplify thinking**: design decisions, data insights, customer empathy — these need your full attention
- The product conversation IS the work. Every session is one coherent thread, not a checklist across tools
- Never let the process become more visible than the product

## Sequence Argument

After all epics, include a paragraph explaining the overall sequencing logic — why this order and not another. Every epic has a reason for its position in the build order.

## Edge Cases
- Epic overlaps with existing one: merge into existing, don't create duplicate
- Stakeholder says "build all at once": push back — sequencing reveals assumptions
- Success criterion can't be measured: make it directional ("reduce time spent on X by half") rather than precise
