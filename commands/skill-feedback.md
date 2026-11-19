---
description: Rate how a skill performed (good|bad) so the audit can spot degradation the telemetry misses.
argument-hint: <skill> <good|bad> [notes]
---

Record user feedback for a skill: `$ARGUMENTS` = `<skill> <good|bad> [notes]`.

1. If the skill name or rating is missing or the rating is not `good`/`bad`,
   ask for it; do not guess.
2. Append one JSON line to `${SIL_DIR:-~/.claude/debug}/skill-feedback.jsonl`
   (create the directory if needed):
   `{"ts":"<UTC ISO-8601>","skill":"<skill>","rating":"good|bad","notes":"<notes>"}`
3. Confirm with the line written. On `bad`, ask what went wrong and offer to
   amend the skill (with a versioned backup, see `/self-improve-audit`).
