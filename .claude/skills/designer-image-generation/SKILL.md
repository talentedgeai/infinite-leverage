---
name: designer-image-generation
description: >-
  Generates one hero image using the Gemini AI image API, optimizes it to a compact web-friendly file (WebP, under 200 KB), and saves it alongside the blog post. Reads JSON image prompts from images.md created by the Writer. If images.md is missing, invokes the Writer to generate it first. If generation fails, saves the prompt so it can be used in any external image tool.
---

# Designer: Image Generation

## Discovery
```bash
ls -1t content/topics/   # newest first
```
Find the first folder that has `blog.md` but NOT `{slug}-hero.webp`.

## Prompt source — MANDATORY before generating

Before calling the image API, locate the JSON prompts the Writer prepared:

```bash
cat content/topics/{slug}/image-prompts.md 2>/dev/null
```

**If `image-prompts.md` exists:** read the `## hero.webp` section and parse the JSON block as the generation prompt.

**If `image-prompts.md` does NOT exist:** stop image generation and invoke the Writer agent to produce it first:
1. Tell the operator: "`image-prompts.md` not found for `{slug}` — invoking Writer to generate image prompts from the post."
2. Delegate to the Writer with the instruction: "Read `content/topics/{slug}/blog.md` and generate `content/topics/{slug}/image-prompts.md` with JSON image prompts for hero.webp, social-card.png, and any inline images. Follow the brand voice in `docs/brand/style-guide.md`."
3. Once the Writer returns and `image-prompts.md` exists, re-run this skill from the top.

Do NOT invent a prompt. The Writer owns prompt creation to ensure brand-voice and topic consistency.

## Generation
- Model: Gemini flash image preview (`gemini-2.0-flash-preview-image-generation` or latest)
- Method: Python Gemini SDK or curl + Gemini API
- Save raw output to `working_files/{slug}-raw.png`

## Optimisation
```bash
ffmpeg -i working_files/{slug}-raw.png -vf scale=1200:630 -q:v 85 content/topics/{slug}/{slug}-hero.webp
# If over 200 KB, reduce -q:v in 5% steps until under 200 KB
```

## Size Budget
- Target: under 200 KB per hero image
- Dimensions: 1200×630 (OG standard)
- Format: WebP

## Output Paths
| Artifact | Path |
|----------|------|
| Raw output | `working_files/{slug}-raw.png` |
| Optimised hero | `content/topics/{slug}/{slug}-hero.webp` |
