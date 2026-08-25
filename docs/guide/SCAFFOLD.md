# Scaffold Guide

How this template repository is used by the `infiniteleverage-*` skills to bootstrap, onboard, and scaffold client projects.

---

## What This Repo Is

`talentedgeai/infinite-leverage` is the **single source of truth** for the Infinite Leverage agent team.

It contains:
- **8 agent definition files** in `.claude/agents/` — the deployed team
- **35+ skill directories** in `.claude/skills/` — the team's capabilities
- **Rules files** in `.claude/rules/` — Claude Code behavioral guardrails
- **Bootstrap skill packages** in `setup-skills/` — the tools that deploy everything
- **A project scaffold template** in `templates/project-scaffold/` — the starting point for each new client project
- **This guide** in `docs/guide/` — documentation for operators and contributors

---

## Four Skills, Four Jobs

| Skill | Who runs it | When |
|---|---|---|
| `infiniteleverage-init` | Operator, on the Mac Mini | First time only — bootstraps the machine from zero |
| `infiniteleverage-onboard` | Client, on their laptop | After Mac Mini is live — connects client's personal machine |
| `infiniteleverage-project` | Operator or client | Any time — scaffolds a new client project directory |
| `infiniteleverage-patch` | Operator | Ongoing — pushes agent/skill/rule updates to deployed machines |

---

## Phase 1 — Machine Bootstrap (`infiniteleverage-init`)

**Runs on:** the Mac Mini (or any operator machine being set up from zero)  
**Prerequisite:** Homebrew + git only

`infiniteleverage-init` is the first-time full setup. It runs in two parts:

**Phase 1A — Claude Chat (manual prerequisites):**
- Google Workspace, GitHub, Vercel, Supabase accounts created
- API keys collected: Gemini, Resend + DNS, Supabase (+ Lark if using)
- Claude Code Desktop installed and signed in

**Phase 1B — Claude Code (automated):**
- Installs tools: `gh`, `node`, `jq`, `ffmpeg`, `vercel`, `supabase`, `resend` CLIs
- Writes `~/.claude/settings.local.json` with global permissions
- Writes `~/.claude/rules/global-engineering.md` and `~/.claude/rules/agent-routing.md`
- Configures Supabase MCP
- Fetches all 8 agents from this repo → `~/.claude/agents/`
- Deploys all skills from this repo → `~/.claude/skills/`
- Registers 8 RemoteTrigger cloud schedules
- Writes `HANDOFF.md` for the client

```
setup-skills/infiniteleverage-init/
├── SKILL.md                     ← the skill
├── agents/                      ← bundled agent fallback copies
├── .claude/skills/              ← bundled skill fallback copies
└── references/
    ├── phase1-manual.md         ← step-by-step for accounts + API keys
    ├── phase2-prompts.md        ← Claude Code prompt sequence
    └── env-template.md          ← credentials file template
```

---

## Phase 2 — Client Laptop Onboarding (`infiniteleverage-onboard`)

**Runs on:** the client's personal laptop  
**Prerequisite:** Mac Mini bootstrap complete — website is live on Vercel

`infiniteleverage-onboard` connects a client's personal machine to the already-running AI team. The Mac Mini is already set up; this just mirrors the agent team and project onto the client's laptop so they can work locally.

**What it does:**
- Installs Homebrew, git, `gh`, Claude Code on the client's machine
- Clones the project repo from GitHub
- Fetches all 8 agents → `~/.claude/agents/`
- Deploys all skills → `~/.claude/skills/`
- Runs a quick-win: client sees their live website running locally before any config

```
setup-skills/infiniteleverage-onboard/
├── SKILL.md                     ← the skill
├── agents/                      ← bundled agent fallback copies
├── .claude/skills/              ← bundled skill fallback copies
└── references/
    └── phase2-prompts.md        ← Claude Code prompt sequence for laptop setup
```

---

## Phase 3 — New Project Scaffold (`infiniteleverage-project`)

**Runs on:** any machine with Claude Code  
**Prerequisite:** Agents and skills already deployed (init or onboard complete)

