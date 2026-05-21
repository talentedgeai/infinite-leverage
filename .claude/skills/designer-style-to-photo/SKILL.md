---
name: designer-style-to-photo
description: >-
  Reads a blog post's tone and subject matter, matches it to the best visual style from the design system, and writes a detailed, structured image prompt ready for the image generation step. Bridges the gap between written content and a visual that feels on-brand.
---

# Designer: Style-to-Photo Alignment

Run before every image generation.

## Steps
1. Read `docs/brand/style-guide.md` — identify the 5 presets
2. Read the blog post title and first paragraph from `content/topics/{slug}/blog.md`
3. Match the content's tone and subject to the best-fit preset:
   - Editorial/thought-leadership → clean serif + muted palette
   - Technical/product → monospace accents + functional palette
   - Lifestyle/personal → warm tones + expressive typography
4. Record the selected preset as an HTML comment at the top of `content/topics/{slug}/image-prompts.md`:
   `<!-- design-preset: {preset-name} — {one-line reason} -->`
5. Use the preset's palette and tone descriptor when constructing the image generation prompt

## Prompt Format
```
subject: {main visual element}
style: {art style or photographic style aligned to design preset}
mood: {emotional tone}
palette: {key colors from preset}
composition: {framing or layout note}
avoid: {things to exclude}
```
