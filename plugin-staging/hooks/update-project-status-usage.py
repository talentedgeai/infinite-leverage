#!/usr/bin/env python3
"""
Update the Claude Usage section of docs/project-status.html.

Tracks human tokens (active hours) and Claude tokens PER CONTRIBUTOR,
accumulated across multiple machines and contributors over time.

Design:
  - Each contributor runs this script after their session.
  - The script reads their ALL-TIME local JSONL stats for this project.
  - It REPLACES (not adds) their entry in the HTML — fully idempotent.
  - The team total = sum of all contributor entries in the HTML.
  - project-status.html (in git) is the accumulation store — no external DB.

Usage:
    python3 ~/.claude/hooks/update-project-status-usage.py [path/to/project-status.html]

If no path given, walks up from CWD looking for docs/project-status.html.
"""
import json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

_PROJECTS = Path.home() / ".claude" / "projects"
_GAP = timedelta(minutes=30)


# ── Contributor identity ──────────────────────────────────────────────────────

def _contributor_id() -> str:
    """Stable contributor ID from git config user.name, fallback to $USER."""
    try:
        name = subprocess.check_output(
            ["git", "config", "user.name"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        if name:
            return name.lower().replace(" ", "-")
    except Exception:
        pass
    return os.environ.get("USER", "unknown")


# ── Local JSONL stats (all-time, no time filter) ──────────────────────────────

def _all_timestamps(project_dir: Path) -> list[datetime]:
    ts_list: list[datetime] = []
    for f in project_dir.glob("*.jsonl"):
        try:
            for line in f.read_text(errors="ignore").splitlines():
                obj = json.loads(line)
                ts_raw = obj.get("timestamp", "")
                if ts_raw:
                    ts_list.append(datetime.fromisoformat(ts_raw.replace("Z", "+00:00")))
        except Exception:
            pass
    return sorted(ts_list)


def _all_tokens(project_dir: Path) -> int:
    total = 0
    for f in project_dir.glob("*.jsonl"):
        try:
            for line in f.read_text(errors="ignore").splitlines():
                try:
                    u = json.loads(line).get("message", {}).get("usage", {})
                    total += u.get("input_tokens", 0) + u.get("output_tokens", 0)
                except Exception:
                    pass
        except Exception:
            pass
    return total


def _active_mins(timestamps: list[datetime]) -> int:
    """Sum consecutive intervals ≤ _GAP. Idle gaps excluded."""
    total = timedelta()
    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap <= _GAP:
            total += gap
    return int(total.total_seconds() / 60)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _replace(html: str, marker: str, value: str) -> str:
    """Replace inline content between <!-- marker --> and <!-- /marker -->."""
    pat = rf"(<!-- {re.escape(marker)} -->)[^<]*(<!-- /{re.escape(marker)} -->)"
    return re.sub(pat, rf"\g<1>{value}\g<2>", html)


def _replace_block(html: str, marker: str, value: str) -> str:
    """Replace multi-line block between <!-- marker --> and <!-- /marker -->."""
    pat = rf"(<!-- {re.escape(marker)} -->).*?(<!-- /{re.escape(marker)} -->)"
    return re.sub(pat, rf"\g<1>{value}\g<2>", html, flags=re.DOTALL)


def _extract_block(html: str, marker: str) -> str:
    m = re.search(
        rf"<!-- {re.escape(marker)} -->(.*?)<!-- /{re.escape(marker)} -->",
        html, re.DOTALL
    )
    return m.group(1).strip() if m else ""


# ── Formatting ────────────────────────────────────────────────────────────────

def _fmt_time(mins: int) -> str:
    if mins < 1:
        return "0h"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if h and m else (f"{h}h" if h else f"{m}m")


# ── Locate project-status.html ────────────────────────────────────────────────

def _find_html(start: Path) -> Path | None:
    current = start
    for _ in range(6):
        candidate = current / "docs" / "project-status.html"
        if candidate.exists():
            return candidate
        if current == current.parent:
            break
        current = current.parent
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _find_html(Path.cwd())
    if not html_path or not html_path.exists():
        print("project-status.html not found — pass path as argument or run from project root.")
        return

    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    slug = cwd.replace("/", "-")
    project_dir = _PROJECTS / slug

    if not project_dir.exists():
        print(f"No local usage data found at {project_dir} — skipping.")
        return

    # ── Collect this contributor's all-time local stats ───────────────────────
    contributor = _contributor_id()
    timestamps  = _all_timestamps(project_dir)
    my_mins     = _active_mins(timestamps)
    my_tokens   = _all_tokens(project_dir)
    my_hours    = round(my_mins / 60, 1)
    today_str   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_str     = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Load existing contributor data from HTML JSON blob ────────────────────
    html = html_path.read_text()
    raw = _extract_block(html, "contributor-data")
    try:
        contributors: dict[str, dict] = json.loads(raw) if raw and raw != "{}" else {}
    except Exception:
        contributors = {}

    # Replace this contributor's entry with fresh all-time totals (idempotent)
    contributors[contributor] = {
        "hours":       my_hours,
        "tokens":      my_tokens,
        "active_mins": my_mins,
        "updated":     today_str,
    }

    # ── Aggregate team totals ─────────────────────────────────────────────────
    total_hours  = round(sum(c["hours"]       for c in contributors.values()), 1)
    total_tokens = sum(c["tokens"]            for c in contributors.values())
    total_mins   = sum(c["active_mins"]       for c in contributors.values())

    # ── Render contributor breakdown ──────────────────────────────────────────
    sorted_contribs = sorted(contributors.items(), key=lambda x: x[1]["hours"], reverse=True)
    rows = "\n      ".join(
        f'<li><strong>{name}</strong>: {c["hours"]}h active'
        f' &middot; {c["tokens"]:,} tokens'
        f' (last updated {c["updated"]})</li>'
        for name, c in sorted_contribs
    )
    breakdown_html = f"\n      {rows}\n    "

    # ── Write back to HTML ────────────────────────────────────────────────────
    html = _replace(html,       "human-tokens",         f"{total_hours}h")
    html = _replace(html,       "claude-tokens",        f"{total_tokens:,}")
    html = _replace(html,       "active-hours",         _fmt_time(total_mins))
    html = _replace(html,       "usage-updated",        now_str)
    html = _replace_block(html, "contributor-breakdown", breakdown_html)
    html = _replace_block(html, "contributor-data",
                          "\n" + json.dumps(contributors, indent=2) + "\n")
    html_path.write_text(html)

    # ── Report ────────────────────────────────────────────────────────────────
    print(f"✅ project-status.html updated — contributor: {contributor}")
    print(f"   My hours    : {my_hours}h ({_fmt_time(my_mins)})")
    print(f"   My tokens   : {my_tokens:,}")
    print(f"   Team total  : {total_hours}h active · {total_tokens:,} tokens")
    names = [name for name, _ in sorted_contribs]
    print(f"   Contributors: {', '.join(names)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Usage update skipped: {e}")
