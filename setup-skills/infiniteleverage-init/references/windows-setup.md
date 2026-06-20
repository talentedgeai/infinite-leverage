# Windows Setup — Running Infinite Leverage on a Windows PC

This guide is written for macOS, but it works on Windows too. **The one thing to know:** the team's automation uses bash shell scripts and hooks (for effort-tracking and auto-updates) that only run in a Unix-style shell. So on Windows we run everything inside **WSL2** — a free, official Windows feature that gives you an Ubuntu (Linux) shell. Inside WSL2, **every step in this guide works exactly as written.**

> **Do NOT use native Windows / PowerShell for this setup.** Claude Code itself runs on native Windows, but this team relies on bash hooks that don't work there — `chmod` is ignored, `~/.zshrc` doesn't exist, and the `session-start` / `install-hooks.sh` hooks (effort tracking + auto-update notices) silently fail. WSL2 avoids all of that. (Source: Claude Code hooks docs — bash hooks require a Unix shell; native Windows falls back to PowerShell.)

---

## Step W1 — Turn on WSL2 (one-time, ~10 min)

1. Click **Start**, type **PowerShell**, right-click it → **Run as administrator**.
2. Run:
   ```powershell
   wsl --install
   ```
   This installs WSL2 and Ubuntu (the default Linux).
3. **Restart** your PC when prompted.
4. After the reboot an **Ubuntu** window opens by itself. Choose a username and password — this is your Linux login, write it down. (The password won't show as you type — that's normal.)
   - If Ubuntu doesn't open on its own: **Start → type "Ubuntu" → Enter.**
5. You now have a Linux shell. **From here on, run every command from this guide inside this Ubuntu window — not PowerShell.**

> Requires Windows 10 (version 2004+) or Windows 11. If `wsl --install` is "not recognized," update Windows first (Settings → Windows Update), then retry.

---

## Step W2 — Install the Claude Desktop app (for the Chat tab)

- Download the Windows app from **https://claude.com/download**, install it, and sign in with your Claude Pro account.
- You'll use its **Chat** tab for the account-setup phase, exactly like macOS.

---

## Step W3 — Install Claude Code inside Ubuntu (WSL)

In the **Ubuntu** window, install the Claude Code CLI:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

(Alternative, after Node is installed in Phase 2: `npm install -g @anthropic-ai/claude-code`.)

Verify, then sign in on first run:

```bash
claude --version
```

Run the Phase 2 prompts from this **Ubuntu** shell.

---

## Then follow the normal guide — everything is identical in WSL

Because WSL gives you a real Linux shell, the rest of `infiniteleverage-init` works unchanged. The only translations:

| In this guide (macOS) | On Windows (do this instead) |
|---|---|
| "Open Terminal" / `Cmd + Space` → Terminal | Open the **Ubuntu** app (WSL) |
| Drag the Claude app into `/Applications` | Run the installer from https://claude.com/download |
| Homebrew install (Phase 1, Step 8) | **Same command** — Homebrew runs on Linux. The installer prints the PATH lines to add; they'll point to `~/.bashrc` and `/home/linuxbrew/.linuxbrew/...` instead of the Mac paths. Just follow exactly what it prints, as the guide already says. |
| `~/.zprofile` / `~/.zshrc` | `~/.bashrc` (the Homebrew installer tells you the exact line) |
| `brew install gh node jq ffmpeg`, `chmod +x`, the session hooks, `/plugin`, `claude plugin marketplace add …` | **All work verbatim** in WSL — no changes |

### Working with your files
- Your project lives inside WSL at `~/code-projects/...` (same as macOS).
- To open WSL files in Windows Explorer, run this from the Ubuntu shell: `explorer.exe .`
- Keep projects inside the Linux home (`~`), **not** the Windows `C:` drive — it's much faster.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `wsl --install` not recognized | Update Windows (Settings → Windows Update), reboot, retry in an **admin** PowerShell. |
| Ubuntu window never appeared | Start → "Ubuntu" → Enter. First launch sets your username/password. |
| `brew: command not found` after install | Close and reopen the Ubuntu window, then run the `eval "$(... shellenv)"` line the installer printed. |
| `claude` not found after install | Close/reopen Ubuntu (PATH refresh), or re-run the install command. |
| Everything is slow | Make sure your project folder is under `~` (Linux side), not `/mnt/c/...` (Windows drive). |

---

## If you truly cannot use WSL2

Native Windows is **not supported for this setup** because the bash hooks won't run (you'd lose effort tracking and auto-update notices). If WSL2 is blocked on your machine (e.g. corporate policy), stop and contact the operator — the hooks need a PowerShell-compatible adaptation first. Do not proceed on native Windows expecting the full team experience.
