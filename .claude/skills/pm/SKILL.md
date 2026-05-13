---
name: pm
description: "Product Manager skill set: client interview, product documentation, project-status dashboard, standup management, epic writing (Dan Shipper style). Covers the full PM lifecycle from discovery to delivery tracking."
---

# Product Manager Skill Set

## 1. Client Interview (max 5 questions)

Gather sufficient context before any product work. Ask these questions — no more than 5, adapt order to conversation flow:

1. **What problem are you trying to solve?** — What is broken, missing, or frustrating? Who experiences it? What have they tried?
2. **What solution/product do you have in mind?** — Even if vague. What would success look like? What is the minimal version?
3. **What are your biggest pain points or constraints?** — Time, budget, team, technical, regulatory, or market timing.
4. **What are your conditions, preferences, or tech stack?** — Existing infrastructure, preferred platforms, non-negotiables (self-hosted vs SaaS, mobile-first vs web, etc.).
5. **What else do I need to know to build the right thing?** — Open-ended catch-all for context not covered above.

After answers, synthesize into the product documentation (Section 2).

## 2. Product Documentation

Create and maintain exactly 4 files:

### `docs/product/product.md`
Strategic product document with sections: problem, solution, users, JTBD, differentiation, market, business model, assumptions, metrics, next 90 days. One framing sentence at top: *"If you can't tell a stranger why we'd be sad if this product didn't exist, I've failed."*

### `docs/product/epics.md`
Each epic structured exactly as: **The problem** / **The mechanism** / **What it bundles** / **What success looks like** / **Why it goes first**. No deviations.

### `docs/product/epic-status.md`
Pipeline stages: Specified → In flight → Feature-complete → Tested → Shipped. Table per epic with: status, % done, pipeline dots, open/closed bugs.

### `docs/project-status.html`
Single self-contained HTML file (no external deps). Sections: Hero (headline, last-updated, stat tiles), Epic summary table, Epic detail grid (2-column cards), Build log, Companion docs. CSS variables for theming.

## 3. project-status.html Management

Must include the **5-point progress tracker** for each epic:

```
Pipeline: ● ● ● ● ●
           │  │  │  │  └── Shipped
           │  │  │  └───── Tested
           │  │  └──────── Feature-complete
           │  └─────────── In flight
           └────────────── Specified
```

- Filled dot (●) = reached stage, empty dot (○) = not yet
- Use the same design system as the project default, but allow client DS overrides once defined
- Sections in order: Hero → Stats → Epic summary → Epic detail grid → Build log → Companion docs

## 4. Standup Management

Four sub-capabilities:

- **daily-checkin**: Help write structured daily check-ins. Record to `standup/individual/`.
- **raid-log**: Maintain a RAID log (Risks, Assumptions, Issues, Dependencies) at `docs/product/raid-log.md`.
- **scope-change**: Document and assess scope changes. Record scope, impact, decision.
- **blocker-triage**: Classify blockers by severity (critical/major/minor), escalate appropriately.

## 5. Epic Writing (Dan Shipper Style)

Every epic must pass this test: *"If you read only the title and the problem statement, you know exactly what bet we're making."*

Structure:
```
## E{N} · {Epic Name}

**The problem:** {One sentence: specific user frustration or gap}
**The mechanism:** {One sentence: causal chain — how solving this produces the outcome}
**What it bundles:**
- {Feature or component 1}
- {Feature or component 2}
**What success looks like:** {Specific, measurable — number + date or behaviour threshold}
**Why it goes first:** {One sentence: dependency, risk reduction, or fastest learning}
```

Never use: Thesis, Hypothesis, Acceptance criteria, Definition of done, Priority signal in epics.md. Those belong in task plans.

## Output Paths

| Artifact | Path |
|----------|------|
| Product doc | `docs/product/product.md` |
| Epics | `docs/product/epics.md` |
| Epic status | `docs/product/epic-status.md` |
| Project status | `docs/project-status.html` |
| RAID log | `docs/product/raid-log.md` |
| Daily plans | `docs/plans/` |
| Standups | `standup/individual/` |
| Standup briefings | `standup/briefings/` |
