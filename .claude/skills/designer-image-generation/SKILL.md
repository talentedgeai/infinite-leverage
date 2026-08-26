---
name: designer-image-generation
description: >-
  Generates one hero image using the Gemini AI image API, optimizes it to a compact web-friendly file (WebP, under 200 KB), and saves it alongside the blog post. Reads JSON image prompts from image-prompts.md created by the Writer. If image-prompts.md is missing, invokes the Writer to generate it first. If generation fails, saves the prompt so it can be used in any external image tool.
  Use when the operator says "generate the image", "hero image", "create a visual", or a finished post is missing its hero image.
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

If the file has no `<!-- design-preset: … -->` comment at the top, run
`designer-style-to-photo` first — it aligns `style` / `mood` / `palette` to
`docs/brand/style-guide.md` so the image comes back on-brand.

**If `image-prompts.md` does NOT exist:** stop image generation and invoke the Writer agent to produce it first:
1. Tell the operator: "`image-prompts.md` not found for `{slug}` — invoking Writer to generate image prompts from the post."
2. Delegate to the Writer with the instruction: "Read `content/topics/{slug}/blog.md` and generate `content/topics/{slug}/image-prompts.md` with JSON image prompts for hero.webp, social-card.png, and any inline images. Follow the brand voice in `docs/brand/style-guide.md`."
3. Once the Writer returns and `image-prompts.md` exists, re-run this skill from the top.

Do NOT invent a prompt. The Writer owns prompt creation to ensure brand-voice and topic consistency.

## Generation
- Model: the CURRENT Gemini image-generation model — never a pinned preview. Check the Gemini API docs/models list for the latest image-capable model at run time; if the call errors with a model-not-found, list available models and pick the newest image-capable one before falling back to the prompt-save flow.
- Method: Python Gemini SDK or curl + Gemini API
- Create the scratch dir first (gitignored, per `FOLDER-STRUCTURE.md`):
  `mkdir -p context/source-material/working_files`
- Save raw output to `context/source-material/working_files/{slug}-raw.png`

## Optimisation

Scale-and-crop to 1200×630 rather than a bare `scale=1200:630`, which stretches
anything that isn't already 40:21 and makes faces and type look wrong:

```bash
mkdir -p context/source-material/working_files
ffmpeg -y -i context/source-material/working_files/{slug}-raw.png \
  -vf "scale=1200:630:force_original_aspect_ratio=increase,crop=1200:630" \
  -q:v 85 content/topics/{slug}/{slug}-hero.webp

# Check the budget, then step quality down until it fits
while [ "$(wc -c < content/topics/{slug}/{slug}-hero.webp)" -gt 204800 ]; do
  echo "over 200 KB — re-encoding at lower quality"; break   # re-run with -q:v 80, 75, 70…
done
```

Stop stepping at `-q:v 60`; if it still exceeds 200 KB, tell the operator rather than
shipping a visibly degraded hero.

## Size Budget
- Target: under 200 KB per hero image
- Dimensions: 1200×630 (OG standard)
- Format: WebP

## Output Paths
| Artifact | Path |
|----------|------|
| Raw output | `context/source-material/working_files/{slug}-raw.png` |
| Optimised hero | `content/topics/{slug}/{slug}-hero.webp` |
