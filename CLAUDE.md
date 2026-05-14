# Infinite Leverage — 8-Agent Templates

This repo is the single source of truth for the 8 universal Infinite Leverage agent definitions and their 21 dedicated skills.

## Structure
- `.claude/agents/` — Thin agent shells (role + skill references only)
- `.claude/skills/` — 21 standalone skill files, one per capability
- `.claude/rules/` — Global engineering guardrails
- `setup-skills/` — Bootstrap skills (init, onboard, patch) for deployment zips
- `scripts/rebuild-zips.sh` — Sync agents + skills into bootstrap bundles and rebuild zips

## Workflow
1. Edit `.claude/agents/*.md` or `.claude/skills/*/SKILL.md`
2. Run `./scripts/rebuild-zips.sh` to rebuild deployment zips
3. Upload to GitHub Releases or deploy to Claude Team

## Guidelines
- Agent `.md` files are thin — delegate workflow detail to skills
- Each skill is granular (one capability) and self-contained
- Skills load from `~/.claude/skills/<name>/` at runtime
- Never put project-specific context here — that goes in per-project repos
