import json
from pathlib import Path

def write_record(outbox_dir, record: dict) -> None:
    try:
        d = Path(outbox_dir)
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{record['session_id']}.json").write_text(json.dumps(record))
    except Exception:
        pass

def pending_records(outbox_dir) -> list[dict]:
    out: list[dict] = []
    try:
        d = Path(outbox_dir)
        if not d.exists():
            return out
        for f in sorted(d.glob("*.json")):
            try:
                out.append(json.loads(f.read_text()))
            except Exception:
                pass
    except Exception:
        pass
    return out

def mark_delivered(outbox_dir, session_id: str) -> None:
    try:
        (Path(outbox_dir) / f"{session_id}.json").unlink(missing_ok=True)
    except Exception:
        pass
