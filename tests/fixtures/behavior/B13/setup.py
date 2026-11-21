"""B13: resume a settled, uncommitted draft on its existing local-only task branch."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add textstats"
BRANCH = "add-min-length"

DRAFT = '''\
# Task

Status: draft
Tier: standard
Task ID:
Base commit:
Target branch:
Issue:
PR:

## Goal

Add a --min-length N option to textstats.

## Context

- Agreed task branch: add-min-length.
- Agreed target branch: main.
- User decisions: standard tier; keep words with length at least N before
  counting; N defaults to zero; reject negative N with argparse; preserve the
  existing output format and the behavior when the option is omitted.
- User decisions: automated core and CLI tests; python3 -m unittest discover -s tests.
- Every interview decision is settled. Final criteria confirmation is pending.

## Scope

- Change core filtering, CLI option handling, and tests only.
- The user makes every commit. Do not implement during the interview.

## Acceptance criteria

- AC-1: --min-length N excludes shorter words from word count and frequencies.
- AC-2: N is a nonnegative integer, defaults to zero, and negative values are
  rejected by argparse. Omission preserves existing output and behavior.
- AC-3: Automated core and CLI tests cover filtering, defaults, and invalid N;
  python3 -m unittest discover -s tests passes.

## Relevant areas

- textstats/core.py, textstats/cli.py, tests/test_core.py, tests/test_cli.py.

## Validation

- python3 -m unittest discover -s tests

## Do not change

- Existing report format and behavior when --min-length is omitted.

## Open questions

- None.
'''


def plant(project) -> None:
    plant_textstats(project)
    project.git("config", "init.defaultBranch", "main")
    project.git("switch", "--quiet", "-c", BRANCH)


def dirty(project) -> None:
    project.write("TASK.md", DRAFT)
