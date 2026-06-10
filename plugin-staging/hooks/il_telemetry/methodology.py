"""
methodology.py — Canonical contribution methodology vendored from team-hours.py.
All functions/constants are copied verbatim from:
  .claude/skills/pm-contribution-sync/team-hours.py
Do NOT modify the copied logic — it is the source of truth.
"""

import json
import os
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# ── constants (§2 knobs) ──────────────────────────────────────────────────────
MAX_GAP_S = 2 * 3600        # git-hours strict: 2 h gap cap
SESSION_S = 30 * 60         # session-start credit: 30 min
JSONL_GAP_S = 5 * 60        # JSONL activity gap: 5 min


# ── timezone helpers ──────────────────────────────────────────────────────────
def parse_tz(offset: str) -> timezone:
    sign = -1 if offset.startswith('-') else 1
    parts = offset.lstrip('+-').split(':')
    h, m = int(parts[0]), (int(parts[1]) if len(parts) > 1 else 0)
    return timezone(timedelta(hours=sign * h, minutes=sign * m))


def date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


# ── git helpers ───────────────────────────────────────────────────────────────
def fetch_commits(repo: str, author: str, start: date, end: date, tz: timezone) -> list:
    after = start.isoformat()
    before = (end + timedelta(days=1)).isoformat()
    try:
        out = subprocess.check_output(
            ['git', '-C', repo, 'log',
             f'--author={author}',
             f'--after={after}', f'--before={before}',
             '--format=%aI', '--all'],
            stderr=subprocess.DEVNULL, text=True
        )
    except subprocess.CalledProcessError:
        return []
    result = []
    for line in out.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            result.append(datetime.fromisoformat(line).astimezone(tz))
        except ValueError:
            continue
    return sorted(result)


# ── three bases ───────────────────────────────────────────────────────────────
def git_hours_strict(times: list) -> float:
    """§2.1 — standard open-source heuristic."""
    if not times:
        return 0.0
    total = SESSION_S
    for prev, curr in zip(times, times[1:]):
        gap = (curr - prev).total_seconds()
        total += gap if gap < MAX_GAP_S else SESSION_S
    return total / 3600


def commit_span_by_day(times: list, tz: timezone) -> dict:
    """§2.2 — same-day wall-clock span + session credit."""
    by_day = defaultdict(list)
    for dt in times:
        by_day[dt.astimezone(tz).date()].append(dt)
    return {
        day: ((max(lst) - min(lst)).total_seconds() + SESSION_S) / 3600
        for day, lst in by_day.items()
    }


def commit_hours_by_day(times: list, tz: timezone) -> dict:
    """Return {date: sorted list of clock-hours} from commit timestamps — used for man_hour slot expansion."""
    by_day = defaultdict(set)
    for dt in times:
        local = dt.astimezone(tz)
        by_day[local.date()].add(local.hour)
    return {day: sorted(hours) for day, hours in by_day.items()}


def scan_jsonl(dirs: list, start: date, end: date, tz: timezone, with_tokens: bool):
    """§2.3 + §2.4 — JSONL activity hours and token totals (deduped dirs).
    Returns: (hours_by_day, tokens_by_day, unique_dirs, all_ts)
    all_ts is the full sorted timestamp list used for sync-file hour-slot expansion."""
    end_excl = end + timedelta(days=1)
    all_ts = []
    tokens_by_day = defaultdict(lambda: {'billed': 0, 'total': 0})

    # Dedup dirs by resolved path (§2.4 gotcha)
    seen = set()
    unique_dirs = []
    for d in dirs:
        r = Path(d).resolve()
        if r not in seen:
            seen.add(r)
            unique_dirs.append(Path(d))

    for d in unique_dirs:
        for f in d.rglob('*.jsonl'):
            try:
                with open(f, encoding='utf-8', errors='replace') as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        ts = _extract_ts(obj)
                        if ts is None:
                            continue
                        local = ts.astimezone(tz)
                        day = local.date()
                        if start <= day < end_excl:
                            all_ts.append(local)
                            if with_tokens:
                                u = _extract_usage(obj)
                                tokens_by_day[day]['billed'] += u['billed']
                                tokens_by_day[day]['total'] += u['total']
            except (OSError, PermissionError):
                continue

    all_ts.sort()

    # §2.3 — 5-min-gap session definition per day
    by_day = defaultdict(list)
    for ts in all_ts:
        by_day[ts.date()].append(ts)

    hours_by_day = {}
    for day, lst in by_day.items():
        sessions, active = 1, 0
        sess_start = last = lst[0]
        for t in lst[1:]:
            if (t - last).total_seconds() <= JSONL_GAP_S:
                last = t
            else:
                active += (last - sess_start).total_seconds()
                sessions += 1
                sess_start = last = t
        active += (last - sess_start).total_seconds()
        hours_by_day[day] = (active + sessions * SESSION_S) / 3600

    return hours_by_day, dict(tokens_by_day), unique_dirs, all_ts


