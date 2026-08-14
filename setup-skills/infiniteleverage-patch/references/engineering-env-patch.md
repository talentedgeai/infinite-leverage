## Environment variables
- `website/.env.local` (gitignored) is the ONLY env file. Never create a `.env.example`.
- Every new env var introduced in code must be added to `.env.local` with a one-line comment (what it's for, where the value comes from) as part of the same task.
- Never commit `.env.local`, `.env.production`, or any file containing real secrets.
