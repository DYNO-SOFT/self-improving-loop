#!/usr/bin/env bash
set -euo pipefail
event="$1"
if [ "$event" = "stop" ]; then
  name="Stop"
  msg="Before you finish: run the self-improve audit (verify every claim — executed? exit code checked? number, not a guess?) and save any durable lesson (fact -> ~/.claude/LEARNED.md or <repo>/AGENTS.md; repeatable procedure -> a skill). State in your final answer what you verified and saved."
else
  name="SessionStart"
  msg="Self-improvement is active this session. Before finalizing work, run the self-improve skill: audit for cognitive errors and capture durable lessons so future sessions need less steering."
fi
printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}' "$name" "$msg"
echo