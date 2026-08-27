---
name: il-adopt
description: This skill should be used when the operator says "il adopt", "il init", "install the agents", "add the agent team to this repo", "init the agents in this project", "set up infinite leverage here", "adopt infinite leverage", or has an already-established repository that needs the 4-agent team. Installs the canonical 4 agent definitions, the workflow skills, and the engineering rules into the CURRENT repo's `.claude/`, injects the AGENT-DELEGATION block into the repo's CLAUDE.md, and seeds only the missing doc anchors — without touching any existing project file. The existing-repo counterpart of `/il-project` (which scaffolds a brand-new project).
version: 1.0.0
---

# Infinite Leverage — Adopt the Agent Team into an Existing Repo

## What this is

`/il-project` scaffolds a **brand-new** project and installs the 4-agent team into it.
This skill does the install half **for a repo that already exists** — a codebase the
operator built before Infinite Leverage, or a project where the plugin was installed
but the per-project team never was (the plugin itself ships no agents; they are always
installed per-project).

**Every file this skill writes comes from ONE repo:**

> https://github.com/talentedgeai/infinite-leverage

| What | Canonical path |
|---|---|
| 4 agent definitions | `.claude/agents/*.md` |
| Project workflow skills | `.claude/skills/*/SKILL.md` |
| Engineering rules | `.claude/rules/global-engineering.md` |
| Persona stubs | `templates/project-scaffold/agents/<name>/context/persona.md` |
| Doc anchors (product, brand, status) | `templates/project-scaffold/docs/` |
| AGENT-DELEGATION block content | embedded below — same block as `/il-project` Step 7 |

## When to invoke

The operator is inside an existing repository and wants the Infinite Leverage team
working in it. Prerequisites: the Infinite Leverage v2 plugin installed (which is how
this skill is running), plus `git`, an authenticated `gh`, and `perl` — Step 1 checks
them. Agents are installed into the project itself; nothing is ever written to
`~/.claude/`.

## Execution contract (read before Step 1)

1. **Zero required inputs.** The target is the current repo. Run end-to-end without
   pauses except the two confirmations below.
2. **Two decision points only:** (a) the dirty-tree / preview confirmation in Step 2,
   and (b) the overwrite confirmation in Step 3 — and only if an earlier install is
   detected. Nothing else asks.
3. **Non-destructive by default.** Canonical-managed files (`.claude/agents/`,
   `.claude/skills/`, `.claude/rules/global-engineering.md`) may be overwritten —
   that is what "refresh" means and Step 3 confirms it first. Everything else
   (personas, doc anchors, CLAUDE.md content outside the managed block) is written
   **only where missing**.
4. **Never commit.** This skill stages nothing and commits nothing — it prints the
   exact commands at the end for the operator to run.
5. **Stay inside the repo.** Every write goes to the repo root — never to
   `~/.claude/`, never to any other directory.
6. **Never bypass a blocker silently.** If a prerequisite fails, stop and report.

## Steps

All commands below are run via the Bash tool. Each step is independent and re-runnable.

### Step 1 — Verify prerequisites

```bash
MISSING=""
for t in git gh perl; do
  command -v "$t" >/dev/null 2>&1 || MISSING="$MISSING $t"
done
[ -n "$MISSING" ] && { echo "❌ missing required tools:$MISSING"; echo "   run /il-doctor for per-tool install commands"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "❌ gh is not authenticated — the operator must run 'gh auth login' themselves"; exit 1; }
echo "✅ prerequisites OK"
```

### Step 2 — Resolve the target repo and preview

```bash
TARGET=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "❌ not inside a git repository — cd into the repo first (or run /il-project to create a new one)"; exit 1; }
echo "target repo: $TARGET"
git -C "$TARGET" status --short
```

Print a dry-run preview and confirm before writing anything:

```
About to adopt the Infinite Leverage team into:
  Repo            : <$TARGET>
  Will install    : 4 agents → .claude/agents/
                    workflow skills → .claude/skills/
                    engineering rules → .claude/rules/global-engineering.md
  Will inject     : AGENT-DELEGATION block into ./CLAUDE.md (created if missing)
  Only-if-missing : agents/<name>/context/persona.md stubs,
                    docs/product/{product,epics,epic-status}.md,
                    docs/brand/style-guide.md, docs/project-status.html
  Will NOT touch  : your source code, package.json, CI, git history — no commits
Proceed? (y/N)
```

