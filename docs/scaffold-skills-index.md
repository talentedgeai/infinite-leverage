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
| `/scaffold-rich-text` | "add markdown renderer", "scaffold markdown editor", "add rich text", "add content renderer" | ReactMarkdown renderer with GFM + syntax highlighting + custom components, MDXEditorFull (WYSIWYG), lightweight @uiw editor option |
| `/scaffold-performance` | "scaffold performance", "add loading states", "add skeletons", "improve loading time", "add Suspense" | loading.tsx, 5 skeleton components (Card/Table/Text/Avatar/PageHeader), clientOnly/lazyLoad dynamic import helpers |
| `/scaffold-notifications` | "add notifications", "scaffold notification bell", "add realtime notifications" | Supabase notifications table + RLS, realtime subscription, NotificationBell component, TanStack Query hooks |
| `/scaffold-file-upload` | "add file upload", "scaffold storage", "add drag and drop upload" | Supabase Storage signed URL API, FileUpload drag-and-drop component, XHR upload hook with progress, next/image remote config |
| `/scaffold-dashboard` | "scaffold dashboard", "add dashboard layout", "add sidebar nav" | Protected layout shell, Sidebar nav, Breadcrumbs, responsive MobileDrawer, auth guard wired in |
| `/scaffold-payments` | "add payments", "scaffold Stripe", "add subscriptions", "add billing" | Stripe Checkout session, customer portal, webhook handler, subscriptions table + RLS, feature-gate guard, PricingCard + UpgradeButton |

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
| AI Chatbot | `templates/project-scaffold/website/app/api/chat/`, `lib/chat/`, `components/chat/` |
| Auth | `templates/project-scaffold/website/lib/supabase/`, `lib/auth/`, `components/auth/` |
| SEO | `templates/project-scaffold/website/lib/seo/`, `components/seo/`, `app/sitemap.ts`, `app/robots.ts` |
| Rich-text | `templates/project-scaffold/website/lib/markdown/`, `components/markdown/`, `components/editor/` |
| Performance | `templates/project-scaffold/website/components/ui/skeletons/`, `lib/perf/`, `app/dashboard/loading.tsx` |
| Notifications | `templates/project-scaffold/website/app/api/notifications/`, `lib/notifications/`, `components/notifications/` |
| File Upload | `templates/project-scaffold/website/app/api/upload/`, `lib/upload/`, `components/upload/` |
| Dashboard | `templates/project-scaffold/website/app/dashboard/layout.tsx`, `lib/dashboard/`, `components/dashboard/` |
| Payments | `templates/project-scaffold/website/app/api/billing/`, `lib/billing/`, `components/billing/` |

Spec docs: `docs/superpowers/specs/`

---

## Combining scaffold skills

Skills are independent — apply them in any combination:

**Recommended order for a full SaaS app:**
```
/scaffold-auth           → auth first (everything else needs user sessions)
/scaffold-dashboard      → protected layout shell (requires auth)
/scaffold-seo            → add metadata to public pages
/scaffold-performance    → loading states + skeletons
/scaffold-chatbot        → AI chat with multi-session history (configure auth guard = yes)
/scaffold-rich-text      → markdown renderer for AI responses + CMS editor
/scaffold-notifications  → realtime notification bell (mount in dashboard Header)
/scaffold-file-upload    → drag-and-drop uploads to Supabase Storage
/scaffold-payments       → Stripe billing + feature gates
```

**Chatbot + rich-text** (AI responses rendered as Markdown):
After scaffolding both, update `MessageBubble.tsx` to use `<MarkdownRenderer>` instead of plain `<Response>` for assistant messages.

**Auth + SEO** (content site with protected dashboard):
Use `requireAuth()` from the auth scaffold in protected pages; `buildMetadata()` from the SEO scaffold on public pages.

**Dashboard + notifications** (common SaaS pattern):
Mount `<NotificationBell>` inside the `<Header>` right-side slot after scaffolding both.

**Payments + dashboard** (gated features):
Use `requirePlan('pro')` from the payments scaffold inside protected dashboard routes.
