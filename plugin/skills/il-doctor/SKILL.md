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
- **Project layout** — inside a project scaffolded by `/il-project` **or** adopted
  with `/il-adopt` (detected by `FOLDER-STRUCTURE.md`, `.claude/agents/`, or the
  delegation block): the 4 canonical agents present in `.claude/agents/` (custom
  extras are fine), 16 skills in `.claude/skills/`, `global-engineering.md` in
  `.claude/rules/`, no retired v2.4-era agents/skills lingering (writer/designer and
  their content pipeline), and a `CLAUDE.md` delegation block that is present **and
  current** (a v2.4 block still routes to writer/designer)
- **Plugin version** — installed vs. newest release tag; names the update command
- **Companion plugin** — whether `edge8-telemetry` is installed (Edge8-internal; not needed by outside users)

## Interpreting results

- Every FAIL line carries its own `fix:` — apply it directly when it's a
  read-only or local operation (installing a CLI, setting git config).
- `gh` not authenticated → tell the user to run `gh auth login` themselves
  (interactive; never run it for them).
- Any project-layout FAIL (missing agents, skills, rules, retired leftovers, stale
  or missing delegation block) → offer to run `/il-adopt`. It is the one refresh
  path for scaffolded and adopted repos alike: it reinstalls the canonical files,
  retires the v2.4 set by moving it to `.claude/retired-il-<date>/`, and replaces
  only the managed block in `CLAUDE.md`.

## Hard rules

- This skill is read-only — it never writes files or settings.
- Telemetry consent, effort tracking, and v1-residue cleanup belong to the
  `/edge8-telemetry` skill (private Edge8 plugin) — if the user asks about
  tracking and that plugin isn't installed, say it's Edge8-internal and not
  part of this product.
