# Personal Laptop — Phase 1: Manual Steps

All steps performed by the client in a browser or terminal. Dave guides; client acts. End with the live project running locally.

---

## 1 — Check and install Chrome

```bash
ls /Applications/Google\ Chrome.app 2>/dev/null && echo "✅ Chrome" || echo "❌ Missing"
```

If missing: download from `chrome.google.com` and install.

---

## 2 — Check and install Homebrew

```bash
brew --version 2>/dev/null && echo "✅ Homebrew" || echo "❌ Missing"
```

If missing — press `Cmd+Space`, type `Terminal`, press Enter. Then run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
When it finishes, **follow the PATH instructions it prints** — they look like two lines starting with `echo` and `eval`. Copy and run both. Then reopen Terminal and run `brew --version` to confirm.

---

## 3 — Check and install git, gh CLI, Node

```bash
git --version 2>/dev/null && echo "✅ git" || brew install git
gh --version 2>/dev/null && echo "✅ gh" || brew install gh
node --version 2>/dev/null && echo "✅ node" || brew install node
```

---

## 4 — Authenticate GitHub CLI

```bash
gh auth login
```

- Where: `GitHub.com`
- Protocol: `HTTPS`
- Authenticate: Login with browser

Log in as the operator account (`{firstname}@{clientdomain}.com`). Back to Terminal when done.

```bash
gh auth status  # confirm operator account shown
```

---

## 5 — Install Claude Code Desktop + CLI

**Claude Code Desktop** (the app): download from `claude.ai/download` → install → sign in with the operator Claude Pro account.

**Claude Code CLI** (the terminal command — required for automation):
```bash
npm install -g @anthropic-ai/claude-code
claude --version

# Authenticate CLI (opens browser)
claude
# Complete OAuth with the same operator Claude Pro account
# Type /exit when done
```

Both are needed: Desktop for interactive sessions, CLI for scheduled tasks and scripts.

---

## 6 — Install and authenticate Vercel CLI

```bash
vercel --version 2>/dev/null || npm install -g vercel
vercel login  # authenticate with operator GitHub account
```

---

## 7 — Transfer credentials from Mac Mini

Transfer `{project-slug}-credentials.md` from the Mac Mini to the client laptop securely:
- AirDrop (fastest if both machines are nearby)
- Password manager shared note
- Encrypted message

**Never email it. Never commit it.**

---

## 8 — Quick win: clone both repos, see the live site, run locally

### Clone both repos

```bash
mkdir -p ~/code-projects
cd ~/code-projects

# 1. Clone the website project
gh repo clone {clientslug}/{project-slug}

# 2. Clone the agents repo (one shared repo for the whole operator)
gh repo clone {clientslug}/{clientslug}-agents
```

Confirm both folders exist:
```bash
ls ~/code-projects/
# Expected: {project-slug}/   {clientslug}-agents/
```

---

### Find and open the live website

```bash
vercel projects ls
```

- If **one project** is listed → that's your site. Copy the URL (`.vercel.app` domain).
- If **multiple projects** are listed → find the one matching the pattern `infiniteleverage-{number}-hello-{client-name}`. Copy that URL.

Open the URL in Chrome. The client sees their live, deployed site — running in the cloud — before touching any local configuration.

> **This is the reward moment.** The site is live. The agents are in GitHub. Everything is real.

---

### Run it locally

```bash
cd ~/code-projects/{project-slug}
npm install --prefix website
npm run dev --prefix website
```

Open `http://localhost:3000` — same site, running locally. Confirm it matches what you saw at the Vercel URL.

```bash
# Stop the server when done
Ctrl+C
```

---

Phase 1 is complete. Claude Code is installed and authenticated. Both repos are cloned. The live site is verified and running locally.

---

## ✅ Phase 1 complete — switch to Claude Code now

Everything above is done. From here, Claude Code takes over.

1. Open **Claude Code Desktop** — it's already installed and signed in
2. Open the project folder: click **"Open Folder"** → select `~/code-projects/{project-slug}`
   Or in Terminal: `cd ~/code-projects/{project-slug} && claude`
3. You're now in Claude Code. Copy and run **Prompt 1** from the Phase 2 guide.

> This is the last step you do in Claude Chat. Everything from here runs in Claude Code.
