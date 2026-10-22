"""`newproj adopt`: add the template to an existing repository without replacing its files (spec section 20.2).

The template is rendered into a temporary directory first, so every collision is known
before anything in the repository is written. Adopt never stages or commits.
"""

from __future__ import annotations

import argparse
import difflib
import os
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from newproj import doctor, source, state
from newproj.new import HOOKS_PATH, NAME, SET_HEAD, command_line, shown
from newproj.tools import run, which

# Project-owned paths in the template: copier.yml _skip_if_exists (spec section 19.2).
PROJECT_OWNED = ["AGENTS.md", "CLAUDE.md", "TASK.md", "HANDOFF.md", "README.md", "LICENSE", ".env.example",
                 "docs/DECISIONS.md"]
HYGIENE = [".gitignore", ".editorconfig", ".gitattributes"]
# Required .gitignore entries (spec section 18.3), in the order they are appended.
IGNORE_RULES = [".env", ".env.*", "!.env.example", "context.md"]
IGNORE_START = "# Added by newproj adopt: required entries (spec section 18.3)"
IGNORE_END = "# End of entries added by newproj adopt"
INIT = ["git", "init", "-b", "main"]
RENORMALIZE = "git add --renormalize ."
MAX_LISTED = 40
IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003  # a Windows junction; stat defines the name only on Windows


@dataclass
class Row:
    path: str
    result: str
    review: bool = False


@dataclass
class Plan:
    """What adoption writes, and what it reports."""

    create: list[str]
    rows: list[Row]
    template_created: int
    append_ignore: list[str]
    details: list[str]


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", type=Path, default=Path("."),
                        help="the repository to adopt (default: the current directory)")
    parser.add_argument("--name", help="project name (default: the folder name; lowercase letters, digits, "
                                       "and hyphens)")
    # Development and tests only (ERRATA E-002): render a local directory instead of the tagged template.
    parser.add_argument("--template-path", type=Path, help=argparse.SUPPRESS)


def interactive() -> bool:
    return sys.stdin.isatty()


