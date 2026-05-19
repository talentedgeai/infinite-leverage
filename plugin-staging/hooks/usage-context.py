#!/usr/bin/env python3
"""
Inject a compact usage briefing into Claude's context at SessionStart.
Reads ~/.claude/projects/ JSONL directly — no external tools, works offline.
Tracks: tokens (weekly/daily/session) + active hours per project.

JSONL format notes:
  - Timestamped entries (type=queue-operation) are used for active-time calculation.
  - Token data lives in message.usage (assistant entries) which lack timestamps.
  - File mtime is used as a session-date proxy to filter tokens by period.

Never raises — a failure here must never block the session.
"""
import json, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

_PROJECTS = Path.home() / ".claude" / "projects"
_GAP = timedelta(minutes=30)  # gaps > this between msgs = idle, not counted


# ── Timestamp-based helpers (for active-time) ─────────────────────────────────

def _load_timestamps(project_dir: Path, since: datetime) -> list[datetime]:
    """Collect all top-level timestamps (queue-operation entries) since `since`."""
    ts_list: list[datetime] = []
    for f in project_dir.glob("*.jsonl"):
        try:
            for line in f.read_text(errors="ignore").splitlines():
                obj = json.loads(line)
                ts_raw = obj.get("timestamp", "")
                if not ts_raw:
                    continue
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                if ts >= since:
                    ts_list.append(ts)
        except Exception:
            pass
    return sorted(ts_list)


def _active_mins(timestamps: list[datetime]) -> int:
    """Sum consecutive intervals ≤ _GAP. Idle gaps are excluded."""
    total = timedelta()
    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap <= _GAP:
            total += gap
    return int(total.total_seconds() / 60)


# ── File-mtime-based helpers (for token counts) ───────────────────────────────

def _tokens_since(project_dir: Path, since: datetime) -> int:
    """
    Sum input+output tokens from files modified since `since`.
    Token data is in message.usage (assistant message entries).
    File mtime proxies session-end time — accurate enough for daily/weekly windows.
    """
    total = 0
    for f in project_dir.glob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime < since:
                continue
            for line in f.read_text(errors="ignore").splitlines():
                try:
                    u = json.loads(line).get("message", {}).get("usage", {})
                    total += u.get("input_tokens", 0) + u.get("output_tokens", 0)
                except Exception:
                    pass
        except Exception:
            pass
    return total


# ── Formatting ────────────────────────────────────────────────────────────────

def _fmt_time(mins: int) -> str:
    if mins < 1:
        return "—"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if h and m else (f"{h}h" if h else f"{m}m")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    slug = cwd.replace("/", "-")   # matches ~/.claude/projects/ naming convention
    now = datetime.now(timezone.utc)
    project_dir = _PROJECTS / slug

    week_ago  = now - timedelta(days=7)
    day_ago   = now - timedelta(hours=24)
    hour_ago  = now - timedelta(hours=1)

    if project_dir.exists():
        week_ts   = _load_timestamps(project_dir, week_ago)
        day_ts    = [ts for ts in week_ts if ts >= day_ago]
        sess_ts   = [ts for ts in day_ts  if ts >= hour_ago]
        w_mins    = _active_mins(week_ts)
        d_mins    = _active_mins(day_ts)
        w_tok     = _tokens_since(project_dir, week_ago)
        d_tok     = _tokens_since(project_dir, day_ago)
        s_tok     = _tokens_since(project_dir, hour_ago)
    else:
        w_mins = d_mins = w_tok = d_tok = s_tok = 0

    # Cross-project weekly comparison
    all_weekly: dict[str, tuple[int, int]] = {}  # slug → (tokens, active_mins)
    if _PROJECTS.exists():
        for p in _PROJECTS.iterdir():
            if p.is_dir():
                tok = _tokens_since(p, week_ago)
                if tok > 0:
                    ts = _load_timestamps(p, week_ago)
                    all_weekly[p.name] = (tok, _active_mins(ts))

    name = Path(cwd).name
    parts = [
        f"[Usage: /{name} — "
        f"session {s_tok:,}t"
        f" · today {d_tok:,}t / {_fmt_time(d_mins)} active"
        f" · week {w_tok:,}t / {_fmt_time(w_mins)} active."
    ]

    if len(all_weekly) > 1:
        top = sorted(all_weekly.items(), key=lambda x: x[1][0], reverse=True)[:3]
        top_str = " · ".join(
            f"{p.split('-')[-1]} {v[0]:,}t/{_fmt_time(v[1])}" for p, v in top
        )
        parts.append(f" Top this week: {top_str}.")

    if d_tok > 50_000:
        parts.append(" High daily usage — consider /compact.")

    parts.append("]")
    print("".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
