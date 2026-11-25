"""Contract tests for the shell hooks (Claude Code + Codex output, telemetry, guards)."""
import json, os, subprocess, tempfile, time, unittest

HOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, script, *args, stdin="{}"):
        env = dict(os.environ, SIL_DIR=self.dir)
        p = subprocess.run(["bash", os.path.join(HOOKS, script), *args],
                           input=stdin, capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def path(self, name):
        return os.path.join(self.dir, name)

    def write_telemetry(self, n, age_days=0):
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_days * 86400))
        with open(self.path("skill-telemetry.jsonl"), "a") as f:
            for _ in range(n):
                f.write(json.dumps({"ts": ts, "event": "post", "skill": "x", "outcome": "success"}) + "\n")


class LifecycleHook(Base):
    def ctx(self, out, event):
        o = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(o["hookEventName"], event)
        return o["additionalContext"]

    def test_start_both_platforms(self):
        for platform in ("claude", "codex"):
            ctx = self.ctx(self.run_hook("self-improve-hook.sh", "start", platform), "SessionStart")
            self.assertIn("self-improve", ctx)
            self.assertIn("Load shared and legacy machine lessons", ctx)

    def test_audit_due_when_never_audited(self):
        self.write_telemetry(3)
        self.assertIn("audit is due (last: never, 3", self.ctx(self.run_hook("self-improve-hook.sh", "start"), "SessionStart"))

    def test_audit_not_due_after_recent_audit(self):
        self.write_telemetry(3, age_days=1)
        open(self.path("last-skill-audit"), "w").write(str(int(time.time())))
        self.assertNotIn("audit is due", self.ctx(self.run_hook("self-improve-hook.sh", "start"), "SessionStart"))

    def test_audit_due_after_50_uses(self):
        open(self.path("last-skill-audit"), "w").write("0")
        os.utime(self.path("last-skill-audit"), (time.time() - 3600,) * 2)
        self.write_telemetry(50)
        self.assertIn("audit is due", self.ctx(self.run_hook("self-improve-hook.sh", "start"), "SessionStart"))

    def test_stop_claude(self):
        ctx = self.ctx(self.run_hook("self-improve-hook.sh", "stop", "claude"), "Stop")
        self.assertIn("self-improve audit", ctx)
        self.assertIn("~/.self-improving-loop/LEARNED.md for machine lessons", ctx)

    def test_stop_codex_blocks_once(self):
        out = json.loads(self.run_hook("self-improve-hook.sh", "stop", "codex"))
        self.assertEqual(out["decision"], "block")
        self.assertIn("~/.self-improving-loop/LEARNED.md for machine lessons", out["reason"])

    def test_stop_guard_prevents_loop(self):
        for platform in ("claude", "codex"):
            for payload in ('{"stop_hook_active":true}', '{"stop_hook_active": true}'):
                self.assertEqual(self.run_hook("self-improve-hook.sh", "stop", platform, stdin=payload), "")

    def test_witness_warns_on_unbacked_claim(self):
        out = self.run_hook("self-improve-hook.sh", "stop", "claude",
                            stdin=json.dumps({"last_assistant_message": "Done, all verified."}))
        self.assertIn("Test-witness", self.ctx(out, "Stop"))

    def test_witness_quiet_after_recent_test_run(self):
        open(self.path("test-witness"), "w").write("npm test\n")
        out = self.run_hook("self-improve-hook.sh", "stop", "claude",
                            stdin=json.dumps({"last_assistant_message": "Done, all verified."}))
        self.assertNotIn("Test-witness", self.ctx(out, "Stop"))

    def test_witness_reads_claude_transcript(self):
        tr = self.path("t.jsonl")
        with open(tr, "w") as f:
            f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": "Tests pass, verified."}]}}) + "\n")
        out = self.run_hook("self-improve-hook.sh", "stop", "claude", stdin=json.dumps({"transcript_path": tr}))
        self.assertIn("Test-witness", self.ctx(out, "Stop"))

    def test_codex_skips_claude_only_checks(self):
        self.write_telemetry(60)
        start = json.loads(self.run_hook("self-improve-hook.sh", "start", "codex"))
        self.assertNotIn("audit is due", start["hookSpecificOutput"]["additionalContext"])
        out = self.run_hook("self-improve-hook.sh", "stop", "codex",
                            stdin=json.dumps({"last_assistant_message": "all verified"}))
        self.assertNotIn("Test-witness", json.loads(out)["reason"])

    def test_stop_silent_on_unreadable_input(self):
        for bad in ("not json", "[1]", ""):
            for platform in ("claude", "codex"):
                self.assertEqual(self.run_hook("self-improve-hook.sh", "stop", platform, stdin=bad), "")

    def test_start_survives_odd_telemetry(self):
        with open(self.path("skill-telemetry.jsonl"), "w") as f:
            f.write("2026-01-01T00:00:00Z\tpost\tx\n123\n{\"event\":\"post\"}\n")
        self.write_telemetry(2)
        ctx = json.loads(self.run_hook("self-improve-hook.sh", "start"))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("audit is due", ctx)

    def test_witness_reads_long_transcript_tail(self):
        tr = self.path("t.jsonl")
        with open(tr, "w") as f:
            f.write(json.dumps({"message": {"role": "assistant", "content": "x" * 300000}}) + "\n")
            f.write(json.dumps({"message": {"role": "assistant", "content": "verified " + "y" * 70000}}) + "\n")
        out = self.run_hook("self-improve-hook.sh", "stop", "claude", stdin=json.dumps({"transcript_path": tr}))
        self.assertIn("Test-witness", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_default_platform_is_claude(self):
        self.assertIn("hookSpecificOutput", self.run_hook("self-improve-hook.sh", "stop"))


class Telemetry(Base):
    def lines(self):
        with open(self.path("skill-telemetry.jsonl")) as f:
            return [json.loads(l) for l in f]

    def test_json_lines_with_outcomes(self):
        self.run_hook("skill-telemetry.sh", "pre", stdin=json.dumps({"tool_input": {"skill": "a"}}))
        self.run_hook("skill-telemetry.sh", "post", stdin=json.dumps({"tool_input": {"skill": "a"}, "tool_response": {"result": "ok"}}))
        self.run_hook("skill-telemetry.sh", "post", stdin=json.dumps({"tool_input": {"skill": "a"}, "tool_response": {"is_error": True, "error": "boom"}}))
        self.run_hook("skill-telemetry.sh", "post", stdin=json.dumps({"tool_input": {"skill": "a"}, "tool_response": ""}))
        rows = self.lines()
        self.assertEqual([r["event"] for r in rows], ["pre", "post", "post", "post"])
        self.assertNotIn("outcome", rows[0])
        self.assertEqual([r["outcome"] for r in rows[1:]], ["success", "error", "empty"])
        self.assertEqual(rows[2]["error"], "boom")

    def test_garbage_input_never_fails(self):
        self.run_hook("skill-telemetry.sh", "post", stdin="not json")
        self.assertEqual(self.lines()[0]["skill"], "unknown")


class BashGuard(Base):
    def test_failure_nudge(self):
        out = json.loads(self.run_hook("bash-guard.sh", "fail", stdin=json.dumps({"tool_input": {"command": "ls x"}})))
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUseFailure")

    def test_witness_for_test_runners(self):
        for cmd in ("npm test", "cd app && pytest -q", "python3 -m unittest discover", "go test ./...", "cargo test"):
            if os.path.exists(self.path("test-witness")):
                os.remove(self.path("test-witness"))
            self.assertEqual(self.run_hook("bash-guard.sh", "ok", stdin=json.dumps({"tool_input": {"command": cmd}})), "")
            self.assertTrue(os.path.exists(self.path("test-witness")), cmd)

    def test_witness_for_multiline_command(self):
        self.run_hook("bash-guard.sh", "ok", stdin=json.dumps({"tool_input": {"command": "cd app\nnpm test"}}))
        self.assertTrue(os.path.exists(self.path("test-witness")))

    def test_no_witness_when_result_is_masked(self):
        for cmd in ("pytest -q 2>&1 | tail -5", "npm test || true", "cargo test | grep ok"):
            self.run_hook("bash-guard.sh", "ok", stdin=json.dumps({"tool_input": {"command": cmd}}))
        self.assertFalse(os.path.exists(self.path("test-witness")))

    def test_no_witness_for_other_commands(self):
        for cmd in ("ls -la", "bash -n hooks/x.sh", "echo pytest is great", "cat test.py",
                    'git commit -m "wip; pytest later"', "git commit -m 'x && npm test'", "makefile-lint"):
            self.run_hook("bash-guard.sh", "ok", stdin=json.dumps({"tool_input": {"command": cmd}}))
        self.assertFalse(os.path.exists(self.path("test-witness")))


if __name__ == "__main__":
    unittest.main()
