# Changelog

All notable changes to the Infinite Leverage agent templates are recorded here.

Format: `## [version] — YYYY-MM-DD` with sections Added / Changed / Fixed / Removed.

---

## [2.4.4] — 2026-08-26

**The plan-protocol engine, actually run.** A 35 KB engine with its own 30-test suite ships
into every scaffolded project, and nothing had ever executed either — not CI, not a review.
Running it end to end surfaced a portability bug that made the skill's headline claim false.

### Fixed
- **`plan-protocol` imposed one client's domain vocabulary on every project.** The engine
  hard-coded `components: ['learner', 'manager', 'admin', 'platform']` and `init` never
  wrote the key into `config.json`, so it was invisible and unoverridable in practice —
  a Rails shop had to label its billing work `learner`. The skill's own description says it
  "works in any stack". `components` now ships **empty**, meaning any non-empty component
  string is valid; a project opts into a fixed vocabulary by filling the list in, and the
  enum is enforced against that. A missing `component` is still an error.
  Backwards compatible: an install that already sets `components` keeps its enum
- **`init` now writes `components` into `config.json`** so the knob is discoverable, and
  `bootstrapPlan` no longer indexes into a possibly-empty list

### Added
- **CI runs the plan-protocol engine suite** (`node --test`, 32 tests, no install needed).
  It had never run; a regression in the enforcement engine would have shipped silently
- **CI asserts the engine ships no domain vocabulary** — `DEFAULT_CONFIG.components` must be
  empty. Verified against the regression: reintroducing the old list fails the build
- Two engine tests for the taxonomy modes (free-form by default, enforced when configured),
  replacing the one that asserted the client-specific enum

### Verified end to end (not just unit-tested)
Installed the protocol into two throwaway repos — a Next-shaped one and a Rails-shaped one:
- `init` writes `config.json`, scaffolds `.githooks/pre-push` mode 755, sets
  `core.hooksPath`, seeds a bootstrap plan, and `doctor` reports enforcing
- hot-zone detection found the Rails layout (`db/migrate`, `Gemfile`) with no Node marker
- the pre-push hook **blocks a direct push to `main`**
- the blast-radius guard exits 1 on an undeclared hot-zone change, and the pre-push hook
  blocks that push too — the protocol's core promise, now demonstrated rather than asserted

### Changed
- `SKILL.md` documents `components` in the policy list; `AGENTS-template.md` no longer
  implies the list is always populated

---

## [2.4.3] — 2026-08-26

**Scaffold-to-CI continuity.** Verified that a project `il-project` produces passes the
pipeline `devops-cicd` installs, and documented what Next 16 now adds on its own.

### Verified (no code change needed)
- **The first commit does not swallow `node_modules`.** Step 10 stages every untracked
  file *after* Step 9's `npm install`; confirmed the root `.gitignore` and
  create-next-app's `website/.gitignore` both cover it — 158 files, 1.1 MB, zero
  `node_modules`, `.next`, or `.env` entries
- **`npm ci` works from the committed lockfile**, and every file the generated pipeline
  reads (`package.json`, `package-lock.json`, `tsconfig.json`, `eslint.config.mjs`,
  `vitest.config.mts`, `vitest.setup.ts`) is in that first commit
- **The generated CI pipeline is green on a fresh project**: install, lint, type check,
  test (20 passing), build — all exit 0

### Added
- `website/AGENTS.md` and `website/CLAUDE.md` documented in `FOLDER-STRUCTURE.md` and
  `il-project` step 9. Next 16's create-next-app writes both (`CLAUDE.md` is a one-line
  `@AGENTS.md` import; `next dev` rewrites the block inside `AGENTS.md`). They are
  framework-owned, they load only when an agent works inside `website/`, and they must not
  be confused with the repo-root `CLAUDE.md` that carries the agent-delegation block or a
  repo-root `AGENTS.md` installed by `plan-protocol`

---

## [2.4.2] — 2026-08-26

