---
name: infiniteleverage-project
description: This skill should be used when the operator says "new project", "scaffold a project", "create infinite leverage project", "init new project", "start new client project", or "bootstrap project folder". Scaffolds a brand-new project directory from the canonical `templates/project-scaffold/` in `talentedgeai/infiniteleverage-8-agents-template`, substitutes placeholders, wires the 8-agent team into `.claude/`, seeds `docs/product/` (product.md, epics.md, epic-status.md) from any rich description the operator provides, seeds `docs/brand/` styling from a chosen or random getdesign.md reference, initializes git, and prints next steps. All operations are inline — no bundled scripts.
version: 2.3.0
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
| Planning / product attachments | PRD, brief, vision doc, transcripts, epic list, **or a rich inline description of the product** | optional | anything the operator pasted or attached in the chat invoking this skill. Used by Step 8.6 to populate `docs/product/`. |
| Desired styling / design reference | "make it like Linear", brand colors + fonts, an existing style guide, or nothing | optional | Used by Step 8.7 to fill `docs/brand/`. If absent, Step 8.7 pulls a random DESIGN.md from getdesign.md. |

### Detecting planning attachments & styling

Before running, scan the invoking message for two kinds of material:

**Product/planning material** → drives Step 8.6. Treat any of these as planning input:
- Files dragged into the chat or referenced by path (`.md`, `.pdf`, `.docx`, `.txt`)
- **A rich inline description** of the product — audience, problem, mechanism, success metrics, non-goals, epics, features, roadmap, or acceptance criteria. A few descriptive paragraphs counts; you do not need a formal PRD.
- Links to Notion / Google Docs / Lark docs the operator wants Claude to read first

If present, hold it in working memory and apply it in **Step 8.6** to fill `docs/product/*.md` accurately to our convention, instead of leaving empty placeholders. If absent, Step 8.6 is a no-op and the PM agent fills the files later via `pm-client-interview` / `pm-epic-writing`.

**Styling material** → drives Step 8.7. Treat any of these as a styling preference:
- A reference brand/site ("like Stripe / Linear / Vercel"), an explicit palette/fonts, a mood ("clean editorial", "playful", "brutalist"), or an attached style guide.

If present, apply it in Step 8.7. **If absent, Step 8.7 picks a random DESIGN.md from https://getdesign.md/** and seeds the brand files from it — so a project is never left style-less.

**Confirm with the operator before running step 1.** Print a dry-run preview:

```
About to scaffold:
  Target          : /Users/.../acme-bookstore
  Project         : Acme Bookstore
  Slug            : acme-bookstore
  First date      : 2026-05-20
  First topic     : welcome-launch
  Next.js         : YES (App Router, TypeScript, Tailwind)        [mandatory]
  Planning docs   : <N attachments / rich description detected> → will seed docs/product/   [auto, optional]
  Styling         : <"like Linear" | none → random from getdesign.md> → will seed docs/brand/   [auto]
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

### Step 8.6 — Populate `docs/product/` from operator-supplied planning docs (conditional)

**Run this step ONLY if planning attachments were detected at invocation time.** Otherwise skip — leave the placeholder files as-is for the PM agent to fill later.

This step transforms whatever the operator handed over (PRD, brief, vision doc, raw transcript, bullet list of features) into the three canonical files. Claude does the synthesis directly — no external scripts.

#### Inputs

Collect every planning attachment into a single working context. Acceptable sources:
- Inline text pasted into the invoking message
- Local file paths the operator referenced (read with the Read tool)
- Multiple attachments — merge them; if they conflict, prefer the most recent / most specific one and flag the conflict in the file as an open question

#### 8.6a — Write `docs/product/product.md`

Replace the placeholder template at `$TARGET/docs/product/product.md` with content extracted from the attachments. Honor the canonical heading structure exactly — the `pm-documentation` skill enforces this format:

```markdown
# Product Vision — <Project Name>

> Synthesized from operator-supplied planning docs on <FIRST_DATE>. Owned by the PM agent — re-run `pm-client-interview` to refine.

## Problem
<Who hurts, how badly, why now — pulled from the attachments. If the attachment doesn't say, write "OPEN QUESTION: …" instead of guessing.>

## Audience
<Who we serve.>

## Mechanism
<How we solve it.>

## Success
<Measurable outcomes / KPIs the attachments call out.>

## Non-goals
<Anything the operator explicitly excluded.>

