---
name: infiniteleverage-patch
description: Health-check local Claude Code setup, then fetch latest agent templates from GitHub and apply updates. Safe on Mac Mini or laptop.
---

# infiniteleverage-patch — Machine Sync Skill

Two phases every run:

1. **Health check** — verifies the local Claude Code configuration matches the full bootstrap spec (CLAUDE.md, engineering rules, env vars, skills, permissions)
2. **Agent diff + apply** — compares installed agents against the latest in the GitHub repo, shows what changed, applies after confirmation

Run this whenever the operator updates agent definitions, or whenever you suspect a machine is out of sync with the current spec.

---

## Settings Safety Protocol

Before writing or patching any configuration file — `settings.local.json`, `CLAUDE.md`, `global-engineering.md` — check what's already there and follow these three rules:

| Scenario | Action |
|---|---|
| File exists with compatible content (e.g. `settings.local.json` with different permissions, `CLAUDE.md` with custom sections) | **Merge** — add what's missing without removing what's already there |
| File exists and is a complete previous version of this template | **Upgrade** — replace the whole file with the latest version |
| File exists with content that conflicts with the template's intended pattern | **Try to resolve** — preserve the user's value and intent while satisfying the template requirement. If you can't resolve cleanly without losing something, ask the user before touching the file |

**When asking about a conflict, use plain language — no JSON keys, no file paths, no technical jargon:**
- Say what the setting *does*, not what it's called
- Offer a simple choice: keep theirs, use the template's, or combine both

---

## Phase 1 — Machine Health Check

```bash
bash ~/.claude/skills/infiniteleverage-patch/scripts/health-check.sh
```

The script checks and reports ✅ / ⚠️ / ❌ for each item:

| Check | What it looks for |
|-------|-------------------|
| `~/.claude/agents/`, `skills/`, `rules/` | Directories exist |
| `settings.local.json` | `Bash(*)` permission + MCP entry present |
| `~/.claude/CLAUDE.md` | File exists + references `product.md` (not `00-product-overview.md`) + has `## Environment variables` section + has `AGENT-DELEGATION` block |
| Project `CLAUDE.md` | (For every repo under `~/code-projects/`) has `AGENT-DELEGATION` block — auto-injected by `scripts/inject-agent-delegation.sh` when missing |
| `~/.claude/rules/global-engineering.md` | File exists + has `## Environment variables` section |
| `~/.claude/.env` | Required keys present and non-empty: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `RESEND_API_KEY`. Optional: `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WEBHOOK_URL` (all three or none — partial config warns). |
| CLI tools | `gh`, `vercel`, `resend` all in PATH and reporting versions |
| Supabase plugin (MCP) | `plugin:supabase` installed (Supabase MCP tools available) + auth credentials (`SUPABASE_URL` + `SERVICE_ROLE_KEY`) in `~/.claude/.env` |
| Hooks | `~/.claude/hooks/pre-bash` + `prompt-submit` exist and are executable |
| Hook wiring | `PreToolUse` and `UserPromptSubmit` entries present in `settings.local.json` |
| Global skills | `daily-checkin`, `create-local-routine`, `create-remote-routine`, `infiniteleverage-patch`, `infiniteleverage-help`, `create-agent` installed |
| Agent count | ≥ 8 agents in `~/.claude/agents/` |

**If any ❌ items appear**: show the user the full report and ask which gaps to fix before continuing. Do not auto-fix without confirmation — some gaps (like missing credentials) require manual input.

**If only ⚠️ items**: note them, offer to fix, and continue to Phase 2 regardless.

**Common fixes for ❌ items:**

