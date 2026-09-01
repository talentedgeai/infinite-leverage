#!/usr/bin/env bash
# doctor.sh — Infinite Leverage setup check. Read-only, always exits 0.
# Never prints secrets or credentials.

pass() { printf "  ✅  PASS  %-46s %s\n" "$1" "$2"; }
fail() { printf "  ❌  FAIL  %-46s %s\n" "$1" "$2"; }
info() { printf "  ·   %s\n" "$1"; }

# The canonical team. CI keeps these in lockstep with il-project step 6 and
# il-adopt step 5 — drift here is how "found 6/8" once shipped.
CANON_AGENTS="product-manager developer qa devops"
MIN_SKILLS=16
# Retired in v2.6 — a project scaffolded on v2.4.x carries them until refreshed.
RETIRED_AGENTS="writer designer"
RETIRED_SKILLS="writer-seo-content writer-quality-critique marketing-strategist \
  email-marketer-nurture designer-design-system designer-style-to-photo \
  designer-image-generation designer-ui-ux"
# One refresh path for every project, scaffolded or adopted.
REFRESH="run /il-adopt (refreshes the team in place)"

echo ""
echo "=== INFINITE LEVERAGE — DOCTOR ==="

# ── A. Prerequisites ─────────────────────────────────────────────────────────
echo ""
echo "[ A · Prerequisites ]"
# Required set = exactly what /il-project runs:
#   git+gh (steps 1-3, 12) · perl (steps 4, 7) · node/npm/npx + rsync (step 9)
for tool in git gh perl node npm npx rsync; do
  if command -v "$tool" >/dev/null 2>&1; then
    pass "$tool available" "$($tool --version 2>&1 | grep -m1 . | cut -c1-40)"
  else
    case "$tool" in
      gh)              fix="fix: brew install gh && gh auth login" ;;
      node|npm|npx)    fix="fix: brew install node (needed for the Next.js scaffold, step 9)" ;;
      rsync)           fix="fix: brew install rsync (needed to merge the starter kit, step 9)" ;;
      perl)            fix="fix: install Xcode Command Line Tools (placeholder substitution, steps 4+7)" ;;
      *)               fix="fix: install Xcode Command Line Tools" ;;
    esac
    fail "$tool available" "$fix"
  fi
done
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    pass "gh authenticated" "logged in as $(gh api user --jq .login 2>/dev/null)"
  else
    fail "gh authenticated" "fix: the user must run 'gh auth login' themselves"
  fi
fi

# ── B. Repo context ──────────────────────────────────────────────────────────
echo ""
echo "[ B · Repo Context ]"
REMOTE=$(git config --get remote.origin.url 2>/dev/null)
if [ -n "$REMOTE" ]; then
  pass "git remote" "$REMOTE"
else
  info "not inside a git repo — fine if you're about to scaffold a new project"
fi
EMAIL=$(git config user.email 2>/dev/null)
if [ -n "$EMAIL" ]; then
  pass "git author email" "$EMAIL"
else
  fail "git author email" "fix: git config --global user.email you@company.com"
fi

