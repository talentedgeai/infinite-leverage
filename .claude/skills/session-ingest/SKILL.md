---
name: session-ingest
description: >-
  Auto-tracks human + Claude tokens and billed man-hours per Claude Code session
  and posts them to the human-token-tracker Supabase pipeline. Installs two hooks
  (SessionStart → 1 billed hour; SessionEnd → token totals) that fire automatically
  in any repo containing .claude/project.json. Use when setting up token/man-hour
  tracking for a repo, or when sessions are not producing token_entries / man_hour_entries.
---

# Session-Ingest

Two hooks instrument every Claude Code session in an **instrumented repo** (one that
has `.claude/project.json`) and feed the data pipeline:

- **SessionStart** → `session-ingest-start.py` → POST `ingest-session-start` → **1 billed
  man-hour** (idempotent per clock-hour: many sessions in the same hour = one hour).
- **SessionEnd** → `session-ingest-end.py` → POST `ingest-session-end` → **token_entries**
  (one `human` row, one `claude` row).

Both resolve the engineer by `git config user.email` server-side (the Edge Function maps
it to a team member via `resolve_team_member`). The hooks are **silent on every failure** —
they never block, slow, or break a session. In a repo without `.claude/project.json` they
no-op immediately.

## Token method (approximation — document it for reconciliation)

| Metric | How it's computed |
|---|---|
| `human_tokens` | characters of **human-authored text** in the transcript ÷ 4. Only user `text` blocks count; `tool_result` blocks are excluded (machine output, not keystrokes). |
| `claude_tokens` | sum of assistant `usage.output_tokens` (what Claude generated). |

This is an estimate. If org-level Anthropic Admin API access exists, reconcile daily totals
(see plan Phase E2).

## Install (per machine)

1. Copy the hook scripts to `~/.claude/hooks/`:
   - `session-ingest-start.py`
   - `session-ingest-end.py`
   (and merge `hooks.json` so `SessionStart` runs the start hook and `SessionEnd` runs the
   end hook — see `plugin-staging/hooks/hooks.json`).

2. Create `~/.claude/.env` (NEVER committed) with:
   ```
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_ANON_KEY=<anon key>
   INGEST_SECRET=<the value set via `supabase secrets set INGEST_SECRET=...`>
   ```
   The hooks also fall back to `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   if the `SUPABASE_*` names are absent.
   > **Auth key note.** Both ingest functions are deployed with **`verify_jwt:false`**, so the
   > real access guard is the `x-ingest-secret` header (validated against `INGEST_SECRET`).
   > With JWT verification off, the `Authorization: Bearer` value is not gateway-checked, so the
   > modern `sb_publishable_…` key works fine here. (Historical caveat: while `verify_jwt` was
   > `true`, the publishable key was rejected at the gateway with `UNAUTHORIZED_INVALID_JWT_FORMAT`
   > and the legacy `eyJ…` anon JWT was required. If JWT verification is ever re-enabled, switch
   > `SUPABASE_ANON_KEY` back to the legacy JWT.)

3. In each repo you want tracked, add `.claude/project.json`:
   ```json
   {
     "client_id": "<clients uuid>",
     "project_id": "<projects uuid>",
     "primary_role": "developer",
     "token_source": "pr_commit"
   }
   ```
   `token_source` must be one of: `pr_commit`, `pr_review`, `planning`, `design`,
   `research`, `manual`.

## Verify it works

Run a short session in the instrumented repo (make a trivial edit), then end it. Check:

```sql
select source, hours, occurred_on, occurred_hour from man_hour_entries
  where project_id='<uuid>' order by created_at desc limit 3;
select kind, amount, source from token_entries
  where project_id='<uuid>' order by created_at desc limit 4;
```

Expect a `1.00` `auto_session` hour and a `human`/`claude` token pair, attributed to your
team member. Re-running within the same clock-hour must NOT add a second hour.

## Contract

See `docs/architecture/session-ingest-contract.md` in the human-token-tracker repo for the
full request schema (both `author_email` and `user_id` are accepted; `author_email` is
preferred for hooks).
