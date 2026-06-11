#!/usr/bin/env python3
"""
team-hours.py — compute per-author engineering hours over a window using three
independent bases, then resolve a single "best-evidence" number per day.

Bases
-----
1. git-hours (strict):    standard open-source heuristic. Walks each author's
                          commit timeline. Continuous work = gaps < MAX_GAP.
                          Credit SESSION_START_CREDIT at each session start.
                          Knobs: MAX_GAP=2h, SESSION_START_CREDIT=30 min.

2. commit-span:           per calendar day, hours = (last_commit - first_commit)
                          + SESSION_START_CREDIT. Captures long supervision
                          stretches that the 2h cap eats. Zero on days with
                          no commits.

3. claude-jsonl:          reads ~/.claude/projects/*<keyword>*/**/*.jsonl,
                          extracts timestamps, applies a 5-minute-gap session
                          definition. Captures days where the author worked
                          but did not commit (sub-agent supervision, planning,
                          reading). Limited to activity in this Claude folder.

Resolution
----------
Per calendar day in the window:
  resolved_hours[day] = max(commit-span[day], claude-jsonl[day])
total = sum(resolved_hours[day] for day in window)

Rationale: each basis fails differently. Commit-span misses no-commit days.
Claude-jsonl misses non-Claude work (IDE-only edits, offline reading).
Taking the per-day max prefers whichever basis had evidence that day.

CLI
---
  python3 scripts/team-hours.py \\
      --start 2026-05-25 --end 2026-05-29 \\
      --author "TracNg99" --author "James Murray" \\
      --jsonl-keyword longev --jsonl-keyword wha \\
      --tz +07:00 \\
      [--repo /path/to/repo] [--no-jsonl] [--json]

Outputs a markdown summary table by default, or JSON with --json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_MAX_GAP = dt.timedelta(hours=2)
DEFAULT_JSONL_GAP = dt.timedelta(minutes=5)
DEFAULT_SESSION_CREDIT = dt.timedelta(minutes=30)


def parse_tz(s: str) -> dt.tzinfo:
    sign = 1 if s[0] == "+" else -1
    h, m = s[1:].split(":")
    return dt.timezone(sign * dt.timedelta(hours=int(h), minutes=int(m)))


def git_commit_times(repo: Path, author: str, start: dt.datetime, end: dt.datetime) -> list[dt.datetime]:
    cmd = [
        "git", "-C", str(repo), "log",
        f"--author={author}",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
        "--no-merges",
        "--pretty=format:%aI",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    times = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        times.append(dt.datetime.fromisoformat(line).astimezone(start.tzinfo))
    return sorted(times)


def git_hours_strict(times: list[dt.datetime],
                     max_gap: dt.timedelta = DEFAULT_MAX_GAP,
                     credit: dt.timedelta = DEFAULT_SESSION_CREDIT) -> float:
    if not times:
        return 0.0
    total = credit
    for prev, curr in zip(times, times[1:]):
        gap = curr - prev
        total += gap if gap < max_gap else credit
    return total.total_seconds() / 3600


def commit_span_per_day(times: list[dt.datetime],
                        credit: dt.timedelta = DEFAULT_SESSION_CREDIT) -> dict[dt.date, float]:
    by_day: dict[dt.date, list[dt.datetime]] = defaultdict(list)
    for t in times:
        by_day[t.date()].append(t)
    out: dict[dt.date, float] = {}
    for day, lst in by_day.items():
        span = (max(lst) - min(lst)) + credit
        out[day] = span.total_seconds() / 3600
    return out


def claude_jsonl_events(jsonl_keywords: list[str],
                        start: dt.datetime, end: dt.datetime,
                        projects_root: Path) -> list[dt.datetime]:
    if not projects_root.exists():
        return []
    dirs = set()
    for kw in jsonl_keywords:
        dirs.update(projects_root.glob(f"*{kw}*"))
    times: list[dt.datetime] = []
    for d in dirs:
        if not d.is_dir():
            continue
        for jf in d.rglob("*.jsonl"):
            try:
                with open(jf) as f:
                    for line in f:
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        ts = obj.get("timestamp") or obj.get("created_at") or obj.get("time")
                        if not ts:
                            continue
                        try:
                            t = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                        except Exception:
                            continue
                        t_local = t.astimezone(start.tzinfo)
                        if start <= t_local < end:
                            times.append(t_local)
            except OSError:
                continue
    return sorted(times)


def claude_tokens_per_day(jsonl_keywords: list[str],
                          start: dt.datetime, end: dt.datetime,
                          projects_root: Path) -> dict[dt.date, dict[str, int]]:
    """Aggregate Claude token usage per day from JSONL transcripts.

    Returns per-day dict of: input, output, cache_creation, cache_read, billed, total.
    billed = input + output + cache_creation (what you pay for).
    total  = billed + cache_read (the full token volume processed).
    """
    if not projects_root.exists():
        return {}
    dirs = set()
    for kw in jsonl_keywords:
        dirs.update(projects_root.glob(f"*{kw}*"))
    by_day: dict[dt.date, dict[str, int]] = {}
    for d in dirs:
        if not d.is_dir():
            continue
        for jf in d.rglob("*.jsonl"):
            try:
                with open(jf) as f:
                    for line in f:
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        ts = obj.get("timestamp") or obj.get("created_at") or obj.get("time")
                        if not ts:
                            continue
                        try:
                            t = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                        except Exception:
                            continue
                        t_local = t.astimezone(start.tzinfo)
                        if not (start <= t_local < end):
                            continue
                        u = (obj.get("message") or {}).get("usage") or obj.get("usage") or {}
                        if not u:
                            continue
                        day = t_local.date()
                        bucket = by_day.setdefault(day, {
                            "input": 0, "output": 0,
                            "cache_creation": 0, "cache_read": 0,
                        })
                        bucket["input"] += int(u.get("input_tokens", 0) or 0)
                        bucket["output"] += int(u.get("output_tokens", 0) or 0)
                        bucket["cache_creation"] += int(u.get("cache_creation_input_tokens", 0) or 0)
                        bucket["cache_read"] += int(u.get("cache_read_input_tokens", 0) or 0)
            except OSError:
                continue
    for day, b in by_day.items():
        b["billed"] = b["input"] + b["output"] + b["cache_creation"]
        b["total"] = b["billed"] + b["cache_read"]
    return by_day


def jsonl_hours_per_day(times: list[dt.datetime],
                        gap: dt.timedelta = DEFAULT_JSONL_GAP,
                        credit: dt.timedelta = DEFAULT_SESSION_CREDIT) -> dict[dt.date, float]:
    if not times:
        return {}
    by_day: dict[dt.date, list[dt.datetime]] = defaultdict(list)
    for t in times:
        by_day[t.date()].append(t)
    out: dict[dt.date, float] = {}
    for day, lst in by_day.items():
        lst = sorted(lst)
        active = dt.timedelta()
        sess_start = lst[0]
        last = lst[0]
        sessions = 1
        for t in lst[1:]:
            if t - last <= gap:
                last = t
            else:
                active += last - sess_start
                sessions += 1
                sess_start = t
                last = t
        active += last - sess_start
        total = active + credit * sessions
        out[day] = total.total_seconds() / 3600
    return out


def daterange(start: dt.datetime, end: dt.datetime) -> list[dt.date]:
    days = []
    d = start.date()
    last = (end - dt.timedelta(seconds=1)).date()
    while d <= last:
        days.append(d)
        d += dt.timedelta(days=1)
    return days


def resolve_hours(commit_span: dict[dt.date, float],
                  jsonl: dict[dt.date, float],
                  days: list[dt.date]) -> tuple[float, dict[dt.date, dict[str, float]]]:
    detail: dict[dt.date, dict[str, float]] = {}
    total = 0.0
    for d in days:
        cs = commit_span.get(d, 0.0)
        jl = jsonl.get(d, 0.0)
        chosen = max(cs, jl)
        if chosen <= 0:
            continue
        source = "commit-span" if cs >= jl else "claude-jsonl"
        detail[d] = {"commit_span": cs, "jsonl": jl, "resolved": chosen, "source": source}
        total += chosen
    return total, detail


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--author", action="append", required=True, help="git author name (repeatable)")
    p.add_argument("--jsonl-keyword", action="append", default=[], help="match Claude project dirs (repeatable)")
    p.add_argument("--tz", default="+00:00", help="local TZ offset like +07:00")
    p.add_argument("--repo", default=".", help="git repo path")
    p.add_argument("--projects-root", default=str(Path.home() / ".claude/projects"),
                   help="Claude projects root")
    p.add_argument("--no-jsonl", action="store_true", help="skip Claude JSONL basis")
    p.add_argument("--with-tokens", action="store_true",
                   help="also aggregate Claude tokens per day (operator total, not per-author)")
    p.add_argument("--json", action="store_true", help="output JSON instead of markdown")
    args = p.parse_args()

    tz = parse_tz(args.tz)
    start = dt.datetime.fromisoformat(args.start).replace(tzinfo=tz)
    end_inclusive = dt.datetime.fromisoformat(args.end).replace(tzinfo=tz)
    end_exclusive = end_inclusive + dt.timedelta(days=1)
    days = daterange(start, end_exclusive)
    repo = Path(args.repo).resolve()
    projects_root = Path(args.projects_root)

    report: dict[str, dict] = {}
    for author in args.author:
        commit_times = git_commit_times(repo, author, start, end_exclusive)
        git_h = git_hours_strict(commit_times)
        span_per_day = commit_span_per_day(commit_times)
        span_total = sum(span_per_day.values())

        jl_per_day: dict[dt.date, float] = {}
        if not args.no_jsonl and args.jsonl_keyword:
            jl_events = claude_jsonl_events(args.jsonl_keyword, start, end_exclusive, projects_root)
            jl_per_day = jsonl_hours_per_day(jl_events)
        jl_total = sum(jl_per_day.values())

        resolved_total, resolved_detail = resolve_hours(span_per_day, jl_per_day, days)

        report[author] = {
            "commits": len(commit_times),
            "git_hours_strict": round(git_h, 2),
            "commit_span_total": round(span_total, 2),
            "jsonl_total": round(jl_total, 2),
            "resolved_total": round(resolved_total, 2),
            "per_day": {
                d.isoformat(): {
                    "commit_span": round(span_per_day.get(d, 0.0), 2),
                    "jsonl": round(jl_per_day.get(d, 0.0), 2),
                    "resolved": round(resolved_detail.get(d, {}).get("resolved", 0.0), 2),
                    "source": resolved_detail.get(d, {}).get("source", ""),
                } for d in days
            },
        }

    tokens_per_day: dict[dt.date, dict[str, int]] = {}
    if args.with_tokens and not args.no_jsonl and args.jsonl_keyword:
        tokens_per_day = claude_tokens_per_day(args.jsonl_keyword, start, end_exclusive, projects_root)

    if args.json:
        out = {"window": {"start": args.start, "end": args.end}, "authors": report}
        if tokens_per_day:
            out["tokens_per_day"] = {d.isoformat(): v for d, v in sorted(tokens_per_day.items())}
        print(json.dumps(out, indent=2))
        return 0

    print(f"# Team hours · {args.start} → {args.end}\n")
    print("| Author | Commits | git-hours (strict) | commit-span sum | claude-jsonl sum | **Resolved** |")
    print("|---|---:|---:|---:|---:|---:|")
    for a, r in report.items():
        print(f"| {a} | {r['commits']} | {r['git_hours_strict']} | "
              f"{r['commit_span_total']} | {r['jsonl_total']} | **{r['resolved_total']}** |")
    print()
    for a, r in report.items():
        print(f"## {a} — per-day detail\n")
        print("| Date | commit-span | claude-jsonl | resolved | source |")
        print("|---|---:|---:|---:|---|")
        for d, v in r["per_day"].items():
            if v["resolved"] <= 0:
                continue
            print(f"| {d} | {v['commit_span']} | {v['jsonl']} | "
                  f"**{v['resolved']}** | {v['source']} |")
        print()

    if tokens_per_day:
        print("## Claude tokens per day (operator total — not per-author)\n")
        print("| Date | input | output | cache_creation | cache_read | **billed** | total |")
        print("|---|---:|---:|---:|---:|---:|---:|")
        for d, v in sorted(tokens_per_day.items()):
            print(f"| {d} | {v['input']:,} | {v['output']:,} | {v['cache_creation']:,} | "
                  f"{v['cache_read']:,} | **{v['billed']:,}** | {v['total']:,} |")
        totals = {k: sum(b[k] for b in tokens_per_day.values())
                  for k in ("input", "output", "cache_creation", "cache_read", "billed", "total")}
        print(f"| **window** | {totals['input']:,} | {totals['output']:,} | "
              f"{totals['cache_creation']:,} | {totals['cache_read']:,} | "
              f"**{totals['billed']:,}** | {totals['total']:,} |")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
