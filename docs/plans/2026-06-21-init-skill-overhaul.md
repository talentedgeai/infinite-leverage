# Init Skill Overhaul — Smoother Setup, OS-Robust, Onboard Merged

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Treat each Workstream below as an independently shippable PR.

**Goal:** Make first-time setup the smooth, high-energy part of the retreat (it is currently the one rough edge). Fold `infiniteleverage-onboard` into `infiniteleverage-init`, harden OS detection, reorder phases so the shortest path to a first working project comes before the full agent-team scaffold, defer credential steps that block momentum, and add an experimental cloud (Codespaces) track for old/unsupported machines.

**Why (source — "Infinite Leverage" Lark group, Jun 20–21 retreat debrief):**
- Quan: *"if we can figure out a way to smooth out tech stack setup we'll just be cruising on high energy the whole time."*
- Trac: init skill needs more robust OS detection; the hardest part is users **without Claude Code yet**; text instructions for grabbing keys → ENV files aren't intuitive; Gemini/Resend are asked too early and are redundant for a first project.
- Khoa/Loc: only need **Windows vs macOS + a minimum version floor** — don't over-engineer per-machine.
- Quan/Khoa: capture **machine type at registration**; assign **prework** so we know where people get stuck.
- Yon: built a **GitHub Codespaces** flow (run Claude CLI in a cloud IDE, never touch the user's machine) for old hardware.
- David: removed the `product-manager` agent-routing line from the retreat prompt — attendees don't have global routing rules, so it broke.

**Source of truth:** `infiniteleverage-8-agents-template` → `setup-skills/`. Skills propagate to client machines via the patch skill / SessionStart auto-update and to deployment zips via `scripts/rebuild-zips.sh`.

**Decisions locked (from operator):**
1. **Merge onboard into init.** Init's first question is **not** "Mac Mini or laptop" — it's *"Is this your very first Infinite Leverage setup, or have you done this before and are now setting up another machine?"* The real fork is **whether the shared infrastructure (accounts, repos, live site) already exists**, not the hardware.
2. **Codespaces = additive Track B**, marked experimental. Local install stays Track A. Does not block the core rework.
3. **Registration prework, not pre-owned accounts.** Add a machine-type field + optional pre-retreat setup attempt. We do **not** pool/own clients' GitHub/Vercel/Resend accounts.

---

## The two setup modes (replaces init-vs-onboard split)

Init opens with one branch question and routes to one of two modes. Everything shared (Settings Safety, Canonical Source, OS detection, credential collection, agent install, plugin/version stamping) lives once and is referenced by both.

| | **Mode A — First Setup** (was `init`) | **Mode B — Additional Machine** (was `onboard`) |
|---|---|---|
| Precondition | No infra exists yet | Infra exists (accounts, repo, live site) |
| Creates accounts/infra? | Yes (Phase 1 manual) | No — reuses existing |
| First visible win | Live site deployed to Vercel | Existing live site running at `localhost:3000` (quick-win clone) |
| Agents | Build all 8 + schedules + dashboard | Pull all 8 from canonical repo; no schedule re-registration |
| Effort-tracking registration | At end | At end (existing onboard flow) |
| Ends with | HANDOFF.md | first-actions.md pointer |

**Boundary vs patch:** `init` = **stand up** a machine (first time or an additional machine). `patch` = **keep an already-stood-up machine in sync**. Mode B and patch must not blur: Mode B installs from zero on a new machine; patch diffs/updates what's already installed.

---

## Workstream 1 — Merge onboard → init (retire onboard)

**Files:**
- Rewrite `setup-skills/infiniteleverage-init/SKILL.md` to open with the Mode A/B branch question, then route. Keep Mode A as today's two-phase bootstrap; add Mode B section sourced from current onboard SKILL.md (quick-win clone, no infra creation, no schedules, effort-tracking registration block, `first-actions.md`).
- Move onboard-only references into init: `first-actions.md` → `infiniteleverage-init/references/`. Merge the two `phase1-manual.md` / `phase2-prompts.md` pairs (see W2/W3 — they get split by concern anyway).
- Delete `setup-skills/infiniteleverage-onboard/` after content is absorbed.
- Update `CLAUDE.md` (template root) line listing "Bootstrap skills (init, onboard, patch)" → "(init, patch, project)".
- Update `scripts/rebuild-zips.sh` to stop building an onboard zip; ensure init zip carries the merged references.
- Grep the repo for `infiniteleverage-onboard` references (plugin hooks, help skill, project skill, docs) and repoint to init Mode B. **Known callers to fix:** init SKILL.md "Next" line ("run `infiniteleverage-onboard`"), patch health-check skills list, any `/infiniteleverage-onboard` mentions in `infiniteleverage-help`.

**Acceptance:** Searching the repo for `infiniteleverage-onboard` returns only historical/changelog mentions. Init Mode B reproduces every step the old onboard did. `rebuild-zips.sh` runs clean and the init zip contains `first-actions.md`.

---

## Workstream 2 — OS detection + version floors (shared reference)

**Problem:** detection isn't robust; Windows path is a separate doc; the team wants only Win/macOS + a version floor, not per-machine handling.

**Files:**
- New `infiniteleverage-init/references/os-detection.md` — the single OS guide both modes and the patch health-check reference:
  - Detect macOS vs Windows (and confirm WSL2 Ubuntu shell on Windows — bash hooks require it).
  - **Package manager per OS:** macOS → Homebrew; Windows(WSL2) → `apt`; document `winget` only for the host-side Windows app installs (Claude Desktop). Mention `winget` per Trac's note but route real tooling through the Unix shell.
  - **Minimum version floor table** (Khoa/Loc): Node ≥ (pin), git ≥ (pin), macOS ≥ (pin), Ubuntu/WSL ≥ (pin). Anything below the floor → point to Track B (Codespaces, W5) instead of fighting the machine. "Accept some special cases" — don't enumerate every old OS.
  - One detection snippet that prints a plain-English "your machine is supported / borderline / use the cloud track" verdict.
- Fold `infiniteleverage-init/references/windows-setup.md` into `os-detection.md` (or keep it as the deep-dive WSL2 install and link from os-detection). Remove the standalone "On Windows?" section from SKILL.md in favor of a single pointer to `os-detection.md`.
- `infiniteleverage-patch/scripts/health-check.sh` — make OS-aware: don't assume `brew`; check the package manager that matches the detected OS; reuse the version-floor table.

**Acceptance:** A Windows-WSL2 user and a macOS user both run the same Smart-Start detection and get a correct supported/borderline verdict. health-check.sh passes on both OSes without brew-on-Windows false negatives.

---

## Workstream 3 — Reorder phases: Claude Code first, shortest path to first project, defer credentials

**Problem (Trac):** hardest part is users *without Claude Code yet*; static "grab keys, paste into ENV" instructions aren't intuitive; Gemini + Resend are asked too early; Resend is friction (people want their own domain, not a practice one). Redundant steps kill momentum before the first win.

**New Phase 1 (manual, minimal) — Mode A:**
1. OS detection (W2).
2. Install Git + package manager (Homebrew / WSL2+apt) — clear Mac vs Windows branch.
3. **Install + auth Claude Code CLI early** — it's the engine that runs everything else. Once it's in, Claude Code itself guides the rest interactively instead of relying on static text.
4. Core accounts only: **GitHub + Vercel + Supabase** (+ Git identity for effort tracking).
5. **Defer Gemini and Resend** out of the first-project critical path — collected later, only when the feature that needs them is built. Resend especially: don't make people buy/verify a throwaday domain just to proceed.

**New Phase 2 (Claude Code) — split dependency setup from agent setup:**
- **2a — Dependencies & first project (shortest path to a win):** install remaining CLIs, scaffold + deploy a minimal first project, get HTTP 200 / `localhost:3000`. **This is the dopamine hit — reach it before scaffolding the 8-agent team.**
- **2b — Agent team & schedules:** all 8 agents, dashboard, CronCreate/RemoteTrigger routines, HANDOFF.md.

**Interactive credential collection (replaces static ENV instructions):**
- New `infiniteleverage-init/scripts/collect-credentials.(sh|py)` — prompts for each key **one at a time, only when first needed**, validates non-empty/format, writes `~/.claude/.env` and project `.env.local` without clobbering existing keys (reuse the merge discipline already in `setup-permissions.py`). Gemini/Resend prompts live in 2b/feature-time, not Phase 1.
- Update `references/env-template.md` to mark Gemini/Resend as **deferred / optional-at-start** and document the just-in-time collection order.

**Acceptance:** A first-time user reaches a live deployed page (Mode A) or `localhost:3000` (Mode B) **before** any agent scaffolding and **without** having touched Gemini or Resend. No step asks for a credential the current step doesn't use.

---

## Workstream 4 — Fix the distribution prompt (David's note)

**Files:** `references/phase2-prompts.md` (init) and any retreat/blueprint prompt the template ships.
- Remove the `product-manager` agent-routing line ("Route this whole flow through the product-manager agent per my global agent-routing rules") — attendees don't have global routing rules on a fresh machine, so it references an agent that doesn't exist yet and breaks. Inline the PM-interview behavior directly instead.
- Audit every Phase-2 prompt for other assumptions of pre-existing global config (routing rules, named agents, skills) that won't exist on a virgin machine. Each prompt must be self-contained for a zero-state machine.

**Acceptance:** Every shipped prompt runs verbatim on a machine with an empty `~/.claude/` and never references an agent/skill/rule that isn't installed by an earlier step in the same sequence.

---

## Workstream 5 — Track B: Codespaces cloud path (additive, experimental)

**Files:** New `infiniteleverage-init/references/cloud-track-codespaces.md`, linked from the OS-detection "borderline / unsupported" verdict and from SKILL.md as an explicit alternative.
- Document Yon's flow: open `codespaces.new/<org>/il-workspace?quickstart=1` → sign in with GitHub (new or existing) → open the Claude side panel (orange icon, top-right) → auth Claude Code (paid sub required; **free Claude won't work on CLI**) → run init inside the cloud IDE → create the GitHub repo in the cloud, download to the machine after the retreat.
- Mark **EXPERIMENTAL — verify before relying on it at a retreat.** Capture the open question: which org hosts the `il-workspace` devcontainer, and what's pre-baked into it (CLIs, skills).
- Note constraints: requires a paid Claude Code subscription; the IDE takes minutes to load; repo lives in the cloud until downloaded.

