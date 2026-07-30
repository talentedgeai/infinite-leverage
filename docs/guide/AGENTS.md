# Agent Guide

All 8 agents in the Infinite Leverage team — their roles, definition files, context paths, trigger phrases, skills, hard rules, and output paths.

---

## Dev Team

### Product Manager

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/product-manager.md` |
| **Context path** | `agents/product-manager/context/` |
| **Trigger (auto)** | "plan", "spec", "what should we build", "acceptance criteria", "epic" |
| **Trigger (on-demand)** | `@product-manager` |

**Skills:**
- `pm-grill-with-docs` — validate plan against project-status.html + epics
- `pm-to-issues` — break approved spec into GitHub Issues
- `pm-standup` — daily standup compilation
- `pm-epic-writing` — write epics with acceptance criteria
- `pm-documentation` — project documentation updates
- `pm-project-status` — update project-status.html
- `pm-client-interview` — structured client discovery

**Hard Rules:**
- Never approves implementation without a written, reviewed plan.
- Never creates issues without grilling the plan first (`pm-grill-with-docs`).
- Reads `git log` and `project-status.html` before every task.

**Output Paths:**
- `docs/product/epics.md` — epic list
- `docs/product/epic-status.md` — epic progress
- `docs/project-status.html` — live dashboard
- GitHub Issues (via `gh issue create`)
- Lark notifications (via `lark-cli`)

---

### Developer

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/developer.md` |
| **Context path** | `agents/developer/context/` |
| **Trigger (auto)** | "build", "implement", "code this", "fix", "debug" |
| **Trigger (on-demand)** | `@developer` |

**Skills:**
- `dev-diagnose` — structured debug loop
- `dev-zoom-out` — module context before changes
- `dev-grill` — adversarial plan interrogation
- `dev-handoff` — session/agent handoff documentation
- `dev-tdd` — strict red-green-refactor discipline
- `dev-prototype` — throwaway spike for technical unknowns
- `dev-improve-arch` — strategic module improvement
- `dev-planning` — implementation plan before coding
- `dev-github-hygiene` — PR hygiene and branch management
- `plan-protocol` — installs the plan registry, blast-radius guard and pre-push hook (any stack)
- `dev-karpathy` — deep technical reading protocol
- `dev-multi-agent` — orchestrating multiple agents in parallel
- `dev-qa-delegation` — structured handoff to QA agent

**Hard Rules:**
- Never starts implementation without an approved PM plan.
- Never force-pushes or skips CI.
- Never merges its own PR.
- Reads `git log --oneline -10` before every task.
- Runs `dev-zoom-out` before touching unfamiliar modules.

**Output Paths:**
- Feature branches → PRs
- `docs/engineering/changes/{date}-{slug}/` — change records and handoffs

---

### QA

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/qa.md` |
| **Context path** | `agents/qa/context/` |
| **Trigger (auto)** | "test", "triage", "bug", "regression", "QA report" |
| **Trigger (on-demand)** | `@qa` |

**Skills:**
- `qa-triage` — classify → score → route bugs
- `qa-best-practices` — test strategy and pyramid guidance
- `qa-documentation` — QA report writing
- `qa-planning` — test plan for an epic or feature

**Hard Rules:**
- Never skips triage — every bug is classified and scored.
- Never marks a bug as P3 without PM review if it's a regression.
- Never signs off on a feature without running against the acceptance criteria in the PM plan.

**Output Paths:**
- `docs/qa/{date}-{slug}-triage.md` — triage reports
- `docs/qa/{date}-{slug}-qa-report.md` — full QA reports
- `docs/product/epic-status.md` — known issues section
- `docs/project-status.html` — bugs table

---

### DevOps

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/devops.md` |
| **Context path** | `agents/devops/context/` |
| **Trigger (auto)** | "ci/cd", "pipeline", "deploy", "infrastructure", "pre-commit" |
| **Trigger (on-demand)** | `@devops` |

**Skills:**
- `devops-setup-pre-commit` — Husky + lint-staged + Prettier + type-check
- `devops-git-guardrails` — Claude Code hooks blocking dangerous git commands
- `devops-ops` — operational runbook for deploy, rollback, and incident response

