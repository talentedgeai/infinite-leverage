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

Already have it installed? `install` won't upgrade an existing plugin — update instead:

```bash
claude plugin update infiniteleverage@infiniteleverage
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

## Prompt 0 — already installed an older version?

Use this **before** the install prompts if there's any chance an older Infinite Leverage
is on the machine. It detects which of two situations applies and handles either:

- **v1 residue** — v1 installed itself into `~/.claude/` (v2 never does; it only writes
  inside your project). That residue includes a `Bash(*)` permission grant, which is the
  reason v2 exists and the one thing worth fixing even if nothing else is touched.
- **v2, just out of date** — nothing to clean, only a plugin update.

**Edge8-internal only:** if `/edge8-telemetry` is installed, run that instead. It carries
`migrate_v1.py`, which removes only byte-exact copies of files v1 shipped, verified by
hash against a manifest built from both v1 repos' full git history, and reports anything
locally modified instead of deleting it. The prompt below is the careful manual
equivalent for everyone else.

```
I may have an older version of Infinite Leverage installed. Please check,
explain what you find in plain English, and fix it.

I'm not a developer. Plain English only, no raw errors, one question at a
time, never ask me to edit a file myself — and never delete anything without
showing me first and waiting for me to say yes.

STEP 0 — LOOK ONLY. CHANGE NOTHING YET.

Version 1 installed itself into my home folder. Version 2 never does — it
only ever writes inside a project folder. So anything below in ~/.claude/ is
v1 residue:

- ~/.claude/agents/ containing any of: designer.md, developer.md, devops.md,
  email-marketer.md, product-manager.md, qa.md, web-publisher.md, writer.md
- ~/.claude/hooks/ containing any of: pre-bash, prompt-submit, session-start,
  usage-context.py, update-project-status-usage.py, or an il_telemetry folder
- ~/.claude/.infiniteleverage-version
- ~/.claude/skills/ containing anything whose name starts with
  infiniteleverage-, pm-, dev-, devops-, qa-, writer-, designer-,
  web-publisher-, email-marketer-, scaffold-, or speckit- ... or is exactly
  one of: pm, dev, devops, qa, writer, designer, web-publisher,
  email-marketer, marketing-strategist, plan-protocol, github-flow,
  global-caveman, seo-audit, session-ingest, use-dev-team,
  use-marketing-team, create-agent, create-local-routine,
  create-local-task, create-remote-routine
- In ~/.claude/settings.json and ~/.claude/settings.local.json:
    * a permission entry of exactly  Bash(*)        <-- most important
    * "defaultMode": "acceptEdits"
    * any hook pointing at ~/.claude/hooks/pre-bash, prompt-submit,
      session-start, session-telemetry-*, or telemetry-privacy-guard

Also check whether the v2 plugin is installed and current:
    claude plugin list
and compare against the newest release tag of
talentedgeai/infinite-leverage.

Now tell me, in plain English: what you found, what each thing does, and
which of these two I'm in —
  CASE A: v1 leftovers found        -> we clean up, then install v2
  CASE B: no leftovers, just old/absent v2 -> we only install or update

ANYTHING NOT ON THOSE LISTS IS MINE
~/.claude/ is also where I keep my own settings, my own skills, and other
plugins. If you can't match something to the lists above, it is mine — leave
it alone, even if the name looks similar. When in doubt, ask me.

CASE A — CLEAN UP FIRST

1. The permission grant first, because it's the one that actually matters.
   Back up both settings files (copy them next to themselves with today's
   date in the name). Then remove ONLY:
     - the  Bash(*)  entry from the permissions allow list
     - "defaultMode": "acceptEdits"
     - the v1 hook registrations listed above
   Leave every other setting exactly as it is. Show me the before and after
   for each file and explain what Bash(*) was letting through.

2. Don't delete the leftover files — move them. Make one folder named
   ~/.claude/il-v1-archive-<today's date> and move the v1 agents, hooks and
   skills into it, keeping their folder names. Then tell me plainly:
   "nothing was deleted, it's all in that folder if we need it back."

3. If any file's name matches the list but you can tell I've edited it
   myself, leave it where it is and tell me — don't move it.

4. Write me a short list of what moved and what you changed.

CASE B — JUST UPDATE

     claude plugin update infiniteleverage@infiniteleverage

BOTH CASES END THE SAME WAY

5. Make sure the current version is installed:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage
   If it says the plugin is already installed, update it instead:
     claude plugin update infiniteleverage@infiniteleverage