If `git status` showed uncommitted changes, say so in the preview and let the
operator decide — the install writes only into `.claude/`, `agents/`, `docs/`, and
`CLAUDE.md`, but they should know their tree is dirty before new files land in it.

### Step 3 — Detect a previous install (refresh vs. first install)

```bash
EXISTING=$(find "$TARGET/.claude/agents" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
```

- `EXISTING` = 0 → first install, continue silently.
- `EXISTING` > 0 → this run is a **refresh**: the canonical agents, skills, and
  `global-engineering.md` will be overwritten with the versions matching the running
  plugin. Ask: *"Found an existing team install (`<EXISTING>` agents). Refresh it to
  the canonical v<plugin version>? Any local edits to `.claude/agents/`,
  `.claude/skills/`, or `.claude/rules/global-engineering.md` will be overwritten —
  project personas and docs are untouched. (y/N)"* Stop on no.

### Step 4 — Fetch the canonical repo, pinned to the plugin's version

Same pinning rule as `/il-project` Step 3: the installed plugin is cached per
version, so clone the tag that matches it — otherwise the files installed can be
newer than the skill instructions running.

```bash
TMP=$(mktemp -d)
REPO=talentedgeai/infinite-leverage

IL_VERSION=$(python3 -c "import json,os,sys; print(json.load(open(os.path.join(os.environ['CLAUDE_PLUGIN_ROOT'],'.claude-plugin','plugin.json')))['version'])" 2>/dev/null)

if [ -n "$IL_VERSION" ] && git ls-remote --tags "https://github.com/$REPO" "refs/tags/v$IL_VERSION" | grep -q .; then
  gh repo clone "$REPO" "$TMP/il-canonical" -- --depth 1 --branch "v$IL_VERSION"
  echo "✅ canonical content pinned to v$IL_VERSION — matches the installed plugin"
else
  gh repo clone "$REPO" "$TMP/il-canonical" -- --depth 1
  echo "⚠️  no tag v${IL_VERSION:-?} on $REPO — falling back to main."
  echo "   The installed files may be newer than this skill. Report it if something looks wrong."
fi
```

### Step 5 — Install agents + skills + rules into the repo's `.claude/`

Identical to `/il-project` Step 6 — canonical-managed files, overwrite is correct
(Step 3 already confirmed if anything existed):

```bash
mkdir -p "$TARGET/.claude/agents" "$TARGET/.claude/skills" "$TARGET/.claude/rules"
cp "$TMP/il-canonical/.claude/agents/"*.md "$TARGET/.claude/agents/"
cp -R "$TMP/il-canonical/.claude/skills/." "$TARGET/.claude/skills/"
rm -rf "$TARGET/.claude/skills/PH-skill-name"   # scaffold placeholder — not a real skill
cp "$TMP/il-canonical/.claude/rules/global-engineering.md" "$TARGET/.claude/rules/"
```

Verify — hard gate, same as `/il-project`:

