# Quick prompts — `infiniteleverage-project`

## Operator invocation

> "Create a new Infinite Leverage project called **Acme Bookstore** at `~/code-projects/acme-bookstore`. First topic: `2026-05-20-welcome-launch`. Owner: Dave Hajdu."

The skill will collect any missing inputs and confirm before scaffolding.

## Interview script (if the operator gives no details)

1. What's the project slug? (kebab-case, used as folder + repo name)
2. What's the human-readable project name?
3. Where should it live? (default `~/code-projects`)
4. First publish date? (default today)
5. First topic slug? (default `welcome-launch`)
6. Project owner name?
7. Default content author?
8. Scaffold Next.js into `website/` now? (Y/n)
9. Create GitHub repo and push? (Y/n)
10. Which GitHub org? (only asked if step 9 = Y)

## Dry-run preview

Before running, print the plan:

```
About to scaffold:
  Target      : /Users/.../acme-bookstore
  Project     : Acme Bookstore
  Slug        : acme-bookstore
  First date  : 2026-05-20
  First topic : welcome-launch
  Next.js     : YES (will run create-next-app)
  GitHub repo : YES (talentedgeai/acme-bookstore, private)

Proceed? (y/N)
```

Only run after explicit "y".

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| `❌ already exists` | Target directory not empty | Pick different slug or `rm -rf` (with confirmation) |
| `gh: command not found` | GitHub CLI not installed | Run `brew install gh` first |
| `agents not installed` | Skipped `infiniteleverage-init` | Operator must run init Phase 2 Prompt 7 first |
| Placeholder still present after run | Filename starts with `PH-` (intentional) | Rename deliberately on first real use |
