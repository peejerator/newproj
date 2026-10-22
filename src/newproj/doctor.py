"""`newproj doctor`: environment checks, and the Phase 1 project checks of spec section 20.7.

Task-file parsing, recovery signals, and default-branch resolution come from the shared
module `newproj.state` (docs/DECISIONS.md, D-002); this module only classifies its results.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from newproj import state
from newproj.tools import git_config, run, which

ANSWERS = ".copier-answers.yml"
PROTOCOL = "docs/AGENT_PROTOCOL.md"
PROTOCOL_LINE = "At the start of every session, read and follow `docs/AGENT_PROTOCOL.md`."
CLAUDE_IMPORTS = ["@AGENTS.md", "@docs/AGENT_PROTOCOL.md"]
REQUIRED = ["AGENTS.md", "TASK.md", "HANDOFF.md", "docs/DECISIONS.md"]  # spec section 19.2
OPTIONAL = ["CLAUDE.md", "README.md", "LICENSE", ".env.example"]
SKILLS = ["resume", "handoff", "bootstrap", "start-task", "review", "accept"]
USER_SKILLS = ["bootstrap", "start-task", "review", "accept"]  # ERRATA E-010, E-018
AGENTS_BUDGET = 150
PROTOCOL_BUDGET = 120
HOOKS_PATH = ".githooks"
HOOK = ".githooks/commit-msg"
ATTRIBUTION_COMMITS = 20
# Kept equivalent to the grep patterns in template/.githooks/commit-msg (a test checks both).
ATTRIBUTION = re.compile(r"^[ \t]*co-authored-by:|^[^a-z0-9\n]*generated with",
                         re.IGNORECASE | re.MULTILINE | re.ASCII)
CONFLICT_MARKERS = "^(<<<<<<<|>>>>>>>)( |$)"
MAX_DETAILS = 40

LEVELS = ["PASS", "WARN", "FAIL", "INFO"]


@dataclass
class Check:
    level: str
    message: str
    details: list[str] = field(default_factory=list)


@dataclass
class Report:
    sections: list[tuple[str, list[Check]]] = field(default_factory=list)

    def section(self, title: str) -> None:
        self.sections.append((title, []))

    def add(self, level: str, message: str, details: list[str] | None = None) -> None:
        assert level in LEVELS
        self.sections[-1][1].append(Check(level, message, list(details or [])))

    def checks(self) -> list[Check]:
        return [check for _, checks in self.sections for check in checks]

    def render(self) -> str:
        out = []
        for title, checks in self.sections:
            out.append(title)
            for check in checks:
                out.append(f"  {check.level:<5} {check.message}")
                details = check.details
                if len(details) > MAX_DETAILS:
                    details = details[:MAX_DETAILS] + [f"... {len(check.details) - MAX_DETAILS} more lines"]
                out += [f"        {line}" for line in details]
            out.append("")
        counts = {level: sum(c.level == level for c in self.checks()) for level in LEVELS}
        out.append(", ".join(f"{counts[level]} {level}" for level in LEVELS))
        return "\n".join(out) + "\n"

    @property
    def failed(self) -> bool:
        return any(check.level == "FAIL" for check in self.checks())


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", type=Path, default=Path("."),
                        help="the project to check (default: the current directory)")


# Environment


def environment(report: Report, cwd: Path) -> None:
    report.section("Environment")
    report.add("INFO", f"newproj {version('newproj')}")
    has_git = which("git") is not None
    for tool, missing in [("git", "FAIL"), ("gh", "WARN"), ("uv", "WARN")]:
        result = run(tool, "--version")
        if result.ok:
            report.add("PASS", f"{tool}: {result.out.splitlines()[0] if result.out else 'available'}")
        else:
            report.add(missing, f"{tool} is not available", ["Install it as in spec section 21 (machine setup)."])
    try:
        report.add("PASS", f"Copier {version('copier')}")
    except PackageNotFoundError:
        report.add("FAIL", "Copier is not installed", ["Reinstall newproj: uv tool install --force ..."])
    if has_git:
        for key in ("user.name", "user.email"):
            value = git_config(key, cwd)
            if value:
                report.add("PASS", f"Git {key}: {value}")
            else:
                report.add("FAIL", f"Git {key} is not set",
                           [f'git config --global {key} "<{key.split(".")[1]}>"'])
    if which("gh") is not None:
        if run("gh", "auth", "status").ok:
            report.add("PASS", "gh is authenticated")
        else:
            report.add("WARN", "gh is not authenticated, or GitHub did not answer", ["gh auth login"])
    if has_git:
        credentials(report, cwd)


def credentials(report: Report, cwd: Path) -> None:
    result = run("git", "config", "--get-regexp", r"^credential\.", cwd=cwd)
    pairs = [line.split(None, 1) for line in result.out.splitlines()] if result.ok else []
    helpers = [pair for pair in pairs if pair[0].endswith(".helper") and len(pair) == 2 and pair[1].strip()]
    if helpers:
        report.add("PASS", "Git credential helper configured: " + ", ".join(f"{k} {v}" for k, v in helpers))
        return
    ssh = Path.home() / ".ssh"
    keys = sorted(p.name for p in ssh.glob("id_*.pub")) if ssh.is_dir() else []
    if keys:
        report.add("PASS", f"SSH keys found in ~/.ssh ({', '.join(keys)})")
        return
    report.add("WARN", "No Git credential setup found (no credential helper and no SSH key)",
               ["gh auth setup-git"])


# Project


def find_project(path: Path) -> Path | None:
    """The directory holding .copier-answers.yml: `path` or a parent, up to the repository root."""
    path = path.resolve()
    root = state.find_root(path)
    for candidate in [path, *path.parents]:
        if (candidate / ANSWERS).is_file():
            return candidate
        if root is not None and candidate == root.resolve():
            break
    return None


def read_text(path: Path) -> str | None:
    try:
        return path.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return None


def answers(text: str) -> dict[str, str]:
    """Top-level scalar values of the answers file (Copier writes plain `key: value` lines)."""
    values = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([A-Za-z_][\w-]*):\s*(.*)", line.rstrip())
        if match:
            values[match[1]] = match[2].strip().strip("'\"")
    return values


def template_version(report: Report, values: dict[str, str]) -> None:
    src, commit = values.get("_src_path", ""), values.get("_commit", "")
    if "://" in src or src.startswith("git@"):
        report.add("INFO", f"Template version: {commit or 'unknown'} (from {src})")
    else:
        recorded = f", commit {commit}" if commit else ""
        report.add("INFO", f"Template version: development render from {src or 'an unknown source'}{recorded}"
                           " (ERRATA E-002)")
    report.add("INFO", "Template update check: arrives with newproj update")


def restore_hint(git: state.Git | None, root: Path, name: str) -> list[str]:
    if git is not None:
        if git.ok("cat-file", "-e", f"HEAD:{name}"):
            return [f"Restore it from the last commit: git checkout HEAD -- {name}"]
        deleted = git.out("log", "-1", "--format=%h", "--diff-filter=D", "--", name)
        if deleted:
            return [f"Restore it from history: git checkout {deleted}^ -- {name}"]
    if name in state.TASK_FILES and (root / state.NEUTRAL_DIR / name).is_file():
        return [f"Restore the neutral copy: copy {state.NEUTRAL_DIR}/{name} to {name}, byte for byte"]
    return ["Render the template into an empty directory (newproj new <name> --no-remote)"
            f" and copy {name} from it"]


def owned_files(report: Report, git: state.Git | None, root: Path, values: dict[str, str]) -> None:
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    for name in missing:
        report.add("FAIL", f"Required project-owned file missing: {name}", restore_hint(git, root, name))
    optional = [name for name in OPTIONAL if name != "LICENSE" or values.get("license", "none") != "none"]
    absent = [name for name in optional if not (root / name).is_file()]
    for name in absent:
        report.add("WARN", f"Optional project-owned file missing: {name}",
                   ["Fine if intended; it is never recreated.", *restore_hint(git, root, name)])
    if not missing and not absent:
        report.add("PASS", "Project-owned files present")
    elif not missing:
        report.add("PASS", "Required project-owned files present")


def frontmatter(text: str) -> tuple[str, dict[str, str]] | None:
    """The raw frontmatter block and its `key: value` fields, or None when malformed."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end < 0:
        return None
    block = text[: end + 5]
    fields = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            return None
        fields[key.strip()] = value.strip()
    return block, fields