```bash
# find, not a glob: under zsh a non-matching glob aborts the command instead of
# returning nothing, so `ls dir/*.md` would error out rather than count zero.
A=$(find "$TARGET/.claude/agents" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
S=$(find "$TARGET/.claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
echo "agents: $A/4 · skills: $S/16"
[ "$A" -eq 4 ] && [ "$S" -ge 16 ] || {
  echo "❌ install incomplete — expected 4 agents and at least 16 skills"
  echo "   check that \$TMP/il-canonical/.claude/ exists and the mkdir -p above ran"
  exit 1
}
```

Do not continue unless this gate passes. Report the counts either way.

### Step 6 — Install persona stubs (only where missing)

The agent definitions read `agents/<name>/context/persona.md` on first invocation
for project-specific overrides. Seed the stubs, never clobbering an existing one:

```bash
for name in developer devops product-manager qa; do
  DST="$TARGET/agents/$name/context/persona.md"
  [ -e "$DST" ] && continue
  mkdir -p "$(dirname "$DST")"
  cp "$TMP/il-canonical/templates/project-scaffold/agents/$name/context/persona.md" "$DST"
done
```

### Step 7 — Inject/refresh the AGENT-DELEGATION block in the repo's CLAUDE.md

Create `CLAUDE.md` if the repo has none. If it exists, only the managed block
(between `BEGIN: AGENT-DELEGATION` / `END: AGENT-DELEGATION` markers) is replaced —
everything else the operator wrote stays byte-for-byte. Idempotent.

```bash
TARGET_CLAUDE_MD="$TARGET/CLAUDE.md"
touch "$TARGET_CLAUDE_MD"

# Canonical block content — kept in lockstep with /il-project Step 7.
BLOCK=$(cat <<'BLOCK_EOF'
<!-- BEGIN: AGENT-DELEGATION (managed by infiniteleverage skills — do not delete this block) -->
## Agent delegation (auto-routing)

When you receive a request, **delegate to the right specialist agent** before doing the work yourself. The 4 agents and their triggers:

| Agent | Delegate when the request involves… |
|---|---|
| **product-manager** | roadmap, vision, epics, daily plan, project-status.html, scope changes, approval triage, stakeholder updates |
| **developer** | writing/changing code, fixing bugs, refactoring, scaffolding pages, API endpoints, Supabase migrations, env-vars wiring, **publishing posts to the live site** |
| **qa** | testing, regression checks, browser matrix, accessibility, QA plans, "verify this works" |
| **devops** | CI/CD, deployments, secret management, infra escalations, Vercel/GitHub workflow issues |

**Delegation rules:**
1. Pick exactly **one** agent per turn — don't run two in parallel unless the operator explicitly says so.
2. If a request spans agents (e.g., "build it *and* verify it"), call them **in sequence**: developer → qa.
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

### Step 8 — Seed missing doc anchors (only where missing)

The PM/QA agents key on a handful of files. Seed the placeholders **only where the
repo doesn't already have them** — an existing project's real docs always win:

```bash
for rel in \
  docs/product/product.md \
  docs/product/epics.md \
  docs/product/epic-status.md \
  docs/brand/style-guide.md \
  docs/project-status.html; do
  DST="$TARGET/$rel"
  [ -e "$DST" ] && continue
  mkdir -p "$(dirname "$DST")"
  cp "$TMP/il-canonical/templates/project-scaffold/$rel" "$DST"
done
```

Then substitute the branded placeholders in any file this step just created (skip
files that already existed). Derive the display name from the repo folder unless the
operator stated one:

```bash
PROJECT_NAME="My Project"                 # operator-supplied or derived from basename
PROJECT_SLUG=$(basename "$TARGET")
# run ONLY on the files copied above:
perl -i -pe "s/\Q{Project Name}\E/$PROJECT_NAME/g; s/\Q{project-slug}\E/$PROJECT_SLUG/g" <each copied file>
```

These are placeholders on purpose — `pm-client-interview` / `pm-epic-writing` fill
them properly. Unlike `/il-project`, this skill never seeds product content or brand
styling from attachments; in an existing repo that synthesis deserves its own
conversation with the PM agent.

### Step 9 — Clean up and summarize

```bash
rm -rf "$TMP"
```

Print:

```
✅ Team adopted into <$TARGET>
   .claude/agents/     — 4 agents (product-manager, developer, qa, devops)
   .claude/skills/     — <S> workflow skills
   .claude/rules/      — global-engineering.md
   agents/*/context/   — persona stubs (<N> created, <M> already existed)
   CLAUDE.md           — AGENT-DELEGATION block <injected|refreshed>
   docs/               — <K> anchors seeded, existing files untouched

Nothing was committed. To commit the install (staging explicitly — no `git add .`):
  cd <$TARGET>
  git add .claude/agents .claude/skills .claude/rules CLAUDE.md agents docs
  git commit -m "chore: adopt Infinite Leverage agent team (v<IL_VERSION>)"

Next steps:
1. Restart Claude Code in this repo so the project agents and skills load
2. Invoke @product-manager → pm-client-interview (or pm-grill-with-docs if docs/product/ already has content)
3. Review CLAUDE.md — the delegation block sits alongside your existing instructions
```

## What this skill does NOT do

- Scaffold folders, Next.js, spec-kit, or git — the repo already exists; `/il-project` owns greenfield setup
- Overwrite any file the operator wrote — only canonical-managed files under `.claude/` are refreshed, and only after the Step 3 confirmation
- Seed product/brand content from attachments — that's the PM agent's job in an existing repo
- Commit, push, or create GitHub repos
- Write anything under `~/.claude/`

## References

- `il-project/SKILL.md` — greenfield counterpart; Steps 3/6/7 here mirror its pinning, install gate, and delegation block
- `il-doctor/SKILL.md` — run after adopting to verify the project layout
