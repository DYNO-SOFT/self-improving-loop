#!/usr/bin/env bash
# Lifecycle hook for Claude Code and OpenAI Codex.
#   self-improve-hook.sh <start|stop> [claude|codex]
# The platform argument selects the output contract; it defaults to claude.
#
# start: "self-improvement is active" context, plus an audit-due reminder when the
#        last /self-improve-audit is 7+ days old or 50+ skill uses ago.
# stop:  "run the audit before you finish" — once per turn (stop_hook_active guard).
#        If the reply claims verified/fixed/passing but no test or build command
#        has succeeded in the last 30 minutes (test-witness), it says so.
set -uo pipefail
event="${1:-start}"
platform="${2:-claude}"
dir="${SIL_DIR:-$HOME/.claude/debug}"

EVENT="$event" PLATFORM="$platform" SIL_DIR="$dir" python3 -c '
import calendar, json, os, sys, time

event, platform, d = os.environ["EVENT"], os.environ["PLATFORM"], os.environ["SIL_DIR"]
AUDIT_DAYS, AUDIT_USES, WITNESS_MIN = 7, 50, 30
try:
    data = json.load(sys.stdin)
except Exception:
    data = None
if not isinstance(data, dict):
    # Unreadable input: on stop we cannot see stop_hook_active, so stay silent
    # rather than risk a loop.
    if event == "stop":
        sys.exit(0)
    data = {}
# Skill telemetry and the test-witness are written by Claude Code hooks only;
# on Codex they would describe another agent, so those checks are Claude-only.
claude = platform != "codex"

def age_s(path):
    try:
        return time.time() - os.path.getmtime(path)
    except OSError:
        return None

def emit(name, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}}))

if event != "stop":
    msg = ("Self-improvement is active this session. Before finalizing work, run the "
           "self-improve skill: audit for cognitive errors and capture durable lessons "
           "so future sessions need less steering.")
    marker = os.path.join(d, "last-skill-audit")
    age = age_s(marker)
    uses = 0
    if claude:
        since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.path.getmtime(marker))) if age is not None else ""
        try:
            with open(os.path.join(d, "skill-telemetry.jsonl"), encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue          # legacy TSV lines
                    # ISO-8601 UTC strings compare correctly as text: no parsing needed.
                    if isinstance(r, dict) and r.get("event") == "post" and str(r.get("ts", "")) > since:
                        uses += 1
        except OSError:
            pass
    if uses and (age is None or age > AUDIT_DAYS * 86400 or uses >= AUDIT_USES):
        when = "never" if age is None else "%d days ago" % (age // 86400)
        msg += (" Skill audit is due (last: %s, %d skill uses since): run "
                "/self-improve-audit when this task is done." % (when, uses))
    emit("SessionStart", msg)
    sys.exit(0)

# Stop: fire once per turn. Both Claude Code and Codex send stop_hook_active.
if data.get("stop_hook_active"):
    sys.exit(0)

msg = ("Before you finish: run the self-improve audit (verify every claim — executed? "
       "exit code checked? number, not a guess?) and save any durable lesson (fact -> "
       "~/.claude/LEARNED.md or <repo>/AGENTS.md; repeatable procedure -> a skill). "
       "State in your final answer what you verified and saved.")

def last_reply():
    if data.get("last_assistant_message"):
        return str(data["last_assistant_message"])
    path = data.get("transcript_path")
    try:
        with open(path, "rb") as f:
            f.seek(0, 2); size = f.tell(); f.seek(max(0, size - 262144))
            lines = f.read().decode("utf-8", "replace").splitlines()
        if size > 262144:
            lines = lines[1:]   # first line is cut mid-record
    except (OSError, TypeError):
        return ""
    for line in reversed(lines):
        try:
            m = json.loads(line).get("message") or {}
        except ValueError:
            continue
        if m.get("role") == "assistant":
            c = m.get("content")
            return c if isinstance(c, str) else " ".join(
                p.get("text", "") for p in c or [] if isinstance(p, dict))
    return ""

CLAIMS = ("verified", "tests pass", "all tests", "is fixed", "works now", "проверено", "тесты прошли")
witness = age_s(os.path.join(d, "test-witness"))
if claude and (witness is None or witness > WITNESS_MIN * 60) and any(c in last_reply().lower() for c in CLAIMS):
    msg += (" Test-witness: the reply claims verification, but no test or build command "
            "succeeded in the last %d minutes — run it or drop the claim." % WITNESS_MIN)

if platform == "codex":
    # Codex Stop output has no additionalContext; "block" + reason continues the turn once.
    print(json.dumps({"decision": "block", "reason": msg}))
else:
    emit("Stop", msg)
' 2>/dev/null || exit 0
