---
description: Roll a skill back to a previous version saved by an amendment.
argument-hint: <skill> [version]
---

Roll back a skill: `$ARGUMENTS` = `<skill> [version]`.

1. Find the skill dir (`~/.claude/skills/<skill>/` or `<repo>/.claude/skills/<skill>/`)
   and its `versions/manifest.jsonl`. No versions → say so and stop.
2. List the versions (v, date, reason). Without a version argument, ask which one.
3. Back up the current `SKILL.md` first as the next version, with reason
   `"pre-rollback to v<N>"`, so the rollback itself can be undone.
4. Copy `versions/SKILL.md.v<N>` over `SKILL.md` and show the diff.
5. Append `{"v":<new>,"ts":"<UTC>","reason":"rollback to v<N>"}` to the manifest.
