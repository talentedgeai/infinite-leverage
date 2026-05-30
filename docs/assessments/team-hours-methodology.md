---
name: pm-team-hours
description: >-
  Compute defensible per-author engineering hours, Claude token usage, and
  delivery metrics over a time window, then publish them in the Team
  Contributions section + Pulse chart of project-status.html. Three
  independent hour bases (strict git-hours, commit-span, Claude JSONL) are
  resolved per-day by best-evidence max. Token aggregation reads the same
  JSONL files. Chart design follows the small-multiples convention — never
  share a Y-axis across metrics with different units. Use this skill when
  updating project-status.html, writing a retro / weekly report, or
  answering "how many hours did <person> work this week". Never invent
  numbers — always state the basis.
---

# PM — Team Hours Methodology

The product-manager agent owns the **Team Contributions** section of
`docs/project-status.html`. Every hours figure published there must cite a
named basis from this doc. No free-form estimation.

The companion script is **`scripts/team-hours.py`** — single-file Python,
stdlib only, runs anywhere git + Python 3.11+ is installed.

---

## 1 — Why three bases

Every single-basis hours estimate has a known failure mode. Publishing one
number without naming the basis hides the failure mode and produces
arguments later when reality diverges.

| Basis | What it measures | Failure mode |
|---|---|---|
| **git-hours (strict)** | Continuous commit activity, capped at a 2h gap | Collapses long supervision stretches to a single 0.5h "session start" credit. Massively under-counts sub-agent / multi-tab workflows. |
| **commit-span** | Wall-clock span between first and last commit of each working day | Zero on days with no commits, even if the author worked all day. Common for operators who run sub-agents and ship work under another name. |
| **claude-jsonl** | 5-minute-gap activity in `~/.claude/projects/*<keyword>*` JSONL transcripts | Misses IDE-only / offline / Slack / GitHub-review time. Bound to a single machine — can only be attributed to whoever ran the script. |

The three together cover the failure modes of each individually.

---

## 2 — Formulas

### 2.1 git-hours (strict)

Standard open-source heuristic. Same formula used in `git-hours`,
`git-quick-stats`, GitHub's REST commit-activity API.

```
times = sorted(git_commit_timestamps_for_author)
total = SESSION_START_CREDIT
for prev, curr in pairs(times):
  gap = curr - prev
  total += gap if gap < MAX_GAP else SESSION_START_CREDIT
hours = total / 1h
```

**Knobs.** `MAX_GAP = 2h`, `SESSION_START_CREDIT = 30 min`.

### 2.2 commit-span

Same-day span from first commit to last commit, plus one start credit per
working day. No within-day cap.

```
by_day = group(times, key=date)
hours = 0
for day, lst in by_day:
  span = max(lst) - min(lst)
  hours += span + SESSION_START_CREDIT
```

**Knobs.** `SESSION_START_CREDIT = 30 min`.

### 2.3 claude-jsonl

Reads every `*.jsonl` under `~/.claude/projects/*<keyword>*/`, extracts each
record's `timestamp` (or `created_at`, or `time`) field, filters to the
window, applies a 5-minute-gap session definition, credits one start per
session.

```
events = sorted(timestamps in ~/.claude/projects/*<keyword>*/**.jsonl
                 where start <= ts < end)
by_day = group(events, key=date)
for day, lst in by_day:
  sessions = 1
  active = 0
  sess_start = last = lst[0]
  for t in lst[1:]:
    if t - last <= 5 min:
      last = t
    else:
      active += last - sess_start
      sessions += 1
      sess_start = last = t
  active += last - sess_start
  hours_day = active + sessions * SESSION_START_CREDIT
```

**Knobs.** `JSONL_GAP = 5 min`, `SESSION_START_CREDIT = 30 min`.

### 2.4 Token accounting (operator total, not per-author)

Same scan, different field. Each JSONL record may carry a `usage` block:

