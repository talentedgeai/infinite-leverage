---
name: web-publisher-publish
description: >-
  Takes a finished blog post all the way to production — delegates React/Next.js implementation to Developer, commits, pushes to remote, merges to main, and confirms the Vercel deployment is healthy. The post is not done until the build is green.
---

# Web Publisher: Publish Post

## Discovery
```bash
ls -1t content/topics/   # newest first
```
Find the first folder that has both `blog.md` AND `{slug}-hero.webp` but NO published page.

## Steps per Run

### Phase 1 — Content assembly
1. Read `blog.md` and `seo.md` — full content + front matter + SEO metadata
2. Read the project's web style guide for component conventions
3. Copy `{slug}-hero.webp` to `website/public/images/blog/`

### Phase 2 — Code (delegated to Developer)
4. **Brief the Developer agent:**
   - Target file: `website/pages/blog/posts/{slug}.jsx`
   - Requirements: `import Head from 'next/head'` (title, meta, OG/Twitter, canonical); `import Image from 'next/image'` for all images; read-time estimate in post header; category tag from style guide; CSS module or global styles (no inline)
   - Patterns to follow: existing posts in `website/pages/blog/posts/`
5. **Wait for Developer to confirm** the component is written and `npm run build` passes clean

### Phase 3 — Index update (Web Publisher's responsibility)
6. Add post card at the top of `website/pages/blog/index.jsx` — follow existing card pattern exactly

### Phase 4 — Quality gate (run before commit)
- [ ] Component renders — correct JSX, no missing imports
- [ ] All images use `next/image` with correct `src`, `alt`, `width`, `height`
- [ ] `<Head>` includes title, meta description, OG/Twitter tags
- [ ] Category tag matches a valid blog category
- [ ] Post card at top of blog index grid
- [ ] Read-time estimate in post header

### Phase 5 — Commit and push
7. Stage explicitly:
   ```bash
   git add website/pages/blog/posts/{slug}.jsx \
           website/public/images/blog/{slug}-hero.webp \
           website/pages/blog/index.jsx
   ```
8. Commit: `git commit -m "publish: {Post Title}"`
9. Push: `git push origin main`

### Phase 6 — Merge to main
10. If on a feature branch, open a PR and merge it:
    ```bash
    gh pr create --title "publish: {Post Title}" --body "Publishes {slug}"
    gh pr merge --merge --auto
    ```
    If already on main, the push in Phase 5 is sufficient.

### Phase 7 — Vercel build verification
11. Wait ~60 seconds, then check the latest deployment:
    ```bash
    vercel ls --limit 1   # get deployment URL
    vercel inspect <deployment-url>   # confirm status = READY
    ```
    Or use the Vercel MCP tool `list_deployments` and confirm `state: READY`.
12. If the build fails, immediately brief the Developer with the build log and do not append to `publish-log.md` until fixed.
13. On success, append to `context/general-project-agent-context/publish-log.md`:
    ```
    {YYYY-MM-DD} — published: {Post Title} → {deployment-url}
    ```
