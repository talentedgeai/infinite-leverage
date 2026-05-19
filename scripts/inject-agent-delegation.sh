#!/usr/bin/env bash
# Inject (or refresh) the AGENT-DELEGATION block in a CLAUDE.md file.
#
# Usage:
#   ./inject-agent-delegation.sh <path-to-CLAUDE.md>
#
# Behavior:
#   - If the file is missing → exit 1 with a clear message
#   - If the BEGIN/END markers exist → replace the block in place
#   - If the markers do not exist → append the block at the end of the file
#
# The canonical block content lives in scripts/agent-delegation-block.md
# (sibling to this script). Other skills (init, onboard, patch, project) call
# this script — single source of truth, no duplication.

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path-to-CLAUDE.md>"
  exit 1
fi

TARGET="$1"
if [ ! -f "$TARGET" ]; then
  echo "❌ CLAUDE.md not found: $TARGET"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BLOCK_FILE="$SCRIPT_DIR/agent-delegation-block.md"
if [ ! -f "$BLOCK_FILE" ]; then
  echo "❌ Block content file not found: $BLOCK_FILE"
  exit 1
fi

if grep -q "BEGIN: AGENT-DELEGATION" "$TARGET" 2>/dev/null; then
  # Replace existing block in place. Pass the block file path via env so perl
  # can slurp it without quoting headaches.
  BLOCK_FILE="$BLOCK_FILE" perl -i -0pe '
    BEGIN {
      open(my $f, "<", $ENV{BLOCK_FILE}) or die "open $ENV{BLOCK_FILE}: $!";
      local $/;
      $block = <$f>;
      $block =~ s/\s+\z//;
    }
    s{<!-- BEGIN: AGENT-DELEGATION.*?<!-- END: AGENT-DELEGATION -->}{$block}s;
  ' "$TARGET"
  echo "✅ Refreshed AGENT-DELEGATION block in $TARGET"
else
  # Append. Use a blank-line separator only if the file is non-empty and does
  # not already end with a newline-terminated blank line.
  if [ -s "$TARGET" ]; then
    printf '\n' >> "$TARGET"
  fi
  cat "$BLOCK_FILE" >> "$TARGET"
  echo "✅ Appended AGENT-DELEGATION block to $TARGET"
fi
