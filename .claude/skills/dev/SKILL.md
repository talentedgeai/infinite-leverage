---
name: dev
description: "Developer skill set: planning from project-status, multi-agent delegation, Karpathy coding principles, GitHub hygiene, QA delegation. Covers the full development workflow from plan to merge."
---

# Developer Skill Set

## 1. Planning from Project Status

Read `docs/project-status.html` and `docs/product/epic-status.md` to identify:
- Open/approved items in the daily plan
- Bugs listed in epic-status.md
- Pending items from previous plans

Draft a daily plan file at `docs/plans/plan-{index}-{YYYY-MM-DD}.md`:

```markdown
# Plan #{index} — YYYY-MM-DD

## Approved Items
| # | Item | Epic | Risk | Assigned |
|---|------|------|------|----------|

## Bugs to Fix
| # | Bug | Epic | Severity |

## Definition of Done for Each Item
```

Present the plan for confirmation before executing.

## 2. Multi-Agent Delegation

Use the multi-agent orchestrator pattern: assess → plan → distribute → collect → validate → report.

For complex tasks, decompose into independent work items and dispatch parallel sub-agents via the Task tool. Each sub-agent prompt must include: scope, goal, constraints, output format.

Wave execution model:
```
Wave 1: [Agent A] [Agent B] [Agent C]   ← independent, parallel
Wave 2: [Agent D] [Agent E]             ← depends on Wave 1 results
```

Refer to `multi-agent-feature-skill` for the full orchestrator protocol.

## 3. Karpathy Coding Principles

Prefer code that is:
- **Auditable** — a reader can understand every line without context
- **Minimal** — no framework added unless the alternative is materially worse
- **Runnable** — no unnecessary dependencies; the simpler version ships first
- **Clear intent** — obvious naming and structure beats clever abstraction

When pulled toward a complex solution, ask: *"What is the simplest version that works?"*

## 4. GitHub Hygiene

- Run `git status` before any file work. Stop if uncommitted changes or merge conflicts.
- Never force-push. Never skip hooks. Never amend pushed commits.
- Never `git add .` or `git add -A` — stage files explicitly by name.
- Never push directly to `main` or `master`. All changes through PRs.
- Branch naming: `feat/{kebab-case-slug}` or `fix/{kebab-case-slug}`.
- PR title: `[type]: [concise description]`. Body: what changed + why + QA result.
- Squash merge to main. Delete the branch after merge.
- Never merge while CI checks are failing.

## 5. QA Delegation

After implementation:
1. Invoke `@qa "QA review needed: [summary of what was built, files changed, acceptance criteria]"` 
2. Wait for QA to run tests and report results
3. Read QA report from `docs/project-status.html`
4. If failures: fix each issue → re-invoke QA → repeat until green
5. Only merge after QA returns PASS

## File Paths

| Artifact | Path |
|----------|------|
| Daily plans | `docs/plans/plan-{index}-{YYYY-MM-DD}.md` |
| PRs | GitHub PR interface |
| QA status | `docs/project-status.html` |
