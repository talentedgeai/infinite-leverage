# Infinite Leverage — canonical repo (v2)

Single source of truth for the Infinite Leverage system: the v2 Claude Code
plugin, the 4 agent definitions, their skills, and the project scaffold.

## Structure
- `.claude-plugin/marketplace.json` — this repo IS the plugin marketplace
- `plugin/` — the shipped plugin payload: 4 skills (`il-project`, `il-adopt`,
  `il-doctor`, `il-memory-cleanup`). No hooks. Telemetry + v1 cleanup live in
  the private `edge8-telemetry` repo
- `.claude/agents/` — the 4 agent definitions (installed **per-project** by `il-project`)
- `.claude/skills/` — agent workflow skills (installed **per-project** by `il-project`)
- `.claude/rules/` — engineering guardrails copied into projects
- `templates/project-scaffold/` — the canonical new-project layout

## Hard rules for edits here
- **Nothing installs globally.** No file in this repo may write to `~/.claude/`.
  Never add a `cp` into `~/.claude/` anywhere. (The one carve-out:
  `il-memory-cleanup` edits the operator's *own memory content* under `~/.claude/`
  at their direction, with per-item approval and a backup first — it never installs
  plugin files, agents, hooks, or settings there.)
- **Never grant permissions.** No code or skill may touch `permissions` in any
  settings file (the v1 `Bash(*)` grant is the reason v2 exists).
- Agent `.md` files stay thin — role + hard rules + skill index; workflow detail
  lives in skills. Keep each agent under ~4KB.
- No telemetry, hooks, or company-internal content in this public repo —
  that all belongs in `talentedgeai/edge8-telemetry` (private).

## Release flow
1. Bump `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
   versions together (and `VERSION`, kept for v1 machines' update nag).
2. Update `CHANGELOG.md`.
3. Merge to `main`.
4. **Tag the merge commit `vX.Y.Z` and push the tag.** This is not optional.
   `/il-project` step 3 clones the tag matching the running plugin's version so
   a client's scaffold matches the skill instructions they are executing; with
   no tag it falls back to `main` and the two can drift. `/il-doctor` also
   compares the installed version against the newest tag to tell a client when
   to update — a cached older plugin is how a fixed bug keeps biting, since the
   `/il-project` steps themselves ship inside the plugin.
5. **Mirror the release to `talentedgeai/infiniteleverage-8-plugin`** (private).
   The claude.ai org plugin directory can only sync private repos, so that repo
   distributes this plugin to every AIO Labs seat ("Installed by default") — a
   webhook on its `main` triggers the directory re-sync. From this repo:

   ```bash
   git clone git@github.com:talentedgeai/infiniteleverage-8-plugin.git /tmp/il-dist
   rm -rf /tmp/il-dist/.claude-plugin /tmp/il-dist/plugin
   git archive vX.Y.Z -- .claude-plugin plugin | tar -x -C /tmp/il-dist
   git -C /tmp/il-dist add -A && git -C /tmp/il-dist commit -m "mirror vX.Y.Z" && git -C /tmp/il-dist push
   ```

   Skipping this leaves org seats on the previous version while external
   installs (public marketplace add) move ahead — exactly the v1 freeze that
   served a June snapshot for 2½ months.

Installed plugins update through the marketplace — there is no zip/copy step.

Before a release that a client will run, work through `docs/RELEASE-CHECKLIST.md`.
