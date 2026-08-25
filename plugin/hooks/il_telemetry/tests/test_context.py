from il_telemetry.context import parse_repo_full_name, gather_context

def test_parse_https_and_ssh_remotes():
    assert parse_repo_full_name("https://github.com/talentedgeai/edge8-web.git") == "talentedgeai/edge8-web"
    assert parse_repo_full_name("git@github.com:Work-Healthy-Australia/OCCUSPAN.git") == "Work-Healthy-Australia/OCCUSPAN"

def test_gather_context_uses_injected_runner():
    cmds = {
        ("git","config","--get","remote.origin.url"): "git@github.com:o/r.git\n",
        ("git","rev-parse","--abbrev-ref","HEAD"): "feat/y\n",
        ("git","config","user.email"): "a@edge8.ai\n",
        ("gh","api","user","--jq",".login"): "alice\n",
    }
    ctx = gather_context(run=lambda c: cmds.get(tuple(c), ""))
    assert ctx == {"repo_full_name":"o/r","session_branch":"feat/y","author_email":"a@edge8.ai","github_login":"alice"}
