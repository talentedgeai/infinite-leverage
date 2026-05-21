---
name: create-remote-routine
description: >
  Use this skill whenever the user wants to create a scheduled routine, automated task, cron job,
  or recurring agent that sends outbound notifications, emails, messages, or HTTP requests to
  external services. Triggers on: "create a routine", "schedule a task", "send daily/weekly X",
  "automate sending", "set up a cron", "remind me via", "notify me when", or any request to
  periodically trigger an action in Lark, Slack, Discord, Telegram, Resend, SendGrid, Twilio,
  ntfy, Airtable, Notion, Make, Zapier, or similar services.
---

# Create Remote Routine

A routine is a scheduled Claude task (via `CronCreate`) that fires on a cron schedule and
runs a bash script using `curl` + `python3` to call external service APIs. No CLI tools,
no npm installs — only tools already on the machine.

## Step 1: Clarify the routine

Ask the user:
1. **What should it do?** (e.g., "send me a morning Lark message", "email me a weekly report")
2. **When should it run?** (e.g., "every weekday at 9am", "every Monday at 8am")
3. **Which service(s)?** If not already clear, present the options from the table below

## Step 2: Identify the service and get the API key

**Present this table** and ask which service they want to use. Then guide them to get the key.

| Service | Use case | Free tier | Auth type |
|---------|----------|-----------|-----------|
| **Lark** | Team chat message | Generous free | App ID + Secret → 2-step token |
| **Resend** | Transactional email | 3,000/month | Bearer API key |
| **SendGrid** | Email (high volume) | 100/day | Bearer API key |
| **Mailgun** | Email | 5,000/month (3 mo) | Basic auth (api:<key>) |
| **Slack** | Team chat message | Free (webhook) | Webhook URL or Bearer bot token |
| **Discord** | Chat message | Free | Webhook URL |
| **Telegram** | Personal/group message | Free | Bot token in URL |
| **ntfy.sh** | Push notification | Completely free | Topic URL (no key needed) |
| **Twilio** | SMS | Free trial | Basic auth (SID:token) |
| **Airtable** | Database append/update | 1,000 records/base | Bearer API key |
| **Notion** | Database/page update | Free personal | Bearer integration token |
| **Make.com** | Trigger automation | 1,000 ops/month | Webhook URL |
| **Zapier** | Trigger automation | 100 tasks/month | Webhook URL |

Read `references/services.md` for full API key setup instructions for each service.

## Step 3: Build the bash script

Once you know the service and have the key, build a `curl`-based bash script.
Read `references/curl-patterns.md` for tested, copy-paste-ready patterns for every service.

**Key rules for all scripts:**
- Use `python3` (pre-installed on macOS/Linux) for JSON building — never shell-escape JSON manually
- Store credentials as env vars, never hardcode them in the script body
- Use `set -euo pipefail` so errors surface immediately
- The script must be self-contained: source env vars if they may not be in the CronCreate env

**Script location:** Save to `~/.claude/scripts/<routine-name>.sh` and `chmod +x` it.

## Step 4: Create the routine

Use `CronCreate` with:
- `durable: true` so it survives desktop restarts
- A prompt that tells Claude to run the script and report success/failure
- Offset the minute from :00/:30 (e.g., use :03, :17, :47) to avoid API thundering herds

**Prompt template for CronCreate:**
```
Run the routine script:
  bash ~/.claude/scripts/<name>.sh

If the script exits with an error, report the error message.
Otherwise confirm success with the key output (e.g., message_id, email_id).

Env vars needed (export these if not already set):
  export SERVICE_API_KEY="<key>"
  export SERVICE_TARGET="<chat_id or email or topic>"
```

**Important: tell the user about the 7-day limit.** CronCreate recurring tasks
auto-expire after 7 days. They'll need to re-run this skill to renew. If they want
permanent scheduling without re-registration, suggest `crontab` or a GitHub Actions cron instead.

## Step 5: Test immediately

After creating the routine, run the script once right now to confirm it works:
```bash
bash ~/.claude/scripts/<name>.sh
```
Fix any issues before leaving the user with a non-working routine.
