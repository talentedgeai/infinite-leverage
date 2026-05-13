#!/usr/bin/env bash
# Applies agent updates from the source templates to ~/.claude/agents/.
# Usage: apply-patch.sh <source-dir> [mode: full|no-remove]
#   source-dir: path to templates (defaults to bundled agents/ in skill dir)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="${1:-$SCRIPT_DIR/../agents}"
INSTALLED_DIR="$HOME/.claude/agents"
MODE="${2:-full}"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "ERROR: template source not found at $TEMPLATE_DIR" >&2
  exit 1
fi

added=0
updated=0
removed=0
errors=0

# Add new and update modified
for tmpl_file in "$TEMPLATE_DIR"/*.md; do
  [ -f "$tmpl_file" ] || continue
  name=$(basename "$tmpl_file")
  installed_file="$INSTALLED_DIR/$name"

  if [ ! -f "$installed_file" ]; then
    if cp "$tmpl_file" "$installed_file"; then
      echo "  + added:   $name"
      added=$((added + 1))
    else
      echo "  ERROR: failed to copy $name" >&2
      errors=$((errors + 1))
    fi
  elif ! diff -q "$tmpl_file" "$installed_file" > /dev/null 2>&1; then
    if cp "$tmpl_file" "$installed_file"; then
      echo "  ~ updated: $name"
      updated=$((updated + 1))
    else
      echo "  ERROR: failed to update $name" >&2
      errors=$((errors + 1))
    fi
  fi
done

# Remove deprecated agents (full mode only)
if [ "$MODE" = "full" ]; then
  for inst_file in "$INSTALLED_DIR"/*.md; do
    [ -f "$inst_file" ] || continue
    name=$(basename "$inst_file")
    if [ ! -f "$TEMPLATE_DIR/$name" ]; then
      if rm "$inst_file"; then
        echo "  - removed: $name"
        removed=$((removed + 1))
      else
        echo "  ERROR: failed to remove $name" >&2
        errors=$((errors + 1))
      fi
    fi
  done
fi

echo ""
echo "=== PATCH COMPLETE: $added added · $updated updated · $removed removed ==="

if [ "$errors" -gt 0 ]; then
  echo "WARNING: $errors error(s) occurred — check output above"
  exit 1
fi

exit 0
