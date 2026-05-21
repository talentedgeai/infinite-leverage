# Infinite Leverage 8-Agent Template — Tool Compatibility Assessment

**Date:** 2026-05-21
**Assessed by:** Claude Code (claude-sonnet-4-6)
**Scope:** Compatibility of this codebase with Opencode and OpenAI Codex (ChatGPT)
**Exclusions:** MCP (Model Context Protocol) considerations excluded per request

---

## Executive Summary

This codebase is a **Claude Code/Claude Desktop-specific** multi-agent template system. However, the core conventions — `SKILL.md` files with YAML frontmatter, `AGENTS.md` for project instructions, and subagent delegation — are based on the [open agent skills standard](https://agentskills.io), which OpenAI Codex also implements. This makes the codebase **highly compatible** with Codex with minimal changes. Opencode compatibility is moderate, requiring format adaptation.

**OpenAI Codex compatibility: HIGH** — skill format is identical (SKILL.md + YAML frontmatter), AGENTS.md is native, subagents map to the 8-agent model.
**Opencode compatibility: MODERATE** — agent definitions are portable in content but need format adaptation.

---

## 1. Codebase Summary

| Aspect | Detail |
|--------|--------|
| Type | Agent definition templates + skill files (markdown-based) |
| Application code | None |
| Agent definitions | 8 files in `.claude/agents/*.md` |
| Skills | 21 files in `.claude/skills/*/SKILL.md` |
| Rules | 2 files in `.claude/rules/` |
| Plugin hooks | `hooks/session-start`, `hooks/pre-bash`, `hooks/prompt-submit` |
| Bootstrap | `setup-skills/` (init, onboard, patch, project) |
| Config | `CLAUDE.md`, `.vscode/settings.json`, `plugin-staging/package.json` |
| Stack assumptions | Next.js, TypeScript, Tailwind, Supabase, Vercel |

---

## 2. OpenAI Codex (ChatGPT) Compatibility

### 2.1 Feature Mapping

| Claude Code Concept | OpenAI Codex Equivalent | Compatibility |
|---------------------|------------------------|---------------|
| `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` | **Identical** — same `SKILL.md` format with YAML frontmatter (`name`, `description`). Both use the [open agent skills standard](https://agentskills.io) |
| `CLAUDE.md` | `AGENTS.md` | **Direct rename** — Codex natively reads `AGENTS.md` from repo root and nested directories |
| `.claude/rules/*.md` | `AGENTS.md` content or `/codex/rules` | Content is portable; Codex has a dedicated rules system |
| Agent definitions (`.claude/agents/*.md`) | Custom agents (`.codex/agents/*.toml`) | **Concept match** — Codex uses TOML files with `name`, `description`, `developer_instructions` |
| Multi-agent routing | Subagents (`/codex/subagents`) | **Native support** — Codex spawns specialized agents in parallel with custom configurations |
| Plugin hooks | [Codex hooks](https://developers.openai.com/codex/hooks) | Shell commands at key execution points; different trigger names but same concept |
| Scheduled tasks | Codex Automations | Built-in automation system |
| Cross-session memory | [Chronicle](https://developers.openai.com/codex/memories/chronicle) | Codex's memory system for cross-session persistence |
| `~/.claude/skills/` | `$HOME/.agents/skills`, `$REPO_ROOT/.agents/skills` | Codex scans multiple skill locations including user and repo scopes |
| Config | `~/.codex/config.toml` | TOML-based configuration |

### 2.2 What Works Out of the Box

| Element | Status | Notes |
|---------|--------|-------|
| **SKILL.md files** | **Directly portable** | Codex uses the exact same `SKILL.md` format with YAML frontmatter. The 21 skill files can be copied to `.agents/skills/` with no content changes |
| **Skill content (workflows, steps)** | Portable | Tool-agnostic procedural instructions transfer directly |
| **Engineering rules** | Portable | Can be embedded in `AGENTS.md` or Codex rules |
| **Documentation structure** | Portable | `docs/` conventions apply to any tool |
| **Git workflow rules** | Portable | The 13-step git sequence is tool-agnostic |
| **Stack assumptions** | Portable | Next.js/Supabase/Vercel stack is tool-independent |
| **Multi-agent concept** | **Native** | Codex subagents with custom TOML definitions directly support the 8-agent model |

### 2.3 What Requires Adaptation

| Element | Effort | Details |
|---------|--------|---------|
| Directory structure | Low | `.claude/skills/` → `.agents/skills/` (Codex scans `.agents/skills` from CWD up to repo root) |
| `CLAUDE.md` | Low | Rename to `AGENTS.md`; content is fully compatible |
| Agent definitions | Medium | `.claude/agents/*.md` (YAML frontmatter + markdown) → `.codex/agents/*.toml` (TOML with `name`, `description`, `developer_instructions`) |
| Plugin hooks | Medium | Claude Desktop hooks → Codex hooks (different trigger points, same shell command concept) |
| Speckit integration | High | `speckit-*` skills reference Claude Code commands; need standalone scripts or Codex-native equivalents |
| Bootstrap skills | Medium | `setup-skills/` reference Claude Desktop setup; need Codex-specific installation steps |
| Skill loading path | Low | `~/.claude/skills/` → `$HOME/.agents/skills/` or `$REPO_ROOT/.agents/skills/` |

### 2.4 Codex-Specific Advantages

| Advantage | Impact |
|-----------|--------|
| **Identical skill format** | `SKILL.md` files are directly portable — no content rewriting needed |
| **Native subagent support** | 8-agent model maps to Codex custom agents with TOML definitions, each with their own model, sandbox mode, and skills config |
| **AGENTS.md native** | No format conversion needed for project instructions |
| **Local execution** | Codex runs locally (CLI, IDE, Desktop app) — same filesystem access as Claude Code |
| **Multiple surfaces** | Desktop app, IDE extension, CLI, web — agents work across all |
| **Chronicle memory** | Built-in cross-session persistence |
| **Automations** | Native scheduled task support |
| **Worktrees** | Git worktree support for parallel development |
| **Integrations** | GitHub, Slack, Linear natively supported |

### 2.5 Codex-Specific Gaps

| Gap | Impact |
|-----|--------|
| No speckit commands | `speckit-specify`, `speckit-clarify`, `speckit-analyze` have no Codex equivalent; need standalone scripts |
| Different hook triggers | Claude Desktop's `session-start`, `pre-bash`, `prompt-submit` → Codex has different hook trigger points |
| Agent definition format differs | YAML frontmatter + markdown (Claude) → TOML (Codex); content is portable but format needs conversion |
| No Claude Desktop plugin system | `plugin-staging/` is Claude-specific; Codex uses plugins for skill distribution |

### 2.6 Migration Effort Estimate

| Phase | Effort | Details |
|-------|--------|---------|
| Skill directory move | 1-2 hours | Copy `.claude/skills/` → `.agents/skills/`; no content changes needed |
| `CLAUDE.md` → `AGENTS.md` | 1 hour | Direct rename; content is compatible |
| Agent definitions conversion | 4-8 hours | Convert 8 agent `.md` files to `.codex/agents/*.toml` format |
| Hook rewriting | 2-4 hours | Adapt hooks to Codex trigger points |
| Speckit replacement | 4-8 hours | Create standalone scripts for speckit-equivalent workflows |
| Bootstrap skills | 2-4 hours | Create Codex-specific init/onboard/patch flows |
| Testing | 4-8 hours | Verify skill loading, subagent spawning, and hook execution |
| **Total** | **18-35 hours** | ~2-4 working days |

---

## 3. Opencode Compatibility

### 3.1 What Works Out of the Box

| Element | Status | Notes |
|---------|--------|-------|
| Agent role descriptions | Portable | YAML frontmatter (`name`, `description`) + markdown body is a common convention |
| Skill content (workflows, steps) | Portable | Tool-agnostic procedural instructions transfer directly |
| Engineering rules (`.claude/rules/`) | Portable | Guardrails like `global-engineering.md` are tool-independent |
| Documentation structure | Portable | `docs/` conventions apply to any tool |
| Git workflow rules | Portable | The 13-step git sequence is tool-agnostic |
| Stack assumptions | Portable | Next.js/Supabase/Vercel stack is tool-independent |

### 3.2 What Requires Adaptation

| Element | Effort | Details |
|---------|--------|---------|
| Directory structure | Low | `.claude/agents/` → `.opencode/agents/` or equivalent |
| `CLAUDE.md` | Low | Rename to `AGENTS.md` (Opencode convention) |
| Agent frontmatter | Low | Verify Opencode supports `name` + `description` YAML keys |
| Skill loading mechanism | Medium | `~/.claude/skills/` runtime loading is Claude-specific; Opencode uses its own skill/plugin system |
| Plugin hooks | Medium | Claude Desktop-specific hooks; Opencode has different hook conventions |
| Speckit integration | High | `speckit-*` skills reference Claude Code commands; need Opencode equivalents |
| Scheduled tasks | Medium | `.claude/scheduled-tasks/` is Claude-specific; Opencode has its own scheduling |
| Bootstrap skills | Medium | `setup-skills/` reference Claude Desktop setup flows |

### 3.3 Opencode Migration Effort Estimate

| Phase | Effort | Details |
|-------|--------|---------|
| Format conversion | 2-4 hours | Rename directories, convert agent frontmatter, create `opencode.json` |
| Skill adaptation | 4-8 hours | Adapt 21 skills to Opencode format; content mostly portable |
| Hook rewriting | 2-4 hours | Rewrite hooks for Opencode trigger points |
| Bootstrap skills | 4-6 hours | Create Opencode-specific init/onboard/patch flows |
| Testing | 4-8 hours | Verify all 8 agents load correctly and skills trigger properly |
| **Total** | **16-30 hours** | ~2-4 working days |

---

## 4. Comparative Summary

| Dimension | OpenAI Codex | Opencode |
|-----------|-------------|----------|
| **Skill format** | **Identical** (SKILL.md + YAML frontmatter, open agent skills standard) | Moderate (adaptation needed) |
| **Project instructions** | **Native** (AGENTS.md) | Moderate (rename CLAUDE.md → AGENTS.md) |
| **Multi-agent support** | **Native** (subagents with custom TOML definitions) | Unknown (depends on Opencode features) |
| **Hook system** | Moderate (equivalent concept, different triggers) | Moderate (rewrite needed) |
| **Memory / cross-session** | High (Chronicle built-in) | Unknown |
| **Local execution** | Yes (CLI, IDE, Desktop app) | Yes |
| **Content portability** | **High** (SKILL.md directly portable) | High |
| **Migration effort** | **18-35 hours** | 16-30 hours |
| **Fidelity after migration** | **High** (same execution model, local filesystem) | High |
| **Ongoing maintenance** | Low (same skill format) | Low |

---

## 5. Recommendations

### For OpenAI Codex (Recommended Primary Target)

1. **Copy skills directly** — move `.claude/skills/` to `.agents/skills/` with no content changes. The `SKILL.md` format is identical.
2. **Rename `CLAUDE.md` to `AGENTS.md`** — Codex reads this natively for project instructions.
3. **Convert agent definitions to TOML** — create `.codex/agents/*.toml` files for each of the 8 agents with `name`, `description`, and `developer_instructions` fields.
4. **Leverage subagents** — the 8-agent model maps naturally to Codex's subagent system. Each agent can have its own model, sandbox mode, and skills configuration.
5. **Replace speckit with standalone scripts** — `speckit-specify`, `speckit-clarify`, `speckit-analyze` need Codex-native equivalents.
6. **Adapt hooks** — rewrite `session-start`, `pre-bash`, `prompt-submit` hooks to Codex's hook trigger points.
7. **Use Chronicle for memory** — migrate cross-session state from file-based handoffs to Codex's Chronicle memory system.

### For Opencode

1. **Start with format conversion** — rename `.claude/` to `.opencode/`, create `opencode.json`, rename `CLAUDE.md` to `AGENTS.md`
2. **Adapt skills incrementally** — start with the 5 highest-quality skills (`dev-diagnose`, `dev-tdd`, `qa-triage`, `dev-handoff`, `pm-epic-writing`)
3. **Preserve multi-agent routing** — verify Opencode supports agent delegation before flattening
4. **Create Opencode bootstrap skills** — replace Claude Desktop-specific setup flows

### General

1. **Abstract agent definitions** — create a tool-agnostic format (YAML) that can be compiled to Claude, Codex (TOML), Opencode, or other targets
2. **Separate content from format** — keep workflow instructions in tool-agnostic markdown (`SKILL.md`), with thin format wrappers per tool
3. **Add compatibility matrix** — document which features work on which platforms in the README

---

## 6. Risk Assessment

| Risk | OpenAI Codex | Opencode |
|------|-------------|----------|
| Feature loss after migration | Low (SKILL.md is identical, AGENTS.md is native) | Low (most features portable) |
| Migration complexity | Low-Medium (format changes for agents only) | Medium |
| Ongoing maintenance burden | Low (same skill format) | Low |
| Operator disruption | Low (same local execution model) | Low (similar UX) |
| Skill fidelity | **High** (identical format) | High |
| Multi-agent fidelity | **High** (native subagent support) | Unknown |
| Cost predictability | Medium (token-based, per-session) | Unknown |

---

## 7. Verdict

**OpenAI Codex: Highly recommended target for porting.** The codebase's `SKILL.md` skill format is **identical** to Codex's — both use the open agent skills standard with YAML frontmatter (`name`, `description`). Skills can be copied to `.agents/skills/` with zero content changes. `CLAUDE.md` maps directly to Codex's native `AGENTS.md`. The 8-agent model maps to Codex's subagent system with custom TOML definitions. Migration requires 18-35 hours, primarily for agent definition format conversion (YAML+markdown → TOML) and speckit replacement.

**Opencode: Recommended target for porting.** The codebase's agent definitions and skill content are largely tool-agnostic. With 16-30 hours of format adaptation, the full 8-agent system can be preserved on Opencode with local execution intact.

**Best strategy:** Maintain tool-agnostic skill content in `SKILL.md` (open agent skills standard), then compile agent definitions to each platform's format: YAML+markdown for Claude, TOML for Codex, and Opencode's native format. This codebase's content (workflows, rules, best practices) is valuable across all three platforms, with Codex being the closest match due to the identical skill format.
