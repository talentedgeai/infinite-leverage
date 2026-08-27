---
name: il-memory-cleanup
description: This skill should be used when the operator says "clean up my memory", "il memory", "memory cleanup", "my CLAUDE.md is a mess", "consolidate my memory", "too many accounts messed up my setup", "fix my memory index", or complains that switching between Claude accounts left their global CLAUDE.md or memory files inconsistent. Reads every memory file in full, narrates duplicates, conflicts, and stale facts back to the operator in plain language, and only then — with explicit per-item approval — deletes, merges, rewrites, or re-indexes. Always backs up before the first write. Never installs anything; only edits the operator's own memory content.
version: 1.0.0
---

# il-memory-cleanup — Human-in-the-Loop Memory Cleanup

## The problem this solves

People switch between several Claude accounts on one machine. All of them read and
write the same `~/.claude/` directory, so over months the global `CLAUDE.md` and the
per-project memory folders accumulate:

- the same fact written twice in slightly different words,
- two memories that give **contradictory** guidance (each account "learned" a
  different preference),
- facts about projects, tools, or clients that no longer exist,
- index files (`MEMORY.md`) that point at deleted files, or miss files that exist,
- instructions that clearly belong to a different persona/client/account.

## How this skill is different from other memory tools

Most memory consolidators are batch jobs: they rewrite everything in one silent pass.
This skill is a **conversation**. The agent does the reading and the reasoning; the
**human makes every destructive call**. Concretely:

1. The agent actually **reads every memory file in full** — never just the index,
   never just the descriptions.
2. It **narrates** what it found: quotes both sides of each conflict, explains in
   plain language why they can't both be right, and says which one the evidence
   favors and why.
3. It **proposes** an action per finding (delete / merge / rewrite / keep both,
   marked) — and **waits**.
4. Only after the operator approves a specific item (or a batch where every item was
   listed) does it touch a file. Silence is never approval.

If the operator asks you to "just clean it all up automatically", explain that this
skill deliberately keeps them in the loop for conflicts and deletions — offer to
auto-apply only the **safe** categories (index repair, exact duplicates) and still
walk them through conflicts one by one.

## Scope — what counts as memory

| Surface | Path | Notes |
|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md` | Applies to every project and every account on this machine |
| Auto-memory index | `~/.claude/projects/<slug>/memory/MEMORY.md` | One per project the user has worked in |
| Memory files | `~/.claude/projects/<slug>/memory/*.md` | One fact per file, frontmatter + body |

Default to the **current project's** memory directory plus the global `CLAUDE.md`.
Offer to sweep other projects' memory directories only if the operator asks or if
they said the whole machine is a mess. Never touch anything else in `~/.claude/`
(no settings, no permissions, no plugins, no agents) — if the mess extends to
settings or leftover installs, that is `/il-doctor` territory, not this skill.

## Phase 0 — Inventory (read-only)

List the surfaces in scope and their sizes so the operator knows the blast radius:

```bash
ls -la ~/.claude/CLAUDE.md 2>/dev/null
ls ~/.claude/projects/*/memory/ 2>/dev/null
```

Report: how many memory files, how many index lines, when each was last modified.
Ask which surfaces to include if there are many projects. Then proceed.

## Phase 1 — Read and narrate (still read-only)

Read **every file in scope, in full**. Then present a findings report grouped into
five categories. For each finding, quote the actual text (short excerpts) and name
the file it lives in, so the operator can verify without opening anything.

1. **Exact/near duplicates** — the same fact in two or more places. Show both,
   note the wording difference if any.
2. **Conflicts** — two memories that give contradictory guidance. This is the
   heart of the skill: quote both sides, explain the contradiction in one or two
   plain sentences ("one says always use pnpm, the other says this machine
   standardized on bun in March"), and state which side the evidence favors —
   file modification dates, references to things that still exist, corroboration
   from other memories — while being explicit that the operator may know context
   the files don't show.
3. **Stale or orphaned facts** — memories naming files, tools, flags, projects, or
   people you can verify no longer exist. Actually verify (check the path, grep the
   repo) before calling something stale; report the check you ran.
4. **Index drift** — `MEMORY.md` lines pointing at files that don't exist; files
   with no index line; `[[links]]` to memory names that were never written.
5. **Cross-account bleed** — facts that plainly belong to a different account,
   client, or persona (different email, different company's conventions, a project
   that lives under a different org). Flag these; only the operator knows which
   account this machine should serve.

End the narration with a numbered list of proposed actions. **Do not act yet.**

## Phase 2 — Decide together

Walk the findings with the operator, category by category:

- **Safe categories** (index repair, byte-identical duplicates) may be approved as
  a batch — but list every item in the batch before asking.
- **Conflicts** are resolved one at a time. Recommend, never decide: "I'd keep A
  and delete B because …. Keep A, keep B, merge them, or keep both marked as
  disputed?" If the operator can't decide now, keep both and append a one-line
  `> Disputed with [[other-name]] — resolve later` marker to each.
- **Cross-account bleed** — ask whether to delete, or move the text into a file the
  operator names (e.g. a notes file outside `~/.claude/`). Never guess which
  account is "the real one".
- Anything not explicitly approved stays untouched.

Record the decisions as a checklist in the conversation before applying anything.

## Phase 3 — Back up, then apply

**Before the first write**, snapshot everything in scope:

```bash
mkdir -p ~/.claude/memory-backups && tar -czf ~/.claude/memory-backups/memory-$(date +%Y%m%d-%H%M%S).tar.gz -C ~ .claude/CLAUDE.md .claude/projects/*/memory 2>/dev/null
```

Tell the operator the backup path and the restore command
(`tar -xzf <backup> -C ~`). Then apply **only** the approved changes with Edit/Write:

- Deletions: remove the file **and** its `MEMORY.md` line together.
- Merges: write the consolidated fact into the surviving file (keep its `name:`),
  update any `[[links]]` that pointed at the removed name, delete the loser, fix
  the index.
- Rewrites: preserve frontmatter shape (name / description / metadata.type).
- Index repair: one line per surviving file, no content in the index — pointers only.

## Phase 4 — Verify and report

- Re-read each touched `MEMORY.md` and confirm every line resolves to a file and
  every file has a line.
- Confirm no `[[link]]` points at a deleted name.
- Report: N deleted, N merged, N rewritten, N index lines fixed, N kept-as-disputed,
  backup location. List anything the operator deferred so it can be picked up next
  time.

## Hard rules

- **Never delete, merge, or rewrite anything the operator did not explicitly
  approve in this session.** Silence, "looks good" about the *report*, or approval
  of a different item does not count.
- **Never write before the backup exists.** If the backup command fails, stop and
  say so.
- **Only memory content.** This skill never touches settings, permissions, hooks,
  plugins, agents, or anything else in `~/.claude/` — and never installs anything
  there. It edits the operator's own memory files at their direction, nothing more.
- **Never resolve a conflict on the agent's own judgment.** Recommend with reasons;
  the human picks.
- **Verify before calling something stale.** A memory is only "orphaned" after an
  actual check (path exists? tool on PATH? repo still cloned?), and the report says
  which check ran.
- If the operator's mess turns out to be v1 install residue (global agents, hooks,
  a `Bash(*)` grant) rather than memory content, stop and route them to
  `/il-doctor` and the recovery prompt in `docs/guide/CLIENT-SETUP.md`.
