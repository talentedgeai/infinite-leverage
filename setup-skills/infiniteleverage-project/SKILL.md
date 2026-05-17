---
name: infiniteleverage-project
description: This skill should be used when the operator says "new project", "scaffold a project", "create infinite leverage project", "init new project", "start new client project", or "bootstrap project folder". Scaffolds a brand-new project directory from the canonical `templates/project-scaffold/` in `talentedgeai/infiniteleverage-8-agents-template`, substitutes placeholders, wires the 8-agent team into `.claude/`, initializes git, and prints next steps. All operations are inline — no bundled scripts.
version: 2.0.0
---

# Infinite Leverage — New Project Scaffold

## Canonical Source — Read This First

**Every file this skill writes comes from ONE repo:**

> https://github.com/talentedgeai/infiniteleverage-8-agents-template

| What | Canonical path |
|---|---|
| Project folder scaffold + stub files | `templates/project-scaffold/` |
| Folder structure spec | `templates/project-scaffold/FOLDER-STRUCTURE.md` |
| 8 agent definitions | `.claude/agents/*.md` |
| Project skills | `.claude/skills/*/SKILL.md` |
| Engineering rules | `.claude/rules/global-engineering.md` |
| AGENT-DELEGATION block content | embedded below in this SKILL.md — single source for the routing table |

**Rules:**
1. Never modify the scaffold template locally. To change what new projects look like, edit `templates/project-scaffold/` in the canonical repo, commit, push — the next scaffold pulls it automatically.
2. All shell operations are inline in this SKILL.md. **This skill does NOT depend on any external `.sh` files** — every step is something Claude executes directly. That keeps each action visible and auditable.

---

## When to invoke

The operator wants a fresh project folder that follows the canonical Infinite Leverage layout. Run this AFTER `infiniteleverage-init` has set up the machine (agents installed in `~/.claude/agents/`, GitHub + Vercel + Supabase accounts ready).

---

## Inputs to gather

| Input | Example | Required | Notes |
|---|---|---|---|
| Project slug (kebab-case) | `acme-bookstore` | yes | used as folder name AND GitHub repo name |
| Project display name | `Acme Bookstore` | yes | |
| Parent directory | `~/code-projects` | yes (default `~/code-projects`) | |
| First topic date | `2026-05-20` | optional (defaults to today) | |
| First topic slug | `welcome-launch` | optional | |
| Owner name | `Dave Hajdu` | optional | |
| Primary author for content | `Dave Hajdu` | optional | |
| GitHub placement | personal vs org | **interactive** | resolved during Step 11 — never assume |

**Confirm with the operator before running step 1.** Print a dry-run preview:

```
About to scaffold:
  Target          : /Users/.../acme-bookstore
  Project         : Acme Bookstore
  Slug            : acme-bookstore
  First date      : 2026-05-20
  First topic     : welcome-launch
  Next.js         : YES (App Router, TypeScript, Tailwind)        [mandatory]
  GitHub repo     : asked at the end as a tail question           [optional]
Proceed? (y/N)
```

---

## Steps

All commands below are run via the Bash tool. Each step is independent and re-runnable.

### Step 1 — Verify prerequisites

```bash
command -v gh   >/dev/null || { echo "❌ gh CLI required";  exit 1; }
command -v git  >/dev/null || { echo "❌ git required";      exit 1; }
command -v perl >/dev/null || { echo "❌ perl required";     exit 1; }
[ -d "$HOME/.claude/agents" ] || echo "⚠️  Global agents not installed — run infiniteleverage-init first"
```

### Step 2 — Refuse to overwrite an existing project

```bash
TARGET="$HOME/code-projects/<project-slug>"   # substitute real value
[ -e "$TARGET" ] && { echo "❌ $TARGET exists — pick a different slug or remove the directory"; exit 1; }
```

### Step 3 — Fetch the canonical scaffold

> **gh syntax note** — flags for the underlying `git clone` (e.g. `--depth 1`) must come after a `--` separator, otherwise gh interprets them as its own options.

```bash
TMP=$(mktemp -d)
gh repo clone talentedgeai/infiniteleverage-8-agents-template "$TMP/il-template" -- --depth 1
cp -R "$TMP/il-template/templates/project-scaffold/." "$TARGET"
```

### Step 4 — Substitute placeholders (inline)

No external script — Claude runs this perl block directly. Only text files are touched; binaries are skipped by the find filter.

