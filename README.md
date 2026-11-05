# Self-Improving Loop — by [DYNO SOFT](https://dynosoft.md)

> **Tired of your agent repeating the same mistakes?** Stop re-teaching it every session — give it a loop that verifies, remembers, and repairs its own skills.

`self-improving-loop` is a production-grade self-improvement loop for coding agents.
It audits every claim before done, captures lessons as durable memory, promotes
recurring patterns into project rules, and detects when its own skills silently
degrade. One repo, five platforms.

## Why it works where others fall short

Most memory plugins do exactly one slice. This plugin fuses the full loop.

| Capability | self-improving-loop | self-improving-agent (claude-skills) | self-improving-skills (unisone) | memem / skillmem / omega-memory |
|---|---|---|---|---|
| Verify-before-done audit (executed vs claimed, exit codes, reproduce-the-fix) | ✅ | — | — | — |
| Durable memory capture (machine + project) | ✅ | — | — | ✅ |
| Auto-memory curation + promotion (MEMORY.md -> CLAUDE.md / .claude/rules) | ✅ | ✅ | — | — |
| Skill degradation loop (telemetry -> audit -> amend -> evaluate) | ✅ | — | ✅ | — |
| Multi-platform (Claude Code / Codex / Cursor / Hermes / DSH) | ✅ | partial | Claude Code only | Claude Code only |

The three loops it fuses:

1. **Verify-first** — a cognitive-error audit runs before you can claim done:
   did it actually execute? is the exit code checked? was the fix reproduced?
   A claim that fails the audit gets fixed, not shipped.
2. **Memory promotion** — auto-memory (MEMORY.md) is capture, not curation. A
   pattern that recurs 2-3 times graduates into CLAUDE.md or a scoped
   `.claude/rules/` rule. Machine lessons go to `~/.claude/LEARNED.md`.
3. **Skill degradation** — a skill is a static file in a dynamic environment and
   it decays silently. Telemetry logs every use; the audit flags unused or
   broken skills; amendments are backed up and evaluated.

## Install

### Claude Code (tested)

```
/plugin marketplace add DYNO-SOFT/self-improving-loop
/plugin install self-improving-loop@dyno-soft
```

Local dev: `/plugin marketplace add /path/to/self-improving-loop`

### OpenAI Codex

The `.codex-plugin/plugin.json` shim ships the skill and interface. Add this
repo as a Codex plugin source (Codex reads `.codex-plugin/`), or copy
`skills/self-improve` into your Codex skills directory.

### Cursor

The `.cursor-plugin/plugin.json` shim ships the skill. Point Cursor at this repo,
or copy `skills/self-improve` into your Cursor rules.

### Hermes Agent

```
hermes plugins install DYNO-SOFT/self-improving-loop
```

Registers the skill and a `pre_llm_call` hook that bootstraps the loop on session start.

### DeepSeek Harness (DSH)

```
dsh plugin add @dynosoft/self-improving-loop
```

(or `pnpm add @dynosoft/self-improving-loop`). Ships a cordis plugin
(`lib/index.js` + `cordis.patch.yml`) that registers the `self-improve` skill
into the DSH skill catalog. Manual (no-npm) path — symlink the skill and add
the machine-notes loop — see `dsh/README.md`.

## Measure effectiveness

Repeat a task class a week later and count how much steering it still needs.
Fewer corrections = the loop is working.

## About

Built by [DYNO SOFT](https://dynosoft.md) — senior-led AI development studio:
autonomous agents, multi-agent orchestration, RAG, MCP servers, evals.