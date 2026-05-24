---
name: scaffold-rich-text
description: >-
  Stamps a Markdown renderer (ReactMarkdown with custom components, syntax
  highlighting, GFM) and a plug-and-play Markdown editor into the current
  Next.js project. Invoke when a user asks to "add markdown renderer",
  "scaffold markdown editor", "add rich text", "add content renderer", or similar.
---

# Scaffold: Rich-Text Rendering + Markdown Editor

Stamps a production-ready Markdown renderer and editor into the current project.

## Before you start

Ask:
- **Syntax highlighting theme?** (default: `github-dark` — any highlight.js theme name)
- **Need the editor component?** (default: yes — skip if display-only)
- **Tailwind Typography already installed?** (default: assume no — we'll install it)

Note as `$HIGHLIGHT_THEME`, `$INCLUDE_EDITOR`, `$HAS_TYPOGRAPHY`.

---

## Editor choice

Two options — pick one per project:

| Option | Package | When to use |
|---|---|---|
| **MDXEditorFull** (recommended) | `@mdxeditor/editor` | User-facing content creation, CMS pages, rich editing UX |
| **MarkdownEditor** (lightweight) | `@uiw/react-md-editor` | Admin forms, internal tools, quick markdown input |

Note answer as `$EDITOR_CHOICE` (`mdxeditor` or `uiw`).

---

## Step 1 — Install dependencies

**Always needed (renderer):**
```bash
npm install react-markdown remark-gfm rehype-highlight rehype-slug rehype-external-links
npm install -D @tailwindcss/typography
```

**If `$EDITOR_CHOICE` = `mdxeditor` (recommended):**
```bash
npm install @mdxeditor/editor
```
Then add to `app/layout.tsx`:
```ts
import '@mdxeditor/editor/style.css'
```

**If `$EDITOR_CHOICE` = `uiw` (lightweight):**
```bash
npm install @uiw/react-md-editor
```
Then add to `app/layout.tsx`:
```ts
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-md-editor/markdown.css'
```

---

## Step 2 — Syntax theme

In `app/globals.css`:
```css
@import 'highlight.js/styles/$HIGHLIGHT_THEME.css';
```

If `$INCLUDE_EDITOR`, also in `app/layout.tsx`:
```ts
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-md-editor/markdown.css'
```

---

## Step 3 — Plugin config

`lib/markdown/plugins.ts` — re-exports all plugins with shared options. Keeps MarkdownRenderer clean.

---

## Step 4 — MarkdownRenderer

`components/markdown/MarkdownRenderer.tsx` with these overrides:
- `pre` → `<CodeBlock>` with copy button and language label
- `code` → inline code styling
- `img` → `next/image` for local images, passthrough for external
- `table` → horizontal scroll wrapper
- `h1/h2/h3` → anchor links on hover (requires `rehype-slug`)

**Important:** Hoist plugin arrays to module level — do NOT define them inline in JSX. Inline arrays cause the component to re-create plugin instances on every render.

Usage:
```tsx
import { MarkdownRenderer } from '@/components/markdown/MarkdownRenderer'
<MarkdownRenderer content={post.body} />
```

---

## Step 5 — MarkdownEditor (if `$INCLUDE_EDITOR`)

`components/editor/MarkdownEditor.tsx` — controlled component wrapping `@uiw/react-md-editor`:

```tsx
import { MarkdownEditor } from '@/components/editor/MarkdownEditor'

const [content, setContent] = useState('')
<MarkdownEditor value={content} onChange={setContent} height={500} />
```

Dynamic import required (browser-only APIs). Already handled inside the component.

---

## Post-scaffold TODOs

| File | TODO |
|---|---|
| `app/globals.css` | Import highlight.js theme |
| `app/layout.tsx` | Import editor CSS if editor is included |
| `next.config.ts` | Add remote image domains for external images in Markdown |
| `components/markdown/MarkdownRenderer.tsx` | Replace Tailwind prose classes with project design system |
| `components/markdown/CodeBlock.tsx` | Style copy button with project design system |

---

## Common mistakes to avoid

- **Never** use `dangerouslySetInnerHTML` for Markdown — use ReactMarkdown
- **Never** import `@uiw/react-md-editor` without `dynamic({ ssr: false })` — it uses browser APIs
- **Never** skip `rehype-external-links` — raw external links miss `rel="noopener"` security attribute
- **Never** define plugin arrays inline in JSX — hoist to module level to prevent re-creation on every render
- **Always** use `next/image` for local images, NOT `<img>` — avoids CLS and enables optimization

Reference implementation: `templates/project-scaffold/website/` in the infiniteleverage-8-agents-template repo.
