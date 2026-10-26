"""B9: an interrupted standard task with a partial handoff and an uncommitted change."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add top_words"
BRANCH = "add-top-option"

TASK = '''\
# Task

Status: active
Tier: standard
Task ID:
Base commit: {base}
Target branch: main
Issue:
PR:

## Goal

Add a `--top N` option to textstats that prints only the N most frequent words.

## Context

- Requested by the user; spans sessions, so it runs as a standard task.

## Scope

- A `top_words` function in `textstats/core.py`, the `--top` option in `textstats/cli.py`, and their tests.
- Do not commit; the user commits.

## Acceptance criteria

- AC-1: `textstats.core.top_words(text, n)` returns the n most frequent words with their counts, most frequent first, ties in alphabetical order.
- AC-2: `python -m textstats FILE --top N` prints the word count line and then only the N most frequent words, in the existing format.
- AC-3: Tests cover AC-1 and AC-2, and `python -m unittest discover -s tests` passes.

## Relevant areas

- `textstats/core.py`, `textstats/cli.py`, `tests/`

## Validation

- `python -m unittest discover -s tests`

## Do not change

- The report format without `--top`.

## Open questions
'''

HANDOFF_STARTED = '''\
# Handoff

Last updated: {date} by an earlier agent session
Branch: add-top-option
Task: standard

## Status

not started

## Completed

## Current working area

## Validation

## Review

Outcome: none

## Exact next steps

1. Implement AC-1 to AC-3.

## Blockers / open questions

## Relevant decisions
'''

HANDOFF_PARTIAL = '''\
# Handoff

Last updated: {date} by an earlier agent session
Branch: add-top-option
Task: standard

## Status

in progress

## Completed

- AC-1: `top_words` added to `textstats/core.py`, with tests in `tests/test_core.py`.

## Current working area

- `textstats/core.py`
- `textstats/cli.py`
- `tests/test_cli.py`

## Validation

- PASS | python -m unittest discover -s tests | 6 passed, covers AC-1 | macOS | implementer

## Review

Outcome: none

## Exact next steps

1. Add the `--top N` option to `textstats/cli.py`, using `top_words` (AC-2).
2. Add a CLI test for `--top` to `tests/test_cli.py` (AC-3).
3. Run `python -m unittest discover -s tests` and update this handoff.

## Blockers / open questions

## Relevant decisions
'''

TOP_WORDS = '''

def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """The n most frequent words and their counts, most frequent first, ties in alphabetical order."""
    return sorted(frequencies(text).items(), key=lambda item: (-item[1], item[0]))[:n]
'''

TOP_WORDS_TESTS = '''
    def test_top_words(self) -> None:
        self.assertEqual(top_words("b a b c a b", 2), [("b", 3), ("a", 2)])

    def test_top_words_ties_are_alphabetical(self) -> None:
        self.assertEqual(top_words("y x z", 2), [("x", 1), ("y", 1)])
'''


def plant(project) -> None:
    plant_textstats(project)
    date = "2026-10-20"
    base = project.commit("Add textstats")
    project.git("switch", "--quiet", "-c", BRANCH)
    project.write("TASK.md", TASK.format(base=base))
    project.write("HANDOFF.md", HANDOFF_STARTED.format(date=date))
    project.commit("Start --top option")
    project.write("textstats/core.py", project.read("textstats/core.py") + TOP_WORDS)
    project.replace("tests/test_core.py", "from textstats.core import frequencies, word_count, words",
                    "from textstats.core import frequencies, top_words, word_count, words")
    project.replace("tests/test_core.py", '''        self.assertEqual(frequencies("a b a")["a"], 2)
''', '''        self.assertEqual(frequencies("a b a")["a"], 2)
''' + TOP_WORDS_TESTS)
    project.write("HANDOFF.md", HANDOFF_PARTIAL.format(date=date))


def dirty(project) -> None:
    """The interrupted session had started step 1: the option is parsed but not used yet."""
    project.replace("textstats/cli.py", '''    parser.add_argument("file", help="UTF-8 text file to read")
''', '''    parser.add_argument("file", help="UTF-8 text file to read")
    parser.add_argument("--top", type=int, metavar="N", help="print only the N most frequent words")
''')
