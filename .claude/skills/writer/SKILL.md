---
name: writer
description: "Writer skill set: SEO-optimized blog content production with Neil Patel style self-critique. Produces one post per run including blog.md, SEO metadata, and image prompt."
---

# Writer Skill Set

## Workflow

1. **Discover** — Find the oldest topic folder with a `brief.md` but no `blog.md`
2. **Read brief** — Validate all required fields: title, target keyword, audience, angle, hook, supporting points, CTA, tone, deadline
3. **Research** — Search top-performing content for the target keyword. Reference current patterns.
4. **Write** — Produce `content/topics/{slug}/blog.md` and `content/topics/{slug}/image-prompts.md`
5. **Self-critique** (see below) — Run the Neil Patel critique before saving
6. **Output** — One blog post and one image prompt per run

## Neil Patel Self-Critique (mandatory after every draft)

Run this checklist before writing the final files:

### Hook
- Does the opening line make the reader need to keep reading?
- Weak: starts with context-setting or background
- Strong: opens with a surprising claim, data point, or direct challenge

### SEO Structure
- Primary keyword in: title, first 100 words, and at least two H2s
- H2s: do they tell a complete story when read alone (without body text)?
- Meta description: would a one-sentence summary make someone click?

### Proof Density
- Every claim needs evidence: data, named example, or case study
- "Many businesses find that..." is not proof — name the business, cite the stat
- Remove any assertion a reader could dismiss with "says who?"

### Scanability
- Can someone read only H2s and subheadings and understand the main point?
- No paragraph longer than 4 lines
- Bullet lists for 3+ parallel items

### Call to Action
- Exactly one CTA at the end — not three
- Specific ("Book a 30-min call"), not generic ("Get in touch")

### Cut 20%
- Every sentence earns its place or gets cut
- If a section doesn't add new information, it goes

## Brief Format (required)

Every topic folder must have a `brief.md` before the Writer runs:

```markdown
# Post Brief
**Title**: {working title}
**Target keyword**: {primary SEO keyword}
**Audience**: {who is this for — be specific}
**Angle**: {unique point of view or claim}
**Hook idea**: {optional — surprising stat, claim, or question}
**Supporting points**: {3–5 bullet points}
**Call to action**: {what should the reader do after reading?}
**Tone**: {authoritative, conversational, technical, story-driven}
**Deadline**: {YYYY-MM-DD or "next Monday run"}
```

## Output Paths

| Artifact | Path |
|----------|------|
| Blog post | `content/topics/{slug}/blog.md` |
| Image prompt | `content/topics/{slug}/image-prompts.md` |
