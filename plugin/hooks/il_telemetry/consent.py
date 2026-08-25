"""
consent.py — Explicit opt-in gate for il_telemetry.

v2 rule: telemetry NEVER captures or delivers anything unless the contributor
has explicitly opted in. Consent is stored as a single word in
~/.claude/.il-telemetry/consent — "granted" or "denied" — written by the
/il-doctor skill after asking the contributor directly.

No file, or any other content, means NOT granted (fail closed, silent).
"""
from __future__ import annotations
from pathlib import Path

CONSENT_PATH = Path.home() / ".claude" / ".il-telemetry" / "consent"


def has_consent() -> bool:
    """True only when the contributor explicitly opted in. Never raises."""
    try:
        return CONSENT_PATH.read_text().strip() == "granted"
    except Exception:
        return False


def consent_state() -> str:
    """'granted' | 'denied' | 'unset' — for /il-doctor reporting. Never raises."""
    try:
        v = CONSENT_PATH.read_text().strip()
        return v if v in ("granted", "denied") else "unset"
    except Exception:
        return "unset"


def set_consent(granted: bool) -> None:
    """Record the contributor's answer. Never raises."""
    try:
        CONSENT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONSENT_PATH.write_text("granted" if granted else "denied")
    except Exception:
        pass
