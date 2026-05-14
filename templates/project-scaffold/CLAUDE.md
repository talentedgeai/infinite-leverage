# {Project Name} — Project Instructions

This file is the entry point Claude Code reads when this repo is opened. It defines roles, folder conventions, and publishing/engineering workflows.

## Stack
- Website: Next.js + Tailwind + shadcn (`website/`)
- Database: Supabase (`website/supabase/`)
- Deployment: Vercel (auto-deploy on push to `main`)
- Email: Resend or Brevo (see `agents/email-marketer/context/`)

## Folder conventions
See `templates/project-scaffold/` in the agent template repo for the canonical structure every project follows. Agents MUST honor it — do not invent new top-level folders.

## Publishing workflow
Read source content from `content/topics/<slug>/` → optimize images → generate React components via `build-page` skill → copy into `website/pages/` → update `website/pages/blog/index.jsx` → commit → hand off push command to operator.

## Cross-tool context bridge
- Read `~/Documents/Claude/shared-context/BRIDGE.md` at session start
- Update it at session end with handoff notes
