# Infinite Leverage — canonical repo (v2)

Single source of truth for the Infinite Leverage system: the v2 Claude Code
plugin, the 8 agent definitions, their skills, and the project scaffold.

## Structure
- `.claude-plugin/marketplace.json` — this repo IS the plugin marketplace
- `plugin/` — the shipped plugin payload: 2 skills (`il-project`, `il-doctor`),
  opt-in telemetry hooks, and the one-time v1 residue cleanup (`migrate_v1.py`)
- `.claude/agents/` — the 8 agent definitions (installed **per-project** by `il-project`)
- `.claude/skills/` — agent workflow skills (installed **per-project** by `il-project`)
- `.claude/rules/` — engineering guardrails copied into projects
- `templates/project-scaffold/` — the canonical new-project layout

## Hard rules for edits here
- **Nothing installs globally.** No file in this repo may write to `~/.claude/`
  outside the plugin's own consent file and the one-time migration. Never add a
  `cp` into `~/.claude/` anywhere.
- **Never grant permissions.** No code or skill may touch `permissions` in any
  settings file (the v1 `Bash(*)` grant is the reason v2 exists).
- Agent `.md` files stay thin — role + hard rules + skill index; workflow detail
  lives in skills. Keep each agent under ~4KB.
- Telemetry is opt-in only; every entrypoint is gated on
  `il_telemetry.consent.has_consent()`. Keep it that way.
- Tests: `cd plugin/hooks && python3 -m pytest test_migrate_v1.py il_telemetry/tests`
  must pass on Python 3.9 (system CommandLineTools python). No `X | Y` unions
  without `from __future__ import annotations`.

## Release flow
Bump `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
versions together (and `VERSION`, kept for v1 machines' update nag), update
`CHANGELOG.md`, merge to `main`. Installed plugins update through the
marketplace — there is no zip/copy step anymore.
