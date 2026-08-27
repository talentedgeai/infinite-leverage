# Client setup — four prompts, in order

This guide is written for people who don't code — CEOs, sales, marketing. You never type
commands. You paste **four prompts into Claude Code, in order**, and Claude does the
typing. Each prompt ends by telling you which one to copy next, by name.

| # | Prompt | When |
|---|---|---|
| 0 | **Clean up** | Only if you've used Infinite Leverage before. Never used it? Skip. |
| 1 | **Install** | Everyone starts here. Takes a minute. |
| 2 | **Set up your accounts** | Claude walks you through creating each account, click by click. |
| 3 | **Create your project** | Your website and your six-person AI team, built in front of you. |

Every prompt follows the same rules: plain English, no jargon, no walls of output, one
question at a time, and Claude never asks you to edit a file — it makes the changes and
tells you what it did.

---

## Prompt 0 — Clean up (only if you've used Infinite Leverage before)

The old version 1 installed itself into a shared folder on your computer. Version 2
doesn't. This prompt quietly removes the old version's leftovers — and only those. It
tells you the plan in three sentences, then handles everything itself. "Removed" really
means moved to a dated backup folder, so nothing is ever truly gone, and anything it
can't positively identify as the old version is left alone.

```
I think I have an old version of Infinite Leverage on my computer. Please
clean it up for me and get me onto the current version.

I'm not a developer. Talk to me in plain, friendly English — no technical
terms, no file paths, no raw output. And I don't want to approve every
little step: for anything on the old-version lists below, just do it.

FIRST, TELL ME THE PLAN — THREE SENTENCES, TOPS
Have a quiet look around first (change nothing yet), then tell me simply:
- whether you found leftovers from the old version, or not
- what you're going to do about it, in one plain sentence — something like
  "I'll remove the old version's files and one leftover setting, then get
  you onto the current version."
- that nothing of mine will be touched
Then get on with it. Don't list files at me, and don't wait for a yes.

WHAT COUNTS AS THE OLD VERSION
(This list is for you — never read it back to me.)

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
    * a permission entry of exactly  Bash(*)
    * "defaultMode": "acceptEdits"
    * any hook pointing at ~/.claude/hooks/pre-bash, prompt-submit,
      session-start, session-telemetry-*, or telemetry-privacy-guard

WHAT TO DO — QUIETLY, WITHOUT ASKING ME STEP BY STEP
1. Fix the settings: make dated backup copies of both settings files next
   to the originals, then remove only the old-version entries listed above.
   Change nothing else in those files. Don't show me the edits — just do it.
2. Remove the old files: move everything matching the lists above into one
   folder, ~/.claude/il-v1-archive-<today>. When you talk to me, call this
   "removed" — the folder is just a safety net, and you'll mention it once
   at the end.
3. If something matches an old-version name but looks like I changed it
   myself, leave it where it is and note it for the summary. Don't
   interrupt me about it.
4. Get me onto the current version:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage
   If it says the plugin is already installed, update it instead:
     claude plugin update infiniteleverage@infiniteleverage
5. Run /il-doctor. If everything passes, just tell me "all checks passed."
   If something fails, tell me what it means in plain English and what you
   need from me — one thing at a time.

THE ONE RULE THAT NEVER BENDS
Anything in ~/.claude/ that is not on the lists above is MINE — my own
settings, my own skills, other tools I use. Leave all of it completely
alone. If you're not sure whether something is old Infinite Leverage or
mine, treat it as mine. That is the one thing worth stopping to ask me
about. Everything else, just handle.

WHEN YOU'RE DONE
Give me a short, friendly summary — three or four sentences, no jargon:
- what you cleaned up, or "your machine was already clean"
- that everything of yours was untouched, and a backup folder exists in
  case anything is ever needed back
- that you're now on the current version and all checks passed
Then my next step, worded like this: "Go back to the setup guide and copy
the prompt called 2 - Set up your accounts. If you still have your GitHub,
Supabase and Vercel accounts from before, you can skip ahead to 3 - Create
your project instead. Paste it right here in this chat — or in a new one,
both work."
Then stop and wait. Don't start setting up a project on your own.

IF YOU GET STUCK
Stop and tell me in plain English. Don't guess, don't remove anything extra
to get past an error, and don't tell me it worked if it didn't.
```