def _extract_ts(obj: dict):
    for key in ('timestamp', 'created_at', 'time'):
        val = obj.get(key)
        if val:
            try:
                return datetime.fromisoformat(str(val).replace('Z', '+00:00'))
            except ValueError:
                continue
    return None


def _extract_usage(obj: dict) -> dict:
    u = None
    msg = obj.get('message')
    if isinstance(msg, dict):
        u = msg.get('usage')
    if u is None:
        u = obj.get('usage')
    if not isinstance(u, dict):
        return {'billed': 0, 'total': 0}
    inp = u.get('input_tokens', 0) or 0
    out = u.get('output_tokens', 0) or 0
    cc = u.get('cache_creation_input_tokens', 0) or 0
    cr = u.get('cache_read_input_tokens', 0) or 0
    return {'billed': inp + out + cc, 'total': inp + out + cc + cr}


def find_jsonl_dirs(keywords: list) -> list:
    base = Path.home() / '.claude' / 'projects'
    if not base.exists():
        return []
    dirs = []
    for kw in keywords:
        dirs.extend(d for d in base.glob(f'*{kw}*') if d.is_dir())
    return dirs


# ── resolution §2.5 ───────────────────────────────────────────────────────────
def resolve(span_by_day: dict, jsonl_by_day: dict, window: list) -> dict:
    result = {}
    for day in window:
        span = span_by_day.get(day, 0.0)
        jsonl = jsonl_by_day.get(day, 0.0)
        resolved = max(span, jsonl)
        source = 'commit-span' if span >= jsonl else 'claude-jsonl'
        result[day] = {
            'resolved': round(resolved, 2),
            'source': source,
            'commit_span': round(span, 2),
            'jsonl': round(jsonl, 2),
        }
    return result


# ── per-author orchestration helper (new — used by flush hook) ────────────────
def human_hours_for(repo: str, author: str, start: date, end: date,
                    tz: timezone, jsonl_keywords: list) -> dict:
    """Per-day resolved human hours (3-basis max(commit_span, jsonl)) + commit-hour slots
    for ONE author over [start, end]. Mirrors team-hours.py main()'s per-author block.
    Returns {'per_day': {date_str: {resolved, source, commit_span, jsonl}},
             'commit_hours_by_day': {date_str: [hours...]}}. Never raises — returns
    empty dicts on any failure."""
    try:
        window = list(date_range(start, end))
        commits = fetch_commits(repo, author, start, end, tz)
        span_by_day = commit_span_by_day(commits, tz)
        commit_hrs = commit_hours_by_day(commits, tz)
        jsonl_hours = {}
        if jsonl_keywords:
            dirs = find_jsonl_dirs(jsonl_keywords)
            if dirs:
                jsonl_hours, _tokens, _dirs, _ts = scan_jsonl(dirs, start, end, tz, with_tokens=False)
        per_day = resolve(span_by_day, jsonl_hours, window)
        return {
            'per_day': {str(d): v for d, v in per_day.items()
                        if v['resolved'] > 0 or v['commit_span'] > 0 or v['jsonl'] > 0},
            'commit_hours_by_day': {str(d): hrs for d, hrs in commit_hrs.items()},
        }
    except Exception:
        return {'per_day': {}, 'commit_hours_by_day': {}}
