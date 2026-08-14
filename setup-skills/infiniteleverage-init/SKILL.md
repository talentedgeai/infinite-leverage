---
name: infiniteleverage-init
description: Set up the Infinite Leverage stack on any machine — one guided flow from a signed-in Claude Desktop to a live site, an 8-agent team, and a Claude that works autonomously (SQL, PRs, deploys). Handles macOS, Windows (WSL2), corporate machines (cloud track), fresh installs, reuse of a previous stack, and additional machines. Every human step is called out with its reason and verified.
---

# Infinite Leverage — Stack Setup

## Read me first (instructions to Claude)

You are running the Infinite Leverage stack setup. The person in front of you may be completely non-technical. Your job:

- **Do every step a computer can do yourself.** Installing, configuring, writing files, running commands, copying values, verifying. If you find yourself about to ask the human to paste SQL, run a command, or click a deploy button, stop: that is either a step you should do, or a gate below that you should present properly.
- **The human does only the gates.** Each gate in this guide has three parts, always delivered together: **what to do** (numbered clicks), **why it's yours** (one sentence), and **verify** (a real check you run after they say done; never trust "done" without it).
- **Plain English, one step at a time.** No jargon, no code shown unless asked. Say what you're doing and what just succeeded.
- **Never delete anything.** Not files, not folders, not repos, not cloud projects. Archiving (renaming into an archive folder) is the strongest action you may take, and only in the fresh-start fork.
- **Secrets live in `website/.env.local` and Vercel's environment settings. Nowhere else.** Never in CLAUDE.md, never in git, never echoed into chat.

---

## The end state: the autonomy contract

Setup is done when Claude on this machine holds these standing powers, proven by the graduation lap in Stage F, not merely installed:

| After setup, Claude does this alone | Because of | The one human grant |
|---|---|---|
| Runs any SQL: creates tables, applies migrations, seeds and queries data | The Supabase connection (MCP), plus the service key in `.env.local` for the app itself | One Authorize click on the Supabase consent screen (Gate 4) |
| Branches, commits, pushes, opens PRs, merges PRs | The GitHub CLI signed in as the operator | One browser sign-in for `gh auth login` (Gate 2) |
| Deploys by pushing, then watches the build and confirms the live site | The git-push-to-Vercel pipeline, plus the Vercel CLI (read-only) for status and logs | One Vercel sign-in (Gate 3) plus the one-time repo import click (Gate 5) |
| Edits files and runs commands without per-step permission prompts | Claude Code's permission settings on this machine | One deliberate choice at Gate 0 |
| Sends email from code (from Build 2 onward) | The Resend key in `.env.local` | Deferred: the operator mints the key when the email feature is built |

Nothing on this list is granted twice, and nothing outside it is needed to run the workshop builds. A build block that stalls asking for a credential means a grant above is missing; the graduation lap exists to catch that here, not there.

---

## The manual moments, and why

Two different reasons a step belongs to the human. Keep them distinct when you explain.

**Claude cannot, by rule and by design:**

| Moment | Why (say it in these terms) |
|---|---|
| Creating accounts (GitHub, Vercel, Supabase, later Resend) | Sites require a human to accept their terms, pass the robot check, and verify an email. The accounts must belong to you, not to an AI session. |
| Typing any password, anywhere | Claude never sees or handles passwords, full stop. |
| Entering 2FA codes | The code goes to your phone; that's the entire point of 2FA. |
| Buying a domain or choosing a paid plan | Spending your money is always your decision and your click. |

**Claude technically could, but should not, so the human does it deliberately:**

| Moment | Why it stays human |
|---|---|
| The permission setting (Gate 0) | This one choice defines how much the AI may do unsupervised on this machine. It is made knowingly, once, by the operator, never defaulted by a script. |
| The Authorize clicks on consent screens (GitHub, Vercel, Supabase) | Each click is a standing grant of access to your code, deployments, or data. The click is the contract; consenting on your own behalf is not delegable. |
| Minting API keys | Creating a credential decides its blast radius. The operator creates it while Claude watches; Claude carries it into `.env.local` and nowhere else. |
| Approving DNS records | Standing changes to your domain sit behind your registrar login and outlive any session. |

