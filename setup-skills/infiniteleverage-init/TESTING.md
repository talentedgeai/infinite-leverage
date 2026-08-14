# Testing — infiniteleverage-init

How to verify the setup skill and prompt. Three sources of truth, cheapest first: CI statics on every PR, the onboarding fleet in the field, and a small crash rig for what onboarding can't ethically do.

## The onboarding fleet (primary field testing)

Every engineer onboarding IS a test run of the current release, and it's the cleanest one possible: real accounts that stay in use, real machines, real networks, and a stack the engineer keeps. Rules that make it work as testing rather than anecdote:

1. **Engineers onboard with the real prompt, verbatim**, from the workshop page or PROMPT.md at `stable`. No shortcuts, no engineer-only path — the moment engineers set up differently from attendees, the field test stops testing the product.
2. **The run reports itself.** Stage F files a `setup-report` issue on the canonical repo automatically (skill version, OS, triage state, per-stage timing, gate outcomes, verify failures, hand-fixes). The engineer's only duty is honesty about hand-fixes: anything done by hand that the guide didn't ask for is a bug in the skill, and the existing rule applies — file it, same day, or the fix is lost.
3. **Triage the reports on a cadence.** Review open `setup-report` issues weekly and before every release; fixes land as PRs; the release notes name what field reports they close. Version-over-version improvement is measured, not felt: compare stage timings and hand-fix counts across versions from the reports.
4. **Both modes get covered free.** New engineers on client projects exercise Mode A; engineers adding a laptop exercise Mode B.

One honest limit: engineers are the wrong proxy for non-technical attendees. They don't hesitate where attendees will, and they instinctively fix what Claude fumbles, which hides bugs — that's what the hand-fix rule and the pre-retreat dress rehearsal (bottom of this file) exist to counter.

## The crash rig (what onboarding can't do)

Onboarding runs can't be reset, re-run into forks, or asked to lie at gates. Keep a minimal synthetic kit for exactly the runs marked **[rig]** in the sequence below: the fresh-alongside archive fork, the corporate simulations, the negative gates, and the Windows reboot when no onboarding covers it. Never run destructive or dishonest tests on a real engineer's accounts.

The flow creates accounts, repos, projects, and deployments. The rig never uses real operator accounts: it pollutes them, and it silently skips the account-creation gates a real attendee hits.

| Asset | What to create | Notes |
|---|---|---|
| Test inbox | One dedicated mailbox, e.g. a free Gmail | Every account below verifies against it. Don't use plus-addressing on edge8.ai — it bounces (Lark Mail). |
| Test GitHub account | New account on the test inbox | The flow will create and delete repos here. Real accounts never get test repos. |
| Test Vercel account | Sign up with the test GitHub | Free tier is fine. |
| Test Supabase account | Sign up with the test GitHub | Free tier allows two projects, so the reset script below is not optional — a full org fails the next run confusingly. |
| Claude account | Reuse a real paid seat | Acceptable: Claude Desktop sign-in is prework, not something the flow provisions. A dedicated test seat is nicer if one exists. Paid is mandatory for the cloud track. |
| Resend account + cheap test domain | Only when testing Build 2 / the ship block | Not needed to verify this skill. |

Keep the test credentials in a password manager entry, not in any repo.

## Test machines

| Machine | How | Reset between runs |
|---|---|---|
| Clean Mac (release runs) | A macOS VM with a "clean" snapshot, or a wiped spare Mac Mini | Restore the snapshot / re-wipe |
| Quick-iteration Mac | A brand-new macOS user account on any Mac | Delete `~/.claude`, `~/code-projects`, CLI auths (`gh auth logout`, `vercel logout`). **Caveat:** Homebrew is machine-global, so this machine is clean for `~/.claude`, folders, and auth, but NOT for tools — Stage A's install path needs the VM to be truly tested. |
| Windows own-machine | A physical PC with WSL2 not yet enabled (VMs need nested virtualization and behave differently) | `wsl --unregister Ubuntu`, disable the WSL feature, delete the test folders |
| Corporate machine | Simulated, two ways (below) — real group policy isn't required | — |
| Chat-only surface | claude.ai in a browser on any machine | — |

