---
name: writer-quality-critique
description: >-
  Critiques a draft blog post through the lens of Dan Shipper (every.to) — evaluating intellectual depth, original point of view, narrative pull, and conceptual originality. Returns a scored critique with specific revision instructions. The writer applies all feedback before passing to the Neil Patel SEO critique.
---

# Writer: Quality Critique (Dan Shipper / every.to POV)

## When to invoke

After the initial draft is complete and before the Neil Patel SEO critique. This gate ensures the post has intellectual substance and a genuine point of view before optimization.

## Critique framework

Read the full draft in `content/topics/{slug}/blog.md`, then score and comment on each dimension below. Output the critique as a section appended to `content/topics/{slug}/critique-quality.md` — do NOT modify `blog.md` yet.

---

### 1. Original insight (0–10)

Dan Shipper's bar: the post must contain at least one idea the reader could not have found by Googling the topic. A synthesis, a contrarian take, a personal observation backed by reasoning — not a list of common wisdom.

- **10**: The core idea is genuinely novel or reframes a familiar problem in a way readers haven't seen
- **5**: Contains one interesting observation buried inside mostly conventional content
- **0**: Pure aggregation — everything here exists elsewhere, stated more plainly

**Threshold to pass: 6. Below 6, rewrite the central argument before proceeding.**

---

### 2. Point of view (0–10)

every.to publishes writers with a voice, not content machines. The post must have a discernible stance — not "here are both sides" but "here is what I think and why."

- **10**: The author's position is unmistakable; the reader knows exactly where the writer stands
- **5**: A mild opinion surfaces but is hedged into near-meaninglessness
- **0**: No position — pure informational summary

**Threshold to pass: 6. If the writer is hiding behind "many people think," rewrite with a declared position.**

---

### 3. Narrative pull (0–10)

Does the piece make the reader want to reach the next paragraph? Shipper's work moves — there is tension, a question being answered, a story unfolding.

- **10**: Each section creates a question the next section resolves; the reader is pulled through
- **5**: Decent flow but sections could be reordered without loss
- **0**: The post is a flat list of points with no through-line

**Threshold to pass: 6. If it reads like a listicle in disguise, add a narrative arc.**

---

### 4. Intellectual depth (0–10)

Does the post go one level deeper than the obvious? every.to pieces explain the *why behind the why* — not just what to do, but the mental model or mechanism underneath.

- **10**: The post reveals a mechanism, mental model, or underlying truth most readers haven't made explicit
- **5**: Touches on why but stops before the reader has a new mental model
- **0**: Surface-level how-to with no explanatory depth

**Threshold to pass: 6. If there's no "aha" moment, identify the deepest idea and expand it.**

---

### 5. Opening 150 words (pass/fail)

Shipper's editorial standard: the opening must not explain what the post is about. It must *start in the middle of something* — a scene, a claim, a question, a contradiction.

- **Pass**: The reader is hooked within 3 sentences and has no idea what standard advice is coming
- **Fail**: The opening tells the reader what they're about to learn, or starts with context-setting

**Fail = mandatory rewrite of the opening before proceeding.**

---

## Output format

Append to `content/topics/{slug}/critique-quality.md`:

```markdown
# Quality Critique — Dan Shipper / every.to POV
**Date**: {YYYY-MM-DD}

## Scores
| Dimension | Score | Pass? |
|---|---|---|
| Original insight | /10 | ✅/❌ |
| Point of view | /10 | ✅/❌ |
| Narrative pull | /10 | ✅/❌ |
| Intellectual depth | /10 | ✅/❌ |
| Opening 150 words | pass/fail | ✅/❌ |

**Overall**: PASS / REVISE

## Revision instructions
[Specific, actionable list — reference exact sections or paragraphs in blog.md]
```

---

## Revision step (mandatory if any dimension fails)

1. Apply every revision instruction from `critique-quality.md` to `blog.md`
2. Re-read the revised draft and confirm each failed dimension now passes
3. Update `critique-quality.md` with a `## Post-Revision Check` section noting what changed
4. Only then proceed to the Neil Patel SEO critique
