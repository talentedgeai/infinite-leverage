import json
from datetime import datetime, timedelta
from pathlib import Path
from il_telemetry.methodology import _extract_usage

_GAP = timedelta(minutes=30)

def capture_session(transcript_path: str, session_id: str) -> dict | None:
    """Cumulative metrics for one session's JSONL transcript. Never raises."""
    try:
        p = Path(transcript_path)
        if not p.exists():
            return None
        tokens = 0
        stamps: list[datetime] = []
        for line in p.read_text(errors="ignore").splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            tokens += _extract_usage(obj)["billed"]
            ts = obj.get("timestamp")
            if ts:
                try:
                    stamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                except Exception:
                    pass
        if not stamps:
            return None
        stamps.sort()
        active = timedelta()
        for i in range(1, len(stamps)):
            gap = stamps[i] - stamps[i - 1]
            if gap <= _GAP:
                active += gap
        return {
            "session_id": session_id,
            "claude_tokens": tokens,
            "active_minutes": int(active.total_seconds() / 60),
            "started_at": stamps[0].isoformat(),
            "ended_at": stamps[-1].isoformat(),
        }
    except Exception:
        return None
