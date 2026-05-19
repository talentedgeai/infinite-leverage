#!/usr/bin/env bash
# Rebuilds all bootstrap skill zips with the latest agent templates.
# Run from repo root after updating .claude/agents/*.md.
#
# Usage: ./scripts/rebuild-zips.sh
#   Output: setup-skills/<skill>.zip for each bootstrap skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_SRC="$REPO_ROOT/.claude/agents"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DIR="$REPO_ROOT/setup-skills"

# Skills that bundle the canonical agent definitions (init/onboard/patch use them at setup time)
AGENT_BUNDLED_SKILLS=(infiniteleverage-init infiniteleverage-onboard infiniteleverage-patch)

# Skills that do NOT bundle agents (they fetch agents from the canonical repo at runtime)
STANDALONE_SKILLS=(infiniteleverage-project)

for skill in "${AGENT_BUNDLED_SKILLS[@]}"; do
  SKILL_DIR="$SKILLS_DIR/$skill"
  echo "→ Syncing canonical agents to $skill/agents/..."
  mkdir -p "$SKILL_DIR/agents"
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

for skill in "${STANDALONE_SKILLS[@]}"; do
  SKILL_DIR="$SKILLS_DIR/$skill"
  echo "→ Rebuilding $skill.zip (standalone — no agent bundling)..."
  if [ -d "$SKILL_DIR/scripts" ]; then
    chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true
  fi
  cd "$SKILLS_DIR"
  rm -f "$skill.zip"
  zip -r "$skill.zip" "$skill/" -x "*.DS_Store" > /dev/null
  echo "   Done: $(ls -lh "$skill.zip" | awk '{print $5}')"
done

# Sync setup skills to plugin repo (if it exists as a sibling directory)
PLUGIN_REPO="$(cd "$SCRIPT_DIR/.." && pwd)/../infiniteleverage-plugin"
if [ -d "$PLUGIN_REPO" ]; then
  echo "→ Syncing setup skills to infiniteleverage-plugin/skills/..."
  for skill in "${AGENT_BUNDLED_SKILLS[@]}" "${STANDALONE_SKILLS[@]}"; do
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
