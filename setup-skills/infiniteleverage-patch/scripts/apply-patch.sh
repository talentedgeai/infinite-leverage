#!/usr/bin/env bash
# Applies agent, skill, and rule updates from the canonical template source.
#
# Phase 1: copies agent .md files from .claude/agents/ → ~/.claude/agents/
# Phase 2: copies skill directories from .claude/skills/ → ~/.claude/skills/
# Phase 3: copies rule .md files from .claude/rules/ → ~/.claude/rules/
#
# Usage: apply-patch.sh [mode: full|no-remove]
#   full      — adds + updates agents; removes deprecated agents (default)
#   no-remove — adds + updates only; never removes agents

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MODE="${1:-full}"

# ── Phase 1: Agents ───────────────────────────────────────────────────────────

AGENTS_SRC="$REPO_ROOT/.claude/agents"
AGENTS_DEST="$HOME/.claude/agents"

if [ ! -d "$AGENTS_SRC" ]; then
  echo "ERROR: agent source not found at $AGENTS_SRC" >&2
  exit 1
fi

mkdir -p "$AGENTS_DEST"

added=0
updated=0
removed=0
errors=0

for tmpl_file in "$AGENTS_SRC"/*.md; do
  [ -f "$tmpl_file" ] || continue
  name=$(basename "$tmpl_file")
  dest_file="$AGENTS_DEST/$name"

  if [ ! -f "$dest_file" ]; then
    if cp "$tmpl_file" "$dest_file"; then
      echo "  + added:   $name"
      added=$((added + 1))
    else
      echo "  ERROR: failed to copy $name" >&2
      errors=$((errors + 1))
    fi
  elif ! diff -q "$tmpl_file" "$dest_file" > /dev/null 2>&1; then
    if cp "$tmpl_file" "$dest_file"; then
      echo "  ~ updated: $name"
      updated=$((updated + 1))
    else
      echo "  ERROR: failed to update $name" >&2
      errors=$((errors + 1))
    fi
  fi
done

if [ "$MODE" = "full" ]; then
  for inst_file in "$AGENTS_DEST"/*.md; do
    [ -f "$inst_file" ] || continue
    name=$(basename "$inst_file")
    if [ ! -f "$AGENTS_SRC/$name" ]; then
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
echo "=== AGENTS: $added added · $updated updated · $removed removed ==="

# ── Phase 2: Skills ───────────────────────────────────────────────────────────

SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DEST="$HOME/.claude/skills"

skills_added=0
skills_updated=0
skills_errors=0

if [ -d "$SKILLS_SRC" ]; then
  mkdir -p "$SKILLS_DEST"

  for skill_dir in "$SKILLS_SRC"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    dest_skill="$SKILLS_DEST/$skill_name"

    if [ ! -d "$dest_skill" ]; then
      if cp -r "$skill_dir" "$dest_skill"; then
        echo "  + added skill:   $skill_name"
        skills_added=$((skills_added + 1))
      else
        echo "  ERROR: failed to copy skill $skill_name" >&2
        skills_errors=$((skills_errors + 1))
      fi
    elif ! diff -rq "$skill_dir" "$dest_skill" > /dev/null 2>&1; then
      if cp -r "$skill_dir" "$SKILLS_DEST/"; then
        echo "  ~ updated skill: $skill_name"
        skills_updated=$((skills_updated + 1))
      else
        echo "  ERROR: failed to update skill $skill_name" >&2
        skills_errors=$((skills_errors + 1))
      fi
    fi
  done

  # Remove deprecated skills that have been renamed or removed from the template
  DEPRECATED_SKILLS=("create-local-task")
  skills_removed=0
  for deprecated in "${DEPRECATED_SKILLS[@]}"; do
    deprecated_path="$SKILLS_DEST/$deprecated"
    if [ -d "$deprecated_path" ]; then
      if rm -rf "$deprecated_path"; then
        echo "  - removed deprecated skill: $deprecated"
        skills_removed=$((skills_removed + 1))
      else
        echo "  ERROR: failed to remove deprecated skill $deprecated" >&2
        skills_errors=$((skills_errors + 1))
      fi
    fi
  done

  echo ""
  echo "=== SKILLS: $skills_added added · $skills_updated updated · $skills_removed removed ==="
fi

# ── Phase 3: Rules ────────────────────────────────────────────────────────────

RULES_SRC="$REPO_ROOT/.claude/rules"
RULES_DEST="$HOME/.claude/rules"

rules_added=0
rules_updated=0
rules_errors=0

if [ -d "$RULES_SRC" ]; then
  mkdir -p "$RULES_DEST"

  for rule_file in "$RULES_SRC"/*.md; do
    [ -f "$rule_file" ] || continue
    rule_name=$(basename "$rule_file")
    dest_rule="$RULES_DEST/$rule_name"

    if [ ! -f "$dest_rule" ]; then
      if cp "$rule_file" "$dest_rule"; then
        echo "  + added rule:   $rule_name"
        rules_added=$((rules_added + 1))
      else
        echo "  ERROR: failed to copy rule $rule_name" >&2
        rules_errors=$((rules_errors + 1))
      fi
    elif ! diff -q "$rule_file" "$dest_rule" > /dev/null 2>&1; then
      if cp "$rule_file" "$dest_rule"; then
        echo "  ~ updated rule: $rule_name"
        rules_updated=$((rules_updated + 1))
      else
        echo "  ERROR: failed to update rule $rule_name" >&2
        rules_errors=$((rules_errors + 1))
      fi
    fi
  done

  echo ""
  echo "=== RULES: $rules_added added · $rules_updated updated ==="
fi

# ── Phase 4: Refresh AGENT-DELEGATION block in CLAUDE.md files ───────────────

INJECTOR="$HOME/.claude/skills/infiniteleverage-patch/scripts/inject-agent-delegation.sh"
if [ -x "$INJECTOR" ]; then
  echo ""
  echo "→ Refreshing AGENT-DELEGATION block in CLAUDE.md files…"
  delegation_touched=0
  if [ -f "$HOME/.claude/CLAUDE.md" ]; then
    bash "$INJECTOR" "$HOME/.claude/CLAUDE.md" && delegation_touched=$((delegation_touched + 1))
  fi
  if [ -d "$HOME/code-projects" ]; then
    shopt -s nullglob
    for proj in "$HOME/code-projects"/*/; do
      proj_claude="${proj}CLAUDE.md"
      if [ -f "$proj_claude" ]; then
        bash "$INJECTOR" "$proj_claude" && delegation_touched=$((delegation_touched + 1))
      fi
    done
    shopt -u nullglob
  fi
  echo "   AGENT-DELEGATION refreshed in $delegation_touched CLAUDE.md file(s)"
fi

# ── Phase 5: Hooks ───────────────────────────────────────────────────────────

INSTALL_HOOKS="$HOME/.claude/skills/infiniteleverage-patch/scripts/install-hooks.sh"
echo ""
echo "→ Installing hooks…"
if [[ -x "$INSTALL_HOOKS" ]]; then
  bash "$INSTALL_HOOKS" "$REPO_ROOT"
else
  echo "  ⚠️  install-hooks.sh not found at $INSTALL_HOOKS — skipping (run patch again after skills sync)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "=== PATCH COMPLETE ==="

total_errors=$((errors + skills_errors + rules_errors))
if [ "$total_errors" -gt 0 ]; then
  echo "WARNING: $total_errors error(s) occurred — check output above"
  exit 1
fi

exit 0
