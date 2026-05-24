# Rich-Text Rendering + Editor — ReactMarkdown

> Reference spec for scaffolding accurate Markdown rendering and a plug-and-play Markdown editor.
> Status: Approved

## Architecture

Two independent systems:
1. **MarkdownRenderer** — renders Markdown strings with custom component overrides, syntax highlighting, and safe HTML sanitization
2. **MarkdownEditor** — controlled textarea-based editor with preview (`@uiw/react-md-editor`)

## Why custom component overrides

ReactMarkdown renders standard HTML elements by default. Most projects need:
- Code blocks: syntax highlighting, copy button, language label
- Links: `target="_blank"` + `rel="noopener noreferrer"` for external links
- Images: `next/image` instead of `<img>` for optimization
- Tables: horizontal scroll wrapper to prevent overflow
- Headings: anchor links for deep-linking

Without overrides, these are either missing or broken.

## Plugin stack

| Plugin | Purpose |
|---|---|
| `remark-gfm` | GitHub Flavoured Markdown (tables, strikethrough, task lists) |
| `rehype-highlight` | Syntax highlighting via highlight.js |
| `rehype-slug` | Auto-generates id on headings for anchor links |
| `rehype-external-links` | Adds target+rel to external links automatically |

## Key decisions

- **No `dangerouslySetInnerHTML`** — use ReactMarkdown which sanitizes by default
- **`rehype-external-links` over custom link component** — more reliable for all link types
- **`@uiw/react-md-editor` for editor** — zero-config, has split view, preview, toolbar. No Tiptap/ProseMirror complexity needed for Markdown-only use cases.
- **CSS variables for syntax theme** — import a highlight.js theme globally, not inline

## File map

| File | Responsibility |
|---|---|
| `lib/markdown/plugins.ts` | Shared remark/rehype plugin config |
| `components/markdown/MarkdownRenderer.tsx` | Main rendering component |
| `components/markdown/CodeBlock.tsx` | Custom code block with copy button |
| `components/editor/MarkdownEditor.tsx` | Controlled Markdown editor with preview |
