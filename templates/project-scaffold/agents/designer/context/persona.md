# designer — Project Persona

Project-specific rules for the designer agent. These override or extend global defaults.

## How this file is populated

Fill in `docs/brand/style-guide.md` first — the designer reads it automatically on every run.
This file is for designer-specific rules that go beyond the shared style guide.

When the PM agent runs `pm-client-interview`, it will prompt you to complete:
- `docs/brand/style-guide.md` — voice, colors, typography, visual mood, and brand adjectives

Once that is filled, update the sections below.

## Project-specific rules
<!-- What the designer must always do for this project -->
- (e.g. Always use a dark overlay on hero images so text is readable)
- (e.g. Always output WebP at max 200KB)

<!-- What the designer must never do for this project -->
- (e.g. Never use stock photos of people — illustrations only)
- (e.g. Never use colors outside the brand palette)

## Visual style
<!-- Preferred aesthetic, composition rules, style references -->
- Overall mood: (e.g. Clean, editorial, high contrast)
- Image style: (e.g. Abstract geometric, cinematic photography, flat illustration)
- Reference accounts: (e.g. @brandname on Behance, Dribbble team X)

## Stack and tools
<!-- Tools and output destinations for this project -->
- Output path: (e.g. content/topics/{slug}/images/)
- Generation tool: (e.g. Gemini API via designer-image-generation skill)
- Fallback: (e.g. Ideogram — paste prompt if API fails)
