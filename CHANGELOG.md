# Changelog

All notable changes to the Infinite Leverage 8-Agent Templates are recorded here.

Format: `## [version] — YYYY-MM-DD` with sections Added / Changed / Fixed / Removed.

---

## [2.2.0] — 2026-08-25

**The skill cut.** Audit of all 62 workflow skills (dependency graph + staleness + redundancy
vs current models) → 35 survive. `/il-project` installs roughly half of what it used to.

### Removed
- **11 orphans** nothing referenced: create-agent, create-local-routine, create-remote-routine,
  github-flow, global-caveman, pm-contribution-sync, pm-hub-report, seo-audit,
  speckit-git-commit, speckit-git-remote, speckit-implement (~110KB, frozen since May–June)
- **15 "teach the model to think" skills** current models make redundant (and that degrade
  them): the dev-* soft belt (brainstorm, karpathy, zoom-out, grill, multi-agent, prototype,
  planning, handoff, improve-arch, diagnose, github-hygiene, qa-delegation) and
  qa-best-practices / qa-planning / qa-documentation. Their few real rules are folded into
  the developer/qa agent files as short "Working style" sections
- **The autonomous cron rhythm** (decided dead): .claude/scheduled-tasks/ (11 schedule defs),
  pm-standup, the scaffold's standup/ tree, and the team-hours scripts

### Changed
- pm-epic-writing routes straight to dev-feature-plan (dev-planning removed)
- agent-routing rows for removed skills keep their trigger → agent mapping
- Survivors: content pipeline (writer/designer/publisher/email ×9), PM discovery pipeline
  (×9 incl. speckit chain ×9), dev-feature-plan + dev-tdd + plan-protocol, devops ×4, qa-triage

---

## [2.1.0] — 2026-08-25

### Changed
- **Telemetry split.** All effort telemetry (il_telemetry hooks, consent flow) and the
  v1 residue cleanup (migrate_v1.py + manifest + tests) moved to the private
  `talentedgeai/edge8-telemetry` plugin. This public repo is now purely the product:
  2 skills, no hooks, no background behavior, no company internals
- `il-doctor` slimmed to a product setup check (prerequisites, repo context, scaffolded
  project layout) and updated to use `${CLAUDE_PLUGIN_ROOT}` in all commands

### Removed
- `plugin/hooks/` entirely; the `hooks` key in plugin.json
- `docs/assessments/` (internal effort-measurement methodology + self-audits) and
  `docs/superpowers/` (internal feature specs) — moved to the private repo.
  Note: this repo has always been public, so these remain in public git history;
  removal is about discoverability, not secrecy

---

## [2.0.0] — 2026-08-25

**The bare-minimum release.** One repo, one plugin, nothing global. Addresses the two
problems from client review: v1 installed far too much (95 skills + 8 agents + hooks +
a Bash(*) permission grant, all user-global via cp -R), and the prompts had drifted
behind current models.

### Added
- **v2 plugin shipped from this repo** — `.claude-plugin/` marketplace + `plugin/` payload;
  hooks run via `${CLAUDE_PLUGIN_ROOT}` (v1's hooks.json pointed at `~/.claude/hooks/*`, so
  plugin updates never took effect without a manual copy step)
- **`/il-doctor`** — health check + telemetry consent + v1 residue report (replaces
  `infiniteleverage-validate` and the patch health-check)
- **`migrate_v1.py`** — one-time, hash-verified cleanup of v1's global installs. Removes only
  byte-exact copies of files v1 shipped (manifest generated from the full git history of both
  v1 repos); modified files and symlinks are reported, never deleted. Also removes the v1
  `Bash(*)` grant, `acceptEdits` default, and stale v1 hook registrations from settings files
- **Telemetry consent gate** — `il_telemetry.consent`; every entrypoint (stop/flush/scan) is
  opt-in. No consent → no capture, no delivery, no network calls
- **Registration cache TTL (7d, both directions)** — v1 cached only negatives, permanently:
  a repo registered after first probe was silenced forever. Positives are now cached too, so
  no per-session probes
