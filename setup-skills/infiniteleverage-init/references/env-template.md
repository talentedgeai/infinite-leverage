# .env.example — Bootstrap Template

Every project must have a `.env.example` at the repo root. Scaffold this file before writing any code that reads environment variables. Values must be empty — never commit real secrets.

**Rule**: If `.env.example` does not exist at project root, create it before starting any implementation. If it exists but is missing keys the current task introduces, add those keys with empty values and a one-line comment explaining each — on the same commit as the code that reads them.

---

```bash
# ─────────────────────────────────────────────────────────────────────────────
# {Project Name} — environment variables
#
# Copy to .env.local for local development. All secrets stay server-side
# unless prefixed NEXT_PUBLIC_. Missing optional keys must silently no-op —
# never hard-error in preview environments.
# ─────────────────────────────────────────────────────────────────────────────

# ── Supabase (OPERATOR-ONLY) ──────────────────────────────────────────────────
# IMPORTANT: Contributors who only push effort telemetry (session-telemetry-*)
# do NOT need any Supabase keys. The telemetry flow uses `gh` (GitHub CLI) +
# `git config user.email` only — no local secrets required.
#
# These keys are needed ONLY for:
#   • Operators running the central Infinite Leverage app (Supabase MCP, admin UI)
#   • CI/CD pipelines that deploy or migrate the Supabase project
#
# If you are a contributor (not an operator), leave these blank and skip this block.
# Use new key naming (sb_publishable_* / sb_secret_*).
# Do NOT use legacy ANON_KEY / SERVICE_ROLE_KEY env names.
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=

# ── Site ─────────────────────────────────────────────────────────────────────
# Used for absolute URLs (auth callbacks, emails, Stripe redirects).
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# ── Anthropic (Claude API) ───────────────────────────────────────────────────
ANTHROPIC_API_KEY=

# ── Resend (transactional email) ─────────────────────────────────────────────
# Welcome email silently no-ops if RESEND_API_KEY is absent — intentional.
RESEND_API_KEY=
RESEND_FROM_EMAIL=

# ── Lark (internal notifications — OPTIONAL) ─────────────────────────────────
# Leave blank to disable Lark. All agents check for LARK_WEBHOOK_URL before
# sending — notifications are silently skipped if these values are absent.
LARK_APP_ID=
LARK_APP_SECRET=
LARK_WEBHOOK_URL=

# ── Gemini (image generation) ────────────────────────────────────────────────
GEMINI_API_KEY=

# ── Stripe (payments — uncomment when payment feature is built) ───────────────
# STRIPE_WEBHOOK_SECRET is from the dashboard webhook config, not the API key.
# Webhook route reads raw body for signature verification — do not add body
# parsers in front of /api/stripe/webhook.
# STRIPE_SECRET_KEY=
# STRIPE_WEBHOOK_SECRET=
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
# STRIPE_PRICE_MONTHLY=
# STRIPE_PRICE_ANNUAL=

# ── Sentry (error monitoring — uncomment when monitoring is set up) ───────────
# DSN is safe to expose; auth token is build-time only for source maps.
# NEXT_PUBLIC_SENTRY_DSN=
# SENTRY_AUTH_TOKEN=
```

---

## Rules for maintaining .env.example

1. **Every new env var added in code must be added here on the same commit** — empty value, one-line comment.
2. **Never commit `.env.local`, `.env.production`, or any file with real values** — these are in `.gitignore`.
3. **Optional vars go commented out** (prefixed `#`) so the file runs with just core vars.
4. **Section headers** — group by service. New services get a new `# ── Service ──` block.
5. **`NEXT_PUBLIC_` prefix** — only for values safe to expose in the browser bundle.

## Claude session telemetry (Stream A) — prerequisites

Per-contributor Claude token usage and session time are captured by global hooks
and delivered to `talentedgeai/human-token-tracker` via your existing GitHub auth.
**There is no secret to set on your machine.** You only need:

1. **GitHub CLI authenticated** — `gh auth status` must succeed (`gh auth login` if not).
2. **Write access to `talentedgeai/human-token-tracker`** — confirm with
   `gh api repos/talentedgeai/human-token-tracker --jq .permissions`.
3. **A `team_members` row** in the tracker DB keyed to your git email
   (`git config user.email`) — provisioned during onboarding. Without it your effort
   lands unattributed.

If `gh` is not authenticated or your git email is unset, the SessionStart guard prints a
one-line reminder and effort is simply not tracked — your session is never blocked.