def disallows_implicit_invocation(policy: str) -> bool:
    """Whether the top-level `policy:` mapping sets `allow_implicit_invocation: false` (ERRATA E-010)."""
    in_policy, indent = False, None
    for line in policy.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        depth = len(line) - len(line.lstrip(" \t"))
        if depth == 0:
            in_policy, indent = re.fullmatch(r"policy:\s*", line) is not None, None
            continue
        if not in_policy:
            continue
        if indent is None:
            indent = depth
        if depth == indent and re.fullmatch(r"allow_implicit_invocation:\s*false", stripped):
            return True
    return False


def skill_problems(root: Path, name: str) -> list[str]:
    base = f".agents/skills/{name}"
    text = read_text(root / base / "SKILL.md")
    if text is None:
        return [f"{base}/SKILL.md is missing"]
    parsed = frontmatter(text)
    if parsed is None:
        return [f"{base}/SKILL.md has no well-formed frontmatter"]
    _, fields = parsed
    problems = []
    if fields.get("name") != name:
        problems.append(f"{base}/SKILL.md: name is {fields.get('name')!r}, expected {name!r}")
    if not fields.get("description"):
        problems.append(f"{base}/SKILL.md has no description")
    if name in USER_SKILLS:
        if fields.get("disable-model-invocation") != "true":
            problems.append(f"{base}/SKILL.md lacks disable-model-invocation: true (ERRATA E-010)")
        policy = read_text(root / base / "agents" / "openai.yaml")
        if policy is None:
            problems.append(f"{base}/agents/openai.yaml is missing")
        elif not disallows_implicit_invocation(policy):
            problems.append(f"{base}/agents/openai.yaml lacks allow_implicit_invocation: false")
    if name == "handoff":
        problems += [f"{base}/neutral/{doc} is missing" for doc in state.TASK_FILES
                     if not (root / base / "neutral" / doc).is_file()]
    if name == "resume" and not (root / base / "scripts" / "state.py").is_file():
        problems.append(f"{base}/scripts/state.py is missing")
    if name == "start-task" and not (root / base / "references" / "interview.md").is_file():
        problems.append(f"{base}/references/interview.md is missing")
    return problems


