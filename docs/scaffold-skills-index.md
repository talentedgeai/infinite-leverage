# Scaffold Skills Index

These skills stamp production-ready feature baselines into any Next.js + Supabase project.
Each skill asks a few customisation questions, then creates all necessary files with `TODO:` markers for project-specific overrides.

Invoke with `/scaffold-<feature>` in any project session, or reference by name in agent instructions.

---

## Available scaffold skills

| Skill | Trigger phrases | What it creates |
|---|---|---|
| `/scaffold-chatbot` | "add chatbot", "add multi-session chat", "scaffold AI chat" | Supabase schema, streaming API route, session CRUD, TanStack Query hooks, Zustand store, full chat UI (AI SDK v6) |
| `/scaffold-auth` | "add auth", "add login", "scaffold authentication", "add Supabase auth" | Supabase SSR clients, server actions (login/signup/logout/reset), OAuth callback route, TanStack Form login+signup pages, session guards |
| `/scaffold-seo` | "add SEO", "scaffold metadata", "set up sitemap", "add structured data", "add Open Graph" | Metadata helpers, JSON-LD structured data, sitemap.ts, robots.ts, next/font config, metadata examples |
| `/scaffold-rich-text` | "add markdown renderer", "scaffold markdown editor", "add rich text", "add content renderer" | ReactMarkdown renderer with GFM + syntax highlighting + custom components, copy-button code blocks, plug-and-play Markdown editor |

---

## How scaffold skills work

1. **Claude Code reads the skill** from `~/.claude/skills/scaffold-<feature>/SKILL.md`
2. **Asks customisation questions** (model choice, route paths, font names, etc.)
3. **Creates all files** with your answers substituted in
4. **Leaves `TODO:` comments** at every project-specific decision point
5. **Lists post-scaffold steps** (migrations to run, npm installs, env vars to set)

---

## Reference implementations

Each skill has a full reference implementation you can audit or diff against:

| Feature | Reference path |
|---|---|
| AI Chatbot | `templates/project-scaffold/website/` (chatbot files) |
| Auth | `templates/project-scaffold/website/lib/supabase/`, `lib/auth/`, `components/auth/` |
| SEO | `templates/project-scaffold/website/lib/seo/`, `components/seo/`, `app/sitemap.ts`, `app/robots.ts` |
| Rich-text | `templates/project-scaffold/website/lib/markdown/`, `components/markdown/`, `components/editor/` |

Spec docs: `docs/superpowers/specs/`

---

## Combining scaffold skills

Skills are independent — apply them in any combination:

**Typical full-stack project:**
```
/scaffold-auth        → auth first (chatbot needs user sessions)
/scaffold-chatbot     → configure auth guard = yes
/scaffold-seo         → add metadata to pages
/scaffold-rich-text   → add markdown renderer for AI responses
```

**Chatbot + rich-text** (AI responses rendered as Markdown):
After scaffolding both, update `MessageBubble.tsx` to use `<MarkdownRenderer>` instead of plain `<Response>` for assistant messages.

**Auth + SEO** (content site with protected dashboard):
Use `requireAuth()` from the auth scaffold in protected pages; `buildMetadata()` from the SEO scaffold on public pages.
