---
name: infiniteleverage-init
description: Stand up an Infinite Leverage machine — first-ever setup (zero to live website, 8-agent team, schedules) or an additional machine connecting to an existing team. Handles macOS and Windows (WSL2), with a cloud track for old hardware.
---

# Infinite Leverage — Machine Setup

## Welcome

You're about to set up a fully autonomous AI marketing and development team. By the end of this you'll have a live website, 8 specialist agents, and a content pipeline that runs itself Monday–Wednesday every week. Let's go! 🚀

This setup is built on the **Infinite Leverage 18 Protocols** — the principles that make an AI team actually work in practice. You'll see them called out **[Protocol N]** at the exact moment each one becomes relevant so you understand *why* you're doing what you're doing, not just *what* to do.

---

## Step 0 — Which setup is this?

Ask the user one question before anything else:

> **"Is this your very first Infinite Leverage setup, or have you done this before and are now setting up another machine?"**

The answer decides the whole flow — because the real difference isn't the hardware, it's **whether the shared infrastructure (accounts, GitHub repo, live site) already exists.**

| Answer | Mode | What it means |
|---|---|---|
| "First time — nothing exists yet" | **Mode A — First Setup** | Create accounts + infrastructure, deploy a live site, build all 8 agents + schedules. Full bootstrap. |
| "Done it before — new machine" | **Mode B — Additional Machine** | Infra already exists. Connect this machine: clone the live project (see it run locally), pull the 8 agents, sync config. No account/infra creation, no schedule re-registration. |

- **Mode A** → follow Phase 1 → Phase 2a → Phase 2b below.
- **Mode B** → skip to the **Mode B — Additional Machine** section near the end; it reuses the same building blocks without recreating infrastructure.

> Mode B replaces the old separate `infiniteleverage-onboard` skill. If something points you there, use Mode B here instead.

---

## Check your machine first (both modes)

Before any install, confirm the machine is supported. Read **`references/os-detection.md`** and run its Step 1 detection snippet. It covers **macOS and Windows (WSL2)** in one place and gives a plain-English verdict:

- ✅ **Supported** → continue with local setup (Track A, below).
- ⚠️ **Borderline** → upgrade the one named tool, then continue.
- ☁️ **Use the cloud track** → the machine is below the version floor or can't run WSL2. Switch to **`references/cloud-track-codespaces.md`** (Track B) instead of fighting the hardware.

**On Windows:** you must work inside the **Ubuntu (WSL2)** shell — native Windows/PowerShell silently breaks the bash hooks. `references/os-detection.md` links to `references/windows-setup.md` for the one-time WSL2 turn-on.

> Running a retreat? See **`references/pre-retreat-readiness.md`** — catch sub-floor machines at registration and route them to a loaner or the cloud track *before* the day.

---

## Settings Safety Protocol

Before writing any configuration file — `settings.local.json`, `CLAUDE.md`, `global-engineering.md`, `.env` — check what's already there and follow these three rules:

| Scenario | Action |
|---|---|
| File exists with compatible content (e.g. `settings.local.json` with different permissions, `CLAUDE.md` with custom sections already present) | **Merge** — add what's missing without removing what's already there |
| File exists and is a complete previous version of this template | **Upgrade** — replace the whole file with the latest version |
| File exists with content that conflicts with the template's intended pattern | **Try to resolve** — preserve the user's value and intent while satisfying the template requirement. If you can't resolve cleanly without losing something, ask the user before touching the file |

**When asking about a conflict, use plain language — no JSON keys, no file paths, no technical jargon:**
- Say what the setting *does*, not what it's called
- Offer a simple choice: keep theirs, use the template's, or combine both

> **Example:** "Your Claude Code is already set to ask permission before running shell commands. The team setup works best with shell commands allowed automatically. Would you like to switch to automatic, keep the ask-first behaviour, or handle them separately?"