## Source material
- <list every attachment used, with a one-line summary each>
```

Rules:
- Never invent facts. If the attachments don't cover a section, write `OPEN QUESTION: <specific question>` so the PM agent picks it up in the next session.
- Keep the five canonical H2s (`Problem`, `Audience`, `Mechanism`, `Success`, `Non-goals`) — adding new ones breaks the PM skill's parser.
- Preserve the `# Product Vision — <Project Name>` H1 exactly (with `$PROJECT_NAME` substituted).

#### 8.6b — Write `docs/product/epics.md` (strict Dan Shipper format)

If the attachments list features / epics / bundles, write them into `$TARGET/docs/product/epics.md` using the **exact** format enforced by `pm-epic-writing`. No deviations — `pm-grill-with-docs` and `pm-analyze-split` parse this file by structure and will reject non-conforming entries.

**Header + opening block** (write once, at the top of the file):

```markdown
# Epics — <Project Name>

> Seeded from operator-supplied planning docs on <FIRST_DATE>. Owned by `pm-epic-writing`. Each epic must eventually have a matching spec at `.specify/features/<slug>/spec.md`.

These are thematic bundles of work. Each epic makes a bet on user behavior — a specific problem that, if solved, unlocks a meaningful outcome. Epics are not a sprint backlog.
```

**Epic entry format** (strict — one H2 per epic, numbered sequentially `E1`, `E2`, `E3`…):

```markdown
## E<N> · <Epic Name>

**The problem:** <One sentence: the specific user frustration or gap this epic addresses>
**The mechanism:** <One sentence: the causal chain — how solving this produces the outcome>
**What it bundles:**
- <Feature or component 1>
- <Feature or component 2>
**What success looks like:** <Specific, measurable — number + date or behaviour threshold>
**Why it goes first:** <One sentence: dependency, risk reduction, or fastest learning>

_Spec: `.specify/features/<slug>/spec.md`_
```

**Sequence argument** (append after the last epic — one short paragraph):

```markdown
## Sequence argument

<Why this ordering and not another. Reference dependencies, risk reduction, or learning velocity. If the attachments don't justify the order, write "OPEN QUESTION: confirm sequence with operator before development starts.">
```

**Hard rules — match `pm-epic-writing` exactly:**

1. **One bet per epic.** If an attachment lumps two user problems together, split them into separate epics.
2. **No horizontal slicing.** Epics are user-outcome bundles, never tech layers ("Build the API", "Build the UI" → ❌).
3. **Success must be measurable.** "Improve performance" is not valid. "Reduce task completion time from 5 min to 90 s for 80% of users by Q3" is. If the attachment is vague, write `OPEN QUESTION: define measurable success criterion` — don't invent numbers.
4. **Never include** these fields — they belong in `.specify/features/<slug>/spec.md`, not in the epic entry:
   - `Thesis`, `Hypothesis`, `Acceptance criteria`, `Definition of done`, `Priority signal`, timeline dates
5. **Heading exactly `## E<N> · <Epic Name>`** — the `E<N> · ` prefix is what the parser keys on. Don't change the separator (`·` is U+00B7 middle dot, not a hyphen).
6. **Sequence argument is required** whenever there are ≥2 epics.
7. **Epic numbering is sequential** starting at `E1`. If a later `pm-epic-writing` run reads this file, it continues from the next integer.

If the attachments don't contain anything epic-shaped (no discrete user problems, just vision narrative), leave the placeholder comment intact — don't fabricate epics.

#### 8.6c — Write `docs/product/epic-status.md` (strict Dan Shipper format)

For every epic written in 8.6b, create `$TARGET/docs/product/epic-status.md` using the canonical pipeline-stage tracker that `pm-epic-writing` Step 7 builds. Use this exact structure:

```markdown
# <Project Name> · Epic Status · Last updated: <FIRST_DATE> · Phase in flight: Phase 1

## Pipeline stages

| Stage | Gate question |
|-------|---------------|
| 1 · Specified | Is there a written spec with acceptance criteria? |
| 2 · In flight | Is active development underway? |
| 3 · Feature-complete | Does it meet every acceptance criterion? |
| 4 · Tested | Have all tests passed? |
| 5 · Shipped | Is it deployed and measurably impacting users? |

Status glyphs: 🔄 in flight · ✅ done · ⏳ partially done · ☐ planned · 🛑 paused

## At a glance

| Epic | Status | % done (est) | Pipeline | Open bugs | Closed bugs | Notes |
|------|--------|--------------|----------|-----------|-------------|-------|
| E1 · <Epic Name> | ☐ planned | 0% | ○○○○○ | 0 | 0 | Seeded from planning doc |
| E2 · <Epic Name> | ☐ planned | 0% | ○○○○○ | 0 | 0 | Seeded from planning doc |

## Drilldown

## Obsolete / won't fix
```

