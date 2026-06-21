# Infinite Leverage — 8-Agent Templates

Universal agent definition templates and bootstrap skills for the Infinite Leverage system.

## Repo Structure

```
.claude/                       ← Claude Code convention layout
├── agents/                    ← Thin agent shells (8 files, ~25 lines each — role + skill references)
│   ├── product-manager.md
│   ├── developer.md
│   ├── qa.md
│   ├── devops.md
│   ├── writer.md
│   ├── designer.md
│   ├── web-publisher.md
│   └── email-marketer.md
├── skills/                    ← Standalone skill files (one per capability, rich standalone context)
│   ├── pm-client-interview/
│   ├── pm-documentation/
│   ├── pm-project-status/
│   ├── pm-standup/
│   ├── pm-epic-writing/
│   ├── pm-constitution-sync/
│   ├── dev-planning/
│   ├── dev-feature-plan/
│   ├── dev-brainstorm/
│   ├── dev-zoom-out/
│   ├── dev-karpathy/
│   ├── dev-tdd/
│   ├── dev-prototype/
│   ├── dev-improve-arch/
│   ├── dev-multi-agent/
│   ├── dev-github-hygiene/
│   ├── dev-diagnose/
│   ├── dev-grill/
│   ├── dev-qa-delegation/
│   ├── dev-handoff/
│   ├── qa-triage/
│   ├── qa-best-practices/
│   ├── qa-planning/
│   ├── qa-documentation/
│   ├── devops-ops/
│   ├── devops-setup-pre-commit/
│   ├── devops-cicd/
│   ├── devops-git-guardrails/
│   ├── designer-design-system/
│   ├── designer-ui-ux/
│   ├── designer-style-to-photo/
│   ├── designer-image-generation/
│   ├── writer-seo-content/
│   ├── marketing-strategist/
│   ├── web-publisher-publish/
│   └── email-marketer-nurture/
└── rules/
    └── global-engineering.md  ← Shared engineering guardrails

setup-skills/                  ← Bootstrap skills (outside .claude, for release zips)
├── infiniteleverage-init/     ← Machine setup — Mode A (first-ever) + Mode B (additional machine)
│   ├── SKILL.md
│   ├── agents/                ← Bundled copy (synced from .claude/agents/)
│   ├── references/            ← incl. os-detection, cloud-track-codespaces, pre-retreat-readiness, mode-b-*
│   └── scripts/               ← incl. collect-credentials.py, setup-permissions.py
└── infiniteleverage-patch/    ← Machine sync & agent update
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/

.env.example                   ← Required env vars template
scripts/
└── rebuild-zips.sh            ← Sync agents → rebuild all 3 zips
```

## The 8 Agents & Their Skills

### Build Team
| Agent | Skills (`.claude/skills/`) |
|-------|---------------------------|
| product-manager | `pm-client-interview`, `pm-documentation`, `pm-project-status`, `pm-standup`, `pm-epic-writing`, `pm-constitution-sync` |
| developer | `dev-planning`, `dev-feature-plan`, `dev-brainstorm`, `dev-zoom-out`, `dev-karpathy`, `dev-tdd`, `dev-prototype`, `dev-improve-arch`, `dev-multi-agent`, `dev-github-hygiene`, `dev-diagnose`, `dev-grill`, `dev-qa-delegation`, `dev-handoff` |
| qa | `qa-triage`, `qa-best-practices`, `qa-planning`, `qa-documentation` |
| devops | `devops-ops`, `devops-setup-pre-commit`, `devops-cicd`, `devops-git-guardrails` |

### GTM Team
| Agent | Skills (`.claude/skills/`) |
|-------|---------------------------|
| writer | `writer-seo-content`, `marketing-strategist` |
| designer | `designer-design-system`, `designer-ui-ux`, `designer-style-to-photo`, `designer-image-generation` |
| web-publisher | `web-publisher-publish` |
| email-marketer | `email-marketer-nurture` |

## Updating Agent Templates

1. Edit `.claude/agents/*.md` or `.claude/skills/*/SKILL.md` — these are canonical
2. Commit and push to `main` — CI rebuilds zips automatically and publishes a GitHub Release
3. Run `/infiniteleverage-patch` on any client machine to pull the latest

```bash
# Manual rebuild (local only — CI handles releases):
./scripts/rebuild-zips.sh
# Output: setup-skills/infiniteleverage-{init,patch,project,validate}.zip
```

## Releases

Pre-built zips are auto-published to [GitHub Releases](https://github.com/talentedgeai/infiniteleverage-8-agents-template/releases) by CI on every push to `main` that touches agents or skills.

Clients update by running `/infiniteleverage-patch` in Claude Code — no manual zip upload needed.

## Template Format

Each agent `.md` follows:
- YAML frontmatter: `name`, `description`
- Role definition
- Workflow / work loop
- Skill dependencies

Templates are project-agnostic. Project-specific context lives in per-project repos.
