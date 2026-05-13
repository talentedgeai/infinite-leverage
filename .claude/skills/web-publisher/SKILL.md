---
name: web-publisher
description: "Web Publisher skill set: publishes one blog post per run — builds React component from markdown, updates blog index, stages git commit. Pushes content live without human handoff."
---

# Web Publisher Skill Set

## Workflow

### Discovery
Find the first topic folder that has both `blog.md` AND `{slug}-hero.webp` but NO published page:
```bash
ls -1t content/topics/
```

### Steps per run

1. **Read inputs**: `blog.md` (full content + front matter) and `seo.md` (meta description, OG tags)
2. **Read style guide**: the project's web style guide for component conventions
3. **Copy image**: `{slug}-hero.webp` → `website/public/images/blog/`
4. **Generate component**: Build a Next.js (Pages Router) `.jsx` component with:
   - `import Head from 'next/head'` — title, meta description, OG/Twitter tags, canonical URL
   - `import Image from 'next/image'` for all images
   - Read-time estimate in the post header
   - Category tag matching a valid blog category from the style guide
   - CSS module or global styles — no inline styles unless unavoidable
5. **Write component** to `website/pages/blog/posts/{slug}.jsx`
6. **Update blog index**: Add post card at top of `website/pages/blog/index.jsx` — follow existing card pattern exactly
7. **Stage changes**:
   ```bash
   git add website/pages/blog/posts/{slug}.jsx \
           website/public/images/blog/{slug}-hero.webp \
           website/pages/blog/index.jsx
   ```
8. **Commit**: `git commit -m "publish: {Post Title}"`
9. **Output**: "Run `git push origin main` to go live."

## Quality Checklist (before commit)
- [ ] Component renders without errors — correct JSX, no missing imports
- [ ] All images use `next/image` with correct `src`, `alt`, `width`, `height`
- [ ] `<Head>` includes title, meta description, OG/Twitter tags
- [ ] Category tag matches a valid blog category from the style guide
- [ ] Post card added at the top of the blog index grid
- [ ] Read-time estimate included in the post header
