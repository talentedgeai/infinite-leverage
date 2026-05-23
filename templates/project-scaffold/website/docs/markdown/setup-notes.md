# Rich-Text — Setup Notes

## Dependencies

```bash
npm install react-markdown remark-gfm rehype-highlight rehype-slug rehype-external-links
npm install @uiw/react-md-editor
```

## Syntax highlighting theme

Import a highlight.js theme in `app/globals.css`:
```css
@import 'highlight.js/styles/github-dark.css';
```

Or pick any theme from [highlight.js styles](https://highlightjs.org/demo).

## Tailwind Typography

MarkdownRenderer uses Tailwind's `prose` class. Install the plugin if not already:
```bash
npm install -D @tailwindcss/typography
```

```ts
// tailwind.config.ts
plugins: [require('@tailwindcss/typography')]
```

## Editor styles

`@uiw/react-md-editor` ships its own CSS. Import in `app/layout.tsx`:
```ts
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-md-editor/markdown.css'
```

## External images in MarkdownRenderer

For external image domains, add them to `next.config.ts`:
```ts
images: {
  remotePatterns: [
    { protocol: 'https', hostname: '**.example.com' },
    // TODO: add your CDN/image hosting domains
  ]
}
```
