#!/usr/bin/env bash
# Lifecycle hook for Claude Code and OpenAI Codex.
#   self-improve-hook.sh <start|stop> [claude|codex]
# The platform argument selects the output contract; it defaults to claude.
set -euo pipefail
event="${1:-start}"
platform="${2:-claude}"

start_msg="Self-improvement is active this session. Before finalizing work, run the self-improve skill: audit for cognitive errors and capture durable lessons so future sessions need less steering."
stop_msg="Before you finish: run the self-improve audit (verify every claim — executed? exit code checked? number, not a guess?) and save any durable lesson (fact -> ~/.claude/LEARNED.md or <repo>/AGENTS.md; repeatable procedure -> a skill). State in your final answer what you verified and saved."

if [ "$event" = "stop" ]; then
  # Skip when this turn was already continued by a Stop hook (prevents an infinite loop).
  # Both Claude Code and Codex send stop_hook_active on stdin.
  input=$(cat || true)
  case "$input" in *'"stop_hook_active":true'*|*'"stop_hook_active": true'*) exit 0 ;; esac
  if [ "$platform" = "codex" ]; then
    # Codex Stop output has no additionalContext; "block" + reason continues the turn once.
    printf '{"decision":"block","reason":"%s"}\n' "$stop_msg"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"%s"}}\n' "$stop_msg"
  fi
else
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$start_msg"
fi
