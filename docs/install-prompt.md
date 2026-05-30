# One-Step Install / Update Prompt

Copy and paste this entire prompt into a **new Claude Code session** (any project directory is fine).
It is safe to run on a machine that is already set up — it is additive and respects existing config.

---

```
Run infiniteleverage-patch to sync my local machine with the latest Infinite Leverage template.

Specific instructions for this run:

1. Follow the full patch skill exactly (Phase 1 health-check → Phase 2 diff + apply → Phase 3 version stamp).

2. Additive-only rules — honour these throughout:
   - MERGE config files (settings.local.json, CLAUDE.md, global-engineering.md): add what is missing, never remove or overwrite existing content unless you confirm it is an exact previous-version duplicate of the template.
   - SKIP removals: use the "no-remove" apply mode so no existing agent or skill is deleted even if it no longer appears in the template.
   - For any conflict between my current local value and the incoming template value: show me both in plain language (no JSON keys), tell me what each one does, and ask me to choose before touching the file.

3. After syncing agents and skills, also:
   a. Sync scheduled tasks from the template (cp -R to ~/.claude/scheduled-tasks/).
   b. Deploy team-hours.py to every ~/code-projects/*/scripts/ directory that has a CLAUDE.md (mkdir -p scripts/ first; only overwrite if template version is newer).
   c. Append "scripts/contribution-snapshot.json" to .gitignore in each project that does not already have it.
   d. Install / re-install all hooks from the template (run install-hooks.sh against the freshly cloned template). Do not skip this even if hooks appear to already exist — the script is idempotent.

4. After the patch is fully applied, register the pm-weekly-contribution scheduled task if it is not already registered:
   - Cron: "30 7 * * 1" (Mondays 7:30 AM local time)
   - Prompt: run pm-contribution-sync then pm-hub-report for the prior week's window

5. Stamp the installed version and ensure the plugin is registered (claude plugin marketplace add talentedgeai/infiniteleverage-plugin).

6. Print a final summary:
   - Agents: N added / N updated / N unchanged
   - Skills: N added / N updated / N unchanged
   - team-hours.py deployed to: [list of project paths]
   - Hooks installed: [list]
   - Scheduled task pm-weekly-contribution: registered / already running
   - Any items that needed my input and how they were resolved
```
