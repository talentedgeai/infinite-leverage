---
name: qa
description: "QA skill set: best practices (test pyramid, stability), Dan Shipper style QA planning, documentation under docs/qa and project-status.html. Ensures quality without becoming process overhead."
---

# QA Skill Set

## 1. QA Best Practices

### Test Pyramid (enforce this ratio)

```
        /\
       /  \  e2e (Playwright)
      / 1  \  ← 1 per critical user flow only
     /------\
    /        \  integration (API + DB)
   /  3 to 5  \  ← per feature
  /------------\
 /              \  unit (Jest + React Testing Library)
/   10 or more  \  ← default layer, always start here
```

**Rule**: Start at unit. Only write integration when unit cannot cover the behavior. Only write e2e for flows that touch auth, form submission, payment, or signup.

### Production Quality First
1. **Stability over coverage** — a flaky test that sometimes passes is worse than no test
2. **Maintainability over thoroughness** — tests needing updates on implementation detail changes are a liability
3. **Intent over implementation** — test what the code is supposed to do, never how it does it internally
4. **Fail clearly over fail quietly** — every failure must point to the broken behavior

### Anti-patterns — refuse and fix these
- Screenshot-only e2e (no behavioral assertions)
- Mocking the database (use test DB)
- Testing implementation details (internal state, class names, DOM structure)
- `await sleep(N)` — use `waitFor` or Playwright's automatic waiting
- Ambiguous test names — always describe expected behavior
- Over-mocking — you're testing mocks, not code

## 2. QA Planning (Dan Shipper Style)

QA is not a gate — it is part of the development thread. The goal is to keep the developer in flow, not interrupt with process overhead.

### Principles
- **Immediate feedback**: respond in the same session the Developer calls you
- **Actionable only**: every failure must state exactly what broke and the minimum fix
- **Eliminate overhead**: log results directly to `docs/project-status.html` — no separate ticket system
- **Tight loop**: Developer → QA → Developer is one continuous thread

### Workflow
1. Read the epic/task and extract acceptance criteria (each AC = one or more test cases)
2. Draft a QA plan mapping each AC to a test type (unit/integration/e2e)
3. Present QA plan to Developer before writing tests
4. Write tests (start at unit layer, go higher only when necessary)
5. Run tests — confirm red before implementation, green after
6. Write QA report to the task's engineering doc folder
7. Update `docs/project-status.html` with pass/fail per task
8. Notify Developer immediately with results

## 3. QA Documentation

### Per-task QA report at `docs/engineering/changes/{YYYY-MM}/{YYYY-MM-DD-{slug}}/QA-REPORT.md`:

```markdown
# QA REPORT: {task name}
Date: YYYY-MM-DD | Result: PASS / FAIL

## Acceptance Criteria Coverage
| AC | Test type | Result |

## Automated Tests
| Suite | Tests | Pass | Fail |

## Manual Verification Required
- [ ] item (flag to human)

## Edge Cases Tested

## Known Issues / Follow-ups
```

### Project status dashboard at `docs/project-status.html`:
- ✅ All tests pass — safe to merge
- ❌ Failures — list each with expected vs actual (exact assertion, not "it broke")
- ⚠️ Needs human verification — list what and why

## What AI Can Test
- Unit tests: logic, components, hooks, utilities
- Integration tests: API routes, DB queries, Edge Functions
- e2e: critical flows via Playwright
- TypeScript types, lint, build success

## What AI Cannot Test (flag to human)
- Visual appearance and pixel-level rendering
- Accessibility with real assistive technology
- Real payment flows (Stripe test mode minimum)
- Mobile touch and native device behavior
- Third-party service availability and latency under load
