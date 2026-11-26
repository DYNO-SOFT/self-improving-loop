"""Smoke test for the Hermes plugin with a mock ctx (no Hermes runtime needed)."""
import importlib.util, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("hermes_plugin", os.path.join(ROOT, ".hermes-plugin", "__init__.py"))
plugin = importlib.util.module_from_spec(spec); spec.loader.exec_module(plugin)


class Ctx:
    def __init__(self): self.skills, self.hooks = {}, {}
    def register_skill(self, name, path): self.skills[name] = path
    def register_hook(self, name, fn): self.hooks[name] = fn


class HermesPluginTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Ctx(); plugin.register(self.ctx)

    def test_registers_skill_and_hooks(self):
        self.assertIn("self-improve", self.ctx.skills)
        self.assertEqual(set(self.ctx.hooks), {"pre_llm_call", "pre_verify"})

    def test_bootstrap_only_on_first_turn(self):
        first = self.ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertIn(plugin.BOOTSTRAP_MARKER, first["context"])
        self.assertIn("~/.self-improving-loop/projects/<project-id>/LEARNED.md", first["context"])
        self.assertIn("Read legacy files only for an explicit migration or memory audit.", first["context"])
        self.assertIsNone(self.ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_pre_verify_nudges(self):
        out = self.ctx.hooks["pre_verify"](session_id="s")
        self.assertEqual(out["action"], "continue")
        self.assertIn("self-improve audit", out["message"])
        self.assertIn("shared or project learned file specified by the self-improve skill", out["message"])


if __name__ == "__main__":
    unittest.main()
