"""
Tests for migrate_v1.py — the one-time v1 residue cleanup.

The invariant under test: ONLY byte-exact copies of files v1 actually shipped
are removed. Anything modified, symlinked, or unknown is reported and left.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "migrate_v1", Path(__file__).parent / "migrate_v1.py")
mig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mig)


def _h(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _setup(tmp_path, monkeypatch, manifest: dict):
    claude = tmp_path / ".claude"
    claude.mkdir()
    monkeypatch.setattr(mig, "CLAUDE", claude)
    monkeypatch.setattr(mig, "MARKER", claude / ".il-telemetry" / "v2-migrated")
    monkeypatch.setattr(mig, "LOG", claude / "il-v2-migration.log")
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps(manifest))
    monkeypatch.setattr(mig, "MANIFEST", mpath)
    return claude


def _empty_manifest(**over):
    base = {"agents": {}, "hooks": {}, "telemetry_files": {}, "rules": {}, "skills": {}}
    base.update(over)
    return base


# ── hash-gated file removal ──────────────────────────────────────────────────

def test_removes_exact_v1_agent_keeps_modified(tmp_path, monkeypatch):
    v1 = "# developer agent v1\n"
    claude = _setup(tmp_path, monkeypatch,
                    _empty_manifest(agents={"developer.md": [_h(v1)],
                                            "qa.md": [_h("# qa v1\n")]}))
    agents = claude / "agents"
    agents.mkdir()
    (agents / "developer.md").write_text(v1)                 # exact v1 → removed
    (agents / "qa.md").write_text("# qa v1 — my edits\n")    # modified → kept
    mig.main()
    assert not (agents / "developer.md").exists()
    assert (agents / "qa.md").exists()
    log = (claude / "il-v2-migration.log").read_text()
    assert "developer.md" in log and "qa.md" in log


def test_removes_hash_matched_skill_dir(tmp_path, monkeypatch):
    v1 = "---\nname: dev-tdd\n---\nv1 body\n"
    claude = _setup(tmp_path, monkeypatch, _empty_manifest(skills={"dev-tdd": [_h(v1)]}))
    d = claude / "skills" / "dev-tdd"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(v1)
    (d / "references.md").write_text("extra file — still removed with the dir")
    mig.main()
    assert not d.exists()


def test_keeps_modified_skill_and_symlinked_skill(tmp_path, monkeypatch):
    claude = _setup(tmp_path, monkeypatch,
                    _empty_manifest(skills={"dev-tdd": [_h("v1")], "code-review": [_h("v1")]}))
    skills = claude / "skills"
    modified = skills / "dev-tdd"
    modified.mkdir(parents=True)
    (modified / "SKILL.md").write_text("user's own rewrite")
    target = tmp_path / "real-store" / "code-review"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("v1")                    # even exact content:
    (skills / "code-review").symlink_to(target)               # symlink → never touched
    mig.main()
    assert modified.exists()
    assert (skills / "code-review").is_symlink()
    assert target.exists()


def test_telemetry_pkg_removed_only_when_fully_known(tmp_path, monkeypatch):
    v1_stop = "print('v1 stop')\n"
    claude = _setup(tmp_path, monkeypatch,
                    _empty_manifest(telemetry_files={"stop.py": [_h(v1_stop)]}))
    d = claude / "hooks" / "il_telemetry"
    d.mkdir(parents=True)
    (d / "stop.py").write_text(v1_stop)
    (d / "local_patch.py").write_text("site-local change")     # stray → whole dir kept
    mig.main()
    assert d.exists()


# ── settings surgery ─────────────────────────────────────────────────────────

def test_permissions_cleanup(tmp_path, monkeypatch):
    claude = _setup(tmp_path, monkeypatch, _empty_manifest())
    s = claude / "settings.local.json"
    s.write_text(json.dumps({"permissions": {
        "allow": ["Bash(*)", "WebFetch", "Skill(*)"],
        "defaultMode": "acceptEdits"}}))
    mig.main()
    data = json.loads(s.read_text())
    assert data["permissions"]["allow"] == ["WebFetch", "Skill(*)"]
    assert "defaultMode" not in data["permissions"]


def test_hook_registration_cleanup_keeps_foreign_hooks(tmp_path, monkeypatch):
    claude = _setup(tmp_path, monkeypatch, _empty_manifest())
    s = claude / "settings.json"
    s.write_text(json.dumps({"hooks": {
        "SessionStart": [
            {"hooks": [{"type": "command",
                        "command": "bash ~/.claude/hooks/session-start 2>/dev/null || true"}]},
            {"hooks": [{"type": "command", "command": "my-own-hook.sh"}]},
        ],
        "Stop": [
            {"hooks": [
                {"type": "command", "command": "bash ~/.claude/hooks/session-telemetry-stop"},
            ]},
        ]}}))
    mig.main()
    data = json.loads(s.read_text())
    assert data["hooks"]["SessionStart"] == [
        {"hooks": [{"type": "command", "command": "my-own-hook.sh"}]}]
    assert "Stop" not in data["hooks"]


# ── run-once + report mode ───────────────────────────────────────────────────

def test_marker_prevents_second_run(tmp_path, monkeypatch):
    v1 = "v1 agent\n"
    claude = _setup(tmp_path, monkeypatch, _empty_manifest(agents={"qa.md": [_h(v1)]}))
    mig.main()                                               # first run writes marker
    agents = claude / "agents"
    agents.mkdir()
    (agents / "qa.md").write_text(v1)
    mig.main()                                               # second run: no-op
    assert (agents / "qa.md").exists()


def test_report_mode_changes_nothing(tmp_path, monkeypatch, capsys):
    v1 = "v1 agent\n"
    claude = _setup(tmp_path, monkeypatch, _empty_manifest(agents={"qa.md": [_h(v1)]}))
    agents = claude / "agents"
    agents.mkdir()
    (agents / "qa.md").write_text(v1)
    monkeypatch.setattr(sys, "argv", ["migrate_v1.py", "--report"])
    mig.main()
    assert (agents / "qa.md").exists()                       # nothing removed
    assert not (claude / ".il-telemetry" / "v2-migrated").exists()  # no marker
    assert "qa.md" in capsys.readouterr().out


def test_missing_manifest_is_a_noop(tmp_path, monkeypatch):
    claude = _setup(tmp_path, monkeypatch, _empty_manifest())
    mig.MANIFEST.unlink()
    agents = claude / "agents"
    agents.mkdir()
    (agents / "qa.md").write_text("anything")
    mig.main()
    assert (agents / "qa.md").exists()
    assert not (claude / ".il-telemetry" / "v2-migrated").exists()
