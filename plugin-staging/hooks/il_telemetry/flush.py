import json, os, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
from il_telemetry.outbox import pending_records, mark_delivered
from il_telemetry.deliver import deliver_record
from il_telemetry import methodology
from il_telemetry.context import gather_context
from il_telemetry.registration import check_and_gate

OUTBOX = Path.home() / ".claude" / ".il-telemetry" / "outbox"
REPO = "talentedgeai/human-token-tracker"  # the CENTRAL repo the telemetry files live in

def gh_api(method, path, **kw):
    """Map `gh api` to (status, body). Coarse but safe: success→200; GET failure→404; PUT failure→409.
    Uses the contributor's existing gh auth — NO secret/token handled here."""
    url = f"repos/{REPO}/contents/{path}"
    try:
        if method == "GET":
            out = subprocess.run(["gh", "api", f"{url}?ref={kw.get('ref', 'telemetry')}"],
                                 capture_output=True, text=True, timeout=20)
            return (200, json.loads(out.stdout or "{}")) if out.returncode == 0 else (404, {})
        args = ["gh", "api", "-X", "PUT", url,
                "-f", f"message={kw.get('message', '')}",
                "-f", f"content={kw.get('content', '')}",
                "-f", f"branch={kw.get('branch', 'telemetry')}"]
        if kw.get("sha"):
            args += ["-f", f"sha={kw['sha']}"]
        out = subprocess.run(args, capture_output=True, text=True, timeout=20)
        return (200, json.loads(out.stdout or "{}")) if out.returncode == 0 else (409, {})
    except Exception:
        return (500, {})

def build_human_records(hh: dict, ctx: dict) -> list[dict]:
    """Per-day human-time records from a methodology.human_hours_for result. Pure; never raises on shape."""
    out = []
    for day, v in (hh.get("per_day") or {}).items():
        hours = (hh.get("commit_hours_by_day") or {}).get(day, [])
        first_hour = hours[0] if hours else 0  # first commit-hour, else midnight — matches team-hours.py occurred_at
        out.append({
            "record_type": "human",
            "occurred_on": day,
            "resolved_hours": v.get("resolved", 0.0),
            "source": v.get("source"),
            "commit_hours": hours,
            "author_email": ctx.get("author_email", ""),
            "github_login": ctx.get("github_login", ""),
            "repo_full_name": ctx.get("repo_full_name", ""),
            "started_at": f"{day}T{first_hour:02d}:00:00+00:00",
        })
    return out

def _human_records_for_cwd(cwd: str) -> list[dict]:
    """I/O: compute today+yesterday human hours for the current repo/author. Never raises."""
    try:
        os.chdir(cwd)
        ctx = gather_context()
        if "/" not in (ctx.get("repo_full_name") or "") or not ctx.get("author_email"):
            return []
        slug = cwd.replace("/", "-")
        today = date.today()
        tz = methodology.parse_tz(os.environ.get("IL_TZ", "+00:00"))
        hh = methodology.human_hours_for(cwd, ctx["author_email"], today - timedelta(days=1), today, tz, [slug])
        return build_human_records(hh, ctx)
    except Exception:
        return []

def main() -> None:
    cwd = None
    try:
        cwd = (json.load(sys.stdin) or {}).get("cwd")
    except Exception:
        cwd = None
    # 1) per-day human records (only when invoked with a repo cwd)
    if cwd:
        for rec in _human_records_for_cwd(cwd):
            try:
                repo = rec.get("repo_full_name") or ""
                if "/" not in repo:
                    continue
                if not check_and_gate(repo):
                    continue  # repo not registered — skip delivery silently
                owner, name = repo.split("/", 1)
                deliver_record(gh_api, {**rec, "client_slug": owner, "project_slug": name})
            except Exception:
                continue
    # 2) per-session claude records from the outbox
    for rec in pending_records(OUTBOX):
        try:
            repo = rec.get("repo_full_name") or ""
            if "/" not in repo:
                continue
            if not check_and_gate(repo):
                continue  # repo not registered — skip delivery silently
            owner, name = repo.split("/", 1)
            payload = {**rec, "record_type": "claude", "client_slug": owner, "project_slug": name}
            if deliver_record(gh_api, payload):
                mark_delivered(OUTBOX, rec.get("session_id", ""))
        except Exception:
            continue

if __name__ == "__main__":
    main()
