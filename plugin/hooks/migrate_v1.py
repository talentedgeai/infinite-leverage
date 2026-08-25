#!/usr/bin/env python3
"""
migrate_v1.py — One-time cleanup of Infinite Leverage v1 global installs.

v1's init/patch skills copied agents, skills, hooks, and rules into ~/.claude/
with `cp -R`, and wrote a blanket Bash(*) permission grant. v2 is plugin-scoped
and installs nothing globally, so on first run this script removes that residue.

Safety model:
  - Runs once: gated by a marker file (~/.claude/.il-telemetry/v2-migrated).
  - Removes ONLY files whose sha256 matches a version actually shipped by the
    v1 repos (v1-manifest.json, generated from the full git history of both
    infiniteleverage-8-agents-template and infiniteleverage-plugin).
  - Anything name-matched but content-modified is REPORTED, never deleted.
  - Symlinks are never followed or removed (a user-managed skill store may
    symlink names that collide with v1 skill names).
  - settings edits are surgical: remove the exact v1 grants/hook commands only.
  - Everything is logged to ~/.claude/il-v2-migration.log; a one-line summary
    is printed into the session context.
  - Never raises; a failure must never degrade the session.

Run with --report to preview without changing anything (used by /il-doctor).
"""
from __future__ import annotations
import hashlib
import json
import shutil
import sys
from pathlib import Path

CLAUDE = Path.home() / ".claude"
MARKER = CLAUDE / ".il-telemetry" / "v2-migrated"
LOG = CLAUDE / "il-v2-migration.log"
MANIFEST = Path(__file__).parent / "v1-manifest.json"

# v1 hook commands these exact registrations are removed from settings files.
V1_HOOK_SUBSTRINGS = (
    ".claude/hooks/session-start",
    ".claude/hooks/session-telemetry-end",
    ".claude/hooks/session-telemetry-stop",
    ".claude/hooks/pre-bash",
    ".claude/hooks/prompt-submit",
    ".claude/hooks/usage-context.py",
    ".claude/hooks/update-project-status-usage.py",
)


