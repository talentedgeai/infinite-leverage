import json, os, sys
from pathlib import Path
from il_telemetry.capture import capture_session
from il_telemetry.context import gather_context
from il_telemetry.outbox import write_record

OUTBOX = Path.home() / ".claude" / ".il-telemetry" / "outbox"

def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    try:
        cwd = data.get("cwd") or os.getcwd()
        try:
            os.chdir(cwd)
        except Exception:
            pass
        metrics = capture_session(data.get("transcript_path") or "", data.get("session_id") or "")
        if not metrics:
            return
        write_record(OUTBOX, {**metrics, **gather_context()})
    except Exception:
        return

if __name__ == "__main__":
    main()
