---
name: infiniteleverage-patch
description: This skill should be used when the user says "patch agents", "update my agents", "sync agent changes", "what changed in agents", "agents out of date", "patch this machine", "check my setup", or "apply agent updates". Runs a full two-phase update: (1) health-checks the local Claude Code setup against the bootstrap spec, then (2) fetches the latest universal agent templates from the GitHub canonical repo (`talentedgeai/infiniteleverage-8-agents-template`), diffs against installed agents, and applies updates after confirmation. Safe to run on any machine — Mac Mini or personal laptop.
version: 2.0.0
---

# infiniteleverage-patch — Machine Sync Skill

Two phases every run:

1. **Health check** — verifies the local Claude Code configuration matches the full bootstrap spec (CLAUDE.md, engineering rules, env vars, skills, permissions)
2. **Agent diff + apply** — compares installed agents against the latest in the GitHub repo, shows what changed, applies after confirmation

Run this whenever the operator updates agent definitions, or whenever you suspect a machine is out of sync with the current spec.

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
| `~/.claude/CLAUDE.md` | File exists + references `product.md` (not `00-product-overview.md`) + has `## Environment variables` section |
| `~/.claude/rules/global-engineering.md` | File exists + has `## Environment variables` section |
| `~/.claude/.env` | All 8 required keys present and non-empty: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `RESEND_API_KEY`, `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WEBHOOK_URL` |
| CLI tools | `gh`, `vercel`, `supabase`, `resend` all in PATH and reporting versions |
| Supabase MCP | MCP entry in `settings.local.json` + auth credentials (`SUPABASE_URL` + `SERVICE_ROLE_KEY`) in `~/.claude/.env` |
| Global skills | `daily-checkin`, `create-routines`, `infiniteleverage-patch` installed |
| Agent count | ≥ 8 agents in `~/.claude/agents/` |

**If any ❌ items appear**: show the user the full report and ask which gaps to fix before continuing. Do not auto-fix without confirmation — some gaps (like missing credentials) require manual input.

**If only ⚠️ items**: note them, offer to fix, and continue to Phase 2 regardless.

**Common fixes for ❌ items:**

- `## Environment variables` missing from `global-engineering.md`: append the section from `~/.claude/skills/infiniteleverage-patch/references/engineering-env-patch.md`
- `~/.claude/CLAUDE.md` references `00-product-overview.md`: update the product documentation section to use `product.md`
- Missing `~/.claude/.env` keys: ask the user to supply the values — never guess credentials
- Missing CLI tool: brew install for system tools (`brew install gh supabase`), npm install -g for JS tools (`npm install -g vercel resend`)
- Missing Supabase MCP entry: re-run `setup-permissions.py` from this skill or manually add `"mcpServers"` section to `settings.local.json`
- Missing skills: ask if they want to install the missing skills

---

## Phase 2 — Universal Agent Template Sync

Canonical source: **https://github.com/talentedgeai/infiniteleverage-8-agents-template**

The patch skill fetches the latest templates from this GitHub repo, then diffs against installed agents. A bundled fallback exists in this skill's `agents/`.

### Step 1 — Fetch the latest canonical templates

```bash
if gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-agents 2>/dev/null; then
  SOURCE_DIR="/tmp/il-agents/agents"
  echo "✅ Fetched latest templates from GitHub canonical repo"
else
  SOURCE_DIR="$HOME/.claude/skills/infiniteleverage-patch/agents"
  echo "⚠️  GitHub fetch failed — using bundled fallback"
fi
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

## Edge cases

- **Permission denied**: report and stop — do not use sudo
- **Health check shows `00-product-overview.md` in CLAUDE.md**: offer to patch in place — replace the old reference with `product.md` and update the section description
- **`.env` key is present but empty**: warn and continue — do not halt the agent sync for missing credentials
