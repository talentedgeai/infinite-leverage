---
name: infiniteleverage-help
description: "Show the full Infinite Leverage skill menu — all available skills grouped by team with trigger phrases and what each one produces. Use when the user asks 'what can I do?', 'what skills are available?', 'show me the menu', 'infiniteleverage help', or '/infiniteleverage-help'."
---

# Infinite Leverage — Skill Menu

Print the following menu verbatim, then offer to invoke any skill the user points to.

---

## 🚀 Setup & Maintenance

| Skill | Trigger | Produces |
|-------|---------|---------|
| `infiniteleverage-init` | "set up a new machine", "bootstrap from scratch", "connect my laptop", "add my personal machine", "onboard a new computer" | Stand up a machine — Mode A (first-ever: website + 8 agents + schedules) or Mode B (additional machine connected to the existing team). Asks which at the start. |
| `infiniteleverage-patch` | "update my agents", "sync to latest", "my skills are out of date" | Health check + agents/skills/hooks synced to latest |
| `infiniteleverage-project` | "new project", "scaffold a project", "start a new client project" | New project directory scaffolded with 8-agent team wired in |
| `infiniteleverage-help` | "what can I do", "show the menu", "what skills are available" | This menu |

---

## 🛠 Developer

| Skill | Trigger | Produces |
|-------|---------|---------|
| `dev-planning` | "plan today's work", "read project status" | Daily plan drafted under `docs/plans/` |
| `dev-karpathy` | "spec first before coding", "think before building", "design the solution fully first" | Spec-first design → TDD implementation |
| `dev-tdd` | "tdd", "red-green-refactor", "test-driven" | Failing test → minimal impl → green |
| `dev-feature-plan` | "plan this feature", "break this down" | Scoped feature plan with acceptance criteria |
| `dev-brainstorm` | "brainstorm", "think through options" | Structured options + recommendation |
| `dev-diagnose` | "why is this broken", "debug", "diagnose" | Root cause analysis + fix |
| `dev-zoom-out` | "zoom out", "give me context", "I'm new to this area" | Module map + key entry points |
| `dev-grill` | "grill me", "stress-test this plan", "what could go wrong" | Devil's advocate review of a plan or design |
| `dev-prototype` | "spike", "prototype", "is this feasible" | Minimal proof-of-concept + verdict |
| `dev-improve-arch` | "refactor", "improve architecture", "tech debt" | Targeted architecture improvement plan |
| `dev-github-hygiene` | "clean up branches", "enforce PR rules", "fix commit messages" | Branch/PR/commit guardrails enforced |
| `dev-qa-delegation` | "call QA", "hand off to QA", "done implementing" | QA delegated, bugs fixed, PR merged |
| `dev-multi-agent` | "parallel agents", "wave-based", "multi-file task" | Wave-based parallel agent delegation |
| `dev-handoff` | "handoff", "wrapping up", "passing to QA" | BRIDGE.md handoff doc written |
| `create-agent` | "create an agent", "build an agent", "I need an agent that..." | Full agent package: persona + skills + evals + installed |

---

## 🧪 QA

| Skill | Trigger | Produces |
|-------|---------|---------|
| `qa-triage` | "triage", "classify this bug", "prioritise" | Bug scored P0–P3 with reproduction steps |
| `qa-best-practices` | "test strategy", "what to test", "test plan" | Test pyramid strategy for the feature |
| `qa-planning` | "QA plan", "what should QA cover" | Full QA plan with scope + exit criteria |
| `qa-documentation` | "document tests", "write test docs" | Test documentation written |

---

## ⚙️ DevOps

| Skill | Trigger | Produces |
|-------|---------|---------|
| `devops-setup-pre-commit` | "pre-commit", "husky", "lint-staged" | Pre-commit hooks configured |
| `devops-git-guardrails` | "protect main", "git guardrails", "branch rules" | Branch protection + guardrail rules applied |
| `devops-ops` | "check pipeline", "CI status", "deployment health" | Pipeline health report + fixes |

---

## 📋 Product Manager

