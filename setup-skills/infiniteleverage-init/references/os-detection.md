# OS Detection & Version Floors — Read This First

The single source for "is this machine supported, and how do I install tools on it?" Both setup modes and the patch health-check reference this file. The rule the team agreed on (Khoa/Loc): **we only branch on Windows vs macOS plus a minimum version floor — we do not handle every machine variant.** Below the floor → use the cloud track (`cloud-track-codespaces.md`), don't fight the machine.

---

## Step 1 — Detect the OS and shell

Run this in the terminal (macOS Terminal, or the **Ubuntu (WSL)** window on Windows — never PowerShell):

```bash
bash -c '
OS="unknown"; SHELL_OK="no"; PKG="none"
case "$(uname -s)" in
  Darwin) OS="macOS"; PKG="brew" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then OS="Windows (WSL2 Ubuntu)"; else OS="Linux"; fi
    PKG="apt" ;;
esac
# bash hooks (effort tracking + auto-update) require a Unix shell
[ -n "$BASH_VERSION" ] && SHELL_OK="yes"
echo "OS:            $OS"
echo "Unix shell:    $SHELL_OK   (required — native Windows/PowerShell is NOT supported)"
echo "Package mgr:   $PKG"
echo "macOS ver:     $(sw_vers -productVersion 2>/dev/null || echo n/a)"
echo "node:          $(node --version 2>/dev/null || echo MISSING)"
echo "git:           $(git --version 2>/dev/null | awk "{print \$3}" || echo MISSING)"
echo "claude:        $(claude --version 2>/dev/null || echo MISSING)"
'
```

**If `OS` is `Windows (WSL2 Ubuntu)`** → good, you're in the right shell. Continue.
**If you are on Windows but NOT in WSL2** (PowerShell/CMD) → stop. Open the **Ubuntu (WSL)** window first. See `windows-setup.md` to turn on WSL2 (one-time, ~10 min). The bash hooks silently fail on native Windows.

---

## Step 2 — Package manager per OS

| OS | Package manager for CLI tools | Notes |
|---|---|---|
| **macOS** | **Homebrew** (`brew install …`) | Install via the official one-liner if missing. |
| **Windows (WSL2 Ubuntu)** | **`apt`** inside Ubuntu (`sudo apt install …`); Homebrew-on-Linux also works | `winget` is **only** for the host-side Windows apps (the Claude Desktop installer). All project tooling runs through the Unix shell, never `winget`. |
| **Linux** | `apt` (or the distro's manager) | Treated like the WSL2 path. |

Do **not** route real tooling (gh, node, jq, ffmpeg, vercel, claude) through `winget` — they must live in the Unix shell so the hooks see them.

---

## Step 3 — Minimum version floor

> **Confirm these pins with the operator before a retreat — they are the working defaults, not gospel.**

| Tool / OS | Minimum (floor) | Below the floor → |
|---|---|---|
| **Node.js** | **20 LTS** | Install/upgrade via package manager; if the OS can't get Node 20+, use the cloud track |
| **git** | **2.30** | Upgrade via package manager |
| **macOS** | **13 (Ventura)** | Older Macs that can't run Homebrew/modern Node → **cloud track** |
| **Windows** | **10 (build 2004+)** or **11** (for WSL2) | Older Windows can't run WSL2 → **cloud track** |
| **Ubuntu / WSL distro** | **22.04** | Upgrade the WSL distro, or **cloud track** |

The "2018 Windows machine" problem Quan flagged: those usually fail the macOS/Windows-version or Node floor. Catch them with the registration machine-type field (`pre-retreat-readiness.md`) and route to the cloud track *before* the retreat, not during it.

---

## Step 4 — Verdict (say this in plain English)

After Steps 1–3, give the user one of three verdicts:

- ✅ **Supported** — OS at/above floor, Unix shell confirmed, package manager present. → Continue with local setup (Track A).
- ⚠️ **Borderline** — one tool below floor but upgradeable (e.g. Node 18 → install 20). → Upgrade the named tool, then continue Track A.
- ☁️ **Use the cloud track** — OS itself below floor, or WSL2 can't be enabled, or hardware too old to run the stack. → Go to `cloud-track-codespaces.md` (Track B). Don't spend retreat time fighting the machine.

Phrase it for a non-technical user, e.g.:
> "Your Mac is on macOS 12 and this setup needs 13+. Two options: update macOS in System Settings, or skip the install entirely and run everything in the cloud — I can set that up in a couple of minutes. Which do you prefer?"

---

## Translations (macOS guide → WSL)

The rest of the guide is written for macOS. In WSL2 everything works verbatim except:

| Guide says (macOS) | On Windows (WSL2) |
|---|---|
| "Open Terminal" / `Cmd+Space` → Terminal | Open the **Ubuntu** app |
| `brew install …` | `brew install …` (Homebrew-on-Linux) **or** `sudo apt install …` |
| `~/.zprofile` / `~/.zshrc` | `~/.bashrc` (the installer prints the exact line) |
| Drag Claude app to `/Applications` | Run the installer from https://claude.com/download |

Keep projects under the Linux home (`~/code-projects/…`), **not** `/mnt/c/...` — it's far faster. Full WSL2 turn-on walkthrough: `windows-setup.md`.
</content>
