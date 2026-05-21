# curl Patterns for Outbound API Calls

All patterns use `python3` (pre-installed everywhere) for safe JSON building.
Never build JSON via shell string interpolation — escaping breaks silently.

---

## Lark / Feishu

Two-step: fetch tenant token, then send. Token is valid ~2 hours so fetch fresh each run.

```bash
#!/usr/bin/env bash
set -euo pipefail

APP_ID="${LARK_APP_ID:?LARK_APP_ID not set}"
APP_SECRET="${LARK_APP_SECRET:?LARK_APP_SECRET not set}"
CHAT_ID="${LARK_CHAT_ID:?LARK_CHAT_ID not set}"     # oc_xxx (group) or use open_id for DM
MESSAGE="${1:?message required}"
BASE="https://open.larksuite.com/open-apis"

# Step 1: tenant access token
TOKEN=$(curl -s -X POST "$BASE/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")

# Step 2: send message (python3 builds the nested JSON safely)
python3 - "$TOKEN" "$CHAT_ID" "$MESSAGE" << 'EOF'
import json, sys, urllib.request
token, chat_id, message = sys.argv[1], sys.argv[2], sys.argv[3]
body = json.dumps({
    "receive_id": chat_id,
    "msg_type": "text",
    "content": json.dumps({"text": message})   # content is a pre-serialized string
}).encode()
req = urllib.request.Request(
    "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
if d.get("code") == 0:
    print("ok message_id=" + d["data"]["message_id"])
else:
    print("error:", d.get("msg"), file=__import__("sys").stderr); exit(1)
EOF
```

**For DM (send to a user directly):**
- Change `receive_id` to the user's `open_id` (format: `ou_xxx`)
- Change query param to `?receive_id_type=open_id`

---

## Resend

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - << EOF
import json, urllib.request, os, sys

key  = os.environ.get("RESEND_API_KEY") or sys.exit("RESEND_API_KEY not set")
frm  = os.environ.get("RESEND_FROM")    or sys.exit("RESEND_FROM not set")
to   = os.environ.get("RESEND_TO")      or sys.exit("RESEND_TO not set")

body = json.dumps({
    "from": frm,
    "to": [t.strip() for t in to.split(",")],
    "subject": "Your subject here",
    "html": "<p>Your message here</p>"
}).encode()