**Acceptance:** A user on a sub-floor machine is routed to Track B and can stand up a repo without local installs. Section is clearly flagged experimental until the team signs off on a tested run.

---

## Workstream 6 — Pre-retreat readiness (registration prework, not pre-owned accounts)

**Scope:** lightweight, mostly process — but anything the skill can support, it should.
- Add guidance (and a checklist the operator can send) for capturing **machine type/OS/version at registration** so sub-floor machines are flagged → routed to Track B or a loaner ahead of time (Quan/Khoa).
- Optional **prework**: attendees attempt Phase 1 (OS detect + core accounts) before the retreat; the Smart-Start scan reports exactly where they're stuck so the retreat starts from a known state (Quan's "we'll at least know where they're stuck").
- Include the GitHub-signup friction notes Yon shared (Arkose/FunCAPTCHA): prefer mobile/cellular signup and **"Continue with Google"** social sign-up — as a troubleshooting aside, **not** an account-pooling scheme. Explicitly do **not** pre-create/own client accounts.

**Acceptance:** A pre-retreat checklist exists; Smart-Start produces a "here's where you are" report a prework attendee can paste back; FunCAPTCHA workarounds are documented as troubleshooting only.

---

## Workstream 7 — Patch skill alignment

The merge and reordering change what patch must keep in sync.
- `health-check.sh`: OS-aware (W2); update skills list (drop `infiniteleverage-onboard`, it's gone); add a check that the merged init references exist; keep telemetry/hook checks intact (see `.claude/rules/hooks-regression-check.md`).
- Phase-2 sync table: ensure renamed/moved references (os-detection, cloud-track, collect-credentials) propagate.
- Confirm the SessionStart auto-update path still covers the restructured skill files.

**Acceptance:** Running `/infiniteleverage-patch` on a current machine reports the new structure correctly and applies the renamed/moved files without false ❌s.

---

## Sequencing & dependencies

```
W2 (OS detection) ─┬─► W3 (phase reorder) ─► W4 (prompt fixes)
                   ├─► W5 (Track B routing depends on floor verdict)
                   └─► W7 (patch reuses floor table)
W1 (merge onboard) ─► W7 (patch skills list)      W6 (process) ── parallel
```
- Land **W2** first (shared foundation). **W1** can run in parallel. **W3** depends on W2. **W4** after W3. **W5/W6** parallel. **W7** last (reflects all structural changes).
- Each workstream = one PR. Keep `.claude/rules/hooks-regression-check.md` green on any health-check/hook edits.

## Out of scope (note, don't build here)
- Pre-owned account pooling + email-transfer flow (explicitly rejected for now).
- Loaner-machine logistics / buying Neos (ops decision, not skill code).
- Charging/pricing changes for future retreats.

## Open questions
1. Exact version floors for Node / git / macOS / Ubuntu — needs a pinned table (W2).
2. Where does the `il-workspace` Codespaces devcontainer live and what's pre-baked (W5)?
3. Interactive credential collector: bash or python? (Lean python — reuse `setup-permissions.py` merge logic.)
4. Does Mode B still need *any* Gemini/Resend prompt, or inherit them entirely from the already-configured Mac Mini?