```bash
PROJECT_NAME="Acme Bookstore"
PROJECT_SLUG="acme-bookstore"
FIRST_DATE="2026-05-20"       # YYYY-MM-DD, real first publish date
OWNER="Dave Hajdu"
AUTHOR="Dave Hajdu"

# 4a. Replace branded placeholders everywhere
find "$TARGET" -type f \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.next/*' \
  \( -name '*.md' -o -name '*.html' -o -name '*.json' \
     -o -name '*.txt' -o -name '*.example' -o -name '.gitignore' \
     -o -name '.env*' -o -name 'CLAUDE.md' -o -name 'README.md' \) \
  -exec perl -i -pe "
    s/\Q{Project Name}\E/$PROJECT_NAME/g;
    s/\Q{project-slug}\E/$PROJECT_SLUG/g;
    s/\QPH-author\E/$AUTHOR/g;
    s/\QPH-Author\E/$AUTHOR/g;
  " {} +

# 4b. Replace YYYY-MM-DD ONLY inside folders where it represents a real date
for scope in \
  "$TARGET/content/topics" \
  "$TARGET/standup/briefings" \
  "$TARGET/emails/drafts" \
  "$TARGET/docs/engineering/changes"; do
  [ -d "$scope" ] || continue
  find "$scope" -type f \( -name '*.md' -o -name '*.html' -o -name '*.json' \) \
    -exec perl -i -pe "s/\QYYYY-MM-DD\E/$FIRST_DATE/g" {} +
done
```

**Important — what is NOT renamed automatically:**
`PH-` prefixed *filenames* stay as placeholders. The operator renames them deliberately when starting real work (a real plan, real feature, real research topic). This avoids creating ghost files with auto-generated names.

### Step 5 — Rename the seed topic folder and briefing month

```bash
FIRST_TOPIC_SLUG="welcome-launch"   # operator-supplied

mv "$TARGET/content/topics/YYYY-MM-DD-PH-topic-slug" \
   "$TARGET/content/topics/${FIRST_DATE}-${FIRST_TOPIC_SLUG}"

MONTH=$(printf '%s' "$FIRST_DATE" | cut -c1-7)
mv "$TARGET/standup/briefings/YYYY-MM" "$TARGET/standup/briefings/$MONTH"
mv "$TARGET/standup/briefings/$MONTH/YYYY-MM-DD.md" \
   "$TARGET/standup/briefings/$MONTH/${FIRST_DATE}.md"
```

### Step 6 — Install canonical agents + skills + rules into the project's `.claude/`

```bash
cp "$TMP/il-template/.claude/agents/"*.md "$TARGET/.claude/agents/"
cp -R "$TMP/il-template/.claude/skills/." "$TARGET/.claude/skills/"
cp "$TMP/il-template/.claude/rules/global-engineering.md" "$TARGET/.claude/rules/" 2>/dev/null || true
```

### Step 7 — Inject/refresh the AGENT-DELEGATION block in the project CLAUDE.md (inline)

The scaffold ships with the block already (between `BEGIN: AGENT-DELEGATION` / `END: AGENT-DELEGATION` markers). This step re-applies the canonical content from below so it matches the latest version of this skill. Run it even on a fresh scaffold — it's idempotent.

