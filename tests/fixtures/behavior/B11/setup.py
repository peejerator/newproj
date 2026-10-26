"""B11: lightweight work half done, no task (Status: none), and a dirty tree."""

from shared import plant_textstats

COMMIT_MESSAGE = "Add textstats"


def plant(project) -> None:
    plant_textstats(project)


def dirty(project) -> None:
    """A half-finished `--json` option: parsed and partly built, never printed, no tests."""
    project.replace("textstats/cli.py", "import argparse\n", "import argparse\nimport json\n")
    project.replace("textstats/cli.py", '''    parser.add_argument("file", help="UTF-8 text file to read")
''', '''    parser.add_argument("file", help="UTF-8 text file to read")
    parser.add_argument("--json", action="store_true", help="print the report as a JSON object")
''')
    project.replace("textstats/cli.py", '''        text = handle.read()
''', '''        text = handle.read()
    if args.json:
        report = {"words": word_count(text), "frequencies": dict(frequencies(text))}
        # TODO: print the report, sorted like the text output, and add tests.
''')
