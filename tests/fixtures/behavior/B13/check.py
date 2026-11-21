"""B13: resume the agreed local-only branch and activate the confirmed draft."""

import importlib.util
import re
from pathlib import Path

import start_task

_spec = importlib.util.spec_from_file_location("behavior_B13_draft", Path(__file__).with_name("setup.py"))
assert _spec and _spec.loader
_setup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_setup)
DRAFT = _setup.DRAFT

JUDGE = []


def criteria(text: str) -> list[str]:
    """Each acceptance criterion of a task, with whitespace normalized."""
    section = text.split("## Acceptance criteria\n", 1)[1].split("\n## ", 1)[0]
    return [" ".join(item.split()) for item in re.split(r"^- (?=AC-\d+:)", section, flags=re.M)[1:]]


def check(result) -> list[str]:
    failures = start_task.check(result)
    try:
        activated = criteria(result.project.read("TASK.md"))
    except IndexError:
        activated = []
    if activated != criteria(DRAFT):
        failures.append("activated criteria differ from the draft's settled criteria")
    return failures
