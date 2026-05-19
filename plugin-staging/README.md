# infiniteleverage-plugin

> **Staging area** — extract this directory into its own repo (`infiniteleverage-plugin`) before publishing.

Claude Desktop Team plugin for the Infinite Leverage 8-agent system.

## Extract to standalone repo

```bash
cp -r plugin-staging/ /path/to/infiniteleverage-plugin
cd /path/to/infiniteleverage-plugin
git init && git checkout -b main

# Populate skills/ from the template repo's setup-skills/
cp -r /path/to/infiniteleverage-8-agents-template/setup-skills/infiniteleverage-init skills/
cp -r /path/to/infiniteleverage-8-agents-template/setup-skills/infiniteleverage-onboard skills/
cp -r /path/to/infiniteleverage-8-agents-template/setup-skills/infiniteleverage-patch skills/
cp -r /path/to/infiniteleverage-8-agents-template/setup-skills/infiniteleverage-project skills/

git add . && git commit -m "init: infiniteleverage-plugin"
gh repo create talentedgeai/infiniteleverage-plugin --public --source=. --remote=origin --push
```

## Hook files

| File | Purpose |
|---|---|
| `hooks/session-start` | 4-stage SessionStart hook (init check, version, routing, usage) |
| `hooks/usage-context.py` | Token usage briefing injected into Claude's context |
| `hooks/hooks.json` | Registers `session-start` as the SessionStart hook in settings.json |

## Sync with template repo

When `setup-skills/` in the template repo changes, rebuild the plugin's `skills/` directory by re-running the copy commands above and pushing a new plugin version.
