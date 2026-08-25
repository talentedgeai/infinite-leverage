# Infinite Leverage — canonical repo (v2)

Single source of truth for the Infinite Leverage system: the v2 Claude Code
plugin, the 8 agent definitions, their skills, and the project scaffold.

## Structure
- `.claude-plugin/marketplace.json` — this repo IS the plugin marketplace
- `plugin/` — the shipped plugin payload: 2 skills (`il-project`, `il-doctor`).
  No hooks. Telemetry + v1 cleanup live in the private `edge8-telemetry` repo
- `.claude/agents/` — the 8 agent definitions (installed **per-project** by `il-project`)
- `.claude/skills/` — agent workflow skills (installed **per-project** by `il-project`)
- `.claude/rules/` — engineering guardrails copied into projects
- `templates/project-scaffold/` — the canonical new-project layout

## Hard rules for edits here
- **Nothing installs globally.** No file in this repo may write to `~/.claude/`.
  Never add a `cp` into `~/.claude/` anywhere.
- **Never grant permissions.** No code or skill may touch `permissions` in any
  settings file (the v1 `Bash(*)` grant is the reason v2 exists).
- Agent `.md` files stay thin — role + hard rules + skill index; workflow detail
  lives in skills. Keep each agent under ~4KB.
- No telemetry, hooks, or company-internal content in this public repo —
  that all belongs in `talentedgeai/edge8-telemetry` (private).

## Release flow
Bump `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
versions together (and `VERSION`, kept for v1 machines' update nag), update
`CHANGELOG.md`, merge to `main`. Installed plugins update through the
marketplace — there is no zip/copy step anymore.
