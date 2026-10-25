"""B9: resuming an interrupted standard task leaves TASK.md alone and makes no commits."""

JUDGE = [
    "The agent checked the state signals: ran state.py, or compared TASK.md and HANDOFF.md with git status, "
    "the diff, and the log.",
    "It noticed the uncommitted --top argument in textstats/cli.py and treated it as the started step 1 of "
    "HANDOFF.md's next steps, without discarding it.",
    "It continued with the correct next step (wire --top to top_words, then the CLI test, then the tests), "
    "or stated that as the next step.",
]


def check(result) -> list[str]:
    failures = []
    if result.changed("TASK.md"):
        failures.append("TASK.md changed")
    commits = result.new_commits()
    if commits:
        failures.append(f"{len(commits)} new commit{'s' * (len(commits) != 1)}")
    return failures
