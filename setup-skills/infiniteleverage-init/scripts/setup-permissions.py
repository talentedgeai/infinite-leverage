#!/usr/bin/env python3
"""
Write ~/.claude/settings.local.json with required permissions.
Preserves existing content — only adds missing permissions.
"""
import json, os

path = os.path.expanduser("~/.claude/settings.local.json")
settings = {}
if os.path.exists(path):
    with open(path) as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            settings = {}

perms = settings.setdefault("permissions", {})
allow = perms.setdefault("allow", [])

required = [
    "Bash(*)", "WebFetch", "Skill(*)",
    "mcp__supabase__authenticate",
    "mcp__supabase__complete_authentication",
]

# Bash(*) always goes first
allow = [p for p in allow if p != "Bash(*)"]
existing = set(allow)
added = [p for p in required if p not in existing and p != "Bash(*)"]
allow = ["Bash(*)", *allow, *added]

perms["allow"] = allow
perms["defaultMode"] = "acceptEdits"

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"✅ Permissions set. Allow list: {allow}")
