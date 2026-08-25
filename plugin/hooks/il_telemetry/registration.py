"""
registration.py — Delivery gate for il_telemetry.

Checks whether the current repo is registered in the tracker before allowing
delivery. Both outcomes are cached as marker files with a TTL so the network
probe runs at most once per repo per TTL window — never on every flush, and
(unlike v1) a repo that gets registered later starts flowing once the negative
marker expires instead of being silenced forever.

All network failures are fail-safe: skip delivery (never crash, never block).
"""

from __future__ import annotations
import os
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

TRACKER_URL = os.environ.get("IL_TRACKER_URL", "https://human-token-tracker.vercel.app")
_BASE = Path.home() / ".claude" / ".il-telemetry"
_UNREGISTERED = _BASE / "unregistered"
_REGISTERED = _BASE / "registered"
TTL_SECONDS = 7 * 24 * 3600  # re-probe weekly


def _marker(base: Path, repo_full_name: str) -> Path:
    return base / repo_full_name.replace("/", "__")


def _fresh(p: Path) -> bool:
    try:
        return p.exists() and (time.time() - p.stat().st_mtime) < TTL_SECONDS
    except Exception:
        return False


def _write_marker(base: Path, repo_full_name: str) -> None:
    try:
        base.mkdir(parents=True, exist_ok=True)
        _marker(base, repo_full_name).touch()
    except Exception:
        pass


def _probe(repo_full_name: str) -> bool | None:
    """Ask the tracker. True/False on an answer, None on network failure."""
    try:
        url = f"{TRACKER_URL}/api/projects/status?repo={urllib.request.quote(repo_full_name, safe='/')}"
        req = urllib.request.Request(url, headers={"User-Agent": "il-telemetry/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
        return bool(body.get("registered", False))
    except Exception:
        return None


def is_registered(repo_full_name: str) -> bool:
    """Cached registration check. Fail safe: unknown → False (skip delivery)."""
    if not repo_full_name or "/" not in repo_full_name:
        return False
    if _fresh(_marker(_REGISTERED, repo_full_name)):
        return True
    if _fresh(_marker(_UNREGISTERED, repo_full_name)):
        return False
    answer = _probe(repo_full_name)
    if answer is True:
        _write_marker(_REGISTERED, repo_full_name)
        try:  # clear a stale negative so state stays consistent
            _marker(_UNREGISTERED, repo_full_name).unlink(missing_ok=True)
        except Exception:
            pass
        return True
    if answer is False:
        _write_marker(_UNREGISTERED, repo_full_name)
    return False  # unregistered, or network failure → skip delivery


def mark_unregistered(repo_full_name: str) -> None:
    """Kept for callers/tests from v1: write the negative marker."""
    if repo_full_name and "/" in repo_full_name:
        _write_marker(_UNREGISTERED, repo_full_name)


def check_and_gate(repo_full_name: str) -> bool:
    """Gate function: True if delivery should proceed."""
    return is_registered(repo_full_name)
