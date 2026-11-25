# DeepSeek Harness (DSH) install

The self-improvement loop ships as a DSH agent skill (filesystem provider at
~/.agents/skills), plus a machine-notes loop that DSH loads every session.

## Install

1. Symlink the skill (single source of truth — no copy drift):

   mkdir -p ~/.agents/skills
   ln -sfn "$(pwd)/skills/self-improve" ~/.agents/skills/self-improve

2. Ensure the machine-notes rule is present in ~/.dsh/AGENTS.md (the file DSH
   loads into every session):

   Load shared and legacy machine lessons as described in the self-improve
   skill. Before the final answer of any session that did real work, run the
   skill and save verified machine lessons to `~/.self-improving-loop/LEARNED.md` and project
   lessons to the repo `AGENTS.md`.

Prefer the native cordis plugin when you can use npm: `dsh plugin add
@dynosoft/self-improving-loop` registers the skill and a runtime reminder
context automatically (see the main README). The manual path above is for
installs without npm.
