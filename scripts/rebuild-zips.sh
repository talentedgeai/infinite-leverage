#!/usr/bin/env bash
# Rebuilds all bootstrap skill zips from their current folder contents.
# Skills fetch agents and .claude/ from the canonical template repo at runtime —
# nothing is pre-bundled here.
#
# Usage: ./scripts/rebuild-zips.sh
#   Output: setup-skills/<skill>.zip for each bootstrap skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/setup-skills"

ALL_SKILLS=(infiniteleverage-init infiniteleverage-onboard infiniteleverage-patch infiniteleverage-project)

for skill in "${ALL_SKILLS[@]}"; do
  SKILL_DIR="$SKILLS_DIR/$skill"
  if [ ! -d "$SKILL_DIR" ]; then
    echo "→ Skipping $skill (directory not found)"
    continue
  fi
  echo "→ Rebuilding $skill.zip..."
  if [ -d "$SKILL_DIR/scripts" ]; then
    chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true
  fi
  cd "$SKILLS_DIR"
  rm -f "$skill.zip"
  zip -r "$skill.zip" "$skill/" -x "*.DS_Store" > /dev/null
  echo "   Done: $(ls -lh "$skill.zip" | awk '{print $5}')"
done

# Sync setup skills to plugin repo (if it exists as a sibling directory)
PLUGIN_REPO="$REPO_ROOT/../infiniteleverage-plugin"
if [ -d "$PLUGIN_REPO" ]; then
  echo "→ Syncing setup skills to infiniteleverage-plugin/skills/..."
  for skill in "${ALL_SKILLS[@]}"; do
    SRC="$SKILLS_DIR/$skill"
    DEST="$PLUGIN_REPO/skills/$skill"
    if [ -d "$SRC" ]; then
      rm -rf "$DEST"
      cp -r "$SRC" "$DEST"
      echo "   Synced: $skill"
    fi
  done
  echo "   Plugin skills sync complete."
else
  echo "→ infiniteleverage-plugin not found at $PLUGIN_REPO — skipping plugin sync."
fi

echo ""
echo "✅ All zips rebuilt at:"
for f in "$SKILLS_DIR"/*.zip; do
  echo "   $f"
done
