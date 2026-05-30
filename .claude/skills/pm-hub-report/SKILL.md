---
name: pm-hub-report
description: >-
  Adaptive cross-project hub skill. Explores what centralized dashboard
  pattern the user already has, expands upon it, or creates ~/.claude/hub/hub.html
  as the canonical fallback. Aggregates contribution-snapshot.json from every
  project under ~/code-projects/ into one cross-project view showing per-project
  human tokens, Claude tokens billed, commits, and PRs. Additive — never
  overwrites existing hub structure.
---

# PM — Hub Report (Cross-Project Dashboard)

This skill aggregates all per-project contribution snapshots into one
centralized view. It **explores what the operator already has** before
deciding where to write — never assumes a fixed location.

---

## Step 1 — Discover existing hub pattern

Search in this order — stop at the first match:

```bash
# 1. Explicit hub project
ls ~/code-projects/ | grep -iE 'hub|dashboard|central|reports'

# 2. Any project-level hub HTML
find ~/code-projects/ -name "hub.html" -o -name "dashboard.html" 2>/dev/null | head -5

# 3. Machine-level hub (previous pm-hub-report runs)
ls ~/.claude/hub/ 2>/dev/null

# 4. Any standalone HTML in ~
find ~ -maxdepth 2 -name "*hub*" -o -name "*dashboard*" 2>/dev/null | head -5
```

**Pattern resolution:**

| What you find | Action |
|---|---|
| A project named `*hub*` or `*dashboard*` with an `index.html` or `hub.html` | Expand that file in place — keep all existing sections, add/update the Contributions section |
| A project named `*hub*` with a `docs/` folder but no hub HTML | Create `docs/hub.html` inside it using the schema below |
| A standalone `hub.html` anywhere under `~/code-projects/` | Update it in place |
| `~/.claude/hub/hub.html` exists | Update it in place |
| Nothing found | Create `~/.claude/hub/hub.html` using the schema below |

**Never delete, replace, or restructure an existing hub file.** Only add or update the `#contributions` section.

---

## Step 2 — Collect contribution snapshots

```bash
find ~/code-projects/ -name "contribution-snapshot.json" 2>/dev/null
```

Read each snapshot. For snapshots older than 25 hours, note them as stale (don't skip — stale data is better than no data, but flag it in the UI).

---

## Step 3 — Build the contributions section

Produce an HTML section with id `contributions` (or update it if it already exists).

### Headline summary bar

4 tiles:
- **Total human tokens** — sum of all resolved_total across all projects and authors
- **Total Claude tokens billed** — sum of tokens_window.billed / 1_000_000 across all projects  
- **Active projects** — count with at least 1 commit in the window
- **Window** — the date range (use the most recent snapshot's window)

### Per-project table

| Project | Owner | Human tokens (h) | Claude tokens (M billed) | Commits | PRs | Last synced | Link |
|---|---|---|---|---|---|---|---|

- **Owner** — from snapshot (highest resolved_total author, or explicit name from CLAUDE.md)
- **Human tokens** — resolved_total for Owner row + Development team row summed
- **Claude tokens** — tokens_window.billed / 1_000_000 (operator total, not per-author)
- **Link** — relative path to `~/code-projects/<slug>/docs/project-status.html`
- Sort by Human tokens descending

Label hours as **"Human tokens"** (methodology editorial rule 7 — intentional parallel with Claude tokens).

### Cross-project Pulse chart

One combined normalised line chart (same convention as per-project §5.5):
- One line per **project** (not per metric — this is the cross-project view)
- Y-axis: 0–100 % of each project's own peak human tokens in the window
- X-axis: calendar dates (shared across all projects)
- Each project gets a distinct colour (cycle through the §5.5 colour tokens)
- Legend: project name + peak value + window total
- Max 8 projects on one chart; past 8, show top 8 by total human tokens and note "N more projects"
- Reading-guide paragraph: "Most active project: X with Y h on date Z"

### Footnotes

```
† Human tokens = engineering hours measured by best-evidence max of commit-span and 
  Claude JSONL activity (methodology: docs/assessments/team-hours-methodology.md).
‡ Claude tokens reflect the operator's Anthropic account — not per-author.
  JSONL attribution is single-machine only (Limitation 1 of the methodology).
```

---

## Step 4 — Write / update the hub file

If updating an existing file:
- Find the `<section id="contributions">` block (or `<!-- HUB-CONTRIBUTIONS-START -->` marker)
- Replace only that block — leave all other content intact
- If no marker exists, append the section before `</body>`

If creating `~/.claude/hub/hub.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Operator Hub — Cross-Project Dashboard</title>
  <style>
    :root {
      --primary: #2563EB; --accent: #F97316;
      --bg: #0B1426; --surface: #1E293B;
      --text: #F1F5F9; --text-muted: #94A3B8;
      --success: #22C55E; --warning: #F59E0B; --danger: #EF4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; padding: 2rem; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .subtitle { color: var(--text-muted); margin-bottom: 2rem; }
    .tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
    .tile { background: var(--surface); border-radius: 8px; padding: 1.25rem; }
    .tile-value { font-size: 2rem; font-weight: 700; color: var(--primary); }
    .tile-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 2rem; }
    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #2d3748; }
    th { color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; }
    a { color: var(--primary); text-decoration: none; }
    .stale { color: var(--warning); font-size: 0.75rem; }
    .footnotes { color: var(--text-muted); font-size: 0.75rem; margin-top: 2rem; line-height: 1.6; }
    figure { margin-bottom: 2rem; }
    figcaption { color: var(--text-muted); font-size: 0.8rem; margin-top: 0.5rem; }
  </style>
</head>
<body>
  <h1>Operator Hub</h1>
  <p class="subtitle">Cross-project contribution dashboard — updated by pm-hub-report</p>
  <!-- HUB-CONTRIBUTIONS-START -->
  <!-- HUB-CONTRIBUTIONS-END -->
</body>
</html>
```

---

## Step 5 — Print summary

```
✅ Hub updated: <path to hub file>
Projects aggregated: N (M stale)
Total human tokens this window: X h
Total Claude tokens billed this window: Y M
```

Open the file path for the operator so they can review it.