---

## Step 0 — Triage: three checks before anything

Run these in order, before installing or explaining anything.

### Check 1 — Where am I running?

Try to run a trivial command (`echo ok`). If you can run commands, continue here. If you cannot (this guide was pasted into a chat with no computer access), treat this machine as one that can't be set up directly and follow **`references/cloud-track-codespaces.md`** with the user in their browser. Do not attempt any local step from a chat surface.

### Check 2 — What machine is this?

Detect, don't ask. Run the detection snippet from **`references/os-detection.md`** yourself, silently, and act on the verdict:

- **macOS at or above the floor** → local setup, continue.
- **Windows** → ask exactly one question first: *"Is this your own computer, or one your company manages?"*
  - **Own machine** → the Ubuntu (WSL2) path. If WSL2 is already present (`wsl.exe --status` succeeds from the Windows side, or you're already inside Ubuntu), continue. If not, run the Windows gates (W1–W3 below).
  - **Company-managed** → do not attempt any local install, not even WSL2. Check the browser can reach claude.ai and github.com. Reachable → cloud track (`references/cloud-track-codespaces.md`). Blocked → stop and say plainly: *"This machine's restrictions mean it can't run the setup. You'll need a loaner or a personal machine — your company's IT policy is the blocker, not anything we did."*
- **Below the version floor** (old macOS, Windows that can't run WSL2) → cloud track. Don't fight the machine.
- **Native Windows shell with WSL2 available but unused** → never offer native as an option. Say: *"Claude Code runs on native Windows, but the Infinite Leverage team system around it is built on a Unix shell, so on Windows the team runs inside Ubuntu — a free Windows feature. It's a one-time ten-minute setup."* Then run gates W1–W3.

### Check 3 — What's already here?

Scan for evidence before asking anything:

```bash
ls ~/.claude/agents/ 2>/dev/null | wc -l                    # 8 = team installed
cat ~/.claude/.infiniteleverage-version 2>/dev/null          # version stamp
ls ~/code-projects/ 2>/dev/null                              # project folders
grep -l "Project Catalog" ~/code-projects/*/CLAUDE.md 2>/dev/null   # catalog projects
gh auth status 2>&1 | head -2; vercel whoami 2>&1 | head -1  # standing grants
```

Classify into one of five states and follow its path. Present what you found in plain English first ("I found a working setup from June: 8 agents, a project called X, and a live site at Y"), then ask only the question that state requires.

| Evidence found | State | Path |
|---|---|---|
| Nothing | **Clean machine** | Run the full flow, Stage A onward |
| Some pieces, incomplete (tools but no agents, folder but no repo, repo but no live site) | **Half-finished** | Resume: report what's done and what's next, continue from the first failing check. Redo nothing that verifies. |
| Everything verifies | **Working stack** | Ask: *"Keep building on this, or start a new project alongside it?"* Keep → verify each stage's checks, repair only failures, then run `/infiniteleverage-patch` to bring it current, then jump to Stage D if they want a new project wired, or finish. |
| Everything verifies, user wants to start over | **Fresh alongside** | Archive the old project folder to `~/code-projects/archive/<slug>-<date>/` (rename, never delete). Leave every cloud resource untouched and say so: *"Your old project is archived at this path. Nothing was deleted; the old site stays live until you take it down yourself."* Then run the flow; the machine layer (Stage C) will verify and skip. |
| Nothing local, but the user says the team already exists on another machine | **Additional machine (Mode B)** | See the Mode B section near the end. No infrastructure creation, no schedule registration. |

Reuse is not a second procedure: because every stage below ends in a verify, running this same flow on a non-empty machine naturally skips what passes and repairs what fails.

---

## Settings Safety Protocol

Before writing any configuration file — `settings.local.json`, `CLAUDE.md` (global or project), `global-engineering.md`, `.env` — check what's already there:

| Scenario | Action |
|---|---|
| File exists with compatible content | **Merge** — add what's missing without removing what's there |
| File exists and is a complete previous version of this template | **Upgrade** — replace with the latest version |
| File exists with conflicting content | **Resolve** — preserve the user's value and intent while satisfying the template. If you can't do both, ask, in plain language, offering: keep theirs, use the template's, or combine |

This protocol explicitly covers the **project CLAUDE.md**: if the project folder already contains a catalog CLAUDE.md written by the product-plan interview (Block I of the workshop), the scaffold's CLAUDE.md content is merged *into* it. The interview's catalog and rules are never overwritten; scaffold sections are added. The interview file wins on conflict.

When asking about a conflict, plain language only — say what the setting does, not what it's called.

---

## Canonical source

Everything lives in one repo — the single source of truth:

> https://github.com/talentedgeai/infiniteleverage-8-agents-template

| What | Where |
|---|---|
| 8 agent definitions | `.claude/agents/*.md` |
| Global skills | `.claude/skills/*/SKILL.md` |
| Engineering rules | `.claude/rules/global-engineering.md` |
| Project scaffold | `templates/project-scaffold/` (spec: `FOLDER-STRUCTURE.md`) |
| This skill, its prompt, and references | `setup-skills/infiniteleverage-init/` |

Rules, non-negotiable:

1. **Never hand-edit agents, skills, or scaffold files on a client machine.** Changes go to the canonical repo by PR, get released, and reach machines via `/infiniteleverage-patch`.
2. **The plugin (`talentedgeai/infiniteleverage-plugin`) carries no skills.** It is a runtime shim: session advisory, routing hints, telemetry hooks. If you find skill files inside an installed copy of it, they are from an old version; the local `~/.claude/skills/` copies installed by this flow are the ones that count.
3. **Consume `stable`, not `main`.** When fetching anything from the canonical repo at runtime, use the `stable` branch — it moves only at releases.
4. When in doubt, fetch fresh: `gh repo clone --depth 1 -b stable talentedgeai/infiniteleverage-8-agents-template /tmp/il-template`

---

## The flow

Stages A through F, in order, in one session. Each stage ends with its verify; a verified stage is never redone.

### Gate 0 — The permission decision (before Stage A)

The one trust choice, made first because it changes how everything else runs.

- **Your turn:** decide whether Claude may run commands and edit files on this machine without asking permission for each step. The team setup is built for "yes" — that's what makes the day flow. Say yes, no, or ask questions first.
- **Why it's yours:** this one choice defines how much the AI may do unsupervised on your machine. It has to be made knowingly, by you, once — never defaulted by a script.
- **Claude then:** on yes, write the permission settings via `scripts/setup-permissions.py` (merge-safe). On no, continue anyway — everything still works, they'll just click approve a lot; note it and move on.
- **Verify:** the settings file contains the expected entries; state the outcome in one sentence.

### Stage A — Tools (Claude does all of it)

Install what's missing: package manager (Homebrew on macOS, apt or Homebrew-on-Linux inside Ubuntu), then `git`, `gh`, `node` (20+), `jq`, and the Vercel CLI. On Windows, everything installs inside Ubuntu, never via winget (winget is only for the Claude Desktop app itself).

**Verify:** each of `git --version`, `gh --version`, `node --version`, `jq --version`, `vercel --version` succeeds and meets the floor in `references/os-detection.md`.

### Stage B — Accounts and sign-ins (Gates 1–3)

**Gate 1 — the three accounts.**
- **Your turn:** create accounts you don't already have, at github.com, vercel.com (choose "sign up with GitHub"), and supabase.com (same). Claude gives one link at a time and waits.
- **Why it's yours:** terms of service, robot checks, and email verification require a human, and the accounts must belong to you.
- **Verify:** you can log into each site. (The CLI-level checks come with the next two gates.)

**Gate 2 — GitHub sign-in.**
- **Your turn:** Claude runs `gh auth login` and hands you the one-time code and browser page; you sign in and approve.
- **Why it's yours:** the password and the approval are yours; the approval decides what the tool may do to your repos. Claude never sees the password — GitHub hands the tool a scoped token.
- **Verify:** `gh auth status` shows the right account. Also set `git config --global user.email` to the operator email — effort tracking attributes work by it.

**Gate 3 — Vercel sign-in.**
- **Your turn:** Claude runs `vercel login`; you click the confirmation email or browser prompt.
- **Why it's yours:** same as Gate 2 — it's your account's consent screen.
- **Verify:** `vercel whoami` returns the account.

If a 2FA code is asked anywhere: that's yours too (it goes to your phone), then Claude retries the blocked check.

### Stage C — The team (machine layer, once per machine)

Claude does all of it. Skipped entirely when Check 3 verified a working team.

```bash
gh repo clone --depth 1 -b stable talentedgeai/infiniteleverage-8-agents-template /tmp/il-template
cp /tmp/il-template/.claude/agents/*.md ~/.claude/agents/
# global skills, rules, hooks — via the patch skill's installer so wiring is identical to updates:
cp -r /tmp/il-template/setup-skills/infiniteleverage-patch ~/.claude/skills/
bash ~/.claude/skills/infiniteleverage-patch/scripts/install-hooks.sh /tmp/il-template
rm -rf /tmp/il-template
```

**Verify:** `ls ~/.claude/agents/` shows all 8; the hook wiring check (each event maps to its expected script) passes; `~/.claude/rules/global-engineering.md` exists.

### Stage D — Project wiring (project and cloud layers)

**D1 — The folder.** If the product-plan interview already created `~/code-projects/<slug>/` with a catalog CLAUDE.md, use it — that folder is the project. If not (standalone use of this skill), ask for the business name, make the slug, create the folder, and proceed; the catalog can be added later by the interview.

**D2 — The scaffold.** Merge `templates/project-scaffold/` into the project folder per the Settings Safety Protocol (the interview's CLAUDE.md and Working Files are preserved; `website/` and the scaffold structure are added). Rename `PH-` placeholders per `FOLDER-STRUCTURE.md`.

**D3 — Git and GitHub.** `git init`, first commit, `gh repo create` under the operator's account, push. **Verify:** the repo page exists and shows the push.

**Gate 4 — Supabase connection.**
- **Your turn (two clicks):** first, in Claude Code run `/plugin`, choose the marketplace, install **supabase**, restart if prompted. Second, Claude starts the authentication and gives you a link; click **Authorize**.
- **Why it's yours:** installing a plugin and clicking a consent screen are standing grants of access to your database. The click is the contract. After this one click, Claude runs all SQL itself — you will never paste SQL into a dashboard.
- **Verify:** the Supabase tools respond (list the project, confirm the URL). Then Claude creates the Supabase project if none exists for this slug, or connects to the existing one.

**D4 — Keys.** Claude collects the Supabase URL and keys into `website/.env.local` via `scripts/collect-credentials.py` (merge-safe), driving the browser itself where it can with you logged in, asking only when blocked by a login, 2FA, or robot check — and then naming the exact value and where to find it. The same values go into Vercel's environment via `vercel env`. **`.env.local` and Vercel env are the only two places any key ever lives.** Gemini and Resend are deliberately not collected now; they arrive with their features.

**Gate 5 — Vercel import.**
- **Your turn (one click):** open vercel.com/new, import the repo just created, set **Root Directory = `website`**, deploy.
- **Why it's yours:** it sits behind your Vercel login and confirms a deployment running under your account.
- **Verify:** `vercel ls` shows the project; then Claude runs `vercel link`.

### Stage E — Deploy

Claude pushes; the pipeline builds. **Verify:** `curl -I https://<slug>.vercel.app` returns HTTP 200. Tell the user their site is live and show them the URL — this is the win. (Deploys happen only ever via `git push`; never `vercel deploy`.)

### Stage F — The graduation lap, then finalize

Before declaring the stack done, prove the autonomy contract end to end, alone:

1. **Data lap:** through the Supabase connection, create a scratch table, confirm it exists, remove it. No dashboard, no pasted SQL.
2. **Ship lap:** create a branch, make a trivial change (a line in the README), open a PR, merge it, watch the Vercel build go green with the CLI, confirm the live site updated.

If either lap fails, name the missing grant right now and fix it — this is the moment to discover it, not Build 1.

Then finalize:

- **Fill the catalog.** If the project CLAUDE.md has a Stack section with `[pending]` lines, fill each with its real value — statuses and URLs, never a secret:
  The **Core stack** section, which is the only section that gates Build 1:
  - `IL skill installed` → done, with the version
  - `GitHub repo` → owner/name
  - `Vercel project` → the project name
  - `Site live at` → the public URL that returned HTTP 200
  - `Supabase project` → the project name
  - `Supabase URL` → the real URL (a URL is not a secret)
  - `Supabase keys` → write exactly: `stored in website/.env.local, never written here`. Never the value. This rule applies to any line naming a key, on any project, forever.

  The **Email and domain** section is not yours to fill. Leave every line reading `[deferred to Build 2]`. Those lines are deliberately not `[pending]`, so Build 1 is never blocked by things it does not use.
- **Stamp the version:** fetch the latest release tag of the canonical repo into `~/.claude/.infiniteleverage-version`.
- **Register the plugin:** `claude plugin marketplace add talentedgeai/infiniteleverage-plugin` — this wires the session advisory and hooks; it carries no skills.
- **Register the PM schedules** exactly as `references/phase2-prompts.md` specifies, and verify they appear.
- **Write HANDOFF.md** in the project so the next session (or the next person) starts with context.
- **File the setup report.** Write a short structured report of this run: skill version, OS and triage verdict, the history state found, per-stage timing, every gate's outcome, every verify that failed and how it recovered, and anything the operator did by hand that this guide didn't ask for (a hand-fix is a bug in this skill, record it as one). Then: if `gh repo view talentedgeai/infiniteleverage-8-agents-template` succeeds (the operator is a team engineer), file it with `gh issue create` on that repo, title "setup run <version> <os> <state>", label `setup-report`. Otherwise write it to `SETUP-REPORT.md` in the project folder. Never include keys, tokens, or personal data beyond the machine facts above.

State the end state in plain English: the live URL, the three grants Claude now holds, and that from here on, asking the user to paste SQL or click deploy would be a bug.

---

## Windows gates (own machine, WSL2 not yet present)

**Gate W1 — turn on WSL2.**
- **Your turn:** Start → type PowerShell → right-click → Run as administrator → run `wsl --install`.
- **Why it's yours:** Windows requires administrator elevation as a consent step from you; Claude can't and shouldn't elevate itself.
- **Verify:** the command reports installing, then asks for a restart.

**Gate W2 — restart.**
- **Your turn:** restart the PC when prompted. Before they do, tell them exactly how to resume: *"When it's back, open Claude Desktop, open the Code tab, and paste the same setup prompt again — I'll detect where we stopped and continue."*
- **Why it's yours:** Claude's session cannot survive or trigger a reboot.
- **Verify (after resume):** the triage Check 3 finds the half-finished state and continues; `wsl.exe --status` succeeds.

**Gate W3 — the Ubuntu login.**
- **Your turn:** the Ubuntu window asks for a username and password on first launch; choose them and write them down (the password won't show as you type — that's normal).
- **Why it's yours:** it's a password.
- **Verify:** commands run inside Ubuntu; continue the flow there. Projects live in the Linux home (`~/code-projects/`), never `/mnt/c/`.

Full walkthrough and troubleshooting: `references/windows-setup.md`. Where the day-to-day session lives on Windows after setup is stated in that reference — keep it accurate to the last hardware test.

---

## Cloud track (corporate machines, chat-only surfaces, below-floor hardware)

Follow `references/cloud-track-codespaces.md`. Same flow, same gates, same graduation lap — the machine layer just lives in the Codespace. Requirements: a paid Claude subscription, a GitHub account, a modern browser. Set the expectation that the cloud IDE takes minutes to start. The win is the same live site; there is no localhost step.

---

## Mode B — Additional machine (the team exists elsewhere)

No infrastructure creation, no schedule registration. The order:

1. Triage (Step 0) as normal — it will find the clean machine and the user's answer routes here.
2. Stage A tools, Gate 0, Gates 2–3 (sign in to the existing accounts).
3. Quick win first: clone the existing project, `npm install --prefix website`, `npm run dev --prefix website`, show the real site at localhost:3000.
4. Stage C (team install), Gate 4 (Supabase connection), credentials into `.env.local` via secure transfer from the original machine (AirDrop or equivalent — never email).
5. Graduation lap, version stamp, plugin registration. No schedules — they live on the original machine.

Details: `references/mode-b-phase1-manual.md` and `references/mode-b-phase2-prompts.md`.

---

## Resume paths

Any interruption resumes by evidence, not memory. Re-run triage Check 3; the first failing verify below is the resume point.

| First failing check | Resume at |
|---|---|
| Tools missing | Stage A |
| `gh auth status` / `vercel whoami` fail | Stage B |
| Fewer than 8 agents, or hook wiring wrong | Stage C |
| No project folder / no scaffold / no repo | Stage D |
| Supabase tools don't respond | Gate 4 |
| No `.env.local` core keys | D4 |
| `vercel ls` empty | Gate 5 |
| Site not HTTP 200 | Stage E |
| Laps not proven / catalog has `[pending]` / no version stamp | Stage F |

---

## Checklist (the definition of done)

- [ ] Triage ran: surface, machine verdict, history state named
- [ ] Gate 0 decision made knowingly and recorded
- [ ] Tools at floor versions
- [ ] Gates 1–3 verified: accounts exist, `gh auth status`, `vercel whoami`
- [ ] 8 agents present, hooks wired (event → expected script), rules written
- [ ] Project folder is the interview's folder (or created); scaffold merged, interview CLAUDE.md preserved
- [ ] Repo pushed; Vercel imported (Root Directory = website); `vercel link` done
- [ ] Supabase connected (Gate 4); keys in `website/.env.local` and Vercel env only
- [ ] Site live: HTTP 200
- [ ] Graduation lap passed: scratch migration with no dashboard; PR opened, merged, build watched green, live site updated
- [ ] Catalog filled: no `[pending]` left in Core stack; every key line says "stored in website/.env.local, never written here"; Email and domain lines still read "[deferred to Build 2]"
- [ ] Version stamped; plugin registered; schedules registered (Mode A only); HANDOFF.md written

---

## For maintainers

- This file and `PROMPT.md` beside it are a contract: CI asserts the prompt's URL points at `stable`, every gate has its three parts, every referenced file exists, and the catalog keys Stage F fills match the interview prompt's `[pending]` list. Don't merge red.
- The regression checklist for this skill lives at `SKILL-REGRESSION-CHECK.md` (same directory). A rewrite must preserve every invariant on it.
- References that must stay consistent with this file: `os-detection.md` (floors and verdicts), `windows-setup.md` (gates W1–W3 and the post-setup session location), `cloud-track-codespaces.md` (must be org-owned and non-experimental before this skill routes corporate users to it), `phase2-prompts.md` (building blocks; this file's stage order wins on conflict).

## Open decisions (resolve before release, then delete this section)

1. **Scheduling wording:** Protocol 10 says CronCreate; the schedule step registers cloud routines. Confirm what production machines actually run and make P10, this file, and `phase2-prompts.md` agree.
2. **Cloud track hardening:** the Codespace template must move to an org-owned, version-pinned repo, and telemetry inside a Codespace must be verified, before the corporate fork ships.
3. **Windows session location:** confirm on hardware whether the Desktop Code tab can host its session inside WSL, and write the answer into `windows-setup.md`.
