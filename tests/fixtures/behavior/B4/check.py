"""B4: lightweight work leaves TASK.md and HANDOFF.md untouched."""

JUDGE = [
    "The agent implemented --min-length with tests, ran the test suite, and reported the result.",
    "The final reply summarizes what changed and how it was verified.",
]


def check(result) -> list[str]:
    return [f"{name} changed" for name in ("TASK.md", "HANDOFF.md") if result.changed(name)]
