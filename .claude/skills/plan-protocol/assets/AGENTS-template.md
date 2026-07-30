# AGENTS.md — the Plan Protocol

Every agent and every human follows this before touching code. This file is **protocol
only** — how to read, write, update, sync, and merge plans. It contains no facts about the
codebase; facts live in the docs it points to, and **the tree always wins over any doc**.

`AGENTS.md` is the cross-tool standard: Claude Code, Codex, Cursor and Windsurf all read it
natively. That is why the protocol lives here and not in a Claude-only file. And everything
binding is a **command** or a **git hook**, never a paragraph you are trusted to remember:
a rule an agent has to interpret is a rule that quietly stops happening at 2am, on the
twentieth branch.

```bash
node .specify/extensions/plan-protocol/plan.mjs <verb>
```

Zero dependencies — `node:` builtins only, no install, no `package.json` needed.

| Verb | Command | When |
|---|---|---|
| **READ** | `git show origin/main:.specify/ACTIVE.md` | always, first |
| **WRITE** | `plan.mjs submit` | registering new work |
| **UPDATE** | `plan.mjs index` | status or scope changed |
| **SYNC** | `plan.mjs sync` | before the first code edit |
| **MERGE** | `plan.mjs premerge` | before merging any code PR |

## The one rule

**No plan on `main`, no code.** Every piece of development starts with a plan in
`.specify/features/<slug>/`, merged to `main` before the first code edit. A plan that
exists only in chat, in a ticket, or on an unmerged branch **does not exist** — agents
cannot see it, so it cannot prevent a collision.

*Exemption:* trivial fixes — **≤ 3 changed files, none in a hot zone**. No plan dir needed;
`guard` grants this automatically. SYNC still applies. Anything larger fails the gate, so
do not talk yourself into "this is basically a typo".

## READ — where the truth lives, in resolution order

1. **`.specify/ACTIVE.md` as it exists on `origin/main`** — the registry of all in-flight
   and shipped work. **Generated** (`plan.mjs index`), never hand-edited, and your
   worktree's copy is as old as your branch point, so read the remote one:

   ```bash
   git fetch origin main --quiet && git show origin/main:.specify/ACTIVE.md
   ```

2. `.specify/features/<slug>/` — spec, plan, tasks, and `meta.yaml` for one feature.
3. **The tree.** If any doc disagrees with the code, the code is correct — fix the doc in
   the same PR rather than working around it.

## WRITE — starting new work

### 1. ELICIT — ask the human, before writing a single line of the plan

**Never author a plan from inference.** A plan is a decision about someone else's project:
what gets built, what does not, and what it may touch. Deciding that from a ticket, a chat
transcript, or your own judgment is making the call on their behalf and calling it process.
If you cannot **quote** what was asked, you do not have a plan yet — you have a guess with
a slug.

Ask at least these, and wait for answers:

| Ask | Because |
|---|---|
| **The problem, in your words** — what is wrong or missing today? | Goes in `ask:` verbatim. A paraphrase is already your interpretation. |
| **What does done look like?** | Becomes the success criteria. Without it you will decide when to stop. |
| **What is explicitly out?** | The scope you *would* have invented. Cheapest question here. |
| **Which shared surfaces may this touch?** | Becomes `touches` and any hot zone. Under-claim and the gate blocks you; over-claim and you collide with everyone. |
| **How does this sequence against what is already in flight?** | The registry shows what is running; only the human can rank it. |

One round is usually enough. Open questions that do not change the shape of the work go in
the spec as open questions — do not stall on them.

**No human available** (a cron run, a batch job, an autonomous sweep)? Register the plan as
`status: planned` with no approval fields. That is a **proposal**: visible in the registry,
costing nothing, and it grants **no lease** — `guard` will refuse to license code against it
until somebody agrees. Proposing work is always allowed. Starting it is not.

### 2. Run SYNC

```bash
node .specify/extensions/plan-protocol/plan.mjs sync
```

### 3. Write the plan

Create `.specify/features/<slug>/` with at minimum `meta.yaml` + `spec.md`. Flat YAML,
validated by `plan.mjs check`:

```yaml
slug: 001-example-feature        # must equal the dir name
title: Example feature
component: platform              # one of config.json's `components`
status: planned                  # planned | in-progress | blocked | shipped | superseded
owner: your-name/claude-code     # person/runtime — required once status is active
branch: feat/001-example         # required once in-progress
approved_by: sam                 # a PERSON, never a runtime — required once in-progress
approved_on: 2026-01-01          # required once in-progress
ask: the library page is slow on mobile and nobody can tell which module is next
touches: [src/lib/example]       # required once in-progress
migration: '010'                 # only if you will add a numbered migration
updated: 2026-01-01
```