`infiniteleverage-project` scaffolds a brand-new project directory from `templates/project-scaffold/` in this repo. It substitutes all `{placeholders}`, wires the 8-agent team into `.claude/`, initialises git, and prints next steps.

**What it creates:**

```
~/code-projects/{project-slug}/
├── CLAUDE.md                    ← project instructions with agent routing
├── .claude/
│   └── agents/ → CLAUDE.md references ~/.claude/agents/
├── agents/                      ← per-agent context folders (persona, workflows)
├── docs/                        ← project documentation (epics, status, engineering)
├── standup/                     ← daily check-ins and briefings
├── working_files/               ← git-ignored scratch space
└── website/                     ← Next.js application
    ├── pages/
    ├── components/
    ├── public/
    └── supabase/
```

All operations are inline — no external `.sh` dependencies. Every step Claude executes is visible and auditable.

```
setup-skills/infiniteleverage-project/
└── SKILL.md                     ← the skill (self-contained, no scripts)

templates/project-scaffold/      ← the source files this skill copies from
├── CLAUDE.md
├── FOLDER-STRUCTURE.md
└── agents/
    ├── product-manager/context/
    ├── developer/context/
    └── ...
```

---

## Ongoing — Patching (`infiniteleverage-patch`)

**Runs on:** any deployed machine  
**Prerequisite:** Machine already set up (init or onboard)

`infiniteleverage-patch` pushes agent, skill, and rule updates from this repo to an already-deployed client machine.

```bash
bash setup-skills/infiniteleverage-patch/scripts/apply-patch.sh
```

The patch script runs three phases:
- **Phase 1 — Agents**: adds new, updates modified, removes deprecated agents
- **Phase 2 — Skills**: adds new, updates modified skill directories
- **Phase 3 — Rules**: adds new, updates modified rule files

No manual file copying needed — run the patch script and the client is up to date.

```
setup-skills/infiniteleverage-patch/
├── SKILL.md                     ← the skill + health check table
├── agents/                      ← bundled agent fallback copies
├── .claude/skills/              ← bundled skill fallback copies
└── scripts/
    ├── apply-patch.sh           ← deploys agents + skills + rules
    ├── health-check.sh          ← validates deployed state
    └── inject-agent-delegation.sh ← refreshes AGENT-DELEGATION block in CLAUDE.md files
```

---

## What Gets Deployed vs What Stays Here

| Location in this repo | Deployed to client machine? | Destination |
|---|---|---|
| `.claude/agents/*.md` | Yes (init / onboard / patch) | `~/.claude/agents/` |
| `.claude/skills/*/` | Yes (init / onboard / patch) | `~/.claude/skills/` |
| `.claude/rules/*.md` | Yes (init / onboard / patch) | `~/.claude/rules/` |
| `templates/project-scaffold/` | Yes (project skill) | `~/code-projects/{slug}/` |
| `setup-skills/` | No — used by operator only | Stays in this repo |
| `docs/guide/` | No | Stays in this repo |

---

## RemoteTrigger Schedules

`infiniteleverage-init` registers 8 cloud schedules. Each fires the relevant agent automatically:

| Agent | Schedule | Task |
|---|---|---|
| PM | Mon–Fri 08:00 | Daily standup + project-status.html update |
| PM | Mon–Fri 10:10 | Auto-approve P0 items if no human response (conditional) |
| Writer | Monday 09:00 | Draft this week's content |
| Designer | Tuesday 09:00 | Generate images for approved Writer drafts |
| Web Publisher | Tuesday 14:00 | Build and commit published posts |
| Email Marketer | Wednesday 09:00 | Draft subscriber announcement |
| QA | Wednesday 14:00 | Regression check |
| DevOps | Thursday 09:00 | Deployment health check |
| PM | Friday 16:00 | Weekly retrospective + next week planning |

---

## Contributing to This Repo

All changes to agents, skills, or rules must go through a PR on this repo. The PR is deployed to all client machines via `infiniteleverage-patch` on the next update cycle.

1. Branch from `main`.
2. Add or update files in `.claude/agents/`, `.claude/skills/`, or `.claude/rules/`.
3. Update `docs/guide/AGENTS.md` if agent roles or routing changes.
4. Open a PR — do not merge without a reviewer.
