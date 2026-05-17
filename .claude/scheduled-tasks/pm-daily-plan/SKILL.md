---
name: pm-daily-plan
description: Weekdays at 7:03 AM — checks git log and standup check-ins, sets today's 3 priorities, auto-approves low-risk tasks, writes decisions to docs/project-status.html.
suggested_cron: "3 7 * * 1-5"
---

It is now 7:03 AM. Today's date is YYYY-MM-DD.

## Step 0 — Load credentials

```python
import os, sys

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
for f in [".env", ".env.development", ".env.production", ".env.local"]:
    env.update(parse_env(f))
```

## Step 1 — Load project context

```bash
cd ~/code-projects/{project-slug}
git log --oneline --since="48 hours ago" --all
```

Read `standup/individual/*.md` — note any new check-ins since yesterday.
Read `content/content-calendar/` — identify this week's queue.

## Step 2 — Set today's 3 priorities

Based on git activity, check-ins, and content calendar: list today's 3 priorities in order of value. Flag any blockers.

Auto-approve tasks that are BOTH:
- (a) High priority AND
- (b) Low risk: no new code, no external API calls, content or config only

Log: `Auto-approved [task] at [time]` for each auto-approved item.
Everything else → log to backlog for tomorrow.

## Step 3 — Write to project status

Update `docs/project-status.html` with today's priorities, auto-approvals, and any blockers.

## Step 4 — Notify (if Lark configured)

If `LARK_WEBHOOK_URL` is set:
```bash
lark-cli im +messages-send --as bot --chat-id "$LARK_CHAT_ID" --text $'🌅 Good morning — daily plan is set. Check docs/project-status.html for today\'s priorities.'
```
