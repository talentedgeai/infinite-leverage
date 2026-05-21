---
name: pm-project-status
description: >-
  Builds and updates the project status dashboard — a single HTML page showing which features are planned, in progress, and shipped. Includes a build log, key metrics, and links to all important docs. The operator uses this to understand where the project stands at a glance.
---

# PM: Project Status Dashboard

Maintain `docs/project-status.html`. Single HTML file, no external CSS/JS dependencies. If file exists, update it — never create from scratch.

## Sections (in order)

### 1. Hero
- Headline + prose sub (last updated date, current state in plain English, open bug count)
- 4 stat tiles: epics count, avg estimate %, open bugs, phases in flight

### 2. Epic Summary Table
One row per epic:
| # | Name | Pipeline (5 dots) | Estimate % | Depends on | Open bugs |

Pipeline uses 5 dots: Specified ●/○ → In flight ●/○ → Feature-complete ●/○ → Tested ●/○ → Shipped ●/○

### 3. Epic Detail Grid
2-column card grid. Each card:
- Epic number, title, thesis (one-liner)
- Status pill, % done bar
- Meta row: what's done / what's missing / success criterion / open bugs
- Deep-link to epic-status.md

### 4. Build Log
Recent commits to main, grouped by date, newest first. Omit PM/standup commits.

### 5. Companion Docs
Grid of links to all docs/product/ files.

## Theming
Use CSS variables:
```css
:root {
  --primary: #2563EB;
  --accent: #F97316;
  --bg: #0B1426;
  --surface: #1E293B;
  --text: #F1F5F9;
  --text-muted: #94A3B8;
  --success: #22C55E;
  --warning: #F59E0B;
  --danger: #EF4444;
}
```
Serif headlines, system sans-serif body, no inline styles.

## Design Note
Use the project default design system above. If the client defines their own design system in `docs/brand/style-guide.md`, update the CSS variables to match — but maintain the same section structure and layout.
