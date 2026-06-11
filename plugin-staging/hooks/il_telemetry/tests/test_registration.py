"""
Tests for il_telemetry.registration — delivery gate + marker logic.

Mirrors the existing pytest style in test_deliver.py / test_flush.py:
- Mock HTTP calls and filesystem via monkeypatch / tmp_path.
- Never touch real network or real ~/.claude/.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

import il_telemetry.registration as reg


# ─── helpers ───────────────────────────────────────────────────────────────

def _make_response(body: dict, status: int = 200):
    """Return a context-manager mock that mimics urllib.request.urlopen."""
    m = MagicMock()
    m.__enter__ = MagicMock(return_value=m)
    m.__exit__ = MagicMock(return_value=False)
    m.read.return_value = json.dumps(body).encode()
    m.status = status
    return m


# ─── marker path ────────────────────────────────────────────────────────────

def test_marker_path_replaces_slash(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    p = reg._marker_path("owner/repo")
    assert p == tmp_path / "owner__repo"


# ─── is_registered ──────────────────────────────────────────────────────────

def test_registered_repo_returns_true(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": True})):
        assert reg.is_registered("owner/repo") is True


def test_unregistered_repo_returns_false(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": False})):
        assert reg.is_registered("owner/repo") is False


def test_network_error_fails_safe(tmp_path, monkeypatch):
    """Any network exception must return False (fail safe = skip delivery, never crash)."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        result = reg.is_registered("owner/repo")
    assert result is False


def test_unexpected_exception_fails_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", side_effect=Exception("unexpected")):
        result = reg.is_registered("owner/repo")
    assert result is False


def test_local_marker_short_circuits_network(tmp_path, monkeypatch):
    """If marker exists, return False without making any HTTP call."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    reg.mark_unregistered("owner/repo")

    with patch("urllib.request.urlopen") as mock_open:
        result = reg.is_registered("owner/repo")

    assert result is False
    mock_open.assert_not_called()


def test_empty_repo_returns_false_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen") as mock_open:
        result = reg.is_registered("")
    assert result is False
    mock_open.assert_not_called()


def test_repo_without_slash_returns_false(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen") as mock_open:
        result = reg.is_registered("nodash")
    assert result is False
    mock_open.assert_not_called()


# ─── mark_unregistered ──────────────────────────────────────────────────────

def test_mark_unregistered_creates_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    reg.mark_unregistered("alice/myrepo")
    assert (tmp_path / "alice__myrepo").exists()


def test_mark_unregistered_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    reg.mark_unregistered("alice/myrepo")
    reg.mark_unregistered("alice/myrepo")  # second call must not error
    assert (tmp_path / "alice__myrepo").exists()


# ─── check_and_gate ─────────────────────────────────────────────────────────

def test_gate_registered_returns_true_no_marker(tmp_path, monkeypatch):
    """Registered repo: gate returns True, no marker is written."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": True})):
        result = reg.check_and_gate("owner/repo")
    assert result is True
    assert not (tmp_path / "owner__repo").exists()


def test_gate_unregistered_returns_false_and_writes_marker(tmp_path, monkeypatch):
    """Unregistered repo: gate returns False AND writes the marker file."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", return_value=_make_response({"registered": False})):
        result = reg.check_and_gate("owner/repo")
    assert result is False
    assert (tmp_path / "owner__repo").exists()


def test_gate_network_error_returns_false_no_crash(tmp_path, monkeypatch):
    """Network error: gate returns False (fail safe). No exception propagates."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    with patch("urllib.request.urlopen", side_effect=Exception("network down")):
        result = reg.check_and_gate("owner/repo")
    assert result is False


def test_gate_second_call_uses_marker(tmp_path, monkeypatch):
    """Second call for same unregistered repo must skip the HTTP probe."""
    monkeypatch.setattr(reg, "_MARKER_BASE", tmp_path)
    call_count = {"n": 0}

    def fake_open(*a, **kw):
        call_count["n"] += 1
        return _make_response({"registered": False})

    with patch("urllib.request.urlopen", side_effect=fake_open):
        reg.check_and_gate("owner/repo")  # first call — hits network
        reg.check_and_gate("owner/repo")  # second call — marker hit

    assert call_count["n"] == 1  # network called exactly once


# ─── flush.py integration ───────────────────────────────────────────────────

def test_flush_skips_unregistered_repo(tmp_path, monkeypatch):
    """flush.main skips delivery when check_and_gate returns False."""
    import sys, io, json as _json
    import il_telemetry.flush as flush_mod

    delivered = []

    def fake_deliver(gh, record):
        delivered.append(record)
        return True

    monkeypatch.setattr(flush_mod, "deliver_record", fake_deliver)
    monkeypatch.setattr(flush_mod, "check_and_gate", lambda repo: False)
    # Patch _human_records_for_cwd to return a fake record
    monkeypatch.setattr(flush_mod, "_human_records_for_cwd", lambda cwd: [{
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
    }])
    # Patch pending_records to empty so only human path runs
    monkeypatch.setattr(flush_mod, "pending_records", lambda d: [])

    stdin_data = _json.dumps({"cwd": "/fake/cwd"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_data))
    flush_mod.main()

    assert delivered == []  # gate blocked delivery


def test_flush_delivers_registered_repo(tmp_path, monkeypatch):
    """flush.main delivers when check_and_gate returns True."""
    import sys, io, json as _json
    import il_telemetry.flush as flush_mod

    delivered = []

    def fake_deliver(gh, record):
        delivered.append(record)
        return True

    monkeypatch.setattr(flush_mod, "deliver_record", fake_deliver)
    monkeypatch.setattr(flush_mod, "check_and_gate", lambda repo: True)
    monkeypatch.setattr(flush_mod, "_human_records_for_cwd", lambda cwd: [{
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
    }])
    monkeypatch.setattr(flush_mod, "pending_records", lambda d: [])

    stdin_data = _json.dumps({"cwd": "/fake/cwd"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_data))
    flush_mod.main()

    assert len(delivered) == 1
