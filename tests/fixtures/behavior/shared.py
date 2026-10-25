"""Planted content shared by the behavioral fixtures: `textstats`, a small standard-library package."""

from __future__ import annotations

DESCRIPTION = (
    "`textstats` is a small command-line tool that reads a UTF-8 text file and prints its word count, then "
    "every word's frequency, most frequent first. Its author uses it to spot repeated words in drafts of short "
    "essays. It targets Python 3.9 or newer and uses only the standard library."
)

FILES = {
    "textstats/__init__.py": '''\
"""Word statistics for plain text."""

from textstats.core import frequencies, word_count, words

__all__ = ["frequencies", "word_count", "words"]
''',
    "textstats/__main__.py": '''\
from textstats.cli import main

raise SystemExit(main())
''',
    "textstats/core.py": '''\
"""Splitting text into words and counting them."""

from __future__ import annotations

import re
from collections import Counter

WORD = re.compile(r"[a-z']+")


def words(text: str) -> list[str]:
    """The lowercase words in text, in order."""
    return WORD.findall(text.lower())


def word_count(text: str) -> int:
    return len(words(text))


def frequencies(text: str) -> Counter[str]:
    return Counter(words(text))
''',
    "textstats/cli.py": '''\
"""Command line: python -m textstats FILE"""

from __future__ import annotations

import argparse

from textstats.core import frequencies, word_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="textstats", description="Report word statistics for a text file.")
    parser.add_argument("file", help="UTF-8 text file to read")
    args = parser.parse_args(argv)
    with open(args.file, encoding="utf-8") as handle:
        text = handle.read()
    print(f"words: {word_count(text)}")
    for word, count in sorted(frequencies(text).items(), key=lambda item: (-item[1], item[0])):
        print(f"{count:6d} {word}")
    return 0
''',
    "tests/__init__.py": "",
    "tests/test_core.py": '''\
import unittest

from textstats.core import frequencies, word_count, words


class CoreTest(unittest.TestCase):
    def test_words_are_lowercase(self) -> None:
        self.assertEqual(words("The cat, the hat."), ["the", "cat", "the", "hat"])

    def test_word_count(self) -> None:
        self.assertEqual(word_count("one two  three"), 3)
        self.assertEqual(word_count(""), 0)

    def test_frequencies(self) -> None:
        self.assertEqual(frequencies("a b a")["a"], 2)


if __name__ == "__main__":
    unittest.main()
''',
    "tests/test_cli.py": '''\
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from textstats.cli import main


class CliTest(unittest.TestCase):
    def run_cli(self, text: str, *args: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "input.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([path, *args]), 0)
            return out.getvalue()

    def test_report(self) -> None:
        self.assertEqual(self.run_cli("b a b"), "words: 3\\n     2 b\\n     1 a\\n")


if __name__ == "__main__":
    unittest.main()
''',
}


def fill_agents_md(project, description: str, test: str, run: str, conventions: str) -> None:
    """Replace the template's TODO lines in AGENTS.md with this project's facts."""
    project.replace("AGENTS.md", "TODO: describe the project in one paragraph.", description)
    project.replace("AGENTS.md", "- Build: TODO", "- Build: none (no build step)")
    project.replace("AGENTS.md", "- Test: TODO", f"- Test: {test}")
    project.replace("AGENTS.md", "- Run: TODO", f"- Run: {run}")
    project.replace("AGENTS.md", "- Lint and format: TODO (remove if not applicable)\n", "")
    project.replace("AGENTS.md",
                    "- TODO: language and style conventions, commit conventions, module boundaries, files not to "
                    "modify, platform constraints.", conventions)
    project.replace("AGENTS.md", "- TODO: areas that always count as formal tier for this project, if any.\n", "")


def ignore_bytecode(project) -> None:
    """Running the tests is read-only for the checks, so the bytecode it writes is ignored."""
    project.write(".gitignore", project.read(".gitignore") + "\n# Python\n__pycache__/\n")


def plant_textstats(project) -> None:
    ignore_bytecode(project)
    for rel, text in FILES.items():
        project.write(rel, text)
    fill_agents_md(
        project, DESCRIPTION,
        test="`python -m unittest discover -s tests` (on Windows, `py -3 -m unittest discover -s tests`)",
        run="`python -m textstats FILE`",
        conventions="- Python 3.9 or newer, standard library only; no third-party dependencies.",
    )
