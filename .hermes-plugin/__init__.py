import os
from pathlib import Path

BOOTSTRAP_MARKER = "self-improving-loop bootstrap for hermes"


def _skills_dir():
    here = os.path.dirname(os.path.realpath(__file__))
    for cand in (
        os.path.realpath(os.path.join(here, "..", "skills")),
        os.path.realpath(os.path.join(here, "skills")),
    ):
        if os.path.isfile(os.path.join(cand, "self-improve", "SKILL.md")):
            return cand
    raise RuntimeError(
        "self-improving-loop plugin: cannot find skills/ tree; reinstall with "
        "'hermes plugins install DYNO-SOFT/self-improving-loop'."
    )


def _strip_frontmatter(content):
    parts = content.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else content.strip()


def _build_bootstrap(skills_dir):
    with open(os.path.join(skills_dir, "self-improve", "SKILL.md"), encoding="utf-8") as f:
        body = _strip_frontmatter(f.read())
    return (
        "<SELF_IMPROVING>\n"
        + BOOTSTRAP_MARKER + "\n\n"
        + "Self-improvement is active this session. The self-improve skill is "
        + "loaded below; follow it before finalizing any work.\n\n"
        + body
        + "\n</SELF_IMPROVING>"
    )


def register(ctx):
    skills_dir = _skills_dir()
    for name in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, name, "SKILL.md")
        if os.path.isfile(skill_md):
            ctx.register_skill(name, Path(skill_md))

    def pre_llm_call(session_id=None, user_message=None, conversation_history=None,
                     is_first_turn=None, model=None, platform=None, **kwargs):
        if is_first_turn:
            return {"context": _build_bootstrap(skills_dir)}
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)
