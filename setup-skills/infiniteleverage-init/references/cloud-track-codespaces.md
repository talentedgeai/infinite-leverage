# Track B — Cloud Setup via GitHub Codespaces (EXPERIMENTAL)

> ⚠️ **EXPERIMENTAL — verify a full run before relying on this at a retreat.** Built by Yon (Jun 21 2026) to solve the old-hardware / can't-install problem. Track A (local install) remains the default; this is the escape hatch for machines that fail the version floor in `os-detection.md`, or where WSL2 can't be enabled.

## What this is

Run Claude Code in a **cloud IDE** (GitHub Codespaces) — the user's GitHub repo is created and built **in the cloud, without ever touching their machine**. They download everything to the laptop *after* the retreat. No Homebrew, no WSL2, no local Node — just a browser.

## When to use it

- `os-detection.md` returned ☁️ **Use the cloud track** (OS below floor, WSL2 blocked, hardware too old).
- A retreat attendee shows up on a machine you can't get the local stack onto in time.
- You want everyone productive on identical, pre-baked environments.

## Requirements

- A **paid Claude Code subscription** — **free Claude does NOT work on the CLI.** This is the hard prerequisite; confirm it before starting.
- A GitHub account (new "virgin" account is fine, or an existing one).
- A modern browser. That's it.

## Steps

1. Open the workspace template:
   `https://codespaces.new/<org>/il-workspace?quickstart=1`
   *(Yon's test link used `yon-create/il-workspace` — see Open Questions for which org hosts the canonical one.)*
2. **Sign in with GitHub** (new or existing account).
3. Wait for the cloud IDE to load — **it takes a few minutes**, tell the user that up front so they don't bail.
4. Click the **orange Claude icon, top-right** → the Claude side panel opens.
5. **Authenticate Claude Code** in the panel (paid sub required).
6. Run the Infinite Leverage init inside the cloud IDE — it scaffolds and creates the GitHub repo in the cloud.
7. After the retreat, the user **downloads the repo to their machine** (or keeps working in the cloud) once it's set up locally.

## Constraints & caveats

- **Paid Claude Code sub is mandatory** — the single most common failure.
- The repo lives in the cloud until downloaded; effort-tracking hooks behave differently in a Codespace — confirm telemetry still flows before depending on it.
- IDE cold-start is slow (minutes). Set expectations.
- This bypasses the local quick-win (`localhost:3000`) — the "win" here is a live cloud repo, framed accordingly.

## Open questions (resolve before this is non-experimental)

1. **Which org hosts the canonical `il-workspace` devcontainer?** Yon used a personal `yon-create/...`. We need an org-owned, version-pinned template.
2. **What is pre-baked into the devcontainer?** (CLIs, the 8 agents, skills, the init skill itself.) Document it so the in-IDE init doesn't re-install what's already there.
3. **Does effort tracking work inside a Codespace?** The hooks assume a persistent `~/.claude/` + `gh` auth — verify capture/deliver still works, or document the gap.
4. **Account/cost ownership** — whose Codespaces minutes and whose Claude sub are billed during a retreat?

Until 1–3 are answered with a tested run, present Track B as "experimental — works, but we're still hardening it."
</content>
