"""
Tests for il_telemetry.registration (v2: TTL-cached both ways) and
il_telemetry.consent (v2: explicit opt-in gate).

Style mirrors test_deliver.py / test_flush.py:
- Mock HTTP calls and filesystem via monkeypatch / tmp_path.
- Never touch real network or real ~/.claude/.
"""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

import il_telemetry.registration as reg
import il_telemetry.consent as consent


# ─── helpers ───────────────────────────────────────────────────────────────

def _make_response(body: dict, status: int = 200):
    """Return a context-manager mock that mimics urllib.request.urlopen."""
    m = MagicMock()
    m.__enter__ = MagicMock(return_value=m)
    m.__exit__ = MagicMock(return_value=False)
    m.read.return_value = json.dumps(body).encode()
    m.status = status
    return m


def _markers(tmp_path, monkeypatch):
    """Point both marker dirs into tmp_path; return (unreg, regd)."""
    unreg = tmp_path / "unregistered"
    regd = tmp_path / "registered"
    monkeypatch.setattr(reg, "_UNREGISTERED", unreg)
    monkeypatch.setattr(reg, "_REGISTERED", regd)
    return unreg, regd


def _age(marker: Path, seconds: int) -> None:
    old = time.time() - seconds
    os.utime(marker, (old, old))


# ─── is_registered: probe outcomes ──────────────────────────────────────────

def test_registered_repo_returns_true_and_caches(tmp_path, monkeypatch):
    unreg, regd = _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": True})):
        assert reg.is_registered("owner/repo") is True
    assert (regd / "owner__repo").exists()          # positive result cached
    assert not (unreg / "owner__repo").exists()


def test_unregistered_repo_returns_false_and_caches(tmp_path, monkeypatch):
    unreg, _ = _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": False})):
        assert reg.is_registered("owner/repo") is False
    assert (unreg / "owner__repo").exists()          # negative result cached


def test_network_error_fails_safe_and_does_not_cache(tmp_path, monkeypatch):
    """Network failure returns False but writes NO marker — next flush re-probes."""
    unreg, regd = _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        assert reg.is_registered("owner/repo") is False
    assert not (unreg / "owner__repo").exists()
    assert not (regd / "owner__repo").exists()


def test_unexpected_exception_fails_safe(tmp_path, monkeypatch):
    _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen", side_effect=Exception("unexpected")):
        assert reg.is_registered("owner/repo") is False


def test_empty_repo_returns_false_without_network(tmp_path, monkeypatch):
    _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen") as mock_open:
        assert reg.is_registered("") is False
    mock_open.assert_not_called()


def test_repo_without_slash_returns_false(tmp_path, monkeypatch):
    _markers(tmp_path, monkeypatch)
    with patch("urllib.request.urlopen") as mock_open:
        assert reg.is_registered("nodash") is False
    mock_open.assert_not_called()


# ─── marker caching + TTL ───────────────────────────────────────────────────

def test_fresh_negative_marker_short_circuits_network(tmp_path, monkeypatch):
    _markers(tmp_path, monkeypatch)
    reg.mark_unregistered("owner/repo")
    with patch("urllib.request.urlopen") as mock_open:
        assert reg.is_registered("owner/repo") is False
    mock_open.assert_not_called()


def test_fresh_positive_marker_short_circuits_network(tmp_path, monkeypatch):
    _, regd = _markers(tmp_path, monkeypatch)
    regd.mkdir(parents=True)
    (regd / "owner__repo").touch()
    with patch("urllib.request.urlopen") as mock_open:
        assert reg.is_registered("owner/repo") is True
    mock_open.assert_not_called()