def pointer_problems(root: Path, name: str) -> list[str]:
    path = f".claude/skills/{name}/SKILL.md"
    text = read_text(root / path)
    if text is None:
        return [f"{path} is missing"]
    parsed = frontmatter(text)
    canonical = frontmatter(read_text(root / f".agents/skills/{name}/SKILL.md") or "")
    problems = []
    if parsed is None:
        problems.append(f"{path} has no well-formed frontmatter")
    elif canonical is not None and parsed[0] != canonical[0]:
        problems.append(f"{path}: frontmatter differs from .agents/skills/{name}/SKILL.md")
    if f".agents/skills/{name}/SKILL.md" not in text:
        problems.append(f"{path} does not point to .agents/skills/{name}/SKILL.md")
    return problems


def protocol_and_skills(report: Report, git: state.Git | None, root: Path) -> None:
    ok = True
    if not (root / PROTOCOL).is_file():
        report.add("FAIL", f"{PROTOCOL} is missing", restore_hint(git, root, PROTOCOL))
        ok = False
    for name in SKILLS:
        problems = skill_problems(root, name)
        if problems:
            report.add("FAIL", f"Malformed or incomplete skill: {name}", problems)
            ok = False
        problems = pointer_problems(root, name)
        if problems:
            report.add("FAIL", f"Broken Claude pointer: {name}", problems)
            ok = False
    if ok:
        report.add("PASS", f"{PROTOCOL}, the {len(SKILLS)} skills, and their pointers")


def instruction_files(report: Report, root: Path) -> None:
    agents = read_text(root / "AGENTS.md")
    if agents is not None:
        if PROTOCOL_LINE in agents.splitlines():
            report.add("PASS", "AGENTS.md references the protocol")
        else:
            report.add("FAIL", "AGENTS.md does not reference the protocol",
                       ["Add this line under '## Agent protocol':", PROTOCOL_LINE])
    claude = read_text(root / "CLAUDE.md")
    if claude is not None:
        lines = [line.strip() for line in claude.splitlines()]
        missing = [line for line in CLAUDE_IMPORTS if line not in lines]
        for line in missing:
            report.add("FAIL", f"CLAUDE.md does not import {line[1:]}", ["Add this line to CLAUDE.md:", line])
        if not missing:
            report.add("PASS", "CLAUDE.md imports AGENTS.md and the protocol")


def neutral_diff(doc: state.Doc, st: state.State) -> list[str]:
    expected = read_text(st.neutral_dir / doc.name) or ""
    actual = (doc.data or b"").decode("utf-8", errors="replace")
    return [line.rstrip("\n") for line in difflib.unified_diff(
        expected.splitlines(keepends=True), actual.splitlines(keepends=True),
        fromfile=f"{state.NEUTRAL_DIR}/{doc.name}", tofile=doc.name)]


