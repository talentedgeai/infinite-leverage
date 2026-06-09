import json, subprocess
from pathlib import Path
from il_telemetry.outbox import pending_records, mark_delivered
from il_telemetry.deliver import deliver_record

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

def main() -> None:
    try:
        for rec in pending_records(OUTBOX):
            try:
                repo = rec.get("repo_full_name") or ""
                if "/" not in repo:
                    continue
                owner, name = repo.split("/", 1)
                if deliver_record(gh_api, {**rec, "client_slug": owner, "project_slug": name}):
                    mark_delivered(OUTBOX, rec.get("session_id", ""))
            except Exception:
                continue
    except Exception:
        return

if __name__ == "__main__":
    main()
