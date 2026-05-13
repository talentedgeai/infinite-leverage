# Multi-Agent Wave Development — Guidelines

**Author:** Trac Nguyen  
**Last updated:** 2026-05-11

---

## Overview

This guideline documents two interlocking practices used for all feature and incident work in this repo:

1. **Multi-agent wave execution** — how parallel agents are dispatched and how they must behave
2. **5-doc incident/feature documentation** — the output standard every completed piece of work must produce

Both practices are enforced by the `superpowers:dispatching-parallel-agents` skill and the `docs-structure` skill. When used together, they produce fast, parallel investigation with a clean, auditable output trail.

---

## Part 1: Multi-Agent Wave Execution

### What a "Wave" Is

A wave is a batch of agents dispatched in a single message, all running concurrently. Waves are sequential — Wave 2 starts only after Wave 1 is fully resolved. Within a wave, every agent is fully independent.

```
Wave 1: [Agent A] [Agent B] [Agent C]   ← all dispatched simultaneously
           ↓          ↓          ↓
         done        done        done
                     ↓
Wave 2: [Agent D] [Agent E]             ← uses Wave 1 results as input
```

### When to Use Parallel Dispatch

| Situation | Action |
|-----------|--------|
| 2+ independent failures/tasks | Dispatch one agent per domain |
| Tasks share state or depend on each other | Sequential agents or single agent |
| Single problem, unclear root cause | Single agent investigates first |
| Agents would edit the same files | Do NOT dispatch in parallel |

### Agent Prompt Requirements

Every agent prompt must include:

1. **Scope** — exactly what files, subsystem, or test this agent owns
2. **Goal** — single clear deliverable (e.g. "make these tests pass", "find root cause", "implement X endpoint")
3. **Constraints** — what the agent must NOT touch
4. **Output format** — what the agent must return when done (see below)

**Template:**
```
You are working on [specific scope]. Your goal: [single deliverable].

Context:
- [relevant background the agent needs to understand the problem]
- [error messages / failing tests / requirements, verbatim]

Constraints:
- Do NOT modify [files/systems outside scope]
- Do NOT ask clarifying questions — make the best call and document your reasoning

When done, return:
- Root cause / decision made
- Files created or modified (path + one-line description)
- Any caveats or follow-up items
```

### Autonomous Execution Rule — Non-Negotiable

**Agents must run to completion without pausing to ask questions.**

This applies to every agent in every wave. Agents have all context they need in their prompt. If something is ambiguous, they must make the best reasonable call and document the assumption in their output. They must never:
- Ask the coordinator (user) for clarification mid-task
- Pause to confirm a decision before acting
- Request additional context that should have been in the prompt

If an agent would need to ask, that means the prompt is incomplete — fix the prompt before dispatching.

### Wave Coordinator Responsibilities

The coordinator (Claude Code) is responsible for:

| Responsibility | When |
|----------------|------|
| Decompose task into independent domains | Before Wave 1 |
| Craft complete, self-contained agent prompts | Before each wave |
| Collect and synthesize all agent outputs | After each wave |
| Check for conflicts between agent changes | After each wave |
| Decide whether a Wave 2 is needed | After Wave 1 resolves |
| Write the 5-doc output (see Part 2) | After all waves complete |

### Output Synthesis

After all agents complete, the coordinator must produce a unified summary:

```
## Wave Results

### Agent: [scope name]
- Root cause: ...
- Files changed: ...
- Caveats: ...

### Agent: [scope name]
...

## Integration
- Conflicts found: none / [list]
- Follow-up waves needed: none / [describe]
```

---

## Part 2: 5-Doc Documentation Standard

Every completed feature or incident must produce exactly five files inside a `YYYY-MM-DD-<slug>/` folder nested under `docs/engineering/development/YYYY-MM-consolidated/`.

### Required Files

| File | Purpose | When to Write |
|------|---------|---------------|
| `ASSESSMENT.md` | Problem statement, requirements, scope, risks, dependencies | Before or during implementation |
| `EXEC_PLAN.md` | Phase-by-phase checklist of what was done | During implementation; check off as you go |
| `TECH_PLAN.md` | Architecture, schema, API contracts, data flows | Before or during implementation |
| `CHANGELOG.md` | What changed — files created/modified, migrations applied, env vars added | After implementation |
| `QA_REPORT.md` | Test results, manual verification steps, edge cases hit | After testing |