> **Example:** "You already have a global Claude instruction file with some notes in it. We'd like to add the 8-agent team routing table. Should we add it at the end, or would you like to look at the additions first?"

---

## Smart Start — Find Out Where You Are

Not sure if you've already done some of this? Don't guess. Run this first in Claude Code (or Claude chat):

> **"I'm setting up Infinite Leverage. First run the OS detection from `references/os-detection.md` and give me the supported/borderline/cloud verdict. Then scan my environment: brew/apt, git --version, gh --version, node --version, vercel --version, claude --version, ls ~/.claude/agents/, ls ~/code-projects/. Then a friendly summary: am I doing a first-time setup or an additional machine, what's already done, what's next, and which prompt to resume from."**

Claude will give you a personalised status report — the machine verdict first, then no redoing steps you've already done, no guessing what's missing. (This is also exactly what a prework attendee pastes back — see `references/pre-retreat-readiness.md`.)

**First time here?** Start at Phase 1 below — everything is waiting for you.
**Returning mid-way?** Run the smart start above — it'll tell you exactly where to jump back in.

---

## What You're Building

| Track | The Principles |
|-------|---------------|
| 🧠 Mindset | Humans orchestrate; agents act when asked **[P1]** · AI is the new CMS **[P2]** · Stack = Claude + GitHub + Vercel + Supabase **[P3]** · Agents are folders, not magic **[P4]** |
| 🏗 Infrastructure | GitHub for all code and context **[P5]** · Vercel deploys only via `git push` — never `vercel deploy` directly **[P6]** · Supabase for data and subscribers **[P7]** |
| 🔨 Building | Design system written before any component **[P8]** · Concrete step-by-step workflows **[P9]** · PM schedules auto-run via CronCreate (local, durable) **[P10]** · Skills for admin so humans never escalate for small things **[P11]** |
| 👥 Team & Ops | DevOps escalates to a human engineer when needed **[P12]** · 8 fixed agent roles — no improvising **[P13]** · PM plans epics with acceptance criteria **[P14]** · PM reads git history before every task **[P15]** |
| ♻️ Continuity | QA knows exactly what AI can and cannot test **[P16]** · Context handed off via BRIDGE.md and memory system **[P17]** · Work outlives the operator — universal agent templates on GitHub **[P18]** |

---

## Canonical Source — Read This First

**ALL of the following live in ONE repo — the single source of truth:**

> https://github.com/talentedgeai/infiniteleverage-8-agents-template

| What | Where in the canonical repo |
|---|---|
| 8 agent definitions | `.claude/agents/*.md` |
| Global skills | `.claude/skills/*/SKILL.md` |
| Engineering rules | `.claude/rules/global-engineering.md` |
| Project folder scaffold | `templates/project-scaffold/` |
| Folder structure spec | `templates/project-scaffold/FOLDER-STRUCTURE.md` |
| AGENT-DELEGATION block content | `scripts/inject-agent-delegation.sh` |
| Bootstrap skills (init/patch/project) | `setup-skills/` |

**Rules — these are non-negotiable:**

1. **Never hand-edit agents, skills, or scaffold files on the client machine.** Any change must be made in the canonical repo first, committed, and pulled by the patch skill.
2. **Never invent new agent behavior in CLAUDE.md.** The AGENT-DELEGATION block is generated from `scripts/inject-agent-delegation.sh` — edit that script in the repo, not the CLAUDE.md on disk.
3. **When in doubt, fetch fresh** with `gh repo clone --depth 1 talentedgeai/infiniteleverage-8-agents-template /tmp/il-template`.
4. The bundled copy inside this skill's zip is a **fallback** for offline use only. If GitHub is reachable, always prefer the live repo.

```bash
# Fetch canonical agents and hooks at any time:
gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-agents
cp /tmp/il-agents/.claude/agents/*.md ~/.claude/agents/
bash ~/.claude/skills/infiniteleverage-patch/scripts/install-hooks.sh /tmp/il-agents
rm -rf /tmp/il-agents
```

