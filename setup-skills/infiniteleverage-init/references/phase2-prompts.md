# Mac Mini — Phase 2: Claude Code Prompts

Open Terminal on the Mac Mini, then run: `claude`
A prompt will appear — paste each numbered prompt below and press Enter. Wait for it to finish before running the next one.

---

## Prompt 1 — Install tools + global permissions

```
Set up the Mac Mini tools and Claude Code configuration:

1. Install remaining tools:
   brew install gh node jq ffmpeg
   npm install -g vercel @anthropic-ai/claude-code resend

   Verify all CLIs:
   gh --version && node --version && jq --version && vercel --version && claude --version && resend --version

2. Authenticate GitHub CLI:
   gh auth login
   # → GitHub.com, HTTPS, Login with browser
   gh auth status

3. Authenticate Vercel CLI:
   vercel login
   # → select "Continue with GitHub" → browser opens → authorize → return to terminal
   vercel whoami   # confirm your username appears

4. Authenticate Resend CLI:
   resend login
   # → browser opens → sign in to resend.com → authorize → return to terminal
   # If resend login is not available, authenticate via API key instead:
   #   export RESEND_API_KEY={from-credentials-file}
   #   resend domains list   # confirm the client domain appears as verified
   # Save the API key to ~/.zshrc or ~/.bash_profile so it persists across sessions:
   #   echo 'export RESEND_API_KEY={from-credentials-file}' >> ~/.zshrc

5. Authenticate Claude Code (opens browser):
   claude
   # Complete OAuth in browser, then type /exit

6. Create global directories:
   mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/rules

7. Run scripts/setup-permissions.py from this skill folder to write ~/.claude/settings.local.json
   (adds Bash(*), WebFetch, Skill(*), Supabase MCP permissions without overwriting existing content)

8. Print ~/.claude/settings.local.json to confirm.
```

---

## Prompt 2 — Global engineering rules
> **[Protocol 3]** The stack is Claude + GitHub + Vercel + Supabase. These rules enforce how that stack is used safely.

```
Write ~/.claude/rules/global-engineering.md with these exact contents:

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

## Environment variables
- Every project must have a `.env.example` at the repo root with all required and optional vars listed (empty values, one-line comments).
- Use `references/env-template.md` from the infiniteleverage-init skill as the starting template.
- If `.env.example` does not exist when starting implementation work, create it first.
- Every new env var introduced in code must be added to `.env.example` on the same commit.
- Optional vars (Stripe, Sentry) go commented out with a `#` prefix.

## Approvals
- Social posts → draft for approval first.
- Email campaigns → ALWAYS require human approval before sending.

## Destructive operations
- Always confirm with the user before: `rm -rf`, `git reset --hard`, dropping database tables.
```

---

## Prompt 3 — Supabase MCP
> **[Protocol 7]** Supabase is the data layer — contact forms, subscribers, CRM. The MCP lets Claude talk to it directly.

```
Set up the Supabase MCP server on this machine:
1. Fetch the latest Supabase MCP setup documentation so you follow the current install method
2. Add the MCP server to ~/.claude/settings.local.json
3. Start the Supabase authentication flow and give me the browser URL to authorize
4. After I tell you I've completed authorization, finish the auth flow
5. Verify the connection by listing the Supabase projects on this account and confirming {project-slug} is present
```

> **Manual step**: Open the URL Claude outputs → click **Authorize** → tell Claude "done".
>
> Note: The Supabase project was already created during Phase 1 account setup. Do NOT create a new project here.

---

## Prompt 4 — Project scaffold
> **[Protocol 4]** Agents are folders, not magic — every context file lives at an explicit path. **[Protocol 8]** The design system (`docs/brand/`) is written before any component ever gets built.

```
Create a project at ~/code-projects/{project-slug}/ that follows the Infinite Leverage folder structure:

mkdir -p ~/code-projects/{project-slug}
cd ~/code-projects/{project-slug}

