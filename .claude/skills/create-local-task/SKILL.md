# Skill: create-local-task

Create a local Claude Code scheduled task using the `CronCreate` tool — a cron job that runs inside the current Claude Code session and persists across restarts.

## When to use

Trigger this skill when the user says things like:
- "schedule a local task to..."
- "create a local scheduled task for..."
- "set up a routine that runs every..."
- "add a cron job to..."

**Always use `CronCreate` with `durable: true`.** Never use `RemoteTrigger` (cloud-hosted CCR) or `mcp__scheduled-tasks__create_scheduled_task` (Claude Desktop MCP) — those are different systems. This skill is for local Claude Code routines only.

---

## How local CronCreate tasks work

`CronCreate` schedules a prompt to fire on a cron expression inside the Claude Code session:

- **`durable: true`** — persists to `.claude/scheduled_tasks.json`, survives Claude restarts. Always set this.
- **`recurring: true`** (default) — fires on every cron match. Set `recurring: false` for one-shot reminders.
- **7-day auto-expiry** — recurring tasks fire one final time after 7 days, then are deleted. Tell the user.
- **Returns a job ID** — save it if the user may want to cancel later via `CronDelete`.
- **Off-minute rule** — avoid `:00` and `:30`. Use `57 8` instead of `0 9` for "morning". Stagger fleet load.

```
CronCreate(
  cron = "57 8 * * 1-5",   // weekdays at 8:57 AM local time (not 9:00)
  prompt = "...",           // the full task prompt
  recurring = true,
  durable = true            // ALWAYS — survives restarts
)
```

No files are written by CronCreate itself. Persistence is in `.claude/scheduled_tasks.json`.

---

## Prompt body patterns

The prompt passed to `CronCreate` IS the task. Draft it as you would any agent instruction.

### 1. Open with time context
```
It is now 8:57 AM Asia/Saigon. Today's date is YYYY-MM-DD.
```
Use `YYYY-MM-DD` as a literal placeholder — the running agent substitutes the real date at fire time.

### 2. Step 0 — Load credentials
If the task needs API keys or secrets, start with a Python env-loading snippet that reads `.env`, `.env.development`, `.env.production`, `.env.local` (in that order, last wins). Fail fast if any key is missing:
```python
def parse_env(path):
    vals = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                vals[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return vals

env = {}
env.update(parse_env(".env"))
env.update(parse_env(".env.development"))
env.update(parse_env(".env.production"))
env.update(parse_env(".env.local"))

missing = [k for k in ("KEY1", "KEY2") if not env.get(k)]
if missing:
    raise SystemExit(f"ERROR: missing keys: {missing}")
```
After the Python snippet, export values to the shell for CLI tools.

### 3. Git workflow (if writing files)
Tasks that write files always branch off main:
```bash
git pull origin main
git checkout -b <agent-prefix>/<task-name>/YYYY-MM-DD
# ... do work on branch ...
git add <specific files>
git commit -m "<prefix>(<task-name>): YYYY-MM-DD"
git push origin <branch>
gh pr create --title "..." --base main --body "..."
gh pr merge --merge --auto --delete-branch
git checkout main && git pull origin main
git branch -d <branch> 2>/dev/null || true
```
Tasks that only send notifications (no file writes) skip git entirely.

### 4. Notification pattern
Always send both Lark and Resend — they are not fallbacks for each other, both always fire:
- **Lark**: `lark-cli im +messages-send --as bot --chat-id "$LARK_CHAT_ID" --text $'...'`
  - Fallback chain if it fails: re-auth → verify chat ID → try `--markdown` → HTTP direct
- **Resend**: read HTML template → substitute `{{DATE}}` → write to `/tmp/` → `resend emails send`
  - Fallback chain if it fails: reinstall CLI → cURL API → Python requests
- **If BOTH fail**: append a failure note inline to a relevant existing file. Never create new alert files.

### 5. Numbered steps
Structure the prompt as numbered steps (`## Step 0`, `## Step 1`, etc.). Include an explicit `IMPORTANT:` note for any edge case where the agent might stall (empty results, missing files).

---

## Workflow

1. **Gather requirements from the user:**
   - Task name (suggest kebab-case if not given)
   - What it does (the agent's job)
   - When it fires (time + recurrence)
   - What credentials it needs
   - Whether it writes files (needs git workflow) or is notifications-only
   - What notifications to send (Lark, email, both, neither)

2. **Draft the full prompt** using the patterns above:
   - Open with time/date context
   - Step 0: credential loading (if needed)
   - Numbered steps for task logic
   - Notification step (if needed)
   - Git commit/PR step (if writing files)

3. **Register via `CronCreate`:**
   ```
   CronCreate(
     cron = "<5-field cron in local time>",
     prompt = "<full prompt body>",
     recurring = true,
     durable = true
   )
   ```
   - Use local timezone — no conversion needed
   - Avoid `:00` and `:30` minute marks unless the user named an exact time
   - **Always set `durable: true`** so the task survives Claude restarts

4. **Confirm to the user:**
   - Job ID returned by `CronCreate` (save it — needed for `CronDelete` to cancel)
   - Next scheduled fire time
   - Remind them that recurring tasks **auto-expire after 7 days** — they must re-register after that
   - Remind them to verify the task fired on first run before relying on it

---

## Cron expression reference

| Schedule | Expression | Notes |
|----------|-----------|-------|
| Weekdays at ~9 AM | `57 8 * * 1-5` | Off-minute — avoid `0 9` |
| Daily at ~7 AM | `3 7 * * *` | Off-minute |
| Every hour | `7 * * * *` | Off-minute — avoid `0 *` |
| Every 5 minutes | `*/5 * * * *` | |
| Fridays at ~4 PM | `47 15 * * 5` | Off-minute |
| One-shot at 2:30 PM today | `30 14 <dom> <month> *` | Set `recurring: false` |

---

## Example: notification-only task

```
CronCreate(
  cron = "57 8 * * 1-5",
  prompt = """It is 8:57 AM. Today's date is YYYY-MM-DD.

## Step 0 — Load credentials
[credential loading snippet]

## Step 1 — Fetch open PRs
gh pr list --state open --json number,title,author,createdAt --limit 20

## Step 2 — Send Lark digest
[build message, send via lark-cli]
""",
  recurring = true,
  durable = true
)
```

## Example: file-writing task

```
CronCreate(
  cron = "47 15 * * 5",
  prompt = """It is Friday ~4 PM. Today's date is YYYY-MM-DD.

## Step 0 — Load credentials
[credential loading snippet]

## Step 1 — Read this week's briefings
[read standup/briefings/YYYY-MM/*.md]

## Step 2 — Write summary
[write standup/briefings/YYYY-MM/weekly-YYYY-MM-DD.md]

## Step 3 — Send notifications
[lark + resend]

## Step 4 — Git commit and PR
[branch, commit, push, PR, merge, cleanup]
""",
  recurring = true,
  durable = true
)
```