---

## Project Scaffold

Every project follows the canonical folder structure defined in `templates/project-scaffold/` of this repo. The authoritative spec is `templates/project-scaffold/FOLDER-STRUCTURE.md`.

**During Phase 2a — Prompt 4 (project scaffold)**, Claude (Session A — it provisions a local `developer.md` inline first, per the zero-state rule) MUST:

```bash
# Fetch the canonical scaffold into the new project
gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-template
cp -r /tmp/il-template/templates/project-scaffold/. ~/code-projects/{project-slug}/
rm -rf /tmp/il-template

# Then rename placeholders:
#   - All `PH-` prefixed files → real names from the project intake
#   - YYYY-MM-DD → real first publish date
#   - {Project Name} / {project-slug} → real values
```

**Fixed files that must NOT be renamed:**
- `docs/product/product.md`, `epics.md`, `epic-status.md`, `01-product-timeline.md`
- `docs/project-status.html`
- `CLAUDE.md`, `README.md`, `.gitignore`

The PM agent and developer agent both reference this structure on every action — read `FOLDER-STRUCTURE.md` before creating any new file.

---

## Phase Structure (Mode A — First Setup)

The order is deliberate: **reach a live site fast (the win), and build the agent team in parallel.** Phase 1 is minimal — Claude **Desktop** + core accounts, no keys. Phase 2 then runs as **two concurrent Claude Code sessions**: **2a** is the interactive track the user watches; **2b** is an autonomous track that runs unattended. **All credential collection happens in Phase 2** and Claude collects keys itself where it can (Claude-in-Chrome / computer-use), asking the user only when blocked.

```
PHASE 1 — Claude Chat / Desktop (manual, minimal — NO keys)
  Get Desktop ready + core accounts — human does this
  ├── Check the machine: references/os-detection.md (supported / borderline / cloud)
  ├── Install Git + package manager (Homebrew on macOS / apt in WSL2)
  ├── Install Claude Code Desktop (signed in with Claude Pro) ← Phase 2 prompts run HERE
  ├── [P5][P6][P7] Core accounts only: GitHub, Vercel, Supabase (+ Git identity for effort tracking)
  ├── NO API keys here — all env collection happens in Phase 2 (automated where possible)
  └── (Claude CLI is NOT needed yet — optional install at the very end of this skill)
      │
      └─ Desktop signed in + GitHub/Vercel/Supabase exist ──►

PHASE 2 — Claude Code: run 2a and 2b as TWO PARALLEL SESSIONS
  On first opening Code, start 2b in one session (let it run), then run 2a in another.

  ┌─ PHASE 2a — INTERACTIVE (user watches + interacts) ──────────────────┐
  │  Shortest path to a live site — the win                             │
  │  ├── Tool install: gh, node, jq, ffmpeg, vercel CLI + auth          │
  │  ├── [P3] Global permissions + engineering rules                    │
  │  ├── [P7] Supabase plugin (MCP): /plugin install + OAuth (manual)   │
  │  ├── [P4][P8][P9] Project scaffold: Next.js 16 in website/          │
  │  ├── ENV (core/Supabase): Claude auto-fetches via Chrome MCP /      │
  │  │     computer-use → collect-credentials.py; asks only if blocked  │
  │  ├── [P5][P6] Deploy: git push → GitHub → Vercel CI/CD              │
  │  └── 🎉 Site live (HTTP 200) — the dopamine hit                     │
  └──────────────────────────────────────────────────────────────────┘

  ┌─ PHASE 2b — AUTONOMOUS (unattended, no live-site dependency) ────────┐
  │  The team — runs on its own while the user drives 2a                │
  │  ├── [P13][P1] Fetch + install all 8 agents from canonical repo     │
  │  ├── [P16] QA · [P12] DevOps · [P15] PM definitions                 │
  │  ├── Global skills [P11] + hooks (pre-bash, prompt-submit)          │
  │  └── [P10] Register the 10 RemoteTrigger routines                   │
  │     (NO dashboard here — it needs the live site; built at 2a finalize)│
  └──────────────────────────────────────────────────────────────────┘
      │
      └─ 2a FINALIZE / JOIN (after HTTP 200, in the 2a session):
         ├── Verify 2b finished: 8 agents present + 10 schedules registered
         │     → if incomplete, report what's missing and finish it
         ├── Agent team dashboard (needs live site + agents) — built NOW
         └── [P17] HANDOFF.md written for client
```

