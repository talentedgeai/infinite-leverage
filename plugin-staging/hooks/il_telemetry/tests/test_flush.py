from il_telemetry.flush import build_human_records

def test_build_human_records_maps_per_day():       # AC15/AC17
    hh = {"per_day": {"2026-06-09": {"resolved": 2.5, "source": "commit-span", "commit_span": 2.5, "jsonl": 1.0}},
          "commit_hours_by_day": {"2026-06-09": [9, 11]}}
    ctx = {"author_email": "a@e.ai", "github_login": "alice", "repo_full_name": "o/r"}
    recs = build_human_records(hh, ctx)
    assert len(recs) == 1
    r = recs[0]
    assert r["record_type"] == "human"
    assert r["occurred_on"] == "2026-06-09"
    assert r["resolved_hours"] == 2.5
    assert r["commit_hours"] == [9, 11]
    assert r["author_email"] == "a@e.ai" and r["github_login"] == "alice" and r["repo_full_name"] == "o/r"
    assert r["started_at"] == "2026-06-09T09:00:00+00:00"   # first commit-hour (matches team-hours.py occurred_at)

def test_build_human_records_empty():
    assert build_human_records({"per_day": {}, "commit_hours_by_day": {}}, {}) == []
