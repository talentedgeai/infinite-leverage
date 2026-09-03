# Release checklist

What has to be true before a release a client will run. Adapted from the invariants and
run matrix in the retired v1 init PR (#55), rewritten for the v2 marketplace plugin.

Runs are marked **[ci]** (automated, every PR), **[rel]** (before tagging a release), or
**[teach]** (before a client workshop or hand-off).

---

## Run 0 — the mechanical gate **[ci]**

`.github/workflows/plugin-ci.yml`, every PR. Nothing below is worth doing until it is
green.

| Check | Invariant it protects |
|---|---|
| Manifests parse; versions in lockstep | a broken manifest disables the plugin silently |
| No writes to `~/.claude/`, no telemetry in the payload | **nothing installs globally** — the reason v2 exists |
| 4 agents / 16 skills, in lockstep across il-project's gate, il-adopt's gate and `doctor.sh` — retired v2.4 lists too | the names the tooling asserts match reality, in every place they are hard-coded |
| `AGENT-DELEGATION` block identical in il-project, il-adopt and the scaffold; routes exactly the shipped agents | `/il-project` and `/il-adopt` install the same routing |
| `doctor.sh` parses; smoke test drives its layout section over scaffolded, adopted, legacy-v2.4 and partial trees | the check a client reads actually fires — its adopted-repo path had never run |
| Scaffold `.claude/rules/` byte-identical to the canonical rules; no `~/.claude` advice in them | the rules a project gets are the rules this repo reviews |
| Step 4 substitution tokens equal the template's; the step runs against the template with a name containing `/ @ & $ \` | no dead substitutions, no leftover placeholders, no mangled project names |
| Skill frontmatter `name` matches its directory | a mismatched skill is silently unroutable |
| Plan-protocol engine suite (32 tests) | the enforcement engine still enforces |
| Plan-protocol ships no domain vocabulary | the engine stays stack-neutral |
| Web template imports all declared by step 9c | no dependency resolving by accidental hoisting |
| Web template queries match its migrations | no query against a table/column that doesn't exist |
| Web template RLS hygiene | every table has RLS; no bare `auth.uid()`; policies scoped |

## Run 1 — scaffold a project from scratch **[rel]**

On a clean directory, with the plugin installed (not from a checkout):

```
/il-project
```

Passes when:

- [ ] Step 1 blocks on any missing prerequisite rather than failing later
- [ ] Step 3 prints `scaffold pinned to vX.Y.Z` — **not** the fallback warning
- [ ] Step 6's gate reports `agents: canonical 4 present · skills: 16/16` and does not continue if it can't
- [ ] Step 9e is green on all four: `lint`, `tsc --noEmit`, `build`, `vitest`
- [ ] Step 10's first commit contains no `node_modules`, `.next`, or `.env*`
- [ ] `/il-doctor` inside the new project is all-PASS

## Run 2 — the generated project's own CI **[rel]**

In the scaffolded project, run `devops-cicd`, then confirm its pipeline passes on a PR:
install → lint → type check → test → build. A red first CI run on template code is a
failed release; it is what shipped in 2.4.1.

- [ ] all five steps green on the generated `.github/workflows/ci.yml`

## Run 3 — the plugin is what a client actually gets **[rel]**

The published payload is `plugin/` only. Everything else in this repo is a *source* the
skills clone at run time.

- [ ] the tag `vX.Y.Z` exists and points at the release commit (pinning depends on it)
- [ ] the `mirror-release` workflow run for that tag is green, and the mirror repo's
      newest commit is `mirror vX.Y.Z` — org seats get nothing until it is
- [ ] `/il-doctor` on a deliberately older cached plugin reports the skew and names the
      update command

## Run 4 — refresh an existing project **[rel]**

Run `/il-adopt` against a project scaffolded from the previous release, and once against
a repo that was never scaffolded (no `FOLDER-STRUCTURE.md`).

- [ ] agents and skills are refreshed to the new counts, nothing else is clobbered
- [ ] the `AGENT-DELEGATION` block in `CLAUDE.md` is replaced, not duplicated
- [ ] on a v2.4.x tree, writer/designer and their 8 skills land in
      `.claude/retired-il-<date>/` and a custom agent beside them survives
- [ ] `/il-doctor` in the adopted repo prints the `Project Layout` section, all PASS

## Run 5 — the guardrails actually bite **[rel]**

Not "the files exist" — the checks fire.

- [ ] `devops-git-guardrails`: `git push --force` denied; `git push origin feat/x` allowed;
      `--amend` allowed on an unpushed branch and denied once pushed
- [ ] `plan-protocol`: pre-push blocks a direct push to `main`; `guard` exits non-zero on
      an undeclared hot-zone change
- [ ] a non-executable hook is caught by `doctor --heal` (a present-but-unexecutable hook
      is ignored by git silently, and looks installed)

## Run 6 — the agent chain, end to end **[teach]**

One feature, all the way through, on the scaffolded project:

- [ ] `pm-client-interview` → `pm-documentation` fills `docs/product/product.md`
- [ ] `pm-epic-writing` → `pm-grill-with-docs` → `pm-to-issues` produces real GitHub issues
- [ ] `dev-feature-plan` → `dev-tdd` produces a tested vertical slice
- [ ] `qa-triage` on a seeded bug writes `docs/qa/` and updates `epic-status.md`
- [ ] the PR is opened, not merged by the agent (except under `developer.md` auto-merge)
- [ ] no agent committed anything the operator did not ask for

## Run 7 — the publishing chain **[teach]**

- [ ] `web-publisher-publish` opens a PR; nothing lands on `main` directly

## Run 8 — the negative cases **[teach]**

The ones that matter in a room full of people:

- [ ] `/il-project` against an existing directory refuses, and says why
- [ ] with `gh` unauthenticated, step 1 stops and tells the operator to run
      `gh auth login` themselves rather than attempting it
- [ ] offline, `/il-doctor` degrades to "could not reach the marketplace" instead of failing

---

## Cadence

| When | Runs |
|---|---|
| Every PR | 0 |
| Patch release | 0, 1, 3 |
| Minor release | 0–5 |
| Before teaching a client | all of 0–8, on a clean machine, by someone who did not write the change |

## Honest status

Runs 0–3 and most of 5 are verified and automated as of v2.4.6. **Runs 6, 7 and 8 have
never been executed end to end** — the agent and content chains are reviewed for internal
consistency, not observed working against a live Supabase/Vercel project. Do those
before the first client session, and record what breaks here.