```
usage = obj.message.usage || obj.usage    # both shapes exist in the wild
input          = usage.input_tokens
output         = usage.output_tokens
cache_creation = usage.cache_creation_input_tokens
cache_read     = usage.cache_read_input_tokens

billed[day] = input + output + cache_creation      # what Anthropic charges
total[day]  = billed[day] + cache_read             # full token volume processed
```

**Gotcha — directory-set dedup.** A single Claude project directory often
matches multiple `--jsonl-keyword` globs (e.g. `*longev*` and `*wha*` both
match `-Applications-E8-client-work-healthy-james-prj-longevity-coach-wha`).
The script de-duplicates with `set()` before walking. **If you write a one-off
shell loop instead of using `scripts/team-hours.py --with-tokens`, you will
double-count.** The cumulative `88 M billed / 1.34 B total` figure in the
project-status.html hero was computed by an earlier ad-hoc script that did
not dedup — treat it as a 2× upper bound until re-audited.

**Why operator-total, not per-author.** Tokens are billed to whichever
Anthropic account ran Claude. JSONL records do not carry an author identity
in the per-event payload, so we cannot split. Document this in the table
caption. If two authors share an Anthropic account, attribution requires an
out-of-band record (a Slack message, a working agreement) — not the JSONL.

### 2.5 Resolution (per-day best-evidence)

For each calendar day in the window:

```
resolved[day] = max(commit_span[day], claude_jsonl[day])
source[day]   = "commit-span" if commit_span >= jsonl else "claude-jsonl"
total = sum(resolved[day] for day in window)
```

**Why max-not-sum.** The two bases overlap heavily on commit days (you can't
commit without keyboard activity, and most keyboard activity in the JSONL
window also produced commits). Summing would double-count. `max` picks
whichever basis had stronger evidence that day.

**Why not include git-hours (strict) in the max.** It's a worse instrument
than commit-span — strictly dominated by commit-span on any day with
≥ 2 commits. Kept in the report for backward-compatibility with the
cumulative `project-status.html` table only.

---

## 3 — Known limitations (document, don't hide)

1. **Per-author JSONL attribution is impossible from one machine.** The
   JSONL transcripts live under the operator's `~/.claude/projects/`.
   Running the script on author A's machine attributes 0h to author B even
   if B worked just as hard. If you publish a JSONL figure for an author
   other than the one whose machine you ran the script on, you are wrong.
   The script's CLI does not even try — it just emits the same JSONL number
   for every author. Footnote it in the table.

2. **Offline work is invisible to all three bases.** Reading code in an
   editor with no LSP, paper-and-pen architecture sketches, Slack DMs,
   reviewing a PR on GitHub web — none of this leaves a timestamp the script
   can find. The resolved number is a floor, not a ceiling.

3. **Batched commits collapse spans.** If an author commits ten times at
   the same instant (e.g. a worktree-consolidation batch), the
   commit-span for that day is whatever the *other* commits on that day
   span — possibly zero. Claude-jsonl catches this; git-only methods do not.

4. **Squash-merges hide the true author.** A PR squash-merged under author X
   may contain commits originally authored by Y on the underlying branch.
   The script reads `--author` against the post-squash log, so Y gets zero
   credit. If a sub-agent or pair-programmer's work was merged this way,
   note it in the row.

5. **All three bases credit a flat 30 min per session start.** This is the
   `git-hours` convention. It's a guess at pre-work setup time. It is not
   measured.

---

## 4 — Usage

### 4.1 Update the Team Contributions section of project-status.html

```bash
python3 scripts/team-hours.py \
  --start 2026-05-25 --end 2026-05-29 \
  --author "TracNg99" --author "James Murray" \
  --jsonl-keyword longev --jsonl-keyword wha \
  --tz +07:00 \
  --repo .
```

Output is a Markdown table you can paste into `project-status.html` after
re-styling. Always include:

- Which basis was chosen per author (column `source` rolls up to the row).
- The two losing-basis numbers as parentheticals or in a footnote, so a
  reader can see what was traded off.
- Limitation 1 disclosed in the caveat paragraph if any JSONL figure
  appears for an author other than the script-runner.

