#!/usr/bin/env python3
"""Report the task state of a repository and check the mechanical rules of TASK.md and HANDOFF.md.

Standard library only; runs on Python 3.9 and newer. Read-only: it never modifies
the repository, never runs `git remote set-head`, and never writes files.

The source is src/newproj/state.py in newproj. Generated projects ship a
byte-identical copy at .agents/skills/resume/scripts/state.py.

Run from anywhere inside the repository:

    state.py [--neutral-dir DIR]          print the report (spec section 17.2)
    state.py check [--neutral-dir DIR]    exit 1 if a mechanical rule is broken
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

TASK_HEADER = ["Status", "Tier", "Task ID", "Base commit", "Target branch"]
TASK_HEADER_OPTIONAL = ["Issue", "PR", "Baseline note"]
TASK_SECTIONS = [
    "Goal",
    "Context",
    "Scope",
    "Acceptance criteria",
    "Relevant areas",
    "Validation",
    "Do not change",
    "Open questions",
]
TASK_STATUSES = ["none", "draft", "active"]

HANDOFF_HEADER = ["Last updated", "Branch", "Task"]
HANDOFF_HEADER_OPTIONAL = ["Environment"]
HANDOFF_SECTIONS = [
    "Status",
    "Completed",
    "Current working area",
    "Validation",
    "Review",
    "Exact next steps",
    "Blockers / open questions",
    "Relevant decisions",
]
HANDOFF_STATUSES = ["none", "not started", "in progress", "blocked", "validating", "complete"]
REVIEW_OUTCOMES = ["PASS", "FAIL", "INCONCLUSIVE", "none"]
PROVENANCES = ["implementer", "reviewer", "CI"]

NEUTRAL_DIR = ".agents/skills/handoff/neutral"
TASK_FILES = ["TASK.md", "HANDOFF.md"]
LS_REMOTE_TIMEOUT = 10
SET_HEAD = "git remote set-head origin --auto"

HEADER_LINE = re.compile(r"([A-Za-z][A-Za-z /-]*):(.*)")
AC_LINE = re.compile(r"\s*[-*]\s+AC-\d+\b")


def one_of(values: list[str]) -> str:
    return ", ".join(values[:-1]) + ", or " + values[-1]


@dataclass
class Problem:
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.message}"


@dataclass
class Doc:
    """A TASK.md or HANDOFF.md file, read by heading."""

    name: str
    data: bytes | None = None
    header: dict[str, tuple[int, str]] = field(default_factory=dict)
    sections: dict[str, tuple[int, list[tuple[int, str]]]] = field(default_factory=dict)
    problems: list[Problem] = field(default_factory=list)

    @property
    def exists(self) -> bool:
        return self.data is not None

    def value(self, key: str) -> str:
        return self.header.get(key, (0, ""))[1]

    def line_of(self, key: str) -> int:
        return self.header.get(key, (1, ""))[0]

    def body(self, heading: str) -> list[tuple[int, str]]:
        return self.sections.get(heading, (0, []))[1]

    def text(self, heading: str) -> list[str]:
        """The section's lines without leading and trailing blank lines."""
        lines = [line for _, line in self.body(heading)]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return lines

    def problem(self, line: int, message: str) -> None:
        self.problems.append(Problem(self.name, line, message))


