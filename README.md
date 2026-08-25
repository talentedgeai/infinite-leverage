# Infinite Leverage (v2)

The Infinite Leverage system in one repo: a bare-minimum Claude Code plugin, the
6 agent definitions, their workflow skills, and the canonical project scaffold.

**v2 principle: nothing installs globally.** The plugin ships 2 skills — no
hooks, no telemetry, no background behavior; agents and workflow skills are
installed **into each client project** by `/il-project`. (Edge8-internal
telemetry and the v1 cleanup live in the separate private `edge8-telemetry`
plugin.)

## Install

Add this repo as a plugin marketplace in Claude Code and install
`infiniteleverage`:

```bash
claude plugin marketplace add talentedgeai/infinite-leverage
claude plugin install infiniteleverage@infiniteleverage
```

Then run `/il-doctor` once — it verifies the prerequisites.

## What the plugin contains

| Piece | What it does |
|---|---|
| `/il-project` | Scaffolds a new client project from `templates/project-scaffold/`, installs the 6 agents + skills **into the project's `.claude/`**, seeds `docs/product/` and `docs/brand/`, initializes git |
| `/il-doctor` | Setup check: prerequisites, repo context, scaffolded-project layout |

## Repo structure

```
.claude-plugin/            ← marketplace manifest (this repo IS the marketplace)
plugin/                    ← the shipped plugin payload
├── .claude-plugin/        ← plugin manifest
└── skills/                ← il-project, il-doctor
.claude/
├── agents/                ← 6 agent definitions (per-project install source)
├── skills/                ← agent workflow skills (per-project install source)
└── rules/                 ← engineering guardrails
templates/project-scaffold/ ← canonical new-project layout
docs/                      ← guides, plans, slides
```

## Where the skills live now

The plugin itself exposes only `/il-project` and `/il-doctor`. Everything else
is **project-scoped**: `/il-project` installs the 6 agents and all workflow
skills below into the new project's own `.claude/`, so they are active only
inside Infinite Leverage projects — never globally on a machine.

The v1 setup skills are retired and replaced:

| v1 (retired) | v2 |
|---|---|
| `/infiniteleverage-init` | Install the plugin + run `/il-project` — there is no machine setup anymore |
| `/infiniteleverage-onboard` | Same — any laptop just installs the plugin |
| `/infiniteleverage-patch` | Marketplace plugin updates; projects refresh via `/il-project` step 6 |
| `/infiniteleverage-validate` | `/il-doctor` (product checks) + `/edge8-telemetry` (Edge8-internal tracking) |
| `/infiniteleverage-project` | `/il-project` |

Machines still carrying the v1 copies keep working until they migrate; the
private `edge8-telemetry` plugin cleans them up on its first run.

## The 6 agents

**Build team**: product-manager, developer, qa, devops · **GTM team**: writer, designer.
(The developer owns publishing; the writer owns email — the old web-publisher and
email-marketer roles were folded in as skills.)

Each agent is a thin definition in [`.claude/agents/`](.claude/agents) listing
the workflow skills it uses; the skills themselves live in
[`.claude/skills/`](.claude/skills). Those two directories are the single
source of truth — this README deliberately doesn't enumerate skills, because a
hand-maintained list is how the v1 docs drifted.

## Updating

1. Edit `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, or `plugin/` — all canonical here
2. Bump the version in `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, update `CHANGELOG.md`
3. Merge to `main` — installed plugins update through the marketplace

Existing projects refresh their agents/skills by re-running the copy step of
`/il-project` (step 6) — or wait for the next scaffolded project to pick up the
latest automatically. There are no zips and no `/infiniteleverage-patch` anymore.

## Migrating from v1

Edge8-internal: handled by the private `edge8-telemetry` plugin (its first
session run cleans v1's global installs, hash-verified). Outside users never
had v1 and need nothing.

## Tests

CI validates the plugin manifests, version lockstep, and the no-global-install
invariants on every PR. (The telemetry test suite moved to `edge8-telemetry`.)
