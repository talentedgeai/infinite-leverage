# Your AI Team — First Actions Guide

Your team is ready. Here is everything needed to get started.

---

## Your 8 agents

Open Terminal, navigate to the project, and run `claude`. Then talk to agents:

**Build Team**
- `@product-manager` — "What are we working on?" / "Compile today's standups" / "Write a RAG report"
- `@developer` — "Build X" / "Fix this bug" / "Review this code"
- `@qa` — "Test this change" / "What breaks if I do X?"
- `@devops` — "Check deployment status" / "Review git history" (escalates to human engineer when needed)

**GTM Team**
- `@writer` — "Write this week's post" (or runs automatically every Monday 9am)
- `@designer` — "Generate the hero image" (or runs automatically every Tuesday 9am)
- `@web-publisher` — "Publish this post" (or runs automatically every Wednesday 9am)
- `@email-marketer` — "Draft a welcome email" / "Write this week's newsletter"

---

## Daily workflow

**Content publishes itself Monday–Wednesday.** The only required actions:

1. **Queue a post** — create folder `content/topics/{slug}/` and add `brief.md`:
   ```
   Title: [working title — clear, specific, searchable]
   Target keyword: [primary SEO keyword or phrase]
   Audience: [who this is for — be specific, e.g. "women 35-50 going through career transition"]
   Angle: [the unique perspective or hook that makes this different from existing articles]
   Hook idea: [opening line or question that stops the scroll]
   Supporting points: [point 1 / point 2 / point 3 — the argument structure]
   Call to action: [what you want the reader to do after reading]
   Tone: [one word — e.g. empathetic, authoritative, conversational, provocative]
   Deadline: [YYYY-MM-DD or "next Monday"]
   ```

2. **Push to go live** (Wednesday after 9am):
   ```bash
   cd ~/code-projects/{project-slug}
   git push origin main
   ```
   Vercel deploys automatically within 1–2 minutes.

---

## Content pipeline (automatic)

| When | What happens | Action needed |
|------|-------------|---------------|
| Monday 9am | Writer writes post from oldest brief | None |
| Tuesday 9am | Designer generates hero image | None |
| Wednesday 9am | Web Publisher builds page, stages commit | `git push origin main` |
| Thursday 10am | Email Marketer sends weekly outreach | None |

---

## Keep agents updated

When Dave updates the agent team, say in Claude Code:

> **"sync agents"**

Pulls the latest from GitHub and installs automatically.

---

## Live website

URL: `https://{project-slug}.vercel.app`
Repo: `https://github.com/{clientslug}/{project-slug}`

---

## Where to find things

| What | Where |
|------|-------|
| Content queue | `content/topics/` — one folder per post |
| Daily standups | `standup/briefings/` |
| Project tasks | `working_files/tasks/` |
| Publish history | `context/general-project-agent-context/publish-log.md` |

---

## If something goes wrong

- **Agent doesn't respond** → "sync agents"
- **Build fails** → ask `@developer` and paste the error
- **Site not updating after push** → go to `vercel.com/dashboard` → click your project → "Deployments" tab → check status and error logs
- **Not sure what to prioritise** → ask `@product-manager "what should I focus on this week?"`
