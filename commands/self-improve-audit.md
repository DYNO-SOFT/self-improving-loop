---
description: Audit skills and memory health using telemetry — find unused/stale skills, degradation and promotion candidates.
---

Run a self-improvement health audit:

1. Read `~/.claude/debug/skill-telemetry.jsonl` and count uses per skill.
2. Flag: skills unused for a long time, failing skills, memory entries worth
   promoting to CLAUDE.md or .claude/rules/, stale or duplicate notes.
3. Report a short health table, then offer to amend (with backup), promote, or
   extract. Do not change anything without showing the evidence first.

Before amending a skill, back it up (cp to a .bak next to it).