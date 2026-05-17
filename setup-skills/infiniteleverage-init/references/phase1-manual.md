# Mac Mini — Phase 1: Manual Steps

All steps are performed by the operator in a browser or terminal. Claude narrates; human acts.

---

## 1 — Google Workspace: Add client domain

1. `gmail.com` → log in as `infinite-8.com` master account → grid icon → **Admin Console**
2. **Domains** → **Manage Domains** → **Add a domain** → **Add as a secondary domain**
3. Enter `{clientdomain}.com` → **Continue and verify domain ownership**
4. Copy the displayed TXT record value

## 2 — Vercel DNS: TXT verification + MX

1. Vercel → **Domains** → select client domain → **DNS Records**
2. Add: Type=`TXT`, Name=`@`, Value=the copied TXT record
3. Return to Google Admin Console → **Verify** (usually < 2 min)
4. After verification: in Vercel DNS panel → **Set MX records for Google** → auto-configures

## 3 — Create operator email

1. Google Admin Console → **Users** → **Add new user**
2. Email: `{firstname}@{clientdomain}.com` | set temporary password
3. **Log in once** as operator email → set permanent password

## 4 — Create service accounts (all under operator email)

**GitHub**: `github.com` → Sign up → Username: `{clientslug}` → verify email

**Claude Pro**: `claude.ai` → Sign up with operator email → select **Pro plan**

**Vercel**: `vercel.com` → **Sign up with GitHub** (links both accounts)

**Supabase**: `supabase.com` → Sign up → create project: name=`{project-slug}`, region=closest to client users → **save database password**

## 5 — Generate API keys

**Gemini**:
1. `aistudio.google.com` → log in with operator Google account
2. **Get API key** → **Create API key** → copy → `GEMINI_API_KEY`

**Resend (API key + domain verification)**:
1. `resend.com` → Sign up with operator email
2. **API Keys** → **Create API Key** → name: `{project-slug}-email-marketer` → copy → `RESEND_API_KEY`
3. Resend dashboard → **Domains** → **Add Domain** → enter `{clientdomain}.com`
4. Resend shows DNS records → return to Vercel DNS panel → add each:
   - TXT on `resend._domainkey` — DKIM key
   - MX on `bounce` — bounce tracking
   - TXT on `@` — SPF: add `include:amazonses.com` to existing, or create new
5. Back in Resend → **Verify DNS Records** → wait for green (< 5 min, up to 30 if slow propagation)

**Lark** *(optional — skip if not using Lark for team notifications)*:
1. `open.larksuite.com` → create Bot App for internal notifications
2. Copy: `LARK_APP_ID`, `LARK_APP_SECRET`, webhook URL → `LARK_WEBHOOK_URL`
3. If skipping: leave `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_WEBHOOK_URL` blank in the credentials file — agents will skip notifications silently

**Supabase credentials** (from project dashboard → **Project Settings** → **API**):
- `SUPABASE_URL` — Project URL
- `SUPABASE_ANON_KEY` — anon public
- `SUPABASE_SERVICE_ROLE_KEY` — service_role (keep secret)

## 6 — Save credentials file

Create `{project-slug}-credentials.md` locally — NOT in any repo:

```
# {Project Name} — Operator Credentials

## Operator Identity
Email: {firstname}@{clientdomain}.com
GitHub username: {clientslug}

## API Keys
GEMINI_API_KEY=
RESEND_API_KEY=
RESEND_DOMAIN=
# Lark (optional — leave blank to disable)
LARK_APP_ID=
LARK_APP_SECRET=
LARK_WEBHOOK_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

## GitHub Repositories (created in Phase 2)
{project-slug}
{project-slug}-agents
```

## 7 — Install Claude Code Desktop on Mac Mini

Go to `claude.ai/download` in Chrome → download the Mac app → drag it to `/Applications` → open it → sign in with the operator Claude Pro account.

Once you see the Claude Code interface, leave it open — you'll use it to run Phase 2.

---

## 8 — Install Homebrew and git on Mac Mini

**On the Mac Mini**: press `Cmd + Space`, type `Terminal`, press Enter. A black window with a prompt appears — that's the terminal.

Copy and paste this command exactly, then press Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

The installer will print instructions — **follow whatever it prints at the end** about adding Homebrew to your PATH. It will look like one of these (copy and run both lines it shows):

```bash
# Apple Silicon Mac (M1/M2/M3) — the installer will print something like this:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

When it finishes, run this to confirm and install git:

```bash
brew --version   # should print: Homebrew X.X.X
brew install git
git --version    # should print: git version X.X.X
```

If `brew --version` says "command not found", the PATH step was missed. Close Terminal, reopen it, and run the `eval` line again.

Phase 1 is complete. Everything else (gh, node, jq, ffmpeg, vercel CLI, Claude Code) is installed in Phase 2 — Claude Code handles those steps automatically.

---

## ✅ Phase 1 complete — switch to Claude Code now

Everything above is done. From here, Claude Code takes over.

1. Open **Claude Code Desktop** — it's already installed and signed in
2. Open the project folder: click **"Open Folder"** → select `~/code-projects/` (or any folder — Phase 2 Prompt 4 creates the project)
   Or in Terminal: `claude` from any directory
3. You're now in Claude Code. Copy and run **Prompt 1** from the Phase 2 guide.

> This is the last step you do in Claude Chat. Everything from here runs in Claude Code.