**The web template, actually run.** `il-project` step 9 had never been executed end to
end in CI or in review. Running it revealed the shipped Next.js starter fails its own
pipeline, plus a dependency that only resolved by luck. CI now guards the whole class.

### Fixed
- **The web template failed `npm run lint` with 2 errors**, so every new project's first
  CI run — from the pipeline `devops-cicd` installs — went red on template code the
  operator never wrote:
  - `components/upload/FilePreview.tsx` called `setState` synchronously inside an effect
    (`react-hooks/set-state-in-effect`). The object URL is now derived with `useMemo` and
    revoked in a cleanup effect, which also removes a cascading render and the flash of
    the file icon before the thumbnail
  - `lib/chat/queries.test.ts` returned an anonymous wrapper component
    (`react/display-name`) — now a named `Wrapper`
  - Two unused-variable warnings cleared: `Link` in `MobileDrawer.tsx`, and the unused
    props parameter (plus its now-orphaned type import) in `MDXEditorFull.tsx`
- **`unified` was imported but never installed.** `MarkdownRenderer.tsx` does
  `import type { PluggableList } from 'unified'`; step 9c never listed it, so it resolved
  only because npm hoists it as a transitive dep of react-markdown. Added to step 9c
- **`vitest.config.ts` → `vitest.config.mts`.** Vitest warned that ESM syntax in a
  CommonJS-loaded config breaks under `configLoader: 'native'`, planned to become the
  default. The `.mts` extension makes it explicitly ESM
- **Step 6's install check was a `printf`, not a gate.** It only stopped when a count hit
  zero. Now asserts 6 agents and ≥20 skills and exits non-zero otherwise — and counts with
  `find` rather than a glob, because under zsh a non-matching glob aborts the command
  instead of returning nothing

### Changed
- **Step 9e verifies the full pipeline**, not half of it: `npm run lint && npx tsc
  --noEmit && npm run build && npx vitest run`. The previous gate ran build + vitest only,
  which is exactly why two lint errors shipped
- **`FilePreview` gained a test** (`FilePreview.test.tsx`, 6 cases) covering the
  thumbnail, the non-image icon path, size formatting, `onRemove`, revoke-on-unmount, and
  URL rotation when the file changes — the path the `useMemo` refactor could have broken

### Added — CI guards for everything this review found
The existing "no global-install regressions" check grepped only for `cp`, which is why
`il-project` step 13's `mkdir`/`touch` into `~/.claude` survived three releases. Now:
- Any write verb (`cp`/`mv`/`mkdir`/`touch`/`tee`/`rm`/`ln`/`install`) or shell
  redirection targeting `~/.claude`, `$HOME/.claude` or `${HOME}/.claude` fails the build,
  as does any mention of `human-token-tracker` or `il-telemetry` in the shipped payload
- Agent and skill counts are asserted (6 / 24) **and cross-checked against the threshold
  hard-coded in `doctor.sh`** — the drift that produced "found 6/8"
- Every skill must have frontmatter whose `name` matches its directory
- Every package the web template imports must be declared by step 9c

Each guard was verified against the bug it targets: re-injecting the step-13 telemetry
write, restoring `-ge 8`, and removing `unified` each fail CI.

---

## [2.4.1] — 2026-08-26

**Final skill review.** A full pass over all 26 skills, the 6 agents, the routing rules and
the scaffold. Three of these were install-breaking.

### Fixed
- **`il-project` step 6 never installed the agents.** The scaffold ships `.claude/rules/`
  and `.claude/skills/` but not `.claude/agents/`, so `cp .../agents/*.md "$TARGET/.claude/agents/"`
  failed with `Not a directory` and every new project came up with zero agents. Step 6 now
  `mkdir -p`s all three destinations and verifies the counts (6 agents / 24 skills) before
  continuing
- **`il-doctor` failed on every healthy project.** The agent check asserted `-ge 8` against a
  6-agent roster and told the operator to re-run an install step that was already correct.
  Now checks 6, and also verifies the 24 skills landed
