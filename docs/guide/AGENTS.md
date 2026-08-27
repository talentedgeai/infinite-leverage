# Agent Guide

The Infinite Leverage team is **4 agents**, installed **per project** into that
project's own `.claude/` — by `/il-project` for a new project, or `/il-adopt` for
a repo that already exists. Nothing lives in `~/.claude/`.

- Agent definitions: [`.claude/agents/`](../../.claude/agents) — 4 files
- Workflow skills: [`.claude/skills/`](../../.claude/skills) — 16 skills
- Routing table: [`.claude/rules/agent-routing.md`](../../.claude/rules/agent-routing.md)
- Engineering guardrails: [`.claude/rules/global-engineering.md`](../../.claude/rules/global-engineering.md)

Those directories are the single source of truth. This page is a map, not a copy — if it
disagrees with a `SKILL.md` or an agent definition, the source file wins.

---

## The roster

| Agent | Owns | Skills |
|---|---|---|
| **product-manager** | Roadmap, specs, epics, `project-status.html`, approval triage | `pm-client-interview`, `pm-documentation`, `pm-constitution-sync`, `pm-epic-writing`, `pm-grill-with-docs`, `pm-to-issues`, `pm-project-status` |
| **developer** | Implementation, debugging, architecture, **publishing posts** | `dev-feature-plan`, `dev-tdd`, `plan-protocol`, `web-publisher-publish` |
| **qa** | Test strategy, bug triage, regression verification | `qa-triage` |
| **devops** | CI/CD, Vercel operations, git guardrails | `devops-ops`, `devops-cicd`, `devops-setup-pre-commit`, `devops-git-guardrails` |

One v1 agent was folded in rather than retired: **web-publisher → developer**. There is
no separate publisher agent; its skill kept its name. The writer and designer agents
(and their skills, including email) were removed in v2.6.0.

---

## The chains

**Feature work**

```
pm-epic-writing → pm-grill-with-docs → (operator approves) → pm-to-issues
                → dev-feature-plan → dev-tdd → qa-triage → PR → operator merges
```

**Publishing**

```
operator provides finished post + hero image in content/topics/{slug}/
                   → web-publisher-publish (branch + PR) → Vercel green
```

---

## Hard rules that cross agents

1. The Developer never starts without a plan the PM approved.
2. Every bug is triaged (`qa-triage`) before anyone works on it. Security and
   data-integrity bugs carry a priority floor.
3. Nothing is committed unless the operator asked for it; nothing is pushed to `main`.
   All changes land through a PR.
4. No agent merges its own PR except under the auto-merge criteria in
   [`developer.md`](../../.claude/agents/developer.md).

---

## Where output goes

| Artifact | Path |
|---|---|
| Product strategy | `docs/product/product.md` |
| Epics / epic status | `docs/product/epics.md`, `docs/product/epic-status.md` |
| Specs, plans, tasks | `.specify/features/{slug}/` |
| Constitution | `.specify/memory/constitution.md` → `docs/product/constitution.md` |
| Dashboard | `docs/project-status.html` (+ `.pdf`) |
| QA triage reports | `docs/qa/{YYYY-MM-DD}-{slug}-triage.md` |
| Blog posts | `content/topics/{slug}/` |
| Brand | `docs/brand/style-guide.md` |

Canonical layout: [`templates/project-scaffold/FOLDER-STRUCTURE.md`](../../templates/project-scaffold/FOLDER-STRUCTURE.md).

## Something not working?

See [`troubleshooting.md`](troubleshooting.md), or run `/il-doctor`.
