---
name: pm-contribution-sync
description: >-
  Fan-out skill: discovers every project under ~/code-projects/, runs
  scripts/team-hours.py for each, updates the #contributors table and #pulse
  chart in each project's docs/project-status.html, and writes a
  scripts/contribution-snapshot.json per project for hub aggregation.
  Respects the three-basis methodology and all editorial rules from
  docs/assessments/team-hours-methodology.md.
---

# PM — Contribution Sync (Fan-out)

This skill runs across **all projects** on the operator's machine. It is the
mechanism that keeps every `project-status.html` current without requiring
manual per-project runs.

---

## Step 1 — Discover projects

```bash
ls ~/code-projects/
```

Collect every directory under `~/code-projects/`. For each, check:
1. Does `docs/project-status.html` exist? → include in sync list
2. Does `scripts/team-hours.py` exist? → if not, copy from `~/.claude/skills/pm-contribution-sync/team-hours.py` (deployed by `infiniteleverage-patch`)

Skip dirs that are clearly not Infinite Leverage projects (no `.git`, no `CLAUDE.md`).

---

## Step 2 — Resolve per-project parameters

For each project directory, auto-detect:

### Authors
```bash
git -C ~/code-projects/<slug> log --format='%aN' --all | sort | uniq -c | sort -rn | head -10
```
Use the top committers. If `CLAUDE.md` has an `## Authors` section with explicit names, prefer that.

### JSONL keyword
The Claude project directory name is the project path with `/` replaced by `-`.
Derive the keyword from the project slug:
```bash
# e.g. project slug = "acme-bookstore"
# JSONL dirs will match *acme-bookstore* or *acme* depending on path length
ls ~/.claude/projects/ | grep -i "<slug>"
```
Use the shortest unambiguous substring of the project slug that matches exactly one set of JSONL dirs.
If multiple matches exist (e.g. "wha" matches many), use the full slug.

### Timezone
Read from `.env` or `CLAUDE.md`. If absent, default to `+00:00` and note it.

---

## Step 3 — Run team-hours.py per project

For each project in the sync list, resolve `--author-email` from `CLAUDE.md ## Authors` (format: `Name <email>`) or from `git log --format='%aN <%aE>'`. Pair each `--author` with the matching `--author-email` positionally.

```bash
python3 ~/code-projects/<slug>/scripts/team-hours.py \
  --start <window-start> \
  --end <window-end> \
  --author "<author1>" --author-email "<email1>" \
  --author "<author2>" --author-email "<email2>" \
  --jsonl-keyword <keyword> \
  --tz <offset> \
  --with-tokens \
  --project-slug <slug> \
  --json \
  --sync-output ~/code-projects/<slug>/scripts/contribution-sync.json \
  --repo ~/code-projects/<slug> \
  > ~/code-projects/<slug>/scripts/contribution-snapshot.json
```

`--sync-output` writes `contribution-sync.json` alongside the snapshot (see Step 5b).

**Window:** default = last 7 days (Mon–Sun). On the first run for a project, use the window since the earliest commit if ≤ 30 days; otherwise default to last 7.

**If team-hours.py exits non-zero for a project:** log the error, skip that project, continue with others. Never abort the full fan-out for one bad project.

---

## Step 4 — Update each project-status.html

For each project with a fresh `contribution-snapshot.json`:

### 4a — Team Contributions table (`#contributors`)

Read the snapshot JSON. Build the two-row headline table:

| Row | Who | Rule |
|---|---|---|
| Owner | Person with the most commits + highest resolved hours, or name from `CLAUDE.md ## Owner` | If CLAUDE.md has explicit Owner, always use that |
| Development team | Everyone else | List names as a sub-line |

Columns: **Human tokens (h)** · **Claude tokens billed (M)** · **Commits** · **PRs merged** · **Window**

Label hours as **"Human tokens"** (methodology editorial rule 7). The unit is hours but the label is intentional — it parallels Claude tokens.

Apply all editorial rules:
- Cite basis per row (`commit-span` / `claude-jsonl` / `self-reported`)
- Append new window-slice — never overwrite the cumulative table
- Footnote if JSONL figures exist for an author other than the script-runner

### 4b — Pulse chart (`#pulse`)

Read per-day data from the snapshot. Update each series data point for the window.
Apply peak-normalisation: `y = 100 × raw / max(raw over window)` per series.
Update the reading-guide paragraph with the new peak day and absolute value.

