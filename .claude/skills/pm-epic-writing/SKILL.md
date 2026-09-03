---
name: pm-epic-writing
description: >-
  Takes a new feature idea through the full discovery process — writes a structured spec, runs a business-level clarification interview, reviews the spec for gaps and conflicts, and turns it into a Dan Shipper epic the developer can build from with confidence. Self-contained: the whole spec pipeline (specify → clarify → analyze → epic) lives in this skill. Use when the operator says "write a new epic", "specify a feature", "add an epic for X", or after a client conversation produces a new idea. Output goes to .specify/features/{slug}/ and docs/product/epics.md.
---

# PM: Epic Writing — Full Discovery Workflow

Translates a client idea into a fully specified epic with a feature branch and a
dev handoff package. No client input is required after the initial idea and one
round of clarification questions.

Every epic must pass this test: *"If you read only the title and the problem
statement, you know exactly what bet we're making."*

## Inputs

- **Feature idea**: a sentence or paragraph from the client
- **Product context**: `docs/product/product.md` (required — read before Step 1)
- **Existing epics**: `docs/product/epics.md` (read before Step 5)

## Step 1 — Load product context

Read `docs/product/product.md` in full: the core problem, the target user, and
what the product is explicitly NOT building. If `docs/product/constitution.md`
exists, read it too — constitution violations are a hard gate later.

## Step 2 — Create the feature branch

Branch first, so the spec is born on it rather than carried across a checkout as an
untracked file. Derive `{slug}` from the idea if not given.

```bash
NEXT_NUM=$(git branch --list '[0-9][0-9][0-9]-*' | wc -l | tr -d ' ')
BRANCH_NAME="$(printf '%03d' $((NEXT_NUM + 1)))-{slug}"
git checkout -b "$BRANCH_NAME"
```

(If spec-kit's `.specify/extensions/git/scripts/bash/create-new-feature.sh` is present
it does the same thing — either is fine. The scaffold ships that directory empty.)

Create the branch **once per feature**. If there's no git repo, warn and
continue on the current branch — never block the workflow.

## Step 3 — Write the spec