---

## Prompt 1 — Install

The shortest one. Claude installs Infinite Leverage, checks everything is healthy, and
tells you what to paste next. If it spots an old version 1 on the machine, it stops and
sends you to Prompt 0 first.

```
Please install Infinite Leverage for me.

I'm not a developer. Plain English only — no jargon, no raw output. Tell me
what's happening in one sentence as you go, and only ask me something if
you truly need me.

1. First, a quick silent check: look for leftovers of the old version 1 —
   things like ~/.claude/.infiniteleverage-version, an il_telemetry folder
   inside ~/.claude/hooks, or files like product-manager.md and
   web-publisher.md inside ~/.claude/agents. If you find any, change
   nothing and tell me: "You have an older version on this computer. Go
   back to the setup guide and copy the prompt called 0 - Clean up, and
   paste it right here." Then stop.
2. Check the basic tools are present: git, the GitHub tool (gh), Node,
   rsync, perl. If something's missing and you can install it safely with
   my package manager, ask me once with a one-line reason, then handle it.
3. Install the plugin:
     claude plugin marketplace add talentedgeai/infinite-leverage
     claude plugin install infiniteleverage@infiniteleverage
   If it says the plugin is already installed, update it instead:
     claude plugin update infiniteleverage@infiniteleverage
4. Run /il-doctor. If everything passes, just say "all checks passed."
   (It may mention GitHub sign-in — that's fine, we handle it in the next
   step. Don't try to sign me in now.)
5. Then tell me, exactly: "Installed. Next: go back to the setup guide and
   copy the prompt called 2 - Set up your accounts. Paste it right here."
Then stop and wait.

IF YOU GET STUCK
Stop and tell me in plain English what you need. Don't guess, and don't
tell me it worked if it didn't.
```

---

## Prompt 2 — Set up your accounts

The learning step. Your project needs a few free accounts, and this prompt turns Claude
into a patient guide: what each account is for in one sentence, exactly where to click,
one account at a time, checking each one worked before moving on. Nothing is installed
or changed on your computer here — it's all in your web browser, except the GitHub
sign-in at the end of step 1.

```
Help me set up the accounts my project needs. I'm not a developer — be a
patient guide. Plain English, one account at a time, and don't move to the
next until we've confirmed the current one works.

For each account, do it in this exact shape:
- one sentence on what it is and why my project needs it
- numbered steps: exactly where to go and what to click
- what to type into any field that isn't obvious
- then confirm it worked — check it yourself where you can, otherwise ask
  me what I see on screen

Go in this order:

1. GitHub — where my project's files live, like a shared drive with full
   history.
   - Ask me first: "Do you already have a GitHub account?" If not, walk me
     through creating one at github.com, step by step.
   - Then connect this computer to it: tell me to type  gh auth login  in
     the terminal, and guide me through each question it asks (GitHub.com,
     HTTPS, sign in with the web browser). Stay with me through it.
   - You confirm it worked by running: gh auth status
2. Supabase — my project's database and its sign-in system.
   - Walk me through creating an account at supabase.com (signing in with
     GitHub is the easy path), then creating ONE new project. Tell me
     exactly what to click and what to name things.
   - Tell me to save the database password it shows me somewhere safe, and
     that we'll come back for the project's keys in the next prompt — today
     we just need the project to exist.
3. Vercel — puts my website on the internet.
   - Walk me through creating an account at vercel.com. Signing up with my
     GitHub account is one button, and that's all we need today.
4. Stripe — for taking payments. Ask me first: "Will your project charge
   customers money? If no, or not sure yet, we skip this — it can be added
   any time." Only walk me through stripe.com if I say yes.

After each account, show me a short tick-list of what's done and what's
next. When everything is done, tell me, exactly: "Accounts ready. Next: go
back to the setup guide and copy the prompt called 3 - Create your
project. Paste it right here."
Then stop and wait.

IF ANYTHING GOES WRONG
Tell me what happened in plain English and what to try — never just show
me an error.
```

