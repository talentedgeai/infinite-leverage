#!/usr/bin/env python3
"""
SessionEnd → POST human + Claude token totals to the ingest-session-end Edge Function.

Token method (documented approximation — see references in the SKILL):
  human_tokens  ≈ characters of HUMAN-authored text in the transcript / 4
                  (user `text` blocks only; tool_result blocks are excluded —
                   they are machine output, not keystrokes).
  claude_tokens  = sum of assistant `usage.output_tokens` (what Claude generated).

Only acts in repos with `.claude/project.json`. Resolves the engineer by
`git config user.email`. NEVER blocks the session: every failure path returns silently.

Secrets read from env, falling back to ~/.claude/.env (never committed):
  SUPABASE_URL / NEXT_PUBLIC_SUPABASE_URL, SUPABASE_ANON_KEY /
  NEXT_PUBLIC_SUPABASE_ANON_KEY, INGEST_SECRET.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
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


def parse_transcript(path: str) -> tuple[int, int]:
    """Return (human_chars, claude_output_tokens) from a Claude Code JSONL transcript."""
    human_chars = 0
    claude_tokens = 0
    try:
        for line in Path(path).read_text(errors="ignore").splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            msg = obj.get("message", {}) or {}
            role = msg.get("role") or obj.get("type")
            if role == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    human_chars += len(content)
                elif isinstance(content, list):
                    for c in content:
                        # Count only genuine text the human typed; skip tool_result etc.
                        if isinstance(c, dict) and c.get("type") == "text":
                            human_chars += len(c.get("text", "") or "")
            usage = msg.get("usage") or {}
            if usage:
                claude_tokens += int(usage.get("output_tokens", 0) or 0)
    except Exception:
        pass
    return human_chars // 4, claude_tokens


def main() -> None:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    except Exception:
        raw = "{}"
    try:
        ev = json.loads(raw or "{}")
    except Exception:
        ev = {}

    cwd = ev.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cfg_path = Path(cwd) / ".claude" / "project.json"
    if not cfg_path.exists():
        return
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

    transcript = ev.get("transcript_path")
    human_tokens, claude_tokens = parse_transcript(transcript) if transcript else (0, 0)
    if human_tokens == 0 and claude_tokens == 0:
        return  # nothing to record

    payload = {
        "author_email": email,
        "client_id": client_id,
        "project_id": project_id,
        "human_tokens": human_tokens,
        "claude_tokens": claude_tokens,
        "source": cfg.get("token_source", "pr_commit"),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/functions/v1/ingest-session-end",
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
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
