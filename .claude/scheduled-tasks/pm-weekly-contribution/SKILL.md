---
name: pm-weekly-contribution
description: >-
  Mondays at 7:30 AM — runs pm-contribution-sync across all projects to refresh
  human-token and Claude-token data for the prior week, then runs pm-hub-report
  to update the centralized cross-project dashboard.
suggested_cron: "30 7 * * 1"
---

It is now Monday 7:30 AM. Today's date is YYYY-MM-DD.
Last week's window: YYYY-MM-DD (Mon) → YYYY-MM-DD (Sun).

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
for f in [".env", ".env.development", ".env.production", ".env.local", 
          "~/.claude/.env"]:
    env.update(parse_env(f))
```

## Step 1 — Run contribution sync (all projects)

Invoke `pm-contribution-sync` with:
- Window: last Monday (YYYY-MM-DD) → last Sunday (YYYY-MM-DD)
- Timezone: from `~/.claude/.env TZ` or default `+00:00`

This fans out across every `~/code-projects/*/` directory, runs `team-hours.py`
per project, updates each `docs/project-status.html`, and writes
`scripts/contribution-snapshot.json` per project.

## Step 2 — Run hub report

Invoke `pm-hub-report` to aggregate all fresh snapshots into the
centralized dashboard.

## Step 3 — Notify (if Lark configured)

If `LARK_WEBHOOK_URL` is set:
```bash
lark-cli im +messages-send --as bot --chat-id "$LARK_CHAT_ID" \
  --text $'📊 Weekly contribution sync complete — all project-status.html files updated with last week\'s human tokens + Claude tokens. Hub refreshed.'
```

## Step 4 — Print summary

Print the combined output from pm-contribution-sync and pm-hub-report,
including:
- N projects synced
- Total human tokens across all projects (last week)
- Total Claude tokens billed (last week)
- Hub file path
