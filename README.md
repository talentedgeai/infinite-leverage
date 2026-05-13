# Infinite Leverage — 8-Agent Templates

Universal agent definition templates and bootstrap skills for the Infinite Leverage system.

## Repo Structure

```
.claude/                       ← Claude Code convention layout
├── agents/                    ← Canonical 8-agent templates (single source of truth)
│   ├── product-manager.md
│   ├── developer.md
│   ├── qa.md
│   ├── devops.md
│   ├── writer.md
│   ├── designer.md
│   ├── web-publisher.md
│   └── email-marketer.md
├── skills/                    ← Dedicated per-agent skills (each agent's workflow)
│   ├── pm/                   ← Client interview, documentation, standup, epic writing
│   ├── dev/                  ← Planning, multi-agent, Karpathy, GitHub hygiene, QA delegation
│   ├── qa/                   ← Best practices, planning, documentation
│   ├── designer/             ← Design system, UI/UX, style-to-photo, image generation
│   ├── writer/               ← SEO content, Neil Patel critique
│   ├── devops/               ← CI/CD, Vercel ops, escalation
│   ├── web-publisher/        ← Markdown→component publishing pipeline
│   └── email-marketer/       ← Resend sequences, subscriber nurture
└── rules/
    └── global-engineering.md  ← Shared engineering guardrails

skills/                        ← Bootstrap skills (outside .claude, for release zips)
├── infiniteleverage-init/     ← Full Mac Mini setup
│   ├── SKILL.md
│   ├── agents/                ← Bundled copy (synced from .claude/agents/)
│   ├── references/
│   └── scripts/
├── infiniteleverage-onboard/  ← Client laptop setup
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
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
| Agent | Dedicated Skill (.claude/skills/) | Covers |
|-------|----------------------------------|--------|
| product-manager | `pm/` | Client interview, 4-file documentation, project-status dashboard, standup set, Dan Shipper epic writing |
| developer | `dev/` | Plan from project-status, multi-agent delegation, Karpathy principles, GitHub hygiene, QA delegation |
| qa | `qa/` | Test pyramid best practices, Dan Shipper QA planning, docs/qa + dashboard reporting |
| devops | `devops/` | Vercel/GitHub CI/CD monitoring, deployment model, escalation triggers |

### GTM Team
| Agent | Dedicated Skill (.claude/skills/) | Covers |
|-------|----------------------------------|--------|
| writer | `writer/` | SEO-optimized content, Neil Patel self-critique, brief-driven workflow |
| designer | `designer/` | 5-preset design system, UI/UX best practices, style-to-photo alignment, image generation |
| web-publisher | `web-publisher/` | Markdown-to-component pipeline, blog index update, quality checklist |
| email-marketer | `email-marketer/` | Resend sequences, welcome flow, weekly digest, subscriber lifecycle |

## Updating Agent Templates

1. Edit `.claude/agents/*.md` — these are canonical
2. Run `./scripts/rebuild-zips.sh` — syncs to skill bundles and rebuilds zips
3. Upload new zips to GitHub Releases for deployment

```bash
# One-command update:
./scripts/rebuild-zips.sh
# Output: skills/infiniteleverage-{init,onboard,patch}.zip
```

## Releases

Pre-built zips are published to [GitHub Releases](https://github.com/talentedgeai/infiniteleverage-8-agents-template/releases).
Import these into your Claude Team account or deploy to RemoteTrigger schedules.

## Template Format

Each agent `.md` follows:
- YAML frontmatter: `name`, `description`
- Role definition
- Workflow / work loop
- Skill dependencies

Templates are project-agnostic. Project-specific context lives in per-project repos.
