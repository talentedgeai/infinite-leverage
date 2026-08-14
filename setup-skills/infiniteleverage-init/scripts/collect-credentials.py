#!/usr/bin/env python3
"""
Just-in-time, merge-safe credential collector for Infinite Leverage setup.

Replaces the unintuitive "go grab these keys and paste them into a file" wall of
text. Claude collects each value conversationally (only when the step that needs
it runs), then calls this script to write it. Keys are grouped so we ask ONLY for
what the current step needs.

Two modes:

  --check GROUP|KEY,KEY   Report which keys are missing or empty (so Claude knows
                          what to ask the user for). Prints one line per key:
                          "KEY: present | empty | missing". Exit 0 if all present
                          and non-empty, 1 otherwise.

  --set KEY=VALUE ...     Merge keys into the target file WITHOUT clobbering existing
                          non-empty keys or any other content (comments, blank lines,
                          unrelated keys are preserved). An existing non-empty key is
                          only overwritten with --force.

Target defaults to ~/.claude/.env. Pass --target for a project .env.local.

Examples:
  collect-credentials.py --check core
  collect-credentials.py --set SUPABASE_SECRET_KEY=sb_secret_...
  collect-credentials.py --target website/.env.local --set NEXT_PUBLIC_SUPABASE_URL=https://...
"""
import argparse
import os
import sys

# Key groups, ordered by WHEN they are needed in the flow.
# core = needed to stand up the first project.
GROUPS = {
    "core": [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_SECRET_KEY",
    ],
    # operator-only Supabase admin/MCP keys (legacy names) — usually not on contributor machines
    "supabase-admin": ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"],
}


def resolve_keys(spec):
    """A spec is a group name or a comma-separated list of explicit keys."""
    if spec in GROUPS:
        return list(GROUPS[spec])
    return [k.strip() for k in spec.split(",") if k.strip()]


def parse_env(path):
    """Return (lines, index) where index maps KEY -> line position. Preserves everything."""
    lines = []
    index = {}
    if os.path.exists(path):
        with open(path) as f:
            lines = f.read().splitlines()
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#") or "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if key:
                index[key] = i
    return lines, index


def value_of(lines, index, key):
    if key not in index:
        return None
    return lines[index[key]].split("=", 1)[1].strip()


def do_check(path, keys):
    lines, index = parse_env(path)
    all_ok = True
    for key in keys:
        if key not in index:
            print(f"{key}: missing")
            all_ok = False
        else:
            val = value_of(lines, index, key)
            if val == "":
                print(f"{key}: empty")
                all_ok = False
            else:
                print(f"{key}: present")
    return 0 if all_ok else 1


def do_set(path, pairs, force):
    lines, index = parse_env(path)
    changed, skipped = [], []
    for raw in pairs:
        if "=" not in raw:
            print(f"⚠️  ignoring malformed pair (need KEY=VALUE): {raw}", file=sys.stderr)
            continue
        key, val = raw.split("=", 1)
        key, val = key.strip(), val.strip()
        if key in index:
            existing = value_of(lines, index, key)
            if existing and not force:
                skipped.append(key)
                continue
            lines[index[key]] = f"{key}={val}"
            changed.append(key)
        else:
            lines.append(f"{key}={val}")
            index[key] = len(lines) - 1
            changed.append(key)

    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    # Lock down a secrets file
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

    if changed:
        print(f"✅ wrote {len(changed)} key(s) to {path}: {', '.join(changed)}")
    if skipped:
        print(f"↩️  kept existing non-empty value(s) (use --force to overwrite): {', '.join(skipped)}")
    return 0


def main():
    p = argparse.ArgumentParser(description="Merge-safe, just-in-time credential collector")
    p.add_argument("--target", default=os.path.expanduser("~/.claude/.env"),
                   help="env file to read/write (default ~/.claude/.env)")
    p.add_argument("--check", metavar="GROUP|KEYS",
                   help="report missing/empty keys for a group or comma-list")
    p.add_argument("--set", nargs="+", metavar="KEY=VALUE", dest="set_pairs",
                   help="merge KEY=VALUE pairs (preserves existing content)")
    p.add_argument("--force", action="store_true",
                   help="overwrite existing non-empty keys")
    args = p.parse_args()

    if not args.check and not args.set_pairs:
        p.error("provide --check or --set")

    if args.check:
        return do_check(args.target, resolve_keys(args.check))
    return do_set(args.target, args.set_pairs, args.force)


if __name__ == "__main__":
    sys.exit(main())