### ASSESSMENT.md Structure

```markdown
# ASSESSMENT: <Feature/Incident Name>

**Date:** YYYY-MM-DD
**Author:** <name>
**Status:** In Progress | Implemented & Verified

## Problem Statement
<1–3 paragraphs: what was broken/missing and why it matters>

## Requirements
<numbered list of functional requirements>

## Scope
### In Scope
### Out of Scope

## Risks & Mitigations
| Risk | Severity | Mitigation |

## Dependencies
<list of external systems, env vars, existing services relied upon>
```

### EXEC_PLAN.md Structure

```markdown
# EXECUTION PLAN: <Feature/Incident Name>

**Date:** YYYY-MM-DD
**Author:** <name>

## Phase 1: <Name> (Complete | In Progress)
- [x] Done item
- [ ] Pending item

## Activation Checklist
<steps to enable in production>
```

### TECH_PLAN.md Structure

```markdown
# TECHNICAL PLAN: <Feature/Incident Name>

**Date:** YYYY-MM-DD
**Author:** <name>

## Architecture
<ASCII diagram of component relationships>

## Database Schema
<table definitions with columns, types, constraints, indexes>

## API Endpoints
| Method | Path | Auth | Description |

## Data Flow
<numbered steps through the system>

## Key Implementation Decisions
<decisions made and why — especially non-obvious tradeoffs>
```

### CHANGELOG.md Structure

```markdown
# CHANGELOG: <Feature/Incident Name>

**Date:** YYYY-MM-DD
**Author:** <name>

## Files Created
- `path/to/file.py` — one-line description

## Files Modified
- `path/to/file.py` — what changed and why

## Database Changes
- Migration: <description>

## Environment Variables
- `VAR_NAME` — purpose, required/optional

## Breaking Changes
<any API or behavior changes consumers must know about>
```

### QA_REPORT.md Structure

```markdown
# QA REPORT: <Feature/Incident Name>

**Date:** YYYY-MM-DD
**Author:** <name>
**Test Result:** PASS | FAIL

## Automated Tests
| Suite | Tests | Pass | Fail |

## Manual Verification
- [ ] Step 1
- [ ] Step 2

## Edge Cases Tested
<list with observed behavior>

## Known Issues / Follow-ups
<deferred items with rationale>
```

### Folder Naming

```
docs/engineering/development/2026-05-consolidated/
└── 2026-05-11-my-feature/
    ├── ASSESSMENT.md
    ├── EXEC_PLAN.md
    ├── TECH_PLAN.md
    ├── CHANGELOG.md
    └── QA_REPORT.md
```

- Slug: lowercase, hyphen-separated, descriptive but short
- Never create the folder outside a `YYYY-MM-consolidated/` wrapper
- Update `YYYY-MM-SUMMARY.md` when the entry is complete

---

## Combining Both Practices: Full Workflow

```
1. Receive task/incident
        ↓
2. Write ASSESSMENT.md (scope, risks, deps)
        ↓
3. Write TECH_PLAN.md (architecture, schema)
        ↓
4. Decompose into independent agent domains
        ↓
5. Dispatch Wave 1 agents (parallel, self-contained prompts)
        ↓
6. Collect agent outputs — synthesize, check conflicts
        ↓
7. Dispatch Wave 2 if needed (depends on Wave 1 outputs)
        ↓
8. Mark EXEC_PLAN.md phases complete
        ↓
9. Write CHANGELOG.md (files created/modified, migrations, env vars)
        ↓
10. Write QA_REPORT.md (test results, manual verification)
        ↓
11. Update YYYY-MM-SUMMARY.md
```

**Rule:** Work is not done until all 5 files exist and all EXEC_PLAN phases are checked off.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails |
|--------------|-------------|
| Agent asks a question mid-wave | Breaks parallel execution; coordinator must wait |
| Prompt with ambiguous scope | Agent over-reaches or under-delivers |
| Agents edit the same file | Merge conflicts, unpredictable state |
| Skipping TECH_PLAN for "small" features | Creates undocumented schema/API drift |
| Writing docs after the fact from memory | Loses accuracy; EXEC_PLAN should be checked off live |
| Wave 2 dispatched before Wave 1 fully resolves | Agents act on stale/incomplete context |
