#!/usr/bin/env bash
# Inject (or refresh) the AGENT-DELEGATION block in a CLAUDE.md file.
#
# Usage:
#   ./inject-agent-delegation.sh <path-to-CLAUDE.md>
#
# Behavior:
#   - If the file is missing → exit 1 with a clear message
#   - If the BEGIN/END markers exist → replace the block in place
#   - If the markers do not exist → append the block at the end of the file
#
# The canonical block content lives below in this script (single source of truth).
# Other skills (init, onboard, patch, project) call this script — no duplication.

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path-to-CLAUDE.md>"
  exit 1
fi

TARGET="$1"
if [ ! -f "$TARGET" ]; then
  echo "❌ CLAUDE.md not found: $TARGET"
  exit 1
fi

BLOCK=$(cat <<'BLOCK_EOF'
<!-- BEGIN: AGENT-DELEGATION (managed by infiniteleverage skills — do not delete this block) -->
## Agent delegation (auto-routing)

When you receive a request, **delegate to the right specialist agent** before doing the work yourself. The 8 agents and their triggers:

| Agent | Delegate when the request involves… |
|---|---|
| **product-manager** | roadmap, vision, epics, daily plan, project-status.html, scope changes, approval triage, stakeholder updates, standup briefings |
| **developer** | writing/changing code, fixing bugs, refactoring, scaffolding pages, API endpoints, Supabase migrations, env-vars wiring |
| **qa** | testing, regression checks, browser matrix, accessibility, QA plans, "verify this works" |
| **devops** | CI/CD, deployments, secret management, infra escalations, Vercel/GitHub workflow issues |
| **designer** | UI mockups, brand application, image prompts, design system updates, visual reviews |
| **writer** | blog drafts, social copy, SEO briefs, voice/tone, content briefs |
| **web-publisher** | publishing markdown → Next.js components, updating `website/pages/blog/index.jsx`, image optimization, the publish workflow |
| **email-marketer** | email drafts, sequences, broadcast campaigns, Brevo/Resend, CRM segmentation |

**Delegation rules:**
1. Pick exactly **one** agent per turn — don't run two in parallel unless the operator explicitly says so.
2. If a request spans agents (e.g., "write a blog *and* publish it"), call them **in sequence**: writer → designer → web-publisher.
3. If unclear which agent fits, **ask the operator** before assuming.
4. Cross-cutting engineering rules live in `.claude/rules/global-engineering.md` — every agent honors them.
5. Project-level persona overrides for each agent live in `agents/<name>/context/persona.md` — read these on first invocation.
6. Trigger phrases: `@product-manager`, `@developer`, etc. — but auto-route even without the `@` when intent is clear.
<!-- END: AGENT-DELEGATION -->
BLOCK_EOF
)

if grep -q "BEGIN: AGENT-DELEGATION" "$TARGET" 2>/dev/null; then
  # Replace existing block with perl multi-line substitution
  TMP=$(mktemp)
  printf '%s\n' "$BLOCK" > "$TMP"
  perl -i -0pe '
    BEGIN { local $/; open($f, "<", $ENV{BLOCK_FILE}); $block = <$f>; chomp $block; }
    s{<!-- BEGIN: AGENT-DELEGATION.*?<!-- END: AGENT-DELEGATION -->}{$block}s;
  ' BLOCK_FILE="$TMP" "$TARGET"
  rm -f "$TMP"
  echo "✅ Refreshed AGENT-DELEGATION block in $TARGET"
else
  # Append
  {
    echo ""
    printf '%s\n' "$BLOCK"
  } >> "$TARGET"
  echo "✅ Appended AGENT-DELEGATION block to $TARGET"
fi
