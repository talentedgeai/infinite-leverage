#!/usr/bin/env bash
# Checks the local Claude Code setup against the Infinite Leverage bootstrap spec.
# Prints a status line per item: ✅ OK | ⚠️  WARN | ❌ MISSING
# Exit code 0 = all OK, 1 = one or more issues found.

CLAUDE_DIR="$HOME/.claude"
issues=0

check() {
  local label="$1"
  local status="$2"  # ok | warn | missing
  local note="$3"
  case "$status" in
    ok)      printf "  ✅  %-45s %s\n" "$label" "$note" ;;
    warn)    printf "  ⚠️   %-45s %s\n" "$label" "$note" ; issues=$((issues+1)) ;;
    missing) printf "  ❌  %-45s %s\n" "$label" "$note" ; issues=$((issues+1)) ;;
  esac
}

echo ""
echo "=== MACHINE HEALTH CHECK ==="
echo ""

# ── 1. Required directories ───────────────────────────────────────────────────
echo "[ Directories ]"
for dir in agents skills rules; do
  if [ -d "$CLAUDE_DIR/$dir" ]; then
    check "~/.claude/$dir/" ok ""
  else
    check "~/.claude/$dir/" missing "run: mkdir -p $CLAUDE_DIR/$dir"
  fi
done
echo ""

# ── 2. settings.local.json ────────────────────────────────────────────────────
echo "[ Permissions — settings.local.json ]"
SETTINGS="$CLAUDE_DIR/settings.local.json"
if [ ! -f "$SETTINGS" ]; then
  check "settings.local.json" missing "not found — re-run setup-permissions.py"
else
  if grep -q '"Bash"' "$SETTINGS" 2>/dev/null; then
    check "Bash(*) permission" ok ""
  else
    check "Bash(*) permission" missing "add Bash(*) to $SETTINGS"
  fi
  if grep -q -i '"mcp"\|supabase\|MCP' "$SETTINGS" 2>/dev/null; then
    check "MCP permission entry" ok ""
  else
    check "MCP permission entry" warn "Supabase MCP may not be configured"
  fi
fi
echo ""

# ── 3. global CLAUDE.md ───────────────────────────────────────────────────────
echo "[ Global CLAUDE.md ]"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
if [ ! -f "$CLAUDE_MD" ]; then
  check "~/.claude/CLAUDE.md" missing "not found — run Phase 2 Prompt 2"
else
  check "~/.claude/CLAUDE.md" ok ""
  # Check for product.md reference (new format — not 00-product-overview.md)
  if grep -q "product\.md" "$CLAUDE_MD" 2>/dev/null; then
    check "  product.md format" ok ""
  elif grep -q "00-product-overview" "$CLAUDE_MD" 2>/dev/null; then
    check "  product.md format" warn "references old 00-product-overview.md — update to product.md"
  else
    check "  product doc section" warn "no product documentation section found"
  fi
  # Check for env vars section
  if grep -q -i "environment variable\|\.env\.example" "$CLAUDE_MD" 2>/dev/null; then
    check "  env vars rule" ok ""
  else
    check "  env vars rule" missing "add ## Environment variables section"
  fi
  # Check for AGENT-DELEGATION block
  if grep -q "BEGIN: AGENT-DELEGATION" "$CLAUDE_MD" 2>/dev/null; then
    check "  agent-delegation block" ok ""
  else
    check "  agent-delegation block" missing "run scripts/inject-agent-delegation.sh ~/.claude/CLAUDE.md"
  fi
fi
echo ""