**Hard rules:**

- Pipeline column uses 5 circles, one per stage. `○` = not reached, `●` = reached. Seeded epics start `○○○○○`.
- Status glyph for all seeded epics is `☐ planned` until `pm-epic-writing` produces a real spec.
- `% done (est)` starts at `0%`.
- Both `## Drilldown` and `## Obsolete / won't fix` sections are required even when empty — `pm-project-status` keys on these headings.
- Epic identifier in the table (`E1 · <Name>`) must match the H2 in `epics.md` byte-for-byte.

If no epics were written in 8.6b, leave `epic-status.md` as the empty placeholder.

#### 8.6d — Stash the raw source material

Save the original attachments verbatim under `$TARGET/docs/product/sources/` so the PM agent can re-derive context later without re-asking the operator:

```bash
mkdir -p "$TARGET/docs/product/sources"
# For each attachment, copy or write the raw content into:
#   $TARGET/docs/product/sources/<FIRST_DATE>-<slug>.<ext>
# Use a kebab-case slug derived from the attachment title or filename.
```

Inline pastes get a single file: `$TARGET/docs/product/sources/<FIRST_DATE>-operator-brief.md` with a one-line frontmatter recording where it came from.

#### 8.6e — Print what was populated

Tell the operator exactly which sections were filled vs. which became open questions, so they can decide whether to run `pm-client-interview` immediately or trust the auto-fill:

```
✅ docs/product/product.md       — <N>/5 sections filled, <M> open questions
✅ docs/product/epics.md         — <K> epics seeded
✅ docs/product/epic-status.md   — <K> rows added
✅ docs/product/sources/         — <N> source files stashed
```

If Step 8.6 was skipped (no attachments), print:
```
ℹ️  No planning attachments detected — docs/product/ left as placeholders. Invoke @product-manager → pm-client-interview to fill them.
```

### Step 8.7 — Collect styling and seed `docs/brand/` (always runs)

Every project gets a design direction before any UI is built — the designer, writer, and web-publisher agents all read `docs/brand/style-guide.md`. This step fills it from the operator's preference, or, if none was given, from a **random DESIGN.md on [getdesign.md](https://getdesign.md/)** (a collection of design-system analyses of well-known sites, made to drop into a project as a coding-agent design reference).

#### 8.7a — Determine the design source

| Situation | Action |
|---|---|
| Operator gave explicit styling (palette, fonts, mood, or an attached style guide) | Use it directly — skip getdesign.md. |
| Operator named a reference brand ("like Stripe / Linear / Vercel") | Fetch that entry: `https://getdesign.md/<brand>/design-md`. |
| **No styling provided** | **Pick a random entry from getdesign.md** (see 8.7b). |

#### 8.7b — Pull a DESIGN.md from getdesign.md (when no explicit styling)

getdesign.md is a client-rendered app; entries live at `https://getdesign.md/<brand>/design-md`. Fetch the chosen entry's rendered content using the **Claude in Chrome extension (MCP)** or **WebFetch / computer-use** (a plain `curl` returns an empty SPA shell — use a real renderer).

To pick at random, choose one slug from the collection. A non-exhaustive list (browse `https://getdesign.md/` for the full set): `vercel`, `linear`, `stripe`, `resend`, `figma`, `framer`, `cursor`, `superhuman`, `cohere`, `clickhouse`, `sanity`, `lovable`, `cal`, `composio`, `discord`, `elevenlabs`, `airbnb`, `airtable`, `coinbase`, `claude`. Vary the choice per project (e.g. seed off the project slug) so different projects get different looks.

```
Using the Claude in Chrome extension / WebFetch, open https://getdesign.md/<chosen-brand>/design-md
and read the full DESIGN.md analysis (palette, typography, spacing, mood, component patterns).
```

Drop the raw reference into the project verbatim so the coding agents can consult it:

```bash
mkdir -p "$TARGET/docs/brand"
# Write the fetched DESIGN.md content to:
#   $TARGET/docs/brand/DESIGN.md
# Prepend one line of frontmatter noting the source URL and that it was an auto-pick.
```

> **Fallback — getdesign.md unreachable or rendering fails:** do NOT block the scaffold. Fall back to the built-in default (clean editorial: Inter, near-black ink `#0B1426` on `#F8FAFC`, single blue accent `#2563EB`, generous spacing) and note in the file that it's a fallback the operator can replace later.

#### 8.7c — Synthesize `docs/brand/style-guide.md`