def parse(name: str, data: bytes | None, title: str, header: list[str], optional: list[str],
          headings: list[str]) -> Doc:
    """Split a file into its title, header lines, and `##` sections, recording contract problems.

    Never raises: anything unexpected is recorded as a problem.
    """
    doc = Doc(name, data)
    if data is None:
        doc.problem(1, "file not found")
        return doc
    text = data.decode("utf-8", errors="replace")
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()
    title_line = 0
    current = None  # None before the title, "" in the header block, else the section heading
    fence = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        elif not fence and line.startswith("# "):
            if title_line:
                doc.problem(number, f"unexpected level-1 heading {line.strip()!r}")
                continue
            title_line = number
            current = ""
            if line.rstrip() != f"# {title}":
                doc.problem(number, f"expected heading '# {title}', found {line.strip()!r}")
            continue
        elif not fence and line.startswith("## "):
            heading = line[3:].strip()
            if heading in doc.sections:
                doc.problem(number, f"duplicate heading '## {heading}'")
            elif heading not in headings:
                doc.problem(number, f"unexpected heading '## {heading}' (renamed or merged?)")
            if heading not in doc.sections:
                doc.sections[heading] = (number, [])
            current = heading
            continue
        if current is None:
            if line.strip():
                doc.problem(number, f"text before the '# {title}' heading")
        elif current == "":
            if not line.strip():
                continue
            match = HEADER_LINE.fullmatch(line.rstrip())
            if not match:
                doc.problem(number, f"unexpected text in the header: {line.strip()!r}")
                continue
            key, value = match[1], match[2].strip()
            if key not in header and key not in optional:
                doc.problem(number, f"unexpected header line '{key}:' (renamed?)")
            elif key in doc.header:
                doc.problem(number, f"duplicate header line '{key}:'")
            else:
                doc.header[key] = (number, value)
        else:
            doc.sections[current][1].append((number, line))
    anchor = title_line or 1
    if not title_line:
        doc.problem(1, f"missing heading '# {title}'")
    for key in header:
        if key not in doc.header:
            doc.problem(anchor, f"missing required header line '{key}:'")
    for heading in headings:
        if heading not in doc.sections:
            doc.problem(anchor, f"missing required heading '## {heading}'")
    return doc


def parse_task(data: bytes | None) -> Doc:
    doc = parse("TASK.md", data, "Task", TASK_HEADER, TASK_HEADER_OPTIONAL, TASK_SECTIONS)
    if not doc.exists:
        return doc
    status = doc.value("Status")
    if "Status" in doc.header and status not in TASK_STATUSES:
        doc.problem(doc.line_of("Status"), f"invalid Status: {status!r} (expected {one_of(TASK_STATUSES)})")
    if status == "active":
        if "Goal" in doc.sections and not doc.text("Goal"):
            doc.problem(doc.sections["Goal"][0], "an active task needs a non-empty Goal")
        if "Acceptance criteria" in doc.sections and not any(
            AC_LINE.match(line) for _, line in doc.body("Acceptance criteria")
        ):
            doc.problem(doc.sections["Acceptance criteria"][0],
                        "an active task needs at least one acceptance criterion (- AC-1: ...)")
    return doc


def parse_handoff(data: bytes | None) -> Doc:
    doc = parse("HANDOFF.md", data, "Handoff", HANDOFF_HEADER, HANDOFF_HEADER_OPTIONAL, HANDOFF_SECTIONS)
    if not doc.exists:
        return doc
    if "Status" in doc.sections:
        values = [(n, line.strip()) for n, line in doc.body("Status") if line.strip()]
        if len(values) != 1:
            doc.problem(doc.sections["Status"][0], f"'## Status' must hold exactly one value, found {len(values)}")
        for number, value in values:
            if value not in HANDOFF_STATUSES:
                doc.problem(number, f"invalid '## Status' value {value!r} (expected {one_of(HANDOFF_STATUSES)})")
    if "Review" in doc.sections:
        outcome = review_fields(doc).get("Outcome")
        if outcome is None:
            doc.problem(doc.sections["Review"][0], "'## Review' has no 'Outcome:' line")
        elif outcome[1] not in REVIEW_OUTCOMES:
            doc.problem(outcome[0], f"invalid Outcome: {outcome[1]!r} (expected {one_of(REVIEW_OUTCOMES)})")
    for number, line in doc.body("Validation"):
        if line.startswith(("- ", "* ")):
            provenance = line[2:].split("|")[-1].strip()
            if provenance not in PROVENANCES:
                doc.problem(number, f"validation entry does not end with its provenance ({one_of(PROVENANCES)})")
    return doc


