---
name: github-flow
description: >-
  Complete GitHub workflow skill for clean, consistent branch-to-merge cycles.
  Use this skill whenever you need to: create a branch, make commits, push
  changes, open a pull request, merge a PR, or clean up after a merge.
  Also invoke proactively when the user says "commit this", "push my changes",
  "open a PR", "merge it", "clean up the branch", "I'm done with this feature",
  or any variation of git/GitHub operations. Agents are authorised to merge PRs
  — no human approval is required unless the skill explicitly flags a risk. This
  skill replaces ad-hoc git commands and ensures every change follows the same
  clean workflow.
---

# GitHub Flow Skill

Every change follows the same loop: **branch → commit → push → PR → merge → cleanup**. Never skip steps. Never shortcut. The workflow is cheap; the mess from skipping it is not.

---

## Step 0: Pre-Flight Checks

Run these before touching anything:

```bash
git status                    # must be clean before starting new work
git branch --show-current     # confirm you're not on main
git log --oneline -5          # orient yourself
```

**Stop and report if:**
- Uncommitted changes or merge conflicts exist — resolve before continuing
- You're on `main` or `master` — create a feature branch first (Step 1)
- A `MERGE_HEAD` or `CHERRY_PICK_HEAD` file exists in `.git/` — finish or abort before proceeding

---

## Step 1: Create a Branch

Always branch off an up-to-date `main`:

```bash
git checkout main
git pull origin main
git checkout -b <type>/<short-description>
```

### Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/<slug>` | `feat/seo-audit-skill` |
| Bug fix | `fix/<slug>` | `fix/og-image-missing` |
| Chore / maintenance | `chore/<slug>` | `chore/update-dependencies` |
| Documentation | `docs/<slug>` | `docs/github-flow-guide` |
| Refactor | `refactor/<slug>` | `refactor/skill-structure` |
| Hotfix (prod issue) | `hotfix/<slug>` | `hotfix/broken-sitemap` |

**Rules:**
- All lowercase, hyphens only (no underscores, no slashes beyond the prefix)
- Keep it short — 3–5 words max after the prefix
- Describe the work, not the ticket number

---

## Step 2: Make Changes and Commit

### Stage Explicitly — Never Use `git add .`

```bash
git add src/components/Header.tsx
git add src/styles/global.css
# one file at a time, or a deliberate list — never git add . or git add -A
```

Verify what you're about to commit:
```bash
git diff --staged
```

### Commit Format (Conventional Commits)

```
<type>(<scope>): <subject>

<body — optional, explain why not what>

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**

| Type | When |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change with no behavior change |
| `chore` | Tooling, deps, config — no production code |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `style` | Formatting only, no logic change |

**Subject line rules:**
- Imperative mood: "Add feature" not "Added feature"
- Capitalize first word
- No period at the end
- Under 72 characters total for the header line

**Commit using HEREDOC to avoid quoting issues:**

```bash
git commit -m "$(cat <<'EOF'
feat(seo-audit): add social platform meta tag checks

Pinterest requires portrait-ratio images and explicit rich-pin meta.
Discord and Slack both use OG tags but have size constraints that
affect how previews render — adding platform-specific guidance.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Commit Discipline

- **One logical change per commit.** Don't bundle unrelated fixes.
- **Never commit:** `.env` files, secrets, API keys, `node_modules/`, build artifacts, or editor config unless the project explicitly tracks it.
- **Never amend** a commit that has already been pushed to remote.
- **Never skip hooks** with `--no-verify` — if a hook fails, fix the underlying issue.

---

## Step 3: Push the Branch

### First Push (new branch)

```bash
git push -u origin <branch-name>
```

The `-u` flag sets the upstream tracking reference so future pushes are just `git push`.

### Subsequent Pushes

```bash
git push
```

**Never force-push** (`--force` or `--force-with-lease`) to any branch. If your history has diverged from remote, investigate why before taking any action.

---

## Step 4: Open a Pull Request

Use the `gh` CLI:

```bash
gh pr create \
  --title "<type>: <concise description>" \
  --body "$(cat <<'EOF'
## Summary
- <bullet: what changed>
- <bullet: why>

## Test Plan
- [ ] <what to verify manually or via CI>
- [ ] All existing tests pass

## Notes
<anything reviewers or the merge agent should know>

<!-- author: <handle> <git user.email> -->

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main
```

> The `<!-- author: ... -->` line is REQUIRED — see **Authorship block** below. Because the
> heredoc is quoted (`<<'EOF'`), substitute the real handle + email before running the command.

### PR Title Rules

Follow the same conventional commit format as your commits:
- `feat(scope): Add X capability`
- `fix(scope): Resolve Y issue`
- Under 72 characters
- No ticket numbers in the title (put them in the body)

### PR Body Checklist

Always include:
- **Summary**: 2–4 bullets on what changed and why
- **Test Plan**: what was verified, how CI was checked
- **Notes**: breaking changes, migration steps, or "safe to auto-merge" signal

### Authorship block (REQUIRED)