req = urllib.request.Request(
    "https://api.resend.com/emails",
    data=body,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
print("ok email_id=" + d["id"])
EOF
```

---

## SendGrid

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - << EOF
import json, urllib.request, os, sys

key = os.environ.get("SENDGRID_API_KEY") or sys.exit("SENDGRID_API_KEY not set")
frm = os.environ.get("SENDGRID_FROM")    or sys.exit("SENDGRID_FROM not set")
to  = os.environ.get("SENDGRID_TO")      or sys.exit("SENDGRID_TO not set")

body = json.dumps({
    "personalizations": [{"to": [{"email": to}]}],
    "from": {"email": frm},
    "subject": "Your subject here",
    "content": [{"type": "text/html", "value": "<p>Your message here</p>"}]
}).encode()

req = urllib.request.Request(
    "https://api.sendgrid.com/v3/mail/send",
    data=body,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    method="POST"
)
try:
    urllib.request.urlopen(req)
    print("ok (202 accepted)")
except urllib.error.HTTPError as e:
    print("error:", e.read().decode(), file=__import__("sys").stderr); exit(1)
EOF
```

---

## Mailgun

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - << EOF
import urllib.request, urllib.parse, base64, os, sys

key    = os.environ.get("MAILGUN_API_KEY") or sys.exit("MAILGUN_API_KEY not set")
domain = os.environ.get("MAILGUN_DOMAIN")  or sys.exit("MAILGUN_DOMAIN not set")
frm    = os.environ.get("MAILGUN_FROM")    or sys.exit("MAILGUN_FROM not set")
to     = os.environ.get("MAILGUN_TO")      or sys.exit("MAILGUN_TO not set")

data = urllib.parse.urlencode({
    "from": frm, "to": to,
    "subject": "Your subject here",
    "html": "<p>Your message here</p>"
}).encode()

creds = base64.b64encode(f"api:{key}".encode()).decode()
req = urllib.request.Request(
    f"https://api.mailgun.net/v3/{domain}/messages",
    data=data,
    headers={"Authorization": f"Basic {creds}"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    import json; d = json.load(resp)
print("ok id=" + d.get("id","sent"))
EOF
```

---

## Slack — Incoming Webhook (simplest)

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "${1:?message required}" << 'EOF'
import json, urllib.request, os, sys

url     = os.environ.get("SLACK_WEBHOOK_URL") or sys.exit("SLACK_WEBHOOK_URL not set")
message = sys.argv[1]

body = json.dumps({"text": message}).encode()
req  = urllib.request.Request(url, data=body,
       headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req) as resp:
    result = resp.read().decode()
print("ok" if result == "ok" else "error: " + result)
EOF
```

## Slack — Bot token (any channel/DM)

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "${1:?message required}" << 'EOF'
import json, urllib.request, os, sys

token   = os.environ.get("SLACK_BOT_TOKEN")  or sys.exit("SLACK_BOT_TOKEN not set")
channel = os.environ.get("SLACK_CHANNEL_ID") or sys.exit("SLACK_CHANNEL_ID not set")
message = sys.argv[1]

body = json.dumps({"channel": channel, "text": message}).encode()
req  = urllib.request.Request(
    "https://slack.com/api/chat.postMessage", data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
if d.get("ok"):
    print("ok ts=" + d["ts"])
else:
    print("error:", d.get("error"), file=__import__("sys").stderr); exit(1)
EOF
```

---

## Discord — Webhook

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "${1:?message required}" << 'EOF'
import json, urllib.request, os, sys

url     = os.environ.get("DISCORD_WEBHOOK_URL") or sys.exit("DISCORD_WEBHOOK_URL not set")
message = sys.argv[1]

body = json.dumps({"content": message}).encode()
req  = urllib.request.Request(url, data=body,
       headers={"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req)   # 204 No Content on success
print("ok")
EOF
```

---

## Telegram

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "${1:?message required}" << 'EOF'
import json, urllib.request, os, sys

token   = os.environ.get("TELEGRAM_BOT_TOKEN") or sys.exit("TELEGRAM_BOT_TOKEN not set")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")   or sys.exit("TELEGRAM_CHAT_ID not set")
message = sys.argv[1]

body = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode()
req  = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage", data=body,
    headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
if d.get("ok"):
    print("ok message_id=" + str(d["result"]["message_id"]))
else:
    print("error:", d.get("description"), file=__import__("sys").stderr); exit(1)
EOF
```

---

## ntfy.sh — Push Notification (no account needed)

```bash
#!/usr/bin/env bash
set -euo pipefail

TOPIC="${NTFY_TOPIC:?NTFY_TOPIC not set}"
MESSAGE="${1:?message required}"
TITLE="${2:-Routine Notification}"

# Public topic (no auth)
curl -s \
  -H "Title: $TITLE" \
  -H "Priority: default" \
  -d "$MESSAGE" \
  "https://ntfy.sh/$TOPIC"

# Authenticated topic: add  -H "Authorization: Bearer $NTFY_TOKEN"
```

---

## Twilio — SMS

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "${1:?message required}" << 'EOF'
import urllib.request, urllib.parse, base64, os, sys

sid   = os.environ.get("TWILIO_ACCOUNT_SID") or sys.exit("TWILIO_ACCOUNT_SID not set")
token = os.environ.get("TWILIO_AUTH_TOKEN")  or sys.exit("TWILIO_AUTH_TOKEN not set")
frm   = os.environ.get("TWILIO_FROM")        or sys.exit("TWILIO_FROM not set")
to    = os.environ.get("TWILIO_TO")          or sys.exit("TWILIO_TO not set")
body_text = sys.argv[1]

data  = urllib.parse.urlencode({"From": frm, "To": to, "Body": body_text}).encode()
creds = base64.b64encode(f"{sid}:{token}".encode()).decode()
req   = urllib.request.Request(
    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
    data=data, headers={"Authorization": f"Basic {creds}"}, method="POST"
)
import json
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
print("ok sid=" + d["sid"])
EOF
```

---

## Airtable — Append a row

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - << 'EOF'
import json, urllib.request, os, sys

token   = os.environ.get("AIRTABLE_TOKEN")   or sys.exit("AIRTABLE_TOKEN not set")
base_id = os.environ.get("AIRTABLE_BASE_ID") or sys.exit("AIRTABLE_BASE_ID not set")
table   = os.environ.get("AIRTABLE_TABLE")   or sys.exit("AIRTABLE_TABLE not set")

# Adjust fields to match your table's column names
body = json.dumps({
    "records": [{"fields": {"Name": "Routine run", "Notes": "Automated entry"}}]
}).encode()

req = urllib.request.Request(
    f"https://api.airtable.com/v0/{base_id}/{urllib.parse.quote(table)}",
    data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
import urllib.parse
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
print("ok id=" + d["records"][0]["id"])
EOF
```

---

## Notion — Append a database entry

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - << 'EOF'
import json, urllib.request, os, sys
from datetime import datetime, timezone

token = os.environ.get("NOTION_TOKEN")       or sys.exit("NOTION_TOKEN not set")
db_id = os.environ.get("NOTION_DATABASE_ID") or sys.exit("NOTION_DATABASE_ID not set")

# Adjust properties to match your database schema
body = json.dumps({
    "parent": {"database_id": db_id},
    "properties": {
        "Name": {"title": [{"text": {"content": "Routine entry " + datetime.now(timezone.utc).strftime("%Y-%m-%d")}}]}
    }
}).encode()

req = urllib.request.Request(
    "https://api.notion.com/v1/pages", data=body,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }, method="POST"
)
with urllib.request.urlopen(req) as resp:
    d = json.load(resp)
print("ok page_id=" + d["id"])
EOF
```

---

## Make.com / Zapier Webhook — Trigger automation

```bash
#!/usr/bin/env bash
set -euo pipefail

# Works for both Make.com and Zapier — just change the env var name
URL="${MAKE_WEBHOOK_URL:-${ZAPIER_WEBHOOK_URL:?set MAKE_WEBHOOK_URL or ZAPIER_WEBHOOK_URL}}"

python3 - << EOF
import json, urllib.request, os
from datetime import datetime, timezone

body = json.dumps({
    "triggered_at": datetime.now(timezone.utc).isoformat(),
    "source": "claude-routine"
    # Add any payload fields you want to pass to the automation
}).encode()

req = urllib.request.Request(
    "$URL", data=body,
    headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req) as resp:
    result = resp.read().decode()
print("ok response=" + result[:100])
EOF
```
