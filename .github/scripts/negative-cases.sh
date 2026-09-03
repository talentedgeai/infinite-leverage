#!/usr/bin/env bash
# negative-cases.sh — Run 8 of docs/RELEASE-CHECKLIST.md, executed instead of eyeballed.
# Each case runs the skill's own bash block, extracted from SKILL.md as written, under
# a fault (missing tool, unauthenticated gh, no network) and asserts the skill stops
# with the message the checklist promises.
#
# Usage: bash .github/scripts/negative-cases.sh
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PROJECT="$ROOT/plugin/skills/il-project/SKILL.md"
ADOPT="$ROOT/plugin/skills/il-adopt/SKILL.md"
DOCTOR="$ROOT/plugin/skills/il-doctor/scripts/doctor.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILS=0

# step <file> <n> <next> — the bash blocks under "### Step <n> " up to "### Step <next> "
step() {
  awk -v s="### Step $2 " -v n="### Step $3 " '
    index($0, s) == 1 { on = 1; next }
    index($0, n) == 1 { on = 0 }
    on && /^```bash/ { code = 1; next }
    on && /^```/     { code = 0 }
    on && code       { print }' "$1"
}
expect() {  # expect <case> <yes|no> <regex>
  local case=$1 want=$2 re=$3 got=no
  grep -qE -- "$re" "$TMP/$case.out" && got=yes
  if [ "$got" = "$want" ]; then
    printf '  ok    %-28s %s /%s/\n' "$case" "$want" "$re"
  else
    printf '  FAIL  %-28s expected %s /%s/\n' "$case" "$want" "$re"
    sed 's/^/        | /' "$TMP/$case.out"; FAILS=$((FAILS + 1))
  fi
}
# OFFLINE: rewrite every github.com URL to a closed local port for this process only.
OFFLINE=(env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="url.http://127.0.0.1:9/.insteadOf" GIT_CONFIG_VALUE_0="https://github.com/")

echo "negative cases — $ROOT"

# ── 8a. /il-project against an existing directory refuses, and says why ───────
mkdir -p "$TMP/exists"
( export TARGET="$TMP/exists"; bash -c "$(step "$PROJECT" 2 3 | sed '/^TARGET=/d')" ) > "$TMP/8a-exists.out" 2>&1
echo "exit=$?" >> "$TMP/8a-exists.out"
expect 8a-exists yes 'exists — pick a different slug'
expect 8a-exists yes 'exit=1$'

# ── 8b. gh unauthenticated: step 1 stops and tells the operator to log in themselves
mkdir -p "$TMP/bin"
printf '#!/bin/sh\n[ "$1 $2" = "auth status" ] && exit 1\nexit 0\n' > "$TMP/bin/gh"; chmod +x "$TMP/bin/gh"
for pair in "project:$PROJECT" "adopt:$ADOPT"; do
  name=${pair%%:*}; file=${pair#*:}
  ( export PATH="$TMP/bin:$PATH"; bash -c "$(step "$file" 1 2)" ) > "$TMP/8b-$name-noauth.out" 2>&1
  echo "exit=$?" >> "$TMP/8b-$name-noauth.out"
  expect "8b-$name-noauth" yes 'gh is not authenticated'
  expect "8b-$name-noauth" yes "operator must run 'gh auth login' themselves"
  expect "8b-$name-noauth" yes 'exit=1$'
  expect "8b-$name-noauth" no  'prerequisites OK'
done

# ── 8b-ii. a missing tool is named up front and routed to /il-doctor ──────────
# PATH holding every prerequisite except rsync — the one that used to surface
# minutes later, halfway through step 9.
mkdir -p "$TMP/bin2"
for t in git gh perl node npm npx; do
  real=$(command -v "$t" 2>/dev/null) && ln -s "$real" "$TMP/bin2/$t"
done
CODE=$(step "$PROJECT" 1 2)   # extract first — the stripped PATH has no awk
( export PATH="$TMP/bin2"; /bin/bash -c "$CODE" ) > "$TMP/8b-missing-rsync.out" 2>&1
echo "exit=$?" >> "$TMP/8b-missing-rsync.out"
expect 8b-missing-rsync yes 'missing required tools:.* rsync'
expect 8b-missing-rsync yes 'run /il-doctor'
expect 8b-missing-rsync yes 'exit=1$'

# ── 8c. offline, /il-doctor degrades instead of failing ──────────────────────
( cd "$TMP" && CLAUDE_PLUGIN_ROOT="$ROOT/plugin" "${OFFLINE[@]}" bash "$DOCTOR" ) > "$TMP/8c-doctor-offline.out" 2>&1
echo "exit=$?" >> "$TMP/8c-doctor-offline.out"
expect 8c-doctor-offline yes 'PASS  installed plugin'
expect 8c-doctor-offline yes 'could not reach the marketplace'
expect 8c-doctor-offline no  'plugin up to date'
expect 8c-doctor-offline yes 'exit=0$'

# ── 8d. offline, the pinning step stops with a network message — not "untagged"
for pair in "project:$PROJECT:3:4" "adopt:$ADOPT:4:5"; do
  IFS=: read -r name file n next <<< "$pair"
  ( export CLAUDE_PLUGIN_ROOT="$ROOT/plugin" TARGET="$TMP/never-written"
    "${OFFLINE[@]}" bash -c "$(step "$file" "$n" "$next")" ) > "$TMP/8d-$name-offline.out" 2>&1
  echo "exit=$?" >> "$TMP/8d-$name-offline.out"
  expect "8d-$name-offline" yes 'cannot reach github.com'
  expect "8d-$name-offline" no  'was not tagged'
  expect "8d-$name-offline" yes 'exit=1$'
  [ -e "$TMP/never-written" ] && { echo "  FAIL  8d-$name-offline wrote to TARGET while offline"; FAILS=$((FAILS + 1)); }
done

echo
if [ "$FAILS" -eq 0 ]; then
  echo "negative cases: all assertions passed"
else
  echo "negative cases: $FAILS assertion(s) failed"; exit 1
fi
