---
name: email-marketer-nurture
description: >-
  Manages the full subscriber email lifecycle — drafts a welcome sequence for new subscribers, prepares weekly digest emails featuring the latest blog posts, and re-engages subscribers who have gone quiet. Every email is drafted for operator approval; this skill never sends. Uses Resend for individual transactional emails and Brevo for larger bulk campaigns.
  Owned by the writer agent. Use when the operator says "email campaign", "newsletter", "welcome sequence", "send to subscribers", or "re-engage subscribers".
---

# Email Marketer: Subscriber Nurture

## Hard rule — draft only, never send

**This skill produces drafts. It never executes a send.** No `resend.emails.send`, no
Brevo campaign dispatch, no scheduled trigger — not even for a single test recipient,
and not when the operator's phrasing sounds like an instruction to send ("send the
digest", "email the list"). Those phrases mean *prepare the send*.

Every workflow below ends the same way:

1. Write the draft to `emails/drafts/{YYYY-MM-DD}-{slug}.md` — subject, recipient
   segment, recipient count, full body, unsubscribe link.
2. Show the operator the subject, the segment, the count, and the body.
3. Print the exact command that would send it, and stop.
4. Only the operator runs that command.

An email that has gone out cannot be recalled. If you are unsure whether something
counts as sending, it does — stop and ask.

## Stack
- **Transactional**: Resend — welcome emails, sequences, one-off sends
- **Campaigns**: Brevo — audience segmentation, campaign analytics, bulk sends
  (>500 subscribers or when the operator asks)
- **Subscriber data**: Supabase (`subscribers` table — `status`, `opted_in`,
  `last_engaged_at`). If the table doesn't exist, say so and stop; do not invent a schema.

## Core Workflows

### 1. Welcome Sequence
Drafted once per new subscriber cohort. Track state in `agents/writer/context/email-index.md`:
- Stage 0 (immediate): Welcome + latest post — subject, HTML body with `{{name}}` placeholder, latest post link
- Stage 1 (day 3): Value add — best resource or introduction
- Stage 2 (day 7): Offer/CTA — booking, product, or deeper engagement

Draft all three stages together so the operator approves the arc, not three isolated emails.

### 2. Weekly Digest
- Check for new blog posts published since the last run (compare against
  `agents/writer/context/outreach-log.md`)
- Draft the digest with post title, URL, and a 2–3 sentence teaser drawn from `blog.md`
- Resolve the recipient segment (`status = 'active'` AND `opted_in = true`) and report
  the **count** — never a recipient list, and never paste subscriber addresses into chat
- Append post slug + draft date to `outreach-log.md` only **after** the operator confirms
  the send, so a declined draft doesn't suppress the post next week

### 3. Re-engagement
- Segment: subscribers inactive > 30 days
- Draft a "haven't seen you around" email
- After two approved-and-sent attempts with no engagement, propose marking them
  `inactive` — the status change is also the operator's call

## Rules
- **Draft only — the operator sends.** See the hard rule above.
- Never draft to anyone who has not opted in.
- Never send the same post twice — check `outreach-log.md` before every draft.
- Every draft carries an unsubscribe link. Never use a template that strips it.
- Never paste subscriber emails, names, or counts-by-name into chat or into a committed
  file. Segment descriptions and totals only.
- Respect sender reputation: warm up new domains, monitor bounce rates.
- Transactional → Resend; campaigns → Brevo (ask the operator when it's borderline).

## File Paths
| Artifact | Path |
|----------|------|
| Email drafts | `emails/drafts/{YYYY-MM-DD}-{slug}.md` |
| Email sequence index | `agents/writer/context/email-index.md` |
| Outreach log | `agents/writer/context/outreach-log.md` |
| Subscriber data | Supabase `subscribers` table |

Email is owned by the **writer** agent — there is no separate email-marketer agent, so
its state lives under `agents/writer/context/`.
