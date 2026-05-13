#!/usr/bin/env bash
# Rebuilds all 3 bootstrap skill zips with the latest agent templates.
# Run this from the repo root after updating agents/*.md.
#
# Usage: ./scripts/rebuild-zips.sh <path-to-skills-dir>
#   skills-dir: the directory containing the 3 skill subdirs (init, onboard, patch)

set -euo pipefail

SKILLS_DIR="${1:-}"
if [ -z "$SKILLS_DIR" ] || [ ! -d "$SKILLS_DIR" ]; then
  echo "Usage: $0 <path-to-skills-dir>"
  echo "  skills-dir must contain: infiniteleverage-init/ infiniteleverage-onboard/ infiniteleverage-patch/"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_SRC="$REPO_ROOT/agents"

for skill in infiniteleverage-init infiniteleverage-onboard infiniteleverage-patch; do
  SKILL_DIR="$SKILLS_DIR/$skill"
  if [ ! -d "$SKILL_DIR" ]; then
    echo "⚠️  Skipping $skill — not found at $SKILL_DIR"
    continue
  fi
  echo "→ Syncing agents to $skill..."
  cp "$AGENTS_SRC"/*.md "$SKILL_DIR/agents/"
  echo "→ Rebuilding $skill.zip..."
  cd "$SKILLS_DIR"
  rm -f "$skill.zip"
  zip -r "$skill.zip" "$skill/" -x "*.DS_Store" > /dev/null
  echo "   Done: $(ls -lh "$skill.zip" | awk '{print $5}')"
done

echo ""
echo "✅ All 3 zips rebuilt. Ready to deploy."
