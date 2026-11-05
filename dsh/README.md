# DeepSeek Harness (DSH) install

The self-improvement loop ships as a DSH agent skill (filesystem provider at
~/.agents/skills), plus a machine-notes loop that DSH loads every session.

## Install

1. Symlink the skill (single source of truth — no copy drift):

   mkdir -p ~/.agents/skills
   ln -sfn "$(pwd)/skills/self-improve" ~/.agents/skills/self-improve

2. Ensure the machine-notes rule is present in ~/.dsh/AGENTS.md (the file DSH
   loads into every session):

   Before the final answer of any session that did real work, run the
   self-improve skill and persist verified lessons (machine facts -> this file,
   project facts -> the repo AGENTS.md).

A native cordis plugin/bundle for DSH is not shipped here: it requires the DSH
source repository and its build chain, which are not part of this repo.
