#!/usr/bin/env bash
# validate.sh — Infinite Leverage contributor self-check for effort tracking.
# Prints PASS/FAIL lines for machine setup, repo registration, capture, and delivery.
# Read-only: makes no changes. Always exits 0 (it's a report, not a gate).
# Never prints secrets or credentials.

CLAUDE_DIR="$HOME/.claude"
TELEMETRY_DIR="$CLAUDE_DIR/hooks/il_telemetry"
OUTBOX_DIR="$CLAUDE_DIR/.il-telemetry/outbox"
SETTINGS="$CLAUDE_DIR/settings.local.json"
PASS="PASS"
FAIL="FAIL"
issues=0

result() {
  local label="$1"
  local status="$2"   # PASS | FAIL
  local note="$3"
  if [ "$status" = "PASS" ]; then
    printf "  ✅  PASS  %-50s %s\n" "$label" "$note"
  else
    printf "  ❌  FAIL  %-50s %s\n" "$label" "$note"
    issues=$((issues+1))
  fi
}

echo ""
echo "=== INFINITE LEVERAGE — EFFORT TRACKING VALIDATOR ==="
echo ""

# ─────────────────────────────────────────────────────────
# SECTION A: Machine setup
# ─────────────────────────────────────────────────────────
echo "[ A · Machine Setup ]"

# A1. Telemetry hooks directory
if [ -d "$TELEMETRY_DIR" ]; then
  result "~/.claude/hooks/il_telemetry/ present" "$PASS" ""
else
  result "~/.claude/hooks/il_telemetry/ present" "$FAIL" "fix: update plugin + run /infiniteleverage-patch"
fi

# A2–A4. Hook wiring in settings.local.json
if [ -f "$SETTINGS" ]; then
  for event in Stop SessionEnd SessionStart; do
    if grep -q "session-telemetry" "$SETTINGS" 2>/dev/null && grep -q "\"$event\"" "$SETTINGS" 2>/dev/null; then
      result "  $event wired in settings.local.json" "$PASS" ""
    else
      result "  $event wired in settings.local.json" "$FAIL" "fix: update plugin + run /infiniteleverage-patch"
    fi
  done
else
  result "settings.local.json found" "$FAIL" "not found at $SETTINGS"
fi

# A5. gh auth
gh_auth_ok=$(gh auth status 2>&1 | grep -c "Logged in" || true)
if [ "$gh_auth_ok" -gt 0 ]; then
  GH_LOGIN=$(gh api user --jq '.login' 2>/dev/null || echo "")
  result "gh auth status" "$PASS" "logged in as $GH_LOGIN"
else
  GH_LOGIN=""
  result "gh auth status" "$FAIL" "fix: gh auth login"
fi

# A6. git user.email
git_email=$(git config --global user.email 2>/dev/null || git config user.email 2>/dev/null || echo "")
if [ -n "$git_email" ]; then
  result "git config user.email" "$PASS" "$git_email"
else
  result "git config user.email" "$FAIL" "fix: git config --global user.email 'you@example.com'"
fi

echo ""

# ─────────────────────────────────────────────────────────
# SECTION B: This repo registration
# ─────────────────────────────────────────────────────────
echo "[ B · This Repo — Registration ]"

# Derive owner/repo from git remote
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")
if [ -n "$REMOTE_URL" ]; then
  # Strip .git suffix
  REPO_FULL="${REMOTE_URL%.git}"
  # Handle scp-style: git@host:owner/repo
  if echo "$REPO_FULL" | grep -q ':' && ! echo "$REPO_FULL" | grep -q '://'; then
    REPO_FULL=$(echo "$REPO_FULL" | sed 's/.*://')
  else
    # Handle scheme://host/owner/repo
    REPO_FULL=$(echo "$REPO_FULL" | sed 's|.*://[^/]*/||')
  fi
  REPO_FULL=$(echo "$REPO_FULL" | sed 's|^/||; s|/$||')
  echo "  Repo:     $REPO_FULL"
else
  REPO_FULL=""
  echo "  Repo:     (not in a git repo with an origin remote)"
fi

if [ -n "$REPO_FULL" ]; then
  # Check registration via API
  if command -v curl >/dev/null 2>&1; then
    REG_RESPONSE=$(curl --silent --max-time 8 \
      "https://human-tokens.com/api/projects/status?repo=${REPO_FULL}" 2>/dev/null || echo "")
    if [ -n "$REG_RESPONSE" ]; then
      IS_REGISTERED=$(echo "$REG_RESPONSE" | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('registered') else 'no')" 2>/dev/null || echo "unknown")
      if [ "$IS_REGISTERED" = "yes" ]; then
        PROJ_NAME=$(echo "$REG_RESPONSE" | python3 -c \
          "import sys,json; d=json.load(sys.stdin); print(d.get('name',''))" 2>/dev/null || echo "")
        result "Registered at human-tokens.com" "$PASS" "${PROJ_NAME:+name: $PROJ_NAME}"
      elif [ "$IS_REGISTERED" = "no" ]; then
        result "Registered at human-tokens.com" "$FAIL" "fix: run registration step in /infiniteleverage-project Step 13"
      else
        result "Registered at human-tokens.com" "$FAIL" "unexpected response — check human-tokens.com manually"
      fi
    else
      result "Registered at human-tokens.com" "$FAIL" "could not reach https://human-tokens.com — check network"
    fi
  else
    echo "  NOTE: curl not available — Claude will fetch the registration status via HTTP instead."
    echo "  Run: GET https://human-tokens.com/api/projects/status?repo=${REPO_FULL}"
    echo "       Expect JSON: { \"registered\": true/false }"
    result "Registered at human-tokens.com" "$FAIL" "curl unavailable — see note above"
  fi

  # Check for local declined/unregistered marker
  OWNER_SLUG=$(echo "$REPO_FULL" | tr '/' '__')
  DECLINED_MARKER="$CLAUDE_DIR/.il-telemetry/unregistered/${OWNER_SLUG}"
  if [ -f "$DECLINED_MARKER" ]; then
    echo "  WARNING: declined marker present at $DECLINED_MARKER"
    echo "           You previously skipped registration for this repo."
    echo "           To re-register, delete that marker file and run /infiniteleverage-project Step 13."
  fi
