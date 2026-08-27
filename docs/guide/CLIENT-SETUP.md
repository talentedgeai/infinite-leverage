# Client setup — install Infinite Leverage and scaffold the first project

Two commands to install, one to scaffold. About 15 minutes, most of it `npm install`.

---

## Before you start

You need these on your machine. `/il-doctor` checks all of them, so you can just install
what it flags rather than working through this list first.

| Tool | Check | If missing (macOS) |
|---|---|---|
| Git | `git --version` | `xcode-select --install` |
| GitHub CLI, signed in | `gh auth status` | `brew install gh` then `gh auth login` |
| Node 20+ with npm/npx | `node --version` | `brew install node` |
| rsync | `rsync --version` | `brew install rsync` |
| Perl | `perl --version` | ships with macOS |

Accounts you'll want, though not on day one: **GitHub** (required), **Supabase**
(database and auth), **Vercel** (hosting), **Stripe** (only if the project takes payments).

---

## Step 1 — Install the plugin

In any terminal:

```bash
claude plugin marketplace add talentedgeai/infinite-leverage
claude plugin install infiniteleverage@infiniteleverage
```

## Step 2 — Check the install

Open Claude Code and run:

```
/il-doctor
```

Every line should be `✅ PASS`. It also tells you if your plugin is behind the latest
release — worth doing before a workshop, because `/il-project`'s own instructions ship
inside the plugin. To update:

```bash
claude plugin update infiniteleverage@infiniteleverage
```

## Step 3 — Scaffold the project

```
/il-project
```

It asks for a project slug and display name, previews what it will do, then runs to
completion. It takes several minutes — most of that is installing the Next.js app.

**Bring what you have.** Paste a product brief, a PRD, meeting notes, or just a few
paragraphs describing the product into the same message. It uses that to fill
`docs/product/`. Mention a design reference too ("make it like Linear", or your brand
colours) and it fills `docs/brand/`. Both are optional — with nothing, you get
placeholders and a design picked for you.

At the end it asks once whether to create a GitHub repo and push. You can say no and do it
later.

---

## Step 4 — Add your keys

```bash
cd <your-project>/website
cp .env.local.example .env.local
```

Open `.env.local` and fill it in — it lists every variable the app reads and where to get
each one. `.env.local` is gitignored; the example is not. Never commit real keys.

Then confirm it compiles:

```bash
npm run build
```

## Step 5 — Start working

Open the project in Claude Code. You now have six agents. Talk to them in plain English —
routing is automatic, but you can also name one directly with `@product-manager`.

```
@product-manager let's plan the first feature
```

A good first session:

1. **`pm-client-interview`** — a structured conversation about the business. Its output
   becomes `docs/product/product.md`, which everything else is anchored to. Skip it only
   if step 3 already filled that file from your brief; then run **`pm-grill-with-docs`**
   to check it instead.
2. **`pm-epic-writing`** — turn one idea into a spec with acceptance criteria.
3. **`pm-to-issues`** — break it into GitHub issues.
4. **`@developer`** — build the first one, test-first.

---

## The team

| Agent | Ask it about |
|---|---|
| **product-manager** | roadmap, specs, epics, "where are we", the status dashboard |
| **developer** | writing code, fixing bugs, publishing posts to the site |
| **qa** | testing, bug triage, "verify this works" |
| **devops** | CI/CD, deployments, "is the site up", rolling back |
| **writer** | blog posts, SEO, marketing strategy, email campaigns |
| **designer** | brand system, images, accessibility and UI review |

**Rules they follow, so you don't have to police them:** nothing is committed unless you
ask, nothing is pushed to `main` directly (everything goes through a pull request), and
**no email is ever sent** — the writer drafts it and you run the send.

---

## The install prompt

If you'd rather not run the commands yourself, paste this into a Claude Code session and
it will walk you through it:

```
Install the Infinite Leverage plugin and set up my first project.

1. Check I have what's needed: git, gh (authenticated), node, npm, npx, rsync, perl.
   Tell me exactly what to install if anything is missing — don't install it for me,
   and don't run `gh auth login` for me, since that's interactive.

2. Add the marketplace and install the plugin:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage

3. Run /il-doctor and show me the output as-is. If anything FAILs, tell me the fix
   and stop — don't work around it.

4. Once it's clean, run /il-project to scaffold my project.
   - Project name: <YOUR PROJECT NAME>
   - Slug: <your-project-slug>
   - Put it in: ~/code-projects
   [Paste your product brief here, or a few paragraphs about what you're building.
    Mention a design reference if you have one — e.g. "make it look like Linear".
    Delete these two lines if you have nothing yet.]

5. When it finishes, show me the summary and tell me what to do next.
   Don't create the GitHub repo yet — ask me first.
```

Replace the bracketed parts before pasting. Everything in it is optional except the
project name and slug.

---

## If something goes wrong

Run `/il-doctor` first — it names the fix for most problems.

| Symptom | Cause |
|---|---|
| "No agents responding" | agents install per project — check `.claude/agents/` has 6 files, or re-run step 6 of `/il-project` |
| `gh` not authenticated | run `gh auth login` yourself; the agents won't do it for you |
| Build fails on missing env vars | `.env.local` is incomplete — compare against `.env.local.example` |
| CI red on a fresh project | check the GitHub secrets named in `devops-cicd` match your `.env.local` |

More in [`troubleshooting.md`](troubleshooting.md).
