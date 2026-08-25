from __future__ import annotations
import base64
import json
import os
import urllib.error
import urllib.request

REPO = "talentedgeai/human-token-tracker"
BRANCH = "telemetry"
TRACKER_URL = os.environ.get("IL_TRACKER_URL", "https://human-token-tracker.vercel.app")


def _api_ingest(record: dict) -> bool | None:
    """POST the record to the tracker's ingest endpoint.
    True = accepted; False = endpoint exists but rejected; None = endpoint absent
    or unreachable (fall back to the git-append path). Never raises."""
    try:
        req = urllib.request.Request(
            f"{TRACKER_URL}/api/telemetry/ingest",
            data=json.dumps(record).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "il-telemetry/2.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:  # endpoint responded
        if e.code in (404, 405, 501):
            return None  # not implemented yet — use fallback
        return False
    except Exception:
        return None

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
    """Deliver one record. Tries the tracker's ingest API first; while that
    endpoint isn't live, falls back to appending to the monthly telemetry file
    via the GitHub Contents API (one 409 stale-sha retry).
    Returns True on success, False otherwise. Never raises."""
    try:
        api_result = _api_ingest(record)
        if api_result is not None:
            return api_result

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
