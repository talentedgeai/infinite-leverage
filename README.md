# Infinite Leverage (v2)

The Infinite Leverage system in one repo: a bare-minimum Claude Code plugin, the
8 agent definitions, their workflow skills, and the canonical project scaffold.

**v2 principle: nothing installs globally.** The plugin ships 2 skills and
opt-in telemetry; agents and workflow skills are installed **into each client
project** by `/il-project`. The v1 era of copying 90+ skills and 8 agents into
every machine's `~/.claude/` is over — the plugin's first run cleans that
residue up (see [Migration](#migrating-from-v1)).

## Install

Add this repo as a plugin marketplace in Claude Code and install
`infiniteleverage`:

```bash
claude plugin marketplace add talentedgeai/infiniteleverage-8-agents-template
claude plugin install infiniteleverage@infiniteleverage
```

Then run `/il-doctor` once — it verifies the setup and asks about telemetry
consent (telemetry is **off** until you explicitly opt in).

## What the plugin contains

| Piece | What it does |
|---|---|
| `/il-project` | Scaffolds a new client project from `templates/project-scaffold/`, installs the 8 agents + skills **into the project's `.claude/`**, seeds `docs/product/` and `docs/brand/`, initializes git |
| `/il-doctor` | Health check (plugin, repo, registration, outbox), telemetry consent management, v1 residue report |
| Telemetry hooks | Opt-in only. On Stop/SessionEnd, captures per-session token totals + active minutes for **registered client repos** and delivers to the effort tracker. No consent → no capture, no network calls |
| `migrate_v1.py` | One-time, hash-verified cleanup of everything v1 copied into `~/.claude/` (agents, skills, hooks, rules, the `Bash(*)` permission grant). Modified files are reported, never deleted |

## Repo structure

```
.claude-plugin/            ← marketplace manifest (this repo IS the marketplace)
plugin/                    ← the shipped plugin payload
├── .claude-plugin/        ← plugin manifest (v2.0.0)
├── hooks/                 ← hooks.json (${CLAUDE_PLUGIN_ROOT} paths), il_telemetry/, migrate_v1.py
└── skills/                ← il-project, il-doctor
.claude/
├── agents/                ← 8 agent definitions (per-project install source)
├── skills/                ← agent workflow skills (per-project install source)
└── rules/                 ← engineering guardrails
templates/project-scaffold/ ← canonical new-project layout
docs/                      ← guides, assessments, plans
```

## The 8 agents & their skills

### Build team
| Agent | Skills |
|-------|--------|
| product-manager | `pm-client-interview`, `pm-documentation`, `pm-project-status`, `pm-standup`, `pm-epic-writing` (+ speckit pipeline), `pm-constitution-sync` |
| developer | `dev-planning`, `dev-feature-plan`, `dev-brainstorm`, `dev-zoom-out`, `dev-karpathy`, `dev-tdd`, `dev-prototype`, `dev-improve-arch`, `dev-multi-agent`, `dev-github-hygiene`, `dev-diagnose`, `dev-grill`, `dev-qa-delegation`, `dev-handoff`, `plan-protocol` |
| qa | `qa-triage`, `qa-best-practices`, `qa-planning`, `qa-documentation` |
| devops | `devops-ops`, `devops-setup-pre-commit`, `devops-cicd`, `devops-git-guardrails` |

### GTM team
| Agent | Skills |
|-------|--------|
| writer | `writer-seo-content`, `writer-quality-critique`, `marketing-strategist` |
| designer | `designer-design-system`, `designer-ui-ux`, `designer-style-to-photo`, `designer-image-generation` |
| web-publisher | `web-publisher-publish` |
| email-marketer | `email-marketer-nurture` |

## Updating

1. Edit `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, or `plugin/` — all canonical here
2. Bump the version in `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, update `CHANGELOG.md`
3. Merge to `main` — installed plugins update through the marketplace

Existing projects refresh their agents/skills by re-running the copy step of
`/il-project` (step 6) — or wait for the next scaffolded project to pick up the
latest automatically. There are no zips and no `/infiniteleverage-patch` anymore.

## Migrating from v1

v1 (`infiniteleverage-plugin` repo + `/infiniteleverage-init` + `/infiniteleverage-patch`) is
superseded and frozen:

1. Remove the old plugin/marketplace from Claude Code settings; install v2 (above).
2. On the first session, `migrate_v1.py` removes v1's global residue — only
   byte-exact copies of files v1 actually shipped (verified against the full git
   history of both v1 repos). Anything you modified is reported and left alone.
3. Run `/il-doctor` to see what's left and handle it case by case (scheduled
   tasks and modified files are never auto-removed).

## Tests

```bash
cd plugin/hooks && python3 -m pytest test_migrate_v1.py il_telemetry/tests
```

Must pass on Python 3.9 (macOS system python) — v1 telemetry silently failed to
import on 3.9 for months; CI now guards against that class of bug.