`owner` is `<person>/<runtime>`: at several agents per human, "sam" does not say which
session holds the claim, and `sam/claude-code` and `sam/cursor` will overwrite each other.

`ask` is **the human's own words**, one line, trimmed but not paraphrased. It is the field
that catches invented scope: anyone can compare the ask against what the spec grew into.
Rewriting it in your own voice defeats the point, and a plan whose `ask` cannot be quoted
was not asked for.

`approved_by` is a person. A runtime cannot consent on a human's behalf, and an agent
filling in its own name is the exact failure this field exists to make visible.

### 4. Register and submit

`plan.mjs index`, then `plan.mjs submit` — the **fast lane**: for a plan-only diff it
validates, pushes, opens the PR, and merges it.

**Plan PRs need no review; plan *contents* need consent.** Those are different things, and
conflating them turns "the registry is the review surface" into licence to skip the human
entirely. Consent happens in step 1, in conversation, before anything is written — so by
the time the PR exists there is nothing left to review, and queueing it behind approval
would only teach people to start coding before the plan lands. Code PRs keep human review.

20 lines is a fine plan. Do not gold-plate the spec before registering the work.

## UPDATE — while working

- Status changes are edits to your own `meta.yaml` + `plan.mjs index`, riding in whatever
  PR caused them. The PR that completes a feature also flips its status to `shipped`.
- **Scope changes are declared, never silent.** Need a path outside your `touches`? Widen
  the list, regenerate, and include it in the same PR. Growing the PR instead is the
  mega-PR failure mode this protocol exists to stop.
- Keep `updated` current — claims go stale at 7 days and expire at 14.
- Never edit `ACTIVE.md` directly; it is overwritten on every regeneration.

## SYNC — before the first code edit

`plan.mjs sync` fetches, reads every active plan from the base ref, intersects `touches`
mechanically, checks migration numbers, and reports staleness. Exit 1 names the conflicting
plan and its owner. On a conflict: **stop and surface it to the operator** before writing
code.

## MERGE — before merging any code PR

`plan.mjs premerge`. Parallel branches rarely conflict in git; they conflict in **meaning**.
Two PRs can each be green alone and still break `main` together, with no textual conflict.
So this merges the base ref first, re-runs SYNC (plans that landed since you branched may
now overlap you), then runs the gate on the **merge result**.

## `touches` — the lease, not a hint

Repo-relative path prefixes, matched by path segment: `src/lib/quiz` covers
`src/lib/quiz/grade.ts` and never `src/lib/quizzer`. Declaring a directory claims
everything under it.

`guard` enforces the list as a **blast-radius cap** — every path changed versus the base
ref (committed, uncommitted, untracked) must be covered, or the gate and the pre-push hook
fail with the exact uncovered paths. Claim the narrowest set that fits: a plan claiming
`src` has claimed the whole app and will collide with everyone.

**Hot zones** (`config.json` → `hotZones`) need a declared touch **at least as specific as
the zone** — a broad parent prefix does not grant them. The engine's own directory is a hot
zone: it is the one file that can switch enforcement off.

## Enforcement

- **No consent, no lease.** `guard` refuses to honour a plan's `touches` unless
  `approved_by` is recorded, so forgetting to ask a human fails the gate instead of shipping
  an assumption. This holds for `planned` proposals too — otherwise "propose it yourself,
  then build it" would still be a compliant path. Plans already in flight when the rule
  landed belong in `approvalExempt`; that list only shrinks.
  It is not tamper-proof, and is not meant to be: an agent can type a name it never asked,
  exactly as it can declare `touches` it does not honour. What enforcement buys is that the
  claim is **visible in the diff and in the registry**, so skipping the human becomes an
  explicit false statement rather than silence.
- The project's gate runs `check` then `guard` first, cheapest-first.
- **`.githooks/pre-push`** runs `guard` and refuses direct pushes to `main`. Committed to
  the repo, activated per clone by `core.hooksPath=.githooks`, and it invokes `node`
  directly so it works with no `node_modules`. It fires for **every runtime**, including
  ones that never read this file. Never bypass it with `--no-verify`.
- **Enforcement is per clone AND per branch.** `core.hooksPath` is local config; the hook
  *file* is branch content. A branch cut before the protocol landed has no hook in its tree
  and is not guarded until it merges the base branch. Check a worktree with
  `git -C <path> hook run pre-push` rather than assuming.
- **`plan.mjs doctor`** reports drift — hooks inactive or non-executable (git ignores a
  non-executable hook *silently*), config behind the engine, expired claims. `--heal`
  repairs what it can. Run it in every fresh clone or worktree.
