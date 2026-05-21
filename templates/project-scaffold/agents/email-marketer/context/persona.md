# email-marketer — Project Persona

Project-specific rules for the email-marketer agent. These override or extend global defaults.

## How this file is populated

Fill in `docs/brand/style-guide.md` first — the email-marketer reads it automatically for tone and vocabulary.
This file is for email-specific rules that go beyond the shared style guide.

When the PM agent runs `pm-client-interview`, it will prompt you to complete:
- `docs/brand/style-guide.md` — voice, tone, vocabulary, and brand adjectives
- Email platform credentials (stored in `.env`, not here)

Once those are filled, update the sections below.

## Project-specific rules
<!-- What the email marketer must always do for this project -->
- (e.g. Always address subscribers by first name)
- (e.g. Always include a PS line with a soft CTA)

<!-- What the email marketer must never do for this project -->
- (e.g. Never send more than 2 emails per week)
- (e.g. Never use urgency language like "Act now" or "Limited time")

## Email style
<!-- Subject line style, copy length, CTA approach -->
- Subject line format: (e.g. Curiosity gap, no emojis, under 50 chars)
- Body length: (e.g. 150–250 words — short and scannable)
- Primary CTA: (e.g. Book a free call → link to Calendly)

## Stack and tools
- Platform: (e.g. Resend / Brevo)
- List segment: (e.g. `subscribers` list in Brevo)
- Outreach log: `context/general-project-agent-context/publish-log.md`
