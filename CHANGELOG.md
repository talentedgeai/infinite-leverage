# Changelog

All notable changes to the Infinite Leverage agent templates are recorded here.

Format: `## [version] — YYYY-MM-DD` with sections Added / Changed / Fixed / Removed.

---

## [2.8.1] — 2026-09-02

**`/il-adopt` catches up with 2.7.1, and `/il-doctor` finally checks adopted repos.**
2.7.1 fixed `/il-project`'s refresh path — retire the v2.4 set, assert the canonical 4
instead of counting to exactly 4 — but `/il-adopt` shipped a week earlier with the old
gate and no migration, and nothing cross-checked the two. Meanwhile `/il-doctor` keyed
its whole project-layout section on `FOLDER-STRUCTURE.md`, which an adopted repo never
has, so the one command told to "run after adopting to verify" verified nothing.

### Fixed
- **`il-adopt` step 5 retires the v2.4-era set on refresh** (writer/designer + 8
  skills, moved to `.claude/retired-il-<date>/`, never deleted) and **asserts the
  canonical 4 are present** rather than requiring exactly 4 — same block and same gate
  as `il-project` step 6. Before this, refreshing a v2.4.x repo through `/il-adopt`
  failed its own gate after a successful copy, and so did any repo with a custom agent
- **`il-doctor` runs its layout section for adopted repos** — detected by
  `.claude/agents/` or the delegation block, not only `FOLDER-STRUCTURE.md` (whose
  absence is now an info line, not a failure). It names the missing canonical agents
  instead of counting (six agents with `qa` missing used to pass), checks
  `global-engineering.md` is installed, and flags a **stale v2.4 delegation block** that
  still routes to writer/designer — a refreshed team under the old block sends work to
  agents that no longer exist. Every project-layout `fix:` now says `run /il-adopt`, the
  one refresh path, instead of "re-run /il-project step 6"
- **No more silent `python3` dependency.** All three skills read the plugin's version
  with `sed`; `python3` was never a checked prerequisite, and when it was missing the
  version came back empty, the clone fell back to `main` under a misleading
  "no tag v?" message, and the doctor reported `vunknown`. The fallback now says which
  of the two causes applied (version unreadable vs. release untagged)

### Added
- **CI: canonical team in lockstep** — the agent names in `il-project`'s gate,
  `il-adopt`'s gate and `doctor.sh` must equal `.claude/agents/`; the skills threshold
  must equal the shipped count; the retired v2.4 lists must be identical in all three
  and name nothing that still ships. The old check only compared one regex against
  `doctor.sh`, which is how the `il-adopt` drift went unnoticed for a release
- **CI: AGENT-DELEGATION block parity** — byte-identical in `il-project`, `il-adopt`
  and the scaffold's `CLAUDE.md`, and its rows route exactly the shipped agents
- **CI: `il-doctor` smoke test** (`.github/scripts/doctor-smoke.sh`) — 26 assertions
  over synthetic scaffolded, adopted, legacy-v2.4, missing-`qa`, partial and plain
  trees, plus the `sed` version parse. Before this the doctor's layout checks had never
  executed under CI at all

### Changed
- `il-doctor/SKILL.md` documents the adopted-repo detection, the stale-block check and
  the single `/il-adopt` fix path; `RELEASE-CHECKLIST.md` Run 1 shows the current gate
  output (it still said `6/6 · 24/24`), Run 4 exercises `/il-adopt` on both a scaffolded
  and a never-scaffolded repo; `il-project/references/quick-prompts.md` rewritten to
  match the skill it documents (it still asked whether to scaffold Next.js, which has
  been mandatory since 2.x, and carried the pre-rename skill name)

---

## [2.8.0] — 2026-08-27

**Billing stripped from the web template.** Follow-up to 2.7.2 (which removed Stripe
from the client guide): the scaffold no longer ships payments code at all. A project
that later takes money adds it then — the template shouldn't carry a feature no first
build uses.

### Removed
- `app/api/billing/` (checkout, portal, webhook), `components/billing/`
  (PricingCard, UpgradeButton), `lib/billing/` (guards, queries, stripe client)
- `lib/supabase/service.ts` — the service-role client existed solely for billing
  writes; with no privileged writers left it goes too, and with it
  `SUPABASE_SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` and
  `NEXT_PUBLIC_APP_URL` (read only by the Stripe return URLs) from
  `.env.local.example` — 7 env vars down to 3
- The `subscriptions` migration and `docs/billing/setup-notes.md`
- `stripe` from il-project step 9c's dependency install

### Verified
- Nothing outside the billing tree imported it (NotificationBell's "subscription" is a
  Supabase realtime channel; untouched)
- All 12 CI guards recomputed clean: 16 query sites against 3 tables, 3 env vars all
  read and none stale, 21 imports all declared
- Full scaffold rebuild from scratch without stripe: lint, tsc, build and vitest all
  exit 0 — 15 routes (billing's three gone), 20 tests

---

## [2.7.2] — 2026-08-27

### Removed
- **Stripe dropped from the client setup guide.** The accounts prompt (Prompt 2) now
  covers GitHub-check, Supabase and Vercel only; the ask-first Stripe step, the journey
  table's "and Stripe if you take payments", and the intro's payments mention are gone.
  Payments can be added later when a project actually needs them — the setup path
  shouldn't carry an optional detour every client reads past. (No Resend/Brevo mentions
  existed in the guide; verified.)

---

## [2.7.1] — 2026-08-27

**The v2.4 → v2.6 migration path for existing projects.** v2.6.0 removed the writer and
designer agents, but a project scaffolded on v2.4.x still carries them — and nothing
removed them on refresh. Worse: step 6's gate demanded *exactly* 4 agents, so refreshing
a legacy project (6 on disk) failed the gate even after a successful copy.

### Fixed
- **`il-project` step 6 now retires the v2.4-era set on refresh** — 2 agents
  (writer.md, designer.md) and 8 skills (the content pipeline) — by **moving** them to
  `.claude/retired-il-<date>/`, never deleting, in case a client edited one. On a fresh
  scaffold the block is a no-op. Verified end to end against a real v2.4.5 tree:
  retired files land in the dated folder, a custom agent and a custom skill placed
  beside them survive untouched, and the step is idempotent
- **Step 6's gate asserts the canonical 4 are present instead of counting to exactly 4.**
  The exact count was wrong twice over: it failed legacy projects mid-migration, and it
  failed any project that legitimately added its own custom agent
- **`il-doctor` flags lingering retired agents/skills** inside a project, naming each
  one found and the fix (re-run step 6). Verified: FAILs on the legacy tree before
  migration, PASSes after

---

## [2.7.0] — 2026-08-27

