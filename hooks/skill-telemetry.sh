#!/usr/bin/env bash
# Log every Skill invocation (PreToolUse) and outcome (PostToolUse).
set -euo pipefail
event="$1"
dir="$HOME/.claude/debug"
mkdir -p "$dir"
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
name=$(cat | python3 -c 'import sys,json; d=json.load(sys.stdin); ti=d.get("tool_input") or {}; print(ti.get("skill","") if isinstance(ti,dict) else "")' 2>/dev/null || true)
printf "%s\t%s\t%s\n" "$ts" "$event" "${name:-unknown}" >> "$dir/skill-telemetry.jsonl"
exit 0