> **Mode B (Additional Machine)** has its own shorter flow — see the dedicated section below. It does not recreate any of Phase 1's infrastructure.

---

## Running Phase 1 — Claude Chat / Desktop (Mode A)

Open claude.ai (or the Claude Desktop chat). Narrate each step — the operator acts. Phase 1 is intentionally minimal: get **Claude Desktop** ready and create only the three core accounts. **No API keys are collected here** — all env collection happens in Phase 2 (automated where possible). The Claude **CLI is not needed yet** — it's an optional install at the very end of this skill.

**Decision points:**
- Machine below the version floor? Don't fight it — switch to the cloud track (`references/cloud-track-codespaces.md`).
- Client already has GitHub? Use existing, confirm operator email is owner.
- Tempted to grab API keys now? Don't — Phase 2 collects them, mostly automatically.

**Phase 1 is complete when:**
- `references/os-detection.md` verdict is ✅ (or the user is on the cloud track)
- Claude Code **Desktop** is installed and signed in (this is where Phase 2 runs)
- `git --version` works; `gh auth login` done; `git config --global user.email` set
- GitHub, Vercel, Supabase accounts exist

See `references/phase1-manual.md` for complete step-by-step.

---

## Running Phase 2 — Claude Code: two parallel sessions (Mode A)

Phase 2 runs as **two concurrent Claude Code sessions**. When the user first opens Code, set this up before running anything:

> **Open a second Claude Code session/tab.** In **session 1**, paste the **2b** kickoff prompt — it's autonomous, needs no babysitting, and will install the agent team + schedules on its own. Then switch to **session 2** and run the **2a** prompts yourself — this is the interactive track where you'll click through a couple of browser steps and watch the site go live.

- **2a (interactive, you watch):** deps → permissions → Supabase plugin/OAuth → scaffold → env collection → deploy → HTTP 200. Self-contained prompts; a 2a prompt never invokes an `@agent` (those belong to 2b).
- **2b (autonomous, unattended):** fetch + install all 8 agents, global skills, hooks, register the 10 schedules. **No dashboard** (it needs the live site — built at the 2a finalize step).

**Env collection — automate first, ask only when blocked. [P8]** In Phase 2, Claude collects keys *itself* wherever it can — driving the browser via the **Claude in Chrome extension (MCP)** or **computer-use** to open the Supabase dashboard and copy the values, writing each through the merge-safe collector:
```bash
python3 scripts/collect-credentials.py --check core      # see what's still missing
python3 scripts/collect-credentials.py --set NEXT_PUBLIC_SUPABASE_URL=... SUPABASE_SECRET_KEY=...
```
Claude escalates to a **manual ask only when it genuinely can't proceed** — login walls it can't pass, 2FA, CAPTCHA/Arkose, billing/plan selection. When it asks, it names the exact value and where to find it.

**Decision points:**
- Supabase plugin + OAuth (2a): Claude can't install a plugin or complete OAuth itself. (1) `/plugin` → marketplace → install **supabase** → restart if prompted. (2) open the auth URL → Authorize → tell Claude "done". **[P7]**
- Vercel import (2a): one browser action (import repo at vercel.com/new, Root Directory = website/). **[P6]**
- No approved plan when Developer runs: stop and log to HANDOFF.md. **[P1]**

**Phase 2a is complete when:** `curl -I https://{project-slug}.vercel.app` returns HTTP 200 — 🎉 the win.