### 4.2 Single-author one-off

```bash
python3 scripts/team-hours.py --start 2026-05-25 --end 2026-05-29 \
  --author "TracNg99" --jsonl-keyword longev --tz +07:00
```

### 4.3 Machine-readable for downstream automation

```bash
python3 scripts/team-hours.py ... --json > out.json
```

Schema: `{ window: {start, end}, authors: { name: { commits, git_hours_strict,
commit_span_total, jsonl_total, resolved_total, per_day: { date: {...} } } } }`

### 4.4 Skip JSONL when running on someone else's machine

```bash
python3 scripts/team-hours.py ... --no-jsonl
```

Resolved hours fall back to commit-span alone. Note the limitation in the
publication.

---

## 5 — Editorial rules for the product-manager agent

1. **Never publish an hours figure without naming the basis.** Either inline
   ("Trac: 34.8h, Claude-JSONL 5-min-gap") or via footnote marker (†, ‡).
2. **Never sum across bases.** Cumulative table uses `git-hours (strict)`;
   per-window table uses `resolved`. They are not additive.
3. **When two adjacent rows use different bases, footnote both.** Mixed
   bases in one table are fine as long as each row says which.
4. **If the operator says "I worked X hours" and X >> resolved**, do not
   silently update to X. Reply with the per-day breakdown, ask which days
   are off, and offer Limitation 2 (offline work) as the most likely cause.
   Only override after explicit confirmation, and tag the cell with
   `(self-reported)`.
5. **If two authors collaborated and one shipped under the other's name**
   (squash-merge, pair programming), call it out in the Notes column. Do
   not redistribute hours — just disclose.
6. **The cumulative table in project-status.html does NOT get retroactively
   recomputed each week.** Append a new window-slice table beneath it.