def task_files(report: Report, st: state.State) -> None:
    task = st.task
    neutral = []
    if st.neutral:
        neutral = [p for p in (state.compare_neutral(doc, st.neutral_dir, st.root)
                               for doc in (st.task, st.handoff) if doc.exists) if p]
    problems = [p for p in state.check(st) if p not in neutral]
    if problems:
        report.add("FAIL", "TASK.md and HANDOFF.md break their format rules (state.py check)",
                   [str(p) for p in problems])
    for problem in neutral:
        doc = st.task if problem.file == "TASK.md" else st.handoff
        report.add("WARN", f"{problem.file} is neutral but not byte-identical to its neutral copy",
                   [str(problem), *neutral_diff(doc, st)])
    status, tier = task.value("Status"), task.value("Tier")
    if task.exists and status == "none":
        filled = [key for key in state.TASK_HEADER[1:] + state.TASK_HEADER_OPTIONAL if task.value(key)]
        if filled:
            report.add("WARN", f"TASK.md has Status: none but non-empty header values: {', '.join(filled)}")
    if status in ("draft", "active") and tier not in ("standard", "formal"):
        report.add("FAIL", f"TASK.md has Status: {status} but Tier: {tier or '(empty)'}",
                   ["A draft or active task needs Tier: standard or Tier: formal."])
    if status == "active" and tier == "standard" and task.value("Task ID"):
        report.add("WARN", "An active standard task has a Task ID; it must be empty (ERRATA E-007)")
    if status == "active" and tier == "formal":
        report.add("INFO", "Formal-task checks arrive in Phase 2")
    if not problems:
        report.add("PASS", "TASK.md and HANDOFF.md follow their format rules")
    if st.task_neutral != st.handoff_neutral:
        neutral_name, other = ("TASK.md", "HANDOFF.md") if st.task_neutral else ("HANDOFF.md", "TASK.md")
        report.add("WARN", f"{neutral_name} is neutral but {other} is not: a task was started or cleared"
                           " incompletely")


def review(report: Report, st: state.State, head: str, dirty: list[str]) -> None:
    """Spec section 20.7: the review status in two parts, never collapsed (ERRATA E-011)."""
    if "Review" in st.handoff.sections and "Outcome" in state.review_fields(st.handoff):
        report.add("PASS", "## Review has an Outcome: line")
    if st.task_neutral:
        return
    fields = state.review_fields(st.handoff)
    outcome = fields.get("Outcome", (0, ""))[1]
    if not outcome or outcome == "none":
        report.add("INFO", "Review: none")
        report.add("INFO", "Current review: none")
        return
    reviewed = fields.get("Reviewed at", (0, ""))[1][:7] or "(no commit recorded)"
    date = re.search(r"\d{4}-\d{2}-\d{2}\s*$", fields.get("Reviewer", (0, ""))[1])
    where = f" at {reviewed}" + (f", {date[0].strip()}" if date else "")
    reasons = state.review_invalidations(st, head, dirty)
    if reasons:
        report.add("INFO", f"Review: {outcome} (historical){where}", ["invalidated by: " + "; ".join(reasons)])
        report.add("INFO", "Current review: none")
    else:
        report.add("INFO", f"Review: {outcome} (current){where}")
        report.add("INFO", f"Current review: {outcome}")


def repository_state(report: Report, git: state.Git) -> None:
    ok = True
    unmerged = sorted(set(line.split("\t", 1)[-1] for line in git.out("ls-files", "-u").splitlines()))
    if unmerged:
        report.add("FAIL", "Unmerged paths", unmerged)
        ok = False
    code, out = git.run("grep", "-n", "-I", "--untracked", "-E", CONFLICT_MARKERS)
    if code == 0 and out.strip():
        report.add("FAIL", "Unresolved conflict markers", out.strip().splitlines())
        ok = False
    for operation in state.in_progress(git):
        report.add("WARN", f"A {operation} is in progress",
                   [f"Finish it (git {operation} --continue) or abort it (git {operation} --abort)."])
        ok = False
    if ok:
        report.add("PASS", "No conflict markers, unmerged paths, or operations in progress")


def size_budgets(report: Report, root: Path) -> None:
    ok = True
    for name, budget in [("AGENTS.md", AGENTS_BUDGET), (PROTOCOL, PROTOCOL_BUDGET)]:
        text = read_text(root / name)
        if text is not None and len(text.splitlines()) > budget:
            report.add("WARN", f"{name} has {len(text.splitlines())} lines (budget: about {budget})",
                       ["Move reusable or conditional detail into docs/ and cite it."])
            ok = False
    if ok:
        report.add("PASS", "AGENTS.md and the protocol are within their size budgets")