- **Prerequisite checks matched neither reality nor each other.** `il-project` checked
  `gh`/`git`/`perl` while mandatory step 9 needs `node`/`npm`/`npx`/`rsync`; `il-doctor`
  checked a different set again. Both now check the same union, and `il-project` verifies
  `gh auth status` up front
- **`web-publisher-publish` pushed to `main`, then asked whether it was on a branch.**
  Phase 5 ran `git push origin main` and Phase 6 then offered a PR flow that could never be
  reached. Now: `publish/{slug}` branch → PR → merge only under the auto-merge criteria in
  `developer.md`, with the preview URL handed over when it stops for approval
- **`devops-git-guardrails` blocked `--amend` on branches that were never pushed** — the
  upstream check treated "no upstream" as "already published". Rewritten around
  `@{upstream}` with the logic verified against real repos; also fixes `--force-with-lease`
  slipping through, and moves from the deprecated `{"decision":…}` output to exit-code 2
- **`qa-triage` wrote bugs into a "Known Issues" heading that `epic-status.md` never has.**
  Now writes to the At-a-glance count and the Drilldown section that actually exist
- **`writer-seo-content`'s image-prompt example was a broken nested code fence** — the inner
  ```json fence terminated the outer block early. Outer fence is now four backticks
- **`devops-cicd` ran `npm test -- --ci`**, a Jest-only flag the scaffold's Vitest rejects.
  Now `npx vitest run --passWithNoTests`, with the Jest equivalent noted
- **`designer-image-generation` stretched hero images** — bare `scale=1200:630` on any source
  that isn't 40:21. Now scale-and-crop, and it creates the scratch dir it writes to
- Dead references removed repo-wide: `developer (publishing)-publish` in the routing table,
  `/use-dev-team` and `/use-marketing-team`, `docs/product/01-product-timeline.md`,
  `/capture-learning`, and ~15 skill names retired in 2.2.0/2.4.0

### Removed
- **Effort-tracking registration (`il-project` step 13).** It wrote to `~/.claude/`, pushed
  client names and their staff's git emails to `talentedgeai/human-token-tracker`, and
  referenced a session-start hook this plugin doesn't ship — contradicting the repo's own
  "nothing global, no telemetry" rule, both manifests, and the skill's own execution
  contract. Telemetry belongs to the private `edge8-telemetry` plugin. "telemetry" dropped
  from the plugin keywords and the marketplace description
- **`pm-project-status`'s team-hours machinery.** §6/§7 depended on `scripts/team-hours.py`
  and `docs/assessments/team-hours-methodology.md` — neither ships — and carried
  client-specific language ("human tokens", owner "carries clinical/regulatory risk").
  Replaced with a Contributor Activity table and a Pulse Chart built only from `git`, `gh`,
  `epic-status.md` and `docs/qa/`
- **v1 documents that contradicted the shipped product**: `docs/guide/agent-map.html`
  (titled "8-Agent Team"), `docs/guide/SCAFFOLD.md` and `docs/install-prompt.md` (both
  documenting the retired global `~/.claude/` install). Nothing linked them; recoverable
  from git history
- **Two byte-identical duplicates of the intro deck** (`Infinite-Leverage-8-Introduction.html`,
  `infinite-leverage-introduction.html`). `docs/slides/index.html` is the single copy, and
  its text now names `/il-project` and `/il-doctor` instead of the retired
  `/infiniteleverage-init|onboard|patch`, a 6-agent roster, and the one-repo-is-the-
  marketplace architecture
- **A real contributor's usage data shipped in the scaffold.** `templates/project-scaffold/docs/project-status.html`
  carried a hard-coded username, hour count and token total, plus a call to a
  `~/.claude/hooks/` script this plugin doesn't ship — copied into every new client
  project. Replaced with an empty git/gh-derived Contributor activity table

### Changed
- **Email is draft-only in the skill body, not just the description.** `email-marketer-nurture`
  said "drafted for operator approval" in its frontmatter while its workflows said "send to
  all active subscribers". The hard rule is now the first thing in the body, and its state
  files moved from the non-existent `agents/email-marketer/` to `agents/writer/context/`
- **Image-prompt ownership settled.** The Writer owns `image-prompts.md` (JSON);
  `designer-style-to-photo` now tunes its `style`/`mood`/`palette` in place instead of
  authoring a competing key-value prompt. `FOLDER-STRUCTURE.md` and the scaffold stub
  renamed `images.md` → `image-prompts.md` to match
- **No skill commits without instruction.** `pm-constitution-sync`, `pm-project-status`,
  `dev-tdd`, `devops-cicd`, `devops-setup-pre-commit` and `devops-git-guardrails` all
  auto-committed against `global-engineering.md`; they now stage and hand off
- **`devops-git-guardrails` is project-scoped and merges settings.** It no longer offers
  `~/.claude/settings.json`, and registers its hook without clobbering existing keys
- **`marketing-strategist` writes to paths that exist** — `context/source-material/`,
  `content/content-calendar/content-calendar.md`; dropped the invented `content/images/`
  and the handoff to a non-existent "Content Producer"
- `pm-grill-with-docs` and `pm-to-issues` added to the PM's skill index (previously
  reachable from the routing table but absent from the agent)
- `docs/guide/AGENTS.md` rewritten for the 6-agent roster; `troubleshooting.md` de-v1'd
- `qa-triage` gains severity floors so a rare-but-catastrophic security bug can't score P2

---

## [2.4.0] — 2026-08-25

**The speckit collapse.** The 9-skill speckit chain + 2 guard skills folded into the 4 skills
that orchestrated them. 35 → 24 skills; ~33KB of chained skill-hopping becomes one 8.9KB
self-contained pipeline.

### Changed
- **pm-epic-writing** absorbs speckit-specify, speckit-git-feature, speckit-clarify +
  pm-clarify-guard, speckit-analyze + pm-analyze-split — the full discovery pipeline inline:
  spec format, business-level question filter, gap analysis with the client/dev finding split.
  Upstream spec-kit boilerplate (extension-hook protocols, $ARGUMENTS blocks, orphaned /slash
  references) dropped entirely
- **dev-feature-plan** absorbs speckit-git-validate, speckit-plan, speckit-tasks — branch
  validation, impl-plan format, and the task-checklist format inline
- **pm-to-issues** absorbs speckit-taskstoissues — one skill for both sources (tasks.md or
  spec slicing), with the GitHub-remote-only safety gate and issue-number write-back
- **pm-constitution-sync** absorbs speckit-constitution — create + sync in one skill
- All `.specify/` output paths unchanged — scaffolded projects and existing specs unaffected

---

## [2.3.0] — 2026-08-25

**Six agents, skills that actually trigger.**

### Changed
- **Agent roster 8 → 6** — web-publisher folded into the developer (an agent forbidden from
  writing code that existed to call the developer was ceremony, not a colleague); email-marketer
  folded into the writer with its hard rules (draft-only, unsubscribe, opt-in, no dupes) intact.
  Delegation blocks, routing rules, scaffold, and docs updated
- **Trigger-phrase pass on 17 operator-facing skills** — 25 of 35 descriptions had no "use when"
  language, so skills never auto-fired (a direct cause of "doesn't work great with the models").
  Pipeline-internal skills (speckit chain, guards) correctly keep their called-within descriptions
- web-publisher-publish rewritten developer-owned (no delegation ceremony); email-marketer-nurture
  writer-owned

### Fixed
- designer-image-generation pinned `gemini-2.0-flash-preview-image-generation` — a dead early-2025
  preview model; now instructs resolving the current image-capable model at run time
- designer-image-generation read `images.md` while the writer produces `image-prompts.md` — the
  two halves of the content pipeline disagreed on the handoff filename

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
