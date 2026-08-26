# Folder README templates

Written by the strategist in Step 8 to scaffold supporting folders. Each README is short — purpose + naming convention. Copy the relevant block verbatim into each folder.

---

## `context/source-material/README.md`

```markdown
# Source material

Raw input that fuels the content: transcripts, customer stories, research, founder reflections, photos, references.

Subfolders are defined in `context/strategy.md` (Source Material Plan section) and `context/content-process.md`. Typical layout:

```
context/source-material/
├── user-stories/    # Real stories from users / customers
├── research/        # Data, studies, stats
├── founder/         # Founder's own stories and reflections
├── images/          # Reference photos
├── html/            # UI mockups, design references
```

Convention:
- One discrete idea per file. The Writer searches across this tree.
- Don't dump giant docs. Break into atomic files so AI can retrieve them.
- Every source file should include a header: date added, source type, topic tags.

The conversation IS the source material. AI enriches it; it does not invent it.
```

---

## `content/topics/README.md`

```markdown
# Drafts

One folder per topic. Naming follows the convention in `context/content-process.md`:

`content/topics/<YYYY-MM-DD>-<type>-<topic>/`

Files inside (only what the calendar assigns to this topic):

- `blog.md`             — full blog post
- `seo.md`              — SEO metadata
- `{day}-{channel}.md`  — social posts, e.g. `mon-facebook.md`, `fri-instagram.md`
- `image-prompts.json`  — image generation prompts (written by Writer, consumed by Image Designer)

Lifecycle (status tracked in `content/content-calendar/content-calendar.md`):
`PLANNED` → `WRITTEN` → `DESIGNED` → `APPROVED` → `PUBLISHED`
```

