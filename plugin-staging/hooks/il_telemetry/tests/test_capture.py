from pathlib import Path
from il_telemetry.capture import capture_session

FIX = Path(__file__).parent / "fixtures" / "session.jsonl"

def test_tokens_summed():                     # AC1' — billed = input+output+cache_creation
    m = capture_session(str(FIX), "sess-1")
    assert m["claude_tokens"] == (100 + 50 + 10) + (200 + 30 + 5)   # cache_read (9999/8888) NOT counted

def test_active_minutes_excludes_gap():       # AC2
    m = capture_session(str(FIX), "sess-1")
    assert m["active_minutes"] == 10          # only 02:00->02:10; the 40-min gap dropped
    assert m["started_at"] == "2026-06-09T02:00:00+00:00"
    assert m["ended_at"]   == "2026-06-09T02:50:00+00:00"
    assert m["session_id"] == "sess-1"

def test_missing_file_returns_none():         # AC3
    assert capture_session("/no/such.jsonl", "x") is None