---

## Prompt 3 — Create your project

The build. Fill in the two highlighted lines (and describe your business in a sentence
or two), paste it, and Claude scaffolds the project, connects your accounts one key at a
time, and finishes by telling you the first three things to try.

```
Create my first Infinite Leverage project. I'm not a developer — plain
English only, no jargon, no raw output. One question at a time. Never ask
me to edit a file; you make the changes and tell me what you did.

1. Run /il-project to build my project:
   - Call it: <PROJECT NAME>
   - Folder name: <project-name-with-dashes>
   <Describe your business in a few sentences — what it does, who it's for,
   what you want built first. Mention a website you like the look of if you
   have one. Delete this line to answer questions later instead.>
   While it runs, keep me posted with one plain sentence per stage — no
   command output.
2. Then connect the accounts I made earlier, one key at a time:
   - Tell me exactly where to click to find each key (I already have the
     accounts), I'll paste the value to you, and you put it in the right
     file.
   - After that, confirm to me that the file holding my keys stays private
     on my computer and can never end up on GitHub.
3. Check the project builds. If something fails, fix it yourself if you
   can; otherwise explain in plain English what you need from me.
4. Ask me: "Want your project on GitHub now? It stays private, and it's
   how your site goes live later." Only do it if I say yes.
5. When everything's done, tell me in plain English:
   - what you built and where it lives on my computer
   - the three things I should try first, as things I can paste — starting
     with:  @product-manager let's plan the first feature
Then stop and wait.

IF YOU GET STUCK
Stop and tell me in plain English. Don't guess, and don't tell me
something worked when it didn't.
```

---

## Your team, once it's built

Six AI teammates live inside your project. Talk to them like colleagues — plain
English. Name one directly with `@`, or just describe what you want and the right one
picks it up.

| Teammate | What to ask them |
|---|---|
| **product-manager** | "what should we build next", plans, specs, "where are we" |
| **developer** | building features, fixing bugs, putting posts on the site |
| **qa** | "check this works", testing, sorting out bug reports |
| **devops** | "is the site up", deployments, rolling back a bad release |
| **writer** | blog posts, marketing copy, email campaigns |
| **designer** | brand look and feel, images, "does this page look right" |

House rules they all follow, so you don't have to police them: nothing is saved to the
project history unless you ask, nothing goes live without a review step, and **no email
is ever sent** — the writer drafts, you press send.

## What the commands actually do

You never need to memorise these — the prompts run them for you. This table exists so
none of it feels like magic.

| Command | In plain English |
|---|---|
| `claude plugin marketplace add talentedgeai/infinite-leverage` | Tells Claude Code where Infinite Leverage lives. Run once, ever. |
| `claude plugin install infiniteleverage@infiniteleverage` | Installs Infinite Leverage. |
| `claude plugin update infiniteleverage@infiniteleverage` | Gets the newest version, if it's already installed. |
| `/il-doctor` | A health check. Says what's missing or out of date, and how to fix it. |
| `/il-project` | Builds a new project: the folder, the website, and your six AI teammates. |
| `gh auth login` | Signs this computer in to your GitHub account. The one command you type yourself, because it opens your browser to prove it's really you. |
| `@product-manager …` | Talks to one teammate directly. Works with any of the six names. |
| `npm run build` | Test-assembles the website to prove nothing is broken. Claude runs it for you. |

## If something looks wrong

Paste this, any time:

```
Something's not working with my Infinite Leverage setup. Run /il-doctor,
tell me what's wrong in plain English, fix what you can yourself, and walk
me through anything that needs me — one step at a time.
```

The most common causes, for the curious:

| What you see | What it usually means |
|---|---|
| The teammates don't respond | They live inside each project — make sure you opened the project folder in Claude Code. |
| Something about GitHub sign-in | Run through the GitHub step of Prompt 2 again — signing in is the one thing only you can do. |
| The site won't build after setup | A key is missing or mistyped — Prompt 3's key step, run again, fixes it. |
