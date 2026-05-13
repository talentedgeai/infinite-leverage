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

## The 8 Agents

### Build Team
| Agent | Role |
|-------|------|
| product-manager | OKRs, epics, standups, RAG status |
| developer | Code to project standards, TDD |
| qa | Testing pyramid — knows what AI can and cannot test |
| devops | Git, CI/CD, Vercel operations |

### GTM Team
| Agent | Role |
|-------|------|
| writer | One blog post per run, owner's voice |
| designer | One hero image per run, Gemini |
| web-publisher | Publishes post, stages git commit |
| email-marketer | Subscriber nurture via Resend |

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
