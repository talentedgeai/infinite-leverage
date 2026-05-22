---
name: infiniteleverage-init
description: Full Mac Mini bootstrap: zero to live website, 8-agent team, and 10 local CronCreate schedules. Two phases: manual prerequisites (Claude Chat) then automated setup (Claude Code).
---

# Infinite Leverage — Mac Mini Bootstrap

## Welcome

You're about to set up a fully autonomous AI marketing and development team. By the end of this, the Mac Mini will have a live website, 8 specialist agents, and a content pipeline that runs itself Monday–Wednesday every week. Let's go! 🚀

This setup is built on the **Infinite Leverage 18 Protocols** — the principles that make an AI team actually work in practice. You'll see them called out **[Protocol N]** at the exact moment each one becomes relevant so you understand *why* you're doing what you're doing, not just *what* to do.

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

> **"I'm running the Infinite Leverage Mac Mini bootstrap. Please scan my current environment and tell me exactly where I am: check brew --version, git --version, gh --version, node --version, vercel --version, claude --version, ls ~/.claude/agents/, ls ~/code-projects/. Then give me a friendly summary: what's already done, what's next, and which Phase 2 prompt to start from if I'm mid-way through."**

Claude will give you a personalised status report — no redoing steps you've already done, no guessing what's missing.

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
| Bootstrap skills (init/onboard/patch/project) | `setup-skills/` |

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

**During Phase 2 — Prompt 4 (project scaffold)**, the developer agent MUST:

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
- `CLAUDE.md`, `README.md`, `.env.example`, `.gitignore`

The PM agent and developer agent both reference this structure on every action — read `FOLDER-STRUCTURE.md` before creating any new file.

---

## Phase Structure

```
PHASE 1 — Claude Chat (manual)
  Accounts & prerequisites — human does all of this
  ├── [P3] Google Workspace: add domain, verify DNS, create operator email
  ├── [P5][P6][P7] Service accounts: GitHub, Claude Pro, Vercel, Supabase
  ├── [P10] API keys: Gemini, Resend + DNS, Supabase (+ Lark if using — optional)
  ├── Credentials file: saved locally, never committed
  ├── Claude Code Desktop: installed, signed in
  └── Mac Mini tools: Homebrew + git only (rest installed by Claude Code in Phase 2)
      │
      └─ Homebrew and git confirmed working ──►

PHASE 2 — Claude Code (automated)
  Setup + Agents — Claude Code does all of this
  ├── Tool install: gh, node, jq, ffmpeg, vercel CLI, supabase CLI, resend CLI, Claude Code CLI + auth
  ├── [P3] Global permissions + engineering rules
  ├── [P7] Supabase MCP: install + authenticate (one browser click only)
  ├── [P4][P8][P9] Project scaffold: context folders + Next.js 16 in website/ subdir
  ├── Credentials: .env.local written from credentials file
  ├── [P5][P6] Deploy: git push → GitHub → Vercel CI/CD
  ├── [P13][P1] Agents: fetch all 8 from `.claude/agents/` in GitHub canonical repo
  ├── [P16] QA agent with test pyramid + anti-patterns
  ├── [P12] DevOps agent with escalation rules
  ├── [P15] PM agent that reads git log + standup files
  ├── Agent team dashboard: HTML summary of all 8 agents, weekly calendar, cross-agent flow
  ├── [P10][P11] 10 RemoteTrigger cloud routines registered (persistent, no session needed)
  └── [P17] HANDOFF.md written for client
```

---

## Running Phase 1 — Claude Chat

Open claude.ai. Narrate each step — the operator acts. Do not proceed to Phase 2 until the full Phase 1 checklist is complete.

**Decision points:**
- Client already has GitHub? Use existing, confirm operator email is owner.
- Resend DNS takes > 5 min? Continue with other steps, return to verify before ending Phase 1.
- Existing SPF record on domain? Add `include:amazonses.com` — do not replace.

**Phase 1 is complete when:**
- Credentials file exists locally with all keys filled in
- Claude Code Desktop is open and signed in
- `git --version` works in Terminal

See `references/phase1-manual.md` for complete step-by-step.

---

## Running Phase 2 — Claude Code

Open Claude Code Desktop on the Mac Mini. Run prompts from `references/phase2-prompts.md` in sequence. Each prompt is self-contained — Claude Code executes it fully before the next one starts.

**Decision points:**
- Supabase OAuth: the only manual step in Phase 2. Claude outputs a URL → open in browser → Authorize → tell Claude "done". **[P7]**
- Vercel import: one browser action (import repo at vercel.com/new, set Root Directory = website/). Claude handles everything else. **[P6]**
- No approved plan when Developer runs: stop, notify via Lark (if configured) or log to HANDOFF.md, do not proceed. **[P1]**

