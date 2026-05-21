# Changelog

All notable changes to the Infinite Leverage 8-Agent Templates are recorded here.

Format: `## [version] — YYYY-MM-DD` with sections Added / Changed / Fixed / Removed.

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
