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

# ── Telemetry hooks (from plugin-staging/hooks) ───────────────────────────────
# The il_telemetry package + Stop/SessionEnd wrappers live in plugin-staging/hooks
# (not the top-level hooks/ dir) and include a DIRECTORY the file-only loop above
# skips. Copy them explicitly so effort tracking is actually delivered + registered.
PS_HOOKS="$SOURCE_DIR/plugin-staging/hooks"
if [[ -d "$PS_HOOKS/il_telemetry" ]]; then
  rm -rf "$HOOKS_DEST/il_telemetry"
  cp -r "$PS_HOOKS/il_telemetry" "$HOOKS_DEST/il_telemetry"
  for w in session-telemetry-stop session-telemetry-end; do
    if [[ -f "$PS_HOOKS/$w" ]]; then cp "$PS_HOOKS/$w" "$HOOKS_DEST/$w"; chmod +x "$HOOKS_DEST/$w"; fi
  done
  echo "  + installed telemetry hooks: il_telemetry/, session-telemetry-stop, session-telemetry-end"
fi

# ── Core SessionStart hook (makes session-start self-updating) ────────────────
# session-start lives in plugin-staging/hooks (not the top-level hooks/ dir), so the
# file-loop above skips it. Copy it here so /infiniteleverage-patch delivers it AND the
# auto-update (Stage 2 of session-start calls THIS script) can refresh session-start
# itself. Write-then-atomic-mv: the auto-update runs WHILE ~/.claude/hooks/session-start
# is executing — never overwrite it in place, or a half-written file could corrupt the run.
if [[ -f "$PS_HOOKS/session-start" ]]; then
  _ss_tmp="$HOOKS_DEST/.session-start.tmp.$$"
  if cp "$PS_HOOKS/session-start" "$_ss_tmp" 2>/dev/null; then
    chmod +x "$_ss_tmp"
    mv -f "$_ss_tmp" "$HOOKS_DEST/session-start"
    echo "  + installed core hook: session-start"
  else
    rm -f "$_ss_tmp" 2>/dev/null || true
  fi
fi

# ── Prune obsolete hooks (self-heal stale machines) ──────────────────────────
# Add new names to OBSOLETE_HOOKS as old scripts are retired.

OBSOLETE_HOOKS=(session-ingest-start.py session-ingest-end.py)

for obs in "${OBSOLETE_HOOKS[@]}"; do
  stale="$HOOKS_DEST/$obs"
  if [[ -f "$stale" ]]; then
    rm -f "$stale"
    echo "  - pruned obsolete hook: $obs"
  fi
done

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
    ("PreToolUse",        "pre-bash",                "Bash"),
    ("UserPromptSubmit",  "prompt-submit",           ""),
    ("Stop",              "session-telemetry-stop",  ""),
    ("SessionEnd",        "session-telemetry-end",   ""),
    ("SessionStart",      "session-telemetry-end",   ""),
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

# ── De-register obsolete session-ingest entries from settings.local.json ─────
python3 - "$SETTINGS" <<'PYEOF2'
import sys, json, os

settings_path = sys.argv[1]
if not os.path.exists(settings_path):
    sys.exit(0)

with open(settings_path) as f:
    try:
        settings = json.load(f)
    except json.JSONDecodeError:
        print(f"  WARNING: {settings_path} is not valid JSON — cannot prune session-ingest entries")
        sys.exit(0)

hooks_cfg = settings.get("hooks", {})
removed_events = []

for event in list(hooks_cfg.keys()):
    entries = hooks_cfg[event]
    cleaned = []
    for entry in entries:
        filtered_hooks = [
            h for h in entry.get("hooks", [])
            if "session-ingest" not in h.get("command", "")
        ]
        if filtered_hooks:
            entry = dict(entry)
            entry["hooks"] = filtered_hooks
            cleaned.append(entry)
        # If entry had hooks but all were session-ingest, drop the whole entry
    if len(cleaned) != len(entries):
        removed_events.append(event)
    if cleaned:
        hooks_cfg[event] = cleaned
    else:
        # Drop now-empty event array
        del hooks_cfg[event]

if removed_events:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"  - de-registered session-ingest entries from: {', '.join(removed_events)}")
else:
    print("  = no session-ingest registrations found in settings.local.json")
PYEOF2
