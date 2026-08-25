#!/usr/bin/env bash
# doctor.sh — Infinite Leverage v2 health check. Read-only, always exits 0.
# Never prints secrets or credentials.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"     # skills/il-doctor/scripts → plugin root
HOOKS="$PLUGIN_ROOT/hooks"
IL_STATE="$HOME/.claude/.il-telemetry"

pass() { printf "  ✅  PASS  %-46s %s\n" "$1" "$2"; }
fail() { printf "  ❌  FAIL  %-46s %s\n" "$1" "$2"; }
info() { printf "  ·   %s\n" "$1"; }

echo ""
echo "=== INFINITE LEVERAGE v2 — DOCTOR ==="

# ── A. Plugin ────────────────────────────────────────────────────────────────
echo ""
echo "[ A · Plugin ]"
if command -v python3 >/dev/null 2>&1; then
  pass "python3 available" "$(python3 --version 2>&1)"
else
  fail "python3 available" "fix: install Xcode Command Line Tools or python.org build"
fi

if PYTHONPATH="$HOOKS" python3 -c "import il_telemetry.stop, il_telemetry.flush, il_telemetry.scan" 2>/dev/null; then
  pass "telemetry package imports" ""
else
  fail "telemetry package imports" "fix: update the plugin (marketplace), then re-run /il-doctor"
fi

if [ -f "$HOOKS/hooks.json" ] && python3 -c "import json;json.load(open('$HOOKS/hooks.json'))" 2>/dev/null; then
  pass "hooks.json valid" ""
else
  fail "hooks.json valid" "plugin install is corrupt — reinstall from the marketplace"
fi

# ── B. Consent ───────────────────────────────────────────────────────────────
echo ""
echo "[ B · Telemetry Consent ]"
STATE=$(PYTHONPATH="$HOOKS" python3 -c "from il_telemetry.consent import consent_state; print(consent_state())" 2>/dev/null || echo unknown)
case "$STATE" in
  granted) pass "consent" "granted — sessions in registered repos are tracked" ;;
  denied)  pass "consent" "denied — telemetry fully off" ;;
  *)       info "consent not set — telemetry is OFF until the contributor opts in" ;;
esac

# ── C. Repo context ──────────────────────────────────────────────────────────
echo ""
echo "[ C · This Repo ]"
REMOTE=$(git config --get remote.origin.url 2>/dev/null)
if [ -n "$REMOTE" ]; then
  pass "git remote" "$REMOTE"
else
  info "not inside a git repo with an origin remote — repo checks skipped"
fi
EMAIL=$(git config user.email 2>/dev/null)
if [ -n "$EMAIL" ]; then
  pass "git author email" "$EMAIL"
else
  fail "git author email" "fix: git config --global user.email you@company.com"
fi
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  pass "gh auth (delivery fallback)" "logged in as $(gh api user --jq .login 2>/dev/null)"
else
  info "gh not authenticated — git-append delivery fallback unavailable (tracker API delivery unaffected)"
fi

# ── D. Registration cache ────────────────────────────────────────────────────
if [ -n "$REMOTE" ]; then
  echo ""
  echo "[ D · Registration ]"
  REPO_FULL=$(printf '%s' "$REMOTE" | sed -E 's#\.git$##; s#^git@[^:]+:##; s#^https?://[^/]+/##')
  SAFE=$(printf '%s' "$REPO_FULL" | sed 's|/|__|g')
  if [ -f "$IL_STATE/registered/$SAFE" ]; then
    pass "repo registered (cached)" "$REPO_FULL"
  elif [ -f "$IL_STATE/unregistered/$SAFE" ]; then
    info "repo not registered in the tracker (cached) — sessions here are not delivered"
  else
    info "registration unknown — probed on next session end (never blocks)"
  fi
fi

# ── E. Outbox ────────────────────────────────────────────────────────────────
echo ""
echo "[ E · Outbox ]"
COUNT=$(ls "$IL_STATE/outbox" 2>/dev/null | grep -c '\.json$')
info "captured sessions awaiting delivery: ${COUNT:-0}"

# ── F. v1 residue ────────────────────────────────────────────────────────────
echo ""
echo "[ F · v1 Residue (report only) ]"
python3 "$HOOKS/migrate_v1.py" --report 2>/dev/null | sed 's/^/  /'
if [ -d "$HOME/.claude/scheduled-tasks" ] && [ -n "$(ls -A "$HOME/.claude/scheduled-tasks" 2>/dev/null)" ]; then
  info "scheduled tasks present: $(ls "$HOME/.claude/scheduled-tasks" | tr '\n' ' ')"
  info "(v1 Mac Minis created ~10 agent schedules — review whether these are still wanted)"
fi

echo ""
exit 0
