#!/usr/bin/env bash
# Checks git staleness of the agents repo WITHOUT pulling.
# Fetches remote refs, then reports how many commits behind/ahead local is.
# Usage: check-git-staleness.sh <repo-path>

REPO="$1"

if [ -z "$REPO" ] || [ ! -d "$REPO/.git" ]; then
  echo "ERROR: not a git repo: $REPO" >&2
  exit 1
fi

cd "$REPO" || exit 1

echo "Fetching remote refs (no pull)..."
if ! git fetch origin --quiet 2>&1; then
  echo "WARNING: git fetch failed — working from local refs only"
fi

LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse origin/main 2>/dev/null)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✅  Repo is up to date with origin/main"
  exit 0
fi

BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null)
LAST_PULL=$(git log -1 --format="%ar" HEAD 2>/dev/null)

echo ""
echo "=== GIT STALENESS REPORT ==="
echo "  Local HEAD:    $(git log -1 --format='%h %s' HEAD)"
echo "  Remote HEAD:   $(git log -1 --format='%h %s' origin/main)"
echo ""

if [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -gt 0 ]; then
  echo "  Status: ⚠️  DIVERGED — $BEHIND commit(s) behind, $AHEAD commit(s) ahead of origin/main"
  echo "  Action: manual merge required before applying"
  exit 2
elif [ "$BEHIND" -gt 0 ]; then
  echo "  Status: ⚠️  STALE — $BEHIND commit(s) behind origin/main (last local commit: $LAST_PULL)"
  echo ""
  echo "  Commits you are missing:"
  git log HEAD..origin/main --oneline | head -10
  echo "  Action: safe to pull — no local divergence"
  exit 1
elif [ "$AHEAD" -gt 0 ]; then
  echo "  Status: ℹ️  AHEAD — $AHEAD local commit(s) not yet pushed to origin/main"
  echo "  Action: no pull needed"
  exit 0
fi