The central service account is the git committer for all team work, so GitHub attributes
every commit/PR to it. To credit the real human, **every PR body MUST include an authorship
block** that the daily data sync parses to fill `pull_requests.author_human_user_id`.

Compute and append it from the local git identity:

```bash
EMAIL=$(git config user.email)
HANDLE=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
# append to the PR body:  <!-- author: $HANDLE $EMAIL -->
```

Format (matched by `/<!--\s*author:\s*(\S+)\s+(\S+)\s*-->/i`):

```
<!-- author: <handle> <email> -->
<!-- co-authors: <handle> <email>, <handle> <email> -->   (optional, when pairing)
```

- The `<email>` is the resolution key — it must be the git email registered as that person's
  team member (so `resolve_team_member(email)` resolves). A wrong/placeholder email → the PR
  is recorded as **unattributed** (not an error, but no credit).
- Add a `co-authors:` line when pairing; zero or more `handle email` pairs, comma-separated.
- Full contract: `docs/architecture/authorship-contract.md` in the human-token-tracker repo.

### Labels (add if the project uses them)

```bash
gh pr edit <number> --add-label "feat"
```

Common labels: `feat`, `fix`, `docs`, `chore`, `breaking-change`, `needs-review`, `ready-to-merge`

---

## Step 5: Verify CI Before Merging

```bash
gh pr checks <number>         # list all CI check statuses
gh pr view <number>           # see PR status and reviews
```

**Do not merge if:**
- Any required CI check is failing
- There are unresolved review comments marked "blocking"
- The PR has a `do-not-merge` or `wip` label

If CI is passing and the PR is ready:

```bash
gh pr checks <number> --watch  # wait for all checks to complete
```

---

## Step 6: Merge the PR

Agents are authorised to merge PRs. Default to **squash merge** to keep `main` history clean and linear.

```bash
gh pr merge <number> --squash --delete-branch
```

Flags:
- `--squash` — combines all commits into one clean commit on `main`
- `--delete-branch` — removes the remote branch immediately after merge
- `--auto` — can be added to auto-merge once CI passes (use when kicking off a long CI run)

### When to Use Which Merge Strategy

| Strategy | When | Command |
|---|---|---|
| Squash merge | Default — feature branches, fixes, chores | `--squash` |
| Merge commit | Long-lived branches with meaningful history to preserve | `--merge` |
| Rebase | Linear history is critical, commits are already clean | `--rebase` |

**Never merge a PR with a merge conflict** — resolve it locally first (see Conflict Resolution below).

---

## Step 7: Post-Merge Cleanup

After merging, clean up locally:

```bash
git checkout main
git pull origin main
git branch -d <branch-name>     # delete local branch (safe — won't delete if unmerged)
```

Verify the remote branch is gone (should be, if `--delete-branch` was used):

```bash
git fetch --prune               # removes stale remote-tracking refs
git branch -r                   # confirm branch no longer listed
```

---

## Conflict Resolution

If a PR has conflicts, resolve them locally — never force-merge:

```bash
git checkout <branch-name>
git fetch origin
git rebase origin/main          # preferred over merge for cleaner history
# resolve conflicts in each file, then:
git add <resolved-file>
git rebase --continue
git push --force-with-lease     # ONLY acceptable force-push: rebase on your own branch, not yet reviewed
```

Use `--force-with-lease` (not `--force`) — it refuses to push if someone else has added commits since your last fetch.

If the rebase gets complex, use merge instead:

```bash
git merge origin/main
# resolve, stage, commit
git push
```

---

## Hotfix Workflow

For urgent production fixes that can't wait for normal review:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/<slug>
# make the fix — keep it minimal and surgical
git add <files>
git commit -m "hotfix(<scope>): <what broke and how it's fixed>"
git push -u origin hotfix/<slug>
gh pr create --title "hotfix: <description>" --base main --label "hotfix"
gh pr merge --squash --delete-branch   # agent can merge immediately if CI passes
```

---

## Quick Reference

```bash
# New branch
git checkout main && git pull origin main && git checkout -b feat/<slug>

# Stage and commit
git add <file1> <file2>
git diff --staged
git commit -m "feat(scope): subject"

# Push
git push -u origin <branch>    # first push
git push                       # subsequent

# PR
gh pr create --title "feat: ..." --base main
gh pr checks <number> --watch
gh pr merge <number> --squash --delete-branch

# Cleanup
git checkout main && git pull origin main && git branch -d <branch> && git fetch --prune
```

---

## What Never to Do

| Rule | Why |
|---|---|
| Never `git add .` or `git add -A` | Accidentally stages secrets, build artifacts, or unrelated files |
| Never force-push to `main` | Rewrites shared history — breaks everyone |
| Never `--no-verify` | Hooks exist for a reason — fix the underlying issue |
| Never amend pushed commits | Creates divergent history for anyone who pulled |
| Never merge a failing CI | Breaks `main` for the whole team |
| Never leave branches around after merge | Stale branches create confusion and inflate the branch list |
| Never commit `.env` or secrets | Even if the repo is private — rotate keys immediately if this happens |
