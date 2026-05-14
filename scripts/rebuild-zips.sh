#!/usr/bin/env bash
# Rebuilds all 3 bootstrap skill zips with the latest agent templates.
# Run from repo root after updating .claude/agents/*.md.
#
# Usage: ./scripts/rebuild-zips.sh
#   Output: skills/<skill>.zip for each of the 3 bootstrap skills

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_SRC="$REPO_ROOT/.claude/agents"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DIR="$REPO_ROOT/setup-skills"

for skill in infiniteleverage-init infiniteleverage-onboard infiniteleverage-patch; do
  SKILL_DIR="$SKILLS_DIR/$skill"
  echo "→ Syncing canonical agents to $skill/agents/..."
  cp "$AGENTS_SRC"/*.md "$SKILL_DIR/agents/"
  echo "→ Syncing canonical agent skills to $skill/.claude/skills/..."
  mkdir -p "$SKILL_DIR/.claude/skills"
  cp -r "$SKILLS_SRC"/* "$SKILL_DIR/.claude/skills/"
  echo "→ Rebuilding $skill.zip..."
  cd "$SKILLS_DIR"
  rm -f "$skill.zip"
  zip -r "$skill.zip" "$skill/" -x "*.DS_Store" > /dev/null
  echo "   Done: $(ls -lh "$skill.zip" | awk '{print $5}')"
done

echo ""
echo "✅ All 3 zips rebuilt at:"
for f in "$SKILLS_DIR"/*.zip; do
  echo "   $f"
done
