# .env.local — Environment Variable Contract

`website/.env.local` (gitignored) is the **only** env file a project has. There is no `.env.example` — that pattern confuses agents and users. Keys are documented by one-line comments inside `.env.local` itself, and this file is the canonical reference for what exists and when it's collected.

**Rules:**

1. **Never create a `.env.example`** (or `.env.sample`, `.env.template`, …). If one appears in a repo, delete it and fold any documented keys into this contract.
2. **Every new env var introduced in code must be added to `.env.local`** as part of the same task — with a one-line comment saying what it's for and where the value comes from.
3. **Never commit** `.env.local`, `.env.production`, or any file containing real values.
4. **Collect values just-in-time** via `scripts/collect-credentials.py` (merge-safe — never clobbers existing values): setup collects only what the current step needs; feature keys (Stripe, Sentry, …) are collected when the feature is built, never during setup.
5. **Production values** go into Vercel via `vercel env add` — mirror every server-side key there when the feature ships.

## Key contract

```bash
# ── Supabase (core — collected during setup, Phase 2a) ───────────────────────
# Use new key naming (sb_publishable_* / sb_secret_*).
# Do NOT use legacy ANON_KEY / SERVICE_ROLE_KEY env names.
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=

# ── Site (core) ──────────────────────────────────────────────────────────────
# Used for absolute URLs (auth callbacks, redirects).
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Feature-time keys (added to `.env.local` by the task that introduces them, never earlier) follow the same pattern: `NEXT_PUBLIC_` prefix only for values safe to expose in the browser bundle; missing optional keys must silently no-op — never hard-error in preview environments.

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