def missing_ignore_rules(git: state.Git) -> list[str]:
    """The secret-ignore rules (spec 18.3) that the repository's ignore files do not apply."""
    # The .env.* rule must match any suffix, so probe several names, one of them unlikely
    # to be listed on its own; a single ignored name such as .env.local is not the rule.
    wildcard = [".env.local", ".env.production", ".env.newproj-doctor-probe"]
    expected = [(".env", True, ".env"), *[(path, True, ".env.*") for path in wildcard],
                (".env.example", False, "!.env.example")]
    return list(dict.fromkeys(rule for path, ignored, rule in expected
                              if git.ok("check-ignore", "-q", "--no-index", path) != ignored))


def ignore_rules(report: Report, git: state.Git) -> None:
    missing = missing_ignore_rules(git)
    if missing:
        report.add("WARN", "Secret-ignore rules missing from .gitignore", ["Add these lines:", *missing])
    else:
        report.add("PASS", "Secret-ignore rules present (.env, .env.*, !.env.example)")


def attribution(report: Report, git: state.Git, root: Path) -> None:
    """ERRATA E-016: the commit-msg hook, and attribution lines already in history."""
    hooks = git.out("config", "--get", "core.hooksPath")
    if hooks != HOOKS_PATH:
        report.add("WARN", f"core.hooksPath is {hooks or 'not set'}, so the commit-msg hook does not run",
                   [f"git config core.hooksPath {HOOKS_PATH}"])
    elif not (root / HOOK).is_file():
        report.add("WARN", f"{HOOK} is missing", restore_hint(git, root, HOOK))
    else:
        report.add("PASS", f"core.hooksPath is {HOOKS_PATH}")
    code, out = git.run("log", f"-{ATTRIBUTION_COMMITS}", "--format=%h%x1f%B%x1e")
    found = []
    for entry in out.split("\x1e") if code == 0 else []:
        commit, _, message = entry.strip().partition("\x1f")
        match = ATTRIBUTION.search(message)
        if commit and match:
            found.append(f"{commit}: {match[0].strip()}")
    if found:
        report.add("WARN", f"AI attribution in the last {ATTRIBUTION_COMMITS} commits", found)
    else:
        report.add("PASS", f"No AI attribution in the last {ATTRIBUTION_COMMITS} commits")


def recovery_signals(report: Report, st: state.State, head: str, dirty: list[str]) -> None:
    git = st.git
    branch = git.out("branch", "--show-current")
    areas = state.working_area(st.handoff)
    outside = [p for p in dirty if p not in state.TASK_FILES and not state.in_area(p, areas)]
    signals = state.history_signals(st, head, dirty) + state.metadata_signals(st, branch, head, dirty, outside)
    for signal in signals:
        if signal.startswith("HANDOFF.md is stale"):
            report.add("WARN", signal, ["Update HANDOFF.md (the handoff skill)."])
    report.add("INFO", "Recovery signals (state.py)", signals)


def default_branch(report: Report, git: state.Git) -> None:
    default = state.resolve_default_branch(git)
    if default.name is None:
        report.add("WARN", "The default branch does not resolve", [default.hint])
        return
    report.add("PASS", f"Default branch: {default.describe()}")
    if default.step > 1:
        hint = default.hint or (f"Resolved through a local fallback; once the project has a remote, run"
                                f" `{state.SET_HEAD}`")
        report.add("INFO", hint)


def project(report: Report, root: Path) -> None:
    report.section(f"Project: {root}")
    values = answers(read_text(root / ANSWERS) or "")
    repo = state.find_root(root)
    git = state.Git(repo) if repo is not None else None
    template_version(report, values)
    owned_files(report, git, root, values)
    protocol_and_skills(report, git, root)
    instruction_files(report, root)
    st = state.load(root)
    task_files(report, st)
    if git is None:
        report.add("WARN", "Not a Git repository: the review, repository, hook, and branch checks are skipped",
                   ["git init -b main"])
        size_budgets(report, root)
        return
    head = git.commit("HEAD")
    dirty = git.dirty_paths()
    review(report, st, head, dirty)
    repository_state(report, git)
    size_budgets(report, root)
    ignore_rules(report, git)
    attribution(report, git, root)
    if st.task.value("Status") == "active":
        recovery_signals(report, st, head, dirty)
    default_branch(report, git)


def main(args: argparse.Namespace) -> int:
    path = args.path
    if not path.is_dir():
        print(f"newproj doctor: {path} is not a directory", file=sys.stderr)
        return 2
    report = Report()
    environment(report, path)
    root = find_project(path)
    if root is None:
        report.section("Project")
        report.add("INFO", f"{path.resolve()} is not inside a managed project (no {ANSWERS}); "
                           "project checks skipped")
    else:
        project(report, root)
    sys.stdout.write(report.render())
    return 1 if report.failed else 0
