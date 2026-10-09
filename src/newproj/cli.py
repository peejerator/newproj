"""Command-line entry point for newproj."""

import argparse
from importlib.metadata import version


def main() -> int:
    """Parse CLI arguments and run the selected command."""
    parser = argparse.ArgumentParser(
        prog="newproj",
        description="Create and adopt projects with repository-based state.",
    )
    parser.add_argument("--version", action="version", version=version("newproj"))
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command, description in (
        ("new", "Create a project"),
        ("adopt", "Adopt an existing project"),
        ("doctor", "Check project health"),
    ):
        subcommands.add_parser(command, help=description, description=description)

    args = parser.parse_args()
    print(f"newproj {args.command} is not implemented yet.")
    return 2
