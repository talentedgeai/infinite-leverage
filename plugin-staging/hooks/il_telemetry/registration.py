"""
registration.py — Delivery gate for il_telemetry.

Checks whether the current repo is registered in the tracker before allowing
delivery. Uses a local "declined/seen" marker file so we don't re-probe on
every flush for the same unregistered repo.

All network failures are fail-safe: skip delivery (never crash, never block).
"""

import os
import urllib.request
import urllib.error
import json
from pathlib import Path

TRACKER_URL = os.environ.get("IL_TRACKER_URL", "https://human-token-tracker.vercel.app")
_MARKER_BASE = Path.home() / ".claude" / ".il-telemetry" / "unregistered"


def _marker_path(repo_full_name: str) -> Path:
    """~/.claude/.il-telemetry/unregistered/<owner>__<repo>"""
    safe = repo_full_name.replace("/", "__")
    return _MARKER_BASE / safe


def is_registered(repo_full_name: str) -> bool:
    """
    Return True if the repo is registered in the tracker.

    Probe order:
      1. If local marker exists → already known unregistered → return False immediately.
      2. GET {TRACKER_URL}/api/projects/status?repo=<repo> → parse {"registered": bool}.
      3. On any network/parse error → return False (fail safe = skip delivery).
    """
    if not repo_full_name or "/" not in repo_full_name:
        return False
    try:
        if _marker_path(repo_full_name).exists():
            return False
        url = f"{TRACKER_URL}/api/projects/status?repo={urllib.request.quote(repo_full_name, safe='/')}"
        req = urllib.request.Request(url, headers={"User-Agent": "il-telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
        return bool(body.get("registered", False))
    except Exception:
        return False


def mark_unregistered(repo_full_name: str) -> None:
    """Write the local declined/seen marker so future flushes skip the probe."""
    try:
        _MARKER_BASE.mkdir(parents=True, exist_ok=True)
        _marker_path(repo_full_name).touch()
    except Exception:
        pass


def check_and_gate(repo_full_name: str) -> bool:
    """
    Gate function: returns True if delivery should proceed, False if it should be
    skipped. Also writes the marker when the repo is found to be unregistered so
    subsequent calls short-circuit without a network probe.
    """
    registered = is_registered(repo_full_name)
    if not registered:
        # Only write marker if the repo string is valid (avoids marker for empty string)
        if repo_full_name and "/" in repo_full_name:
            # Don't stomp an already-existing marker (idempotent)
            if not _marker_path(repo_full_name).exists():
                mark_unregistered(repo_full_name)
    return registered
