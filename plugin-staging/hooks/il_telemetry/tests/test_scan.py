"""Tests for il_telemetry.scan — path decoder and processed-marker helpers."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import patch
from pathlib import Path
from il_telemetry.scan import _decode_project_path


# ── _decode_project_path ──────────────────────────────────────────────────────

def test_simple_path(tmp_path):
    # /tmp/myproject
    proj = tmp_path / "myproject"
    proj.mkdir()
    encoded = f"-{str(tmp_path)[1:].replace('/', '-')}-myproject"
    result = _decode_project_path(encoded)
    assert result == proj


def test_hyphenated_segment(tmp_path):
    # /tmp/work-healthy/OCCUSPAN — hyphen inside a segment
    parent = tmp_path / "work-healthy"
    parent.mkdir()
    leaf = parent / "OCCUSPAN"
    leaf.mkdir()
    encoded = f"-{str(tmp_path)[1:].replace('/', '-')}-work-healthy-OCCUSPAN"
    result = _decode_project_path(encoded)
    assert result == leaf


def test_returns_none_for_nonexistent(tmp_path):
    encoded = "-does-not-exist-anywhere-on-this-machine"
    result = _decode_project_path(encoded)
    assert result is None


def test_returns_none_without_leading_dash():
    result = _decode_project_path("Applications-E8-client")
    assert result is None


def test_returns_none_for_empty():
    result = _decode_project_path("")
    assert result is None