**Hard Rules:**
- Never deploys using `vercel deploy` or any direct CLI deploy — all via `git push` → CI/CD.
- Escalates to a human engineer when infra issues exceed defined scope. **[P12]**
- Never modifies environment variables without recording the change in repo env documentation.

**Output Paths:**
- `.husky/` — pre-commit hooks
- `.claude/hooks/` — Claude Code hooks
- `.github/workflows/` — CI/CD pipeline files
- `docs/engineering/` — runbook updates

---

## Marketing Team

### Writer

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/writer.md` |
| **Context path** | `agents/writer/context/` |
| **Trigger (auto)** | "write a post", "draft content", "blog post", "social copy", "seo" |
| **Trigger (on-demand)** | `@writer` |

**Skills:**
- `writer-seo-content` — SEO-optimised blog posts with keyword strategy

**Hard Rules:**
- Does not publish — all approved content goes to Web Publisher.
- Does not generate images — that is Designer's role.
- Reads the content calendar before starting any new piece.

**Output Paths:**
- `content/topics/{slug}/blog.md` — blog post draft
- `content/topics/{slug}/seo.md` — SEO metadata
- `content/topics/{slug}/social-*.md` — social copy

---

### Designer

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/designer.md` |
| **Context path** | `agents/designer/context/` |
| **Trigger (auto)** | "generate image", "hero image", "design system", "visual", "mockup" |
| **Trigger (on-demand)** | `@designer` |

**Skills:**
- `designer-image-generation` — hero and social image generation via Gemini
- `designer-design-system` — brand tokens and design system documentation
- `designer-ui-ux` — UI mockups and screen design
- `designer-style-to-photo` — style reference to photo generation

**Hard Rules:**
- Only generates images after the Writer's copy is approved.
- Images go to `content/topics/{slug}/` (working) → `website/public/images/blog/` (final, via Web Publisher).
- Never deploys images directly to the website.

**Output Paths:**
- `content/topics/{slug}/{image-name}.webp` — generated hero images
- `content/topics/{slug}/social-*.webp` — generated social images

---

### Web Publisher

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/web-publisher.md` |
| **Context path** | `agents/web-publisher/context/` |
| **Trigger (auto)** | "publish", "build the page", "push to site", "update blog index" |
| **Trigger (on-demand)** | `@web-publisher` |

**Skills:**
- `web-publisher-publish` — React component from content, blog index update, git commit

**Hard Rules:**
- Never pushes to GitHub — commits locally and tells the operator to run `git push origin main`.
- Never publishes without approved content from Writer AND approved image from Designer.
- Always updates the blog index after publishing a new post.

**Output Paths:**
- `website/pages/blog/posts/{slug}.jsx` — React blog post component
- `website/pages/blog/index.jsx` — updated blog index
- `website/public/images/blog/{slug}.webp` — promoted image

---

### Email Marketer

| Field | Value |
|---|---|
| **Definition file** | `~/.claude/agents/email-marketer.md` |
| **Context path** | `agents/email-marketer/context/` |
| **Trigger (auto)** | "email campaign", "newsletter", "subscribers", "nurture", "brevo" |
| **Trigger (on-demand)** | `@email-marketer` |

**Skills:**
- `email-marketer-nurture` — lead nurture email sequence management

**Hard Rules:**
- Never sends without explicit operator approval — always drafts first.
- Reads Supabase subscriber list before every campaign to avoid duplicate sends.
- Never imports contacts without confirming opt-in status.

**Output Paths:**
- Brevo campaign drafts (via Brevo API)
- `email-index.md` — email send log with Stage tracking
- Lark notification to operator before any send

---

## Dev Team Chain

```
PM ──────► Developer ──────► QA
 (approved plan)   (feature done)  (bugs found?)
                                       │
                              ◄────────┘
                           Developer fixes
                                       │
                              ─────────►
                                    QA re-verifies
                                       │
                              ─────────►
                                    merge → Vercel CI/CD
```

## Marketing Team Chain

```
Writer ──────► Designer ──────► Web Publisher ──────► Email Marketer
 (approved copy)  (approved images)   (committed to git)    (draft campaign)
                                                                  │
                                                         Operator approves
                                                                  │
                                                         ─────────►
                                                              sent to subscribers
```