- **API-first delivery** — records POST to the tracker's `/api/telemetry/ingest` when live,
  falling back to the v1 git-append path meanwhile
- **CI** — pytest suite (48 tests incl. migration safety) runs on Python 3.9 and 3.12

### Changed
- **`infiniteleverage-project` → `il-project` (3.0.0)** — no more machine-init prerequisite;
  installs agents + skills into the project's `.claude/` only
- **All 8 agents rewritten for current models** — 37KB → 17KB; boilerplate deduplicated,
  dated "research practitioners before acting" crutches dropped, contradictions removed;
  every unique hard rule preserved
- `VERSION` bumped to 2.0.0 (kept so v1 machines see the update nag one last time)

### Fixed
- **Python 3.9 import failure** — v1's `X | None` annotations crashed the whole telemetry
  package on macOS system python; the `2>/dev/null || true` hooks swallowed it, so v1
  telemetry silently captured nothing on those machines. All modules now carry
  `from __future__ import annotations`

### Removed
- `infiniteleverage-init` / `-patch` / `-onboard` and all global `cp -R` machinery — plugin
  marketplace handles distribution and updates
- `setup-permissions.py` — **never again does any installer write `Bash(*)` or change
  `defaultMode`**
- `pre-bash` / `prompt-submit` hooks (keyword-regex routing hints degrade current models;
  guardrails are a per-project choice via `devops-git-guardrails`)
- `session-start` 4-stage hook (version-check curl, usage briefing, nag lines) and
  `usage-context.py` — no more network calls or transcript scans on session start
- `scaffold-*` skill pack (10), `use-dev-team`/`use-marketing-team`, `infiniteleverage-help`,
  `session-ingest`, lark rules, `plugin-staging/`, committed release zips, `rebuild-zips` CI,
  `effort_selfreport.py` experiment

---

## [1.8.0] — 2026-07-30

### Added
- **plan-protocol skill** — installs, upgrades and diagnoses the Plan Protocol in any repository: a plan registry, a blast-radius guard that fails any change outside a plan's declared `touches`, and a committed pre-push hook. Answers the "20 people and 4 agent runtimes on one machine" problem, where undeclared mega-PRs and semantic (not textual) conflicts are the real failure modes
- **`assets/plan.mjs`** — the engine, as a single dependency-free file (`node:` builtins only). No `tsx`, no build step, no `npm install`, and **no `package.json` required anywhere** — so it installs into a Rails, Django or static client project as readily as a Next one. Verbs: `index · check · sync · guard · submit · premerge · init · doctor`
- **`assets/plan.test.mjs`** — 30 tests on `node:test` (builtin), so a project verifies the protocol with plain `node --test` and no test framework
- **`assets/AGENTS-template.md`** — the protocol document, project-agnostic. `init` copies it to the repo root as `AGENTS.md`, the cross-tool standard Codex, Cursor and Windsurf read natively. Copying a fixed asset rather than writing prose per project is what keeps the protocol identical everywhere
- **Per-project policy in `config.json`** — `hotZones`, `exempt`, `plansDir`, `baseRef`, `verifyCmd` and the rest are data, not code. `init` infers hot zones from the tree (migrations dirs, shared component dirs, lockfiles, CI config). Hot zones differ between two Next apps, never mind across stacks, so a generic engine plus per-project policy is the only shape that ports

### Notes
- The skill **installs** enforcement and is never the enforcement itself. Skills only fire in Claude Code; the teeth are a git hook plus the engine, both committed, so they bind every runtime — including ones that never read `CLAUDE.md`
- Two failure modes the skill's `doctor` exists to catch, because both look exactly like working enforcement: git **silently ignores a non-executable hook**, and enforcement is **not retroactive** — `core.hooksPath` is per-clone config while the hook file is per-branch content, so a branch cut before install is unguarded until it merges the base branch

---

## [1.3.1] — 2026-05-21

