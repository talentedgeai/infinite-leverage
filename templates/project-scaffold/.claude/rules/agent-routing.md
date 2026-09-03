# Agent Routing Rules

These rules govern when and how agents are automatically triggered from conversation context. Claude Code reads this file alongside `CLAUDE.md` and routes work to the right agent without requiring an explicit `@agent` call.

---

## Dev Team — Auto-Routing Triggers

The following context patterns automatically invoke the relevant dev team agent.

| Trigger Context | Agent | Skill (if applicable) |
|---|---|---|
| "plan", "spec", "write an epic", "what should we build", "acceptance criteria" | product-manager | — |
| "create issues", "break into tickets", "to issues" | product-manager | `pm-to-issues` |
| "validate plan", "check against epics", "grill with docs" | product-manager | `pm-grill-with-docs` |
| "build", "implement", "code this", "write the function" | developer | — |
| "debug", "why is this broken", "diagnose", "I can't figure out" | developer | — (agent handles natively) |
| "zoom out", "give me context on this module", "I'm new to this area" | developer | — (agent handles natively) |
| "grill me", "stress-test this plan", "what could go wrong" | developer | — (agent handles natively) |
| "tdd", "test-driven", "red-green-refactor" | developer | `dev-tdd` |
| "spike", "prototype", "is this feasible", "hard unknown" | developer | — (agent handles natively) |
| "improve architecture", "refactor this module", "tech debt" | developer | — (agent handles natively) |
| "handoff", "wrapping up", "passing to QA", "done for now" | developer | — (agent handles natively) |
| "triage", "classify this bug", "prioritise this bug" | qa | `qa-triage` |
| "test strategy", "what to test", "test plan" | qa | — (agent handles natively) |
| "ci/cd", "pipeline", "github actions", "deployment setup" | devops | — |
| "pre-commit", "husky", "lint-staged" | devops | `devops-setup-pre-commit` |
| "git hooks", "protect main", "guardrails" | devops | `devops-git-guardrails` |

## Publishing — Auto-Routing Triggers

| Trigger Context | Agent | Skill (if applicable) |
|---|---|---|
| "publish", "build the page", "push to site", "update blog index" | developer | `web-publisher-publish` |

---

## Hard Rules

These cannot be overridden by operator instructions:

1. **Developer never starts without an approved PM plan.** If there is no approved plan, route to PM first.
2. **QA never skips triage.** Every bug is classified and scored before being assigned.
3. **DevOps never deploys directly.** All deployments flow through `git push` → CI/CD pipeline.
4. **Publishing never lands on `main` directly.** The Developer owns publishing (`web-publisher-publish`): commit on a `publish/{slug}` branch, open a PR, merge only under the auto-merge criteria in `developer.md`.
5. **No agent merges its own PR — unless the change is trivial and self-contained.** See auto-merge criteria in `developer.md`. For all other changes: Developer opens → QA verifies → operator merges.

---

## Team Routing Skills

For full routing context in any session, invoke:

The routing table above **is** the full index. Each agent's own definition in
`.claude/agents/` lists the skills it owns; each skill's `SKILL.md` carries its
own trigger phrases. There are no separate team-routing skills.

## Something not working?

- Agents or skills not loading → run `/il-doctor` in the repo; it names what is missing and the fix (`/il-adopt` refreshes the team in place). Restart Claude Code after any change under `.claude/`.
- CI red, deployment failed, production down → `devops-ops` (health checks, logs, the 60-second rollback).

---

## Cross-Team Handoff Points

| From | To | Trigger |
|---|---|---|
| PM (approved plan) | Developer | Plan signed off — issues created |
| Developer (feature complete) | QA | Dev handoff doc written |
| QA (bugs found) | Developer | Triage report → P0/P1 bugs |
| QA (all pass) | Developer (publish) | QA sign-off on content changes |
