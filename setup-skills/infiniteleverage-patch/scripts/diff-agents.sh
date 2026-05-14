#!/usr/bin/env bash
# Compares universal agent templates vs installed agents and prints a structured diff report.
# Usage: diff-agents.sh [source-dir]
#   source-dir: path to templates (defaults to bundled agents/ in skill dir)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="${1:-$SCRIPT_DIR/../agents}"
INSTALLED_DIR="$HOME/.claude/agents"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "ERROR: template source not found at $TEMPLATE_DIR" >&2
  exit 1
fi

if [ ! -d "$INSTALLED_DIR" ]; then
  echo "ERROR: ~/.claude/agents/ does not exist on this machine" >&2
  exit 1
fi

new=()
modified=()
removed=()
unchanged=()

# Check template agents against installed
for tmpl_file in "$TEMPLATE_DIR"/*.md; do
  [ -f "$tmpl_file" ] || continue
  name=$(basename "$tmpl_file")
  installed_file="$INSTALLED_DIR/$name"

  if [ ! -f "$installed_file" ]; then
    new+=("$name")
  elif ! diff -q "$tmpl_file" "$installed_file" > /dev/null 2>&1; then
    modified+=("$name")
  else
    unchanged+=("$name")
  fi
done

# Check installed agents not in template
for inst_file in "$INSTALLED_DIR"/*.md; do
  [ -f "$inst_file" ] || continue
  name=$(basename "$inst_file")
  if [ ! -f "$TEMPLATE_DIR/$name" ]; then
    removed+=("$name")
  fi
done

echo "=== AGENT DIFF REPORT ==="
echo ""

if [ ${#new[@]} -gt 0 ]; then
  echo "NEW (in template, not installed):"
  for f in "${new[@]}"; do echo "  + $f"; done
  echo ""
fi

if [ ${#modified[@]} -gt 0 ]; then
  echo "MODIFIED (content differs):"
  for f in "${modified[@]}"; do echo "  ~ $f"; done
  echo ""
  # Show inline summary of what changed per file
  for f in "${modified[@]}"; do
    echo "  --- diff: $f ---"
    diff --unified=2 "$INSTALLED_DIR/$f" "$TEMPLATE_DIR/$f" | grep -E "^[+-]" | grep -v "^[+-]{3}" | head -20
    echo ""
  done
fi

if [ ${#removed[@]} -gt 0 ]; then
  echo "REMOVED (installed but not in template):"
  for f in "${removed[@]}"; do echo "  - $f"; done
  echo ""
fi

if [ ${#unchanged[@]} -gt 0 ]; then
  echo "UNCHANGED:"
  echo "  $(IFS=' '; echo "= ${unchanged[*]}" | sed 's/ /  = /g')"
  echo ""
fi

total_changes=$(( ${#new[@]} + ${#modified[@]} + ${#removed[@]} ))
echo "=== SUMMARY: $total_changes change(s) — ${#new[@]} new · ${#modified[@]} modified · ${#removed[@]} removed ==="
exit 0
