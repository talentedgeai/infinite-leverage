from datetime import datetime, timezone, timedelta
from il_telemetry.methodology import _extract_usage, git_hours_strict, commit_span_by_day, resolve


def test_extract_usage_includes_cache_creation_in_billed():   # AC1'
    u = {"message": {"usage": {"input_tokens": 100, "output_tokens": 50,
                               "cache_creation_input_tokens": 20, "cache_read_input_tokens": 1000}}}
    got = _extract_usage(u)
    assert got["billed"] == 100 + 50 + 20          # cache_creation counted, cache_read NOT
    assert got["total"] == 100 + 50 + 20 + 1000    # total adds cache_read


def test_git_hours_strict_caps_long_gaps():
    tz = timezone.utc
    base = datetime(2026, 6, 9, 2, 0, tzinfo=tz)
    times = [base, base + timedelta(minutes=20), base + timedelta(hours=5)]  # 20m gap kept, 5h gap → session credit
    # SESSION_S base + 20min + SESSION_S (gap>2h) = 1800 + 1200 + 1800 = 4800s = 1.333h
    assert round(git_hours_strict(times), 3) == round(4800 / 3600, 3)


def test_commit_span_by_day():
    tz = timezone.utc
    d = datetime(2026, 6, 9, 9, 0, tzinfo=tz)
    times = [d, d.replace(hour=11)]   # 2h span + 30min credit = 9000s
    spans = commit_span_by_day(times, tz)
    assert round(spans[d.date()], 3) == round((2 * 3600 + 1800) / 3600, 3)


def test_resolve_takes_max_basis():
    from datetime import date
    window = [date(2026, 6, 9)]
    out = resolve({date(2026, 6, 9): 1.0}, {date(2026, 6, 9): 2.5}, window)
    assert out[date(2026, 6, 9)]['resolved'] == 2.5
    assert out[date(2026, 6, 9)]['source'] == 'claude-jsonl'
