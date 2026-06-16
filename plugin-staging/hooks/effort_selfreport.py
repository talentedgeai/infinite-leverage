"""
Self-report effort hook (project.json piggyback delivery).

Runs on SessionEnd. Reads the just-ended session's transcript, computes the real
active intervals (5-min-gap rule — the anti-overlap measure) + token totals, and
UPSERTS an entry into <repo>/.claude/project.json's `effort_log` array, keyed by
session_id. It is a LOCAL FILE WRITE ONLY — no network, no gh, no secrets. The
contributor commits project.json in their normal flow; the central tracker reads it
(it already has read access) and ingests OWNER entries.

Self-contained on purpose (no il_telemetry import) so it can be vendored into a single
repo's .claude/hooks/ and work standalone on any machine with python3.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

GAP = timedelta(minutes=5)  # gaps longer than this split active intervals (idle excluded)


def _usage_total(obj: dict) -> int:
    u = (obj.get("message") or {}).get("usage") if isinstance(obj.get("message"), dict) else None
    if u is None:
        u = obj.get("usage")
    if not isinstance(u, dict):
        return 0
    return sum(int(u.get(k, 0) or 0) for k in
               ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def build_effort_entry(lines, session_id: str, author_email: str,
                       tz_offset_hours: int = 7, tool: str = "claude-code") -> dict | None:
    """Pure: transcript lines -> one effort_log entry, or None if no timestamps. Never raises."""
    tz = timezone(timedelta(hours=tz_offset_hours))
    stamps: list[datetime] = []
    tokens = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        tokens += _usage_total(obj)
        ts = obj.get("timestamp")
        if ts:
            try:
                stamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz))
            except Exception:
                pass
    if not stamps:
        return None
    stamps.sort()

    # 5-min-gap intervals
    intervals = []
    start = prev = stamps[0]
    for t in stamps[1:]:
        if t - prev <= GAP:
            prev = t
        else:
            intervals.append((start, prev))
            start = prev = t
    intervals.append((start, prev))

    active_s = sum((e - s).total_seconds() for s, e in intervals)
    return {
        "session_id": session_id,
        "occurred_on": stamps[0].date().isoformat(),
        "started_at": stamps[0].isoformat(),
        "ended_at": stamps[-1].isoformat(),
        "active_intervals": [[s.isoformat(), e.isoformat()] for s, e in intervals],
        "active_hours": round(active_s / 3600, 2),
        "wall_clock_hours": round((stamps[-1] - stamps[0]).total_seconds() / 3600, 2),
        "tokens": {"total": tokens},
        "tool": tool,
        "contributor_email": author_email,
        "phase": "auto self-report (SessionEnd)",
    }


def upsert_effort_log(project_json_path: Path, entry: dict) -> None:
    """Insert-or-replace `entry` in project.json effort_log (keyed by session_id). Preserves
    all other keys. Creates the file with {} if absent. Never raises."""
    try:
        data = {}
        if project_json_path.exists():
            try:
                data = json.loads(project_json_path.read_text() or "{}")
            except Exception:
                data = {}
        log = data.get("effort_log")
        if not isinstance(log, list):
            log = []
        log = [e for e in log if e.get("session_id") != entry["session_id"]]
        log.append(entry)
        data["effort_log"] = log
        project_json_path.parent.mkdir(parents=True, exist_ok=True)
        project_json_path.write_text(json.dumps(data, indent=2) + "\n")
    except Exception:
        pass


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    try:
        cwd = Path(payload.get("cwd") or ".")
        transcript = payload.get("transcript_path") or ""
        session_id = payload.get("session_id") or ""
        if not transcript or not session_id:
            return
        tp = Path(transcript)
        if not tp.exists():
            return
        try:
            email = subprocess.check_output(
                ["git", "-C", str(cwd), "config", "user.email"],
                stderr=subprocess.DEVNULL, text=True, timeout=5).strip()
        except Exception:
            email = ""
        entry = build_effort_entry(tp.read_text(errors="ignore").splitlines(), session_id, email)
        if entry:
            upsert_effort_log(cwd / ".claude" / "project.json", entry)
    except Exception:
        return


if __name__ == "__main__":
    main()
