"""Logic for bash-guard.sh (kept in a file: inline python cannot hold shell quotes)."""
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
# A test or build runner at the start of a command segment (after newline ; && || |),
# optionally behind VAR=x / npx / uv run / poetry run. Lint/syntax-only checks do not
# count. Quoted strings are blanked first ("git commit -m 'pytest later'" is not a run).
RUNNER = re.compile(r"(^|[;&|\n])\s*(\w+=\S*\s+)*(npx\s+|uv run\s+|poetry run\s+)?(npm (run )?test|pnpm (run )?test|yarn test|bun test|"
    r"node --test|pytest|python3? -m (pytest|unittest)|go test|cargo (test|build)|"
    r"mvn (test|verify)|gradle(w)? (test|build)|dotnet (test|build)|make( test| check)?(?=\s|$)|"
    r"ctest|rspec|phpunit|vitest|jest|npm run build|pnpm (run )?build|tsc(?=\s|$))", re.M)
clean = re.sub(r"'[^']*'|\"(\\.|[^\"\\])*\"", "''", cmd)
for m in RUNNER.finditer(clean):
    # The tool succeeded, but that is the exit code of the LAST command. If the runner
    # is piped (| tail) or its failure is swallowed (|| true), its own result is unknown.
    nxt = re.search(r"\|\||&&|[;|\n]", clean[m.end():])
    if nxt and nxt.group() in ("|", "||"):
        continue
    with open(os.path.join(os.environ["SIL_DIR"], "test-witness"), "w") as f:
        f.write(cmd[:300] + "\n")
    break
