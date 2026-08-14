# Phase 1 — Manual Steps (Mode A, minimal)

All steps are performed by the operator in a browser or terminal. Claude narrates; human acts. **Phase 1 is intentionally minimal:** get Claude Code **Desktop** ready and create the three core accounts. **No API keys are collected here** — all environment variables are collected in Phase 2, where Claude grabs most of them itself. The Claude **CLI is not needed** in Phase 1 (Phase 2 runs inside Desktop); it's an optional install at the very end of the skill.

> **Windows:** do everything inside the **Ubuntu (WSL2)** shell, not PowerShell — the bash hooks need a Unix shell. See `references/os-detection.md` (and `references/windows-setup.md` for the one-time WSL2 turn-on).

---

## 1 — Check the machine

Run the detection snippet in `references/os-detection.md` (Step 1) and get the verdict:

- ✅ **Supported** → continue.
- ⚠️ **Borderline** → upgrade the one named tool (e.g. Node below the floor), then continue.
- ☁️ **Below floor / can't run WSL2** → stop the local install and use `references/cloud-track-codespaces.md` (Track B).

## 2 — Install Git + package manager

**macOS** — install Homebrew, then git:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Follow the PATH lines the installer prints at the end (the eval "$(... shellenv)" line), then:
brew install git
git --version    # confirm
```

**Windows (WSL2 Ubuntu)** — git usually ships with Ubuntu; if missing:

```bash
sudo apt update && sudo apt install -y git
git --version
```

(Homebrew-on-Linux also works in WSL2 if you prefer it — `references/os-detection.md` covers both.)

If `brew`/`git` says "command not found" after install, close and reopen the terminal (PATH refresh) and re-run the `eval` line Homebrew printed.

## 3 — Install Claude Code Desktop (this is where Phase 2 runs)

- **macOS:** go to `claude.ai/download` in Chrome → download the Mac app → drag it to `/Applications` → open it → sign in with the operator **Claude Pro** account.
- **Windows:** download from `claude.com/download` and run the installer (no "drag to /Applications"). Sign in with Claude Pro.

Leave Desktop open — you'll paste the Phase 2 prompts into it. **You do not need the `claude` terminal CLI yet.**

## 4 — Create the three core accounts (and git identity)

Create these under the operator email. **Only these three.**

- **GitHub:** `github.com` → Sign up → username `{clientslug}` → verify email. (If GitHub's CAPTCHA blocks signup, see the FunCAPTCHA workarounds in `references/pre-retreat-readiness.md`.)
- **Vercel:** `vercel.com` → **Sign up with GitHub** (links both accounts). **[P6]**
- **Supabase:** `supabase.com` → Sign up → create project: name `{project-slug}`, region closest to the client's users → **save the database password**. **[P7]**

Then set the git identity (required so effort tracking can attribute your work):

```bash
gh auth login          # GitHub.com → HTTPS → Login with browser
gh auth status         # confirm authenticated
git config --global user.email "{firstname}@{clientdomain}.com"
```

> **Deferred to Phase 2 (do NOT do now):** the Supabase API keys themselves. Phase 2 collects them — Claude retrieves most automatically via the Claude-in-Chrome extension / computer-use, asking you only when it hits a login wall, 2FA, CAPTCHA, or billing screen.

---

## ✅ Phase 1 complete — switch to Claude Code Desktop

Phase 1 is done when:

- `references/os-detection.md` verdict is ✅ (or you're on the cloud track)
- Claude Code **Desktop** is installed and signed in
- `git --version` works; `gh auth status` is authenticated; `git config user.email` is set
- GitHub, Vercel, and Supabase accounts exist

From here, Claude Code takes over. Open **Claude Code Desktop**, then follow **`references/phase2-prompts.md`** — it starts by having you open a **second session** so the autonomous **2b** track and the interactive **2a** track run in parallel.

> This is the last step you do in Claude Chat. Everything from here runs in Claude Code Desktop.
</content>
