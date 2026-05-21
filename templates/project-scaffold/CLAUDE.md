# {Project Name} — Project Instructions

This file is the entry point Claude Code reads when this repo is opened. It defines roles, folder conventions, and publishing/engineering workflows.

## Stack
- Website: Next.js + Tailwind + shadcn (`website/`)
- Database: Supabase (`website/supabase/`)
- Deployment: Vercel (auto-deploy on push to `main`)
- Email: Resend or Brevo (see `agents/email-marketer/context/`)

<!-- BEGIN: AGENT-DELEGATION (managed by infiniteleverage skills — do not delete this block) -->
## Agent delegation (auto-routing)

Routing is handled automatically by `~/.claude/rules/agent-routing.md` (always active). Use `/use-dev-team` or `/use-marketing-team` skills for the full routing table and handoff chain.

**Core rules:**
1. Pick exactly **one** agent per turn — don't run two in parallel unless the operator explicitly says so.
2. If a request spans agents (e.g., "write a blog *and* publish it"), call them **in sequence**: writer → designer → web-publisher.
3. If unclear which agent fits, **ask the operator** before assuming.
4. Cross-cutting engineering rules live in `.claude/rules/global-engineering.md` — every agent honors them.
5. Project-level persona overrides for each agent live in `agents/<name>/context/persona.md` — read these on first invocation.
<!-- END: AGENT-DELEGATION -->

## Folder conventions
See `FOLDER-STRUCTURE.md` at the project root for the canonical structure every project follows. Agents MUST honor it — do not invent new top-level folders.

## Publishing workflow
Read source content from `content/topics/<slug>/` → optimize images → generate React components via `build-page` skill → copy into `website/pages/` → update `website/pages/blog/index.jsx` → commit → hand off push command to operator.

## Cross-tool context bridge
- Read `~/Documents/Claude/shared-context/BRIDGE.md` at session start
- Update it at session end with handoff notes
