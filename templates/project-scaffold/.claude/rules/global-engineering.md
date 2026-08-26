# Global Engineering Rules

Engineering guardrails that apply to every agent and every action in this repo.

## Git discipline
- Run `git status` before any file work
- Never force-push, never `--no-verify`, never amend pushed commits
- Stage files explicitly — never `git add .` or `git add -A`
- Never commit unless explicitly instructed

## Branch and PR discipline
- Never push directly to `main`
- All changes go through pull requests
- Never merge a PR while CI is red

## Deployment
- Deploys flow through `git push` → CI/CD only
- Never run `vercel deploy` or promote a deployment manually

## Secrets
- Never commit `.env` files or any credential
- Read all secrets from environment variables

## Destructive operations
- Confirm before `rm -rf`, `git reset --hard`, `git branch -D`, or DB drops

## Continuous improvement
When a solution is confirmed working AND explicitly approved, append what was learned to `docs/engineering/changes/{YYYY-MM-DD}-{slug}.md` — the problem, the fix, and what confirmed it.
