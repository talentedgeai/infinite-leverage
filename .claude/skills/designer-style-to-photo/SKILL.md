---
name: designer-style-to-photo
description: >-
  Reads a blog post's tone and subject matter, picks the matching preset from the design system, and tunes the Writer's existing JSON image prompt so the generated visual is on-brand — filling in palette, style, and mood from the style guide. Annotates the Writer's image-prompts.md; never authors a prompt from scratch.
  Use when the operator says "image prompt", "visual for this post", or a blog draft is finalized and its image prompt needs brand alignment before generation.
---

# Designer: Style-to-Photo Alignment

Run after the Writer finalizes the post and before `designer-image-generation`.

**Ownership:** the Writer owns `content/topics/{slug}/image-prompts.md` — subject,
composition, and what to avoid come from the post. This skill only aligns the
*visual* fields (`style`, `mood`, `palette`) to the design system and records which
preset was chosen. If the file doesn't exist, stop and invoke the Writer to create
it — do not write one yourself.

## Steps

1. Read `docs/brand/style-guide.md` — identify the 5 presets. Missing → ask the
   operator to run `designer-design-system` first.
2. Read `content/topics/{slug}/image-prompts.md`. Missing → stop, invoke the Writer.
3. Read the blog post title and first paragraph from `content/topics/{slug}/blog.md`.
4. Match the content's tone and subject to the best-fit preset:
   - Editorial / thought-leadership → clean serif + muted palette
   - Technical / product → monospace accents + functional palette
   - Lifestyle / personal → warm tones + expressive typography
   - Minimal / clean → generous whitespace, single accent colour
   - Bold / creative → high contrast, experimental composition
5. Record the selection as an HTML comment at the top of `image-prompts.md`, above
   the first section:
   ```
   <!-- design-preset: {preset-name} — {one-line reason} -->
   ```
6. Edit each JSON block **in place**, keeping the Writer's `subject`, `composition`,
   and `avoid` untouched. Overwrite only:
   - `style` — the preset's art/photographic direction
   - `mood` — the preset's emotional register, checked against the post's tone
   - `palette` — the preset's actual colour names/hexes from the style guide, not a
     generic description

   The file stays valid JSON inside each fence — `designer-image-generation` parses
   it directly, so a trailing comma or an unquoted value breaks generation.

## Gate

Before handing off to `designer-image-generation`:

- [ ] `<!-- design-preset: … -->` comment present at the top of the file
- [ ] Every JSON block still parses (`python3 -c "import json,sys; json.load(sys.stdin)"`)
- [ ] `palette` names colours that actually appear in `docs/brand/style-guide.md`
- [ ] `subject` / `composition` / `avoid` are unchanged from the Writer's version
