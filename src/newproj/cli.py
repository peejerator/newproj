"""Command-line entry point for newproj."""

import argparse
import sys
from importlib.metadata import version

from newproj import adopt, doctor, new


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and run the selected command."""
    parser = argparse.ArgumentParser(
        prog="newproj",
        description="Create and adopt projects with repository-based state.",
    )
    parser.add_argument("--version", action="version", version=version("newproj"))
    subcommands = parser.add_subparsers(dest="command", required=True)
    commands = {}
    for command, description, module in (
        ("new", "Create a project", new),
        ("adopt", "Adopt an existing project", adopt),
        ("doctor", "Check project health", doctor),
    ):
        sub = subcommands.add_parser(command, help=description, description=description)
        module.add_arguments(sub)
        commands[command] = module.main

    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    return commands[args.command](args)
