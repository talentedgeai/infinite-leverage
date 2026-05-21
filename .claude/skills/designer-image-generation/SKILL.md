---
name: designer-image-generation
description: >-
  Generates one hero image using the Gemini AI image API, optimizes it to a compact web-friendly file (WebP, under 200 KB), and saves it alongside the blog post. Reads the image prompt created by the Style-to-Photo skill. If generation fails, saves the prompt so it can be used in any external image tool.
---

# Designer: Image Generation

## Discovery
```bash
ls -1t content/topics/   # newest first
```
Find the first folder that has `image-prompts.md` but NOT `{slug}-hero.webp`.

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