def fail(problems: list[str]) -> int:
    print("newproj adopt: preflight failed; nothing was written:", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return 2


def listed(paths: list[str]) -> str:
    shown_paths = paths[:MAX_LISTED]
    more = f"\n      ... and {len(paths) - MAX_LISTED} more" if len(paths) > MAX_LISTED else ""
    return "".join(f"\n      {path}" for path in shown_paths) + more


def ensure_repository(target: Path) -> tuple[Path | None, list[str]]:
    """The repository root, initializing a plain folder when the user agrees (spec 20.2, step 1)."""
    root = state.find_root(target)
    if root is not None:
        if not root.samefile(target):  # case and short-name differences on macOS and Windows
            return None, [f"{shown(target)} is inside the Git repository {shown(root)}; adopt the repository root"]
        return root, []
    if not interactive():
        return None, [f"{shown(target)} is not a Git repository. To adopt it, initialize one first:\n"
                      f"      cd {shown(target)}\n      {command_line(INIT)}"]
    try:
        answer = input(f"{shown(target)} is not a Git repository. Run {command_line(INIT)}? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() not in ("y", "yes"):
        return None, [f"{shown(target)} is not a Git repository; run {command_line(INIT)} there, then adopt again"]
    result = run(*INIT, cwd=target)
    if not result.ok:
        return None, [f"{command_line(INIT)} failed: {result.err or f'exit code {result.code}'}"]
    print(f"Initialized a Git repository in {shown(target)}.")
    return target, []


def dirty(git: state.Git) -> list[str]:
    """Paths `git status --porcelain` reports: changes and untracked files, never ignored ones."""
    code, out = git.run("status", "--porcelain", "--untracked-files=all")
    if code != 0:
        return ["(git status failed)"]
    return [line[3:] for line in out.splitlines() if line.strip()]


def same(path: Path, rendered: Path) -> bool:
    return path.is_file() and path.read_bytes() == rendered.read_bytes()


def kind(path: Path) -> str:
    """The entry at `path`, without following links: missing, link, file, dir, or other."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return "missing"
    # A Windows junction is a reparse point, not a symbolic link, but redirects writes the same way.
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) == IO_REPARSE_TAG_MOUNT_POINT:
        return "link"
    return "dir" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else "other"


def blocked(target: Path, name: str) -> str | None:
    """Why `name` cannot be created or preserved safely, or None.

    Writes must stay inside the repository, so no parent may be a link, and a destination may be a link
    only to a file that adopt reads but never writes.
    """
    parts = name.split("/")
    for i in range(1, len(parts)):
        parent = "/".join(parts[:i])
        entry = kind(target / parent)
        if entry == "link":
            return f"{parent} is a symbolic link or junction"
        if entry not in ("missing", "dir"):
            return f"needs {parent}/ to be a directory"
    path = target / name
    entry = kind(path)
    if entry in ("dir", "other"):
        return "is not a regular file"
    if entry == "link" and not path.is_file():
        return "is a symbolic link or junction that does not point to a file"
    return None


# Paths that `* text=auto eol=lf` covers and a narrower rule, such as one for *.txt, misses.
LF_PROBES = ["newproj-adopt-probe", "newproj-adopt-probe.txt", ".newproj-adopt-probe",
             "newproj-adopt-probe/probe.newproj-adopt-probe"]


def lf_rule_applies(git: state.Git) -> bool:
    """True when the repository's attributes normalize all text files to LF (spec section 18.1)."""
    out = git.out("check-attr", "text", "eol", "--", *LF_PROBES)
    values: dict[str, dict[str, str]] = {probe: {} for probe in LF_PROBES}
    for line in out.splitlines():
        path, attribute, value = line.rsplit(": ", 2)
        values.setdefault(path, {})[attribute] = value
    return all(v.get("text") in ("auto", "set") and v.get("eol") == "lf" for v in values.values())


def renormalized(git: state.Git) -> list[str]:
    """Committed text files whose line endings `* text=auto eol=lf` would change."""
    code, out = git.run("ls-files", "--eol", "-z")
    affected = []
    for entry in out.split("\0") if code == 0 else []:
        info, sep, path = entry.partition("\t")
        if sep and info.split()[0] in ("i/crlf", "i/mixed"):
            affected.append(path)
    return affected


def missing_ignore_rules(git: state.Git) -> list[str]:
    missing = set(doctor.missing_ignore_rules(git))
    if not git.ok("check-ignore", "-q", "--no-index", "context.md"):
        missing.add("context.md")
    if ".env.*" in missing:
        missing.add("!.env.example")  # .env.* appended last would ignore .env.example again
    return [rule for rule in IGNORE_RULES if rule in missing]


def editorconfig_diff(existing: Path, rendered: Path) -> list[str]:
    old = existing.read_bytes().decode("utf-8", errors="replace").splitlines()
    new = rendered.read_bytes().decode("utf-8", errors="replace").splitlines()
    diff = list(difflib.unified_diff(old, new, ".editorconfig (this repository)", ".editorconfig (template)",
                                     lineterm=""))
    return diff[:MAX_LISTED] + (["..."] if len(diff) > MAX_LISTED else [])


def plan(target: Path, rendered: Path, git: state.Git) -> tuple[Plan | None, list[str]]:
    """Classify every rendered file. Returns problems instead of a plan on a collision."""
    names = sorted(p.relative_to(rendered).as_posix() for p in rendered.rglob("*") if p.is_file())
    neutral = rendered / state.NEUTRAL_DIR
    create, rows, details, collisions, unsafe, append = [], [], [], [], [], []
    template_created = 0
    for name in names:
        path, new = target / name, rendered / name
        reason = blocked(target, name)
        if reason is not None:
            unsafe.append(f"{name} ({reason})")
            continue
        exists = kind(path) != "missing"
        if name in PROJECT_OWNED:
            if not exists:
                create.append(name)
                rows.append(Row(name, "created"))
            elif name == "AGENTS.md":
                rows.append(Row(name, "preserved; bootstrap review required", True))
            elif name == "CLAUDE.md":
                lines = [line.strip() for line in path.read_bytes().decode("utf-8", errors="replace").splitlines()]
                missing = [line for line in doctor.CLAUDE_IMPORTS if line not in lines]
                if missing:
                    rows.append(Row(name, f"preserved; lacks {', '.join(missing)}: bootstrap review required", True))
                else:
                    rows.append(Row(name, "preserved"))
            elif name in state.TASK_FILES and not same(path, neutral / name):
                rows.append(Row(name, "preserved; not neutral: bootstrap review required", True))
            else:
                rows.append(Row(name, "preserved"))
        elif name == ".gitignore":
            if not exists:
                create.append(name)
                rows.append(Row(name, "created"))
            else:
                append = missing_ignore_rules(git)
                if append and kind(path) == "link":
                    unsafe.append(f"{name} (is a symbolic link or junction, so the required entries cannot be "
                                  "appended)")
                    append = []
                elif append:
                    rows.append(Row(name, f"preserved; appended {', '.join(append)} in a marked block"))
                else:
                    rows.append(Row(name, "preserved"))
        elif name == ".editorconfig":
            if not exists:
                create.append(name)
                rows.append(Row(name, "created"))
            elif same(path, new):
                rows.append(Row(name, "preserved"))
            else:
                rows.append(Row(name, "preserved; differs from the template: review the differences", True))
                details += ["Differences of .editorconfig from the template's defaults (not applied):",
                            *(f"    {line}" for line in editorconfig_diff(path, new))]
        elif name == ".gitattributes":
            if exists:
                if lf_rule_applies(git):
                    rows.append(Row(name, "preserved"))
                else:
                    rows.append(Row(name, "preserved; no general LF rule (* text=auto eol=lf): review", True))
                continue
            affected = renormalized(git)
            if not affected:
                create.append(name)
                rows.append(Row(name, "created"))
                continue
            rows.append(Row(name, "not created: committed files would change line endings: review", True))
            url = f"{source.TEMPLATE_URL.removesuffix('.git')}/blob/{source.tag()}/template/.gitattributes"
            details += ["The LF rule would change the line endings of these committed files, so .gitattributes "
                        f"was left out:{listed(affected)}",
                        "Add it in a separate commit, after committing the adoption, so line-ending churn never "
                        "mixes with real changes:",
                        f"    create .gitattributes with the line '* text=auto eol=lf' (the template's file: {url})",
                        f"    {RENORMALIZE}",
                        '    git commit -m "Normalize line endings"']
        elif not exists:
            create.append(name)
            template_created += 1
        elif same(path, new):
            rows.append(Row(name, "preserved; identical to the template"))
        else:
            collisions.append(name)
    problems = []
    if unsafe:
        problems.append("these paths cannot be written or preserved safely, because adoption would write through "
                        f"a link or replace something that is not a regular file:{listed(unsafe)}\n"
                        "    Replace them with regular files and directories (or remove them), commit, and adopt "
                        "again.")
    if collisions:
        problems.append("these template-owned paths exist and differ from the template, so adoption would replace "
                        f"them:{listed(collisions)}\n"
                        "    Move or remove them (or make them match the template), commit, and adopt again.")
    if problems:
        return None, problems
    ignored = set(git.out("check-ignore", "--no-index", "--", *create).splitlines()) if create else set()
    for name in sorted(ignored):
        rows.append(Row(name, "created, but ignored by .gitignore, so it would not be committed: review", True))
    return Plan(create, rows, template_created, append, details), []


def append_ignore_rules(path: Path, rules: list[str]) -> None:
    data = path.read_bytes()
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    block = [IGNORE_START, *rules, IGNORE_END]
    prefix = newline if data and not data.endswith(b"\n") else b""
    path.write_bytes(data + prefix + newline.join(line.encode("utf-8") for line in block) + newline)


def write(target: Path, rendered: Path, adoption: Plan) -> None:
    for name in adoption.create:
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rendered / name, dest)
    if adoption.append_ignore:
        append_ignore_rules(target / ".gitignore", adoption.append_ignore)


def set_head(git: state.Git) -> list[str]:
    """Spec 20.2, step 3: run set-head when origin exists without origin/HEAD. Returns notes to print."""
    if not git.out("config", "--get", "remote.origin.url"):
        return []
    if git.ok("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"):
        return []
    result = run(*SET_HEAD, cwd=git.root, timeout=state.LS_REMOTE_TIMEOUT)
    if result.ok:
        return [f"Ran {command_line(SET_HEAD)}."]
    return [f"{command_line(SET_HEAD)} failed ({result.err or f'exit code {result.code}'}); "
            "run it again when the remote is reachable."]


def report(adoption: Plan, notes: list[str], default: state.DefaultBranch, hooks: str) -> int:
    width = max(len(row.path) for row in adoption.rows) + 2
    print("\nFiles:\n")
    for row in adoption.rows:
        print(f"{row.path.ljust(width)}{row.result}")
    if adoption.template_created:
        print(f"{'(template)'.ljust(width)}created {adoption.template_created} template-owned files "
              "(protocol, prompts, skills, hooks, answers file)")
    reviews = sum(row.review for row in adoption.rows)
    for line in adoption.details:
        print(f"\n{line}" if not line.startswith("    ") else line)
    print()
    for note in notes:
        print(note)
    print(f"Default branch: {default.describe()}")
    if default.hint:
        print(f"  {default.hint}")
    if reviews:
        plural = "item requires" if reviews == 1 else "items require"
        print(f"\nAdoption completed; {reviews} {plural} review.")
    else:
        print("\nAdoption completed; nothing requires review.")
    print("\nNext steps (newproj adopt did not stage or commit anything):")
    steps = ["Run the bootstrap skill before continuing: /bootstrap in Claude Code, $bootstrap in Codex. "
             "It reconciles AGENTS.md, CLAUDE.md, TASK.md, and HANDOFF.md with this project and works through "
             "any items marked for review."]
    if hooks != HOOKS_PATH:
        current = f" (currently {hooks})" if hooks else ""
        steps.append(f"Enable the commit-msg hook{current}: git config core.hooksPath {HOOKS_PATH}")
    steps.append(f'Review the changes (git status, git diff), then commit them: '
                 f'git add -A && git commit -m "Adopt project-template v{version("newproj")}"')
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    return 1 if reviews else 0


def main(args: argparse.Namespace) -> int:
    target = args.path.resolve()
    name = args.name if args.name is not None else target.name
    problems = []
    if not target.is_dir():
        problems.append(f"{shown(target)} is not a directory")
    if not NAME.fullmatch(name):
        how = "" if args.name is not None else " (from the folder name; pass --name)"
        problems.append(f"invalid project name {name!r}{how}: use lowercase letters, digits, and single hyphens "
                        "only")
    if args.template_path is not None and not (args.template_path / "copier.yml").is_file():
        problems.append(f"--template-path {shown(args.template_path)} has no copier.yml")
    if which("git") is None:
        problems.append("git is not installed or not on PATH (spec section 21)")
    if problems:
        return fail(problems)
    root, problems = ensure_repository(target)
    if root is None:
        return fail(problems)
    git = state.Git(root)
    changed = dirty(git)
    if changed:
        return fail(["the working tree is not clean, so adoption's changes would not be reviewable on their own. "
                     f"Commit or stash these paths first:{listed(changed)}"])
    if (root / source.ANSWERS).exists():
        return fail([f"{source.ANSWERS} already exists: this repository has already been adopted or generated"])
    with tempfile.TemporaryDirectory(prefix="newproj-adopt-", ignore_cleanup_errors=True) as tmp:
        rendered = Path(tmp) / name
        try:
            source.render(name, rendered, args.template_path, quiet=True)
        except source.SourceError as error:
            print(f"newproj adopt: {error}", file=sys.stderr)
            return 2
        except KeyboardInterrupt:
            print("newproj adopt: cancelled; nothing was written", file=sys.stderr)
            return 2
        except Exception as error:
            print(f"newproj adopt: copier copy failed; nothing was written: {error}", file=sys.stderr)
            return 2
        adoption, problems = plan(root, rendered, git)
        if adoption is None:
            return fail(problems)
        try:
            write(root, rendered, adoption)
        except OSError as error:
            print(f"newproj adopt: writing failed: {error}", file=sys.stderr)
            print("Inspect the partial result with git status; git clean and git checkout undo it.",
                  file=sys.stderr)
            return 2
    notes = set_head(git)
    return report(adoption, notes, state.resolve_default_branch(git), git.out("config", "--get", "core.hooksPath"))
