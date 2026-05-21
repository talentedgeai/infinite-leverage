# Troubleshooting Guide

Quick fixes for the most common problems operators run into. Written for non-technical users.

---

## Agents

### "The agent isn't responding / wrong agent is answering"

1. Make sure you addressed the agent directly: `@developer fix this bug` or `@product-manager write an epic`.
2. If you didn't use `@`, Claude picks the most relevant agent automatically. If it picks wrong, add the `@agent-name` prefix.
3. If no agents respond at all, run `/infiniteleverage-patch` to reinstall them.

---

### "The agent says it doesn't have a skill"

Skills live in `~/.claude/skills/`. If a skill is missing:

```bash
ls ~/.claude/skills/
```

If the skill folder isn't there, run `/infiniteleverage-patch` — it will sync the latest skills from the canonical template repo.

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

## Scheduled Routines

### "My daily plan / standup isn't running"

1. Check that the routine is registered: go to [claude.ai/code/routines](https://claude.ai/code/routines)
2. If the routine is listed but not running, check that Claude Code is running (the desktop app must be open).
3. If the routine is missing, run Prompt 10 from your `references/phase2-prompts.md` to re-register it.

---

### "I updated agents via /infiniteleverage-patch but the schedule is still running old prompts"

This is expected. Patching copies new skill files but does NOT automatically update running cron jobs.

To update a routine's prompts: go to [claude.ai/code/routines](https://claude.ai/code/routines) → delete the old routine → re-run Prompt 10 from `references/phase2-prompts.md` to recreate it with the new prompt.

---

## Images & Content

### "Image generation failed"

The Designer will give you the exact prompt it tried. You can paste it into one of these free tools:
- [Ideogram](https://ideogram.ai) — best for text in images
- [Midjourney](https://midjourney.com) — best for photography style
- [Adobe Firefly](https://firefly.adobe.com) — good for brand-consistent images

The prompt is also saved to `content/topics/{slug}/image-prompts.md` so you can find it later.

---

### "The email went out without my approval"

This should never happen — the Email Marketer agent is configured to always draft and show you the email before sending. If a send happened without approval, check `agents/email-marketer/context/outreach-log.md` to see what was sent, then contact Resend or Brevo support to cancel any queued sends.

---

## Plugin & Setup

### "The session-start message says I'm behind on the template version"

Run `/infiniteleverage-patch` in Claude Code. It will:
1. Show you exactly what changed since your installed version
2. Ask for confirmation before applying any changes
3. Update your local agents and skills to the latest version

---

### "I see 'hook failed' or 'permission denied' errors"

The safety hooks (`pre-bash`, `prompt-submit`) must be installed at `~/.claude/hooks/`. Check:

```bash
ls ~/.claude/hooks/
```

If the hooks folder is empty or missing, run `/infiniteleverage-patch` — it will reinstall them.

---

## Still stuck?

Tell `@developer` the exact error message you see. Paste it verbatim — don't paraphrase. The more context you give, the faster it can fix it.
