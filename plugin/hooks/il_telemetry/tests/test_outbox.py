from il_telemetry.outbox import write_record, pending_records, mark_delivered

def test_write_replaces_by_session_id(tmp_path):       # AC4
    d = tmp_path / "outbox"
    write_record(d, {"session_id":"s1","claude_tokens":10})
    write_record(d, {"session_id":"s1","claude_tokens":99})
    recs = pending_records(d)
    assert len(recs) == 1 and recs[0]["claude_tokens"] == 99

def test_mark_delivered_removes_from_pending(tmp_path): # AC6
    d = tmp_path / "outbox"
    write_record(d, {"session_id":"s1"})
    write_record(d, {"session_id":"s2"})
    mark_delivered(d, "s1")
    assert {r["session_id"] for r in pending_records(d)} == {"s2"}
