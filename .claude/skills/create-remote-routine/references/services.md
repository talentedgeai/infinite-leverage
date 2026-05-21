# Service Setup Guides

## Lark / Feishu

**What it does:** Send messages to any Lark group chat or direct message via a bot.

**How to get credentials:**
1. Go to [open.larksuite.com/app](https://open.larksuite.com/app) → Create App
2. Under **Credentials & Basic Info**, copy `App ID` and `App Secret`
3. Under **Permissions & Scopes**, add: `im:message:send_as_bot`
4. Under **Event Subscriptions → Bot Events**, add the bot to the workspace
5. Go to the target Lark group → Add the bot as a member

**Env vars needed:**
```bash
export LARK_APP_ID="cli_xxxx"
export LARK_APP_SECRET="xxxx"
export LARK_CHAT_ID="oc_xxxx"      # group chat (oc_ prefix)
# OR
export LARK_USER_OPEN_ID="ou_xxxx" # direct message (ou_ prefix)
```

**Note:** Lark requires a 2-step token exchange before each request batch. The token expires in ~2 hours, so always fetch fresh at runtime (as shown in curl-patterns.md).

---

## Resend

**What it does:** Send transactional/marketing emails. Clean REST API.

**How to get API key:**
1. Sign up at [resend.com](https://resend.com) (free: 3,000 emails/month, 100/day)
2. Dashboard → API Keys → Create API Key
3. Verify your sending domain (or use the shared `onboarding@resend.dev` for testing)

**Env vars needed:**
```bash
export RESEND_API_KEY="re_xxxx"
export RESEND_FROM="you@yourdomain.com"
export RESEND_TO="recipient@example.com"
```

---

## SendGrid

**What it does:** High-volume transactional email. More complex than Resend but widely adopted.

**How to get API key:**
1. Sign up at [sendgrid.com](https://sendgrid.com) (free: 100 emails/day forever)
2. Settings → API Keys → Create API Key → Full Access (or Mail Send only)
3. Verify sender identity under Sender Authentication

**Env vars needed:**
```bash
export SENDGRID_API_KEY="SG.xxxx"
export SENDGRID_FROM="you@yourdomain.com"
export SENDGRID_TO="recipient@example.com"
```

---

## Mailgun

**What it does:** Developer-focused email API. Reliable deliverability.

**How to get API key:**
1. Sign up at [mailgun.com](https://mailgun.com) (free: 5,000/month for 3 months, then pay-per-use)
2. Dashboard → API Keys → Private API Key
3. Note your sending domain (sandbox domain works for testing)

**Env vars needed:**
```bash
export MAILGUN_API_KEY="key-xxxx"
export MAILGUN_DOMAIN="mg.yourdomain.com"   # or sandbox domain
export MAILGUN_FROM="you@mg.yourdomain.com"
export MAILGUN_TO="recipient@example.com"
```

---

## Slack

**Option A — Incoming Webhook (simplest, no bot setup):**
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From Scratch
2. Incoming Webhooks → Activate → Add New Webhook → pick a channel
3. Copy the webhook URL — it's the only credential you need

**Option B — Bot token (can send to any channel/DM):**
1. Same app creation → OAuth & Permissions → Scopes → Add `chat:write`
2. Install to workspace → copy `Bot User OAuth Token` (starts with `xoxb-`)

**Env vars needed (webhook):**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../xxxx"
```

**Env vars needed (bot token):**
```bash
export SLACK_BOT_TOKEN="xoxb-xxxx"
export SLACK_CHANNEL_ID="C0123456789"   # from channel details
```

---

## Discord

**What it does:** Send messages to a Discord channel via webhook. Zero bot setup.

**How to get webhook URL:**
1. Open Discord → target channel → Edit Channel → Integrations → Webhooks
2. Create Webhook → Copy Webhook URL
3. The URL is the only credential (treat it like a secret)

**Env vars needed:**
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxxx/xxxx"
```

---

## Telegram

**What it does:** Send messages to yourself, a group, or a channel via bot.

**How to get bot token:**
1. Open Telegram → search `@BotFather` → `/newbot` → follow prompts
2. Copy the token BotFather gives you (format: `123456789:ABCdef...`)
3. To get your chat_id: send a message to the bot, then visit:
   `https://api.telegram.org/bot<TOKEN>/getUpdates` — find `"id"` in the `"chat"` object

**Env vars needed:**
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdef..."
export TELEGRAM_CHAT_ID="123456789"   # your personal chat_id (or group id)
```

---

## ntfy.sh

**What it does:** Push notifications to phone/desktop. Completely free, no account needed.

**How to set up:**
1. Install the ntfy app on your phone or use the web at [ntfy.sh](https://ntfy.sh)
2. Subscribe to a topic name you invent (e.g., `my-routine-alerts-abc123`)
   — use a random suffix to avoid conflicts with other users
3. No API key needed for public topics. For private topics, sign up at ntfy.sh and create a token.

**Env vars needed (public topic, no auth):**
```bash
export NTFY_TOPIC="my-routine-alerts-abc123"
```

**Env vars needed (authenticated):**
```bash
export NTFY_TOPIC="my-routine-alerts-abc123"
export NTFY_TOKEN="tk_xxxx"
```

---

## Twilio (SMS)

**What it does:** Send SMS to any phone number.

**How to get credentials:**
1. Sign up at [twilio.com](https://twilio.com) (free trial includes ~$15 credit)
2. Console Dashboard → Account SID and Auth Token
3. Get a Twilio phone number (free with trial)

**Env vars needed:**
```bash
export TWILIO_ACCOUNT_SID="ACxxxx"
export TWILIO_AUTH_TOKEN="xxxx"
export TWILIO_FROM="+15551234567"   # your Twilio number
export TWILIO_TO="+15559876543"     # recipient
```

---

## Airtable

**What it does:** Append rows to a spreadsheet-style database via REST API.

**How to get API key:**
1. Go to [airtable.com/create/tokens](https://airtable.com/create/tokens)
2. Create a personal access token with scopes: `data.records:write`
3. Note your base ID (from the URL: `airtable.com/<BASE_ID>/...`) and table name

**Env vars needed:**
```bash
export AIRTABLE_TOKEN="patxxxx"
export AIRTABLE_BASE_ID="appxxxx"
export AIRTABLE_TABLE="TableName"
```

---

## Notion

**What it does:** Append entries to a Notion database.

**How to get integration token:**
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New Integration
2. Give it a name, select workspace → Submit → copy the Internal Integration Token
3. Open the target Notion database → `...` menu → Connections → add your integration
4. Copy the database ID from the URL: `notion.so/<workspace>/<DATABASE_ID>?v=...`

**Env vars needed:**
```bash
export NOTION_TOKEN="secret_xxxx"
export NOTION_DATABASE_ID="xxxx-xxxx-xxxx-xxxx"
```

---

## Make.com Webhook

**What it does:** Trigger a Make automation scenario via HTTP. Connect to hundreds of apps.

**How to get webhook URL:**
1. Sign up at [make.com](https://make.com) (free: 1,000 ops/month)
2. Create Scenario → Add module → Webhooks → Custom Webhook → Add → Copy URL
3. Design the rest of the scenario to do what you want with the incoming data

**Env vars needed:**
```bash
export MAKE_WEBHOOK_URL="https://hook.eu1.make.com/xxxx"
```

---

## Zapier Webhook

**What it does:** Trigger a Zapier Zap via HTTP. Connect to 5,000+ apps.

**How to get webhook URL:**
1. Sign up at [zapier.com](https://zapier.com) (free: 100 tasks/month)
2. Create Zap → Trigger: Webhooks by Zapier → Catch Hook → Copy URL
3. Design the rest of the Zap to do what you want

**Env vars needed:**
```bash
export ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/xxxx/xxxx/"
```
