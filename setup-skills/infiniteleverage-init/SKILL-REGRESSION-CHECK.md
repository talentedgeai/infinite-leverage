# Skill Regression Check — infiniteleverage-init

Read this before editing `SKILL.md` or `PROMPT.md` in this directory. A rewrite must preserve every invariant below. Tick each item in the PR description. CI covers the mechanical half (`scripts/check-contract.py`); the judgment half is yours.

## Invariants

1. **One source of truth.** Skill and prompt text exist only in this directory of the canonical repo. The plugin carries no skills. The workshop page renders `PROMPT.md` from `stable`; it never owns a copy. Any edit that reintroduces a second maintained copy anywhere is wrong regardless of its content.

2. **One paste, one session.** The setup is a single prompt run in one Code-tab session (or the cloud track from a browser). No step reintroduces a second tab, a second parallel session, or a "now switch to..." handoff.

3. **The triage forks are present and ordered:** surface (can commands run), machine (Mac / Windows own / Windows corporate / below floor), history (clean / half-finished / working-reuse / fresh-alongside / Mode B). Windows own means Ubuntu via WSL2; native Windows is never offered as a choice; corporate means cloud track after a reachability check, never a local attempt.

4. **Every gate has three parts:** numbered clicks, a one-sentence why (cannot vs should-not kept distinct), and a verify command Claude runs after "done". No gate trusts "done" without its check.

5. **The autonomy contract holds.** After setup Claude can, alone: run SQL with no dashboard, branch/PR/merge, deploy by push and watch it live. Asking the user to paste SQL or click deploy post-setup is defined as a bug in the skill text, and the graduation lap (data lap + ship lap) runs before finalize.

6. **Secrets only in `website/.env.local` and Vercel env.** The catalog fill writes statuses and URLs, never a key value; any catalog line asking for a key gets the "stored in website/.env.local — never written here" sentence.

7. **Nothing is ever deleted.** The strongest action is archiving the project folder by rename in the fresh-alongside fork, with the "nothing was deleted" sentence said to the user. Cloud resources are never touched.

8. **The catalog contract:** Stage F fills every `[pending]` line; Resend and domain lines get "deferred — set up in Build 2" so the Build 1 gate is never blocked by things Build 1 doesn't need. The fill list matches the interview prompt's `[pending]` keys (CI-checked once the interview prompt lives in this repo).

9. **Reuse is verification, not a parallel procedure.** Every stage ends in a verify; resume and reuse both work by re-running triage and continuing from the first failing check. Editing a stage means keeping its verify meaningful.

10. **Windows resume-after-reboot survives.** Gate W2 tells the user, before the restart, to paste the same prompt again; triage must find the half-finished state afterward. Don't break this by making any pre-reboot step unverifiable.

11. **Consumers pin `stable`.** Every runtime URL in skill and prompt points at the `stable` branch, never `main`, never a hard tag.

12. **Deploy discipline unchanged:** deploys only via `git push`; the Vercel CLI stays read-only; no step introduces `vercel deploy`.

## Before merging

- [ ] All 12 invariants held (diff the whole file, not just your section)
- [ ] `scripts/check-contract.py` passes
- [ ] References touched by this change updated in the same PR (`os-detection.md`, `windows-setup.md`, `cloud-track-codespaces.md`, `phase2-prompts.md`)
- [ ] Release notes written in plain English (they become the session-start advisory text)
- [ ] For major changes: a clean-machine run on macOS, and the Windows scenario if the change touches gates W1–W3