mkdir -p agents/{product-manager,developer,qa,devops,writer,designer,web-publisher,email-marketer}/{context,skills}
mkdir -p content/{topics,content-calendar}
mkdir -p docs/architecture/{templates,workflows}
mkdir -p docs/{brand,engineering,product,qa,features,archive,plans}
mkdir -p docs/engineering/changes
mkdir -p docs/engineering/prompts
mkdir -p emails/drafts resources
mkdir -p standup/{individual,briefings}
mkdir -p working_files
mkdir -p .claude/{agents,skills,rules}

Scaffold Next.js 16 in the website/ subdirectory:
npx create-next-app@16 website \
  --typescript --tailwind --app --eslint \
  --src-dir --import-alias "@/*" \
  --agents-md --disable-git --yes

cd website && npx shadcn@latest init --defaults && cd ..

Write .gitignore at the project root covering: website/node_modules/, website/.next/, website/.env.local, working_files/, .env, .env.local, .env.*.local, .claude/settings.local.json, *.psd, *.ai, *.mov, *.mp4

Configure fonts in website/src/app/layout.tsx: Inter Tight (sans) + JetBrains Mono (mono) via next/font/google, CSS variables --font-inter-tight and --font-jetbrains-mono

Configure website/tailwind.config.ts with fontFamily.sans → var(--font-inter-tight) and fontFamily.mono → var(--font-jetbrains-mono)

Replace website/src/app/globals.css with Infinite Leverage design tokens:
@tailwind base; @tailwind components; @tailwind utilities;
:root {
  --ink: #0B1426; --ink-soft: #1F2A3D;
  --gray-1: #94A3B8; --gray-2: #64748B; --gray-3: #CBD5E1;
  --rule: #E2E8F0; --blue: #2563EB; --blue-soft: #DBEAFE;
  --cream: #F2EDE3; --paper: #FFFFFF;
}
body { @apply font-sans antialiased; color: var(--ink); background: var(--paper); }

Write ~/code-projects/{project-slug}/CLAUDE.md with: business name, stack (Next.js 16 App Router TypeScript), folder structure tree, Next.js 16 conventions (proxy.ts not middleware.ts, server components by default), engineering rules summary, content queue instructions, automated pipeline schedule.

Then inject the canonical Agent Delegation section so Claude knows how to auto-route requests to the 8 agents. Use the bundled script (single source of truth — never hand-write the table):

```bash
bash ~/.claude/skills/infiniteleverage-init/scripts/inject-agent-delegation.sh \
  ~/code-projects/{project-slug}/CLAUDE.md
```

Also inject it into the global ~/.claude/CLAUDE.md so machine-wide invocations route correctly:

```bash
bash ~/.claude/skills/infiniteleverage-init/scripts/inject-agent-delegation.sh \
  ~/.claude/CLAUDE.md
```

The script is idempotent — running it again refreshes the block between the BEGIN/END markers without touching surrounding content.

Research and document design system presets:
- WebSearch for: "best design systems for [business type] website 2024 typography palette"
- Document 5 distinct presets in docs/brand/style-guide.md
- Each preset must contain:
  name: (e.g. "Editorial", "Technical", "Warm", "Minimal", "Bold")
  use-case: one sentence on what content type or brand tone this suits
  typography: heading font + body font pair (Google Fonts preferred)
  palette: primary, secondary, background, text hex values
  spacing-scale: compact / balanced / generous
  tone: one adjective (e.g. authoritative, approachable, clean, energetic)
- Leave a blank line after each preset for the Designer to annotate which was used

Create the Developer agent definition now — this agent is needed before the others
to build the first personalized page:
Write .claude/agents/developer.md using the full Developer definition from
~/.claude/skills/infiniteleverage-init/references/mac-mini-agents.md

Invoke the Developer agent to build the hello-client landing page:
"Using the business name, tagline, and service description from CLAUDE.md and docs/product/overview.md
(if it exists) or from the credentials file, build a personalized landing page in website/src/app/page.tsx.
Apply the design tokens from globals.css and use the first design preset from docs/brand/style-guide.md.

The page must include all five sections in this exact order:

---

