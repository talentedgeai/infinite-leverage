import subprocess

def _default_run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return ""

def parse_repo_full_name(remote_url: str) -> str:
    s = remote_url.strip()
    if not s:
        return ""
    if s.endswith(".git"):
        s = s[:-4]
    if ":" in s and "//" not in s:          # scp-like ssh: git@host:owner/repo
        s = s.split(":", 1)[1]
    else:                                    # scheme://host/owner/repo
        s = s.split("//", 1)[-1]
        parts = s.split("/", 1)
        s = parts[1] if len(parts) > 1 else parts[0]
    return s.strip("/")

def gather_context(run=_default_run) -> dict:
    def one(cmd: list[str]) -> str:
        return run(cmd).strip()
    return {
        "repo_full_name": parse_repo_full_name(one(["git", "config", "--get", "remote.origin.url"])),
        "session_branch": one(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "author_email": one(["git", "config", "user.email"]),
        "github_login": one(["gh", "api", "user", "--jq", ".login"]),
    }