**Existing repos can finally get the team.** Until now the 4 agents and their skills
were only installed by `/il-project` — as part of scaffolding a brand-new project.
An already-established repo had no path to them (the plugin itself ships no agents;
they are always project-scoped).

### Added
- **New skill `/il-adopt`** — installs the canonical 4 agents, the 16 workflow
  skills, and `global-engineering.md` into the **current** repo's `.claude/`,
  injects the AGENT-DELEGATION block into the repo's `CLAUDE.md` (creating it if
  missing, replacing only the managed block if not), and seeds persona stubs and
  doc anchors (`docs/product/*`, `docs/brand/style-guide.md`,
  `docs/project-status.html`) **only where missing**. Mirrors `/il-project`'s
  version-pinned clone, install gate, and delegation block. Non-destructive:
  detects a previous install and confirms before refreshing canonical files, never
  touches operator-written files, and never commits — it prints the explicit
  `git add` / `git commit` for the operator.

---

## [2.6.1] — 2026-08-27

### Fixed
- **Prompt 1 skipped Homebrew — which just moved the wall to Prompt 3.** Khoa's catch:
  the install prompt later tells Claude Code to add Node/rsync "with my package manager",
  and on a Mac that package manager *is* Homebrew — whose own installation needs an
  interactive password only the client can type, in their own Terminal, during the
  ordinary-Claude phase. New STEP 4 in "Get ready": the brew.sh install command, with the
  two warnings that actually matter to a non-technical person (it will ask for your
  password and nothing shows while you type — that's normal; it takes a few minutes), and
  the instruction to paste the installer's printed "Next steps" commands so the Terminal
  can find brew afterwards. Verified done via `brew --version`
- With Homebrew present, the flow simplifies: git arrives with the developer tools
  Homebrew installs, and gh becomes `brew install gh` instead of a website download.
  Prompt 3 now names Homebrew (and winget on Windows) instead of "my package manager"
- Command table gains the brew.sh install command and `brew install gh`

---

## [2.6.0] — 2026-08-27

**The team slims to 4 agents.** The writer and designer agents are removed — they were
not being used.

### Removed
- Agents `writer` and `designer` (`.claude/agents/`), plus their scaffold personas
  (`templates/project-scaffold/agents/{writer,designer}/`).
- Their skills: `writer-seo-content`, `writer-quality-critique`,
  `email-marketer-nurture`, `marketing-strategist`, `designer-design-system`,
  `designer-image-generation`, `designer-style-to-photo`, `designer-ui-ux`
  (24 → 16 skills).
- Scaffold artifacts of the content/email chain: `emails/` and
  `content/topics/{slug}/image-prompts.md`.

### Changed
- Publishing stays with the developer (`web-publisher-publish`) — the operator now
  supplies the finished post + hero image in `content/topics/{slug}/`.
- Counts updated everywhere the tooling asserts them: CI (`plugin-ci.yml`),
  `doctor.sh`, `/il-doctor`, `/il-project` install gate and delegation block,
  routing rules, README, guides, and the slide deck.

---

## [2.5.0] — 2026-08-27

### Added
- **New skill `/il-memory-cleanup`** — for operators who switch between several
  Claude accounts on one machine and end up with a messy global `CLAUDE.md` and
  memory index. Unlike batch memory consolidators, it is a conversation: the agent
  reads every memory file in full, narrates duplicates / conflicts / stale facts /
  index drift / cross-account bleed back to the operator (quoting both sides of
  each conflict and saying which the evidence favors), and only acts on explicit
  per-item approval. Safety properties: tar backup before the first write with the
  restore command printed; conflicts are always decided by the human, never the
  agent; stale claims require an actual verification check; scope is memory
  content only — settings, permissions, and installs stay untouched (v1 residue is
  routed to `/il-doctor` instead).

---

## [2.4.16] — 2026-08-27

**The bootstrap now runs in ordinary Claude.** Khoa's catch: the guide's first prompt
assumed Claude Code, but Claude Code can't be the guide for installing Claude Code — and
a non-technical client starts from the chat they already have.

### Changed
- **New Prompt 1 — "Get ready" — runs in any Claude: the website, the app, or Cowork.**
  There Claude can't touch the computer, so the prompt makes it a pure instructor: ask
  Mac or Windows first, then one copy-paste at a time — open the Terminal (with the
  reassurance that nothing pasted there can break the computer), install git
  (`git --version` triggering the macOS developer-tools dialog; git-scm.com on Windows),
  install gh from cli.github.com (the downloadable installer — explicitly do NOT make
  the client install Homebrew for this), `gh auth login` guided question by question
  (the browser page opens already signed in from the GitHub step — one Authorize click),
  and finally install the Claude Code desktop app itself. The client pastes back what
  they see; Claude interprets — "never just point at an error"
- **The journey is now five prompts**: 1 Get ready (ordinary Claude) → 2 Set up your
  accounts (Claude Code: Supabase, Vercel, Stripe — GitHub moved to Prompt 1) →
  3 Install → 4 Create your project, with 0 Clean up for v1 veterans. Prompt 2 verifies
  `gh auth status` itself and routes back to Prompt 1 — naming that it runs "in the
  ordinary Claude app, not here" — rather than half-fixing auth
- The journey table gains a **"Where it runs"** column; the standalone get-Claude-Code
  section from 2.4.15 folded into Prompt 1's final step
- Command table gains `git --version` and `gh auth status` rows, since Prompt 1 hands
  those to the client to paste themselves

---

## [2.4.15] — 2026-08-27

### Fixed
- **The guide never said where the prompts run.** It assumed Claude Code was already on
  the machine — the one assumption this audience cannot fill in themselves. New section
  at the top: get the **Claude Code desktop app** (claude.ai/download, normal drag
  install, sign in with a paid Claude plan, open the Claude Code tab), with the
  one-sentence distinction that matters: regular Claude talks, Claude Code can also use
  the computer — install tools, sign the machine in to GitHub, create the project — so
  the client never opens a terminal. An explicit warning covers the near-misses: the
  Claude website and the Cowork side of the app cannot install tools or sign the
  computer in to GitHub, so the prompts will not work there

---

## [2.4.14] — 2026-08-27

### Fixed
- **The journey order had a bootstrap problem.** Install came before accounts, but the
  install prompt runs `gh` and `/il-doctor` complains about GitHub auth — and you cannot
  sign in to an account that does not exist yet. Reordered: **1 Set up your accounts →
  2 Install**. The accounts prompt now also owns the machine-side GitHub connection: it
  installs git/gh if missing (asking once; the client types any password themselves) and
  runs `gh auth login` right after the GitHub sign-up, so the browser page it opens is
  already signed in and the client just clicks Authorize
- **Google Chrome is now step 1 of the accounts prompt.** Every sign-in that follows —
  GitHub, Supabase, Vercel, Stripe, and the `gh auth login` browser flow — happens in one
  browser where the client stays signed in. Claude checks whether Chrome is installed and
  guides the download click by click if not
- **Prompt 2 (Install) refuses to duplicate Prompt 1's work**: if the computer is not
  signed in to GitHub, it says "run the prompt called 1 - Set up your accounts first"
  and stops, instead of half-fixing auth mid-install
- **Prompt 0's handoff updated for the new order**: v1 veterans go straight to
  3 - Create your project (their accounts and sign-ins still work), with 1 as the
  fallback if they no longer have them

---

## [2.4.13] — 2026-08-27

**The setup guide becomes a four-prompt journey.** Rewritten for the actual audience —
CEOs, sales, marketing — after Khoa's feedback: everything prompt-driven, nothing that
assumes the reader runs commands or wants to.

### Changed
- **Structure: four prompts, in order, each naming the next.** 0 Clean up (only if
  they've used v1) → 1 Install → 2 Set up your accounts → 3 Create your project. Every
  prompt ends with the same fixed handoff pattern ("copy the prompt called …"), and
  Prompt 1 detects v1 leftovers itself and routes back to Prompt 0 before touching
  anything. The old Prompt A/B split (hands-off vs guided) is gone — one journey, always
  hands-off; the command table serves anyone technical
- **Account creation is its own guided step (Prompt 2).** Previously buried as "things
  only I can do" inside the install prompt. Now Claude acts as a patient guide per
  account — one sentence on what it's for, numbered click-by-click steps, what to type,
  then a verification before moving on (`gh auth status` for GitHub; Supabase project
  exists; Vercel via the sign-in-with-GitHub button; Stripe asked about and skipped
  unless the project takes payments). Keys are deliberately deferred to Prompt 3 so the
  account step stays browser-only
- **Prompt 3 (create your project) slims down** to what's left once accounts exist:
  scaffold, connect keys one at a time, build check, optional GitHub push, and the
  three-things-to-try ending

### Added
- **A plain-English command table** — every command the prompts run, with what it does
  in one sentence ("Tells Claude Code where Infinite Leverage lives. Run once, ever."),
  under the honest heading that nobody needs to memorise them: it exists so none of it
  feels like magic
- **A rescue prompt** in the troubleshooting section — paste-any-time `/il-doctor`
  wrapper that reports in plain English and fixes what it can

---

## [2.4.12] — 2026-08-27

### Changed
- **Prompt 0 rewritten to run quietly.** The first version was built for caution — show
  every settings edit, list what moves, wait for a yes at each step. For a non-technical
  client that reads as alarming, not safe. Now: one plain-English plan up front (three
  sentences — found leftovers or not, what happens next, nothing of yours will be
  touched), then the whole cleanup runs without step-by-step approvals, file lists, or
  jargon; the client hears "removed", and about the dated backup folder once, at the end.
  The safety net is unchanged underneath — dated settings backups, archive-by-rename
  instead of deletion, locally-modified files left in place — it just stopped narrating
  itself. The one rule that never bends is now the prompt's loudest section: anything not
  on the v1 lists is the client's own and is the only thing worth stopping to ask about.
  The detection lists are explicitly marked "for you — never read this back to me"

---

## [2.4.11] — 2026-08-27

### Fixed
- **Every install site now carries the update path.** `claude plugin install` does not
  upgrade an existing plugin, but three of the four places a client meets the install
  commands (Prompt A, Prompt B, and Prompt 0's closing step) only said `install` — an
  already-installed client following any of them stayed on their old version while the
  conversation reported success. All three prompts now add: "If it says the plugin is
  already installed, update it instead: `claude plugin update
  infiniteleverage@infiniteleverage`", and the manual Step 1 in the guide gains the same
  under "Already have it installed?"

---

## [2.4.10] — 2026-08-27

### Changed
- **Prompt 0 now hands the client to the next prompt when it finishes.** Whether it
  cleaned anything or found nothing to clean, it ends by telling the client — in fixed
  wording — to go back to the setup guide, copy Prompt A (or B), fill in their project
  name, and paste it into the chat, then stops and waits. Previously the cleanup
  conversation just ended, leaving a non-technical client without a next move. Cleanup
  and setup remain two separate prompts on purpose: one conversation that both deletes
  old files and scaffolds a new project is harder to follow and harder to stop halfway

---

## [2.4.9] — 2026-08-26

### Added
- **Prompt 0 in `docs/guide/CLIENT-SETUP.md` — recovering from an old install.** Detects
  which of two cases applies and handles either: v1 residue in `~/.claude/` (agents,
  hooks, the `il_telemetry` package, the version marker, ~95 globally-installed skills,
  and — the part that matters — the `Bash(*)` permission grant plus `acceptEdits` default
  in settings), or simply an out-of-date v2 plugin. Built from ground truth, not memory:
  the v1 file list is generated from both repos' git history, and the settings surgery
  mirrors what `migrate_v1.py` does in the private telemetry plugin. Safety properties:
  look-only first pass; explicit "anything not on these lists is yours — leave it alone";
  settings edited surgically with dated backups, never replaced; files archived into a
  dated folder by rename, never deleted; locally-modified files reported, not moved.
  Edge8-internal machines are pointed at `/edge8-telemetry` instead, which does this
  hash-verified

---

## [2.4.8] — 2026-08-26

### Added
- **A hands-off install prompt for non-technical clients** in
  `docs/guide/CLIENT-SETUP.md`. The existing prompt assumed someone comfortable running
  commands and reading output; this one hands Claude the whole job. It sets working rules
  (plain English, no raw errors, one question at a time, never ask the client to edit a
  file), names the three things Claude genuinely cannot do for them — `gh auth login` is
  an interactive flow, accounts must be created by a person, dashboard keys must be copied
  by a person — and front-loads those so the client isn't interrupted mid-install. It also
  tells Claude to confirm the key file is gitignored, and to stop rather than invent a
  workaround. The original is kept as the guided alternative.

---

## [2.4.7] — 2026-08-26

**The setup instructions named a key the code does not read.** Writing the client setup
guide surfaced it: a client following the instructions exactly got an app where every
Supabase call received `undefined`.

### Fixed
- **`NEXT_PUBLIC_SUPABASE_ANON_KEY` → `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.** The code
  reads `PUBLISHABLE_KEY`; `il-project` step 11 and `devops-cicd` (both the workflow env
  block and the GitHub-secrets instructions) told the operator to set `ANON_KEY`. Builds
  still pass — prerendering never exercises it — so this surfaces at runtime, on the first
  login, in front of the client
- **No `.env.local.example` existed at all.** The client had to derive variable names from
  the source. Added one listing all 7 variables the app reads, each with where to get it
  and why (including why `SUPABASE_SECRET_KEY` must never carry a `NEXT_PUBLIC_` prefix)
- **The example would have been silently untracked.** create-next-app's `.gitignore` has a
  blanket `.env*`, so a committed example is invisible to teammates. Step 9 now appends
  `!.env.local.example` after the merge — verified end to end: the example is staged in the
  first commit, and a real `website/.env.local` stays ignored
- **`docs/billing/setup-notes.md` required `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`**, which
  nothing reads — checkout is server-side and the browser only gets the returned URL. It
  also omitted `SUPABASE_SECRET_KEY`, which billing genuinely needs

### Added
- **CI: every `process.env.*` the template reads must appear in `.env.local.example`**, and
  nothing may be documented that is never read. Both directions, so the list cannot drift
  in either — this is the guard that would have caught the `ANON_KEY` mismatch
- **`docs/guide/CLIENT-SETUP.md`** — the install and first-project walkthrough written for
  the client, including a paste-in prompt that drives the whole install

---

## [2.4.6] — 2026-08-26

**Install-path pinning, and the Designer chain fixed to match the file it actually reads.**
Triaged the last open v1 PR and ported the durable idea out of it.

### Fixed
- **`/il-project` cloned the canonical content from `main`, unpinned, while the plugin
  itself is cached per version.** The two drift: a client on a cached older plugin pulls
  newer scaffold content, and in a workshop two people running the same command minutes
  apart get different scaffolds if `main` moves. Step 3 now clones the tag matching the
  running plugin's version (read from its own `plugin.json` via `CLAUDE_PLUGIN_ROOT`) and
  says so, falling back to `main` with a visible warning when no tag exists
- **v2 releases were never tagged** — the newest tag was `v1.8.0`, so there was nothing to
  pin to. Tagged `v2.4.0` … `v2.4.5` at their release commits, and the release flow in
  `CLAUDE.md` now requires tagging as a step, not an afterthought
- **`/il-doctor` now reports plugin version skew.** A cached older plugin is how a fixed
  bug keeps biting — `/il-project`'s own steps ship *inside* the plugin, so a client stayed
  on the broken step 6 until they updated, and nothing told them to. Verified against the
  real cache: a client on v2.4.0 is told v2.4.5 is out and given the update command
- **The Designer chain read a file shape that does not exist.** `designer-design-system`
  and `designer-style-to-photo` both described `docs/brand/style-guide.md` as holding
  "5 presets"; the file `/il-project` step 8.7 actually creates is a **single brand
  identity** (Brand identity · Voice · Vocabulary · Colour palette · Typography · Visual
  style · Content formats). `designer-style-to-photo` step 1 would have looked for five
  presets and found none — a break in the content pipeline on any real project

### Changed
- **`designer-design-system`** rewritten against the real file: it owns three sections
  (Colour palette, Typography, Visual style), states who owns the rest, refuses to invent
  a guide that does not exist, and gates on contrast plus no leftover placeholders
- **`designer-style-to-photo`** picks a *treatment* within the one brand palette rather
  than swapping palettes, and writes hex values from the guide's actual table. The marker
  comment is now `<!-- treatment: … -->`; the scaffold stub and
  `designer-image-generation` follow
- **`designer-ui-ux`** was 17 lines of bullets with no procedure, yet "does this look
  right" is one of its triggers. Now a review with a scope step, a runnable WCAG contrast
  calculator (verified against the known AA boundary: `#767676` on white = 4.54), a report
  format, and an explicit instruction not to claim a page "looks right" from a code read

### Added
- **`docs/RELEASE-CHECKLIST.md`** — runs 0–8 with a cadence, ported from the retired v1
  init PR's test matrix. It states plainly which runs are verified and which have never
  been executed

### Triaged
- **#55 closed.** All six files it touches were deleted in the v2 restructure; it modified
  the retired `setup-skills/` bootstrap. Closed with a note mapping each of its 12
  invariants to where it lives now, and its test matrix became the release checklist

---

## [2.4.5] — 2026-08-26

**A silent RLS denial in the billing path.** Cross-checking the scaffold's Supabase
migrations against the code that queries them turned up a real bug in the shipped Stripe
integration, plus three RLS hygiene gaps.

### Fixed
- **`app/api/billing/checkout/route.ts` wrote to `subscriptions` with the user-scoped
  client, and RLS denied it silently.** That table's only policy is `for select` — by
  design, since a user who could write their own row could set `plan: 'enterprise'` and
  skip paying (`lib/billing/guards.ts` gates features on `plan`/`status`). The migration
  says so in a comment: *"All writes are performed by the webhook handler using the
  service role client."* The route did not follow it, and the result was never checked
  (`await supabase...upsert(...)` with no `error` destructuring), so the write failed
  without a trace. Consequences: `stripe_customer_id` is never persisted, so the **next**
  checkout attempt finds no customer and mints a **second Stripe customer for the same
  user**, and "Manage billing" returns *"No billing account found"* until a payment
  actually completes and the webhook writes the row. Now uses the service-role client and
  fails closed with a 500 if the write is rejected
- **New `lib/supabase/service.ts`** — one shared service-role client, documented with why
  `subscriptions` is SELECT-only, so the next route to need a privileged write does not
  reinvent it. The webhook's private copy was removed in favour of it; it also throws a
  named error when `SUPABASE_SECRET_KEY` is unset instead of failing at the API call

### Changed — RLS hygiene across all four tables
- **`auth.uid()` → `(select auth.uid())`.** Bare `auth.uid()` re-evaluates for every
  candidate row; the subquery form is hoisted to an initplan and runs once. The documented
  Supabase anti-pattern, present in every policy the scaffold shipped
- **Policies scoped `to authenticated`.** They previously applied to every role, `anon`
  included
- **Explicit `with check`** on the `for all` policies, so the insert path is stated rather
  than inherited from `using`
- **Indexes on the columns RLS filters by** — `chat_sessions(user_id)` and
  `chat_messages(user_id)` had none. `notifications` and `subscriptions` were already
  covered (composite index / `unique` constraint)

Migrations are edited in place because they are template files consumed at scaffold time.
A project already scaffolded needs these as a follow-up migration.

### Added — CI guards
- **Queries match migrations**: every `.from('table').select('col')` in the web template
  must resolve against a `create table` in `supabase/migrations/`. 24 query sites, 4 tables
- **RLS hygiene**: every table enables RLS, no bare `auth.uid()`, every policy scoped
  `to authenticated`

Both verified against deliberate regressions — reverting to bare `auth.uid()`, dropping
`to authenticated`, removing an `enable row level security`, and querying a nonexistent
column each fail the build with a specific message.

### Verified
SQL parsed with libpg_query (`pglast`) — 16 statements across 3 migrations. The scaffolded
app rebuilt from scratch with the billing fix: lint, `tsc --noEmit`, build, and vitest all
exit 0 (20 tests).

---

## [2.4.4] — 2026-08-26

**The plan-protocol engine, actually run.** A 35 KB engine with its own 30-test suite ships
into every scaffolded project, and nothing had ever executed either — not CI, not a review.
Running it end to end surfaced a portability bug that made the skill's headline claim false.

### Fixed
- **`plan-protocol` imposed one client's domain vocabulary on every project.** The engine
  hard-coded `components: ['learner', 'manager', 'admin', 'platform']` and `init` never
  wrote the key into `config.json`, so it was invisible and unoverridable in practice —
  a Rails shop had to label its billing work `learner`. The skill's own description says it
  "works in any stack". `components` now ships **empty**, meaning any non-empty component
  string is valid; a project opts into a fixed vocabulary by filling the list in, and the
  enum is enforced against that. A missing `component` is still an error.
  Backwards compatible: an install that already sets `components` keeps its enum
- **`init` now writes `components` into `config.json`** so the knob is discoverable, and
  `bootstrapPlan` no longer indexes into a possibly-empty list

### Added
- **CI runs the plan-protocol engine suite** (`node --test`, 32 tests, no install needed).
  It had never run; a regression in the enforcement engine would have shipped silently
- **CI asserts the engine ships no domain vocabulary** — `DEFAULT_CONFIG.components` must be
  empty. Verified against the regression: reintroducing the old list fails the build
- Two engine tests for the taxonomy modes (free-form by default, enforced when configured),
  replacing the one that asserted the client-specific enum

### Verified end to end (not just unit-tested)
Installed the protocol into two throwaway repos — a Next-shaped one and a Rails-shaped one:
- `init` writes `config.json`, scaffolds `.githooks/pre-push` mode 755, sets
  `core.hooksPath`, seeds a bootstrap plan, and `doctor` reports enforcing
- hot-zone detection found the Rails layout (`db/migrate`, `Gemfile`) with no Node marker
- the pre-push hook **blocks a direct push to `main`**
- the blast-radius guard exits 1 on an undeclared hot-zone change, and the pre-push hook
  blocks that push too — the protocol's core promise, now demonstrated rather than asserted

### Changed
- `SKILL.md` documents `components` in the policy list; `AGENTS-template.md` no longer
  implies the list is always populated

---

## [2.4.3] — 2026-08-26

**Scaffold-to-CI continuity.** Verified that a project `il-project` produces passes the
pipeline `devops-cicd` installs, and documented what Next 16 now adds on its own.

### Verified (no code change needed)
- **The first commit does not swallow `node_modules`.** Step 10 stages every untracked
  file *after* Step 9's `npm install`; confirmed the root `.gitignore` and
  create-next-app's `website/.gitignore` both cover it — 158 files, 1.1 MB, zero
  `node_modules`, `.next`, or `.env` entries
- **`npm ci` works from the committed lockfile**, and every file the generated pipeline
  reads (`package.json`, `package-lock.json`, `tsconfig.json`, `eslint.config.mjs`,
  `vitest.config.mts`, `vitest.setup.ts`) is in that first commit
- **The generated CI pipeline is green on a fresh project**: install, lint, type check,
  test (20 passing), build — all exit 0

### Added
- `website/AGENTS.md` and `website/CLAUDE.md` documented in `FOLDER-STRUCTURE.md` and
  `il-project` step 9. Next 16's create-next-app writes both (`CLAUDE.md` is a one-line
  `@AGENTS.md` import; `next dev` rewrites the block inside `AGENTS.md`). They are
  framework-owned, they load only when an agent works inside `website/`, and they must not
  be confused with the repo-root `CLAUDE.md` that carries the agent-delegation block or a
  repo-root `AGENTS.md` installed by `plan-protocol`

---

## [2.4.2] — 2026-08-26

**The web template, actually run.** `il-project` step 9 had never been executed end to
end in CI or in review. Running it revealed the shipped Next.js starter fails its own
pipeline, plus a dependency that only resolved by luck. CI now guards the whole class.

### Fixed
- **The web template failed `npm run lint` with 2 errors**, so every new project's first
  CI run — from the pipeline `devops-cicd` installs — went red on template code the
  operator never wrote:
  - `components/upload/FilePreview.tsx` called `setState` synchronously inside an effect
    (`react-hooks/set-state-in-effect`). The object URL is now derived with `useMemo` and
    revoked in a cleanup effect, which also removes a cascading render and the flash of
    the file icon before the thumbnail
  - `lib/chat/queries.test.ts` returned an anonymous wrapper component
    (`react/display-name`) — now a named `Wrapper`
  - Two unused-variable warnings cleared: `Link` in `MobileDrawer.tsx`, and the unused
    props parameter (plus its now-orphaned type import) in `MDXEditorFull.tsx`
- **`unified` was imported but never installed.** `MarkdownRenderer.tsx` does
  `import type { PluggableList } from 'unified'`; step 9c never listed it, so it resolved
  only because npm hoists it as a transitive dep of react-markdown. Added to step 9c
- **`vitest.config.ts` → `vitest.config.mts`.** Vitest warned that ESM syntax in a
  CommonJS-loaded config breaks under `configLoader: 'native'`, planned to become the
  default. The `.mts` extension makes it explicitly ESM
- **Step 6's install check was a `printf`, not a gate.** It only stopped when a count hit
  zero. Now asserts 6 agents and ≥20 skills and exits non-zero otherwise — and counts with
  `find` rather than a glob, because under zsh a non-matching glob aborts the command
  instead of returning nothing

### Changed
- **Step 9e verifies the full pipeline**, not half of it: `npm run lint && npx tsc
  --noEmit && npm run build && npx vitest run`. The previous gate ran build + vitest only,
  which is exactly why two lint errors shipped
- **`FilePreview` gained a test** (`FilePreview.test.tsx`, 6 cases) covering the
  thumbnail, the non-image icon path, size formatting, `onRemove`, revoke-on-unmount, and
  URL rotation when the file changes — the path the `useMemo` refactor could have broken

### Added — CI guards for everything this review found
The existing "no global-install regressions" check grepped only for `cp`, which is why
`il-project` step 13's `mkdir`/`touch` into `~/.claude` survived three releases. Now:
- Any write verb (`cp`/`mv`/`mkdir`/`touch`/`tee`/`rm`/`ln`/`install`) or shell
  redirection targeting `~/.claude`, `$HOME/.claude` or `${HOME}/.claude` fails the build,
  as does any mention of `human-token-tracker` or `il-telemetry` in the shipped payload
- Agent and skill counts are asserted (6 / 24) **and cross-checked against the threshold
  hard-coded in `doctor.sh`** — the drift that produced "found 6/8"
- Every skill must have frontmatter whose `name` matches its directory
- Every package the web template imports must be declared by step 9c

Each guard was verified against the bug it targets: re-injecting the step-13 telemetry
write, restoring `-ge 8`, and removing `unified` each fail CI.

---

## [2.4.1] — 2026-08-26

**Final skill review.** A full pass over all 26 skills, the 6 agents, the routing rules and
the scaffold. Three of these were install-breaking.

### Fixed
- **`il-project` step 6 never installed the agents.** The scaffold ships `.claude/rules/`
  and `.claude/skills/` but not `.claude/agents/`, so `cp .../agents/*.md "$TARGET/.claude/agents/"`
  failed with `Not a directory` and every new project came up with zero agents. Step 6 now
  `mkdir -p`s all three destinations and verifies the counts (6 agents / 24 skills) before
  continuing
- **`il-doctor` failed on every healthy project.** The agent check asserted `-ge 8` against a
  6-agent roster and told the operator to re-run an install step that was already correct.
  Now checks 6, and also verifies the 24 skills landed
- **Prerequisite checks matched neither reality nor each other.** `il-project` checked
  `gh`/`git`/`perl` while mandatory step 9 needs `node`/`npm`/`npx`/`rsync`; `il-doctor`
  checked a different set again. Both now check the same union, and `il-project` verifies
  `gh auth status` up front
- **`web-publisher-publish` pushed to `main`, then asked whether it was on a branch.**
  Phase 5 ran `git push origin main` and Phase 6 then offered a PR flow that could never be
  reached. Now: `publish/{slug}` branch → PR → merge only under the auto-merge criteria in
  `developer.md`, with the preview URL handed over when it stops for approval
- **`devops-git-guardrails` blocked `--amend` on branches that were never pushed** — the
  upstream check treated "no upstream" as "already published". Rewritten around
  `@{upstream}` with the logic verified against real repos; also fixes `--force-with-lease`
  slipping through, and moves from the deprecated `{"decision":…}` output to exit-code 2
- **`qa-triage` wrote bugs into a "Known Issues" heading that `epic-status.md` never has.**
  Now writes to the At-a-glance count and the Drilldown section that actually exist
- **`writer-seo-content`'s image-prompt example was a broken nested code fence** — the inner
  ```json fence terminated the outer block early. Outer fence is now four backticks
- **`devops-cicd` ran `npm test -- --ci`**, a Jest-only flag the scaffold's Vitest rejects.
  Now `npx vitest run --passWithNoTests`, with the Jest equivalent noted
- **`designer-image-generation` stretched hero images** — bare `scale=1200:630` on any source
  that isn't 40:21. Now scale-and-crop, and it creates the scratch dir it writes to
- Dead references removed repo-wide: `developer (publishing)-publish` in the routing table,
  `/use-dev-team` and `/use-marketing-team`, `docs/product/01-product-timeline.md`,
  `/capture-learning`, and ~15 skill names retired in 2.2.0/2.4.0

### Removed
- **Effort-tracking registration (`il-project` step 13).** It wrote to `~/.claude/`, pushed
  client names and their staff's git emails to `talentedgeai/human-token-tracker`, and
  referenced a session-start hook this plugin doesn't ship — contradicting the repo's own
  "nothing global, no telemetry" rule, both manifests, and the skill's own execution
  contract. Telemetry belongs to the private `edge8-telemetry` plugin. "telemetry" dropped
  from the plugin keywords and the marketplace description
- **`pm-project-status`'s team-hours machinery.** §6/§7 depended on `scripts/team-hours.py`
  and `docs/assessments/team-hours-methodology.md` — neither ships — and carried
  client-specific language ("human tokens", owner "carries clinical/regulatory risk").
  Replaced with a Contributor Activity table and a Pulse Chart built only from `git`, `gh`,
  `epic-status.md` and `docs/qa/`
- **v1 documents that contradicted the shipped product**: `docs/guide/agent-map.html`
  (titled "8-Agent Team"), `docs/guide/SCAFFOLD.md` and `docs/install-prompt.md` (both
  documenting the retired global `~/.claude/` install). Nothing linked them; recoverable
  from git history
- **Two byte-identical duplicates of the intro deck** (`Infinite-Leverage-8-Introduction.html`,
  `infinite-leverage-introduction.html`). `docs/slides/index.html` is the single copy, and
  its text now names `/il-project` and `/il-doctor` instead of the retired
  `/infiniteleverage-init|onboard|patch`, a 6-agent roster, and the one-repo-is-the-
  marketplace architecture
- **A real contributor's usage data shipped in the scaffold.** `templates/project-scaffold/docs/project-status.html`
  carried a hard-coded username, hour count and token total, plus a call to a
  `~/.claude/hooks/` script this plugin doesn't ship — copied into every new client
  project. Replaced with an empty git/gh-derived Contributor activity table

### Changed
- **Email is draft-only in the skill body, not just the description.** `email-marketer-nurture`
  said "drafted for operator approval" in its frontmatter while its workflows said "send to
  all active subscribers". The hard rule is now the first thing in the body, and its state
  files moved from the non-existent `agents/email-marketer/` to `agents/writer/context/`
- **Image-prompt ownership settled.** The Writer owns `image-prompts.md` (JSON);
  `designer-style-to-photo` now tunes its `style`/`mood`/`palette` in place instead of
  authoring a competing key-value prompt. `FOLDER-STRUCTURE.md` and the scaffold stub
  renamed `images.md` → `image-prompts.md` to match
- **No skill commits without instruction.** `pm-constitution-sync`, `pm-project-status`,
  `dev-tdd`, `devops-cicd`, `devops-setup-pre-commit` and `devops-git-guardrails` all
  auto-committed against `global-engineering.md`; they now stage and hand off
- **`devops-git-guardrails` is project-scoped and merges settings.** It no longer offers
  `~/.claude/settings.json`, and registers its hook without clobbering existing keys
- **`marketing-strategist` writes to paths that exist** — `context/source-material/`,
  `content/content-calendar/content-calendar.md`; dropped the invented `content/images/`
  and the handoff to a non-existent "Content Producer"
- `pm-grill-with-docs` and `pm-to-issues` added to the PM's skill index (previously
  reachable from the routing table but absent from the agent)
- `docs/guide/AGENTS.md` rewritten for the 6-agent roster; `troubleshooting.md` de-v1'd
- `qa-triage` gains severity floors so a rare-but-catastrophic security bug can't score P2

---

## [2.4.0] — 2026-08-25

**The speckit collapse.** The 9-skill speckit chain + 2 guard skills folded into the 4 skills
that orchestrated them. 35 → 24 skills; ~33KB of chained skill-hopping becomes one 8.9KB
self-contained pipeline.

### Changed
- **pm-epic-writing** absorbs speckit-specify, speckit-git-feature, speckit-clarify +
  pm-clarify-guard, speckit-analyze + pm-analyze-split — the full discovery pipeline inline:
  spec format, business-level question filter, gap analysis with the client/dev finding split.
  Upstream spec-kit boilerplate (extension-hook protocols, $ARGUMENTS blocks, orphaned /slash
  references) dropped entirely
- **dev-feature-plan** absorbs speckit-git-validate, speckit-plan, speckit-tasks — branch
  validation, impl-plan format, and the task-checklist format inline
- **pm-to-issues** absorbs speckit-taskstoissues — one skill for both sources (tasks.md or
  spec slicing), with the GitHub-remote-only safety gate and issue-number write-back
- **pm-constitution-sync** absorbs speckit-constitution — create + sync in one skill
- All `.specify/` output paths unchanged — scaffolded projects and existing specs unaffected

---

## [2.3.0] — 2026-08-25

**Six agents, skills that actually trigger.**

### Changed
- **Agent roster 8 → 6** — web-publisher folded into the developer (an agent forbidden from
  writing code that existed to call the developer was ceremony, not a colleague); email-marketer
  folded into the writer with its hard rules (draft-only, unsubscribe, opt-in, no dupes) intact.
  Delegation blocks, routing rules, scaffold, and docs updated
- **Trigger-phrase pass on 17 operator-facing skills** — 25 of 35 descriptions had no "use when"
  language, so skills never auto-fired (a direct cause of "doesn't work great with the models").
  Pipeline-internal skills (speckit chain, guards) correctly keep their called-within descriptions
- web-publisher-publish rewritten developer-owned (no delegation ceremony); email-marketer-nurture
  writer-owned

### Fixed
- designer-image-generation pinned `gemini-2.0-flash-preview-image-generation` — a dead early-2025
  preview model; now instructs resolving the current image-capable model at run time
- designer-image-generation read `images.md` while the writer produces `image-prompts.md` — the
  two halves of the content pipeline disagreed on the handoff filename

---

## [2.2.0] — 2026-08-25

**The skill cut.** Audit of all 62 workflow skills (dependency graph + staleness + redundancy
vs current models) → 35 survive. `/il-project` installs roughly half of what it used to.

### Removed
- **11 orphans** nothing referenced: create-agent, create-local-routine, create-remote-routine,
  github-flow, global-caveman, pm-contribution-sync, pm-hub-report, seo-audit,
  speckit-git-commit, speckit-git-remote, speckit-implement (~110KB, frozen since May–June)
- **15 "teach the model to think" skills** current models make redundant (and that degrade
  them): the dev-* soft belt (brainstorm, karpathy, zoom-out, grill, multi-agent, prototype,
  planning, handoff, improve-arch, diagnose, github-hygiene, qa-delegation) and
  qa-best-practices / qa-planning / qa-documentation. Their few real rules are folded into
  the developer/qa agent files as short "Working style" sections
- **The autonomous cron rhythm** (decided dead): .claude/scheduled-tasks/ (11 schedule defs),
  pm-standup, the scaffold's standup/ tree, and the team-hours scripts

### Changed
- pm-epic-writing routes straight to dev-feature-plan (dev-planning removed)
- agent-routing rows for removed skills keep their trigger → agent mapping
- Survivors: content pipeline (writer/designer/publisher/email ×9), PM discovery pipeline
  (×9 incl. speckit chain ×9), dev-feature-plan + dev-tdd + plan-protocol, devops ×4, qa-triage

---

## [2.1.0] — 2026-08-25

### Changed
- **Telemetry split.** All effort telemetry (il_telemetry hooks, consent flow) and the
  v1 residue cleanup (migrate_v1.py + manifest + tests) moved to the private
  `talentedgeai/edge8-telemetry` plugin. This public repo is now purely the product:
  2 skills, no hooks, no background behavior, no company internals
- `il-doctor` slimmed to a product setup check (prerequisites, repo context, scaffolded
  project layout) and updated to use `${CLAUDE_PLUGIN_ROOT}` in all commands

### Removed
- `plugin/hooks/` entirely; the `hooks` key in plugin.json
- `docs/assessments/` (internal effort-measurement methodology + self-audits) and
  `docs/superpowers/` (internal feature specs) — moved to the private repo.
  Note: this repo has always been public, so these remain in public git history;
  removal is about discoverability, not secrecy

---

## [2.0.0] — 2026-08-25

**The bare-minimum release.** One repo, one plugin, nothing global. Addresses the two
problems from client review: v1 installed far too much (95 skills + 8 agents + hooks +
a Bash(*) permission grant, all user-global via cp -R), and the prompts had drifted
behind current models.

### Added
- **v2 plugin shipped from this repo** — `.claude-plugin/` marketplace + `plugin/` payload;
  hooks run via `${CLAUDE_PLUGIN_ROOT}` (v1's hooks.json pointed at `~/.claude/hooks/*`, so
  plugin updates never took effect without a manual copy step)
- **`/il-doctor`** — health check + telemetry consent + v1 residue report (replaces
  `infiniteleverage-validate` and the patch health-check)
- **`migrate_v1.py`** — one-time, hash-verified cleanup of v1's global installs. Removes only
  byte-exact copies of files v1 shipped (manifest generated from the full git history of both
  v1 repos); modified files and symlinks are reported, never deleted. Also removes the v1
  `Bash(*)` grant, `acceptEdits` default, and stale v1 hook registrations from settings files
- **Telemetry consent gate** — `il_telemetry.consent`; every entrypoint (stop/flush/scan) is
  opt-in. No consent → no capture, no delivery, no network calls
- **Registration cache TTL (7d, both directions)** — v1 cached only negatives, permanently:
  a repo registered after first probe was silenced forever. Positives are now cached too, so
  no per-session probes
- **API-first delivery** — records POST to the tracker's `/api/telemetry/ingest` when live,
  falling back to the v1 git-append path meanwhile
- **CI** — pytest suite (48 tests incl. migration safety) runs on Python 3.9 and 3.12

### Changed
- **`infiniteleverage-project` → `il-project` (3.0.0)** — no more machine-init prerequisite;
  installs agents + skills into the project's `.claude/` only
- **All 8 agents rewritten for current models** — 37KB → 17KB; boilerplate deduplicated,
  dated "research practitioners before acting" crutches dropped, contradictions removed;
  every unique hard rule preserved
- `VERSION` bumped to 2.0.0 (kept so v1 machines see the update nag one last time)

### Fixed
- **Python 3.9 import failure** — v1's `X | None` annotations crashed the whole telemetry
  package on macOS system python; the `2>/dev/null || true` hooks swallowed it, so v1
  telemetry silently captured nothing on those machines. All modules now carry
  `from __future__ import annotations`

### Removed
- `infiniteleverage-init` / `-patch` / `-onboard` and all global `cp -R` machinery — plugin
  marketplace handles distribution and updates
- `setup-permissions.py` — **never again does any installer write `Bash(*)` or change
  `defaultMode`**
- `pre-bash` / `prompt-submit` hooks (keyword-regex routing hints degrade current models;
  guardrails are a per-project choice via `devops-git-guardrails`)
- `session-start` 4-stage hook (version-check curl, usage briefing, nag lines) and
  `usage-context.py` — no more network calls or transcript scans on session start
- `scaffold-*` skill pack (10), `use-dev-team`/`use-marketing-team`, `infiniteleverage-help`,
  `session-ingest`, lark rules, `plugin-staging/`, committed release zips, `rebuild-zips` CI,
  `effort_selfreport.py` experiment

---

## [1.8.0] — 2026-07-30

### Added
- **plan-protocol skill** — installs, upgrades and diagnoses the Plan Protocol in any repository: a plan registry, a blast-radius guard that fails any change outside a plan's declared `touches`, and a committed pre-push hook. Answers the "20 people and 4 agent runtimes on one machine" problem, where undeclared mega-PRs and semantic (not textual) conflicts are the real failure modes
- **`assets/plan.mjs`** — the engine, as a single dependency-free file (`node:` builtins only). No `tsx`, no build step, no `npm install`, and **no `package.json` required anywhere** — so it installs into a Rails, Django or static client project as readily as a Next one. Verbs: `index · check · sync · guard · submit · premerge · init · doctor`
- **`assets/plan.test.mjs`** — 30 tests on `node:test` (builtin), so a project verifies the protocol with plain `node --test` and no test framework
- **`assets/AGENTS-template.md`** — the protocol document, project-agnostic. `init` copies it to the repo root as `AGENTS.md`, the cross-tool standard Codex, Cursor and Windsurf read natively. Copying a fixed asset rather than writing prose per project is what keeps the protocol identical everywhere
- **Per-project policy in `config.json`** — `hotZones`, `exempt`, `plansDir`, `baseRef`, `verifyCmd` and the rest are data, not code. `init` infers hot zones from the tree (migrations dirs, shared component dirs, lockfiles, CI config). Hot zones differ between two Next apps, never mind across stacks, so a generic engine plus per-project policy is the only shape that ports

### Notes
- The skill **installs** enforcement and is never the enforcement itself. Skills only fire in Claude Code; the teeth are a git hook plus the engine, both committed, so they bind every runtime — including ones that never read `CLAUDE.md`
- Two failure modes the skill's `doctor` exists to catch, because both look exactly like working enforcement: git **silently ignores a non-executable hook**, and enforcement is **not retroactive** — `core.hooksPath` is per-clone config while the hook file is per-branch content, so a branch cut before install is unguarded until it merges the base branch

---

## [1.3.1] — 2026-05-21

### Added
- **devops-cicd skill** — generates a GitHub Actions CI pipeline (lint → type-check → test → build) for Next.js + Vercel projects
- **CI workflow** (`.github/workflows/rebuild-zips.yml`) — automatically rebuilds setup-skill zips and publishes a GitHub Release on every push to `main` that touches agents or skills
- **Troubleshooting guide** (`docs/guide/troubleshooting.md`) — plain-English fixes for the most common operator problems
- **Plugin PreToolUse hook** — `plugin-staging/hooks/hooks.json` now registers `pre-bash` and `prompt-submit` hooks via the plugin, so safety guardrails are active on plugin-only installs (not just full init installs)
- **Plugin UserPromptSubmit hook** — `prompt-submit` (agent routing hints) now wired through the plugin

### Changed
- **developer.md** — Skills section reorganised by use case (Planning, Building, Debugging, Wrapping up) and expanded to include all 14 developer skills: `dev-feature-plan`, `dev-brainstorm`, `dev-zoom-out`, `dev-tdd`, `dev-prototype`, `dev-improve-arch`, `dev-diagnose`, `dev-grill`, `dev-handoff` (previously undocumented)
- **developer.md** — "Testing and deployment" section clarified: `npm test` / `npx jest` / `npx playwright test` (headless) are explicitly allowed; only `next dev` / `npm run dev` (dev server) is prohibited
- **developer.md** — Added plain-English "If something goes wrong" section with CI failure, production rollback, and blocked-credential responses
- **qa.md** — Added `qa-triage` to Skills (was missing from the agent shell). Added "What QA can do autonomously" and "What QA flags to a human" sections for clarity
- **devops.md** — Added `devops-setup-pre-commit`, `devops-cicd`, and `devops-git-guardrails` to Skills section
- **devops-ops/SKILL.md** — Added "Production Rollback" section with operator-friendly step-by-step Vercel dashboard instructions. Removed "secret rotation" from escalation triggers (too technical; operators are not expected to know how to do this)
- **writer.md** — Added `marketing-strategist` skill to Skills section. Added "Brand voice" and "Non-English content" guidance sections
- **email-marketer.md** — Added explicit "Hard rules" section: always draft first, unsubscribe link in every email, opted-in only, no duplicates
- **designer.md** — Added "If image generation fails" section with manual fallback instructions (Ideogram, Midjourney, Adobe Firefly) and prompt-save behaviour
- **dev-tdd/SKILL.md** — Added clarification table: running `npm test` is allowed (it is not a dev server); only `next dev` / `npm run dev` is prohibited
- **README.md** — Skills directory listing and agent/skills tables updated to reflect all skills (previously only 5 of 14 developer skills were listed)
- **README.md** — "Updating Agent Templates" section updated to describe CI-based release flow

### Fixed
- TDD hard rule vs. "no localhost server" contradiction — both rules now consistently refer to different things (`npm test` vs `npm run dev`) and are no longer in conflict

---

## [1.3.0] — 2026-05-20

### Added
- `infiniteleverage-help` skill — full skill menu by team
- Personal laptop setup skill (in addition to Mac Mini setup)

### Changed
- Renamed `create-local-task` → `create-local-routine`
- Pre-bash and prompt-submit hooks now installed via `infiniteleverage-init` and `infiniteleverage-onboard`

---

## [1.2.0] — prior

- Hook scripts (`pre-bash`, `prompt-submit`) added to block force-push, `git add .`, and `--no-verify`
- Plugin staging directory added for Claude Team marketplace distribution
- `devops-git-guardrails` skill added

---

## [1.1.0] — prior

- `qa-triage` skill added with P0–P3 scoring and routing
- `dev-diagnose` skill added (6-phase scientific debugging)
- `dev-handoff` skill added (structured HANDOFF.md format)

---

## [1.0.0] — initial release

- 8 agent shells: product-manager, developer, qa, devops, writer, designer, web-publisher, email-marketer
- 21 foundational skills
- 3 bootstrap skills: infiniteleverage-init, infiniteleverage-onboard, infiniteleverage-patch
- Global engineering rules, agent routing rules, Lark optional integration rules
