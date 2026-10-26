"""B10: judged only (AC-3); records how each skill is invoked in the tool."""

SKILLS = ["resume", "handoff", "bootstrap", "start-task", "review", "accept"]

JUDGE = [
    f"Invocation syntax recorded for each skill: {', '.join(SKILLS)}, including any a built-in command "
    "overrides and the plain-language form that works instead.",
    "Duplicates recorded: whether any skill is listed more than once in the agent's answer or the tool's menu.",
    "Double-loading recorded: whether invoking a skill loads the pointer's content and then the canonical "
    ".agents/skills/<name>/SKILL.md once, or loads either twice.",
]


def check(result) -> list[str]:
    return []