6. Run /il-doctor and tell me whether every line passes.
7. Tell me whether any project folder on my machine still needs its agents
   refreshed, and how I'd do that. Don't do it without asking.

WHEN YOU'RE DONE
Finish with a short message that tells me, in plain English:
- what you found and what you changed — or "nothing needed cleaning up"
- that my machine is now ready for a fresh setup
- my exact next step, worded like this: "Go back to the setup guide and
  copy the prompt called A - Hands-off (or B - Guided if you'd rather run
  the commands yourself). Fill in your project name, then paste it right
  here in this chat — or in a new one, both work."
Then stop and wait. Don't start setting up a project on your own — the
next prompt handles that.

IF YOU GET STUCK
Stop and tell me. Don't guess, don't delete anything to get past an error,
and don't tell me it worked if it didn't.
```

**When it finishes**, it hands the client to the next step itself: it tells them to come
back to this guide and copy Prompt A (or B). Cleanup and setup stay two separate prompts
on purpose — one conversation that both deletes old files and scaffolds a new project is
harder for a non-technical client to follow, and harder to stop halfway.

**What this deliberately does not do:** it never clears `~/.claude/skills/` wholesale.
Most people keep their own skills there, and v1's had ordinary names — the only safe
signal is the name pattern plus the location. It also archives by renaming rather than
deleting, so a wrong guess costs a folder move, not your work.

---

## Prompt A — hands-off (for a non-technical client)

Paste this into Claude Code and it does everything it's allowed to do, stopping only for
the handful of things that genuinely need a human.

**What Claude cannot do for you, no matter how the prompt is worded:** sign in to GitHub
(`gh auth login` is an interactive flow), create accounts, or copy keys out of a
dashboard. Those need you. The prompt front-loads them so you're not interrupted later.

```
I'm not a developer. Please set up Infinite Leverage for me, and do as much of
it yourself as you can.

HOW TO WORK WITH ME
- Plain English only. No jargon. Never paste a raw error at me — tell me what
  it means and what you need from me.
- Don't show me long command output. Just tell me what happened.
- One question at a time, then wait for my answer.
- Never ask me to edit a file. Tell me what to paste, and you make the change.
- If you need my permission to run something, say in one sentence what it does,
  then go ahead.

THINGS ONLY I CAN DO
You're not allowed to do these for me. When you reach one, stop, give me
click-by-click instructions, and wait for me:
- Signing in to GitHub (gh auth login)
- Creating accounts — GitHub, Supabase, Vercel, and Stripe if I need payments
- Copying keys out of those dashboards

Everything else is yours.

START HERE
Before anything else, tell me which accounts I'll need and let me go create
them. Don't start installing until I say I'm ready.

THEN
1. Install the plugin:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage
   If it says the plugin is already installed, update it instead:
     claude plugin update infiniteleverage@infiniteleverage
2. Run /il-doctor. Fix whatever you can fix yourself. For anything you can't,
   walk me through it, then run it again until every line passes.
3. Run /il-project to build my project:
   - Call it: <PROJECT NAME>
   - Folder name: <project-name-with-dashes>
   <Describe your business here in a few sentences — what it does, who it's
   for, what you want to build first. Mention a website you like the look of
   if you have one. Delete this line if you'd rather answer questions later.>
4. Set up my keys. Tell me exactly where to click to find each one, I'll paste
   the values to you, and you put them in the right file. Confirm afterwards
   that the file with my keys in it is not going to end up on GitHub.
5. Check that the project builds.
6. Do not put anything on GitHub until you've asked me first.

WHEN YOU'RE DONE
Tell me, in plain English: what you built, where it is on my computer, and the
three things I should try first. Keep it short.

IF YOU GET STUCK
Stop and tell me. Don't guess, don't invent a workaround, and don't tell me
something worked when it didn't.
```

Replace `<PROJECT NAME>`, `<project-name-with-dashes>`, and the description block. Nothing
else needs editing.

## Prompt B — guided (you run the commands)

If you'd rather stay in control and just be walked through it:

```
Install the Infinite Leverage plugin and set up my first project.

1. Check I have what's needed: git, gh (authenticated), node, npm, npx, rsync, perl.
   Tell me exactly what to install if anything is missing — don't install it for me,
   and don't run `gh auth login` for me, since that's interactive.

2. Add the marketplace and install the plugin:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage
   If it says the plugin is already installed, update it instead:
     claude plugin update infiniteleverage@infiniteleverage

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