## Reset script (after every run, test accounts only)

```bash
# GitHub: delete repos the run created (test account only — never run signed in as a real account)
gh repo list --limit 20 --json name -q '.[].name' | while read r; do gh repo delete "$r" --yes; done
# Vercel: remove test projects
vercel project ls; vercel project rm <name> --yes
# Supabase: delete the run's project in the dashboard (or via API) — free tier caps at two
```

Guard: before running, `gh auth status` must show the test account. If it shows anything else, stop.

## The run sequence

Record for every run: the transcript, a timing sheet per stage, and an intervention tally (every time the tester hesitated or a watching engineer had to speak). Every intervention becomes an issue.

Each run is tagged with its channel: **[fleet]** happens naturally through engineer onboardings, **[rig]** needs the throwaway kit, **[both]** benefits from each.

**Run 0 — static.** `scripts/check-contract.py` green; read the diff against `SKILL-REGRESSION-CHECK.md`, all 12 invariants ticked.

**Run 1 — Mac, clean, full flow. [both]** Fleet: every new engineer's first machine is this run, self-reported. Rig: before a major release, once on the clean VM, played as a non-technical attendee. Pass when: every gate presented with its three parts; the graduation lap passes (scratch migration with no dashboard; PR opened, merged, build watched green, live site updated); the catalog has no `[pending]`; key lines say "stored in website/.env.local"; **effort-telemetry rows actually landed** (telemetry is billing — check the outbox/delivery, not just that hooks exist); Block II timing fits the retreat morning.

**Run 2 — reuse. [both]** On the same machine, paste the same prompt again. Pass when: triage reports the working stack in plain English, asks the one keep-or-fresh question; on "keep", it verifies and repairs only, reinstalls nothing healthy, and finishes fast.

**Run 3 — fresh alongside. [rig]** Same machine, choose "start fresh". Pass when: the old folder is archived by rename with the "nothing was deleted" sentence, cloud resources untouched, old site still answers, new slug wired end to end.

**Run 4 — resume. [rig]** Restore the snapshot, run, kill the session right after Stage C. Paste the prompt again. Pass when: triage finds the half-finished state and continues at Stage D without redoing A–C.

**Run 5 — Windows gates. [both]** On the PC with WSL2 absent. Pass when: native Windows is never offered; W1–W3 fire with their reasons; the resume instruction is given *before* the reboot; after restarting and re-pasting, the flow continues where it stopped; the rest of the flow runs inside Ubuntu; projects land in the Linux home.

**Run 6 — corporate verdicts. [rig]** Two cheap simulations: (a) answer "company-managed" on any Windows machine — pass when no local install is attempted and the reachability check runs; (b) block github.com in the hosts file — pass when the verdict is the plain "loaner or personal machine" stop, with no workaround attempted.

**Run 7 — chat surface. [rig]** Paste the prompt into claude.ai in a browser. Pass when: Claude recognizes it can't run commands and routes to the cloud track without attempting a single local step. (The full cloud run is blocked until the Codespace template is org-owned — tracked as open decision 2.)

**Run 8 — negative gates. [rig]** At Gates 2, 4, and 5, say "done" without doing the thing. Pass when: every verify catches the lie, and Claude re-presents the gate rather than proceeding.

**Run 9 — update path. [fleet]** On a machine running the previous release (the current production machines qualify): apply `/infiniteleverage-patch` after the release. Pass when: duplicate skills reconciled, every invariant on the hooks regression checklist intact, version stamp bumped, advisory stops firing.

## Cadence

- Every PR: Run 0 (CI).
- Continuously: every engineer onboarding is a fleet run; its `setup-report` issue is triaged weekly and before every release, and release notes name the reports they close.
- Minor release: Runs 0–2, plus whichever run the change touches.
- Major release: Runs 0–9, all of them.
- Before each retreat: the dress rehearsal — one genuinely non-technical person runs all four workshop blocks on a clean machine, an engineer watches silently with a stopwatch. Target: zero interventions on the Mac path.
