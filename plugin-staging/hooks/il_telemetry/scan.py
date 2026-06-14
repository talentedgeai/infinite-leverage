"""
Retroactive transcript scanner.

Walks ~/.claude/projects/, finds every .jsonl transcript that has not yet been
delivered, decodes the project path, resolves the git remote, checks registration,
and writes a capture record to the outbox — exactly like stop.py does for the
live session, but covering every past closed session.

Triggered by session-telemetry-end on every SessionEnd / SessionStart so that
any session that ended without a Stop (crash, force-quit, etc.) still gets
captured on the next open.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# ── Path constants (mirror stop.py / flush.py) ────────────────────────────────
PROJECTS_DIR  = Path.home() / ".claude" / "projects"
OUTBOX        = Path.home() / ".claude" / ".il-telemetry" / "outbox"
SCANNED_DIR   = Path.home() / ".claude" / ".il-telemetry" / "scanned"   # processed markers
SKIP_DIR      = Path.home() / ".claude" / ".il-telemetry" / "skip"       # unresolvable / unregistered

# ── Project-path decoder ──────────────────────────────────────────────────────

def _decode_project_path(dir_name: str) -> Path | None:
    """
    Convert a Claude Code project dir name back to its filesystem path.

    Claude encodes paths by replacing every '/' with '-' and prepending '-'.
    e.g.  /Applications/E8/client/work-healthy/OCCUSPAN
          → -Applications-E8-client-work-healthy-OCCUSPAN

    Ambiguity: a literal '-' in the path is indistinguishable from the separator.
    We resolve it with a DFS guided by filesystem existence checks: at each '-',
    try treating it as '/' first; fall back to literal '-' if the slash version
    doesn't exist as a directory.  For the leaf segment we accept either form if
    the full path exists (it doesn't have to be a directory itself).
    """
    if not dir_name.startswith('-'):
        return None
    parts = dir_name[1:].split('-')
    if not parts or not parts[0]:
        return None

    def search(idx: int, current: str) -> str | None:
        if idx == len(parts):
            p = Path('/' + current)
            return str(p) if p.exists() else None
        slash = current + '/' + parts[idx]
        dash  = current + '-'  + parts[idx]
        # Prefer slash (was a real path separator); only fall back to dash if the
        # slash candidate doesn't exist as an intermediate directory.
        for candidate in (slash, dash):
            if Path('/' + candidate).exists():
                result = search(idx + 1, candidate)
                if result:
                    return result
        # Neither intermediate path exists yet — recurse anyway (leaf may exist)
        for candidate in (slash, dash):
            result = search(idx + 1, candidate)
            if result:
                return result
        return None

    raw = search(1, parts[0])
    return Path(raw) if raw else None


def _git_remote(path: Path) -> str | None:
    """Return 'owner/repo' for the git repo at *path*, or None."""
    try:
        url = subprocess.check_output(
            ['git', '-C', str(path), 'remote', 'get-url', 'origin'],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip().removesuffix('.git')
        if 'github.com/' in url:
            return url.split('github.com/')[-1]
        if 'github.com:' in url:
            return url.split('github.com:')[-1]
    except Exception:
        pass
    return None


# ── Processed-marker helpers ──────────────────────────────────────────────────

def _already_handled(session_id: str) -> bool:
    """True if this session was already queued, delivered, or permanently skipped."""
    return (
        (OUTBOX    / f"{session_id}.json").exists() or
        (SCANNED_DIR / session_id).exists() or
        (SKIP_DIR    / session_id).exists()
    )

def _mark_scanned(session_id: str) -> None:
    SCANNED_DIR.mkdir(parents=True, exist_ok=True)
    (SCANNED_DIR / session_id).touch()

def _mark_skip(session_id: str) -> None:
    SKIP_DIR.mkdir(parents=True, exist_ok=True)
    (SKIP_DIR / session_id).touch()


# ── Core scanner ──────────────────────────────────────────────────────────────

def scan_all() -> dict:
    """
    Walk every project dir, find unprocessed transcripts, capture and queue them.
    Returns a summary dict {scanned, queued, skipped, errors}.
    """
    from il_telemetry.capture  import capture_session
    from il_telemetry.context  import gather_context
    from il_telemetry.outbox   import write_record
    from il_telemetry.registration import is_registered

    results = dict(scanned=0, queued=0, skipped=0, errors=0)

    if not PROJECTS_DIR.exists():
        return results

    saved_cwd = os.getcwd()

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        # Skip worktree / nested dirs (contain another '-' segment mid-way)
        project_path = _decode_project_path(project_dir.name)
        if not project_path:
            continue

        repo = _git_remote(project_path)
        if not repo or '/' not in repo:
            continue

        if not is_registered(repo):
            continue

        for transcript in sorted(project_dir.glob('*.jsonl')):
            session_id = transcript.stem
            results['scanned'] += 1

            if _already_handled(session_id):
                continue

            try:
                os.chdir(str(project_path))
                metrics = capture_session(str(transcript), session_id)
                if not metrics:
                    _mark_skip(session_id)
                    results['skipped'] += 1
                    continue

                context = gather_context()
                if not context.get('repo_full_name') or '/' not in context['repo_full_name']:
                    _mark_skip(session_id)
                    results['skipped'] += 1
                    continue

                write_record(OUTBOX, {**metrics, **context})
                _mark_scanned(session_id)
                results['queued'] += 1
            except Exception:
                results['errors'] += 1
            finally:
                try:
                    os.chdir(saved_cwd)
                except Exception:
                    pass

    return results


def main() -> None:
    try:
        results = scan_all()
        if results['queued'] > 0:
            print(
                f"[telemetry] scan: queued {results['queued']} past session(s) "
                f"({results['skipped']} skipped, {results['errors']} errors)"
            )
    except Exception:
        pass   # scanner must never crash the session


if __name__ == '__main__':
    main()