- `## Environment variables` missing from `global-engineering.md`: append the section from `~/.claude/skills/infiniteleverage-patch/references/engineering-env-patch.md`
- `~/.claude/CLAUDE.md` references `00-product-overview.md`: update the product documentation section to use `product.md`
- `AGENT-DELEGATION` block missing from any CLAUDE.md (global or project): inject it with `bash ~/.claude/skills/infiniteleverage-patch/scripts/inject-agent-delegation.sh <path-to-CLAUDE.md>` — the script is idempotent and only edits between BEGIN/END markers
- Missing `~/.claude/.env` keys: ask the user to supply the values — never guess credentials
- Missing CLI tool: brew install for system tools (`brew install gh`), npm install -g for JS tools (`npm install -g vercel resend`)
- Missing Supabase plugin: Claude Code cannot install a plugin on its own — ask the operator to run `/plugin` in Claude Code → marketplace → install **supabase** → restart if prompted, then run the auth flow (`mcp__supabase__authenticate` → `mcp__supabase__complete_authentication`)
- Missing skills: ask if they want to install the missing skills
- Missing hooks or hook wiring: run `bash ~/.claude/skills/infiniteleverage-patch/scripts/install-hooks.sh /tmp/il-agents` (clone first if `/tmp/il-agents` doesn't exist)

---

## Phase 2 — Universal Sync from Canonical Source

**Canonical source (single source of truth for the entire system):**
> https://github.com/talentedgeai/infiniteleverage-8-agents-template

What this skill synchronizes from the canonical repo to the local machine:

| Local target | Canonical source path |
|---|---|
| `~/.claude/agents/*.md` | `.claude/agents/*.md` |
| `~/.claude/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |
| `~/.claude/scheduled-tasks/*/SKILL.md` | `.claude/scheduled-tasks/*/SKILL.md` |
| `~/.claude/rules/global-engineering.md` | `.claude/rules/global-engineering.md` |
| `~/.claude/CLAUDE.md` (AGENT-DELEGATION block) | regenerated by `scripts/inject-agent-delegation.sh` |
| `~/code-projects/*/CLAUDE.md` (AGENT-DELEGATION block) | regenerated by `scripts/inject-agent-delegation.sh` |
| Project scaffold reference | `templates/project-scaffold/` |

The patch skill **fetches the latest from the canonical repo, diffs against what's installed, and applies updates after confirmation**. If GitHub is unreachable, the patch halts and reports — no bundled fallback exists, since offline installs would drift immediately.

**Rule:** Never patch by hand-editing local files — that introduces drift. All changes go upstream first.

### Step 1 — Fetch the latest canonical templates

```bash
gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-agents --depth 1 \
  || { echo "❌ GitHub fetch failed — check gh auth status and network"; exit 1; }
SOURCE_DIR="/tmp/il-agents"
echo "✅ Fetched latest templates from GitHub canonical repo"
```

### Step 2 — Run the agent diff

```bash
bash ~/.claude/skills/infiniteleverage-patch/scripts/diff-agents.sh "$SOURCE_DIR"
```

Compares every `.md` in the source against `~/.claude/agents/`. Report format:

```
=== AGENT DIFF REPORT ===

NEW (in template, not installed):
  + web-scraper.md

MODIFIED (content differs):
  ~ developer.md     [shows changed lines]
  ~ product-manager.md

REMOVED (installed but not in template):
  - old-agent.md

UNCHANGED:
  = qa.md  = devops.md  = writer.md ...

```

Present this verbatim.

---

### Step 3 — Confirm before applying

> "Ready to apply:
> - Add: {list}
> - Update: {list}
> - Remove: {list}
>
> Reply **yes** (full apply), **skip removals**, or **no** (cancel)."

If nothing changed: "All agents are up to date."

---

### Step 4 — Apply

```bash
# Full apply (add + update + remove deprecated):
bash ~/.claude/skills/infiniteleverage-patch/scripts/apply-patch.sh "$SOURCE_DIR" full

# Skip removals (add + update only):
bash ~/.claude/skills/infiniteleverage-patch/scripts/apply-patch.sh "$SOURCE_DIR" no-remove
```

After applying, sync scheduled tasks:

```bash
mkdir -p ~/.claude/scheduled-tasks
cp -R "$SOURCE_DIR/.claude/scheduled-tasks/." ~/.claude/scheduled-tasks/
echo "✅ Scheduled tasks synced"
ls ~/.claude/scheduled-tasks/
```

**Note on CronCreate re-registration**: Copying the SKILL.md files does NOT automatically re-register running cron jobs. After a patch, tell the user to re-run Prompt 10 (schedule registration) if they want updated task prompts to take effect. Existing `CronCreate` jobs with `durable: true` continue running the old prompt until deleted and recreated.

After applying, deploy `team-hours.py` to every existing project under `~/code-projects/`:

```bash
SCRIPT_SRC="$HOME/.claude/skills/pm-contribution-sync/team-hours.py"
if [ -f "$SCRIPT_SRC" ]; then
  for proj in ~/code-projects/*/; do
    [ -f "$proj/CLAUDE.md" ] || continue          # skip non-IL projects
    mkdir -p "$proj/scripts"
    # Additive: only copy if absent or template is newer
    if [ ! -f "$proj/scripts/team-hours.py" ] || \
       [ "$SCRIPT_SRC" -nt "$proj/scripts/team-hours.py" ]; then
      cp "$SCRIPT_SRC" "$proj/scripts/team-hours.py"
      echo "  ✅ team-hours.py → $proj/scripts/"
    else
      echo "  = team-hours.py already current in $proj"
    fi
  done
else
  echo "  ⚠️  team-hours.py not found at $SCRIPT_SRC — skipping project deployment"
fi
```

Also add `scripts/contribution-snapshot.json` to each project's `.gitignore` (machine-local paths, must not be committed):

```bash
for proj in ~/code-projects/*/; do
  [ -f "$proj/CLAUDE.md" ] || continue
  gi="$proj/.gitignore"
  if ! grep -q "contribution-snapshot.json" "$gi" 2>/dev/null; then
    echo "scripts/contribution-snapshot.json" >> "$gi"
    echo "  ✅ .gitignore updated in $proj"
  fi
done
```

---

### Step 5 — Clean up fetched templates

```bash
rm -rf /tmp/il-agents
```

---

### Step 6 — Final report

```bash
ls ~/.claude/agents/
```

Print summary:
> "✅ Patch complete — {N} added, {N} updated, {N} removed. Installed agents: {list}"

Report any errors explicitly — never silently skip a failed copy.

---

## Phase 3 — Stamp installed version and ensure plugin is registered

After confirming the update is complete, stamp the installed release version:

```bash
version="$(curl --silent --max-time 5 \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/talentedgeai/infiniteleverage-8-agents-template/releases/latest" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name','').lstrip('v'))" 2>/dev/null || echo "")"
if [[ -n "$version" ]]; then
  echo "$version" > ~/.claude/.infiniteleverage-version
  echo "Version stamped: $version"
else
  echo "⚠️ Could not fetch version from GitHub Releases — check network or run again"
fi
```

This keeps the local version in sync so the plugin's SessionStart hook knows the machine is current and won't auto-update unnecessarily.

Then ensure the plugin is registered (idempotent — safe to run even if already installed):

```bash
claude plugin marketplace add talentedgeai/infiniteleverage-plugin
```

If the plugin is already registered, this is a no-op. If not (e.g. the machine was set up before the plugin existed), this registers and enables it so future sessions load the hooks automatically.

If `claude plugin` is not available, the user is on an older Claude Code version — run `npm i -g @anthropic-ai/claude-code@latest` to upgrade first.

---

## Edge cases

- **Permission denied**: report and stop — do not use sudo
- **Health check shows `00-product-overview.md` in CLAUDE.md**: offer to patch in place — replace the old reference with `product.md` and update the section description
- **`.env` key is present but empty**: warn and continue — do not halt the agent sync for missing credentials
