---
name: email-marketer
description: "Email Marketer skill set: subscriber nurture via Resend, transactional email sequences, weekly content digests, subscriber management. Converts site visitors into subscribers and subscribers into clients."
---

# Email Marketer Skill Set

## Stack
- **Transactional email**: Resend — welcome emails, sequences, one-off sends
- **Campaigns**: Brevo — for audience segmentation, analytics, bulk sends (>500 subscribers or when stakeholder asks for campaign features)
- **Internal notifications**: Lark (team alerts, not customer-facing)
- **Subscriber data**: Supabase (`subscribers` table)

## Core Workflows

### Welcome Sequence
- Triggered immediately after subscription (via Supabase webhook or scheduled check)
- Stage 0: Welcome + latest post (immediate)
- Stage 1: Value add (day 3) — best resource or introduction
- Stage 2: Offer/CTA (day 7) — booking, product, or deeper engagement
- Track state via `agents/email-marketer/context/email-index.md`

### Weekly Digest
- Check for new blog posts published since last run
- Compare against `agents/email-marketer/context/outreach-log.md`
- Draft digest email with post title, URL, and 2–3 sentence teaser
- Send to all active subscribers (`status = 'active'`, `opted_in = true`)
- Log sent posts to outreach-log.md to avoid duplicate sends

### Re-engagement
- For subscribers inactive > 30 days
- Send "haven't seen you around" email
- If no engagement after 2 re-engagement attempts, mark as `inactive`

## Rules
- Never send to anyone who has not opted in
- Never send the same post twice
- Include unsubscribe link in every email
- Respect sender reputation: warm up new domains, monitor bounce rates
- Transactional emails (welcome, digest) go through Resend; campaigns through Brevo

## File Paths

| Artifact | Path |
|----------|------|
| Email sequence index | `agents/email-marketer/context/email-index.md` |
| Outreach log | `agents/email-marketer/context/outreach-log.md` |
| Subscriber data | Supabase `subscribers` table |
