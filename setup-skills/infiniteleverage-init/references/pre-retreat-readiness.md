# Pre-Retreat Readiness — Catch Setup Problems Before the Room

The retreat's energy stays high when setup "just works." The way to get there is to find the broken machines **before** the day, not during it. This is mostly process the operator runs ahead of time; the skill supports it via the Smart-Start scan.

> **Scope note:** This is the *registration prework* approach (Quan/Khoa). We do **not** pre-create or own clients' GitHub/Vercel/Resend accounts — each person owns their own. The FunCAPTCHA notes below are troubleshooting for *their* signup, not an account-pooling scheme.

---

## 1 — Capture machine type at registration

Add these fields to the retreat registration form so sub-floor machines are flagged early:

- **Operating system + version** (e.g. "macOS 14", "Windows 11", "Windows 10")
- **Approximate machine age / model** (catches the "2018 Windows machine" Quan flagged)
- **Can you install software on this machine?** (corporate-locked laptops can't enable WSL2)

Cross-check answers against the floors in `os-detection.md`. Anything below floor or locked-down → plan a **loaner** or route to the **cloud track** (`cloud-track-codespaces.md`) *before* the day.

---

## 2 — Optional prework (know where people get stuck)

Send attendees the first, safe slice of setup to attempt on their own beforehand:

1. Confirm OS/shell (run the Step 1 snippet from `os-detection.md`).
2. Create the three core accounts: **GitHub, Vercel, Supabase**.
3. Install **git + the package manager** (Homebrew / WSL2).

Then have them paste back the **Smart-Start scan** output (the prompt in the init SKILL.md). As Quan put it: *"they probably won't be able to set it up themselves, but we'll at least know where they're stuck."* You walk in knowing each person's starting state.

A small **prize for anyone who completes prework** drives participation (Quan's suggestion).

---

## 3 — GitHub signup friction (FunCAPTCHA / Arkose) — troubleshooting only

New GitHub accounts sometimes hit GitHub's Arkose Labs (FunCAPTCHA) puzzle wall. This is an IP/risk-score issue, not the user's fault. To lower the risk score:

- **Sign up on a mobile device over cellular** (different IP reputation) — often skips the hard puzzle entirely.
- **Use "Continue with Google"** social sign-up instead of typing the email manually — inherits the Google account's trust rating. Don't hand-type the email on the first screen.
- Avoid mass-signups from the same venue IP in a short window (that's what trips the score — a known retreat-day problem).

These are workarounds for the attendee creating *their own* account. We do not register accounts on their behalf.

---

## 4 — Loaner machines

Keep a couple of known-good machines (or invest in a few, per Quan's note) for attendees whose hardware fails the floor and who can't use the cloud track. Pre-install Track A on loaners so they're retreat-ready.

---

## Readiness checklist (operator, day before)

- [ ] Every registrant's OS/version checked against `os-detection.md` floors
- [ ] Sub-floor / locked machines assigned a loaner or cloud-track slot
- [ ] Prework instructions sent; Smart-Start outputs collected where possible
- [ ] Loaners pre-loaded with Track A and tested
- [ ] Cloud-track (`il-workspace`) link confirmed working that week (it's experimental)
- [ ] Paid Claude Code subs confirmed for anyone going cloud-track
</content>