# ── 3b. project CLAUDE.md files ──────────────────────────────────────────────
echo "[ Project CLAUDE.md files ]"
PROJECTS_DIR="$HOME/code-projects"
if [ -d "$PROJECTS_DIR" ]; then
  shopt -s nullglob
  for proj in "$PROJECTS_DIR"/*/; do
    proj_claude="${proj}CLAUDE.md"
    if [ -f "$proj_claude" ]; then
      if grep -q "BEGIN: AGENT-DELEGATION" "$proj_claude" 2>/dev/null; then
        check "  $(basename "$proj")/CLAUDE.md delegation block" ok ""
      else
        check "  $(basename "$proj")/CLAUDE.md delegation block" missing "run inject-agent-delegation.sh on this file"
      fi
    fi
  done
  shopt -u nullglob
else
  check "  ~/code-projects/" warn "directory not found — skip"
fi
echo ""

# ── 4. global-engineering.md ─────────────────────────────────────────────────
echo "[ Global Engineering Rules ]"
ENG_RULES="$CLAUDE_DIR/rules/global-engineering.md"
if [ ! -f "$ENG_RULES" ]; then
  check "~/.claude/rules/global-engineering.md" missing "not found — run Phase 2 Prompt 2"
else
  check "~/.claude/rules/global-engineering.md" ok ""
  if grep -q -i "environment variable\|\.env\.example" "$ENG_RULES" 2>/dev/null; then
    check "  ## Environment variables section" ok ""
  else
    check "  ## Environment variables section" missing "section not present — needs update"
  fi
fi
echo ""

# ── 5. ~/.claude/.env credentials ────────────────────────────────────────────
echo "[ Credentials — ~/.claude/.env ]"
ENV_FILE="$CLAUDE_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  check "~/.claude/.env" missing "not found — run Phase 2 Prompt 4"
else
  REQUIRED_KEYS=(
    SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY
    GEMINI_API_KEY RESEND_API_KEY
  )
  OPTIONAL_KEYS=(LARK_APP_ID LARK_APP_SECRET LARK_WEBHOOK_URL)
  missing_keys=()
  empty_keys=()
  for key in "${REQUIRED_KEYS[@]}"; do
    line=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null)
    if [ -z "$line" ]; then
      missing_keys+=("$key")
    else
      val="${line#*=}"
      if [ -z "$val" ]; then
        empty_keys+=("$key")
      fi
    fi
  done
  if [ ${#missing_keys[@]} -gt 0 ]; then
    check "required keys present" missing "missing: ${missing_keys[*]}"
  elif [ ${#empty_keys[@]} -gt 0 ]; then
    check "required keys present" warn "empty values: ${empty_keys[*]}"
  else
    check "required keys present and non-empty" ok ""
  fi
  # Lark is optional — warn if partially configured (e.g. only one of three keys set)
  lark_set=0
  lark_missing=0
  for key in "${OPTIONAL_KEYS[@]}"; do
    val=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2-)
    if [ -n "$val" ]; then
      lark_set=$((lark_set + 1))
    else
      lark_missing=$((lark_missing + 1))
    fi
  done
  if [ "$lark_set" -eq 3 ]; then
    check "Lark (optional)" ok "configured"
  elif [ "$lark_set" -eq 0 ]; then
    check "Lark (optional)" warn "not configured — Lark notifications will be skipped"
  else
    check "Lark (optional)" warn "partially configured ($lark_set/3 keys set) — check LARK_APP_ID, LARK_APP_SECRET, LARK_WEBHOOK_URL"
  fi
fi
echo ""

# ── 6. Required CLI tools ────────────────────────────────────────────────────
echo "[ CLI Tools ]"
CLI_TOOLS=(gh vercel supabase resend)
for cli in "${CLI_TOOLS[@]}"; do
  if command -v "$cli" &>/dev/null; then
    version=$("$cli" --version 2>/dev/null | head -1 || "$cli" -v 2>/dev/null | head -1 || echo "installed")
    check "$cli" ok "$version"
  else
    check "$cli" missing "not found — run: brew install $cli / npm install -g $cli"
  fi
done
echo ""

# ── 7. Supabase MCP auth ──────────────────────────────────────────────────────
echo "[ Supabase MCP ]"
SETTINGS="$CLAUDE_DIR/settings.local.json"
if [ -f "$SETTINGS" ] && grep -q -i '"mcp"\|supabase\|MCP' "$SETTINGS" 2>/dev/null; then
  check "MCP entry in settings.local.json" ok ""
  # Check for auth tokens in .env that MCP needs
  if [ -f "$CLAUDE_DIR/.env" ]; then
    has_url=$(grep -c "^SUPABASE_URL=" "$CLAUDE_DIR/.env" 2>/dev/null || true)
    has_key=$(grep -c "^SUPABASE_SERVICE_ROLE_KEY=" "$CLAUDE_DIR/.env" 2>/dev/null || true)
    if [ "$has_url" -gt 0 ] && [ "$has_key" -gt 0 ]; then
      check "MCP auth credentials (SUPABASE_URL + SERVICE_ROLE_KEY)" ok ""
    else
      check "MCP auth credentials" missing "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing from ~/.claude/.env"
    fi
  else
    check "MCP auth credentials" missing "~/.claude/.env not found"
  fi
else
  check "MCP entry in settings.local.json" missing "Supabase MCP not configured — run setup-permissions.py"
fi
echo ""

# ── 8. Hooks ─────────────────────────────────────────────────────────────────
echo "[ Hooks ]"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FOR_HOOKS="$CLAUDE_DIR/settings.local.json"
for hook in pre-bash prompt-submit; do
  if [[ -f "$HOOKS_DIR/$hook" && -x "$HOOKS_DIR/$hook" ]]; then
    check "~/.claude/hooks/$hook" ok ""
  elif [[ -f "$HOOKS_DIR/$hook" ]]; then
    check "~/.claude/hooks/$hook" warn "exists but not executable — run: chmod +x $HOOKS_DIR/$hook"
  else
    check "~/.claude/hooks/$hook" missing "not installed — run infiniteleverage-patch to install"
  fi
done
if [[ -f "$SETTINGS_FOR_HOOKS" ]]; then
  if grep -q "pre-bash" "$SETTINGS_FOR_HOOKS" 2>/dev/null; then
    check "PreToolUse wired in settings.local.json" ok ""
  else
    check "PreToolUse wired in settings.local.json" missing "run infiniteleverage-patch to wire"
  fi
  if grep -q "prompt-submit" "$SETTINGS_FOR_HOOKS" 2>/dev/null; then
    check "UserPromptSubmit wired in settings.local.json" ok ""
  else
    check "UserPromptSubmit wired in settings.local.json" missing "run infiniteleverage-patch to wire"
  fi
fi
echo ""

# ── 9. Required global skills ────────────────────────────────────────────────
echo "[ Global Skills ]"
for skill in daily-checkin create-local-routine create-remote-routine infiniteleverage-patch infiniteleverage-help; do
  if [ -f "$CLAUDE_DIR/skills/$skill/SKILL.md" ]; then
    check "~/.claude/skills/$skill/" ok ""
  else
    check "~/.claude/skills/$skill/" missing "not installed"
  fi
done
echo ""

# ── 9. Installed agents count ─────────────────────────────────────────────────
echo "[ Installed Agents ]"
agent_count=$(ls "$CLAUDE_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$agent_count" -ge 8 ]; then
  check "$agent_count agents installed" ok ""
elif [ "$agent_count" -gt 0 ]; then
  check "$agent_count agents installed" warn "expected 8 — some may be missing"
else
  check "agents installed" missing "no agents found in ~/.claude/agents/"
fi
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
echo "==========================="
if [ "$issues" -eq 0 ]; then
  echo "✅  All checks passed — machine is fully configured"
else
  echo "⚠️   $issues issue(s) found — review items marked ❌ or ⚠️  above"
fi
echo ""

exit $( [ "$issues" -eq 0 ] && echo 0 || echo 1 )
