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

MODE="$mode" SIL_DIR="$dir" python3 -c '
import json, os, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
cmd = str((data.get("tool_input") or {}).get("command") or "")
if os.environ["MODE"] == "fail":
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUseFailure",
        "additionalContext": "Command failed. Do not claim done: fix the cause or say it is "
            "unresolved. If the failure taught something durable (tool quirk, env path, "
            "wrong assumption), record it per the self-improve skill."}}))
    sys.exit(0)
# A test or build runner at the start of a command segment (after ; && || |),
# optionally behind VAR=x / npx / uv run / poetry run. Lint/syntax-only checks do not count.
RUNNER = re.compile(r"(^|[;&|])\s*(\w+=\S*\s+)*(npx\s+|uv run\s+|poetry run\s+)?(npm (run )?test|pnpm (run )?test|yarn test|bun test|"
    r"node --test|pytest|python3? -m (pytest|unittest)|go test|cargo (test|build)|"
    r"mvn (test|verify)|gradle(w)? (test|build)|dotnet (test|build)|make( test| check)?$|"
    r"ctest|rspec|phpunit|vitest|jest|npm run build|pnpm (run )?build|tsc( |$))")
if RUNNER.search(cmd):
    open(os.path.join(os.environ["SIL_DIR"], "test-witness"), "w").write(cmd[:300] + "\n")
' 2>/dev/null || true
exit 0
