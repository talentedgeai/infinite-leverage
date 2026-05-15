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

| Input | Example | Required |
|---|---|---|
| Project slug (kebab-case, used as folder name + repo name) | `acme-bookstore` | yes |
| Project display name | `Acme Bookstore` | yes |
| Parent directory | `~/code-projects` | yes (default `~/code-projects`) |
| First topic date | `2026-05-20` | optional (defaults to today) |
| First topic slug | `welcome-launch` | optional |
| Owner name | `Dave Hajdu` | optional |
| Primary author for content | `Dave Hajdu` | optional |

**Confirm with the operator before running step 1.** Print a dry-run preview showing target dir, project name, slug, first date, and whether Next.js + GitHub repo will be created.

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

### Step 9 — Initialize git + first commit

```bash
cd "$TARGET"
git init -b main
git add .
git commit -m "init: scaffold $PROJECT_NAME from infiniteleverage-project template"
```

### Step 10 — Offer to scaffold Next.js + create GitHub repo

Ask the operator (each gated on explicit "y"):

> Scaffold the Next.js app into `website/` now? (y/N)

```bash
cd "$TARGET"
npx create-next-app@latest website --typescript --tailwind --app --eslint --src-dir --import-alias "@/*" --yes
git add website && git commit -m "feat(website): scaffold Next.js app"
```

> Create the GitHub repo `<github-org>/<project-slug>` and push? (y/N)

```bash
gh repo create "<github-org>/$PROJECT_SLUG" --private --source=. --remote=origin --push
```

### Step 11 — Print next steps

```
✅ Project scaffolded at $TARGET

Next:
1. cd $TARGET
2. Open in Claude Code
3. Invoke @product-manager — runs pm-client-interview, fills docs/product/{product,epics,epic-status,01-product-timeline}.md
4. Rename remaining PH- placeholders deliberately as you start real work:
   - docs/architecture/plans/PH-plan-name.md
   - docs/features/PH-feature-slug/
   - context/source-material/PH-research-topic/
5. Read FOLDER-STRUCTURE.md once — it's the canonical layout spec
6. cp .env.example .env.local and fill in real keys
```

---

## What this skill does NOT do

- Configure Supabase / Vercel / Resend / Brevo — those are done in `infiniteleverage-init` Phase 2
- Generate any content — that's the writer agent
- Write product.md / epics.md content — that's `pm-documentation` via the PM agent
- Push to GitHub without explicit confirmation

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
