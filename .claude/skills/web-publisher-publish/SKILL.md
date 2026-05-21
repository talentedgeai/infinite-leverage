---
name: web-publisher-publish
description: >-
  Takes a finished blog post and makes it live on the website — converts the post to a Next.js page, updates the blog listing, runs a quality checklist, and prepares the git commit. The operator pushes to GitHub; Vercel deploys automatically from there. Nothing goes live until the operator pushes.
---

# Web Publisher: Publish Post

## Discovery
```bash
ls -1t content/topics/   # newest first
```
Find the first folder that has both `blog.md` AND `{slug}-hero.webp` but NO published page.

## Steps per Run
1. Read `blog.md` and `seo.md` — full content + front matter + SEO metadata
2. Read the project's web style guide for component conventions
3. Copy `{slug}-hero.webp` to `website/public/images/blog/`
4. **Delegate to Developer agent** — provide an implementation brief:
   - Target file: `website/pages/blog/posts/{slug}.jsx`
   - Requirements: `import Head from 'next/head'` (title, meta, OG/Twitter, canonical); `import Image from 'next/image'` for all images; read-time estimate in post header; category tag from style guide; CSS module or global styles (no inline)
   - Patterns to follow: existing posts in `website/pages/blog/posts/`
   - Wait for Developer to confirm the component compiles before continuing
5. Add post card at the top of `website/pages/blog/index.jsx` — follow existing card pattern exactly (this file update is Web Publisher's responsibility)
6. Stage: `git add website/pages/blog/posts/{slug}.jsx website/public/images/blog/{slug}-hero.webp website/pages/blog/index.jsx`
7. Commit: `git commit -m "publish: {Post Title}"`
8. Output: "Run `git push origin main` to go live."

## Quality Checklist (before commit)
- [ ] Component renders — correct JSX, no missing imports
- [ ] All images use `next/image` with correct `src`, `alt`, `width`, `height`
- [ ] `<Head>` includes title, meta description, OG/Twitter tags
- [ ] Category tag matches a valid blog category
- [ ] Post card at top of blog index grid
- [ ] Read-time estimate in post header
