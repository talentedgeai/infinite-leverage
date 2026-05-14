## Environment variables
- Every project must have a `.env.example` at the repo root with all required and optional vars listed (empty values, one-line comments).
- If `.env.example` does not exist when starting implementation, create it first.
- Every new env var introduced in code must be added to `.env.example` on the same commit.
- Never commit `.env.local`, `.env.production`, or any file containing real secrets.
- Optional vars (Stripe, Sentry) go commented out with a `#` prefix.
