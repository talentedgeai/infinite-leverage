#!/usr/bin/env python3
"""
team-hours.py — Defensible engineering-hours and Claude token accounting.
See docs/assessments/team-hours-methodology.md for the full spec.

Usage:
  python3 scripts/team-hours.py \\
    --start 2026-05-25 --end 2026-05-29 \\
    --author "TracNg99" --author "James Murray" \\
    --jsonl-keyword longev --jsonl-keyword wha \\
    --tz +07:00 \\
    --repo .

Options:
  --start           Start date inclusive (YYYY-MM-DD)
  --end             End date inclusive (YYYY-MM-DD)
  --author          Git author name or email (repeatable)
  --jsonl-keyword   Keyword to match ~/.claude/projects/*keyword*/ dirs (repeatable)
  --tz              UTC offset for local-day bucketing, e.g. +07:00 (default +00:00)
  --repo            Path to the git repo (default: .)
  --with-tokens     Also aggregate Claude token totals from JSONL
  --no-jsonl        Skip JSONL scan; resolved hours fall back to commit-span only
  --json            Emit machine-readable JSON instead of Markdown
"""

import argparse
import json
import os
import subprocess
import sys
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


def scan_jsonl(dirs: list, start: date, end: date, tz: timezone, with_tokens: bool):
    """§2.3 + §2.4 — JSONL activity hours and token totals (deduped dirs)."""
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

    return hours_by_day, dict(tokens_by_day), unique_dirs


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


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument('--start', required=True)
    ap.add_argument('--end', required=True)
    ap.add_argument('--author', action='append', default=[])
    ap.add_argument('--jsonl-keyword', action='append', default=[], dest='jsonl_keyword')
    ap.add_argument('--tz', default='+00:00')
    ap.add_argument('--repo', default='.')
    ap.add_argument('--with-tokens', action='store_true')
    ap.add_argument('--no-jsonl', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    tz = parse_tz(args.tz)
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    window = list(date_range(start, end))

    # JSONL scan (once, shared across all authors — tokens are operator-total)
    jsonl_dirs_raw = [] if args.no_jsonl else find_jsonl_dirs(args.jsonl_keyword)
    shared_jsonl_hours: dict = {}
    tokens_by_day: dict = {}
    scanned_dirs: list = []

    if jsonl_dirs_raw:
        shared_jsonl_hours, tokens_by_day, scanned_dirs = scan_jsonl(
            jsonl_dirs_raw, start, end, tz, with_tokens=args.with_tokens
        )

    results = {}
    for author in args.author:
        commits = fetch_commits(args.repo, author, start, end, tz)
        span_by_day = commit_span_by_day(commits, tz)
        strict = git_hours_strict(commits)
        per_day = resolve(span_by_day, shared_jsonl_hours, window)

        resolved_total = sum(v['resolved'] for v in per_day.values())
        span_total = sum(v['commit_span'] for v in per_day.values())
        jsonl_total = sum(v['jsonl'] for v in per_day.values())

        source_counts: dict = defaultdict(int)
        for v in per_day.values():
            if v['resolved'] > 0:
                source_counts[v['source']] += 1
        dominant = max(source_counts, key=source_counts.get) if source_counts else 'commit-span'

        results[author] = {
            'commits': len(commits),
            'git_hours_strict': round(strict, 2),
            'commit_span_total': round(span_total, 2),
            'jsonl_total': round(jsonl_total, 2),
            'resolved_total': round(resolved_total, 2),
            'dominant_source': dominant,
            'per_day': {
                str(d): v for d, v in per_day.items()
                if v['resolved'] > 0 or v['commit_span'] > 0 or v['jsonl'] > 0
            },
        }

    output = {
        'window': {'start': str(start), 'end': str(end)},
        'authors': results,
        'jsonl_dirs_scanned': [str(d) for d in scanned_dirs],
        'no_jsonl': args.no_jsonl,
    }

    if args.with_tokens and tokens_by_day:
        output['tokens_by_day'] = {
            str(d): v for d, v in sorted(tokens_by_day.items())
        }
        output['tokens_window'] = {
            'billed': sum(v['billed'] for v in tokens_by_day.values()),
            'total': sum(v['total'] for v in tokens_by_day.values()),
        }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    # ── Markdown output ────────────────────────────────────────────────────────
    print(f"## Team Contributions — {start} → {end}\n")
    print("| Author | Human tokens (h) | Commits | Basis | git-strict (h) | commit-span (h) | claude-jsonl (h) |")
    print("|---|---|---|---|---|---|---|")
    for author, r in results.items():
        basis = 'commit-span (--no-jsonl)' if args.no_jsonl else r['dominant_source']
        print(
            f"| {author} | **{r['resolved_total']}** | {r['commits']} | {basis}"
            f" | {r['git_hours_strict']} | {r['commit_span_total']} | {r['jsonl_total']} |"
        )

    if args.with_tokens and 'tokens_window' in output:
        tw = output['tokens_window']
        bm = tw['billed'] / 1_000_000
        tm = tw['total'] / 1_000_000
        print(f"\n**Claude tokens** — {bm:.1f} M billed / {tm:.1f} M total "
              f"(operator account — not per-author, see methodology §2.4)")

    if not args.no_jsonl:
        if scanned_dirs:
            print(f"\n> JSONL: {len(scanned_dirs)} dir(s) scanned. "
                  f"Figures reflect the machine where this script ran (methodology Limitation 1).")
        elif args.jsonl_keyword:
            print(f"\n> ⚠️  No JSONL dirs matched keywords: {args.jsonl_keyword}. "
                  f"Resolved hours fall back to commit-span.")

    # Per-day breakdown
    days_with_data = sorted({
        d for r in results.values() for d in r['per_day']
    })
    if days_with_data:
        print(f"\n### Per-day breakdown\n")
        header = "| Date |" + "".join(f" {a} h | src |" for a in results)
        sep = "|---|" + "---|---|" * len(results)
        print(header)
        print(sep)
        for d_str in days_with_data:
            row = f"| {d_str} |"
            for r in results.values():
                v = r['per_day'].get(d_str, {'resolved': 0.0, 'source': '—'})
                row += f" {v['resolved']} | {v['source']} |"
            print(row)


if __name__ == '__main__':
    main()