7. **In published tables and hero stat tiles, label hours as "human tokens",
   not "hours" or "dev hours".** This is intentional parallelism with
   *Claude tokens* — both are engineering-effort budgets, and the parallel
   wording makes the trade-off visible at a glance ("we spent X human
   tokens and Y Claude tokens to ship Z"). The underlying *unit is still
   hours* and the methodology / column tooltips must say so — only the
   user-facing label changes. Internal CS terms (`git-hours`,
   `time-between-commits`, etc.) keep their original names — they are
   method names, not measurements.
8. **Roll up contributors into Owner vs Development team for headline
   tables.** The published contributors section in `project-status.html`
   shows exactly two rows per window: `Owner` (the project's founder /
   accountable lead, named in a sub-line) and `Development team` (every
   other human + automated contributor, identities listed in a sub-line).
   This separation reflects the *accountability* split, not the volume
   split — Owner is the person who carries clinical / regulatory /
   business risk for the work; Development team is everyone else
   contributing under the Owner's direction. The complete-window and
   last-one-week tables both use this shape. Columns: Commits · PRs
   merged · Human tokens · Window. Drop diff size (+/− lines, files)
   and per-author breakouts from the headline tables — those live in
   commit history and PR descriptions, not on the status page. The
   Owner identity is project-specific; adapt for the project being
   reported on (see §6).

---

## 5.5 — Publishing the Pulse chart (single line chart, peak-normalised)

> **Convention set by the operator (2026-05-30):** the Pulse section uses **one
> combined line chart with every metric plotted as a coloured line on the
> same axes**. This rule overrides the data-analyst default of small
> multiples. The operator wants a single trajectory view at a glance,
> accepting the trade-offs documented below.

### The shape

One SVG. X-axis is calendar date across the window. Y-axis is **percent of
each series' own window peak (0 → 100 %)** — every series is normalised
independently so they can share the same Y-axis. Each metric is a
different-coloured line with circles at each data point. A legend below
the chart names each line, gives its colour, **and prints the actual peak
value with its real unit** so the absolute scale is recoverable.

```
y[series][day] = 100 * raw[series][day] / max(raw[series] over window)
```

That is a per-series **min-max-to-peak** normalisation, not Day-1-indexed.
A series that hits its peak on day 1 stays at 100 the whole window; a
series with a single late spike sits near 0 until the spike. This matches
the operator's mental model: *"which days were the high-water mark for
each thing"*.

### Why this trades off against analyst best practice

Three things the dashboard reader **cannot** do with this chart, and which
the operator has accepted:

1. **Compare absolute magnitudes between series.** Two lines at 80 % do not
   mean equal effort — one might be 80 % of 20 M tokens, the other 80 % of
   2 PRs. The legend's peak value is the only way back to truth. Mitigation:
   always print peak + window total in the legend, never just the colour.

2. **See sub-peak detail on a flat series.** Anything that didn't move in
   the window (e.g. epics-complete steady at 13 / 14) becomes a dead
   horizontal line at 100 %. Mitigation: dash the line style + label it
   "flat at <value>" in the legend.

3. **Read changes when peak changes week-over-week.** A line that was at
   100 % last week and 100 % this week may have moved 5× in absolute terms,
   or not moved at all — the chart can't tell you. Mitigation: write the
   week-over-week absolute deltas into the reading-guide paragraph below
   the chart, not into the chart itself.

The classic small-multiples pattern (one panel per metric, each with its
own Y-scale and unit) avoids all three. It is preserved in this doc's
**Appendix A** below for any future operator who wants to revert. The
current default is the combined chart.

### Series for project-status.html

| # | Metric | Colour token | Line style | Source |
|---|---|---|---|---|
| 1 | Claude tokens billed (M / day) | `--lc-primary` #2F6F8F | solid | `scripts/team-hours.py --with-tokens` |
| 2 | Team hours resolved (h / day) | `--lc-teal` #4A9A95 | solid | resolved hours (§2.5), sum across authors |
| 3 | Commits to `main` (count / day) | `--lc-accent` #F28C38 | solid | `git log --no-merges` |
| 4 | PRs merged to `main` (count / day) | `--lc-success` #3F8A5C | solid | `gh pr list --base main --state merged --search "merged:<start>..<end>"` |
| 5 | Epics ≥ 95 % complete (cumulative / N) | `--lc-plum` #6B5B8E | **dashed** (signals flat / structural series) | `docs/product/epic-status.md` |
| 6 | Revenue · MRR · engagement | `--lc-grey-soft` #B9C3CB | listed in legend as "pending" — no line drawn | Stripe Sigma + Plausible (not yet wired) |

**Colour budget — max 6 series** on one chart, including pending. Past
that, the human eye can't distinguish line colours reliably and the chart
needs to split into two stacked charts (delivery + engagement) or fall
back to small multiples.

**Inline SVG, no JS.** `project-status.html` stays a single-file dashboard.
The chart is hand-authored SVG. The script emits JSON (`--json`) for any
future tooling that wants to consume the same data.

### Editorial rules for the Pulse section (single-chart convention)

1. **Every series is normalised to its own window peak**, never to a
   shared scale. Do not try to keep raw units on the Y-axis.
2. **Every series in the legend prints its peak value + unit + window
   total.** No colour-only legend entries.
3. **Solid line for series that moved in the window. Dashed line for series
   that were flat or structural** (e.g. cumulative epic count with no new
   ships). This is the only line-style channel the chart uses.
4. **Mark every data point with a circle**, with a slightly larger circle
   on the peak day (radius 4.5 vs 3.5). The reader's eye lands on the
   peak first.
5. **Gridlines at 0 / 25 / 50 / 75 / 100 %, labelled in the Y-axis gutter.**
   These are the only Y-axis ticks — there is no second axis.
6. **Day labels on the X-axis show date + weekday** (e.g. "28 May / Tue").
   Five days at most per chart — past five the lines get crowded; past
   ten use a wider chart or switch to weekly cadence.
7. **Pending series stay in the legend as muted / italic entries**, no line
   drawn. Removing them altogether tells the reader the metric isn't planned,
   which is false.
8. **A "reading guide" paragraph beneath the chart converts the most
   important percent back to absolute units in one sentence** — e.g.
   "Team hours hit peak 23.7 h on 5/29 (a 2.2× increase over the 5/26
   trough at 7.1 h)." Never make the reader do the multiplication.
