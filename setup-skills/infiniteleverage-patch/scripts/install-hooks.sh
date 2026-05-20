#!/usr/bin/env bash
# Installs Infinite Leverage hooks from a canonical template source dir.
#
# Copies hook scripts to ~/.claude/hooks/ and idempotently wires them into
# ~/.claude/settings.local.json as PreToolUse (Bash guardrails) and
# UserPromptSubmit (agent routing hints) hooks.
#
# Usage: install-hooks.sh <source_dir>
#   source_dir — path to cloned infiniteleverage-8-agents-template repo

set -euo pipefail

SOURCE_DIR="${1:-}"
if [[ -z "$SOURCE_DIR" || ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: source_dir not provided or not found at '$SOURCE_DIR'" >&2
  exit 1
fi

HOOKS_SRC="$SOURCE_DIR/hooks"
HOOKS_DEST="$HOME/.claude/hooks"
SETTINGS="$HOME/.claude/settings.local.json"

if [[ ! -d "$HOOKS_SRC" ]]; then
  echo "  ⚠️  hooks/ directory not found in source — skipping hook installation"
  exit 0
fi

# ── Copy hook scripts ─────────────────────────────────────────────────────────

mkdir -p "$HOOKS_DEST"

installed=()
updated=()

for hook_file in "$HOOKS_SRC"/*; do
  [[ -f "$hook_file" ]] || continue
  hook_name="$(basename "$hook_file")"
  dest="$HOOKS_DEST/$hook_name"
  if [[ ! -f "$dest" ]]; then
    cp "$hook_file" "$dest"
    chmod +x "$dest"
    installed+=("$hook_name")
  elif ! diff -q "$hook_file" "$dest" > /dev/null 2>&1; then
    cp "$hook_file" "$dest"
    chmod +x "$dest"
    updated+=("$hook_name")
  fi
done

[[ ${#installed[@]} -gt 0 ]] && echo "  + installed hooks: ${installed[*]}"
[[ ${#updated[@]} -gt 0 ]]   && echo "  ~ updated hooks:   ${updated[*]}"
[[ ${#installed[@]} -eq 0 && ${#updated[@]} -eq 0 ]] && echo "  = hooks already up to date"

# ── Wire into settings.local.json ────────────────────────────────────────────

python3 - "$SETTINGS" "$HOOKS_DEST" <<'PYEOF'
import sys, json, os

settings_path = sys.argv[1]
hooks_dest    = sys.argv[2]

settings = {}
if os.path.exists(settings_path):
    with open(settings_path) as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            print(f"  WARNING: {settings_path} is not valid JSON — cannot wire hooks")
            sys.exit(0)

hooks_cfg = settings.setdefault("hooks", {})

# Each entry: (event_name, hook_filename, matcher)
HOOK_DEFS = [
    ("PreToolUse",        "pre-bash",       "Bash"),
    ("UserPromptSubmit",  "prompt-submit",  ""),
]

wired = []

for event, filename, matcher in HOOK_DEFS:
    hook_path = os.path.join(hooks_dest, filename)
    if not os.path.exists(hook_path):
        print(f"  WARNING: {filename} not found at {hook_path} — skipping {event} wiring")
        continue

    existing = hooks_cfg.get(event, [])
    already_wired = any(
        any(h.get("command") == hook_path for h in entry.get("hooks", []))
        for entry in existing
    )
    if not already_wired:
        hooks_cfg.setdefault(event, []).append({
            "matcher": matcher,
            "hooks": [{"type": "command", "command": hook_path}]
        })
        wired.append(event)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

if wired:
    print(f"  + wired into settings.local.json: {', '.join(wired)}")
else:
    print("  = hook entries already present in settings.local.json")
PYEOF
