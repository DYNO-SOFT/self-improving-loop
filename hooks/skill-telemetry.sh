#!/usr/bin/env bash
# Skill telemetry for Claude Code (PreToolUse / PostToolUse on the Skill tool).
#   skill-telemetry.sh <pre|post>
# Appends one JSON line per event to $SIL_DIR/skill-telemetry.jsonl
# (default ~/.claude/debug):
#   {"ts": "...", "event": "pre|post", "skill": "...", "outcome": "success|error|empty", "error": "..."}
# outcome/error are written on post only; they feed the degradation audit.
# Never blocks the agent: any failure is swallowed and the hook exits 0.
set -uo pipefail
dir="${SIL_DIR:-$HOME/.claude/debug}"
mkdir -p "$dir" 2>/dev/null || exit 0
EVENT="${1:-pre}" OUT="$dir/skill-telemetry.jsonl" python3 -c '
import json, os, sys, time
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
ti = d.get("tool_input") or {}
rec = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "event": os.environ["EVENT"],
    "skill": (ti.get("skill") if isinstance(ti, dict) else None) or "unknown",
}
if rec["event"] == "post":
    r = d.get("tool_response")
    text = r if isinstance(r, str) else json.dumps(r) if r is not None else ""
    failed = isinstance(r, dict) and (r.get("is_error") or r.get("error") or r.get("success") is False)
    if failed:
        rec["outcome"] = "error"
        rec["error"] = str(r.get("error") or r.get("message") or text)[:200]
    elif text.strip() in ("", "{}", "[]", "null"):
        rec["outcome"] = "empty"
    else:
        rec["outcome"] = "success"
with open(os.environ["OUT"], "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
' 2>/dev/null || true
exit 0
