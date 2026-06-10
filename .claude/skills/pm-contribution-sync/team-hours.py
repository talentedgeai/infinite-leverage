#!/usr/bin/env python3
"""
team-hours.py — Defensible engineering-hours and Claude token accounting.
See docs/assessments/team-hours-methodology.md for the full spec.

Usage:
  python3 scripts/team-hours.py \\
    --start 2026-05-25 --end 2026-05-29 \\
    --author "TracNg99" --author-email "trac@edge8.ai" \\
    --author "James Murray" --author-email "james@edge8.ai" \\
    --jsonl-keyword longev --jsonl-keyword wha \\
    --tz +07:00 \\
    --repo . \\
    --project-slug edge8-web \\
    --sync-output scripts/contribution-sync.json

Options:
  --start           Start date inclusive (YYYY-MM-DD)
  --end             End date inclusive (YYYY-MM-DD)
  --author          Git author name or email (repeatable)
  --author-email    DB-resolution email paired with each --author (repeatable, same order)
  --jsonl-keyword   Keyword to match ~/.claude/projects/*keyword*/ dirs (repeatable)
  --tz              UTC offset for local-day bucketing, e.g. +07:00 (default +00:00)
  --repo            Path to the git repo (default: .)
  --project-slug    Project slug written into the sync file header
  --with-tokens     Also aggregate Claude token totals from JSONL
  --no-jsonl        Skip JSONL scan; resolved hours fall back to commit-span only
  --json            Emit machine-readable JSON instead of Markdown
  --sync-output     Path to write contribution-sync.json for DB ingestion
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


# ── sync file builder ─────────────────────────────────────────────────────────
def _write_sync_file(args, output: dict, start: date, end: date, tz: timezone) -> None:
    """Write contribution-sync.json — direct POST payloads for ingest-session-* edge functions.

    man_hours   → POST to ingest-session-start  (one row per author per commit-hour, idempotent)
    token_entries → POST to ingest-session-end  (human centihours + billed claude tokens per author per day)

    The GitHub workflow adds client_id / project_id from env before posting.
    Units: human_tokens = round(resolved_hours × 100) [centihours as int], claude_tokens = raw billed tokens.
    Claude tokens are operator-level (§2.4); attributed to the author with the most resolved hours per day.
    """
    author_emails: list = args.author_email
    authors: list = args.author

    # Map author name → email (positionally paired; unmatched authors are skipped in sync output)
    email_map: dict = {
        authors[i]: author_emails[i]
        for i in range(min(len(authors), len(author_emails)))
        if author_emails[i]
    }

    tokens_by_day: dict = output.get('tokens_by_day', {})

    man_hours: list = []
    token_entries: list = []

    # For each day, find the dominant author (most resolved hours) to carry claude tokens
    def dominant_author_for_day(day_str: str) -> str | None:
        best, best_h = None, -1.0
        for author in authors:
            if author not in email_map:
                continue
            v = output['authors'][author]['per_day'].get(day_str, {})
            h = v.get('resolved', 0.0)
            if h > best_h:
                best_h = h
                best = author
        return best

    for author, r in output['authors'].items():
        email = email_map.get(author)
        if not email:
            continue

        # man_hours — one slot per distinct commit-hour
        for day_str, hours in r.get('commit_hours_by_day', {}).items():
            for hour in hours:
                man_hours.append({
                    'author_email': email,
                    'occurred_on': day_str,
                    'occurred_hour': hour,
                    'primary_role': None,
                })

        # token_entries — one row per active day
        for day_str, v in r['per_day'].items():
            resolved = v.get('resolved', 0.0)
            if resolved <= 0:
                continue

            # Determine first commit-hour or midnight for occurred_at
            day_obj = date.fromisoformat(day_str)
            hours_list = r.get('commit_hours_by_day', {}).get(day_str, [])
            hour = hours_list[0] if hours_list else 0
            occurred_at = datetime(
                day_obj.year, day_obj.month, day_obj.day, hour,
                tzinfo=tz
            ).isoformat()

            # Claude tokens for this day — operator total, only to the dominant author
            day_claude = 0
            day_tok = tokens_by_day.get(day_str, {})
            if day_tok and dominant_author_for_day(day_str) == author:
                day_claude = day_tok.get('billed', 0)

            source = 'pr_commit' if v.get('source') == 'commit-span' else 'planning'

            token_entries.append({
                'author_email': email,
                'occurred_at': occurred_at,
                'source': source,
                'human_tokens': round(resolved * 100),  # centihours as int
                'claude_tokens': day_claude,
            })

    sync = {
        'schema_version': 1,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'project_slug': args.project_slug or '',
        'window': output['window'],
        '_notes': {
            'human_tokens_unit': 'centihours (resolved_hours × 100)',
            'claude_tokens_unit': 'raw billed tokens (operator account, attributed to dominant author per day)',
            'man_hours_target': 'POST each entry to ingest-session-start with client_id + project_id from env',
            'token_entries_target': 'POST each entry to ingest-session-end with client_id + project_id from env',
        },
        'man_hours': man_hours,
        'token_entries': token_entries,
    }

    out_path = Path(args.sync_output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(sync, fh, indent=2)
    print(f'[sync] wrote {out_path} ({len(man_hours)} man_hour slots, {len(token_entries)} token entries)',
          file=sys.stderr)


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
    ap.add_argument('--author-email', action='append', default=[], dest='author_email')
    ap.add_argument('--project-slug', default='')
    ap.add_argument('--with-tokens', action='store_true')
    ap.add_argument('--no-jsonl', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--sync-output', default='', metavar='PATH',
                    help='Write contribution-sync.json to PATH for DB ingestion')
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

    jsonl_all_ts: list = []
    if jsonl_dirs_raw:
        shared_jsonl_hours, tokens_by_day, scanned_dirs, jsonl_all_ts = scan_jsonl(
            jsonl_dirs_raw, start, end, tz, with_tokens=args.with_tokens
        )

    results = {}
    commit_hours_per_author: dict = {}
    for author in args.author:
        commits = fetch_commits(args.repo, author, start, end, tz)
        commit_hours_per_author[author] = commit_hours_by_day(commits, tz)
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
            'commit_hours_by_day': {
                str(d): hrs for d, hrs in commit_hours_per_author[author].items()
            },
        }

    # Compute JSONL active clock-hours by day (operator-level, for sync expansion)
    jsonl_hours_by_day: dict = {}
    if jsonl_all_ts:
        by_day_set: dict = defaultdict(set)
        for ts in jsonl_all_ts:
            local = ts.astimezone(tz)
            by_day_set[local.date()].add(local.hour)
        jsonl_hours_by_day = {str(d): sorted(h) for d, h in by_day_set.items()}

    output = {
        'window': {'start': str(start), 'end': str(end)},
        'authors': results,
        'jsonl_dirs_scanned': [str(d) for d in scanned_dirs],
        'jsonl_hours_by_day': jsonl_hours_by_day,
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
        if args.sync_output:
            _write_sync_file(args, output, start, end, tz)
        return

    if args.sync_output:
        _write_sync_file(args, output, start, end, tz)

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