**2a finalize / join (run at the end of the 2a session, after HTTP 200):**
- Verify 2b finished: `ls ~/.claude/agents/` shows all 8 **[P13]** and all 10 routines are registered at https://claude.ai/code/routines **[P10]**. If 2b is incomplete, report what's missing and finish it here.
- Build the agent team dashboard (needs the live site + agent defs).
- Write HANDOFF.md **[P17]**.

See `references/phase2-prompts.md` for the full prompt sequence (2a, the 2b autonomous block, and the finalize step).

---

## Resume Paths

Stopped partway through? Here's where to pick up — no restarting needed.

| Stopped at | Check (OS-aware) | Resume from |
|-----------|-------|-------------|
| Phase 1, machine/tools | `git --version` fails, or no package manager | Phase 1, Step 2 |
| Phase 1, accounts | Desktop signed in but GitHub/Vercel/Supabase missing | Phase 1, Step 4 |
| Phase 1 complete, Phase 2 not started | Desktop signed in, `~/.claude/rules/` empty | Phase 2 — start 2b session + 2a session |
| 2a deps/config | `~/.claude/rules/` empty | 2a, Prompt 1 |
| 2a Supabase | plugin not installed / MCP not authenticated | 2a, Prompt 3 |
| 2a scaffold | `ls ~/code-projects/{project-slug}` empty | 2a, Prompt 4 |
| 2a env/deploy | no `.env.local` / no GitHub repo / not HTTP 200 | 2a, Prompt 5–7 |
| 2b (autonomous) | `ls ~/.claude/agents/` shows < 8 | 2b kickoff prompt |
| 2b schedules | agents present, no routines registered | 2b (schedule step) |
| Finalize | HTTP 200 + 8 agents, but no dashboard / HANDOFF.md | 2a finalize/join step |

---

## Checklist

### Phase 1 — Manual (minimal — core only)
- [ ] `references/os-detection.md` verdict ✅ (or on cloud track) — machine supported
- [ ] Package manager installed (Homebrew on macOS / apt in WSL2) and in PATH
- [ ] git installed (`git --version` works)
- [ ] Claude Code CLI installed and authenticated (`claude --version`) — installed EARLY
- [ ] Claude Code Desktop installed and signed in (Claude Pro)
- [ ] Run `gh auth login` and set `git config --global user.email` — required for effort tracking to attribute your work
- [ ] Operator email active: `{firstname}@{clientdomain}.com`
- [ ] GitHub `{clientslug}` created and verified
- [ ] Vercel linked to GitHub
- [ ] Supabase project created, database password saved

### Phase 2a — Claude Code (interactive)
- [ ] gh, node, jq, ffmpeg, vercel CLI installed and authenticated *(Claude CLI optional — see end of skill)*
- [ ] `~/.claude/settings.local.json` with `Bash(*)` + `acceptEdits`
- [ ] `~/.claude/rules/global-engineering.md` written
- [ ] Supabase plugin (`plugin:supabase`) installed via `/plugin` + MCP authenticated **[P7]**
- [ ] Project scaffolded at `~/code-projects/{project-slug}/` with context folders + `website/` **[P4]**
- [ ] `.specify/` initialized in project root (done by `infiniteleverage-project` Step 8.5 — verify with `ls .specify/`)
- [ ] `website/.env.local` written with **core** keys (Supabase) — collected automatically where possible; it is the ONLY env file (no `.env.example`)
- [ ] GitHub repo created, pushed, Vercel project imported (Root Directory=website set in dashboard) **[P5][P6]**
- [ ] `vercel link` run, core env vars added via `vercel env`, deployment verified (`vercel ls`)
- [ ] Site live on Vercel (HTTP 200) 🎉

