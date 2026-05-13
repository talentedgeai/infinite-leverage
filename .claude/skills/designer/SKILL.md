---
name: designer
description: "Designer skill set: design system management, UI/UX best practices, style-to-photo alignment, image generation prompting. Generates one hero image per run using Gemini."
---

# Designer Skill Set

## 1. Design System

Maintain a design system at `docs/brand/style-guide.md` with 5 presets:
- **Editorial/thought-leadership** — clean serif + muted palette
- **Technical/product** — monospace accents + functional palette
- **Lifestyle/personal** — warm tones + expressive typography
- **Minimal/clean** — generous whitespace, single accent color
- **Bold/creative** — high contrast, experimental layouts

Each preset defines: color palette (primary, secondary, accent, background, text), typography (headings, body, mono), spacing scale, border radius, shadow tokens.

Before generating any image: read the design system, match the blog's tone to the best-fit preset, record the selection.

## 2. UI/UX Best Practices

- **Accessibility first**: WCAG 2.1 AA minimum, semantic HTML, ARIA labels, sufficient color contrast
- **Responsive**: mobile-first, test at 320px, 768px, 1024px, 1440px
- **Performance**: lazy-load images, minimize CLS, use next/image, avoid layout shifts
- **Interaction states**: hover, focus, active, disabled, loading, error — all must be styled
- **Consistency**: same patterns for same problems — one button style, one card style, one form pattern
- **Progressive disclosure**: show what's needed, hide what's not. No information overload

## 3. Style-to-Photo Generation Alignment

Before generating an image prompt:
1. Read `docs/brand/style-guide.md` — find the best-fit preset for this content
2. Read the blog post title and first paragraph
3. Map the content's tone to the preset's visual language
4. Record the selected preset in the image prompt file

Prompt format:
```
subject: {main visual element}
style: {art style or photographic style aligned to design preset}
mood: {emotional tone}
palette: {key colors from preset}
composition: {framing or layout note}
avoid: {things to exclude}
```

## 4. Image Generation

- Model: `gemini-2.0-flash-preview-image-generation` (or latest Gemini image model)
- Use Python Gemini SDK or curl + Gemini API
- Save raw output to `working_files/{slug}-raw.png`
- Optimise: `ffmpeg -i working_files/{slug}-raw.png -vf scale=1200:630 -q:v 85 content/topics/{slug}/{slug}-hero.webp`
- Target: under 200 KB. If over, reduce `-q:v` in 5% steps.

## Output Paths

| Artifact | Path |
|----------|------|
| Style guide | `docs/brand/style-guide.md` |
| Image prompt | `content/topics/{slug}/image-prompts.md` |
| Raw image | `working_files/{slug}-raw.png` |
| Optimised image | `content/topics/{slug}/{slug}-hero.webp` |
