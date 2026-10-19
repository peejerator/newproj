"""`newproj new`: create a project from the template, commit it, and optionally publish it (spec section 20.1)."""

from __future__ import annotations

import argparse
import re
import sys
from importlib.metadata import version
from pathlib import Path

import copier

from newproj import source
from newproj.tools import git_config, run, which

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ANSWERS = ".copier-answers.yml"
HOOKS_PATH = ".githooks"
SET_HEAD = ["git", "remote", "set-head", "origin", "--auto"]


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("name", help="project name and directory (lowercase letters, digits, and hyphens)")
    parser.add_argument("--public", action="store_true", help="create the GitHub repository as public (default: private)")
    parser.add_argument("--no-remote", action="store_true", help="skip GitHub repository creation")
    parser.add_argument("--owner", help="GitHub user or organization (default: the authenticated gh user)")
    # Development and tests only (ERRATA E-002): render a local directory instead of the tagged template.
    parser.add_argument("--template-path", type=Path, help=argparse.SUPPRESS)


def shown(path: Path) -> str:
    text = str(path)
    return f'"{text}"' if " " in text else text


def command_line(args: list[str]) -> str:
    return " ".join(f'"{a}"' if " " in a else a for a in args)


def preflight(args: argparse.Namespace, target: Path) -> tuple[list[str], str]:
    """Problems that stop `new` before anything is written, and the GitHub owner."""
    problems = []
    if not NAME.fullmatch(args.name):
        problems.append(f"invalid project name {args.name!r}: use lowercase letters, digits, and single hyphens only")
    if target.exists() and not (target.is_dir() and not any(target.iterdir())):
        problems.append(f"{shown(target)} already exists and is not an empty directory")
    if args.template_path is not None and not (args.template_path / "copier.yml").is_file():
        problems.append(f"--template-path {shown(args.template_path)} has no copier.yml")
    if which("git") is None:
        problems.append("git is not installed or not on PATH (spec section 21)")
    else:
        for key in ("user.name", "user.email"):
            if not git_config(key):
                problems.append(f'Git {key} is not set: git config --global {key} "<{key.split(".")[1]}>"')
    owner = args.owner or ""
    if not args.no_remote:
        if which("gh") is None:
            problems.append("gh is not installed or not on PATH; install it (spec section 21) or pass --no-remote")
        elif not run("gh", "auth", "status").ok:
            problems.append("gh is not authenticated: run gh auth login, or pass --no-remote")
        elif not owner:
            result = run("gh", "api", "user", "--jq", ".login")
            owner = result.out if result.ok else ""
            if not owner:
                problems.append(f"could not read the GitHub user from gh api user ({result.err or 'empty reply'}); "
                                "pass --owner")
    return problems, owner


def render(args: argparse.Namespace, target: Path) -> None:
    """Run `copier copy` at the CLI's tag, or from --template-path. Runs no Copier tasks (spec 19.3)."""
    interactive = sys.stdin.isatty()
    if not interactive:
        print("stdin is not a terminal: using the template's default answers.")
    options = dict(data={"project_name": args.name}, defaults=not interactive, skip_tasks=True)
    if args.template_path is not None:
        copier.run_copy(str(args.template_path.resolve()), target, **options)
        return
    tag = source.tag()
    clone = source.template_clone(tag)
    copier.run_copy(str(clone), target, vcs_ref=tag, **options)
    # Record the repository URL, not this machine's cache path, so the answers file
    # works on every machine and leaks no local path.
    answers = target / ANSWERS
    lines = answers.read_bytes().decode("utf-8").splitlines(keepends=True)
    lines = [f"_src_path: {source.TEMPLATE_URL}\n" if line.startswith("_src_path:") else line for line in lines]
    answers.write_bytes("".join(lines).encode("utf-8"))


def generated_files(target: Path) -> list[str]:
    """Every file Copier wrote; the target was absent or empty before rendering."""
    return sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())


def git_or_fail(target: Path, *args: str, capture: bool = True) -> None:
    result = run("git", *args, cwd=target, capture=capture)
    if not result.ok:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.err or f'exit code {result.code}'}")


def commit(target: Path, files: list[str]) -> str:
    message = f"Initialize from project-template v{version('newproj')}"
    git_or_fail(target, "init", "--quiet", "-b", "main")
    git_or_fail(target, "config", "core.hooksPath", HOOKS_PATH)
    for start in range(0, len(files), 100):
        git_or_fail(target, "add", "--", *files[start:start + 100])
    git_or_fail(target, "commit", "--quiet", "-m", message, capture=False)
    return message


def publish(args: argparse.Namespace, owner: str, target: Path) -> int:
    """Create the GitHub repository, push, and set origin/HEAD. Prints recovery commands on failure."""
    repo = f"{owner}/{args.name}"
    create = ["gh", "repo", "create", repo, "--public" if args.public else "--private",
              "--source", ".", "--remote", "origin", "--push"]
    print(f"Creating the GitHub repository {repo}...")
    result = run(*create, cwd=target, capture=False, timeout=None)
    if result.ok:
        result = run(*SET_HEAD, cwd=target)
        if result.ok:
            print(f"Pushed to {repo}; origin/HEAD is set.")
            return 0
    if result.err:
        print(result.err, file=sys.stderr)
    has_origin = bool(git_config("remote.origin.url", cwd=target))
    pushed = run("git", "rev-parse", "--verify", "--quiet", "refs/remotes/origin/main", cwd=target).ok
    if not has_origin:
        steps = [create, SET_HEAD]
    elif not pushed:
        steps = [["git", "push", "-u", "origin", "main"], SET_HEAD]
    else:
        steps = [SET_HEAD]
    print(f"\nThe remote setup failed. The local project at {shown(target)} is complete and committed.",
          file=sys.stderr)
    print("To finish the remote setup, run:", file=sys.stderr)
    print(f"  cd {shown(target)}", file=sys.stderr)
    for step in steps:
        print(f"  {command_line(step)}", file=sys.stderr)
    if not has_origin:
        print(f"If {repo} was created on GitHub before the failure, replace the gh command with:\n"
              f"  git remote add origin https://github.com/{repo}.git\n"
              "  git push -u origin main", file=sys.stderr)
    return 1


def main(args: argparse.Namespace) -> int:
    target = Path.cwd() / args.name
    problems, owner = preflight(args, target)
    if problems:
        print("newproj new: preflight failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    try:
        render(args, target)
    except source.SourceError as error:
        print(f"newproj new: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("newproj new: cancelled", file=sys.stderr)
        return 130
    except Exception as error:  # Copier removes a destination it created when rendering fails.
        print(f"newproj new: copier copy failed: {error}", file=sys.stderr)
        return 1
    files = generated_files(target)
    try:
        message = commit(target, files)
    except RuntimeError as error:
        print(f"newproj new: {error}", file=sys.stderr)
        print(f"The rendered files are in {shown(target)}.", file=sys.stderr)
        return 1
    print(f"Created {shown(target)} and committed {len(files)} files: {message}")
    if args.no_remote:
        return 0
    return publish(args, owner, target)
