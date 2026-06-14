#!/usr/bin/env bash
# End-to-end smoke test for the effort-tracking hook chain.
# Proves: install → wiring correctness → capture → outbox write.
# No real session data is sent; cleans up after itself.
# Usage: bash smoke-test-hooks.sh [source-dir]
#   source-dir: path to template repo (defaults to this script's repo root)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${1:-$(cd "$SCRIPT_DIR/../../../.." && pwd)}"

pass=0; fail=0
ok()   { echo "  ✅  $1"; pass=$((pass+1)); }
fail() { echo "  ❌  $1"; fail=$((fail+1)); }

echo ""
echo "=== HOOKS SMOKE TEST ==="
echo "    source: $SOURCE_DIR"
echo ""

# ── 1. Install into isolated HOME ────────────────────────────────────────────
TH=$(mktemp -d)
trap 'rm -rf "$TH"' EXIT
mkdir -p "$TH/.claude/agents" "$TH/.claude/skills/create-agent" "$TH/.claude/hooks"
echo "0.0.1" > "$TH/.claude/.infiniteleverage-version"

echo "[ 1. install-hooks.sh ]"
HOME="$TH" bash "$SOURCE_DIR/setup-skills/infiniteleverage-patch/scripts/install-hooks.sh" "$SOURCE_DIR" >/dev/null 2>&1 \
  && ok "install-hooks.sh exited 0" || fail "install-hooks.sh failed"

# ── 2. Wiring correctness ─────────────────────────────────────────────────────
echo ""
echo "[ 2. Wiring correctness ]"
SETTINGS="$TH/.claude/settings.local.json"
check_wired() {
  local event="$1" expected="$2"
  python3 -c "
import json, sys
s = json.load(open('$SETTINGS'))
found = any(
    '$expected' in h.get('command','')
    for entry in s.get('hooks',{}).get('$event',[])
    for h in entry.get('hooks',[])
)
sys.exit(0 if found else 1)
" 2>/dev/null && ok "$event → $expected" || fail "$event not wired to $expected"
}
check_wired "SessionStart"   "session-start"
check_wired "Stop"           "session-telemetry-stop"
check_wired "SessionEnd"     "session-telemetry-end"
check_wired "PreToolUse"     "pre-bash"
check_wired "UserPromptSubmit" "prompt-submit"

# ── 3. session-start delivered ────────────────────────────────────────────────
echo ""
echo "[ 3. session-start delivered ]"
[ -x "$TH/.claude/hooks/session-start" ] \
  && ok "session-start exists + executable" || fail "session-start missing/not executable"
grep -q "IL_RELEASES_API" "$TH/.claude/hooks/session-start" 2>/dev/null \
  && ok "session-start uses Releases API (not stale VERSION file)" || fail "session-start missing IL_RELEASES_API"
grep -q "_il_newer" "$TH/.claude/hooks/session-start" 2>/dev/null \
  && ok "session-start has strictly-newer gate" || fail "session-start missing strictly-newer gate"

# ── 4. il_telemetry capture writes to outbox ─────────────────────────────────
echo ""
echo "[ 4. capture → outbox ]"
OUTBOX="$TH/.claude/.il-telemetry/outbox"
FAKE_TRANSCRIPT="$TH/fake-session.jsonl"
# Minimal transcript that capture_session can parse (assistant message with usage)
printf '{"type":"assistant","message":{"usage":{"input_tokens":100,"output_tokens":50}},"timestamp":"2026-01-01T00:00:00Z"}\n' > "$FAKE_TRANSCRIPT"

PYTHONPATH="$SOURCE_DIR/plugin-staging/hooks" python3 - <<PYEOF
import json, os, sys
os.chdir("$TH")
sys.path.insert(0, "$SOURCE_DIR/plugin-staging/hooks")
from il_telemetry.outbox import write_record
from pathlib import Path
outbox = Path("$OUTBOX")
write_record(outbox, {
    "session_id": "smoke-test",
    "repo_full_name": "smoke/test",
    "author_email": "test@test.com",
    "github_login": "smoke-tester",
    "claude_tokens": 150,
    "active_minutes": 1,
    "started_at": "2026-01-01T00:00:00+00:00",
    "ended_at": "2026-01-01T00:01:00+00:00",
    "client_slug": "smoke",
    "project_slug": "test",
})
print("written")
PYEOF
[ -f "$OUTBOX/smoke-test.json" ] \
  && ok "outbox record written (smoke-test.json)" || fail "outbox record not written"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "========================="
total=$((pass+fail))
if [ "$fail" -eq 0 ]; then
  echo "✅  All $total checks passed — hook chain is correctly installed and wired"
else
  echo "❌  $fail/$total checks failed — fix before shipping"
fi
echo ""
exit $fail
