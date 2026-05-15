---
name: infiniteleverage-project
description: This skill should be used when the operator says "new project", "scaffold a project", "create infinite leverage project", "init new project", "start new client project", or "bootstrap project folder". Scaffolds a brand-new project directory from the canonical `templates/project-scaffold/` in `talentedgeai/infiniteleverage-8-agents-template`, substitutes placeholders ({Project Name}, {project-slug}, YYYY-MM-DD, PH-), wires the 8-agent team into `.claude/`, initializes git, and prints next steps.
version: 1.0.0
---

# Infinite Leverage — New Project Scaffold

## When to invoke

The operator wants a fresh project folder that follows the canonical Infinite Leverage layout. Run this AFTER `infiniteleverage-init` has set up the machine (agents installed in `~/.claude/agents/`, GitHub + Vercel + Supabase accounts ready).

---

## Inputs to gather

Before scaffolding, ask the operator for:

| Input | Example | Required |
|---|---|---|
| Project slug (kebab-case, used as folder name + repo name) | `acme-bookstore` | yes |
| Project display name | `Acme Bookstore` | yes |
| Parent directory | `~/code-projects` | yes (default `~/code-projects`) |
| First topic date | `2026-05-20` | optional (defaults to today) |
| First topic slug | `welcome-launch` | optional |
| Owner name | `Dave Hajdu` | optional |
| Primary author for content | `Dave Hajdu` | optional |

Confirm with the operator before continuing.

---

## Steps

### 1. Verify prerequisites

```bash
command -v gh >/dev/null || { echo "gh CLI required"; exit 1; }
command -v git >/dev/null || { echo "git required"; exit 1; }
test -d "$HOME/.claude/agents" || echo "⚠ Global agents not installed — run infiniteleverage-init first"
```

### 2. Refuse to overwrite an existing project

```bash
TARGET="$PARENT_DIR/$PROJECT_SLUG"
if [ -e "$TARGET" ]; then
  echo "❌ $TARGET already exists. Aborting — pick a different slug or remove the directory."
  exit 1
fi
```

### 3. Fetch the canonical scaffold

```bash
TMP=$(mktemp -d)
gh repo clone talentedgeai/infiniteleverage-8-agents-template "$TMP/il-template" --depth 1
cp -r "$TMP/il-template/templates/project-scaffold" "$TARGET"
rm -rf "$TMP"
```

### 4. Substitute placeholders

Run `scripts/substitute-placeholders.sh "$TARGET" "$PROJECT_NAME" "$PROJECT_SLUG" "$FIRST_DATE" "$OWNER" "$AUTHOR"` (bundled with this skill). It replaces in every text file:

- `{Project Name}` → real display name
- `{project-slug}` → real slug
- `YYYY-MM-DD` → first topic date (only inside `content/topics/`, `standup/briefings/`, `emails/drafts/`, `docs/engineering/changes/`)
- `PH-author` → owner / author name (where contextually unambiguous)

The script does NOT rename `PH-` filenames automatically — those stay as placeholders so the operator renames them deliberately on first use (a topic, a feature, etc.).

### 5. Rename the seed topic folder + briefing

```bash
mv "$TARGET/content/topics/YYYY-MM-DD-PH-topic-slug" \
   "$TARGET/content/topics/$FIRST_DATE-$FIRST_TOPIC_SLUG"

MONTH=$(echo "$FIRST_DATE" | cut -c1-7)
mv "$TARGET/standup/briefings/YYYY-MM" "$TARGET/standup/briefings/$MONTH"
mv "$TARGET/standup/briefings/$MONTH/YYYY-MM-DD.md" \
   "$TARGET/standup/briefings/$MONTH/$FIRST_DATE.md"
```

### 6. Install agents into project `.claude/agents/`

```bash
# Pull canonical agent definitions into the project (not just symlink globals)
# so the project carries its own copy that can drift intentionally.
gh repo clone talentedgeai/infiniteleverage-8-agents-template "$TMP/il-agents" --depth 1
cp "$TMP/il-agents/.claude/agents/"*.md "$TARGET/.claude/agents/"
cp -r "$TMP/il-agents/.claude/skills/"* "$TARGET/.claude/skills/" 2>/dev/null || true
cp "$TMP/il-agents/.claude/rules/global-engineering.md" "$TARGET/.claude/rules/" 2>/dev/null || true
rm -rf "$TMP/il-agents"
```

### 7. Initialize git + first commit

```bash
cd "$TARGET"
git init -b main
git add .
git commit -m "init: scaffold $PROJECT_NAME from infiniteleverage-project template"
```

### 8. Offer to scaffold Next.js + create GitHub repo

Ask the operator:

> Scaffold the Next.js app into `website/` now? (Y/n)
> Create the GitHub repo `<github-org>/<project-slug>` and push? (Y/n)

If yes to Next.js:

```bash
cd "$TARGET"
npx create-next-app@latest website --typescript --tailwind --app --eslint --src-dir --import-alias "@/*" --yes
git add website
git commit -m "feat(website): scaffold Next.js app"
```

If yes to GitHub:

```bash
gh repo create "$GH_ORG/$PROJECT_SLUG" --private --source=. --remote=origin --push
```

### 9. Print next steps

Tell the operator:

```
✅ Project scaffolded at $TARGET

Next steps:
1. cd $TARGET
2. Open in Claude Code
3. Invoke the product-manager agent — it will run pm-client-interview and
   populate docs/product/{product,epics,epic-status,01-product-timeline}.md
4. Replace remaining PH- placeholders in:
   - docs/architecture/plans/PH-plan-name.md
   - docs/features/PH-feature-slug/
   - context/source-material/PH-research-topic/
5. Read FOLDER-STRUCTURE.md once — it's the canonical layout spec
6. cp .env.example .env.local and fill in real keys
```

---

## What this skill does NOT do

- Configure Supabase / Vercel / Resend / Brevo — those are done in `infiniteleverage-init` Phase 2
- Generate any actual content — that's the writer agent's job
- Write product.md / epics.md content — that's `pm-documentation` via the PM agent
- Push to GitHub unless the operator explicitly approves

## References

- `templates/project-scaffold/FOLDER-STRUCTURE.md` — the canonical layout this skill produces
- `infiniteleverage-init/SKILL.md` — machine setup prerequisite
- `infiniteleverage-patch/SKILL.md` — keep an existing project's agents in sync after scaffolding

## Safety

- Refuses to overwrite an existing target directory
- Does not touch any directory outside `$PARENT_DIR/$PROJECT_SLUG`
- Does not push to GitHub without explicit confirmation
- Does not run destructive git operations
