---
name: scaffold-effort-sync
description: This skill should be used when the operator says "set up effort tracking for a client project", "scaffold effort sync", "add effort tracking to this repo", "onboard a client project to the tracker", "track this client's effort", or "wire up the owner self-report". Scaffolds the project.json-piggyback effort sync into a client project repo so a project OWNER's effort (Claude tokens + human hours) is captured locally and ingested centrally WITHOUT giving them push access or putting secrets on their machine. All steps are inline — no bundled scripts.
version: 1.0.0
---

# Scaffold Effort Sync (project.json piggyback)

Wires a client project into the human-token-tracker effort pipeline using the
**project.json piggyback** path: a local `SessionEnd` hook writes effort to the repo's
`.claude/project.json`; the owner commits it; a central cron ingests owner entries.

**Why this path:** a project owner/client usually has **no push access** to the central
tracker repo and we never put secrets/env on their machine. A local file write + their
normal commit + the tracker's existing read access = full capture with zero new access.

Full architecture this implements: `human-token-tracker/docs/engineering/EFFORT_TRACKING_PIPELINE.md`.

## When to use vs not

- **Use** for a client/owner repo where the owner runs Claude Code themselves and you want
  their tokens/hours tracked (e.g. each Work Healthy Australia repo).
- **Don't** use for Edge8-internal contributors — they deliver via the `il_telemetry`
  gh-push path. (This cron filters to OWNER entries only, so Edge8 entries are ignored to
  avoid double-counting.)

## Inputs to gather first

1. **Client + project** as they exist in the tracker DB (`clients`, `projects`). The
   `projects.github_repo` must be set to the repo `owner/name`. If the project isn't
   registered yet, register it first (it must exist before ingest runs).
2. **Owner identity** — the owner's GitHub login(s) and git email(s). Get the real login
   from PR data: `select author_login, count(*) from pull_requests pr join projects p on
   p.id=pr.project_id where p.github_repo='<owner/name>' group by author_login order by 2 desc;`

## Steps (all inline)

### 1. Seed the owner into `client_identities`
So the owner is classified as owner (not Edge8) for both the PR split and the ingest filter.
Use the Supabase MCP (`mcp__plugin_supabase__execute_sql`) against the human-token-tracker
project. Idempotent insert (one row per login and per email):

```sql
insert into client_identities (project_id, github_login, git_email, label)
select v.project_id, v.github_login, v.git_email, v.label
from (values
  (null::uuid, '<owner-login>',  null::text, '<Owner Name> (<Client>)'),
  (null::uuid, null::text, '<owner-email>', '<Owner Name> (<Client>)')
) as v(project_id, github_login, git_email, label)
where not exists (
  select 1 from client_identities ci
  where (v.github_login is not null and lower(ci.github_login)=lower(v.github_login))
     or (v.git_email   is not null and lower(ci.git_email)  =lower(v.git_email))
);
```
`project_id = null` makes it a global owner row (fine — a login/email is unique to a person).
Repeat the values rows for every login/email the owner commits under.

**Verify** the split resolves before going further:
```sql
with o as (select lower(github_login) gl from client_identities where github_login is not null)
select count(*) filter (where lower(author_login) in (select gl from o)) owner_prs,
       count(*) filter (where lower(author_login) not in (select gl from o) or author_login is null) edge8_prs
from pull_requests pr join projects p on p.id=pr.project_id where p.github_repo='<owner/name>';
```

### 2. Vendor the self-report hook into the client repo
Work on a branch in the client repo (run `git status` first; stop if dirty).

```bash
cd <client-repo>
git checkout -b feat/effort-selfreport-hook origin/main
mkdir -p .claude/hooks
cp <agents-template>/plugin-staging/hooks/effort_selfreport.py .claude/hooks/effort_selfreport.py
```

The hook is self-contained (no imports), so the single file works standalone.

### 3. Merge a `SessionEnd` hook into the repo's `.claude/settings.json`
**Preserve all existing hooks** — only ADD the `SessionEnd` key (read the file first; if it
already has `SessionEnd`, append to its `hooks` array instead of replacing). Use the
portable `${CLAUDE_PROJECT_DIR}` path (relative paths are unreliable for hooks):

```json
"SessionEnd": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/effort_selfreport.py\" 2>/dev/null || true",
        "timeout": 15,
        "statusMessage": "Recording effort (local)…"
      }
    ]
  }
]
```
Validate: `python3 -c "import json; json.load(open('.claude/settings.json'))"`.

### 4. Ensure `.claude/project.json` is git-tracked
The piggyback only works if the file travels with commits:
```bash
git check-ignore .claude/project.json   # must print NOTHING
git ls-files --error-unmatch .claude/project.json 2>/dev/null || echo "create + track it"
```
If ignored, remove the ignore rule. If absent, the hook creates it on first run; make sure
it's not gitignored so the owner's commit includes it.

### 5. Commit + open a PR (do NOT self-merge a client repo)
Stage only the two files explicitly; never `git add -A`.
```bash
git add .claude/hooks/effort_selfreport.py .claude/settings.json
git commit -m "chore(telemetry): add local effort self-report hook (.claude)"
git push -u origin feat/effort-selfreport-hook
gh pr create --base main --title "chore(telemetry): local effort self-report hook" --body "<explain: local write only, no secrets, SessionEnd hook, one-time trust prompt>"
```
Client-repo changes are cross-tenant → **operator/owner merges**, not the agent.

### 6. Confirm ingestion is wired
- The cron `/api/cron/ingest-effort-logs` (in human-token-tracker, `vercel.json` schedule
  `0 3 * * *`) reads every project's `.claude/project.json` and ingests owner entries. No
  per-project config needed — it iterates all projects with a `github_repo`.
- After the owner runs a session and commits `project.json`, verify:
  ```sql
  select occurred_on, kind, amount, session_id from token_entries
  where project_id='<project-uuid>' and source='effort-log' order by occurred_on desc limit 10;
  ```

## Tell the operator at the end
- The owner must **approve a one-time Claude Code trust prompt** the first time they open
  the repo after the PR merges (security gate — unavoidable, per-directory).
- The owner must **commit `.claude/project.json`** for their effort to sync (it lands on
  their normal commit/push; it is not pushed live).
- Owner **tokens/hours currently blend into project totals**; the owner-vs-Edge8 *separation*
  is PR-only today (read-time split). Separating owner tokens/hours into their own bucket is
  a follow-up extension.

## Guardrails
- Never put `SUPABASE_*` / `INGEST_*` secrets or any env on the owner's machine — the whole
  point is a local file write + their own git.
- Never self-merge the client-repo PR.
- Keep the cron's **owner-only filter** intact — removing it would double-count Edge8
  contributors captured via the `il_telemetry` path.
