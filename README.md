# Infinite Leverage — 8-Agent Templates

Universal agent definition templates for the Infinite Leverage bootstrap system. These 8 files are the canonical agent definitions bundled into `infiniteleverage-init`, `infiniteleverage-onboard`, and `infiniteleverage-patch` skills.

## The 8 Agents

### Build Team
| Agent | Role |
|-------|------|
| product-manager.md | OKRs, epics, standups, RAG status |
| developer.md | Code to project standards, TDD |
| qa.md | Testing pyramid — knows what AI can and cannot test |
| devops.md | Git, CI/CD, Vercel operations |

### GTM Team
| Agent | Role |
|-------|------|
| writer.md | One blog post per run, owner's voice |
| designer.md | One hero image per run, Gemini |
| web-publisher.md | Publishes post, stages git commit |
| email-marketer.md | Subscriber nurture via Resend |

## Usage

These templates are bundled directly into each bootstrap skill. To update:

```bash
# Copy updated templates into each skill
cp agents/*.md path/to/infiniteleverage-init/agents/
cp agents/*.md path/to/infiniteleverage-onboard/agents/
cp agents/*.md path/to/infiniteleverage-patch/agents/

# Rebuild zips
cd path/to/skills && zip -r infiniteleverage-init.zip infiniteleverage-init/
```

## Template Format

Each `.md` file contains:

- YAML frontmatter: `name`, `description`
- Role definition
- Workflow / work loop
- References to the skills the agent depends on

Templates are project-agnostic. Project-specific context lives in the project repo (personas, style guides), not in these templates.
