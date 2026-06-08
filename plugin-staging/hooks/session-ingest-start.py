#!/usr/bin/env python3
"""
SessionStart → POST one billed hour to the ingest-session-start Edge Function.

Only acts in repos that contain `.claude/project.json` (i.e. instrumented repos).
Resolves the engineer by `git config user.email` — the function maps that to the
team member server-side. Idempotent: the function dedupes per (member, date, hour),
so multiple sessions in the same clock-hour record exactly one hour.

NEVER blocks or slows the session: every failure path is a silent return.

Secrets are read from the environment, falling back to ~/.claude/.env:
  SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL)
  SUPABASE_ANON_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY)
  INGEST_SECRET
None of these are ever committed.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def git_email(cwd: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", cwd, "config", "user.email"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def main() -> None:
    raw = ""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
    except Exception:
        raw = ""
    try:
        ev = json.loads(raw or "{}")
    except Exception:
        ev = {}

    cwd = ev.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cfg_path = Path(cwd) / ".claude" / "project.json"
    if not cfg_path.exists():
        return  # repo not instrumented — nothing to do

    cfg = json.loads(cfg_path.read_text())
    client_id = cfg.get("client_id")
    project_id = cfg.get("project_id")
    if not client_id:
        return

    load_env_file(Path.home() / ".claude" / ".env")
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    anon = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    secret = os.environ.get("INGEST_SECRET")
    if not (url and anon and secret):
        return

    email = git_email(cwd)
    if not email:
        return

    now = datetime.now().astimezone()  # local time → local date + hour
    payload = {
        "author_email": email,
        "client_id": client_id,
        "project_id": project_id,
        "primary_role": cfg.get("primary_role"),
        "occurred_on": now.strftime("%Y-%m-%d"),
        "occurred_hour": now.hour,
        # Precise git-pull / session-start instant (ISO-8601, tz-aware). Anchor for
        # the human-token metric; without it the function stores NULL and the metric
        # reads 0. See docs/architecture/session-ingest-contract.md (human-token-tracker).
        "started_at": now.isoformat(),
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/functions/v1/ingest-session-start",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer " + anon,
            "x-ingest-secret": secret,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5).read()
    except Exception:
        pass  # never degrade the session


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
