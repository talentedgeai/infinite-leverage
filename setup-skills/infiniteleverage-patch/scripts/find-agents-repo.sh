#!/usr/bin/env bash
# Locates a local *-agents repo clone.
# Prints the absolute path if found, or NOT_FOUND.

SEARCH_ROOTS=("$HOME/code-projects" "$HOME" "$HOME/Documents" "$HOME/projects" "$HOME/dev")

for root in "${SEARCH_ROOTS[@]}"; do
  if [ -d "$root" ]; then
    # Look for any directory matching *-agents that contains .claude/agents/
    while IFS= read -r candidate; do
      if [ -d "$candidate/.claude/agents" ]; then
        echo "$candidate"
        exit 0
      fi
    done < <(find "$root" -maxdepth 2 -type d -name "*-agents" 2>/dev/null)
  fi
done

echo "NOT_FOUND"
exit 1
