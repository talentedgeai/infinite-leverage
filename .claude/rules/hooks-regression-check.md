# Hooks Regression Check

Read this file before editing `plugin-staging/hooks/session-start`, `install-hooks.sh`, `hooks.json`, or `il_telemetry/*`.

Before committing any hook change, confirm **all** of the following still hold (a rewrite must preserve every one):

1. **Auto-update** — `session-start` Stage 2 still applies (agents + skills + hooks via `install-hooks.sh`) with nudge fallback. It must (a) trigger **only when STRICTLY NEWER** (semver compare — never downgrade a machine that is ahead), and (b) read its remote version from the **GitHub Releases latest tag** — the *same* source `infiniteleverage-init` / `-patch` stamp `~/.claude/.infiniteleverage-version` from. Do NOT split the source (e.g. raw `VERSION` file vs Releases) — that drift causes phantom up/downgrade prompts.
2. **Capture** — `Stop` → `session-telemetry-stop` → `il_telemetry.stop` writes the outbox.
3. **Deliver** — `SessionEnd`/`SessionStart` → `session-telemetry-end` → `il_telemetry.flush` delivers via `gh` (no secrets).
4. **Registration notice** — Stage 5b probes `/api/projects/status` and prompts when unregistered.
5. **No obsolete hooks** — `session-ingest-*.py` are NOT present/registered; `install-hooks.sh` still **prunes** them.
6. **`hooks.json`** valid, single key per event, registers only the current path.
7. **No DB creds on contributor machines** — hooks use only `gh`; never `SUPABASE_*`/`INGEST_SECRET`.

**Rule: editing one stage must not delete another.** Diff the full file and tick every item above before opening a PR.
