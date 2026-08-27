# Troubleshooting Guide

Quick fixes for the most common problems operators run into. Written for non-technical users.

---

## Agents

### "The agent isn't responding / wrong agent is answering"

1. Make sure you addressed the agent directly: `@developer fix this bug` or `@product-manager write an epic`.
2. If you didn't use `@`, Claude picks the most relevant agent automatically. If it picks wrong, add the `@agent-name` prefix.
3. If no agents respond at all, run `/il-doctor` — it reports whether the 4 agents are actually installed in `.claude/agents/`, and how to refresh them.

---

### "The agent says it doesn't have a skill"

Skills are **per project** — they live in this project's `.claude/skills/`, never in
`~/.claude/`. Check what's installed:

```bash
ls .claude/skills/     # expect 16 skill folders
ls .claude/agents/     # expect 4 agent definitions
```

Run `/il-doctor` for a full check. If agents or skills are missing, re-run step 6 of
`/il-project` to refresh them from the canonical repo.

---

### "The agent did something I didn't ask for / made changes without permission"

1. Check `git status` — see exactly what changed.
2. To undo uncommitted changes: `git checkout -- <filename>` (file by file).
3. Tell Claude explicitly: "Don't make any changes — just tell me what you would do."

---

## Git & GitHub

### "CI is failing on GitHub"

1. Go to your GitHub repo → **Actions** tab → click the failing run.
2. Expand the failing step to see the error message.
3. Tell `@developer` the exact error text — it will fix it.

Common causes:
- **Lint error**: a code style rule was violated. The developer agent can fix it.
- **Type error**: TypeScript found a type mismatch. Developer can fix it.
- **Build error**: Next.js couldn't compile. Usually a missing environment variable in GitHub Secrets — check Step 3 of the `devops-cicd` skill.

---

### "The site is broken / production is down"

**Fastest fix (do this first, investigate after):**

1. Go to [vercel.com](https://vercel.com) → open your project → click **Deployments**
2. Find the last deployment with a green ✓ (before the broken one)
3. Click the three-dot `···` menu → **Promote to Production**
4. Site is back in ~30 seconds

Then tell `@developer` what happened and ask it to investigate on a branch.

---

### "Claude is trying to push directly to main"

This is blocked by design. All changes go through a pull request. If Claude tries to push to main, it will be blocked by the `pre-bash` hook with an explanation.

If you see this: tell Claude "open a PR instead of pushing directly."

---

## Plugin & Setup

### "My agents or skills look out of date"

The plugin updates itself through the marketplace — there is no patch command to run.
To refresh a *project's* copy of the agents and skills after a plugin update, re-run
step 6 of `/il-project` against that project.

Confirm what you have with `/il-doctor`.

---

### "I see 'permission denied' errors"

The Infinite Leverage plugin ships **no hooks and no permission grants** — if something
is blocking a command, it is either your own project hook (`.claude/hooks/`, e.g. the
one `devops-git-guardrails` installs) or Claude Code's normal permission prompt.

```bash
ls .claude/hooks/ 2>/dev/null        # project hooks, if any
cat .claude/settings.json 2>/dev/null # what they're wired to
```

A `BLOCKED by git-guardrails:` message is the guardrail hook doing its job — read the
reason and take the safe path it suggests rather than disabling it.

---

## Still stuck?

Tell `@developer` the exact error message you see. Paste it verbatim — don't paraphrase. The more context you give, the faster it can fix it.