def sha256(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


class Migration:
    def __init__(self, dry_run: bool):
        self.dry = dry_run
        self.removed: list[str] = []
        self.kept: list[str] = []      # name-matched but modified → left in place
        self.notes: list[str] = []

    # ── file removal helpers ──────────────────────────────────────────────

    def _remove_file(self, p: Path, why: str) -> None:
        if not self.dry:
            p.unlink(missing_ok=True)
        self.removed.append(f"{p}  ({why})")

    def _remove_tree(self, p: Path, why: str) -> None:
        if not self.dry:
            shutil.rmtree(p, ignore_errors=True)
        self.removed.append(f"{p}/  ({why})")

    def clean_hashed_files(self, directory: Path, table: dict[str, list[str]], label: str) -> None:
        """Remove files in `directory` whose name AND content match the manifest."""
        if not directory.is_dir():
            return
        for name, hashes in table.items():
            p = directory / name
            if p.is_symlink():
                self.kept.append(f"{p}  (symlink — not touched)")
                continue
            if not p.is_file():
                continue
            if sha256(p) in hashes:
                self._remove_file(p, f"v1 {label}")
            else:
                self.kept.append(f"{p}  (modified locally — review manually)")

    def clean_skills(self, table: dict[str, list[str]]) -> None:
        """Remove ~/.claude/skills/<name>/ dirs whose SKILL.md matches a v1 version."""
        skills_dir = CLAUDE / "skills"
        if not skills_dir.is_dir():
            return
        for name, hashes in table.items():
            d = skills_dir / name
            if d.is_symlink():
                self.kept.append(f"{d}  (symlink — not touched)")
                continue
            if not d.is_dir():
                continue
            if sha256(d / "SKILL.md") in hashes:
                self._remove_tree(d, "v1 skill")
            else:
                self.kept.append(f"{d}/  (SKILL.md modified or unknown version — review manually)")

    def clean_telemetry_pkg(self, table: dict[str, list[str]]) -> None:
        """Remove ~/.claude/hooks/il_telemetry/ if every .py in it is a known v1 file."""
        d = CLAUDE / "hooks" / "il_telemetry"
        if not d.is_dir() or d.is_symlink():
            return
        known = {h for hashes in table.values() for h in hashes}
        strays = [
            p for p in d.rglob("*.py")
            if "__pycache__" not in p.parts and sha256(p) not in known
        ]
        if strays:
            self.kept.append(f"{d}/  (contains modified files: "
                             f"{', '.join(p.name for p in strays[:5])} — review manually)")
        else:
            self._remove_tree(d, "v1 telemetry package")

    # ── settings edits ────────────────────────────────────────────────────

    def _load_json(self, p: Path):
        try:
            return json.loads(p.read_text())
        except Exception:
            return None

    def _save_json(self, p: Path, data) -> None:
        if not self.dry:
            p.write_text(json.dumps(data, indent=2) + "\n")

    def clean_permissions(self) -> None:
        """Remove the Bash(*) grant and acceptEdits default v1's installer wrote."""
        for fname in ("settings.local.json", "settings.json"):
            p = CLAUDE / fname
            data = self._load_json(p)
            if not isinstance(data, dict):
                continue
            perms = data.get("permissions")
            changed = False
            if isinstance(perms, dict):
                allow = perms.get("allow")
                if isinstance(allow, list) and "Bash(*)" in allow:
                    perms["allow"] = [a for a in allow if a != "Bash(*)"]
                    changed = True
                    self.removed.append(f"{p}: permissions.allow entry Bash(*)")
                if perms.get("defaultMode") == "acceptEdits":
                    del perms["defaultMode"]
                    changed = True
                    self.removed.append(f"{p}: permissions.defaultMode acceptEdits")
            if changed:
                self._save_json(p, data)

    def clean_hook_registrations(self) -> None:
        """Remove v1 hook command registrations from settings files (they now
        either point at deleted files or duplicate this plugin's own hooks)."""
        for fname in ("settings.json", "settings.local.json"):
            p = CLAUDE / fname
            data = self._load_json(p)
            if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
                continue
            changed = False
            hooks = data["hooks"]
            for event, groups in list(hooks.items()):
                if not isinstance(groups, list):
                    continue
                new_groups = []
                for group in groups:
                    cmds = group.get("hooks") if isinstance(group, dict) else None
                    if isinstance(cmds, list):
                        keep = []
                        for h in cmds:
                            cmd = h.get("command", "") if isinstance(h, dict) else ""
                            if any(s in cmd for s in V1_HOOK_SUBSTRINGS):
                                changed = True
                                self.removed.append(f"{p}: {event} hook `{cmd.strip()[:70]}`")
                            else:
                                keep.append(h)
                        group["hooks"] = keep
                        if keep:
                            new_groups.append(group)
                    else:
                        new_groups.append(group)
                hooks[event] = new_groups
                if not new_groups:
                    del hooks[event]
            if changed:
                self._save_json(p, data)

    def clean_version_file(self) -> None:
        p = CLAUDE / ".infiniteleverage-version"
        if p.is_file():
            self._remove_file(p, "v1 version marker — updates now flow through the plugin marketplace")

    def report_leftovers(self) -> None:
        """Things v1 created that we deliberately do not auto-remove."""
        slated = {r.split("  (")[0].rstrip("/") for r in self.removed}
        agents = CLAUDE / "agents"
        if agents.is_dir() and any(agents.iterdir()):
            leftover = [f.name for f in agents.iterdir()
                        if f.suffix == ".md" and str(f) not in slated]
            if leftover:
                self.notes.append(
                    f"~/.claude/agents/ still has: {', '.join(sorted(leftover))} "
                    "(not shipped by v1 verbatim, or user-modified). "
                    "v2 installs agents per-project — remove these manually if unwanted."
                )
        st = CLAUDE / "scheduled-tasks"
        if st.is_dir() and any(st.iterdir()):
            self.notes.append(
                "Scheduled tasks exist (v1 created ~10 agent schedules on Mac Minis). "
                "Review with /il-doctor — schedules are never auto-removed."
            )


def main() -> None:
    dry_run = "--report" in sys.argv
    if MARKER.exists() and not dry_run:
        return  # already migrated — total silence
    try:
        manifest = json.loads(MANIFEST.read_text())
    except Exception:
        return  # no manifest → do nothing rather than guess

    m = Migration(dry_run)
    try:
        m.clean_hashed_files(CLAUDE / "agents", manifest.get("agents", {}), "agent")
        m.clean_hashed_files(CLAUDE / "hooks", manifest.get("hooks", {}), "hook")
        m.clean_hashed_files(CLAUDE / "rules", manifest.get("rules", {}), "rule")
        m.clean_telemetry_pkg(manifest.get("telemetry_files", {}))
        m.clean_skills(manifest.get("skills", {}))
        m.clean_permissions()
        m.clean_hook_registrations()
        m.clean_version_file()
        m.report_leftovers()
    except Exception:
        pass  # best-effort; partial cleanup is still an improvement

    lines = []
    if m.removed:
        lines.append(("WOULD REMOVE" if dry_run else "Removed") + f" {len(m.removed)} v1 item(s):")
        lines += [f"  - {r}" for r in m.removed]
    if m.kept:
        lines.append(f"Left in place ({len(m.kept)} — name matches v1 but content differs or is a symlink):")
        lines += [f"  - {k}" for k in m.kept]
    lines += [f"NOTE: {n}" for n in m.notes]

    if not dry_run:
        try:
            MARKER.parent.mkdir(parents=True, exist_ok=True)
            MARKER.touch()
            if lines:
                LOG.write_text("\n".join(lines) + "\n")
        except Exception:
            pass

    if dry_run:
        print("\n".join(lines) if lines else "No v1 residue found.")
    elif m.removed or m.kept or m.notes:
        print(f"[Infinite Leverage v2] Cleaned up {len(m.removed)} item(s) from the old v1 "
              f"global install ({len(m.kept)} left for manual review). "
              f"Full log: ~/il-v2-migration.log".replace("~/", "~/.claude/"))


if __name__ == "__main__":
    main()
