---
name: il-doctor
description: Check the Infinite Leverage plugin setup — prerequisites, repo context, and project scaffold health. Use when someone says "il doctor", "check my setup", "is infinite leverage working", "verify my install", or after installing/updating the plugin.
---

# il-doctor — Setup Check

Read-only health check. Run it, show the output as-is, then fix what failed.

## Run

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/il-doctor/scripts/doctor.sh"
```

It prints PASS/FAIL lines for:

- **Prerequisites** — `git`, `gh` (authenticated), `perl`, `node`/`npm`/`npx`, `rsync` —
  exactly what `/il-project` runs (perl for placeholder substitution, node + rsync for
  the Next.js scaffold in step 9)
- **Repo context** — git remote + author email of the current directory
- **Project layout** — when run inside a scaffolded project: `FOLDER-STRUCTURE.md`,
  6 agents in `.claude/agents/`, 24 skills in `.claude/skills/`, `CLAUDE.md` delegation
  block present
- **Companion plugin** — whether `edge8-telemetry` is installed (Edge8-internal; not needed by outside users)

## Interpreting results

- Every FAIL line carries its own `fix:` — apply it directly when it's a
  read-only or local operation (installing a CLI, setting git config).
- `gh` not authenticated → tell the user to run `gh auth login` themselves
  (interactive; never run it for them).
- Missing agents / delegation block inside a project → offer to re-run the
  install step of `/il-project` (step 6) to refresh them.

## Hard rules

- This skill is read-only — it never writes files or settings.
- Telemetry consent, effort tracking, and v1-residue cleanup belong to the
  `/edge8-telemetry` skill (private Edge8 plugin) — if the user asks about
  tracking and that plugin isn't installed, say it's Edge8-internal and not
  part of this product.