```bash
TARGET_CLAUDE_MD="$TARGET/CLAUDE.md"

# Canonical block content — single source of truth lives here in the SKILL.md.
BLOCK=$(cat <<'BLOCK_EOF'
<!-- BEGIN: AGENT-DELEGATION (managed by infiniteleverage skills — do not delete this block) -->
## Agent delegation (auto-routing)

When you receive a request, **delegate to the right specialist agent** before doing the work yourself. The 8 agents and their triggers:

| Agent | Delegate when the request involves… |
|---|---|
| **product-manager** | roadmap, vision, epics, daily plan, project-status.html, scope changes, approval triage, stakeholder updates, standup briefings |
| **developer** | writing/changing code, fixing bugs, refactoring, scaffolding pages, API endpoints, Supabase migrations, env-vars wiring |
| **qa** | testing, regression checks, browser matrix, accessibility, QA plans, "verify this works" |
| **devops** | CI/CD, deployments, secret management, infra escalations, Vercel/GitHub workflow issues |
| **designer** | UI mockups, brand application, image prompts, design system updates, visual reviews |
| **writer** | blog drafts, social copy, SEO briefs, voice/tone, content briefs |
| **web-publisher** | publishing markdown → Next.js components, updating `website/pages/blog/index.jsx`, image optimization, the publish workflow |
| **email-marketer** | email drafts, sequences, broadcast campaigns, Brevo/Resend, CRM segmentation |

**Delegation rules:**
1. Pick exactly **one** agent per turn — don't run two in parallel unless the operator explicitly says so.
2. If a request spans agents (e.g., "write a blog *and* publish it"), call them **in sequence**: writer → designer → web-publisher.
3. If unclear which agent fits, **ask the operator** before assuming.
4. Cross-cutting engineering rules live in `.claude/rules/global-engineering.md` — every agent honors them.
5. Project-level persona overrides for each agent live in `agents/<name>/context/persona.md` — read these on first invocation.
6. Trigger phrases: `@product-manager`, `@developer`, etc. — but auto-route even without the `@` when intent is clear.
<!-- END: AGENT-DELEGATION -->
BLOCK_EOF
)

if grep -q 'BEGIN: AGENT-DELEGATION' "$TARGET_CLAUDE_MD"; then
  BLOCK_FILE=$(mktemp); printf '%s\n' "$BLOCK" > "$BLOCK_FILE"
  BLOCK_FILE="$BLOCK_FILE" perl -i -0pe '
    BEGIN { local $/; open($f, "<", $ENV{BLOCK_FILE}); $b = <$f>; chomp $b; }
    s{<!-- BEGIN: AGENT-DELEGATION.*?<!-- END: AGENT-DELEGATION -->}{$b}s;
  ' "$TARGET_CLAUDE_MD"
  rm -f "$BLOCK_FILE"
else
  printf '\n%s\n' "$BLOCK" >> "$TARGET_CLAUDE_MD"
fi
```

### Step 8 — Clean up the temp clone

```bash
rm -rf "$TMP"
```

### Step 8.5 — Initialize spec-kit

spec-kit is the Spec-Driven Development layer used by the PM and developer agents. Initialize it at the project root:

```bash
cd "$TARGET"
# Try spec-kit CLI first; fall back to manual folder creation if not available
npx -y specify-cli init . --here 2>/dev/null || \
  mkdir -p .specify/features .specify/memory .specify/templates \
           .specify/extensions/git/scripts/bash
```

Then write the git extension config (all auto-commits disabled by default per global-engineering.md):

```bash
mkdir -p "$TARGET/.specify/extensions/git"
cat > "$TARGET/.specify/extensions/git/git-config.yml" <<'EOF'
# spec-kit git extension config
# All auto-commits are DISABLED by default.
# This respects global-engineering.md: never commit without explicit instruction.
# To enable auto-commit for a specific command, set enabled: true for that event.
auto_commit:
  default: false
  after_specify:
    enabled: false
    message: "[spec-kit] Add specification"
  after_plan:
    enabled: false
    message: "[spec-kit] Add implementation plan"
  after_tasks:
    enabled: false
    message: "[spec-kit] Add task list"
EOF
```

### Step 9 — Scaffold Next.js into `website/` (mandatory)

This always runs — every Infinite Leverage project ships a Next.js app at `website/`.

**Important:** the canonical scaffold ships a stub `website/README.md` that documents what `create-next-app` will produce. `create-next-app` refuses to install into a non-empty directory, so delete the stub README first (keep the `website/` folder itself) — `create-next-app` will then populate it and write its own README.

```bash
cd "$TARGET"
rm -f "$TARGET/website/README.md"   # remove stub README so create-next-app sees an empty dir
npx create-next-app@latest website \
  --typescript --tailwind --app --eslint \
  --src-dir --import-alias "@/*" --yes
```

If the operator wants the legacy Pages Router instead (some older projects do), substitute `--no-app` for `--app`. Default is App Router per the canonical stack.

### Step 10 — Initialize git + first commit

```bash
cd "$TARGET"
git init -b main
git add .
git commit -m "init: scaffold $PROJECT_NAME (template + Next.js website/)"
```

### Step 11 — Print local-only summary

At this point the project is fully scaffolded **locally** — Next.js is in place, git is initialized, the first commit exists. Show the operator:

