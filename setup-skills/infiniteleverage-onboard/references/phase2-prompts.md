# Personal Laptop — Phase 2: Claude Code Prompts

Open Claude Code in the project: `cd ~/code-projects/{project-slug} && claude`

Run each prompt in sequence. Claude Code executes fully before the next starts.

---

## Prompt 1 — Prerequisites check + global directories

```
Set up this laptop:

1. Check Claude Code CLI is installed and authenticated:
   claude --version
   If not installed: npm install -g @anthropic-ai/claude-code
   If not authenticated: run `claude`, complete OAuth with operator Claude Pro account, type /exit

2. Check Vercel CLI is installed and authenticated:
   vercel whoami
   If not installed: npm install -g vercel
   If not authenticated: vercel login → select "Continue with GitHub" → authorize in browser

3. Create global directories:
   mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/rules

4. Run scripts/setup-permissions.py from the personal-laptop skill folder to write
   ~/.claude/settings.local.json — adds Bash(*), WebFetch, Skill(*), and Supabase MCP
   permissions without overwriting existing content.

5. Print ~/.claude/settings.local.json to confirm.
```

---

## Prompt 2 — Global CLAUDE.md

```
Write ~/.claude/CLAUDE.md:

# Global Claude Code Rules

## Identity
You are the AI development team for {Business Name}. You have 8 specialist agents available globally.

## Agents
All 8 agents are installed in ~/.claude/agents/.
Agents are defined in the agents repo at ~/{clientslug}-agents/.

## Product documentation
All product docs live under docs/product/:
- docs/product/product.md — strategic product document (thesis, problem, users, JTBD, wedge, differentiation, market, business model, assumptions, metrics, 90-day bets)
- docs/product/epics.md — epics in The problem / The mechanism / What it bundles / What success looks like / Why it goes first format only
- docs/product/epic-status.md — pipeline stages table + at-a-glance + drilldowns with Shipped/Outstanding + bug tracking
- docs/product/01-product-timeline.md — phased roadmap
- docs/project-status.html — single-file HTML dashboard at docs/ root (not inside docs/product/)
Never use Thesis, Bundle, Mechanism, Success criterion, Hypothesis, Acceptance criteria, or Priority signal in epics.md.

## Environment variables
- Every project must have a `.env.example` at the repo root with all required vars listed (empty values, one-line comments).
- If `.env.example` does not exist when starting implementation, create it first.
- Every new env var introduced in code must be added to `.env.example` on the same commit.
- Never commit `.env.local`, `.env.production`, or any file containing real secrets.

## Engineering rules
See ~/.claude/rules/global-engineering.md for all code and git discipline rules.

## Content queue
Add a brief.md to any content/topics/{slug}/ folder to queue a post.
The Writer picks the oldest unwritten topic automatically on schedule.

## Publishing workflow (automated Mon–Wed — runs on Mac Mini)
1. Monday 9am    — Writer writes the post + image prompt
2. Tuesday 9am   — Designer generates the hero image
3. Wednesday 9am — Web Developer builds and stages the page
4. Run: git push origin main (owner only)
```

Then inject the canonical Agent Delegation section into ~/.claude/CLAUDE.md so the laptop knows how to auto-route requests to the 8 agents:

```bash
bash ~/.claude/skills/infiniteleverage-onboard/scripts/inject-agent-delegation.sh \
  ~/.claude/CLAUDE.md
```

After cloning the existing project repo (later prompt), repeat for the project's CLAUDE.md:

```bash
bash ~/.claude/skills/infiniteleverage-onboard/scripts/inject-agent-delegation.sh \
  ~/code-projects/{project-slug}/CLAUDE.md
```

The script is idempotent — safe to re-run; only updates the block between the BEGIN/END markers.

---

## Prompt 3 — Global engineering rules

```
Write ~/.claude/rules/global-engineering.md:

# Global Engineering Rules

## Git
- Run `git status` before any file work.
- Never force-push to any branch.
- Never skip hooks with `--no-verify`.
- Never use `git add .` or `git add -A` — stage files explicitly by name.
- Never create a commit unless explicitly instructed.

## Branch and PR discipline
- Never push directly to `main` or `master`. All changes go through a pull request.
- Confirm the correct base branch before opening a PR.

## Deployment
- Never deploy using `vercel deploy` or `vercel --prod` directly.
- All deployments through `git push` → CI/CD only.

## Secrets
- Never commit `.env` files, API keys, tokens, or passwords.
- Never include secrets in code, comments, or commit messages.

## Approvals
- Social posts → draft for approval first.
- Email campaigns → ALWAYS require human approval before sending.

## Destructive operations
- Always confirm before: `rm -rf`, `git reset --hard`, dropping database tables.
```

