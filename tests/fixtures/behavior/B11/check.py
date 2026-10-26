"""B11: interrupted lightweight work escalates to a standard task without being told to."""

JUDGE = [
    "TASK.md states the --json option as the goal (from the diff, confirmed with the user if the agent asked), "
    "and HANDOFF.md's next steps finish it: print the report and add tests.",
    "The agent wrote both files without being told to, and did not commit.",
]


def check(result) -> list[str]:
    failures = [f"{name} is still neutral" for name in ("TASK.md", "HANDOFF.md") if result.neutral(name)]
    ok, output = result.state_check()
    if not ok:
        failures.append("state.py check reports violations:\n    " + output.replace("\n", "\n    "))
    return failures
