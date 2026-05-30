---
name: pm-eod-summary
description: Weekdays at 6:37 PM — summarises what shipped today, what is blocked, and what is queued for tomorrow. Updates docs/project-status.html. Notifies team via Lark if configured.
suggested_cron: "37 18 * * 1-5"
---

It is now 6:37 PM. Today's date is YYYY-MM-DD.

## Step 0 — Load credentials

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
for f in [".env", ".env.development", ".env.production", ".env.local"]:
    env.update(parse_env(f))
```

## Step 1 — Load today's context

```bash
cd ~/code-projects/{project-slug}
git log --oneline --since="today 7am" --all
```

Read `docs/project-status.html` — today's approved items and auto-approvals.
Read today's briefing at `standup/briefings/YYYY-MM/YYYY-MM-DD.md` if it exists.

## Step 2 — Build EOD summary

Compile three sections:
- **Shipped today**: merged PRs, completed tasks
- **Blocked**: anything flagged during the day with no resolution
- **Queue for tomorrow**: highest-priority pending items

## Step 3 — Update project status

Update `docs/project-status.html` with the EOD summary. Add a timestamp.

Also refresh the Pulse chart and emit a daily snapshot:

```bash
# Today's token + hours data
python3 scripts/team-hours.py \
  --start YYYY-MM-DD --end YYYY-MM-DD \
  --author "Author 1" --author "Author 2" \
  --jsonl-keyword <project-keyword> \
  --tz +HH:00 \
  --with-tokens \
  --repo .
```

Use the output to update today's data point on each Pulse line. The Pulse chart is a single peak-normalised SVG (Y-axis = 0–100 % of each series' window peak). Update the reading-guide paragraph with the latest absolute peak value and day. Follow `docs/assessments/team-hours-methodology.md §5.5` for full chart rules.

Also write the JSON snapshot for hub aggregation:

```bash
python3 scripts/team-hours.py \
  --start YYYY-MM-DD --end YYYY-MM-DD \
  --author "Author 1" --author "Author 2" \
  --jsonl-keyword <project-keyword> \
  --tz +HH:00 \
  --with-tokens \
  --json \
  --repo . \
  > scripts/contribution-snapshot.json
```

If `scripts/team-hours.py` does not exist, copy from `~/.claude/skills/pm-contribution-sync/team-hours.py` first.

## Step 4 — Notify (if Lark configured)

If `LARK_WEBHOOK_URL` is set:
```bash
lark-cli im +messages-send --as bot --chat-id "$LARK_CHAT_ID" --text $'🌇 EOD summary ready — check docs/project-status.html'
```

If Lark fails: append EOD summary inline to `docs/project-status.html` as a comment. Never create new alert files.
