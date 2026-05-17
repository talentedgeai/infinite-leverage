---
name: create-local-task
description: Create a persistent scheduled routine using RemoteTrigger — the native Claude Code Desktop scheduling mechanism. Runs in Anthropic's cloud (CCR), no active session or awake Mac Mini required.
---

# Skill: create-local-task

Create a scheduled routine using `RemoteTrigger` — the native Claude Code Desktop scheduling tool. Each routine spawns a fully isolated remote CCR session in Anthropic's cloud on a cron schedule. The Mac Mini does not need to be awake.

## When to use

Trigger this skill when the user says things like:
- "schedule a task to..."
- "create a routine that runs every..."
- "set up a scheduled agent for..."
- "add a cron job to..."

**Always use `RemoteTrigger`.** Never use `CronCreate` (session-only, dies when Desktop closes) or `mcp__scheduled-tasks` (different system).

---

## How RemoteTrigger routines work

- **Cloud-hosted** — runs in Anthropic's CCR infrastructure, no local session needed.
- **Persistent** — survives Desktop app restarts and Mac Mini sleep/reboot.
- **Fresh git checkout** — each run clones the repo; no access to local `.env` files. Pass credentials via repo-committed config or Vercel/Supabase env vars.
- **Minimum interval: 1 hour** — sub-hourly crons are rejected.
- **Cron in UTC** — convert local time to UTC before registering. Asia/Saigon = UTC+7.
- **Returns a routine ID** — visible at https://claude.ai/code/routines

---

## Step 1 — Load RemoteTrigger schema

```
ToolSearch(query: "select:RemoteTrigger")
```

Always load the schema before calling the tool.

---

## Step 2 — Build the routine body

```json
{
  "name": "kebab-case-task-name",
  "cron_expression": "3 2 * * 1-5",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_01Ly7cgFD1z5N2xN9VtNZ42S",
      "session_context": {
        "model": "claude-sonnet-4-6",
        "sources": [
          {"git_repository": {"url": "https://github.com/{org}/{repo}"}}
        ],
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
      },
      "events": [
        {"data": {
          "uuid": "<generate a fresh lowercase v4 uuid>",
          "session_id": "",
          "type": "user",
          "parent_tool_use_id": null,
          "message": {"content": "<full prompt body>", "role": "user"}
        }}
      ]
    }
  }
}
```

For a **one-time run**, replace `cron_expression` with `"run_once_at": "YYYY-MM-DDTHH:MM:SSZ"` (RFC3339 UTC, must be in the future).

---

## Step 3 — Register

```
RemoteTrigger(action: "create", body: { ...body above... })
```

Save the returned routine ID. Share the link: `https://claude.ai/code/routines/{id}`

---

## Cron expressions (UTC)

Asia/Saigon is UTC+7. Always confirm the conversion with the user.

| Local time (Asia/Saigon) | UTC cron | Notes |
|---|---|---|
| Weekdays 6:03 AM | `3 23 * * 0-4` | Previous UTC day |
| Weekdays 7:03 AM | `3 0 * * 1-5` | |
| Weekdays 9:03 AM | `3 2 * * 1-5` | |
| Weekdays 6:07 PM | `7 11 * * 1-5` | |
| Weekdays 6:37 PM | `37 11 * * 1-5` | |
| Fridays 5:07 PM | `7 10 * * 5` | |
| Mondays 9:03 AM | `3 2 * * 1` | |
| Tuesdays 9:03 AM | `3 2 * * 2` | |
| Wednesdays 9:03 AM | `3 2 * * 3` | |
| Thursdays 10:03 AM | `3 3 * * 4` | |

Off-minute rule: avoid `:00` and `:30` when the user's request is approximate.

---

## Prompt body patterns

The prompt is the entire task. The remote agent starts with zero local context — make it self-contained.

### 1. Open with time context
```
Today's date is YYYY-MM-DD. Current time is HH:MM Asia/Saigon.
```
The agent substitutes real values at fire time via Bash: `date '+%Y-%m-%d'`

### 2. Orient to the repo
The agent gets a fresh git checkout. Start with:
```bash
cd {repo-root}
git log --oneline -5
```

### 3. Credential approach
No local `.env` — use one of:
- **Vercel env vars**: already present in the deployed environment
- **GitHub secrets**: exposed via `gh secret list`
- **Committed non-secret config**: read from repo files

### 4. Git workflow (if writing files)
```bash
git pull origin main
git checkout -b <prefix>/<task-name>/YYYY-MM-DD
# ... work ...
git add <specific files>
git commit -m "<prefix>(<task>): YYYY-MM-DD"
git push origin <branch>
gh pr create --title "..." --base main --body "..."
gh pr merge --merge --auto --delete-branch
git checkout main && git pull origin main
```

### 5. Notification pattern
Send both Lark and Resend — not fallbacks, both always fire:
- **Lark**: `lark-cli im +messages-send --as bot --chat-id "$LARK_CHAT_ID" --text $'...'`
- **Resend**: read HTML template → substitute → `resend emails send`
- **If both fail**: write inline to a repo file, commit. Never create new alert files.

### 6. Numbered steps
Structure as `## Step 0`, `## Step 1`, etc. Add `IMPORTANT:` notes for edge cases where the agent might stall.

---

## Workflow

1. **Gather requirements:**
   - Task name (kebab-case)
   - What it does and what success looks like
   - When it fires (local time — convert to UTC)
   - Which repo(s) it needs access to
   - Whether it writes files (needs git workflow) or is read/notify only
   - What credentials it needs (how they'll be accessed without local .env)
   - Notifications: Lark, email, both, neither

2. **Draft the full prompt** — self-contained, opens with date/time context, references repo files by path.

3. **Build the body** — generate a fresh UUID for `events[].data.uuid`.

4. **Load RemoteTrigger schema** via `ToolSearch(query: "select:RemoteTrigger")`.

5. **Register** via `RemoteTrigger(action: "create", body: {...})`.

6. **Confirm to the user:**
   - Routine ID and link: `https://claude.ai/code/routines/{id}`
   - Schedule in both UTC and local time
   - How to manage it: https://claude.ai/code/routines

---

## MCP connectors (optional)

If the task needs Supabase, Vercel, or other services, add to the body:

```json
"mcp_connections": [
  {
    "connector_uuid": "889b045d-82fa-4674-9917-853b51960594",
    "name": "Supabase",
    "url": "https://mcp.supabase.com/mcp"
  }
]
```

Available connectors: Supabase, Vercel, Figma, Canva, Gmail, QuickBooks, PDF-Viewer, Three-js-3D-Viewer.