### Phase 2b — Claude Code (autonomous, parallel session)
- [ ] All 8 agents fetched from GitHub canonical repo to `~/.claude/agents/` **[P13]**
- [ ] Hooks installed: `~/.claude/hooks/pre-bash` + `prompt-submit` copied and wired into `settings.local.json`
- [ ] Global skills: `daily-checkin`, `create-local-routine`, `create-remote-routine`, `create-agent`, `infiniteleverage-help` **[P11]**
- [ ] 10 RemoteTrigger routines registered — verify at https://claude.ai/code/routines **[P10]**

### 2a finalize / join (after HTTP 200)
- [ ] Verified 2b complete (8 agents + 10 routines) — finished anything missing
- [ ] `email-index.md` Stage 0 populated
- [ ] Agent team dashboard built (needs live site + agents)
- [ ] HANDOFF.md written **[P17]**

**Next**: Hand off HANDOFF.md to the client → on each additional machine (laptop, etc.), run this same `infiniteleverage-init` skill and answer **"another machine"** at Step 0 to follow **Mode B** below.

---

## Mode B — Additional Machine (connect to an existing team)

> Use this when the infrastructure already exists (accounts, GitHub repo, live site) and you're just wiring up another machine — a laptop, a second workstation. This **replaces the old `infiniteleverage-onboard` skill**. The hard part is already done; the reward here is seeing the *real, live site* running locally before touching any config.

**Prerequisite:** Mode A complete somewhere — the live site is on Vercel and the project repo exists on GitHub.

Same building blocks as Mode A, but **nothing creates infrastructure and no schedules are registered** (those live on the original machine). The order:

### Phase 1 (manual) — tools + the quick win
1. Check the machine: `references/os-detection.md` (same verdict logic; cloud track if below floor).
2. Install: package manager, git, gh, Node, Claude Code CLI + Desktop, Vercel CLI — authenticate each.
3. Transfer the credentials file from the original machine (AirDrop / secure share — never email).
4. **Quick win — see the live site locally:**
   ```bash
   mkdir -p ~/code-projects && cd ~/code-projects
   gh repo clone {clientslug}/{project-slug}        # [P5]
   cd {project-slug}
   npm install --prefix website
   npm run dev --prefix website                      # → http://localhost:3000
   ```
   That's the reward — the real deployed site, before any settings work.

Full step-by-step: **`references/mode-b-phase1-manual.md`**.

### Phase 2 (Claude Code) — config + agents (no infra creation)
- Global dirs + permissions (`scripts/setup-permissions.py`), `~/.claude/CLAUDE.md`, `global-engineering.md`.
- Credentials into `~/.claude/.env` with `scripts/collect-credentials.py` (merge-safe).
- Supabase plugin (MCP) install + auth — same two manual steps as Mode A.
- Fetch all 8 agents from the canonical repo → `~/.claude/agents/`; install hooks; test agents respond.
- **Effort-tracking registration** for the cloned repo (register or write the skip marker), then the 5-check validation.

Full prompt sequence + the effort-tracking registration block: **`references/mode-b-phase2-prompts.md`**.

**Mode B is complete when:** all 8 agents respond · hooks installed + wired · `localhost:3000` showed the live site · PM briefed on business context · effort-tracking registered or skipped.

**Then:** point the user to **`references/first-actions.md`** (8 agents, daily workflow, content pipeline, how to update agents). Run Phase 3 below on this machine too (stamp version + register plugin).

---

## Phase 3 — Stamp installed version and register plugin

*(Applies to both modes — run after Mode A or Mode B completes on this machine.)*

After confirming setup is complete, run:

```bash
version="$(curl --silent --max-time 5 \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/talentedgeai/infiniteleverage-8-agents-template/releases/latest" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name','').lstrip('v'))" 2>/dev/null || echo "")"
if [[ -n "$version" ]]; then
  echo "$version" > ~/.claude/.infiniteleverage-version
  echo "Version stamped: $version"
else
  echo "⚠️ Could not fetch version from GitHub Releases — check network or run again"
fi
```

This stamps the installed release version so the plugin's SessionStart hook can detect and auto-apply future updates.