```
✅ Project scaffolded at $TARGET
✅ Next.js installed at $TARGET/website
✅ Git initialized, first commit made (local only — no remote yet)

Next steps locally:
1. cd $TARGET
2. cp .env.example .env.local and fill in real keys
3. cd website && npm run dev   # verify the app starts
4. Open the repo in Claude Code
5. Invoke @product-manager — runs pm-client-interview, fills docs/product/product.md
6. Invoke pm-epic-writing for each feature idea — creates epics.md, epic-status.md, .specify/ specs
7. Rename PH- placeholders deliberately as you start real work
8. Read FOLDER-STRUCTURE.md once — canonical layout spec
```

### Step 12 — Tail-end question: push to GitHub now? (interactive, optional)

Ask the operator — this is the LAST thing the skill does and it is fully optional:

> Do you want to create a GitHub repo for this project and push the initial commit now?
> (You can always do this later with `gh repo create` from inside `$TARGET`.)
>
> y / N

**If the operator answers "n":** stop here. Print:
```
Skipped GitHub push. To do it later:
  cd $TARGET
  gh repo create <owner>/$PROJECT_SLUG --private --source=. --remote=origin --push
```

**If the operator answers "y":** continue with the org-placement sub-flow below.

#### 12a — Detect GitHub orgs

```bash
gh auth status >/dev/null 2>&1 || { echo "❌ Not authenticated to GitHub — run: gh auth login"; exit 1; }
ORGS=$(gh api user/orgs --jq '.[].login' 2>/dev/null || echo "")
GH_USER=$(gh api user --jq '.login')
```

#### 12b — Ask where the repo should live

Ask one of these depending on what `ORGS` returned:

**Case A — operator has one or more orgs:**
> Your GitHub account has access to these organizations:
> 1. `<org-1>`
> 2. `<org-2>`
> 3. Use your personal account (`<gh-user>`)
>
> Where should `<project-slug>` live? (1/2/3, or type a different org name)

**Case B — operator has no orgs:**
> Your GitHub account doesn't belong to any organizations.
> 1. Create a new org now (recommended for client work — keeps client work separate from your personal account)
> 2. Use your personal account (`<gh-user>`)
>
> Which? (1/2)
>
> If "1": ask for the org name. github.com orgs cannot be created via API — direct the operator to https://github.com/account/organizations/new and confirm when done before continuing.

**Case C — operator types a custom org name not listed:**
> Will `<org-name>` accept the repo? (y/N)
> If no, return to Case A.

Set `GH_OWNER` to the resolved owner (org login or `$GH_USER`).

#### 12c — Create the repo and push

```bash
gh repo create "$GH_OWNER/$PROJECT_SLUG" \
  --private \
  --source="$TARGET" \
  --remote=origin \
  --push \
  --description "$PROJECT_NAME — Infinite Leverage project"
```

If creation fails because the repo already exists, ask: "Use the existing repo and push to it, or pick a different slug?" Do NOT silently overwrite.

#### 12d — Print remote URL

```
✅ Pushed to https://github.com/$GH_OWNER/$PROJECT_SLUG (private)

To wire up auto-deploys on Vercel:
  cd $TARGET && vercel link
```

---

## What this skill does NOT do

- Configure Supabase / Vercel / Resend / Brevo — those are done in `infiniteleverage-init` Phase 2
- Link the repo to Vercel for auto-deploy — printed as a next-step for the operator (`vercel link`)
- Generate any content — that's the writer agent
- Write product.md / epics.md content — that's `pm-documentation` via the PM agent
- Skip Next.js scaffolding — that step is mandatory
- Push to GitHub silently — the GitHub repo creation+push is asked as a tail-end question and skipped if the operator declines. The skill prints the exact command they can run later.

## Why no .sh files

Earlier versions of this skill shipped a `scripts/substitute-placeholders.sh` and a `scripts/inject-agent-delegation.sh`. They were removed because:
- Skills are instructions for Claude; Claude already has the Bash tool — wrapping shell commands in a script adds a layer that can drift out of sync with `SKILL.md`
- Every step is now visible inline — the operator can read exactly what will run before confirming
- No "file not found" failure mode when the skill is invoked from a context that didn't bundle the script

All routing-table content for the AGENT-DELEGATION block lives in **Step 7 of this SKILL.md** — that is now the single source of truth.

## References

- `templates/project-scaffold/FOLDER-STRUCTURE.md` — the canonical layout this skill produces
- `infiniteleverage-init/SKILL.md` — machine setup prerequisite
- `infiniteleverage-patch/SKILL.md` — keep an existing project's agents in sync after scaffolding
- `references/quick-prompts.md` — operator invocation patterns and failure-mode table