**Phase 2 is complete when:**
- `curl -I https://{project-slug}.vercel.app` returns HTTP 200
- `ls ~/.claude/agents/` shows all 8 agents **[P13]**
- All 10 RemoteTrigger routines confirmed at https://claude.ai/code/routines **[P10]**
- HANDOFF.md written **[P17]**

See `references/phase2-prompts.md` for the full prompt sequence.

---

## Resume Paths

Stopped partway through? Here's where to pick up — no restarting needed.

| Stopped at | Check | Resume from |
|-----------|-------|-------------|
| Phase 1, steps 1–3 | `git --version` fails | Phase 1, Step 8 |
| Phase 1, steps 4–6 | `brew --version` works, no credentials file | Phase 1, Step 5 |
| Phase 1 complete, Phase 2 not started | `claude --version` fails | Phase 2, Prompt 1 |
| Phase 2 Prompt 1–2 | `ls ~/.claude/rules/` empty | Phase 2, Prompt 1 |
| Phase 2 Prompt 3–4 | Supabase MCP not in settings | Phase 2, Prompt 3 |
| Phase 2 Prompt 5–6 | `ls ~/code-projects/{project-slug}` empty | Phase 2, Prompt 4 |
| Phase 2 Prompt 7 | No GitHub repo yet | Phase 2, Prompt 7 |
| Phase 2 Prompt 8+ | `ls ~/.claude/agents/` shows 0 agents | Phase 2, Prompt 8 |
| Phase 2 nearly done | Agents present, no schedules | Phase 2, Prompt 9 |

---

## Checklist

### Phase 1 — Manual
- [ ] Operator email active: `{firstname}@{clientdomain}.com`
- [ ] GitHub `{clientslug}` created and verified
- [ ] Claude Pro account active
- [ ] Vercel linked to GitHub
- [ ] Supabase project created, database password saved
- [ ] Gemini API key generated
- [ ] Resend API key + domain DNS verified (green in Resend dashboard)
- [ ] Lark bot credentials collected *(optional — skip if not using Lark)*
- [ ] Credentials file complete locally (never committed)
- [ ] Claude Code Desktop installed and signed in
- [ ] Homebrew installed and in PATH
- [ ] git installed (`git --version` works)

### Phase 2 — Claude Code
- [ ] gh, node, jq, ffmpeg, vercel CLI, supabase CLI, resend CLI, Claude Code CLI installed and authenticated
- [ ] `~/.claude/settings.local.json` with `Bash(*)` + `acceptEdits`
- [ ] `~/.claude/rules/global-engineering.md` written
- [ ] Supabase MCP configured **[P7]**
- [ ] Project scaffolded at `~/code-projects/{project-slug}/` with context folders + `website/` **[P4]**
- [ ] `.specify/` initialized in project root (done by `infiniteleverage-project` Step 8.5 — verify with `ls .specify/`)
- [ ] `.env.local` written with all credentials (inside `website/`)
- [ ] Global skills: `daily-checkin`, `create-local-routine`, `create-remote-routine`, `create-agent`, `infiniteleverage-help` **[P11]**
- [ ] GitHub repo created, pushed, Vercel project imported (Root Directory=website set in dashboard) **[P5][P6]**
- [ ] `vercel link` run, env vars added via `vercel env`, deployment verified (`vercel ls`)
- [ ] Site live on Vercel (HTTP 200)
- [ ] All 8 agents fetched from GitHub canonical repo to `~/.claude/agents/` **[P13]**
- [ ] Hooks installed: `~/.claude/hooks/pre-bash` + `prompt-submit` copied and wired into `settings.local.json`
- [ ] `email-index.md` Stage 0 populated
- [ ] 10 RemoteTrigger routines registered — verify at https://claude.ai/code/routines **[P10]**
- [ ] HANDOFF.md written **[P17]**

**Next**: Hand off HANDOFF.md to client → run `infiniteleverage-onboard` skill on client's machine.

---

## Phase 3 — Stamp installed version and register plugin

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

## Additional Resources

- **`references/phase1-manual.md`** — Complete step-by-step for all account creation, DNS setup, API keys, and Mac Mini tool installation
- **`references/phase2-prompts.md`** — Full Claude Code prompt sequence for project scaffold, agent team build, and schedule registration
- **`scripts/setup-permissions.py`** — Python script to write `~/.claude/settings.local.json` without overwriting existing content