def review_fields(doc: Doc) -> dict[str, tuple[int, str]]:
    """The `Key: value` lines of `## Review`, first occurrence of each."""
    fields: dict[str, tuple[int, str]] = {}
    for number, line in doc.body("Review"):
        match = HEADER_LINE.fullmatch(line.rstrip())
        if match and match[1] not in fields:
            fields[match[1]] = (number, match[2].strip())
    return fields


def handoff_status(doc: Doc) -> str:
    values = [line.strip() for _, line in doc.body("Status") if line.strip()]
    return values[0] if len(values) == 1 else ""


def working_area(doc: Doc) -> list[str]:
    areas = []
    for _, line in doc.body("Current working area"):
        item = line.strip()
        if not item.startswith(("- ", "* ")):
            continue
        item = item[2:].strip()
        quoted = re.search(r"`([^`]+)`", item)
        path = (quoted[1] if quoted else item).replace("\\", "/").strip()
        while path.startswith("./"):
            path = path[2:]
        path = path.rstrip("/")
        if path and path != ".":
            areas.append(path)
    return areas


def in_area(path: str, areas: list[str]) -> bool:
    return any(path == a or path.startswith(a + "/") or fnmatch.fnmatchcase(path, a) for a in areas)


class Git:
    """Read-only Git queries against one repository."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")

    def run(self, *args: str, timeout: float | None = None) -> tuple[int, str]:
        try:
            result = subprocess.run(
                ["git", "-c", "core.quotepath=off", *args],
                cwd=self.root, env=self.env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError):
            return -1, ""
        return result.returncode, result.stdout.decode("utf-8", errors="replace")

    def out(self, *args: str) -> str:
        code, out = self.run(*args)
        return out.strip() if code == 0 else ""

    def ok(self, *args: str) -> bool:
        return self.run(*args)[0] == 0

    def commit(self, rev: str) -> str:
        return self.out("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}") if rev else ""

    def is_ancestor(self, rev: str, head: str) -> bool:
        return self.ok("merge-base", "--is-ancestor", rev, head)

    def commits_touching_others(self, since: str, exclude: list[str]) -> list[str]:
        pathspec = [".", *(f":(exclude){name}" for name in exclude)]
        return self.out("log", "--format=%H", f"{since}..HEAD", "--", *pathspec).split()

    def dirty_paths(self) -> list[str]:
        code, out = self.run("status", "--porcelain", "-z", "-uall")
        if code != 0:
            return []
        paths = []
        entries = out.split("\0")
        i = 0
        while i < len(entries):
            entry = entries[i]
            i += 1
            if len(entry) < 4:
                continue
            paths.append(entry[3:])
            if entry[0] in "RC" and i < len(entries):
                paths.append(entries[i])
                i += 1
        return sorted(set(paths))


def find_root(start: Path) -> Path | None:
    code, out = Git(start).run("rev-parse", "--show-toplevel")
    return Path(out.strip()) if code == 0 and out.strip() else None


@dataclass
class DefaultBranch:
    name: str | None
    step: int
    how: str
    hint: str = ""

    def describe(self) -> str:
        if self.name is None:
            return f"unknown (step 4: {self.how})"
        return f"{self.name} (step {self.step}: {self.how})"


def resolve_default_branch(git: Git) -> DefaultBranch:
    """Spec section 4, steps 1 to 4, stopping at the first that succeeds. Never guesses."""
    target = git.out("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if target.startswith("refs/remotes/origin/"):
        return DefaultBranch(target[len("refs/remotes/origin/"):], 1, "refs/remotes/origin/HEAD")
    has_remote = bool(git.out("config", "--get", "remote.origin.url"))
    if has_remote:
        code, out = git.run("ls-remote", "--symref", "origin", "HEAD", timeout=LS_REMOTE_TIMEOUT)
        for line in out.splitlines() if code == 0 else []:
            match = re.fullmatch(r"ref:\s*refs/heads/(\S+)\s+HEAD", line.strip())
            if match:
                return DefaultBranch(match[1], 2, "git ls-remote --symref origin HEAD",
                                     f"refs/remotes/origin/HEAD is missing; `{SET_HEAD}` would let step 1 work offline")
    offline = f"the remote did not answer; `{SET_HEAD}` would help once it does" if has_remote else ""
    configured = git.out("config", "--get", "init.defaultBranch")
    for candidate, how in [(configured, "init.defaultBranch"), ("main", "local branch main"),
                           ("master", "local branch master")]:
        if candidate and git.ok("show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"):
            return DefaultBranch(candidate, 3, f"{how}, no remote or offline", offline)
    if has_remote:
        fix = f"run `{SET_HEAD}` when the remote is reachable"
    else:
        fix = f"add the remote as origin and run `{SET_HEAD}`"
    return DefaultBranch(None, 4, "no step resolved it", f"not guessed; {fix}")


def read_file(root: Path, name: str) -> bytes | None:
    try:
        return (root / name).read_bytes()
    except OSError:
        return None


def compare_neutral(doc: Doc, neutral_dir: Path, root: Path) -> Problem | None:
    """Byte comparison with the canonical neutral copy (spec section 12.8)."""
    reference = neutral_dir / doc.name
    shown = display_path(reference, root)
    try:
        expected = reference.read_bytes()
    except OSError:
        return Problem(doc.name, 1, f"neutral copy not found at {shown}; pass --neutral-dir")
    if doc.data is None or doc.data == expected:
        return None
    actual_lines = doc.data.split(b"\n")
    expected_lines = expected.split(b"\n")
    line = 1
    while line <= min(len(actual_lines), len(expected_lines)) and actual_lines[line - 1] == expected_lines[line - 1]:
        line += 1
    return Problem(doc.name, line, f"neutral, but not byte-identical to {shown} (first difference on this line)")


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


@dataclass
class State:
    root: Path
    neutral_dir: Path
    git: Git
    task: Doc
    handoff: Doc

    @property
    def task_neutral(self) -> bool:
        return not self.task.exists or self.task.value("Status") == "none"

    @property
    def handoff_neutral(self) -> bool:
        return not self.handoff.exists or handoff_status(self.handoff) == "none"

    @property
    def neutral(self) -> bool:
        return self.task_neutral and self.handoff_neutral


def load(root: Path, neutral_dir: Path | None = None) -> State:
    neutral = neutral_dir if neutral_dir is not None else root / NEUTRAL_DIR
    if not neutral.is_absolute():
        neutral = Path.cwd() / neutral
    return State(root, neutral, Git(root), parse_task(read_file(root, "TASK.md")),
                 parse_handoff(read_file(root, "HANDOFF.md")))


def check(state: State) -> list[Problem]:
    """Violations of the mechanical rules; empty when the files pass."""
    problems = state.task.problems + state.handoff.problems
    task = state.task
    if task.exists and task.value("Status") == "active" and "Base commit" in task.header:
        base = task.value("Base commit")
        line = task.line_of("Base commit")
        if not base:
            problems.append(Problem("TASK.md", line, "an active task needs a Base commit (ERRATA E-007)"))
        elif not state.git.commit(base):
            problems.append(Problem("TASK.md", line, f"Base commit {base} does not resolve to a commit"))
    if state.neutral:
        for doc in (state.task, state.handoff):
            if doc.exists:
                difference = compare_neutral(doc, state.neutral_dir, state.root)
                if difference:
                    problems.append(difference)
    return sorted(problems, key=lambda p: (TASK_FILES.index(p.file), p.line))


def in_progress(git: Git) -> list[str]:
    found = []
    for name, label in [("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
                        ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert"), ("BISECT_LOG", "bisect")]:
        path = git.out("rev-parse", "--git-path", name)
        if path and (git.root / path).exists() and label not in found:
            found.append(label)
    return found


def history_signals(state: State, head: str, dirty: list[str]) -> list[str]:
    git = state.git
    signals = []
    last = git.out("log", "-1", "--format=%H", "--", "HANDOFF.md") if head else ""
    if not last:
        signals.append("HANDOFF.md has never been committed; history freshness cannot be computed")
    else:
        later = git.commits_touching_others(last, ["HANDOFF.md"])
        if later:
            signals.append(f"HANDOFF.md is stale: {len(later)} commit{'s' * (len(later) != 1)}"
                           f" since the last handoff ({last[:12]}) changed other files")
        else:
            signals.append(f"No commits since the last handoff ({last[:12]}) changed other files")
    if "HANDOFF.md" in dirty:
        signals.append("HANDOFF.md has local modifications")
    else:
        signals.append("HANDOFF.md has no local modifications")
    return signals


def review_signal(state: State, head: str, dirty: list[str]) -> str:
    """Spec section 13.6: a review is current only while its snapshot still describes the work."""
    fields = review_fields(state.handoff)
    outcome = fields.get("Outcome", (0, ""))[1]
    if not outcome or outcome == "none":
        return "No review recorded (Outcome: none)"
    git = state.git
    reasons = []
    reviewed = git.commit(fields.get("Reviewed at", (0, ""))[1])
    if not reviewed:
        reasons.append("Reviewed at does not resolve to a commit")
    elif not head or not git.is_ancestor(reviewed, head):
        reasons.append("Reviewed at is not an ancestor of HEAD")
    else:
        later = git.commits_touching_others(reviewed, TASK_FILES)
        if later:
            reasons.append(f"{len(later)} commit{'s' * (len(later) != 1)} since review changed other files")
    outside = [p for p in dirty if p != "HANDOFF.md"]
    if outside:
        reasons.append(f"{len(outside)} uncommitted change{'s' * (len(outside) != 1)} outside HANDOFF.md")
    contract = fields.get("Contract", (0, ""))[1]
    if not contract or git.out("hash-object", "TASK.md") != contract:
        reasons.append("TASK.md amended since review")
    if reasons:
        return f"Review {outcome} is historical: " + "; ".join(reasons)
    return f"Review {outcome} is current"


def metadata_signals(state: State, branch: str, head: str, dirty: list[str], outside: list[str]) -> list[str]:
    task, handoff, git = state.task, state.handoff, state.git
    signals = []
    if state.task_neutral != state.handoff_neutral:
        neutral, other = ("TASK.md", "HANDOFF.md") if state.task_neutral else ("HANDOFF.md", "TASK.md")
        signals.append(f"Mismatch: {neutral} is neutral but {other} is not"
                       " (a task was started or cleared incompletely)")
    recorded = handoff.value("Branch")
    if not branch:
        signals.append(f"HEAD is detached; recorded branch is {recorded or '(empty)'}")
    elif recorded != branch:
        signals.append(f"Current branch {branch} differs from recorded branch {recorded or '(empty)'}")
    else:
        signals.append("Current branch matches the recorded branch")
    if "TASK.md" in dirty:
        signals.append("TASK.md has uncommitted changes (an active task should not change)")
    others = [p for p in dirty if p not in TASK_FILES]
    if outside:
        signals.append(f"{len(outside)} dirty path{'s' * (len(outside) != 1)} outside the recorded working area")
    elif others:
        signals.append("All dirty paths are inside the recorded working area")
    base = task.value("Base commit")
    if task.value("Status") == "active" and not base:
        signals.append("Base commit is empty (ERRATA E-007)")
    elif base:
        resolved = git.commit(base)
        if not resolved:
            signals.append(f"Base commit {base} does not resolve")
        elif head and git.is_ancestor(resolved, head):
            signals.append("Base commit resolves and is an ancestor of HEAD")
        else:
            signals.append("Base commit is not an ancestor of HEAD (branch rebased; review diff unaffected)")
    signals.append(review_signal(state, head, dirty))
    return signals


def block(title: str, lines: list[str]) -> list[str]:
    return [title, *(f"  {line}" for line in (lines or ["(none)"]))]


def report(state: State) -> str:
    git = state.git
    branch = git.out("branch", "--show-current")
    head = git.commit("HEAD")
    default = resolve_default_branch(git)
    status_short = git.run("status", "--short")[1].rstrip("\n").splitlines()
    commits = git.out("log", "--oneline", "-10").splitlines() if head else ["No commits yet"]
    default_lines = [default.describe()] + ([default.hint] if default.hint else [])
    out: list[str] = []

    if state.neutral:
        out.append("No active task (neutral state)")
        out += block("Default branch", default_lines)
        comparisons = []
        for doc in (state.task, state.handoff):
            if not doc.exists:
                comparisons.append(f"{doc.name} not found (treated as neutral)")
                continue
            difference = compare_neutral(doc, state.neutral_dir, state.root)
            comparisons.append(str(difference) if difference else f"{doc.name} matches the neutral copy")
        out += block("Neutral copies", comparisons)
        operations = in_progress(git)
        if operations:
            out += block("In progress", operations)
        out += block("git status --short", status_short)
        out += block("Recent commits", commits)
        return "\n".join(out) + "\n"

    dirty = git.dirty_paths()
    areas = working_area(state.handoff)
    outside = [p for p in dirty if p not in TASK_FILES and not in_area(p, areas)]
    task, handoff = state.task, state.handoff
    out += block("Repository", [
        f"Current branch: {branch or '(detached HEAD)'}",
        f"HEAD: {head or '(no commits yet)'}",
        f"Default branch: {default_lines[0]}",
        *default_lines[1:],
        f"In progress: {', '.join(in_progress(git)) or 'none'}",
    ])
    task_lines = [f"{key}: {task.value(key)}" for key in TASK_HEADER] if task.exists else ["not found"]
    task_lines.append(f"Uncommitted changes: {'yes' if 'TASK.md' in dirty else 'no'}")
    out += block("TASK.md", task_lines)
    last = git.out("log", "-1", "--format=%h %s", "--", "HANDOFF.md") if head else ""
    out += block("HANDOFF.md", [
        f"Status: {handoff_status(handoff) or '(invalid)'}",
        f"Recorded branch: {handoff.value('Branch')}",
        f"Task: {handoff.value('Task')}",
        f"Last commit that modified it: {last or '(never committed)'}",
        f"Review outcome: {review_fields(handoff).get('Outcome', (0, '(missing)'))[1]}",
    ] if handoff.exists else ["not found"])
    out += block("Format problems (state.py check)", [str(p) for p in check(state)])
    out.append("")
    out += block("History freshness", history_signals(state, head, dirty))
    out += block("Metadata consistency", metadata_signals(state, branch, head, dirty, outside))
    out += block("Semantic reconciliation", ["Not checked by this script. Compare HANDOFF.md's account with the diff."])
    out.append("")
    out += block("git status --short", status_short)
    out += block("Dirty paths", dirty)
    out += block("Dirty paths outside the recorded working area", outside)
    out += block("Last 10 commits", commits)
    out.append("")
    out += block("TASK.md: Goal", task.text("Goal"))
    out += block("TASK.md: Acceptance criteria", task.text("Acceptance criteria"))
    out += block("HANDOFF.md: Exact next steps", handoff.text("Exact next steps"))
    out.append("")
    out.append("These are signals for reconciliation, not proof that anything is wrong.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="state.py",
        description="Report task state (read-only), or check TASK.md and HANDOFF.md against their fixed rules.",
    )
    parser.add_argument("command", nargs="?", choices=["check"],
                        help="check the mechanical rules; exit 1 on any violation")
    parser.add_argument("--neutral-dir", type=Path, metavar="DIR",
                        help=f"directory holding the neutral TASK.md and HANDOFF.md (default: {NEUTRAL_DIR})")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    root = find_root(Path.cwd())
    if root is None:
        print("state.py: not inside a Git repository", file=sys.stderr)
        return 2
    state = load(root, args.neutral_dir)
    if args.command == "check":
        problems = check(state)
        for problem in problems:
            print(problem)
        if problems:
            print(f"{len(problems)} violation{'s' * (len(problems) != 1)} found.")
            return 1
        print("No violations found.")
        return 0
    sys.stdout.write(report(state))
    return 0


if __name__ == "__main__":
    sys.exit(main())