else
  result "Registered at human-tokens.com" "$FAIL" "no remote origin — cannot determine repo"
fi

echo ""

# ─────────────────────────────────────────────────────────
# SECTION C: Local capture (outbox)
# ─────────────────────────────────────────────────────────
echo "[ C · Local Capture — Outbox ]"

echo "  Outbox dir: $OUTBOX_DIR"
if [ -d "$OUTBOX_DIR" ]; then
  RECORD_COUNT=$(find "$OUTBOX_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$RECORD_COUNT" -gt 0 ]; then
    result "Outbox records pending delivery" "$PASS" "$RECORD_COUNT pending record(s) found"
  else
    result "Outbox records pending delivery" "$PASS" "outbox exists, 0 pending (all delivered or no sessions yet)"
  fi
else
  result "Outbox dir present" "$FAIL" "outbox never written — run a Claude session then end it"
fi

echo ""

# ─────────────────────────────────────────────────────────
# SECTION D: Delivery (best-effort)
# ─────────────────────────────────────────────────────────
echo "[ D · Delivery — telemetry branch (best-effort) ]"

if [ -n "$GH_LOGIN" ] && [ -n "$REPO_FULL" ]; then
  OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
  REPO=$(echo "$REPO_FULL" | cut -d'/' -f2-)

  # client_slug and project_slug are derived from registration JSON in the telemetry branch.
  # As a best-effort check, look for any file under the contributor's login in the telemetry
  # branch of talentedgeai/human-token-tracker.
  # Path format: telemetry/<client_slug>/<project_slug>/<github_login>/<YYYY-MM>.jsonl
  CURRENT_MONTH=$(date -u +%Y-%m)
  SEARCH_PATH="telemetry"

  # Try to find the contributor's folder under any client/project prefix
  API_RESP=$(gh api \
    "repos/talentedgeai/human-token-tracker/contents/${SEARCH_PATH}?ref=telemetry" \
    2>/dev/null || echo "")

  if [ -n "$API_RESP" ]; then
    # Walk one level: find dirs that might lead to contributor files
    CLIENT_DIRS=$(echo "$API_RESP" | python3 -c \
      "import sys,json; items=json.load(sys.stdin); [print(i['name']) for i in items if i.get('type')=='dir']" 2>/dev/null || echo "")

    FOUND_FILE=""
    LAST_TS=""
    for client_dir in $CLIENT_DIRS; do
      PROJ_RESP=$(gh api \
        "repos/talentedgeai/human-token-tracker/contents/${SEARCH_PATH}/${client_dir}?ref=telemetry" \
        2>/dev/null || echo "")
      PROJ_DIRS=$(echo "$PROJ_RESP" | python3 -c \
        "import sys,json; items=json.load(sys.stdin); [print(i['name']) for i in items if i.get('type')=='dir']" 2>/dev/null || echo "")
      for proj_dir in $PROJ_DIRS; do
        # Check if contributor login dir exists
        FILE_CHECK=$(gh api \
          "repos/talentedgeai/human-token-tracker/contents/${SEARCH_PATH}/${client_dir}/${proj_dir}/${GH_LOGIN}/${CURRENT_MONTH}.jsonl?ref=telemetry" \
          2>/dev/null || echo "")
        if [ -n "$FILE_CHECK" ]; then
          FOUND_FILE="${SEARCH_PATH}/${client_dir}/${proj_dir}/${GH_LOGIN}/${CURRENT_MONTH}.jsonl"
          # Extract last commit message/date from the response
          LAST_TS=$(echo "$FILE_CHECK" | python3 -c \
            "import sys,json; d=json.load(sys.stdin); print(d.get('sha','')[:8])" 2>/dev/null || echo "")
          break 2
        fi
      done
    done

    if [ -n "$FOUND_FILE" ]; then
      result "Telemetry file found on branch" "$PASS" "path: $FOUND_FILE (sha prefix: $LAST_TS)"
    else
      result "Telemetry file found on branch" "$FAIL" \
        "no file for $GH_LOGIN/$CURRENT_MONTH found — run a session + end it to trigger delivery"
    fi
  else
    result "Telemetry branch reachable" "$FAIL" \
      "could not access talentedgeai/human-token-tracker telemetry branch — check gh auth"
  fi
else
  result "Delivery check" "$FAIL" "skipped — gh not authenticated or repo not identified"
fi

echo ""

# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
echo "==========================================="
if [ "$issues" -eq 0 ]; then
  echo "OVERALL: PASS — machine set up and logging"
  echo ""
  echo "  Your Claude usage and human hours are being captured and delivered."
  echo "  Note: dashboard numbers may lag until the next ingest run."
else
  echo "OVERALL: PENDING — $issues issue(s) need attention"
  echo ""
  echo "  Review the FAIL lines above and apply the listed fixes."
fi
echo ""

exit 0
