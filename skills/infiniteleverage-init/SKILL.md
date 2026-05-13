---
name: infiniteleverage-init
description: This skill should be used when the operator says "run init", "initialize the system", "set up the mac mini", "bootstrap track A", "run the init skill", or "start client onboarding". Guides the full first-time setup — from zero to a live website, 8-agent team (canonical templates at `talentedgeai/infiniteleverage-8-agents-template`), and cloud schedules — across two phases: manual prerequisites in Claude Chat, then full automation in Claude Code.
version: 0.2.0
---

# Infinite Leverage — Mac Mini Bootstrap

## Welcome

You're about to set up a fully autonomous AI marketing and development team. By the end of this, the Mac Mini will have a live website, 8 specialist agents, and a content pipeline that runs itself Monday–Wednesday every week. Let's go! 🚀

This setup is built on the **Infinite Leverage 18 Protocols** — the principles that make an AI team actually work in practice. You'll see them called out **[Protocol N]** at the exact moment each one becomes relevant so you understand *why* you're doing what you're doing, not just *what* to do.

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
| 🔨 Building | Design system written before any component **[P8]** · Concrete step-by-step workflows **[P9]** · PM schedules auto-run via RemoteTrigger **[P10]** · Skills for admin so humans never escalate for small things **[P11]** |
| 👥 Team & Ops | DevOps escalates to a human engineer when needed **[P12]** · 8 fixed agent roles — no improvising **[P13]** · PM plans epics with acceptance criteria **[P14]** · PM reads git history before every task **[P15]** |
| ♻️ Continuity | QA knows exactly what AI can and cannot test **[P16]** · Context handed off via BRIDGE.md and memory system **[P17]** · Work outlives the operator — universal agent templates on GitHub **[P18]** |

---

## Canonical Source

All 8 agent definition templates live at:
**https://github.com/talentedgeai/infiniteleverage-8-agents-template**

This repo is the single source of truth. Agent templates are fetched from here during setup and patching. A bundled copy exists in this skill's `agents/` as fallback.

```bash
# Fetch canonical agents at any time:
gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-agents
cp /tmp/il-agents/agents/*.md ~/.claude/agents/
rm -rf /tmp/il-agents
```

---

## Phase Structure

```
PHASE 1 — Claude Chat (manual)
  Accounts & prerequisites — human does all of this
  ├── [P3] Google Workspace: add domain, verify DNS, create operator email
  ├── [P5][P6][P7] Service accounts: GitHub, Claude Pro, Vercel, Supabase
  ├── [P10] API keys: Gemini, Resend + DNS, Lark, Supabase
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
  ├── [P13][P1] Agents: fetch all 8 from GitHub canonical repo (fallback: bundled `agents/`)
  ├── [P16] QA agent with test pyramid + anti-patterns
  ├── [P12] DevOps agent with escalation rules
  ├── [P15] PM agent that reads git log + standup files
  ├── Agent team dashboard: HTML summary of all 8 agents, weekly calendar, cross-agent flow
  ├── [P10][P11] 8 RemoteTrigger cloud schedules registered
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
- No approved plan when Developer runs: stop, notify via Lark, do not proceed. **[P1]**

**Phase 2 is complete when:**
- `curl -I https://{project-slug}.vercel.app` returns HTTP 200
- `ls ~/.claude/agents/` shows all 8 agents **[P13]**
- All 8 RemoteTrigger schedules confirmed running **[P10]**
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
- [ ] Lark bot credentials collected
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
- [ ] `.env.local` written with all credentials (inside `website/`)
- [ ] Global skills: `daily-checkin`, `create-routines`, `skill-creator` **[P11]**
- [ ] GitHub repo created, pushed, Vercel project imported (Root Directory=website set in dashboard) **[P5][P6]**
- [ ] `vercel link` run, env vars added via `vercel env`, deployment verified (`vercel ls`)
- [ ] Site live on Vercel (HTTP 200)
- [ ] All 8 agents fetched from GitHub canonical repo (or bundled fallback) to `~/.claude/agents/` **[P13]**
- [ ] `email-index.md` Stage 0 populated
- [ ] 8 RemoteTrigger schedules registered **[P10]**
- [ ] HANDOFF.md written **[P17]**

**Next**: Hand off HANDOFF.md to client → run `infiniteleverage-onboard` skill on client's machine.

---

## Additional Resources

- **`references/phase1-manual.md`** — Complete step-by-step for all account creation, DNS setup, API keys, and Mac Mini tool installation
- **`references/phase2-prompts.md`** — Full Claude Code prompt sequence for project scaffold, agent team build, and schedule registration
- **`scripts/setup-permissions.py`** — Python script to write `~/.claude/settings.local.json` without overwriting existing content
