import base64
import json

REPO = "talentedgeai/human-token-tracker"
BRANCH = "telemetry"

def telemetry_path(client_slug: str, project_slug: str, github_login: str, started_at: str) -> str:
    month = started_at[:7]  # YYYY-MM
    return f"telemetry/{client_slug}/{project_slug}/{github_login}/{month}.jsonl"

def _get_sha_and_content(gh, path: str):
    status, body = gh("GET", path, ref=BRANCH)
    if status == 200 and isinstance(body, dict):
        sha = body.get("sha")
        raw = body.get("content") or ""
        try:
            existing = base64.b64decode(raw).decode() if raw else ""
        except Exception:
            existing = ""
        return sha, existing
    return None, ""

def deliver_record(gh, record: dict) -> bool:
    """Append the record to its monthly telemetry file via the GitHub Contents API.
    One 409 (stale-sha) retry. Returns True on success, False otherwise. Never raises."""
    try:
        path = telemetry_path(record["client_slug"], record["project_slug"],
                              record["github_login"], record["started_at"])

        def attempt():
            sha, existing = _get_sha_and_content(gh, path)
            new_content = existing + json.dumps(record) + "\n"
            kw = {
                "content": base64.b64encode(new_content.encode()).decode(),
                "message": f"telemetry: {record.get('session_id', '')}",
                "branch": BRANCH,
            }
            if sha:
                kw["sha"] = sha
            return gh("PUT", path, **kw)

        status, _ = attempt()
        if status in (200, 201):
            return True
        if status == 409:                 # stale sha — refetch + retry once
            status, _ = attempt()
            return status in (200, 201)
        return False
    except Exception:
        return False