Translate the chosen source (operator preference OR the fetched DESIGN.md) into the canonical brand file at `$TARGET/docs/brand/style-guide.md`, filling the existing template sections — **Color palette** (real hex values), **Typography** (heading/body/mono fonts + line-height), and **Visual style** (mood, image style, reference aesthetics). Substitute `{Project Name}` with `$PROJECT_NAME`. Leave **Voice and tone** / **Vocabulary** / **Content formats** for the PM/writer interview unless the planning docs from Step 8.6 already specify them — in which case fill them too.

Rules:
- Use **concrete values**, not placeholders — real hex codes and named Google Fonts the designer can use immediately.
- Keep the template's H2 headings intact (the designer/writer agents key on them).
- Never invent a brand voice the operator didn't express — that's `Visual style` only here; voice stays an open question for the PM interview.

#### 8.7d — Print what was applied

```
✅ docs/brand/style-guide.md — palette + typography + visual style filled
✅ docs/brand/DESIGN.md       — reference: <source>  (e.g. "getdesign.md/linear — random auto-pick" | "operator: like Stripe" | "built-in fallback")
   Voice/tone left for the PM interview (pm-client-interview) unless planning docs specified it.
```

### Step 9 — Scaffold Next.js into `website/` (mandatory)

This always runs — every Infinite Leverage project ships a Next.js app at `website/`.

**Important:** the canonical scaffold ships a starter kit inside `website/` (chat, billing, notifications, markdown rendering, Supabase migrations, vitest tests) with **no `package.json`** — it is designed to sit on top of a fresh `create-next-app` install. `create-next-app` refuses to install into a non-empty directory, so scaffold Next.js in a temp directory and merge it **underneath** the starter files. The starter uses a root-level `app/` layout, so create-next-app must run with `--no-src-dir`.

```bash
# 9a. Scaffold Next.js in a temp dir (root-level app/, matching the starter kit)
NEXT_TMP=$(mktemp -d)
npx create-next-app@latest "$NEXT_TMP/nextapp" \
  --typescript --tailwind --app --eslint \
  --no-src-dir --import-alias "@/*" --yes
rm -rf "$NEXT_TMP/nextapp/.git" "$NEXT_TMP/nextapp/node_modules"

# 9b. Merge: create-next-app files fill in gaps; starter-kit files always win
rsync -a --ignore-existing "$NEXT_TMP/nextapp/" "$TARGET/website/"
rm -rf "$NEXT_TMP"

# 9c. Install the dependencies the starter kit imports
cd "$TARGET/website"
npm install @ai-sdk/react @mdxeditor/editor @supabase/ssr @supabase/supabase-js \
  @tanstack/react-form @tanstack/react-query @uiw/react-md-editor ai date-fns \
  lucide-react react-markdown rehype-external-links rehype-highlight rehype-slug \
  remark-gfm stripe zustand
npm install -D vitest @vitejs/plugin-react @testing-library/react \
  @testing-library/user-event @testing-library/jest-dom jsdom
```

**9d. Wire the React Query provider into the root layout.** The starter ships `app/providers.tsx` (QueryClientProvider); `app/layout.tsx` comes from create-next-app and must be edited to use it — the chat and notifications features fail to prerender otherwise:

```tsx
// app/layout.tsx — add:
import { Providers } from "./providers";
// ...and wrap the body children:
<body>
  <Providers>{children}</Providers>
</body>
```

**9e. Verify before committing** — both must pass:

```bash
cd "$TARGET/website" && npm run build && npx vitest run
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
2. Write website/.env.local with the core Supabase keys (collect-credentials.py --target website/.env.local --check core)
3. cd website && npm run dev   # verify the app starts
4. Open the repo in Claude Code
5. Invoke @product-manager — if docs/product/ was seeded by Step 8.6, run pm-grill-with-docs to validate; otherwise run pm-client-interview to fill product.md
6. Invoke pm-epic-writing for each feature idea — creates/refines epics.md, epic-status.md, .specify/ specs
7. Review docs/brand/style-guide.md (seeded by Step 8.7) — adjust palette/fonts, then fill voice/tone in pm-client-interview
8. Rename PH- placeholders deliberately as you start real work
9. Read FOLDER-STRUCTURE.md once — canonical layout spec
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

### Step 13 — Register the repo for effort tracking (interactive, optional but recommended)

Now that the GitHub repo exists, register it with the Infinite Leverage effort tracker so human-hours and Claude-session records are captured and displayed in the dashboard.

Ask the operator:

> Do you want to register `$GH_OWNER/$PROJECT_SLUG` for effort tracking now?
> This lets the dashboard show time spent per project. (y / skip)

**If the operator says "skip":** write the local declined marker so the session-start hook stops prompting:

```bash
mkdir -p "$HOME/.claude/.il-telemetry/unregistered"
touch "$HOME/.claude/.il-telemetry/unregistered/${GH_OWNER}__${PROJECT_SLUG}"
echo "Skipped. Marker written — you won't be prompted again for this repo."
echo "To register later, delete: ~/.claude/.il-telemetry/unregistered/${GH_OWNER}__${PROJECT_SLUG}"
```

**If the operator says "y":** gather these details interactively:

| Field | Question to ask |
|---|---|
| Type | "Is this a personal project or a client project?" → `personal` or `client` |
| Display name | "What's the human-readable display name?" (default: `$PROJECT_NAME`) |
| *(client only)* Client name | "What is the client's company name?" |
| *(client only)* Client initials | "Two-letter initials for the client (e.g. E8)?" |
| *(client only)* Is internal? | "Are you part of the client's organisation? (y/n)" — sets `is_internal` |
| *(client only)* Exclude identities | "Are there git emails or GitHub logins belonging to the client's own people that should NOT be counted as AI-assisted effort? (enter email or GitHub login, one per line; blank line to finish)" |

Then build the JSON, commit it to the `telemetry` branch of `talentedgeai/human-token-tracker` at path `registrations/<owner>__<repo>.json`:

```bash
# 1. Resolve current GitHub login
GH_LOGIN=$(gh api user --jq '.login')

# 2. Build the JSON (Claude assembles this from the answers above)
#    Example for a client project:
REGISTRATION_JSON='{
  "repo_full_name": "'"$GH_OWNER/$PROJECT_SLUG"'",
  "github_login": "'"$GH_LOGIN"'",
  "type": "client",
  "project_name": "'"$PROJECT_NAME"'",
  "client": { "name": "Acme Corp", "initials": "AC", "is_internal": false },
  "exclude_identities": [
    { "git_email": "bob@acme.com", "github_login": "bob-acme", "label": "Client" }
  ],
  "submitted_at": "'"$(date -u +%FT%TZ)"'"
}'

# 3. Check if the file already exists on the telemetry branch (to get its sha for update)
REG_PATH="registrations/${GH_OWNER}__${PROJECT_SLUG}.json"
STATUS_RESP=$(gh api "repos/talentedgeai/human-token-tracker/contents/${REG_PATH}?ref=telemetry" 2>/dev/null || echo "")
EXISTING_SHA=$(echo "$STATUS_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sha',''))" 2>/dev/null || echo "")

# 4. Base64-encode the content
ENCODED=$(echo "$REGISTRATION_JSON" | base64)

# 5. PUT to the telemetry branch (with sha if updating, without if creating)
if [ -n "$EXISTING_SHA" ]; then
  gh api -X PUT "repos/talentedgeai/human-token-tracker/contents/${REG_PATH}" \
    -f "message=registration: $GH_OWNER/$PROJECT_SLUG" \
    -f "content=$ENCODED" \
    -f "branch=telemetry" \
    -f "sha=$EXISTING_SHA"
else
  gh api -X PUT "repos/talentedgeai/human-token-tracker/contents/${REG_PATH}" \
    -f "message=registration: $GH_OWNER/$PROJECT_SLUG" \
    -f "content=$ENCODED" \
    -f "branch=telemetry"
fi
```

On success, print:
```
✅ Registration submitted: registrations/$GH_OWNER__$PROJECT_SLUG.json → telemetry branch
   The tracker applies new registrations on its next ingest run (no DB credentials needed).
   Once active, effort records for this repo will appear in the dashboard.
```

On any error, print the error output and tell the operator they can retry by re-invoking this step. Do not leave partial state.

---

## What this skill does NOT do

- Configure Supabase / Vercel / Resend / Brevo — those are done in `infiniteleverage-init` Phase 2
- Link the repo to Vercel for auto-deploy — printed as a next-step for the operator (`vercel link`)
- Generate any content — that's the writer agent
- Write product.md / epics.md content **from scratch** — that's `pm-documentation` via the PM agent. Step 8.6 only seeds these files when the operator hands over planning attachments (or a rich inline description) at invocation time; otherwise they stay as placeholders.
- Define the brand **voice/tone** — Step 8.7 seeds only the *visual* side (palette, typography, visual style) of `docs/brand/style-guide.md`. Voice, vocabulary, and content formats stay for `pm-client-interview` unless planning docs already specify them.
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
