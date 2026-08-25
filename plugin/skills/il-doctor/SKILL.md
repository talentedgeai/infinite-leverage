---
name: il-doctor
description: Check the Infinite Leverage plugin setup and manage effort-telemetry consent. Use when someone says "il doctor", "check my setup", "validate effort tracking", "am I being tracked", "is my Claude usage logged", "verify telemetry", "opt in to tracking", "opt out of tracking", or after installing/updating the plugin.
---

# il-doctor — Setup Check and Telemetry Consent

One skill, three jobs: verify the plugin works on this machine, manage the
contributor's telemetry consent, and report any leftover v1 residue.

## Step 1 — Run the health check

```bash
bash "$(dirname "$SKILL_PATH")/scripts/doctor.sh"
```

(If `$SKILL_PATH` is unavailable, locate `doctor.sh` under this skill's
`scripts/` directory and run it with bash.) Show the output to the user as-is.
It is read-only and prints PASS/FAIL lines for:

- **Plugin** — python3 available, telemetry package imports, hooks runnable
- **Consent** — current telemetry consent state (`granted` / `denied` / `unset`)
- **Repo** — git remote, git author email, `gh` auth (needed for the delivery fallback)
- **Registration** — whether this repo is registered in the effort tracker (cached)
- **Outbox** — captured sessions awaiting delivery
- **v1 residue** — anything the old global install left behind (report only)

## Step 2 — Handle consent

Telemetry NEVER captures or delivers anything without explicit opt-in.

- If consent is **unset**: explain in two sentences what is collected — per-session
  token totals, active minutes, git author email, GitHub login, and repo name,
  delivered to Edge8's effort tracker for registered client repos only; nothing
  else, no code, no prompts. Then ask directly: "Opt in to effort tracking?"
- If the user says yes / no (or asks to opt in / out at any time), record it:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/hooks" python3 -c "from il_telemetry.consent import set_consent; set_consent(True)"   # or False
```

- Never set consent without the user answering. Never re-ask once answered
  unless the user brings it up.

## Step 3 — v1 residue

If the health check reported v1 leftovers, summarize them and offer the choices:

- "modified" files → list them; the user decides per file (delete / keep). Only
  delete on their explicit confirmation.
- v1 scheduled tasks → list names; offer to remove the ones the user confirms.
- To re-run the automated cleanup preview:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/migrate_v1.py" --report
```

## Hard rules

- Read-only by default — the only writes this skill ever makes are the consent
  file, and residue deletions the user explicitly confirmed one by one.
- Never touch `permissions` in any settings file.
- Report failures plainly with the exact fix; no soft-pedaling.