---

## Prompt 4 — Write credentials to ~/.claude/.env

```
Write ~/.claude/.env with these values from the credentials file Dave transferred:

SUPABASE_URL={from-credentials-file}
SUPABASE_ANON_KEY={from-credentials-file}
SUPABASE_SERVICE_ROLE_KEY={from-credentials-file}
GEMINI_API_KEY={from-credentials-file}
RESEND_API_KEY={from-credentials-file}
LARK_APP_ID={from-credentials-file}
LARK_APP_SECRET={from-credentials-file}
LARK_WEBHOOK_URL={from-credentials-file}

Replace each placeholder with the actual value from the credentials file.
```

---

## Prompt 5 — Supabase MCP

```
Set up the Supabase MCP server on this machine:
1. Fetch the latest Supabase MCP setup documentation so you follow the current install method
2. Add the MCP server to ~/.claude/settings.local.json
3. Start the Supabase authentication flow and give me the browser URL to authorize
4. After I tell you I've completed authorization, finish the auth flow
5. Verify the connection by listing the Supabase projects on this account
```

> **Manual step**: Claude outputs a URL → open in browser → **Authorize** → tell Claude "done".

---

## Prompt 6 — Global skills

```
Install two global skills:

Create ~/.claude/skills/daily-checkin/SKILL.md:
---
name: daily-checkin
description: This skill should be used when the user says "daily checkin", "morning standup", or "what's on today". Reads recent git commits, open PRs, and pending content briefs; outputs a plan for the day.
---
Steps: (1) git log --oneline -10 (2) gh pr list --state open (3) check content/topics/ for brief.md without blog.md (4) output: what shipped, open PRs, content queued

Create ~/.claude/skills/create-routines/SKILL.md:
---
name: create-routines
description: This skill should be used when the user says "create task", "new task", "log task", or "add a task". Creates a structured task file with description, acceptance criteria, and priority.
---
Steps: (1) ask: title, description, priority (2) write to working_files/tasks/{YYYY-MM-DD}-{slug}.md (3) format with Title / Priority / Created / Description / Acceptance criteria
```

---

## Prompt 7 — Clone agents repo and install all 8 agents

```
Install the AI agent team from GitHub:

1. Clone the agents repo:
   cd ~
   gh repo clone {clientslug}/{clientslug}-agents

2. Verify all 8 agents are present:
   ls ~/{clientslug}-agents/.claude/agents/
   # Expected: developer.md, devops.md, designer.md, email-marketer.md,
   #           product-manager.md, qa.md, web-publisher.md, writer.md

3. Install all 8 agents globally:
   cp -r ~/{clientslug}-agents/.claude/agents/* ~/.claude/agents/
   echo "✅ All 8 agents installed."

4. Install the sync-agents skill:
   cp -r ~/{clientslug}-agents/skills/sync-agents ~/.claude/skills/sync-agents
   echo "✅ sync-agents installed."

5. Run first sync to confirm round-trip:
   cd ~/{clientslug}-agents
   git pull origin main
   cp -r .claude/agents/* ~/.claude/agents/
   echo "✅ Agents synced from GitHub."
```

---

## Prompt 8 — Test all 8 agents

```
Test each of the 8 agents by asking: "@{agent-name} what are you?"

Test in this order:
@product-manager what are you?
@developer what are you?
@qa what are you?
@devops what are you?
@writer what are you?
@designer what are you?
@web-publisher what are you?
@email-marketer what are you?

All 8 must respond before proceeding. If any don't respond, run "sync agents" and retry.
```

---

## Prompt 9 — Verify email-index.md and confirm schedules

```
1. Verify the email sequence index exists and has Stage 0 populated:
   cat ~/{clientslug}-agents/agents/email-marketer/context/email-index.md
   Confirm: file exists AND Stage 0 has a real subject line and body (not just placeholders).
   If missing or empty — stop and flag to Dave before proceeding.

2. Confirm scheduled work is running on the Mac Mini:
   @product-manager list all registered schedules
   Expected: 10 schedules (1 devops-daily + 1 pm-daily-plan + 1 developer-daily + 1 pm-standup-compile + 1 pm-eod-summary + 1 pm-weekly-rag + 1 writer-weekly + 1 designer-weekly + 1 web-publisher-weekly + 1 email-marketer-weekly)
```

---

## Prompt 10 — First Product Manager briefing

```
@product-manager I just finished setting up my AI team on my laptop.
Walk me through what you need from me to serve this project well.
What business context should I share with you right now?
```

The Product Manager will ask questions and set itself up to give useful daily briefings from day one.
