---
name: infiniteleverage-validate
description: Validate that effort tracking is set up correctly for this contributor and repo. Use this skill when someone says "validate effort tracking", "am I being tracked", "check my telemetry setup", "is my Claude usage logged", "verify telemetry", "check if I'm logging hours", "am I capturing effort", or "is effort tracking working".
version: 1.0.0
---

# infiniteleverage-validate — Contributor Effort Tracking Self-Check

## Canonical Source

This skill is distributed from:
> https://github.com/talentedgeai/infiniteleverage-8-agents-template

Skill path in the template repo: `setup-skills/infiniteleverage-validate/`

---

## Purpose

A contributor runs `/infiniteleverage-validate` to confirm:

1. **Machine** — their local Claude Code hooks directory and event wiring are in place
2. **Repo** — the current git repo is registered for effort tracking at [human-tokens.com](https://human-tokens.com)
3. **Capture** — Claude session data is actually being written to the local outbox
4. **Delivery** — records are reaching the central `telemetry` branch of `talentedgeai/human-token-tracker`

The skill prints a clear PASS / FAIL per check and an overall PASS / PENDING verdict with remediation steps.

---

## Step 1 — Run the validator script

```bash
bash ~/.claude/skills/infiniteleverage-validate/scripts/validate.sh
```

The script is read-only and always exits 0. It never modifies files or prints secrets.

---

## Step 2 — Interpret and present the results

After the script finishes, present its output to the contributor as a formatted table, then give the overall verdict using exactly these labels:

### Overall PASS

> **Set up and logging**
>
> All checks passed. Your Claude token usage and human hours are being captured and delivered to the central tracker.
>
> Note: dashboard numbers at [human-tokens.com](https://human-tokens.com) may lag until the next ingest run — this is normal.

### Overall PENDING (one or more FAILs)

List each FAIL with its fix, grouped by section:

| Section | What's missing | How to fix |
|---------|---------------|------------|
| A · Machine | `~/.claude/hooks/il_telemetry/` missing | Update the Infinite Leverage plugin + run `/infiniteleverage-patch` |
| A · Machine | `Stop` / `SessionEnd` / `SessionStart` not wired | Update the Infinite Leverage plugin + run `/infiniteleverage-patch` |
| A · Machine | `gh` not authenticated | Run `gh auth login` |
| A · Machine | `git user.email` empty | Run `git config --global user.email 'you@example.com'` |
| B · Repo | Repo not registered | Run registration step in `/infiniteleverage-project` Step 13 (or ask the operator to register it) |
| B · Repo | Declined marker present | Delete `~/.claude/.il-telemetry/unregistered/<owner>__<repo>` then re-run Step 13 |
| C · Capture | Outbox dir never created | Run at least one Claude session in this repo, then end it — the `SessionEnd` hook writes the first record |
| D · Delivery | No telemetry file on branch | Run a session, end it, and wait ~1 min — the `Stop`/`SessionEnd` hook delivers on exit. If still missing, check `gh auth status` |

Only list rows that are actually failing for this contributor — omit PASS rows from the remediation table.

---

## Notes for Claude

- **If `curl` is unavailable** in the contributor's environment, the script prints a note and marks section B as FAIL. In that case, make the registration HTTP call yourself:
  ```
  GET https://human-tokens.com/api/projects/status?repo=<owner>/<repo>
  ```
  Expect JSON: `{ "registered": true | false, "status"?: "...", "name"?: "..." }`
  Report the result inline and continue.

- **Telemetry path format** (confirmed from `deliver.py`):
  ```
  telemetry/<client_slug>/<project_slug>/<github_login>/<YYYY-MM>.jsonl
  ```
  in the `telemetry` branch of `talentedgeai/human-token-tracker`.

- **Local outbox directory** (confirmed from `stop.py`):
  ```
  ~/.claude/.il-telemetry/outbox/
  ```
  Each pending record is a `<session_id>.json` file. Records are removed after successful delivery.

- **Unregistered / declined marker path**:
  ```
  ~/.claude/.il-telemetry/unregistered/<owner>__<repo>
  ```

- **Never print** the contents of `.env`, credential files, or authentication tokens. The script is designed to avoid this; if you need to diagnose further, tell the contributor to run `gh auth status` themselves.

- **Dashboard lag is expected** — records are ingested on a schedule. A PASS on delivery means the file exists on the branch; the dashboard number updates on the next ingest. Always mention this so contributors don't assume something is broken.