9. **Never add a second Y-axis** ("for revenue in $") — if a series breaks
   the chart, split the chart.

### Future metrics — what to wire next

| Source | Metrics it would unlock |
|---|---|
| **Stripe Sigma** snapshot (weekly) | MRR, new-MRR, churn $, ARPU, active subscriptions by tier |
| **Plausible** / privacy-first analytics | Sessions, signups, onboarding-completion rate, dashboard daily-active rate |
| **Resend** event log | Welcome-email delivery rate, weekly-check-in open rate, click-through to dashboard |
| **Supabase `consent_records`** | Consent capture rate per signup cohort (an AHPRA-relevant trust indicator) |
| **`patient_uploads` table** | Upload velocity per active member (an engagement signal that doesn't require analytics) |

Each new metric **must arrive as one normalised line on the existing
chart**, not as a new panel. If adding the 7th series, **drop one first** —
do not exceed the colour budget.

### Appendix A — Small-multiples alternative (deprecated default)

Kept here for any future operator who wants to revert to the analyst
default:

> Dashboard requests usually arrive worded as "put all the metrics on one
> chart over time." That request hides three traps: (1) different units
> cannot share a Y-axis; (2) dual / triple Y-axes mislead — the relative
> scale between them is set by the author, not by the data; (3)
> normalised / indexed lines lose absolute scale and make week-over-week
> comparison meaningless when peaks shift.
>
> Small multiples — a panel grid where every panel has its own Y-scale and
> unit label, all sharing one X-axis — solves all three. Tufte (1983,
> 1990) made the case; the FT chart team operationalised it; D3 and
> Vega-Lite both ship `facet` primitives for this reason.
>
> To revert: swap the single-SVG `figure.ps-pulse-chart` for a
> `div.ps-pulse-grid` of `figure.ps-pulse-panel` elements (one per metric).
> Restore the CSS block tagged `============ PULSE / SMALL-MULTIPLES CHART
> ============` from git history (commit before 2026-05-30 evening edit).

---

## 6 — Adapting to a new project

To reuse this skill in another codebase:

1. Copy `scripts/team-hours.py` into the new repo's `scripts/`.
2. Copy this file into the new repo's `docs/engineering/`.
3. Adjust the `--jsonl-keyword` flag to match how the new project appears in
   the operator's `~/.claude/projects/` directory names.
4. Adjust `--tz` to the team's local timezone.
5. No code changes needed in the script.

---

## 7 — File map

| Path | Purpose |
|---|---|
| `scripts/team-hours.py` | The single-file Python script. stdlib-only. CLI + `--json` output. Supports `--with-tokens` for §2.4. |
| `docs/engineering/team-hours-methodology.md` | This document. Source of truth for the formulas, editorial rules, and chart-design pattern. |
| `docs/project-status.html` | Where the published numbers live. Sections: `#pulse` (chart) and `#contributors` (table). |

---

## 8 — Provenance

This methodology was extracted from the 2026-05-30 update to
`docs/project-status.html` after the operator flagged that the strict
`git-hours` heuristic was reporting ~5h for a week of ~40h supervised
sub-agent work. The three-basis design and per-day max resolution were
chosen to make each failure mode visible rather than averaged-away.

The §2.4 token-accounting + §5.5 chart pattern were added in the same
session after the operator asked for a multi-metric trajectory view.
During implementation we caught a real double-counting bug in an ad-hoc
shell script (overlapping `*longev*` and `*wha*` globs visited the same
JSONL files twice), which is the reason §2.4's "directory-set dedup"
warning is the first paragraph: don't bypass the script.

§5.5 originally specified small multiples (analyst default) but was flipped
to a single peak-normalised line chart later that same evening when the
operator reported the panel grid was breaking the page layout and asked
for a single chart with all metrics colour-coded. The small-multiples
spec is preserved as Appendix A in §5.5 for future reversion.
