# Self-Improving Loop — by [DYNO SOFT](https://dynosoft.md)

> **Tired of your agent repeating the same mistakes?** Stop re-teaching it every session — give it a loop that verifies, remembers, and repairs its own skills.

`self-improving-loop` is a production-grade self-improvement loop for coding agents.
It audits every claim before done, captures lessons as durable memory, promotes
recurring patterns into project rules, and detects when its own skills silently
degrade. One repo, five platforms.

## Why it works where others fall short

Most memory plugins do exactly one slice. This plugin fuses the full loop.

| Capability | self-improving-loop | [self-improving-agent](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/self-improving-agent) | [self-improving-skills](https://github.com/unisone/self-improving-skills) | [memem](https://github.com/TT-Wang/memem) / [skillmem](https://github.com/liza-studio/skillmem) / [omega-memory](https://github.com/omega-memory/omega-memory) |
|---|---|---|---|---|
| Verify-before-done audit (executed vs claimed, exit codes, reproduce-the-fix) | ✅ + test-witness | error-capture nudge | — | skillmem: test-witness |
| Durable memory capture (machine + project) | ✅ | ✅ (`/si:remember`) | — | ✅ |
| Auto-memory curation + promotion (scored rubric, capacity gauge, dead refs) | ✅ | ✅ | — | — |
| Skill degradation loop (outcome telemetry → audit → versioned amend → evaluate → rollback) | ✅ | — | ✅ | skillmem: strength + decay |
| Untrusted agent-written memory | ✅ (marked until confirmed) | — | — | skillmem |
| Runtime footprint | markdown + shell + python stdlib | markdown + shell + python | markdown + shell + `jq` | MCP server + SQLite / embeddings |
| Platforms | Claude Code, Codex, Hermes, DSH (hooks); Cursor (skill) | Claude Code + copies for Codex, Gemini, Hermes | Claude Code | Claude Code hooks; MCP for Codex, Cursor and others |

What we deliberately do **not** ship: MCP servers, databases, embeddings, or LLM
calls inside hooks. They add daemons, downloads and cost, and LLM-in-hook mining
has caused hook-recursion incidents elsewhere. Everything here is files you can read.

The three loops it fuses:

1. **Verify-first** — a cognitive-error audit runs before you can claim done:
   did it actually execute? is the exit code checked? was the fix reproduced?
   A claim that fails the audit gets fixed, not shipped.
2. **Memory promotion** — auto-memory (MEMORY.md) is capture, not curation. A
   pattern that recurs 2-3 times graduates into CLAUDE.md or a scoped
   `.claude/rules/` rule. All supported agents share general lessons in
   `~/.self-improving-loop/LEARNED.md` and keep private repository lessons in
   `~/.self-improving-loop/projects/<project-id>/LEARNED.md`. The skill loads
   the current project's notes and reads related projects when the task calls
   for them. GitHub, GitLab (including nested groups), and Bitbucket Cloud use
   the host and repository path across worktrees. For custom endpoints such as
   Bitbucket Data Center, set the same ID in each clone, for example
   `git config --local self-improving-loop.project-id bitbucket.example.com/PROJ/repo`.
   Use legacy files as read-only sources during an explicit migration or memory audit.
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

### Commands (Claude Code)

| Command | What it does |
|---|---|
| `/self-improve` | run the loop now: audit this session, save durable lessons |
| `/self-audit` | cognitive-error audit only, no memory writes |
| `/self-improve-audit` | skill + memory health: score, degraded/stale/archive, amendment evaluation, dead refs, promotion candidates |
| `/skill-feedback <skill> good\|bad [notes]` | rate a skill; feeds the audit |
| `/skill-rollback <skill> [version]` | restore a versioned skill backup |

Hooks: `SessionStart` (context + audit-due reminder after 7 days / 50 skill uses),
`Stop` (audit before finishing, once per turn; test-witness check),
`Pre/PostToolUse` on `Skill` (telemetry with outcome), `PostToolUse` on `Bash`
(records a successful test/build run), `PostToolUseFailure` on `Bash` (fix-or-record nudge).
State lives in `~/.claude/debug/` (`skill-telemetry.jsonl`, `skill-feedback.jsonl`,
`last-skill-audit`, `test-witness`); override with `SIL_DIR`.

### OpenAI Codex

Codex reads `.codex-plugin/plugin.json`: it ships the `self-improve` skill and the
lifecycle hooks in `.codex-plugin/hooks.json` (Codex hooks are stable and on by
default). Add this repo as a Codex plugin source, or copy `skills/self-improve`
into your Codex skills directory (skill only, no hooks).

Hooks on Codex:

| Event | Effect |
|---|---|
| `SessionStart` | adds a short "self-improvement is active" context |
| `Stop` | returns `{"decision":"block","reason":…}` once, so the agent runs the audit before finishing |

The Stop hook exits silently when `stop_hook_active` is true, so it fires once per turn and never loops.

### Cursor

The `.cursor-plugin/plugin.json` shim ships the skill. Point Cursor at this repo,
or copy `skills/self-improve` into your Cursor rules.

### Hermes Agent

```
hermes plugins install DYNO-SOFT/self-improving-loop
```

Registers the skills and two hooks:

| Hook | Effect |
|---|---|
| `pre_llm_call` | first turn only: injects the self-improve skill as bootstrap context |
| `pre_verify` | Stop equivalent: once per turn, when the agent edited code and is about to finish, asks it to run the audit (bounded by `agent.max_verify_nudges`) |

### DeepSeek Harness (DSH)

```
dsh plugin add @dynosoft/self-improving-loop
```

(or `pnpm add @dynosoft/self-improving-loop`). Ships a cordis plugin
(`lib/index.js` + `cordis.patch.yml`) that:

- registers the `self-improve` skill into the DSH skill catalog (`inject: ['skills']`);
- when the `systemPrompt` service is mounted, adds a short runtime context
  (`self-improving-loop:reminder`) — the DSH counterpart of the SessionStart hook.
  It is an optional dependency, so the plugin still loads without it.

Manual (no-npm) path — symlink the skill and add the machine-notes loop — see `dsh/README.md`.

### Platform matrix

| Platform | Skill | Session-start context | Before-finish audit | Skill telemetry |
|---|---|---|---|---|
| Claude Code | ✅ | ✅ `SessionStart` hook (+ audit-due reminder) | ✅ `Stop` hook + test-witness | ✅ outcome per use |
| OpenAI Codex | ✅ | ✅ `SessionStart` hook | ✅ `Stop` hook (block once) | — |
| Hermes Agent | ✅ | ✅ `pre_llm_call` (first turn) | ✅ `pre_verify` | — |
| DeepSeek Harness | ✅ | ✅ `systemPrompt` context | via the context reminder | — |
| Cursor | ✅ | — | — | — |

## Measure effectiveness

Repeat a task class a week later and count how much steering it still needs.
Fewer corrections = the loop is working.

## Development

```
npm test               # DSH plugin (node:test) + Hermes plugin + hook contract (unittest)
npm run version:check  # every platform manifest matches package.json
```

## Releasing

Releases are automated by `.github/workflows/release.yml`:

1. Bump the version: `npm version minor` (syncs all manifests via `scripts/sync-version.mjs`).
2. Merge the change to `main` (`git push --follow-tags` is not needed — the workflow tags).
3. The workflow runs the tests, creates tag `vX.Y.Z` and a GitHub release with generated
   notes (categories in `.github/release.yml`), then publishes to npm with provenance.

npm auth uses trusted publishing (OIDC): configure it once at npmjs.com → package
settings → Trusted publisher (repo `DYNO-SOFT/self-improving-loop`, workflow
`release.yml`). An `NPM_TOKEN` repository secret is used instead when present.

## About

Built by [DYNO SOFT](https://dynosoft.md) — senior-led AI development studio:
autonomous agents, multi-agent orchestration, RAG, MCP servers, evals.
