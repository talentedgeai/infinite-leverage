#!/usr/bin/env bash
# doctor.sh — Infinite Leverage setup check. Read-only, always exits 0.
# Never prints secrets or credentials.

pass() { printf "  ✅  PASS  %-46s %s\n" "$1" "$2"; }
fail() { printf "  ❌  FAIL  %-46s %s\n" "$1" "$2"; }
info() { printf "  ·   %s\n" "$1"; }

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

# ── C. Project layout (only inside a scaffolded project) ─────────────────────
if [ -f "FOLDER-STRUCTURE.md" ]; then
  echo ""
  echo "[ C · Project Layout ]"
  pass "FOLDER-STRUCTURE.md present" ""
  AGENTS=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "$AGENTS" -ge 6 ]; then
    pass "project agents installed" "$AGENTS agents in .claude/agents/"
  else
    fail "project agents installed" "found $AGENTS/6 — fix: re-run /il-project step 6 to refresh"
  fi
  SKILLS=$(ls -d .claude/skills/*/ 2>/dev/null | wc -l | tr -d ' ')
  if [ "$SKILLS" -ge 20 ]; then
    pass "project skills installed" "$SKILLS skills in .claude/skills/"
  else
    fail "project skills installed" "found $SKILLS (expected 24) — fix: re-run /il-project step 6 to refresh"
  fi
  if grep -q "BEGIN: AGENT-DELEGATION" CLAUDE.md 2>/dev/null; then
    pass "CLAUDE.md delegation block" ""
  else
    fail "CLAUDE.md delegation block" "fix: re-run /il-project step 7 to inject it"
  fi
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
