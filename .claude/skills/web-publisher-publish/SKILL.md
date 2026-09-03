---
name: web-publisher-publish
description: >-
  Takes a finished blog post all the way to production — writes the App Router page, updates the blog index, commits on a publish branch, opens a PR, and confirms the Vercel deployment is healthy. Never commits or pushes on main. The post is not done until the build is green. Owned by the developer agent. Use when the operator says "publish", "push the post live", or "build the page", or a finished post + hero image are waiting.
---

# Web Publisher: Publish Post

## Discovery
```bash
ls -1t content/topics/   # newest first
```
Topic folders are named `{YYYY-MM-DD}-{slug}`. **`{slug}` is the `Slug` field in the
folder's `seo.md`** (it equals the folder name minus the date prefix). Find the first
folder that has both `blog.md` AND `{slug}-hero.webp` but NO page at
`website/app/blog/{slug}/page.tsx`. Nothing matches → say so and stop; do not publish a
placeholder post.

## Phase 0 — Branch first

Never work, commit, or push on `main` — `.claude/rules/global-engineering.md` forbids it,
and the branch is what gives you a Vercel preview to check before the post goes live.
Publishing branches are named `publish/{slug}` (the `feat/…` convention in
`developer.md` is for feature work; `agent-routing.md` rule 4 names `publish/`).

```bash
git switch main && git pull
git switch -c publish/{slug}
cd website && npm install && npm run build && cd ..   # build once: Next generates the route types `tsc` needs
```

## Phase 1 — Content assembly
1. Read `blog.md` and `seo.md` — full content + front matter + SEO metadata
2. Read `docs/brand/style-guide.md` — the **Blog posts** entry under *Content formats*
   holds the post shape and the list of valid categories; *Visual style* holds the look.
   If the style guide is still the unfilled template, note it, use the category named in
   `blog.md`'s byline, and flag in the PR that the category list is unconfirmed
3. Copy `{slug}-hero.webp` to `website/public/images/blog/`

## Phase 2 — Code
4. Write the page at `website/app/blog/{slug}/page.tsx` (App Router):
   - `export const metadata = buildMetadata({ title, description, path: "/blog/{slug}", ogImage: "/images/blog/{slug}-hero.webp" })` from `@/lib/seo/metadata` — that gives title, description, canonical and OG/Twitter in one call, resolved against `NEXT_PUBLIC_SITE_URL`
   - `next/image` for all images (hero is 1200×630); read-time estimate in the post header computed from the body word count at ~200 wpm (do not copy a hand-written number from `blog.md`); category tag; Tailwind classes (no inline styles)
   - **First post in the project?** There are no existing posts to copy. Use a single
     `<article>` with `<header>` (h1, byline with date · category · read time), the hero
     image, then the body as semantic HTML. Later posts follow whatever the first one
     established
5. Add the route to `website/app/sitemap.ts` (`/blog` once, then `/blog/{slug}` per post)
6. Confirm `npm run build`, `npm run lint` and `npx tsc --noEmit` pass — build first

## Phase 3 — Index update
7. Add the post card at the top of the blog index `website/app/blog/page.tsx` — follow
   the existing card pattern exactly. **No index yet?** Create it: a heading and a grid of
   cards (hero thumbnail, title linking to the post, date · category · read time, meta
   description). That file is then the pattern for every later publish.

## Phase 4 — Quality gate (run before commit)
- [ ] Page renders — `npm run build` prerenders `/blog/{slug}` with no error
- [ ] All images use `next/image` with correct `src`, `alt`, `width`, `height`
- [ ] `metadata` includes title, meta description, canonical, OG/Twitter tags
- [ ] Category tag is one listed in `docs/brand/style-guide.md` (or flagged as unconfirmed, see Phase 1)
- [ ] Post card at top of blog index grid
- [ ] Read-time estimate in post header, computed from the word count
- [ ] `/blog/{slug}` present in the sitemap

## Phase 5 — Commit and push the branch
8. Stage explicitly (never `git add .` / `-A`). The source content ships with the post —
   the topic folder is the record of what was published:
   ```bash
   git add website/app/blog/{slug}/page.tsx \
           website/app/blog/page.tsx \
           website/app/sitemap.ts \
           website/public/images/blog/{slug}-hero.webp \
           content/topics/{YYYY-MM-DD}-{slug}/
   ```
9. Commit: `git commit -m "publish: {Post Title}"`
10. Push the branch: `git push -u origin publish/{slug}`

## Phase 6 — Open the PR, then let the merge rule decide

11. Open the PR:
    ```bash
    gh pr create --base main --title "publish: {Post Title}" --body "Publishes {slug}: {one-paragraph plain-English summary}. Preview: {URL once Vercel reports it, else 'no Vercel project linked yet'}"
    ```
12. Merge only under the **auto-merge eligibility** rules in `.claude/agents/developer.md`.
    A content-only post — new blog route + hero image + index card + sitemap line, no new
    deps, no schema/auth/env/API change — on a clean branch **with green CI** qualifies:
    ```bash
    gh pr merge --squash --delete-branch
    ```
    Two things stop it here, and both are normal on a young project:
    - **The repo has no CI** (`ls .github/workflows` is empty) — "CI green" cannot hold,
      so auto-merge never fires. Leave the PR open, tell the operator, and point at
      `devops-cicd` to add the pipeline.
    - **Anything beyond content** — a component change, a new dependency, a layout edit,
      the very first blog index — leave the PR open with the plain-English summary and
      tell the operator it needs their approval.

    Never merge on red CI. Record an auto-merge as a row in
    `context/general-project-agent-context/publish-log.md` with `auto-merged` in the
    Category column note, and in the PR body.

## Phase 7 — Vercel build verification

13. **Only if the site is linked to a Vercel project** — `website/.vercel/project.json`
    exists (or `vercel link --yes` succeeds against an existing project). Unlinked,
    `vercel ls` lists *every* deployment in the account and will happily report a
    stranger's project as READY. No link → stop here, hand the operator the PR URL, and
    say the preview cannot be verified until the repo is connected to Vercel
    (`devops-ops` covers the link). Do not create or link a project yourself.
14. Linked: wait ~60 seconds, then check the deployment for **this branch**:
    ```bash
    cd website && vercel ls --limit 5          # find the deployment whose branch is publish/{slug}
    vercel inspect <that-deployment-url>       # confirm status = READY
    ```
    Or use the Vercel MCP tool `list_deployments` filtered to this project and confirm
    `state: READY`. If the PR is still open (Phase 6 stopped for approval), that
    deployment is the **preview** — hand its URL to the operator; the post is not live
    until they merge.
15. If the build fails, read the log, fix the root cause on the same branch, push again,
    and do not log the post until it is green.
16. On success (preview READY, or production READY after a merge), append a row to
    `context/general-project-agent-context/publish-log.md`:
    ```
    | {YYYY-MM-DD} | {Post Title} | website/app/blog/{slug}/page.tsx | {Category} — {preview|production}: {deployment-url} |
    ```