SECTION 1 — HERO
Full-width section. Content:
- Main heading: 'Hello, [ClientName].' (text-5xl font-bold tracking-tight)
- Subheading: one-line tagline from CLAUDE.md or credentials file
- Primary CTA button: label relevant to business type (e.g. 'Book a Session', 'Get Started', 'Let's Talk')
- Secondary link below the button: 'See how it works ↓' that smooth-scrolls to Section 3
Background: use the preset's primary color or a clean gradient. Text contrast must pass WCAG AA.

---

SECTION 2 — WHAT YOU GET (Infinite Leverage Agenda)
Section title: 'What You Get'
3-column card grid. Each card: icon (use a relevant emoji or Heroicons SVG), bold benefit headline,
one-sentence description. Research the business type and write real benefit copy — no placeholders.
Example for a coaching business: 'Clarity on your next move', 'A plan that runs without you',
'Content that builds your audience while you sleep'.

---

SECTION 3 — THE 18 PROTOCOLS (How It Works)
Section title: 'The 18 Protocols'
Section subtitle: 'The operating system behind every Infinite Leverage team.'

Render all 18 protocols grouped into exactly 5 tracks. Use the track names, protocol numbers,
and protocol text exactly as listed below — do not paraphrase or abbreviate:

Track 01 — Mindset
  P1:  Humans are the orchestrator. The real intelligence is still you.
  P2:  The CMS is dead. AI is the CMS.
  P3:  The stack: Claude, GitHub, Vercel, Supabase. Master four tools. Ship anything.
  P4:  Agents are folders, not magic. Structure beats novelty.

Track 02 — Infrastructure
  P5:  GitHub — version control for all code and context.
  P6:  Vercel — deploys only via git push. Never vercel deploy directly.
  P7:  Supabase — data, auth, and subscribers.

Track 03 — Building
  P8:  Design system written before any component ever gets built.
  P9:  Concrete step-by-step workflows that turn intent into output.
  P10: Communications go out automatically via scheduled PM runs.
  P11: Skills for admin so humans never have to escalate for small things.

Track 04 — Team and Ops
  P12: DevOps escalates to a human engineer when needed — never guesses on infrastructure.
  P13: 8 fixed agent roles. No improvising new ones.
  P14: PM plans every epic with acceptance criteria before a single line of code.
  P15: PM reads git history before every task — always knows what shipped yesterday.

Track 05 — Continuity
  P16: QA knows exactly what AI can and cannot test — and flags the rest to a human.
  P17: Context handed off via BRIDGE.md and the memory system — no knowledge tax between sessions.
  P18: Work outlives the operator — agents repo + sync-agents means any machine can be set up from GitHub.

Layout: one card per track. Inside each card: track number + track name as the card heading (monospace
label + bold title), followed by a numbered list of protocols. Use the design system's --blue accent
for protocol numbers and track labels. Cards in a 1-column stack on mobile, 2-column grid on md+,
single wide card for Track 01 to give it visual weight as the foundation track.

---

SECTION 4 — CONTACT FORM (unwired mockup, ready for integration)
Section title: 'Get in Touch'
Section subtitle: 'Ready to build your AI team? Let's talk.'

Form fields:
- Name (text input, required)
- Email (email input, required)
- Message (textarea, 4 rows, required)
- Submit button: 'Send Message'

Form state: on submit, show an inline 'Message sent — we'll be in touch soon.' success message.
The form must be built as a Server Action stub:
- Create website/src/app/actions/contact.ts with a `submitContact` Server Action that currently
  only returns { success: true } — add a TODO comment marking where Supabase insert + Resend email go.
- The form component uses useActionState (React 19) to handle pending/success/error states.
- No API route needed yet — the stub is wired to the Server Action, not a fetch call.
- Add data-testid attributes: 'contact-name', 'contact-email', 'contact-message', 'contact-submit',
  'contact-success' — QA will write Playwright tests against these.

---

SECTION 5 — FINAL CTA
Repeat the primary CTA button from Section 1 centered in a full-width dark background section.
Add one trust line below: e.g. 'Trusted by founders across Australia, Vietnam, and the US.' (adapt
to client's geography if known, otherwise use this default).

---

This is the Hello [ClientName] page — the first thing the client sees when the site goes live.
Make it feel real, not placeholder. No lorem ipsum anywhere."

Verify the dev server starts with the personalized page: cd website && npm run dev
Open http://localhost:3000, confirm the client name and branding appear, then Ctrl+C.
```

---

## Prompt 5 — Write credentials to .env.local

```
Write the following to ~/code-projects/{project-slug}/website/.env.local
(replace each placeholder from the credentials file):

NEXT_PUBLIC_SUPABASE_URL={from-credentials-file}
NEXT_PUBLIC_SUPABASE_ANON_KEY={from-credentials-file}
SUPABASE_SERVICE_ROLE_KEY={from-credentials-file}
GEMINI_API_KEY={from-credentials-file}
RESEND_API_KEY={from-credentials-file}
# Lark is optional — only add these if the client collected Lark credentials in Phase 1
# If LARK_WEBHOOK_URL is blank, leave these lines out entirely
LARK_APP_ID={from-credentials-file-or-leave-out}
LARK_APP_SECRET={from-credentials-file-or-leave-out}
LARK_WEBHOOK_URL={from-credentials-file-or-leave-out}

Confirm .env.local is in .gitignore before writing. Do not commit this file.
```

---

## Prompt 6 — Global skills

```
Install three global skills to ~/.claude/skills/:

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
Steps: (1) ask: title, description, priority (2) write to working_files/tasks/{YYYY-MM-DD}-{slug}.md (3) format: # Title / Priority / Created / ## Description / ## Acceptance criteria

Create ~/.claude/skills/skill-creator/SKILL.md:
---
name: skill-creator
description: This skill should be used when the user says "create a skill", "new skill", "build a skill", or "add a skill". Guides creation of a new Claude Code skill folder following official conventions: lean SKILL.md with third-person triggers, progressive disclosure via references/ and scripts/.
---
Steps: (1) ask: skill name, trigger phrases, purpose (2) create skill-name/ directory under ~/.claude/skills/ (3) write SKILL.md with frontmatter name+description and imperative-form body (4) create references/ and scripts/ subdirectories if needed (5) confirm with ls
```

---

## Prompt 7 — Push to GitHub and connect Vercel
> **[Protocol 5]** GitHub is version control for all code and context. **[Protocol 6]** Vercel deploys only via `git push` — never `vercel deploy` directly.

```
Deploy the project:

1. Push to GitHub:
   cd ~/code-projects/{project-slug}
   git init && git checkout -b main
   git add CLAUDE.md .gitignore website/src/ website/public/ website/package.json website/package-lock.json website/tailwind.config.ts website/tsconfig.json website/next.config.ts
   git commit -m "init: {Business Name} — Infinite Leverage site"
   gh repo create {project-slug} --public --source=. --remote=origin --push

2. Tell me the GitHub repo URL — I need to import it to Vercel manually.
   Here are the exact steps:
   a. Go to vercel.com → click "Add New..." → "Project"
   b. Under "Import Git Repository", find {project-slug} and click "Import"
   c. Under "Configure Project", expand "Build and Output Settings"
   d. Find the "Root Directory" field → type: website
      (This tells Vercel your Next.js app is in the website/ folder, not the repo root)
   e. Click "Environment Variables" → add: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY
   f. Click "Deploy" — wait for green checkmark
   Tell me "deployed" when Vercel shows the green success screen.

3. After I confirm the site is deployed:
   a. Link this local directory to the Vercel project:
      vercel link --project {project-slug} --yes

   b. Add env vars via Vercel CLI (source from credentials file):
      vercel env add SUPABASE_SERVICE_ROLE_KEY production
      vercel env add GEMINI_API_KEY production
      vercel env add RESEND_API_KEY production
      # Lark is optional — only run these if LARK credentials were provided in Phase 1
      # vercel env add LARK_APP_ID production
      # vercel env add LARK_APP_SECRET production
      # vercel env add LARK_WEBHOOK_URL production

   c. Verify deployment and show status:
      vercel ls
      vercel inspect https://{project-slug}.vercel.app
      curl -I https://{project-slug}.vercel.app
```

> **Manual step**: Open vercel.com/new → import `{project-slug}` → set **Root Directory = `website/`** → add `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` → Deploy.
>
> All future deployments flow through `git push origin main` → GitHub → Vercel CI/CD. Never run `vercel deploy` or `vercel --prod` directly.

---

## Prompt 8 — Agent team: repo + definitions
> **[Protocol 1]** Agents act when asked — you are the orchestrator. **[Protocol 4]** Agents are folders with explicit context, not opaque magic. **[Protocol 13]** These 8 roles are fixed — don't improvise new ones.

```
⚠️ AGENTS REPO RULE — READ BEFORE DOING ANYTHING IN THIS PROMPT:
There must be exactly ONE agents repo per operator, ever. It is named `{clientslug}-agents`.
Multiple website/web-app projects may exist, but they all share this single agents repo.
Never create a second agents repo. Never create a per-project agents repo.

1. Check whether the agents repo already exists:
   gh repo view {clientslug}/{clientslug}-agents --json name 2>&1

   IF THE REPO ALREADY EXISTS:
   - Clone it locally if not already present: gh repo clone {clientslug}/{clientslug}-agents ~/{clientslug}-agents
   - cd ~/{clientslug}-agents && git checkout main && git pull origin main
   - Skip to step 3 (write agent definitions into the existing repo — do not reinitialise)
   - Do NOT run git init, do NOT run gh repo create

   IF THE REPO DOES NOT EXIST:
   - Proceed with steps 2 through 7 below to create it for the first time

2. Create the repo structure (first time only):
   mkdir -p ~/{clientslug}-agents/.claude/agents
   mkdir -p ~/{clientslug}-agents/agents/{product-manager,developer,qa,devops,writer,designer,web-publisher,email-marketer}/context
   mkdir -p ~/{clientslug}-agents/skills/sync-agents

   Write sync-agents/SKILL.md (triggers: "sync agents", "update agents", "pull latest agents")
   Steps: git pull origin main, cp -r .claude/agents/* ~/.claude/agents/, confirm with ls

3. Verify the source definitions file exists before proceeding:
   ls ~/.claude/skills/infiniteleverage-init/references/mac-mini-agents.md
   If not found, stop and report the missing file path — do not proceed.

   Write the remaining 7 agent definition files to .claude/agents/ using the definitions in
   ~/.claude/skills/infiniteleverage-init/references/mac-mini-agents.md as the base.
   (developer.md was already written in Prompt 4 — do not overwrite it.)

   Agents to write now: product-manager, qa, devops, writer, designer, web-publisher, email-marketer

   Apply the updated rules across all agents:
   - Product Manager: Dan Shipper product thinking, hypothesis-based epics, user story format; auto-approve only high-priority + low-risk items after 2h; backlog everything else; all approval decisions written directly to project-status.html
   - QA: Dan Shipper tight-loop philosophy — QA is part of the development thread, not a gate; drafts QA plan from epic acceptance criteria before writing any test; writes QA-REPORT.md to the task's engineering doc folder; logs pass/fail to project-status.html; notifies Developer immediately after every run
   - Developer: obra/superpowers spec-first + TDD + Karpathy simplicity (already written in Prompt 4); follows engineering docs pattern for every task
   - DevOps: scoped strictly to GitHub CI/CD and Vercel CLI operations — no application code, no content
   - Writer: Neil Patel self-critique (hook, SEO, proof density, scanability, one CTA, cut 20%); validates brief.md has all required fields before writing
   - Designer: reads style-guide.md presets and selects best fit based on blog tone before generating
   - All agents: industry best practices principle (research top GitHub repos before acting)

   Engineering docs rule — embed this in the Developer and QA agent definitions:
   "## Engineering documentation (every task)
   Every task gets its own folder under docs/engineering/changes/:

   docs/engineering/changes/
   └── YYYY-MM/
       ├── YYYY-MM-DD-{task-slug}/
       │   ├── TECH-PLAN.md    ← Developer writes before any code
       │   ├── EXEC-PLAN.md    ← Developer checks off live during work
       │   ├── CHANGELOG.md    ← Developer writes once QA is green
       │   └── QA-REPORT.md    ← QA writes with AC coverage table + test results
       └── YYYY-MM-summary.md  ← one appended row per shipped task

   Developer: create the folder and write TECH-PLAN.md + EXEC-PLAN.md before touching any file.
   Write CHANGELOG.md and append to YYYY-MM-summary.md once QA returns PASS.
   QA: write QA-REPORT.md to the same folder. Never skip this — work is not done until all 4 files exist."

   Universal wave rule — embed this in EVERY agent definition:
   "## QA Round (every wave)
   After completing your primary deliverable in any wave, call @qa with:
   '@qa Review my output from this wave only: [describe what you just built/wrote/changed].
   Check for correctness, edge cases, and quality issues. Return pass/fail with specific findings.'
   Wait for @qa response. If @qa returns FAIL, fix the flagged issues before declaring the wave done.
   If @qa returns PASS, proceed. Never skip the QA round to save time."

3b. Write the domain-setup skill for the Developer agent:
    Path: ~/{clientslug}-agents/agents/developer/context/skills/domain-setup/SKILL.md
    Also install it globally: ~/.claude/skills/domain-setup/SKILL.md (copy same file)

    The SKILL.md content must be:

    ---
    name: domain-setup
    description: This skill should be used when the operator says "set up a new domain", "add a new client domain", "onboard a new operator account", "create operator email", or "connect domain to Google Workspace". Guides the full Google Workspace secondary domain + DNS + Vercel + service account setup for a new operator.
    ---

    # Domain Setup — New Operator Account

    ## Purpose
    Set up a professional operator email under a client's own domain, fully connected to GitHub, Vercel, and Supabase. Uses the infinite-8.com Google Workspace as the master account.

    ## Steps

    ### 1. Add Secondary Domain in Google Workspace
    - Log into the master infinite-8.com Google Workspace Admin Console (Admin → Add a domain → Add as secondary domain)
    - Enter the new operator domain (e.g. `clientname.com`)
    - Google will provide a TXT record for DNS verification — copy it

    ### 2. Add TXT Record in Vercel DNS
    - Go to Vercel → Domains → find the client domain → DNS tab
    - Add the TXT record Google provided
    - Return to Google Admin Console and click Verify

    ### 3. QA Verification — DNS propagation
    After TXT record is added and Google confirms verification:
    Invoke @qa: "Verify DNS setup for {domain}: confirm the Google TXT record resolves via `dig TXT {domain}`,
    confirm MX records are active via `dig MX {domain}`, and confirm the domain shows as verified
    in Google Admin Console. Log pass/fail to docs/project-status.html under Infrastructure → Domain Setup."

    Wait for @qa confirmation before proceeding to Step 4.

    ### 4. Set MX Records via Vercel
    - In Vercel DNS for the domain, use the "Set MX records for Google" option (handles Google Workspace mail routing automatically)
    - No manual MX record entry needed

    ### 5. Create Operator Email
    - In Google Admin Console → Users → Add new user
    - Create: `{firstname}@{clientdomain}.com`
    - Save the temporary password to the credentials file

    ### 6. Set Up Service Accounts
    Using the new operator email, create accounts at:
    - GitHub (github.com/signup) — verify email
    - Vercel (vercel.com/signup) — link to GitHub via OAuth
    - Supabase (supabase.com) — create new organisation

    ### 7. Update project-status.html
    Open docs/project-status.html and add or update the Infrastructure table row for Domain Setup:

    | Section | Field | Value |
    |---------|-------|-------|
    | Infrastructure → Domain Setup | Domain | {clientdomain}.com |
    | | Operator email | {firstname}@{clientdomain}.com |
    | | Services connected | GitHub ✅ / Vercel ✅ / Supabase ✅ |
    | | DNS verified | ✅ TXT + MX confirmed by @qa |
    | | Status | ✅ Complete — {YYYY-MM-DD} |

    If project-status.html does not yet exist, create it with a minimal HTML shell containing an Infrastructure section table.

    ## Edge Cases
    - **Domain already in Google Workspace**: skip step 1, go straight to TXT verification
    - **DNS not propagated within 10 min**: note in project-status.html as ⏳ Pending, continue with other steps, return to verify
    - **Existing SPF record on domain**: add `include:amazonses.com` to the existing record — do not replace it
    - **@qa not available**: log DNS check manually using `dig` in terminal and paste results to project-status.html

4. Write default-persona.md for all 8 agents at agents/{agent}/context/default-persona.md

5. Write email sequence index at agents/email-marketer/context/email-index.md
   Include Stage 0 welcome email template with clear {placeholder} markers

6. Write README.md describing the 8-agent team, install instructions, sync workflow

7. Push repo to GitHub (first time only — skip if repo already existed in step 1):
   cd ~/{clientslug}-agents
   git init && git checkout -b main
   git add .
   git commit -m "init: 8-agent team — Build + GTM"
   gh repo create {clientslug}/{clientslug}-agents --public --source=. --remote=origin --push

   If repo already existed, just commit and push the updated agent definitions:
   cd ~/{clientslug}-agents
   git add .
   git commit -m "update: agent definitions for {project-slug}"
   git push origin main
```

---

## Prompt 9 — Agent team dashboard

```
Generate an HTML file at ~/{clientslug}-agents/team-dashboard.html that gives the client
a beautiful, at-a-glance overview of their AI team. Commit it to the agents repo when done.

The file must be fully self-contained (no external CSS files, no CDN fonts except Google Fonts).

--- DESIGN SYSTEM ---
Font: Inter from Google Fonts (weights 400, 500, 600)
Base font size: 16px. Never go below 14px anywhere on the page.
Line height: 1.6
Color palette:
  --ink: #0B1426        (headings, body text)
  --ink-soft: #1F2A3D   (secondary text)
  --gray-1: #94A3B8     (muted labels)
  --rule: #E2E8F0       (borders, dividers)
  --blue: #2563EB       (accent, links, badges)
  --blue-soft: #DBEAFE  (badge backgrounds, highlights)
  --cream: #F2EDE3      (section backgrounds)
  --paper: #FFFFFF      (card backgrounds)
Background: #F8FAFC (page level)
Cards: white, border-radius 12px, box-shadow 0 1px 3px rgba(0,0,0,0.08)
Spacing: generous padding (24px inside cards, 32px between sections)

--- SECTION 1: AGENT CARDS (one card per agent, 2-column grid) ---
For each of the 8 agents, render a card with:
  • Agent name (large, 20px, 600 weight) + role badge (blue-soft background)
  • Role: one-sentence description of what this agent owns
  • Tasks: bullet list of 3–5 core recurring tasks
  • Inputs: what triggers or feeds this agent (files, human prompts, schedules)
  • Outputs: what it produces (files, messages, PRs, emails)
Use the 8 agent definitions from .claude/agents/ as the source of truth.

--- SECTION 2: WEEKLY CALENDAR ---
Render a 5-column table (Mon–Fri). Each cell shows scheduled agent runs for that day.
Use the schedule from Prompt 10 (RemoteTrigger registrations) as source:
  Mon 9am — Writer
  Tue 9am — Designer
  Wed 9am — Web Publisher
  Thu 10am — Email Marketer
  Fri 5pm — PM: Weekly RAG report
  Weekdays 7am — PM: Daily plan
  Weekdays 6pm — PM: Standup compile
  Weekdays 6:30pm — PM: EOD summary
Style each entry as a small pill: agent name + time, colored by agent type.

--- SECTION 3: CROSS-AGENT FLOW DIAGRAM ---
Render an inline SVG flow diagram (no Mermaid, no external JS) showing how agents hand off
to each other in the content pipeline:
  Writer → Designer → Web Publisher → (live on site)
  PM → orchestrates all agents → reports to Human
  Developer ← PM (epic) → QA (tests) → DevOps (deploy)
  Email Marketer ← PM (schedule)
Keep it clean: rounded rectangles, directional arrows, agent name + icon emoji inside each node.
Use --blue for arrows, --ink for node borders, --blue-soft for node fills.
Nodes must be large enough to read comfortably (min 120×48px).

--- FOOTER ---
Generated date, project name, live URL (https://{project-slug}.vercel.app), agents repo URL.

After generating:
  cd ~/{clientslug}-agents
  git add team-dashboard.html
  git commit -m "docs: add agent team dashboard"
  git push origin main

Open team-dashboard.html in the browser and confirm it renders correctly.
Tell me: "Dashboard ready — open ~/{clientslug}-agents/team-dashboard.html"
```

---

## Prompt 10 — Install agents globally + register schedules

```
1. Install all 8 agents and skills globally:
   cp -r ~/{clientslug}-agents/.claude/agents/* ~/.claude/agents/
   cp -R ~/{clientslug}-agents/.claude/skills/. ~/.claude/skills/
   mkdir -p ~/.claude/scheduled-tasks
   cp -R ~/{clientslug}-agents/.claude/scheduled-tasks/. ~/.claude/scheduled-tasks/
   ls ~/.claude/agents/           # confirm all 8 present
   ls ~/.claude/scheduled-tasks/  # confirm all 8 task folders present

2. Update ~/.claude/CLAUDE.md with agents repo pointer:
   ## Agents repo
   https://github.com/{clientslug}/{clientslug}-agents
   Local: ~/{clientslug}-agents/
   Update: say "sync agents" in Claude Code

3. Register 10 cloud RemoteTrigger routines:
   # [Protocol 10] These run in Anthropic's cloud (CCR) — Mac Mini does not need to be awake.
   # [Protocol 2] Web Publisher is the CMS — no manual page editing after this.
   #
   # IMPORTANT: Load RemoteTrigger schema first: ToolSearch(query: "select:RemoteTrigger")
   # Read the prompt body from ~/.claude/scheduled-tasks/{name}/SKILL.md for each task.
   # Cron expressions are in UTC. Client timezone is Asia/Saigon (UTC+7).
   # environment_id for all routines: env_01Ly7cgFD1z5N2xN9VtNZ42S

   For each task below, call RemoteTrigger(action: "create", body: { name, cron_expression, job_config }):

   devops-daily         → cron_expression: "3 23 * * 0-4"   (weekdays 6:03 AM Asia/Saigon — production health + CI/CD → epic-status.md)
   pm-daily-plan        → cron_expression: "3 0 * * 1-5"    (weekdays 7:03 AM Asia/Saigon — reads epic-status.md, updates project-status.html)
   developer-daily      → cron_expression: "3 2 * * 1-5"    (weekdays 9:03 AM Asia/Saigon — picks up approved items, runs dev-tdd loop)
   pm-standup-compile   → cron_expression: "7 11 * * 1-5"   (weekdays 6:07 PM Asia/Saigon)
   pm-eod-summary       → cron_expression: "37 11 * * 1-5"  (weekdays 6:37 PM Asia/Saigon)
   pm-weekly-rag        → cron_expression: "7 10 * * 5"     (Fridays 5:07 PM Asia/Saigon)
   writer-weekly        → cron_expression: "3 2 * * 1"      (Mondays 9:03 AM Asia/Saigon)
   designer-weekly      → cron_expression: "3 2 * * 2"      (Tuesdays 9:03 AM Asia/Saigon)
   web-publisher-weekly → cron_expression: "3 2 * * 3"      (Wednesdays 9:03 AM Asia/Saigon)
   email-marketer-weekly → cron_expression: "3 3 * * 4"     (Thursdays 10:03 AM Asia/Saigon)

   Save all 10 routine IDs — record them in HANDOFF.md under "Scheduled routine IDs".
   Routines are persistent — no expiry, no re-registration needed. Manage at: https://claude.ai/code/routines

4. Run verification:
   ls ~/.claude/agents/           # all 8 present
   ls ~/.claude/scheduled-tasks/  # all 8 task folders present
   gh repo view {clientslug}-agents
   curl -I https://{project-slug}.vercel.app  # HTTP 200

   Vercel project health check:
   vercel ls                                     # list recent deployments + status
   vercel inspect https://{project-slug}.vercel.app  # deployment details + build info
   vercel env ls production                      # confirm all env vars present

5. Write HANDOFF.md at ~/{clientslug}-agents/HANDOFF.md
   # [Protocol 17] Context handoff — this document is how the client picks up without Dave present
   # [Protocol 18] Work outlives the operator — agents repo + sync-agents means any machine can be set up from GitHub
   Include: all 8 agents with trigger phrases, content pipeline schedule, sync instructions,
   live URL, repo URL, first-actions guide for the client, and all 10 RemoteTrigger routine IDs.
   Manage routines at: https://claude.ai/code/routines
```
