import json
from effort_selfreport import build_effort_entry, upsert_effort_log


def _line(ts, inp=0, out=0, cc=0, cr=0):
    return json.dumps({"timestamp": ts, "message": {"usage": {
        "input_tokens": inp, "output_tokens": out,
        "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr}}})


def test_single_interval_tokens_and_hours():
    # two stamps 3 min apart (<=5min) -> one interval; tokens = sum of all four usage fields
    lines = [
        _line("2026-06-14T01:00:00+00:00", inp=100, out=50, cc=10, cr=5),
        _line("2026-06-14T01:03:00+00:00", inp=0, out=20, cc=0, cr=0),
    ]
    e = build_effort_entry(lines, "s1", "james@wha.com", tz_offset_hours=7)
    assert e["session_id"] == "s1"
    assert e["tokens"]["total"] == 185               # 165 + 20, cache_read counted
    assert len(e["active_intervals"]) == 1
    assert e["active_hours"] == 0.05                  # 3 min = 0.05 h
    assert e["contributor_email"] == "james@wha.com"
    assert e["occurred_on"] == "2026-06-14"           # +07:00 local date


def test_gap_splits_intervals():
    lines = [
        _line("2026-06-14T01:00:00+00:00"),
        _line("2026-06-14T01:02:00+00:00"),
        _line("2026-06-14T01:30:00+00:00"),  # 28-min gap -> new interval
        _line("2026-06-14T01:31:00+00:00"),
    ]
    e = build_effort_entry(lines, "s1", "e@x.com")
    assert len(e["active_intervals"]) == 2
    assert e["active_hours"] == round((120 + 60) / 3600, 2)  # 2min + 1min active only


def test_no_timestamps_returns_none():
    assert build_effort_entry(['{"message":{"usage":{}}}', 'not json'], "s1", "e@x.com") is None


def test_upsert_creates_and_replaces(tmp_path):
    pj = tmp_path / ".claude" / "project.json"
    pj.parent.mkdir(parents=True)
    pj.write_text(json.dumps({"client_id": "c1", "effort_log": [
        {"session_id": "s1", "active_hours": 1.0},
    ]}))
    # replace s1, preserve client_id
    upsert_effort_log(pj, {"session_id": "s1", "active_hours": 2.5})
    data = json.loads(pj.read_text())
    assert data["client_id"] == "c1"
    assert len(data["effort_log"]) == 1
    assert data["effort_log"][0]["active_hours"] == 2.5
    # append a new session
    upsert_effort_log(pj, {"session_id": "s2", "active_hours": 0.3})
    data = json.loads(pj.read_text())
    assert {e["session_id"] for e in data["effort_log"]} == {"s1", "s2"}


def test_upsert_creates_file_when_absent(tmp_path):
    pj = tmp_path / ".claude" / "project.json"
    upsert_effort_log(pj, {"session_id": "s1", "active_hours": 1.0})
    assert json.loads(pj.read_text())["effort_log"][0]["session_id"] == "s1"
