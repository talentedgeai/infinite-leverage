# Infinite Leverage Plugin

This plugin provides the Infinite Leverage 8-agent system for Claude Desktop Team.

## What this plugin does

On every session start, `hooks/session-start` runs four stages:
1. **Init check** — detects whether the 8 agents are installed; prompts `/infiniteleverage-init` if not
2. **Version check** — compares local template version against canonical GitHub repo; surfaces patch advisory if behind
3. **Context injection** — ensures agent routing rules are active even without a project CLAUDE.md
4. **Usage awareness** — injects a compact token-usage briefing into Claude's context

## Setup skills (in `skills/`)

| Skill | Trigger |
|---|---|
| `/infiniteleverage-init` | First-time Mac Mini setup — zero to live site + 8 agents |
| `/infiniteleverage-onboard` | Client onboarding on a new machine |
| `/infiniteleverage-patch` | Pull latest agent definitions from canonical template repo |
| `/infiniteleverage-project` | Scaffold a new project for an existing operator |

## Agent routing

When this plugin is active, all 8 Infinite Leverage agents are available. Route requests using `@agent-name` or let auto-routing handle it — the session-start hook ensures routing rules are always injected.

| Agent | Handles |
|---|---|
| **product-manager** | roadmap, epics, daily plan, project-status.html |
| **developer** | code, bugs, refactoring, Supabase, env vars |
| **qa** | testing, triage, QA plans, regression |
| **devops** | CI/CD, Vercel, GitHub Actions |
| **writer** | blog posts, SEO, copy, social media |
| **designer** | images, design system, UI mockups |
| **web-publisher** | publish content → Next.js → commit |
| **email-marketer** | email campaigns, Resend/Brevo, sequences |

## Source of truth

All agent definitions and operational skills live in the canonical template repo:
`https://github.com/talentedgeai/infiniteleverage-8-agents-template`

This plugin repo is the **exposure layer only** — it contains setup skills and hooks. Never edit agent definitions here; edit in the template repo and run `/infiniteleverage-patch` to sync.