The Pulse chart is an inline SVG — no JS, no external deps. Edit the SVG `polyline`/`circle` elements in place using the methodology §5.5 colour tokens and line styles.

---

## Step 5 — Write contribution-snapshot.json

The snapshot is the machine-readable handoff to `pm-hub-report`. Schema:

```json
{
  "project_slug": "acme-bookstore",
  "project_path": "/Users/.../code-projects/acme-bookstore",
  "window": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "authors": { ... },
  "tokens_window": { "billed": 0, "total": 0 },
  "no_jsonl": false,
  "jsonl_dirs_scanned": [],
  "synced_at": "ISO-8601"
}
```

Write to `~/code-projects/<slug>/scripts/contribution-snapshot.json`. This file is gitignored (add to `.gitignore` if not already present — it contains machine-local JSONL paths).

---

## Step 5b — Write contribution-sync.json (DB ingestion file)

`team-hours.py --sync-output` produces this file automatically alongside the snapshot. It contains direct POST payloads for the `human-token-tracker` Supabase edge functions.

**Schema:**

```json
{
  "schema_version": 1,
  "generated_at": "ISO-8601",
  "project_slug": "acme-bookstore",
  "window": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "_notes": {
    "human_tokens_unit": "centihours (resolved_hours × 100)",
    "claude_tokens_unit": "raw billed tokens (operator account, attributed to dominant author per day)",
    "man_hours_target": "POST each entry to ingest-session-start with client_id + project_id from env",
    "token_entries_target": "POST each entry to ingest-session-end with client_id + project_id from env"
  },
  "man_hours": [
    {
      "author_email": "trac@edge8.ai",
      "occurred_on": "2026-06-01",
      "occurred_hour": 9,
      "primary_role": null
    }
  ],
  "token_entries": [
    {
      "author_email": "trac@edge8.ai",
      "occurred_at": "2026-06-01T09:00:00+07:00",
      "source": "pr_commit",
      "human_tokens": 150,
      "claude_tokens": 45000
    }
  ]
}
```

**Field notes:**
- `man_hours` → one entry per author per git commit-hour. Maps to `ingest-session-start` → `man_hour_entries` (idempotent via unique index on `team_member_id + occurred_on + occurred_hour` WHERE `auto_session`).
- `token_entries` → one entry per author per active day. Maps to `ingest-session-end` → `token_entries`. `human_tokens` in centihours (int); `claude_tokens` = billed tokens (operator total, attributed to the author with the most resolved hours that day — see methodology §2.4).
- `author_email` is resolved server-side via `resolve_team_member` RPC — no UUID lookup needed in the workflow.
- The GitHub workflow adds `client_id` and `project_id` from environment secrets before posting.

**gitignore:** Add `scripts/contribution-sync.json` to `.gitignore` — it contains private email and timing data.

**Sample GitHub workflow step:**

```yaml
- name: Ingest team hours
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    INGEST_SECRET: ${{ secrets.INGEST_SECRET }}
    CLIENT_ID: ${{ secrets.HUMAN_TOKEN_CLIENT_ID }}
    PROJECT_ID: ${{ secrets.HUMAN_TOKEN_PROJECT_ID }}
  run: |
    jq -c '.man_hours[]' scripts/contribution-sync.json | while read entry; do
      curl -sf -X POST "$SUPABASE_URL/functions/v1/ingest-session-start" \
        -H "x-ingest-secret: $INGEST_SECRET" \
        -H "Content-Type: application/json" \
        -d "$(echo "$entry" | jq --arg c "$CLIENT_ID" --arg p "$PROJECT_ID" \
              '. + {client_id:$c, project_id:$p}')"
    done
    jq -c '.token_entries[]' scripts/contribution-sync.json | while read entry; do
      curl -sf -X POST "$SUPABASE_URL/functions/v1/ingest-session-end" \
        -H "x-ingest-secret: $INGEST_SECRET" \
        -H "Content-Type: application/json" \
        -d "$(echo "$entry" | jq --arg c "$CLIENT_ID" --arg p "$PROJECT_ID" \
              '. + {client_id:$c, project_id:$p}')"
    done
```

---

## Step 6 — Summary report

After all projects are processed, print:

```
✅ Contribution sync complete
Projects updated: N
Projects skipped (errors): N

Per project:
  acme-bookstore   — Owner: X h human tokens, Y M Claude tokens billed
  ...
```

Then invoke `pm-hub-report` to aggregate snapshots into the centralized dashboard.
