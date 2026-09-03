# Quick prompts — `/il-project`

## Operator invocation

> "Create a new Infinite Leverage project called **Acme Bookstore** at
> `~/code-projects/acme-bookstore`. First topic: `2026-05-20-welcome-launch`.
> Make it look like Linear. Here's the brief: …"

Anything the operator states in the invocation is taken as given — the skill asks
only for what is still missing, in one question, then runs end to end. A pasted
brief or attached PRD seeds `docs/product/` (Step 8.6); a named reference brand,
palette, or mood seeds `docs/brand/` (Step 8.7); with no styling given, a random
getdesign.md reference is used so the project is never style-less.

## Interview script (only for inputs the invocation left out)

1. Project slug? (kebab-case — folder name and GitHub repo name)
2. Human-readable project name?
3. Parent directory? (default `~/code-projects`)
4. First topic date? (default today) and slug? (default `welcome-launch`)
5. Any planning docs or a product description to seed `docs/product/`? (optional)
6. Any styling preference — reference brand, palette, mood? (optional; random getdesign.md pick otherwise)

Not asked: Next.js — it is mandatory. GitHub — asked once, at the very end (Step 12),
unless the invocation already answered it ("no GitHub" / "create the repo").

## Dry-run preview

```
About to scaffold:
  Target          : /Users/.../acme-bookstore
  Project         : Acme Bookstore
  Slug            : acme-bookstore
  First date      : 2026-05-20
  First topic     : welcome-launch
  Next.js         : YES (App Router, TypeScript, Tailwind)        [mandatory]
  Planning docs   : 1 brief detected → will seed docs/product/     [auto, optional]
  Styling         : "like Linear" → will seed docs/brand/          [auto]
  GitHub repo     : asked at the end as a tail question            [optional]
Proceed? (y/N)
```

Only run after an explicit "y".

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `❌ missing required tools: …` (Step 1) | a CLI the later steps need is absent | run `/il-doctor` — every missing tool prints its install command |
| `❌ gh is not authenticated` (Step 1) | GitHub CLI installed but not logged in | the operator runs `gh auth login` themselves; never run it for them |
| `❌ <target> exists` (Step 2) | directory already there | pick a different slug, or the operator removes it deliberately |
| `⚠️ could not read the installed plugin's version` (Step 3) | not running from an installed plugin (a checkout, or `CLAUDE_PLUGIN_ROOT` unset) | falls back to `main`; fine for development, report it if seen on a client machine |
| `⚠️ no tag vX.Y.Z … falling back to main` (Step 3) | the release was merged but never tagged | tag the release (`docs/RELEASE-CHECKLIST.md`, Run 3) — the scaffold and the skill can drift until then |
| `❌ install incomplete` (Step 6) | `.claude/` copy failed part-way, usually a missing `mkdir -p` | do not continue; check `$TMP/il-template/.claude/` exists and re-run Step 6 |
| `create-next-app` refuses the directory (Step 9a) | it was pointed at the non-empty `website/` | it must run in the temp dir and be merged with `rsync --ignore-existing`, exactly as written |
| Step 9e red (`lint` / `tsc` / `build` / `vitest`) | starter kit and create-next-app output disagree, or 9d's provider wiring was skipped | fix and re-run 9e — never commit past a red build (Execution contract, rule 5) |
| Placeholder still present after the run | filename starts with `PH-` (intentional) | rename deliberately on first real use |
| `/il-doctor` reports FAILs inside the new project | a step was skipped or a refresh is due | run `/il-adopt` — the one refresh path for scaffolded and adopted repos |
