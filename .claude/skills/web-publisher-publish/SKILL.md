---
name: web-publisher-publish
description: >-
  Takes a finished blog post all the way to production — writes the App Router page, updates the blog index, commits, pushes, and confirms the Vercel deployment is healthy. The post is not done until the build is green. Owned by the developer agent. Use when the operator says "publish", "push the post live", or "build the page", or a finished post + hero image are waiting.
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

### Phase 2 — Code
4. Write the page at `website/app/blog/{slug}/page.tsx` (App Router):
   - `export const metadata` (or `generateMetadata`) with title, description, OG/Twitter, canonical
   - `next/image` for all images; read-time estimate in post header; category tag from style guide; Tailwind classes (no inline styles)
   - Follow the patterns of existing posts under `website/app/blog/`
5. Confirm `npm run build` passes clean

### Phase 3 — Index update
6. Add the post card at the top of the blog index (`website/app/blog/page.tsx`) — follow the existing card pattern exactly

### Phase 4 — Quality gate (run before commit)
- [ ] Page renders — correct TSX, no missing imports
- [ ] All images use `next/image` with correct `src`, `alt`, `width`, `height`
- [ ] `metadata` includes title, meta description, OG/Twitter tags
- [ ] Category tag matches a valid blog category
- [ ] Post card at top of blog index grid
- [ ] Read-time estimate in post header

### Phase 5 — Commit and push
7. Stage explicitly:
   ```bash
   git add website/app/blog/{slug}/page.tsx \
           website/public/images/blog/{slug}-hero.webp \
           website/app/blog/page.tsx
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
