"""Contract tests for hooks/self-improve-hook.sh (Claude Code + Codex output)."""
import json, os, subprocess, unittest

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks", "self-improve-hook.sh")


def run(*args, stdin="{}"):
    p = subprocess.run(["bash", HOOK, *args], input=stdin, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


class HookScriptTest(unittest.TestCase):
    def test_start_both_platforms(self):
        for platform in ("claude", "codex"):
            out = json.loads(run("start", platform))["hookSpecificOutput"]
            self.assertEqual(out["hookEventName"], "SessionStart")
            self.assertIn("self-improve", out["additionalContext"])

    def test_stop_claude(self):
        out = json.loads(run("stop", "claude"))["hookSpecificOutput"]
        self.assertEqual(out["hookEventName"], "Stop")

    def test_stop_codex_blocks_once(self):
        out = json.loads(run("stop", "codex"))
        self.assertEqual(out["decision"], "block")
        self.assertTrue(out["reason"])

    def test_stop_guard_prevents_loop(self):
        for platform in ("claude", "codex"):
            for payload in ('{"stop_hook_active":true}', '{"stop_hook_active": true}'):
                self.assertEqual(run("stop", platform, stdin=payload), "")

    def test_default_platform_is_claude(self):
        self.assertIn("hookSpecificOutput", run("stop"))


if __name__ == "__main__":
    unittest.main()
