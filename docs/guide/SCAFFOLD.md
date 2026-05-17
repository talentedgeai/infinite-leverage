# Scaffold Guide

How this template repository is used by the `infiniteleverage-*` skills to bootstrap and update client machines.

---

## What This Repo Is

`talentedgeai/infiniteleverage-8-agents-template` is the **single source of truth** for the Infinite Leverage agent team.

It contains:
- **8 agent definition files** in `.claude/agents/` — the deployed team
- **35+ skill directories** in `.claude/skills/` — the team's capabilities
- **Rules files** in `.claude/rules/` — Claude Code behavioral guardrails
- **Bootstrap skill packages** in `setup-skills/` — the tools that deploy everything
- **A project scaffold template** in `templates/project-scaffold/` — the starting point for each new client project
- **This guide** in `docs/guide/` — documentation for operators and contributors

---

## Three Deployment Phases

### Phase 1 — Agents (`setup-skills/infiniteleverage-init`)

Deploys the 8 agent `.md` files from `.claude/agents/` to `~/.claude/agents/` on the client machine.

```
.claude/agents/*.md  →  ~/.claude/agents/*.md
```

Agents are the team. They define each role's persona, hard rules, skills, output paths, and trigger phrases.

### Phase 2 — Skills (`setup-skills/infiniteleverage-patch`)

Deploys all skill directories from `.claude/skills/` to `~/.claude/skills/` on the client machine.

```
.claude/skills/{skill-name}/  →  ~/.claude/skills/{skill-name}/
```

Skills are the team's playbooks — structured prompts that agents invoke when performing specific tasks (e.g. `dev-diagnose`, `pm-to-issues`, `qa-triage`).

Phase 2 also deploys rules files:

```
.claude/rules/*.md  →  ~/.claude/rules/*.md
```

Rules are always-on guardrails that Claude Code reads at every session start.

### Phase 3 — Project Scaffold (`setup-skills/infiniteleverage-init`, Phase 2)

Copies `templates/project-scaffold/` to the new client project directory. This creates:

```
~/code-projects/{project-slug}/
├── CLAUDE.md              ← project instructions (agent-aware)
├── agents/                ← per-agent context folders
├── docs/                  ← project documentation
├── standup/               ← daily check-ins
├── working_files/         ← git-ignored scratch space
└── website/               ← Next.js application
```

---

## What Gets Deployed vs What Stays Here

| Location | Deployed to client? | Purpose |
|---|---|---|
| `.claude/agents/*.md` | Yes → `~/.claude/agents/` | The 8 agent definitions |
| `.claude/skills/*/` | Yes → `~/.claude/skills/` | Skill playbooks |
| `.claude/rules/*.md` | Yes → `~/.claude/rules/` | Always-on guardrails |
| `setup-skills/` | No | Bootstrap tools — used once per client setup |
| `templates/project-scaffold/` | Yes → `~/code-projects/{slug}/` | New project starting point |
| `docs/guide/` | No | This guide — for operators and contributors |

---

## Patching (Updates After Initial Setup)

Use `setup-skills/infiniteleverage-patch` to push agent, skill, and rule updates to an already-deployed client machine.

```bash
# Apply agents + skills + rules from the canonical source
bash setup-skills/infiniteleverage-patch/scripts/apply-patch.sh
```

The patch script:
- **Adds** new agents/skills/rules that don't exist on the client machine.
- **Updates** existing agents/skills/rules that differ from the template.
- **Removes** agents that are no longer in the template (agents only, `full` mode).

No manual file copying needed — run the patch script and the client is up to date.

---

## RemoteTrigger Schedules

The init skill registers 8 cloud schedules via RemoteTrigger. Each schedule fires the relevant agent on its set cadence:

| Agent | Schedule | Task |
|---|---|---|
| PM | Monday 08:00 | Weekly standup + epic status update |
| Writer | Monday 09:00 | Draft next week's content |
| Designer | Tuesday 09:00 | Generate images for approved drafts |
| Web Publisher | Tuesday 14:00 | Build and commit published posts |
| Email Marketer | Wednesday 09:00 | Draft subscriber announcement |
| QA | Wednesday 14:00 | Run regression check |
| DevOps | Thursday 09:00 | Deployment health check |
| PM | Friday 16:00 | Weekly retrospective and handoff |

---

## Contributing to This Repo

All changes to agents, skills, or rules must go through a PR on this repo. The PR will be deployed to all client machines via `infiniteleverage-patch` on the next scheduled update cycle.

1. Branch from `main`.
2. Add or update files in `.claude/agents/`, `.claude/skills/`, or `.claude/rules/`.
3. Update `docs/guide/AGENTS.md` if agent roles or routing changes.
4. Open a PR — do not merge without a reviewer.
