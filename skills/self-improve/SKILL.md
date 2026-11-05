---
name: self-improve
description: Run before finalizing any session with real work, and whenever the agent is about to claim something is done, fixed, or verified — to (1) audit for cognitive errors (unverified claims, missing exit-code checks, stale assumptions, unproven works) and (2) capture durable lessons so future sessions need less steering. Also run after the user corrects the agent.
---

# Self-Improve (self-learning + cognitive-error guard)

Weights do not change between sessions; improvement happens at the agent layer:
durable memory + reusable skills + verification habits. This skill closes the loop
and catches the mistakes that cost time twice. Every serious task should leave
behind better operating context: a durable memory, a corrected preference, or a
reusable skill.

## The loop (Hermes-style)

1. Understand the task; inspect the real environment with tools, not guesses.
2. Act with tools.
3. Verify — run the thing with a real test, browser check, or command output;
   check the exit code. A syntax/lint check is not a run.
4. Save durable facts as memory.
5. Convert a repeatable procedure into (or patch) a skill.
6. Next run, load memory + skill automatically before acting.

## Cognitive-error audit (run before claiming done)

Answer each before saying done, fixed, works, or verified:

- Did I actually execute it? If not, say so. `Verified:` only when the command
  ran and its exit code was checked.
- Numbers, not adjectives: did I state the measured result, not a guess?
- Did I check every exit code, including the ones that look fine?
- Is the config actually picked up? Prove the running thing changed, not just
  the file. A switch set in one shell is not state.
- Did I reproduce the fixed state? A verification that never re-enters the
  broken state proves nothing.
- Did I execute every branch the change adds, including the fresh-checkout one?
- Is any statement stale? Did the environment change since I learned it?
- Did I widen scope silently? Say what was left undone.
- Did I treat removing or trusting something as a claim and check references?

If any answer is no, fix the claim or the verification before finishing.

## Routing: fact vs procedure

- Durable FACT (preference, env path, quota, tool quirk, a correction) -> memory:
  machine-wide -> `~/.claude/LEARNED.md`; project-wide -> `<repo>/AGENTS.md`.
- Repeatable PROCEDURE (multi-step workflow, checklist, commands, known failures)
  -> a skill under `~/.claude/skills/<name>/SKILL.md` (frontmatter name + description).

## Claude Code auto-memory (curate, do not duplicate)

Claude Code 2.1.x already writes an auto-memory: MEMORY.md plus topic files. Do
not re-invent it — curate it on every review:

1. Review MEMORY.md for candidates worth promoting, stale entries, and duplicates.
2. Promote a proven pattern that recurs 2-3 times: MEMORY.md (background
   context) -> CLAUDE.md (enforced instruction) or .claude/rules/<topic>.md
   (scoped rule).
3. Extract a recurring fix into its own skill.
4. Prune stale or duplicate entries immediately.

Do not write the same fact into three places. Machine-level lessons go to
~/.claude/LEARNED.md; project-level go to <repo>/AGENTS.md, and MEMORY.md only
when the fact is that project own.

## Skills degrade — observe and repair

A skill is a static file in a dynamic environment: it degrades silently when its
commands, paths, or assumptions go stale. Close the loop instead of trusting it:

1. OBSERVE — telemetry logs every skill use to ~/.claude/debug/skill-telemetry.jsonl.
2. INSPECT — audit: usage frequency, unused or stale skills, failure patterns.
3. AMEND — edit the skill from evidence, keeping a backup before changing it.
4. EVALUATE — re-run the task and confirm the amendment actually helped.

When a skill misbehaves, amend it immediately (with a backup) rather than working
around it; a broken skill is worse than no skill.

## What to save / what NOT to save

Save: user communication preferences and corrections you should not repeat,
stable environment paths, deploy/run conventions, tool quirks and integration
gotchas. A correction the user already made is the highest-value memory — save it
first, so they never have to make it twice.
Do NOT save: temporary task progress, PR numbers, stale run logs, raw secrets,
anything that expires quickly. If the lesson is a procedure, make it a skill, not
a memory note.

## Match effort to task

A small formatting edit should not burn the same reasoning budget as a multi-repo
debugging task. Spend thinking depth in proportion to the size and risk of the job.

## Memory rules

1. Read the target file before appending; never overwrite.
2. One lesson = one short bullet under `## <topic> (learned YYYY-MM-DD)`.
3. Exact ids, codes, slugs, ports; `Verified:` only when executed.
4. Dedupe and prune: extend instead of repeating; remove contradictory entries.
5. Keep additions under ~12 lines; no secrets or tokens.

## Skill rules (procedures)

1. Create a skill only for a workflow likely to recur and multi-step.
2. Include commands, paths, known failures, and the verification step.
3. Patch the skill immediately when a command in it stops working.

## Failure modes to avoid

- Saving too much, or saving run logs instead of preferences.
- Citing stale facts after the environment changed.
- Claiming success without testing.
- Treating "I remembered it in-session" as learning — if it is not in a file a
  future session loads, it is not persisted.

## After running

State in the final answer: what was verified, what fact was saved where, whether
a skill was created or patched. Success = less steering on the next similar task.