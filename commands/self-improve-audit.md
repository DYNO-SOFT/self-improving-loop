---
description: Audit skills and memory health using telemetry — find unused/stale/degraded skills, promotion candidates and dead references.
---

Run a self-improvement health audit. Show evidence before changing anything.

## 1. Skill health (from telemetry)

Read `~/.claude/debug/skill-telemetry.jsonl` (one JSON object per line:
`ts`, `event` pre|post, `skill`, and on post `outcome` success|error|empty, `error`).
Skip lines that are not JSON (older versions wrote TSV).

Per skill, from `post` events: uses, last used, error rate, empty rate. Add
ratings from `~/.claude/debug/skill-feedback.jsonl` (`/skill-feedback`).

| Status | Rule |
|---|---|
| degraded | ≥ 10 uses and error rate > 20%, or ≥ 2 `bad` ratings |
| stale | not used for 30+ days |
| archive candidate | not used for 90+ days and no `pinned: true` in its frontmatter |
| healthy | everything else |

Health score 0-100 = 100 − 2×error% − empty% − 10×bad ratings (floor 0).

## 2. Evaluate past amendments

For each skill with `versions/manifest.jsonl`, compare the error rate before and
after the latest amendment date. Fewer than 10 uses on either side → "insufficient
data". Report improved / regressed / unchanged; offer `/skill-rollback` on regressions.

## 3. Memory health

- Capacity: line count of each MEMORY.md (warn ≥ 150, the loader caps at 200),
  `~/.claude/LEARNED.md`, project `AGENTS.md`.
- Dead references: every path or file name mentioned in those files that no
  longer exists (`test -e`). Report them; prune after confirmation.
- Duplicates and contradictions between the files.
- Promotion candidates: score each recurring entry with the rubric in the
  self-improve skill (promote at ≥ 6/9).
- Entries marked `(agent, unreviewed)`: list them for the user to confirm or drop.

## 4. Report, then act

Print one table (skill | uses | errors | score | status) and the memory findings.
Then offer, one at a time and with evidence: amend, archive, promote, prune.

- Amend → back up first: copy `SKILL.md` to `<skill>/versions/SKILL.md.v<N>` (next
  free N) and append `{"v":N,"ts":"<UTC>","reason":"<why>"}` to
  `<skill>/versions/manifest.jsonl`. Keep the 5 most recent versions.
- Archive → move the skill dir to `~/.claude/skills/.archive/` (never delete).

## 5. Mark the audit done

`date +%s > ~/.claude/debug/last-skill-audit` — the SessionStart hook uses it to
remind you when the next audit is due (7 days or 50 skill uses).