### Added
- **devops-cicd skill** — generates a GitHub Actions CI pipeline (lint → type-check → test → build) for Next.js + Vercel projects
- **CI workflow** (`.github/workflows/rebuild-zips.yml`) — automatically rebuilds setup-skill zips and publishes a GitHub Release on every push to `main` that touches agents or skills
- **Troubleshooting guide** (`docs/guide/troubleshooting.md`) — plain-English fixes for the most common operator problems
- **Plugin PreToolUse hook** — `plugin-staging/hooks/hooks.json` now registers `pre-bash` and `prompt-submit` hooks via the plugin, so safety guardrails are active on plugin-only installs (not just full init installs)
- **Plugin UserPromptSubmit hook** — `prompt-submit` (agent routing hints) now wired through the plugin

### Changed
- **developer.md** — Skills section reorganised by use case (Planning, Building, Debugging, Wrapping up) and expanded to include all 14 developer skills: `dev-feature-plan`, `dev-brainstorm`, `dev-zoom-out`, `dev-tdd`, `dev-prototype`, `dev-improve-arch`, `dev-diagnose`, `dev-grill`, `dev-handoff` (previously undocumented)
- **developer.md** — "Testing and deployment" section clarified: `npm test` / `npx jest` / `npx playwright test` (headless) are explicitly allowed; only `next dev` / `npm run dev` (dev server) is prohibited
- **developer.md** — Added plain-English "If something goes wrong" section with CI failure, production rollback, and blocked-credential responses
- **qa.md** — Added `qa-triage` to Skills (was missing from the agent shell). Added "What QA can do autonomously" and "What QA flags to a human" sections for clarity
- **devops.md** — Added `devops-setup-pre-commit`, `devops-cicd`, and `devops-git-guardrails` to Skills section
- **devops-ops/SKILL.md** — Added "Production Rollback" section with operator-friendly step-by-step Vercel dashboard instructions. Removed "secret rotation" from escalation triggers (too technical; operators are not expected to know how to do this)
- **writer.md** — Added `marketing-strategist` skill to Skills section. Added "Brand voice" and "Non-English content" guidance sections
- **email-marketer.md** — Added explicit "Hard rules" section: always draft first, unsubscribe link in every email, opted-in only, no duplicates
- **designer.md** — Added "If image generation fails" section with manual fallback instructions (Ideogram, Midjourney, Adobe Firefly) and prompt-save behaviour
- **dev-tdd/SKILL.md** — Added clarification table: running `npm test` is allowed (it is not a dev server); only `next dev` / `npm run dev` is prohibited
- **README.md** — Skills directory listing and agent/skills tables updated to reflect all skills (previously only 5 of 14 developer skills were listed)
- **README.md** — "Updating Agent Templates" section updated to describe CI-based release flow

### Fixed
- TDD hard rule vs. "no localhost server" contradiction — both rules now consistently refer to different things (`npm test` vs `npm run dev`) and are no longer in conflict

---

## [1.3.0] — 2026-05-20

### Added
- `infiniteleverage-help` skill — full skill menu by team
- Personal laptop setup skill (in addition to Mac Mini setup)

### Changed
- Renamed `create-local-task` → `create-local-routine`
- Pre-bash and prompt-submit hooks now installed via `infiniteleverage-init` and `infiniteleverage-onboard`

---

## [1.2.0] — prior

- Hook scripts (`pre-bash`, `prompt-submit`) added to block force-push, `git add .`, and `--no-verify`
- Plugin staging directory added for Claude Team marketplace distribution
- `devops-git-guardrails` skill added

---

## [1.1.0] — prior

- `qa-triage` skill added with P0–P3 scoring and routing
- `dev-diagnose` skill added (6-phase scientific debugging)
- `dev-handoff` skill added (structured HANDOFF.md format)

---

## [1.0.0] — initial release

- 8 agent shells: product-manager, developer, qa, devops, writer, designer, web-publisher, email-marketer
- 21 foundational skills
- 3 bootstrap skills: infiniteleverage-init, infiniteleverage-onboard, infiniteleverage-patch
- Global engineering rules, agent routing rules, Lark optional integration rules
