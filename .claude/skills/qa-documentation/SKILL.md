---
name: qa-documentation
description: >-
  Writes a QA report for each completed task — what was tested, what passed, what failed, and any open questions. Also updates the project status dashboard with the current test results. Creates an audit trail showing the quality of every shipped feature.
---

# QA: Documentation

## Per-Task QA Report

Write `QA-REPORT.md` to `docs/engineering/changes/YYYY-MM/YYYY-MM-DD-{task-slug}/`:

```markdown
# QA REPORT: {task name}
Date: YYYY-MM-DD | Result: PASS / FAIL

## Acceptance Criteria Coverage
| AC | Test type | Result |
|----|-----------|--------|

## Automated Tests
| Suite | Tests | Pass | Fail |

## Manual Verification Required
- [ ] item (flag to human)

## Edge Cases Tested

## Known Issues / Follow-ups
```

## Project Status Dashboard Update

Update `docs/project-status.html` under the relevant task:
- ✅ All tests pass — safe to merge
- ❌ Failures — list each with expected vs actual (exact assertion, not "it broke")
- ⚠️ Needs human verification — list what and why

## File Paths

| Artifact | Path |
|----------|------|
| QA report | `docs/engineering/changes/{YYYY-MM}/{YYYY-MM-DD-{slug}}/QA-REPORT.md` |
| Status view | `docs/project-status.html` |