def test_expired_negative_marker_reprobes(tmp_path, monkeypatch):
    """v1 silenced a repo forever once marked; v2 re-probes after the TTL."""
    unreg, regd = _markers(tmp_path, monkeypatch)
    reg.mark_unregistered("owner/repo")
    _age(unreg / "owner__repo", reg.TTL_SECONDS + 60)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": True})) as mock_open:
        assert reg.is_registered("owner/repo") is True
    mock_open.assert_called_once()
    assert (regd / "owner__repo").exists()
    assert not (unreg / "owner__repo").exists()      # stale negative cleared


def test_mark_unregistered_idempotent(tmp_path, monkeypatch):
    unreg, _ = _markers(tmp_path, monkeypatch)
    reg.mark_unregistered("alice/myrepo")
    reg.mark_unregistered("alice/myrepo")  # second call must not error
    assert (unreg / "alice__myrepo").exists()


def test_gate_second_call_uses_marker(tmp_path, monkeypatch):
    """Second call for the same unregistered repo must skip the HTTP probe."""
    _markers(tmp_path, monkeypatch)
    call_count = {"n": 0}

    def fake_open(*a, **kw):
        call_count["n"] += 1
        return _make_response({"registered": False})

    with patch("urllib.request.urlopen", side_effect=fake_open):
        reg.check_and_gate("owner/repo")  # first call — hits network
        reg.check_and_gate("owner/repo")  # second call — marker hit
    assert call_count["n"] == 1


# ─── consent gate ───────────────────────────────────────────────────────────

def test_consent_defaults_to_not_granted(tmp_path, monkeypatch):
    monkeypatch.setattr(consent, "CONSENT_PATH", tmp_path / "consent")
    assert consent.has_consent() is False
    assert consent.consent_state() == "unset"


def test_consent_granted_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(consent, "CONSENT_PATH", tmp_path / "consent")
    consent.set_consent(True)
    assert consent.has_consent() is True
    assert consent.consent_state() == "granted"


def test_consent_denied_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(consent, "CONSENT_PATH", tmp_path / "consent")
    consent.set_consent(False)
    assert consent.has_consent() is False
    assert consent.consent_state() == "denied"


def test_consent_garbage_content_fails_closed(tmp_path, monkeypatch):
    p = tmp_path / "consent"
    p.write_text("maybe?\n")
    monkeypatch.setattr(consent, "CONSENT_PATH", p)
    assert consent.has_consent() is False
    assert consent.consent_state() == "unset"


# ─── flush.py integration ───────────────────────────────────────────────────

def _fake_human_record():
    return {
        "record_type": "human",
        "repo_full_name": "owner/repo",
        "client_slug": "owner",
        "project_slug": "repo",
        "github_login": "alice",
        "started_at": "2026-06-09T09:00:00+00:00",
        "occurred_on": "2026-06-09",
        "resolved_hours": 1.0,
        "source": "commit-span",
        "commit_hours": [9],
        "author_email": "a@e.ai",
    }


def _run_flush(monkeypatch, *, consented: bool, registered: bool):
    import sys, io
    import il_telemetry.flush as flush_mod

    delivered = []
    monkeypatch.setattr(flush_mod, "has_consent", lambda: consented)
    monkeypatch.setattr(flush_mod, "deliver_record", lambda gh, r: delivered.append(r) or True)
    monkeypatch.setattr(flush_mod, "check_and_gate", lambda repo: registered)
    monkeypatch.setattr(flush_mod, "_human_records_for_cwd", lambda cwd: [_fake_human_record()])
    monkeypatch.setattr(flush_mod, "pending_records", lambda d: [])
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": "/fake/cwd"})))
    flush_mod.main()
    return delivered


def test_flush_delivers_with_consent_and_registration(monkeypatch):
    assert len(_run_flush(monkeypatch, consented=True, registered=True)) == 1


def test_flush_skips_unregistered_repo(monkeypatch):
    assert _run_flush(monkeypatch, consented=True, registered=False) == []


def test_flush_skips_without_consent(monkeypatch):
    """No opt-in → nothing delivered even for a registered repo."""
    assert _run_flush(monkeypatch, consented=False, registered=True) == []
