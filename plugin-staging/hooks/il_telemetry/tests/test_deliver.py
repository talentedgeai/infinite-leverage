from il_telemetry.deliver import telemetry_path, deliver_record

def test_path_layout():
    p = telemetry_path("janet", "edge8-web", "alice", "2026-06-09T02:00:00+00:00")
    assert p == "telemetry/janet/edge8-web/alice/2026-06.jsonl"

def test_409_triggers_single_retry_then_succeeds():   # AC5
    calls = []
    def gh(method, path, **kw):
        calls.append(method)
        if method == "GET": return (200, {"sha": "abc", "content": ""})
        if method == "PUT" and calls.count("PUT") == 1: return (409, {})   # stale sha
        return (200, {})
    ok = deliver_record(gh, {"session_id":"s1","client_slug":"janet","project_slug":"edge8-web","github_login":"alice","started_at":"2026-06-09T02:00:00+00:00"})
    assert ok is True
    assert calls.count("PUT") == 2     # one retry only

def test_second_409_is_nonfatal():                    # AC5
    def gh(method, path, **kw):
        return (200, {"sha":"x","content":""}) if method=="GET" else (409, {})
    assert deliver_record(gh, {"session_id":"s1","client_slug":"j","project_slug":"p","github_login":"a","started_at":"2026-06-09T02:00:00+00:00"}) is False
