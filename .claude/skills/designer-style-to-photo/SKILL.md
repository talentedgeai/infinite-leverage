---
name: designer-style-to-photo
description: >-
  Reads a blog post's tone and subject matter, picks a visual treatment within the project's single brand palette, and tunes the Writer's existing JSON image prompt so the generated visual is on-brand — filling in palette, style, and mood from the brand guide. Annotates the Writer's image-prompts.md; never authors a prompt from scratch.
  Use when the operator says "image prompt", "visual for this post", or a blog draft is finalized and its image prompt needs brand alignment before generation.
---

# Designer: Style-to-Photo Alignment

Run after the Writer finalizes the post and before `designer-image-generation`.

**Ownership:** the Writer owns `content/topics/{slug}/image-prompts.md` — subject,
composition, and what to avoid come from the post. This skill only aligns the
*visual* fields (`style`, `mood`, `palette`) to the brand guide and records which
treatment was chosen. If the file doesn't exist, stop and invoke the Writer to create
it — do not write one yourself.

## Steps

1. Read the **Colour palette**, **Typography** and **Visual style** sections of
   `docs/brand/style-guide.md`. Placeholders still in them (`#XXXXXX`, `(e.g. …)`) →
   ask the operator to run `designer-design-system` first.
2. Read `content/topics/{slug}/image-prompts.md`. Missing → stop, invoke the Writer.
3. Read the blog post title and first paragraph from `content/topics/{slug}/blog.md`.
4. Pick a **treatment** — how this post is rendered *within the one brand palette*. The
   palette does not change between posts; the treatment does:

   | Post reads as | Treatment |
   |---|---|
   | Thought-leadership, analysis | restrained: muted tints of the palette, generous negative space |
   | Technical, product, how-to | functional: flat blocks, diagrammatic, mono accents |
   | Personal, story-driven | warm: the palette's warmest accent dominant, softer edges |
   | Launch, campaign | high-contrast: primary against background at full strength |

   Anything the style guide's `Composition rules` or `Colour usage in visuals` says
   overrides this table — those are the client's actual rules, this is a default.
5. Record the choice as an HTML comment at the top of `image-prompts.md`, above the
   first section:
   ```
   <!-- treatment: {treatment} — {one-line reason} -->
   ```
6. Edit each JSON block **in place**, keeping the Writer's `subject`, `composition`,
   and `avoid` untouched. Overwrite only:
   - `style` — the treatment's art/photographic direction, plus anything from
     `Image style` in the guide
   - `mood` — the treatment's emotional register, checked against the post's tone
   - `palette` — **actual hex values** from the guide's Colour palette table, not a
     generic description. Respect `Colour usage in visuals` (e.g. a max-colours rule)

   The file stays valid JSON inside each fence — `designer-image-generation` parses
   it directly, so a trailing comma or an unquoted value breaks generation.

## Gate

Before handing off to `designer-image-generation`:

- [ ] `<!-- treatment: … -->` comment present at the top of the file
- [ ] Every JSON block still parses (`python3 -c "import json,sys; json.load(sys.stdin)"`)
- [ ] every hex in `palette` appears in the guide's Colour palette table
- [ ] `subject` / `composition` / `avoid` are unchanged from the Writer's version