# ── C. Project layout (inside a scaffolded OR adopted project) ───────────────
# /il-project leaves FOLDER-STRUCTURE.md behind; /il-adopt installs into a repo
# that has none. Detect either — keyed on the marker file alone, an adopted
# repo never got its layout checked at all.
if [ -f "FOLDER-STRUCTURE.md" ] || [ -d ".claude/agents" ] \
   || grep -q "BEGIN: AGENT-DELEGATION" CLAUDE.md 2>/dev/null; then
  echo ""
  echo "[ C · Project Layout ]"
  if [ -f "FOLDER-STRUCTURE.md" ]; then
    pass "FOLDER-STRUCTURE.md present" "scaffolded by /il-project"
  else
    info "no FOLDER-STRUCTURE.md — an adopted repo (/il-adopt); that's fine"
  fi

  # Assert the canonical agents are PRESENT — not a bare count. A count of 4
  # passes writer+designer+2 customs with qa missing; a count of "exactly 4"
  # fails every project that legitimately added its own agent.
  MISSING=""
  for a in $CANON_AGENTS; do
    [ -f ".claude/agents/$a.md" ] || MISSING="$MISSING $a"
  done
  AGENTS=$(find .claude/agents -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  if [ -z "$MISSING" ]; then
    pass "canonical agents installed" "$AGENTS agents in .claude/agents/ (all 4 canonical present)"
  else
    fail "canonical agents installed" "missing:$MISSING — fix: $REFRESH"
  fi

  SKILLS=$(find .claude/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  if [ "$SKILLS" -ge "$MIN_SKILLS" ]; then
    pass "project skills installed" "$SKILLS skills in .claude/skills/"
  else
    fail "project skills installed" "found $SKILLS (expected $MIN_SKILLS) — fix: $REFRESH"
  fi

  if [ -f ".claude/rules/global-engineering.md" ]; then
    pass "engineering rules installed" ".claude/rules/global-engineering.md"
  else
    fail "engineering rules installed" "missing .claude/rules/global-engineering.md — fix: $REFRESH"
  fi

  RETIRED=""
  for f in $RETIRED_AGENTS; do
    [ -f ".claude/agents/$f.md" ] && RETIRED="$RETIRED agents/$f.md"
  done
  for d in $RETIRED_SKILLS; do
    [ -d ".claude/skills/$d" ] && RETIRED="$RETIRED skills/$d/"
  done
  if [ -n "$RETIRED" ]; then
    fail "no retired v2.4 agents/skills" "found:$RETIRED — fix: $REFRESH (moves them to .claude/retired-il-<date>/)"
  else
    pass "no retired v2.4 agents/skills" ""
  fi

  if grep -q "BEGIN: AGENT-DELEGATION" CLAUDE.md 2>/dev/null; then
    # The v2.4 block routed to writer/designer. A refreshed team under a stale
    # block still sends requests to agents that no longer exist on disk.
    if sed -n '/BEGIN: AGENT-DELEGATION/,/END: AGENT-DELEGATION/p' CLAUDE.md \
         | grep -qE '\*\*(writer|designer)\*\*'; then
      fail "CLAUDE.md delegation block current" "block still routes to writer/designer (v2.4) — fix: $REFRESH"
    else
      pass "CLAUDE.md delegation block" "present and current"
    fi
  else
    fail "CLAUDE.md delegation block" "fix: $REFRESH"
  fi
fi

# ── C2. Plugin version vs the marketplace ────────────────────────────────────
# A cached older plugin is how a fixed bug keeps biting: /il-project's own steps
# ship IN the plugin, so a client stays on the broken version until they update.
echo ""
echo "[ C2 · Plugin Version ]"
PJ="${CLAUDE_PLUGIN_ROOT:-}/.claude-plugin/plugin.json"
if [ -f "$PJ" ]; then
  # sed, not python3: python3 is not a prerequisite and its absence used to make
  # this silently report "unknown".
  LOCAL_V=$(sed -nE 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' "$PJ" | head -1)
  pass "installed plugin" "v${LOCAL_V:-unknown}"
  REMOTE_V=$(git ls-remote --tags https://github.com/talentedgeai/infinite-leverage 'refs/tags/v*' 2>/dev/null \
    | sed 's#.*refs/tags/v##' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
  if [ -z "$REMOTE_V" ]; then
    info "could not reach the marketplace to compare versions (offline is fine)"
  elif [ "$REMOTE_V" != "$LOCAL_V" ] && [ "$(printf '%s\n%s' "$LOCAL_V" "$REMOTE_V" | sort -V | tail -1)" = "$REMOTE_V" ]; then
    fail "plugin up to date" "v$LOCAL_V installed, v$REMOTE_V released — fix: claude plugin update infiniteleverage@infiniteleverage"
  else
    pass "plugin up to date" "v$LOCAL_V is current"
  fi
else
  info "not running from an installed plugin — version check skipped"
fi

# ── D. Companion plugin (Edge8-internal) ─────────────────────────────────────
echo ""
echo "[ D · Companion ]"
if ls "$HOME/.claude/plugins/cache/edge8/edge8-telemetry" >/dev/null 2>&1; then
  info "edge8-telemetry plugin installed — use /edge8-telemetry for tracking status"
else
  info "edge8-telemetry not installed (Edge8-internal; outside users don't need it)"
fi

echo ""
exit 0