Then register the plugin so Claude Code can discover and load it:

```bash
claude plugin marketplace add talentedgeai/infiniteleverage-plugin
```

This adds `talentedgeai/infiniteleverage-plugin` to `~/.claude/settings.json` as a known marketplace and enables it. After this, every new Claude Code session will automatically receive:
- Agent routing hints via the `UserPromptSubmit` hook
- Version update advisories via the `SessionStart` hook
- Token usage awareness at session start

If `claude plugin` is not yet available, the user is on an older Claude Code version — run `npm i -g @anthropic-ai/claude-code@latest` to upgrade first.

### Partner check — install whitelabel skill if eligible

Run silently after plugin registration. No output on failure — this is invisible to non-partners.

```bash
if gh repo view talentedgeai/infiniteleverage-partner-portal --json name > /dev/null 2>&1; then
  echo "✓ Partner access confirmed — installing whitelabel skill"
  mkdir -p ~/.claude/skills/infiniteleverage-whitelabel
  gh api repos/talentedgeai/infiniteleverage-partner-portal/contents/setup-skills/infiniteleverage-whitelabel/SKILL.md \
    --jq '.content' | base64 --decode \
    > ~/.claude/skills/infiniteleverage-whitelabel/SKILL.md
  echo "  Whitelabel skill installed → /infiniteleverage-whitelabel"
fi
```

Partners will see `/infiniteleverage-whitelabel` available in every future session. Non-partners: silent skip.

---

## Optional — Install the Claude CLI (power users)

Everything above runs inside **Claude Code Desktop**, so the standalone `claude` terminal CLI is **not required** for setup. Offer it only at the end, as a recommendation for users who want to drive Claude Code from the terminal, scripts, or headless/automation contexts:

```bash
# macOS / Linux / WSL2 Ubuntu:
curl -fsSL https://claude.ai/install.sh | bash
# (or, once Node is installed: npm install -g @anthropic-ai/claude-code)
claude --version    # verify
claude              # first run opens browser OAuth — sign in with the same Claude Pro account
```

Skip without consequence if the user only works in Desktop. If they install it, the global hooks, agents, and skills already configured apply to CLI sessions too — no extra setup.

---

## Additional Resources

**Read-first / both modes**
- **`references/os-detection.md`** — OS + shell detection, package-manager mapping, version floors, supported/borderline/cloud verdict (macOS + Windows WSL2 in one place)
- **`references/windows-setup.md`** — One-time WSL2 turn-on walkthrough (linked from os-detection)
- **`references/cloud-track-codespaces.md`** — Track B: cloud setup via GitHub Codespaces for old/unsupported machines (experimental)
- **`references/pre-retreat-readiness.md`** — Catch sub-floor machines at registration; prework + loaners + GitHub-signup troubleshooting

**Mode A — First Setup**
- **`references/phase1-manual.md`** — Minimal Phase 1: machine check, Claude Code early, core accounts (GitHub/Vercel/Supabase).
- **`references/phase2-prompts.md`** — Phase 2a (deps + first deploy = the win) then 2b (agents + schedules). Self-contained prompts for a zero-state machine.

**Mode B — Additional Machine**
- **`references/mode-b-phase1-manual.md`** — Tools + the quick-win clone (`localhost:3000` shows the live site)
- **`references/mode-b-phase2-prompts.md`** — Config + agent install + effort-tracking registration (no infra creation)
- **`references/first-actions.md`** — Client-facing guide: 8 agents, daily workflow, content pipeline, updating agents

**Shared**
- **`references/env-template.md`** — `.env.local` contract + just-in-time collection order (no `.env.example` — ever)
- **`scripts/collect-credentials.py`** — Merge-safe, just-in-time credential writer (`--check <group>` / `--set KEY=VAL`); groups: core, supabase-admin
- **`scripts/setup-permissions.py`** — Writes `~/.claude/settings.local.json` without overwriting existing content