Write `.specify/features/{slug}/spec.md`. The spec is **complete, unambiguous, verifiable, and
technology-agnostic** — outcomes, never implementation ("the system SHALL
present products in a sortable list", not "use React"). Treat the client's
words as *intent*, not spec text.

Sections, in order:

1. **Executive Summary** — 1–2 sentences; who benefits; business value
2. **Context & Problem Statement** — current state, the gap, constraints, dependencies
3. **Requirements** — **MUST** (blocking) / **SHOULD** (important) / **MAY**
   (optional), grouped by category (Functional, Performance, Security, UX,
   Accessibility, Integration…); each one a complete sentence
4. **Success Criteria** — measurable, technology-agnostic, user-focused,
   verifiable. Good: "95% of searches return results in under 1 second". Bad:
   "API response under 200ms", "Redis hit rate above 80%"
5. **Design/Approach (outline)** — high-level strategy, key decisions,
   integration points; no code-level detail
6. **Acceptance Criteria** — standalone testable conditions, one per
   requirement, happy path + key edge cases
7. **Open Questions** — ambiguities, pending decisions, risks
8. **Glossary** (only if needed)

Every section must be substantive — no placeholders. If the feature directory
already exists, load the current spec, show its version, and ask whether to
update it or create a variant.

## Step 4 — Clarify (business-level only)

**4a — Generate candidate questions.** From the spec's unclear, incomplete, or
risky sections, draft 5–10 strategic questions: scope gaps ("does 'user'
include guests?"), edge cases ("what happens when search returns nothing?"),
metrics ("what error rate is acceptable?"), assumptions ("is sub-second
response required?"), trade-offs ("if we can't hit everything, what matters
most?"). Never ask what the spec already answers.

**4b — Filter before the client sees anything.** The client cannot answer
technical questions. For each candidate:

- **KEEP** — user behaviour/journey, business goals and outcomes, scope,
  priority trade-offs, UX edge cases
- **REMOVE or REPHRASE** — API/schema design, database/storage/framework
  choice, performance in engineering units, architecture patterns, DevOps.
  If a technical question hides a business intent, rephrase it in
  user-outcome terms ("acceptable API response time?" → "do users expect
  results instantly, within a few seconds, or is a short wait fine?")

Cap at 5–8 questions. Never tell the client questions were filtered.

**Client not available live?** Answer each kept question from the material on hand
(`docs/product/product.md`, `docs/product/sources/*`, the brief). Where it is silent,
state a sensible default in the spec and list the question under **Open Questions** with
that default — do not block the workflow waiting for a reply.

**4c — Write answers back.** Tighten acceptance criteria, resolve ambiguities,
bump the spec version (semver), and append:

```
## Clarification Summary (Version X.Y.Z)
**Date**: YYYY-MM-DD
**Clarifications made**: …
**Open questions remaining**: …
```

## Step 5 — Analyze, then split findings by audience

**5a — Review the spec** with these passes, producing a findings table
`ID | Issue | Section | Severity | Remediation` (deterministic, actionable,
≤50 rows):

- **Duplication** — near-identical requirements/criteria
- **Ambiguity** — vague quantifiers ("fast", "reliable", "some"), conditionals
  without specifics ("if possible", "as needed")
- **Underspecification** — MUST requirements with no success criterion;
  metrics with no unit; acceptance criteria that aren't independently testable
- **Constitution alignment** — violations of `docs/product/constitution.md`
  principles, if it exists
- **Coverage gaps** — missing edge cases (empty/null/boundary/error states),
  missing cross-cutting concerns (accessibility, security, mobile)
- **Inconsistency** — criteria that don't validate their requirements;
  contradictory requirements

Severity: **HIGH** blocks implementation · **MEDIUM** slows it · **LOW** polish.

**5b — Split into two layers:**

- **PM layer (surface to client, business language only)**: goal conflicts
  with `product.md`, duplication with existing epics, unmeasurable success
  criteria, MUST requirements missing acceptance criteria, constitution
  misalignments, scope vagueness only the owner can resolve. Present as a
  clean table (`ID | Issue | Severity | What We Need From You`) with all
  jargon stripped. **Gate: every HIGH PM-layer finding must be resolved before
  Step 6** — amend the spec with the client's input and re-analyze until none
  remain. MEDIUM/LOW: note, offer, don't block. When the client cannot answer
  live, a HIGH finding that has a safe default is resolved by writing that default
  into the spec and listing the question under Open Questions (it becomes MEDIUM);
  a HIGH finding with no safe default stops here — report it to the operator.
- **Dev layer (never surface to client)**: missing data models, criteria
  requiring implementation knowledge, NFRs without technical constraints,
  ambiguous technical assumptions. Write to
  `.specify/features/{slug}/dev-findings.md` with the same table format —
  consumed by `dev-feature-plan` Phase 0.

## Step 6 — Write the epic entry

Read `docs/product/epics.md`; if an existing epic covers the same problem,
propose merging — never duplicate. The scaffold ships the file with its header,
the opening block ("These are thematic bundles of work…") and a trailing
`## Sequence argument` section. Insert the new entry **above** `## Sequence argument`,
after the last existing epic (create the file with that shape if it is missing):

```
## E{N} · {Epic Name}

**The problem:** {one sentence — the user frustration this addresses}
**The mechanism:** {one sentence — the causal chain to the outcome}
**What it bundles:**
- {feature 1}
- {feature 2}
**What success looks like:** {measurable — number + date or behaviour threshold}
**Why it goes first:** {dependency, risk reduction, or fastest learning}

_Spec: `.specify/features/{slug}/spec.md`_
```

Never use: Thesis, Hypothesis, Acceptance criteria, Definition of done,
Priority signal — those belong in task plans. Epic numbers are sequential.
Then rewrite the **Sequence argument** section (kept last in the file): one short
paragraph on why this order and not another — dependencies, risk reduction, or
learning velocity. With a single epic, one sentence on why it goes first.

## Step 7 — Update epic-status.md

The scaffold ships `docs/product/epic-status.md` with this shape (create it with
the same shape if it is missing):

- H1: `# {Project} · Epic Status · Last updated: {YYYY-MM-DD} · Phase in flight: {phase or —}`
- `## Pipeline stages` — 1 · Specified, 2 · In flight, 3 · Feature-complete, 4 · Tested, 5 · Shipped
- Status glyphs: `🔄 in flight · ✅ done · ⏳ partially done · ☐ planned · 🛑 paused`;
  pipeline column is five circles, `○` not reached / `●` reached
- `## At a glance` — table `Epic | Status | % done (est) | Pipeline | Open bugs | Closed bugs | Notes`
- `## Drilldown` — one `### E{N} · {Epic Name}` subsection per epic
- `## Obsolete / won't fix`

For the new epic: add the row
`| E{N} · {Epic Name} | ☐ planned | 0% | ●○○○○ | 0 | 0 | spec v{X.Y.Z} |`
(stage 1 is reached — the spec exists), add a Drilldown subsection holding the
spec path and dev-findings count (`pm-to-issues` adds issue numbers,
`pm-grill-with-docs` its verdict, `qa-triage` bug counts), and set
`Last updated` in the H1 to today. The epic identifier must match the H2 in
`epics.md` byte for byte — `pm-project-status` joins the two files on it.

## Step 8 — Hand off to the developer

```
EPIC WRITTEN — DEVELOPER HANDOFF
─────────────────────────────────
Epic    : E{N} · {Epic Name}
Branch  : {branch}
Spec    : .specify/features/{slug}/spec.md
Dev findings : .specify/features/{slug}/dev-findings.md ({n} findings, {n} HIGH)

TO START: invoke dev-feature-plan with the spec path — it resolves the dev
findings and produces impl-plan.md + tasks.md.

Nothing was committed. To record the spec and docs on the feature branch
(staging by name — never `git add .`):
  git add .specify/features/{slug} docs/product agents/product-manager/context/persona.md
  git commit -m "docs: E{N} {slug} — spec, dev findings, epic, product docs"
```

Print those commands every time. The developer inherits this branch; uncommitted PM
files there are how a literal reading of `global-engineering.md` ("stop and report if
there are uncommitted changes") blocks the next agent.

## Epic writing rules

- **One bet per epic** — one user problem; split anything that spans two
- **No horizontal slicing** — epics are user-outcome bundles, not tech layers
- **Success is measurable** — "improve performance" is not an epic
- **Sequence argument required** — every epic explains its place in the order
- **No timelines in epics.md** — epics carry sequence, not dates. Delivery dates live on
  the dashboard (`docs/project-status.html`, via `pm-project-status`) and in the GitHub
  issues created by `pm-to-issues`.