| Skill | Trigger | Produces |
|-------|---------|---------|
| `pm-epic-writing` | "write an epic", "acceptance criteria", "spec this feature" | Epic with AC written to `docs/product/epics.md` |
| `pm-to-issues` | "create issues", "break into tickets", "to issues" | GitHub issues created from the epic |
| `pm-grill-with-docs` | "validate plan against docs", "does this match the spec", "check plan for gaps" | Plan verified against product docs |
| `pm-standup` | "standup", "daily briefing", "what shipped" | Standup summary from git log |
| `pm-client-interview` | "client interview", "intake", "gather requirements" | Structured intake doc written |
| `pm-project-status` | "update project status", "project health" | `docs/project-status.html` updated |
| `pm-documentation` | "update docs", "write product docs" | Product documentation updated |
| `pm-clarify-guard` | "clarify", "ambiguous requirement", "missing detail" | Clarifying questions surfaced before building |
| `pm-analyze-split` | "split this epic", "too big", "break this up" | Epic split into deliverable chunks |
| `pm-constitution-sync` | "update product principles", "our strategy has changed", "sync the constitution" | Product constitution synced |

---

## 🏗 Scaffold

| Skill | Trigger | Produces |
|-------|---------|---------|
| `scaffold-auth` | "add auth", "set up login", "I need authentication" | Supabase auth (email + OAuth) stamped into the Next.js project |
| `scaffold-chatbot` | "add a chatbot", "multi-session AI chat", "build a chat interface" | Full AI chatbot with sessions, streaming, and history wired in |
| `scaffold-seo` | "add SEO", "set up metadata", "I need a sitemap" | SEO metadata, JSON-LD, sitemap, and robots.txt added |
| `scaffold-performance` | "improve loading", "add skeletons", "optimize performance" | Suspense boundaries, skeleton screens, and LCP best practices |
| `scaffold-rich-text` | "add a markdown editor", "render rich text", "I need a text editor" | Markdown renderer + editor component stamped in |
| `scaffold-notifications` | "add notifications", "I need toast alerts", "set up in-app notifications" | Notification system (realtime bell + Supabase table) stamped in |
| `scaffold-file-upload` | "add file upload", "I need drag and drop uploads", "set up file storage" | File upload UI + Supabase Storage wiring stamped in |
| `scaffold-dashboard` | "add a dashboard", "I need a sidebar layout", "scaffold the admin area" | Protected layout shell with Sidebar, MobileDrawer, Breadcrumbs, auth guard |
| `scaffold-payments` | "add Stripe", "I need billing", "set up subscriptions" | Stripe Checkout + webhook + subscriptions table + feature-gate guard |

---

## ✍️ Writer

| Skill | Trigger | Produces |
|-------|---------|---------|
| `writer-seo-content` | "seo content", "keyword research", "meta description" | SEO-optimised blog post or page copy |

---

## 🎨 Designer

| Skill | Trigger | Produces |
|-------|---------|---------|
| `designer-image-generation` | "generate image", "hero image", "create a visual" | Gemini-generated image saved as WebP |
| `designer-design-system` | "design system", "brand tokens", "colour palette" | Design tokens + component spec |
| `designer-ui-ux` | "mockup", "wireframe", "ui design" | UI/UX design spec or prototype |
| `designer-style-to-photo` | "style photo", "apply brand style", "retouch" | Brand-styled photo output |

---

## 🌐 Web Publisher

| Skill | Trigger | Produces |
|-------|---------|---------|
| `web-publisher-publish` | "publish", "push to site", "build the page" | React component + blog index updated + commit staged |

---

## 📧 Email Marketer

| Skill | Trigger | Produces |
|-------|---------|---------|
| `email-marketer-nurture` | "email campaign", "newsletter", "nurture sequence" | Email draft written, ready for operator approval |

---

## 🔧 Global / Admin

| Skill | Trigger | Produces |
|-------|---------|---------|
| `daily-checkin` | "daily checkin", "morning briefing", "how's the team" | Team status summary across all agents |
| `create-local-routine` | "create a routine", "automate this", "schedule this locally" | CronCreate routine registered |
| `create-agent` | "create an agent", "I need a new agent role" | Full agent package installed to `.claude/agents/` |
| `marketing-strategist` | "marketing strategy", "content plan", "campaign brief" | Marketing strategy or campaign brief |
| `global-caveman` | "explain this simply", "I don't understand this", "explain like I'm 5" | Complex concept explained simply |

---

After printing the menu, say:

> "Point me at any skill and I'll run it — or just describe what you want to do and I'll match it."
