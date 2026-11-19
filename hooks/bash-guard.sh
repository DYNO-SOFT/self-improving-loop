#!/usr/bin/env bash
# Bash tool guard for Claude Code.
#   bash-guard.sh ok    (PostToolUse on Bash)        — test-witness: a test/build
#                        command succeeded -> touch $SIL_DIR/test-witness
#   bash-guard.sh fail  (PostToolUseFailure on Bash) — error nudge: fix it or record
#                        the lesson, and do not claim done
# Never blocks the agent; any internal failure exits 0 silently.
set -uo pipefail
mode="${1:-ok}"
dir="${SIL_DIR:-$HOME/.claude/debug}"
mkdir -p "$dir" 2>/dev/null || exit 0

MODE="$mode" SIL_DIR="$dir" python3 "$(dirname "$0")/bash_guard.py" 2>/dev/null || true
exit 0
