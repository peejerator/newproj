"""Test the shared state module against temporary Git repositories, with no network."""

import ast
import hashlib
import random
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from newproj import state

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "newproj" / "state.py"
TEMPLATE_COPY = ROOT / "template" / ".agents" / "skills" / "resume" / "scripts" / "state.py"
NEUTRAL = ROOT / "template" / ".agents" / "skills" / "handoff" / "neutral"
SKILLS = ROOT / "template" / ".agents" / "skills"
INVOKE = "uv run --no-project .agents/skills/resume/scripts/state.py"

ACTIVE_TASK = """# Task

Status: active
Tier: standard
Task ID:
Base commit: {base}
Target branch: main
Issue:
PR:

## Goal

Add the widget.

## Context

## Scope

## Acceptance criteria

- AC-1: The widget exists.

## Relevant areas

## Validation

## Do not change

## Open questions
"""

ACTIVE_HANDOFF = """# Handoff

Last updated: 2026-10-19 by test
Branch: {branch}
Task: standard

## Status

in progress

## Completed

## Current working area

- `src/`

## Validation

- PASS | `pytest` | 3 passed, covers AC-1 | Linux | implementer

## Review

{review}

## Exact next steps

1. Finish the widget.

## Blockers / open questions

## Relevant decisions
"""


@pytest.fixture(autouse=True)
def isolated_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the user's and the system's Git configuration out of every test."""
    config = tmp_path / "gitconfig"
    config.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for role in ["AUTHOR", "COMMITTER"]:
        monkeypatch.setenv(f"GIT_{role}_NAME", "Test")
        monkeypatch.setenv(f"GIT_{role}_EMAIL", "test@example.com")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def write(repo: Path, name: str, text: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def commit_all(repo: Path, message: str = "change") -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def make_repo(path: Path, branch: str = "main", task_files: bool = True) -> Path:
    """A repository in the neutral state, with the neutral copies where generated projects keep them."""
    path.mkdir()
    git(path, "init", "-q", "-b", branch)
    shutil.copytree(NEUTRAL, path / state.NEUTRAL_DIR)
    for name in state.TASK_FILES if task_files else []:
        shutil.copyfile(NEUTRAL / name, path / name)
    write(path, "README.md", "# Demo\n")
    commit_all(path, "Initial commit")
    return path


def start_task(repo: Path, review: str = "Outcome: none") -> str:
    """Write and commit an active standard task; returns its base commit."""
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "TASK.md", ACTIVE_TASK.format(base=base))
    write(repo, "HANDOFF.md", ACTIVE_HANDOFF.format(branch=git(repo, "branch", "--show-current"), review=review))
    commit_all(repo, "Start task")
    return base


def record_review(repo: Path, outcome: str = "PASS") -> None:
    """Commit a review record of the current HEAD, as the review skill does."""
    reviewed_at = git(repo, "rev-parse", "HEAD")
    contract = git(repo, "hash-object", "TASK.md")
    text = (repo / "HANDOFF.md").read_text(encoding="utf-8")
    record = f"Outcome: {outcome}\nReviewed at: {reviewed_at}\nContract: {contract}"
    write(repo, "HANDOFF.md", text.replace("Outcome: none", record))
    commit_all(repo, "Record review")


def snapshot(repo: Path) -> dict[str, str]:
    """Every file under the repository, .git included, by content hash."""
    return {
        p.relative_to(repo).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(repo.rglob("*"))
        if p.is_file()
    }


Run = Callable[..., "tuple[int, str]"]


@pytest.fixture
def run(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> Run:
    """Run state.py in a repository and assert the run left it unchanged."""

    def runner(repo: Path, *args: str) -> tuple[int, str]:
        before = snapshot(repo)
        monkeypatch.chdir(repo)
        capsys.readouterr()
        code = state.main(list(args))
        out = capsys.readouterr().out
        assert snapshot(repo) == before, "state.py changed the repository"
        return code, out

    return runner


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


@pytest.fixture
def active(repo: Path) -> Path:
    start_task(repo)
    return repo


# AC-1


def test_template_copy_is_byte_identical() -> None:
    assert TEMPLATE_COPY.read_bytes() == SOURCE.read_bytes(), (
        "template copy is out of date; run: uv run python scripts/sync_state.py"
    )


def test_standard_library_only() -> None:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    modules = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
               for alias in node.names}
    modules |= {node.module.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
    assert modules - {"__future__"} <= set(sys.stdlib_module_names)


def test_parses_as_python_39() -> None:
    ast.parse(SOURCE.read_text(encoding="utf-8"), feature_version=(3, 9))


def test_copy_command_documented() -> None:
    assert "uv run python scripts/sync_state.py" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_template_copy_runs_as_a_script(repo: Path) -> None:
    before = snapshot(repo)
    result = subprocess.run([sys.executable, str(TEMPLATE_COPY), "check"], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No violations found." in result.stdout
    assert snapshot(repo) == before


# AC-2


def add_remote(repo: Path, tmp_path: Path, head: str = "main") -> Path:
    """Push to a local bare repository whose HEAD names `head`; no origin/HEAD is created."""
    bare = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(bare))
    git(repo, "remote", "add", "origin", str(bare))
    git(repo, "push", "-q", "origin", "--all")
    git(bare, "symbolic-ref", "HEAD", f"refs/heads/{head}")
    return bare


def test_step_1_origin_head(repo: Path, tmp_path: Path, run: Run) -> None:
    add_remote(repo, tmp_path)
    git(repo, "remote", "set-head", "origin", "--auto")
    _, out = run(repo)
    assert "main (step 1: refs/remotes/origin/HEAD)" in out
    assert "set-head" not in out


def test_step_2_remote_without_origin_head(repo: Path, tmp_path: Path, run: Run) -> None:
    git(repo, "branch", "develop")
    add_remote(repo, tmp_path, head="develop")
    assert subprocess.run(["git", "symbolic-ref", "-q", "refs/remotes/origin/HEAD"], cwd=repo).returncode != 0
    _, out = run(repo)
    assert "develop (step 2: git ls-remote --symref origin HEAD)" in out
    assert "`git remote set-head origin --auto` would let step 1 work offline" in out
    # Read-only: origin/HEAD is still missing.
    assert subprocess.run(["git", "symbolic-ref", "-q", "refs/remotes/origin/HEAD"], cwd=repo).returncode != 0


def test_step_3_offline(repo: Path, tmp_path: Path, run: Run) -> None:
    git(repo, "remote", "add", "origin", str(tmp_path / "missing.git"))
    _, out = run(repo)
    assert "main (step 3: local branch main, no remote or offline)" in out
    assert "git remote set-head origin --auto" in out


def test_step_3_init_default_branch(tmp_path: Path, run: Run) -> None:
    repo = make_repo(tmp_path / "repo", branch="trunk")
    git(repo, "branch", "main")
    git(repo, "config", "init.defaultBranch", "trunk")
    _, out = run(repo)
    assert "trunk (step 3: init.defaultBranch, no remote or offline)" in out


def test_step_3_master(tmp_path: Path, run: Run) -> None:
    repo = make_repo(tmp_path / "repo", branch="master")
    _, out = run(repo)
    assert "master (step 3: local branch master, no remote or offline)" in out


def test_step_4_unknown(tmp_path: Path, run: Run) -> None:
    repo = make_repo(tmp_path / "repo", branch="feature")
    git(repo, "config", "init.defaultBranch", "trunk")
    _, out = run(repo)
    assert "unknown (step 4: no step resolved it)" in out
    assert "not guessed" in out and "git remote set-head origin --auto" in out
    assert "feature (step" not in out


def test_step_4_unknown_with_unreachable_remote(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo", branch="feature")
    git(repo, "remote", "add", "origin", str(tmp_path / "missing.git"))
    resolved = state.resolve_default_branch(state.Git(repo))
    assert resolved.name is None and resolved.step == 4
    assert "git remote set-head origin --auto" in resolved.hint


# AC-3


def task_problems(text: str) -> list[str]:
    return [str(p) for p in state.parse_task(text.encode("utf-8")).problems]


def handoff_problems(text: str) -> list[str]:
    return [str(p) for p in state.parse_handoff(text.encode("utf-8")).problems]


def neutral(name: str) -> str:
    return (NEUTRAL / name).read_text(encoding="utf-8")


def test_neutral_files_parse_cleanly() -> None:
    assert task_problems(neutral("TASK.md")) == []
    assert handoff_problems(neutral("HANDOFF.md")) == []
    assert task_problems(ACTIVE_TASK.format(base="abc")) == []
    assert handoff_problems(ACTIVE_HANDOFF.format(branch="main", review="Outcome: none")) == []


def test_renamed_task_heading() -> None:
    problems = task_problems(neutral("TASK.md").replace("## Goal\n", "## Goals\n"))
    assert "TASK.md:11: unexpected heading '## Goals' (renamed or merged?)" in problems
    assert "TASK.md:1: missing required heading '## Goal'" in problems


def test_renamed_task_header_line() -> None:
    problems = task_problems(neutral("TASK.md").replace("Base commit:", "Base Commit:"))
    assert "TASK.md:6: unexpected header line 'Base Commit:' (renamed?)" in problems
    assert "TASK.md:1: missing required header line 'Base commit:'" in problems


def test_missing_handoff_heading_and_header_line() -> None:
    text = neutral("HANDOFF.md").replace("## Relevant decisions\n", "").replace("Task: none\n", "")
    problems = handoff_problems(text)
    assert "HANDOFF.md:1: missing required heading '## Relevant decisions'" in problems
    assert "HANDOFF.md:1: missing required header line 'Task:'" in problems


def test_renamed_handoff_heading() -> None:
    problems = handoff_problems(neutral("HANDOFF.md").replace("## Exact next steps", "## Next steps"))
    assert any("unexpected heading '## Next steps'" in p for p in problems)
    assert "HANDOFF.md:1: missing required heading '## Exact next steps'" in problems


def test_headings_inside_code_fences_are_ignored() -> None:
    text = ACTIVE_TASK.format(base="abc").replace("## Context\n", "## Context\n\n```\n## Goal\n# Task\n```\n")
    assert task_problems(text) == []


def test_invalid_values() -> None:
    assert "TASK.md:3: invalid Status: 'done' (expected none, draft, or active)" in task_problems(
        neutral("TASK.md").replace("Status: none", "Status: done"))
    handoff = neutral("HANDOFF.md")
    assert any(p.startswith("HANDOFF.md:9: invalid '## Status' value 'finished'")
               for p in handoff_problems(handoff.replace("\nnone\n", "\nfinished\n")))
    assert any(p.startswith("HANDOFF.md:19: invalid Outcome: 'OK'")
               for p in handoff_problems(handoff.replace("Outcome: none", "Outcome: OK")))
    assert "HANDOFF.md:17: '## Review' has no 'Outcome:' line" in handoff_problems(
        handoff.replace("Outcome: none", ""))
    assert "HANDOFF.md:7: '## Status' must hold exactly one value, found 2" in handoff_problems(
        handoff.replace("\nnone\n", "\nnone\ncomplete\n"))


def test_validation_provenance() -> None:
    text = ACTIVE_HANDOFF.format(branch="main", review="Outcome: none")
    for bad in ["| Linux | Claude", "| Linux | implementer (CI)", "| Linux |", ""]:
        problems = handoff_problems(text.replace("| Linux | implementer", bad))
        assert problems == [
            "HANDOFF.md:19: validation entry does not end with its provenance (implementer, reviewer, or CI)"
        ], bad
    for good in ["reviewer", "CI"]:
        assert handoff_problems(text.replace("| implementer", f"| {good}")) == []


def test_active_task_needs_goal_and_criteria() -> None:
    text = ACTIVE_TASK.format(base="abc")
    assert "TASK.md:11: an active task needs a non-empty Goal" in task_problems(text.replace("Add the widget.\n", ""))
    assert any("at least one acceptance criterion" in p
               for p in task_problems(text.replace("- AC-1: The widget exists.\n", "")))


def malformed_inputs() -> list[bytes]:
    rng = random.Random(0)
    samples = [b"", b"\n", b"\xff\xfe\x00garbage", b"\xef\xbb\xbf# Task\n", b"# Task\n# Task\n## Goal\n## Goal\n",
               b"```\n# Task\n", b"## Status\n## Review\nOutcome:\n## Validation\n- |\n- \n", b"Status: active\n" * 3,
               b"# Handoff\r\nBranch: x\r\n## Status\r\n\r\n", b":\n::\n# :\n## :\n"]
    samples += [bytes(rng.randrange(256) for _ in range(rng.randrange(200))) for _ in range(50)]
    for name in state.TASK_FILES:
        data = (NEUTRAL / name).read_bytes()
        samples += [data[:i] for i in range(0, len(data), 7)]
    return samples


def test_parsers_never_raise() -> None:
    for data in malformed_inputs():
        for parser in (state.parse_task, state.parse_handoff):
            doc = parser(data)
            doc.text("Goal")
            state.working_area(doc)
            state.handoff_status(doc)
            state.review_fields(doc)
    assert state.parse_task(None).problems[0].message == "file not found"


def test_report_and_check_survive_malformed_files(repo: Path, run: Run) -> None:
    write(repo, "TASK.md", "Status: active\n## Goal\n```\n")
    (repo / "HANDOFF.md").write_bytes(b"\xff\xfe\x00 garbage\n## Review\nOutcome:\n")
    code, out = run(repo)
    assert code == 0 and "Format problems" in out
    code, out = run(repo, "check")
    assert code == 1 and "TASK.md:1: missing heading '# Task'" in out


# AC-4


def test_neutral_report(repo: Path, run: Run) -> None:
    write(repo, "notes.txt", "scratch\n")
    code, out = run(repo)
    assert code == 0
    assert out.startswith("No active task (neutral state)\n")
    assert "Default branch\n  main (step 3: local branch main, no remote or offline)" in out
    assert "TASK.md matches the neutral copy" in out and "HANDOFF.md matches the neutral copy" in out
    assert "git status --short\n  ?? notes.txt" in out
    assert "Recent commits\n" in out and "Initial commit" in out
    for skipped in ["History freshness", "Metadata consistency", "Current branch"]:
        assert skipped not in out


def test_neutral_mismatch_task_active(repo: Path, run: Run) -> None:
    write(repo, "TASK.md", ACTIVE_TASK.format(base=git(repo, "rev-parse", "HEAD")))
    _, out = run(repo)
    assert "No active task" not in out
    assert "Mismatch: HANDOFF.md is neutral but TASK.md is not" in out


def test_neutral_mismatch_handoff_active(repo: Path, run: Run) -> None:
    write(repo, "HANDOFF.md", ACTIVE_HANDOFF.format(branch="main", review="Outcome: none"))
    _, out = run(repo)
    assert "Mismatch: TASK.md is neutral but HANDOFF.md is not" in out


def test_active_report_lists_spec_items(active: Path, run: Run) -> None:
    head = git(active, "rev-parse", "HEAD")
    _, out = run(active)
    for item in ["Current branch: main", f"HEAD: {head}", "Recorded branch: main", "Last commit that modified it:",
                 "Format problems (state.py check)\n  (none)", "Uncommitted changes: no", "Status: active",
                 "Base commit:", "Target branch: main", "Review outcome: none", "In progress: none",
                 "git status --short", "Dirty paths\n", "Dirty paths outside the recorded working area",
                 "Last 10 commits", "TASK.md: Goal\n  Add the widget.",
                 "TASK.md: Acceptance criteria\n  - AC-1: The widget exists.",
                 "HANDOFF.md: Exact next steps\n  1. Finish the widget.", "Status: in progress"]:
        assert item in out, item
    groups = [out.index(g) for g in ["\nHistory freshness\n", "\nMetadata consistency\n", "\nSemantic reconciliation\n"]]
    assert groups == sorted(groups)
    assert "Not checked by this script. Compare HANDOFF.md's account with the diff." in out
    assert "No commits since the last handoff" in out
    assert "HANDOFF.md has no local modifications" in out
    assert "Current branch matches the recorded branch" in out
    assert "Base commit resolves and is an ancestor of HEAD" in out


def test_stale_and_dirty_handoff(active: Path, run: Run) -> None:
    write(active, "src/a.py", "a = 1\n")
    commit_all(active)
    write(active, "src/b.py", "b = 1\n")
    commit_all(active)
    write(active, "HANDOFF.md", (active / "HANDOFF.md").read_text(encoding="utf-8") + "\n- note\n")
    _, out = run(active)
    assert "HANDOFF.md is stale: 2 commits since the last handoff" in out
    assert "HANDOFF.md has local modifications" in out


def test_never_committed_handoff(tmp_path: Path, run: Run) -> None:
    repo = make_repo(tmp_path / "repo", task_files=False)
    write(repo, "TASK.md", ACTIVE_TASK.format(base=git(repo, "rev-parse", "HEAD")))
    write(repo, "HANDOFF.md", ACTIVE_HANDOFF.format(branch="main", review="Outcome: none"))
    _, out = run(repo)
    assert "HANDOFF.md has never been committed; history freshness cannot be computed" in out
    assert "Last commit that modified it: (never committed)" in out


def test_branch_mismatch(active: Path, run: Run) -> None:
    git(active, "switch", "-q", "-c", "other")
    _, out = run(active)
    assert "Current branch other differs from recorded branch main" in out


def test_detached_head(active: Path, run: Run) -> None:
    git(active, "switch", "-q", "--detach")
    _, out = run(active)
    assert "HEAD is detached; recorded branch is main" in out


def test_dirty_paths_outside_working_area(active: Path, run: Run) -> None:
    write(active, "src/inside.py", "x = 1\n")
    write(active, "docs/outside.md", "outside\n")
    write(active, "README.md", "# Changed\n")
    _, out = run(active)
    assert "2 dirty paths outside the recorded working area" in out
    assert "git status --short\n   M README.md\n" in out
    section = out.split("Dirty paths outside the recorded working area\n")[1].split("Last 10 commits")[0]
    assert section == "  README.md\n  docs/outside.md\n"


def test_dirty_task_file(active: Path, run: Run) -> None:
    write(active, "TASK.md", (active / "TASK.md").read_text(encoding="utf-8") + "\nMore.\n")
    _, out = run(active)
    assert "TASK.md has uncommitted changes" in out
    assert "Uncommitted changes: yes" in out


def test_base_commit_not_ancestor(repo: Path, run: Run) -> None:
    git(repo, "switch", "-q", "-c", "side")
    write(repo, "side.txt", "side\n")
    side = commit_all(repo)
    git(repo, "switch", "-q", "main")
    write(repo, "TASK.md", ACTIVE_TASK.format(base=side))
    write(repo, "HANDOFF.md", ACTIVE_HANDOFF.format(branch="main", review="Outcome: none"))
    commit_all(repo)
    _, out = run(repo)
    assert "Base commit is not an ancestor of HEAD" in out


def test_review_current(active: Path, run: Run) -> None:
    write(active, "src/a.py", "a = 1\n")
    commit_all(active)
    record_review(active)
    write(active, "HANDOFF.md", (active / "HANDOFF.md").read_text(encoding="utf-8") + "\n- note\n")
    _, out = run(active)
    assert "Review PASS is current" in out


def test_review_historical_after_code_commit(active: Path, run: Run) -> None:
    record_review(active)
    write(active, "src/a.py", "a = 1\n")
    commit_all(active)
    _, out = run(active)
    assert "Review PASS is historical: 1 commit since review changed other files" in out


def test_review_historical_after_task_change(active: Path, run: Run) -> None:
    record_review(active)
    write(active, "TASK.md", (active / "TASK.md").read_text(encoding="utf-8").replace("widget.", "gadget."))
    commit_all(active)
    _, out = run(active)
    assert "Review PASS is historical: TASK.md amended since review" in out


def test_review_historical_with_dirty_tree(active: Path, run: Run) -> None:
    record_review(active, outcome="FAIL")
    write(active, "src/a.py", "a = 1\n")
    _, out = run(active)
    assert "Review FAIL is historical: 1 uncommitted change outside HANDOFF.md" in out


def test_in_progress_merge(active: Path, run: Run) -> None:
    git(active, "switch", "-q", "-c", "side")
    write(active, "README.md", "# Side\n")
    commit_all(active)
    git(active, "switch", "-q", "main")
    write(active, "README.md", "# Main\n")
    commit_all(active)
    assert subprocess.run(["git", "merge", "-q", "side"], cwd=active, capture_output=True).returncode != 0
    _, out = run(active)
    assert "In progress: merge" in out


# AC-5


def test_check_clean_active(active: Path, run: Run) -> None:
    assert run(active, "check") == (0, "No violations found.\n")


def test_check_clean_neutral(repo: Path, run: Run) -> None:
    assert run(repo, "check") == (0, "No violations found.\n")


def replace_in(name: str, old: str, new: str) -> Callable[[Path], None]:
    def mutate(repo: Path) -> None:
        text = (repo / name).read_text(encoding="utf-8")
        assert old in text
        write(repo, name, text.replace(old, new, 1))

    return mutate


ACTIVE_VIOLATIONS = {
    "missing heading": (replace_in("TASK.md", "## Scope\n", ""), "TASK.md:1: missing required heading '## Scope'"),
    "renamed heading": (replace_in("HANDOFF.md", "## Completed", "## Done"),
                        "HANDOFF.md:11: unexpected heading '## Done' (renamed or merged?)"),
    "missing header line": (replace_in("HANDOFF.md", "Branch: main\n", ""),
                            "HANDOFF.md:1: missing required header line 'Branch:'"),
    "task status": (replace_in("TASK.md", "Status: active", "Status: Active"), "TASK.md:3: invalid Status: 'Active'"),
    "handoff status": (replace_in("HANDOFF.md", "in progress", "in-progress"),
                       "HANDOFF.md:9: invalid '## Status' value 'in-progress'"),
    "outcome": (replace_in("HANDOFF.md", "Outcome: none", "Outcome: pass"), "HANDOFF.md:23: invalid Outcome: 'pass'"),
    "provenance": (replace_in("HANDOFF.md", "| implementer", "| me"),
                   "HANDOFF.md:19: validation entry does not end with its provenance"),
    "empty base": (lambda repo: write(repo, "TASK.md", ACTIVE_TASK.format(base="")),
                   "TASK.md:6: an active task needs a Base commit (ERRATA E-007)"),
    "unresolved base": (lambda repo: write(repo, "TASK.md", ACTIVE_TASK.format(base="0" * 40)),
                        f"TASK.md:6: Base commit {'0' * 40} does not resolve to a commit"),
}


@pytest.mark.parametrize("case", list(ACTIVE_VIOLATIONS))
def test_check_violation(case: str, active: Path, run: Run) -> None:
    mutate, expected = ACTIVE_VIOLATIONS[case]
    mutate(active)
    code, out = run(active, "check")
    assert code == 1
    assert any(line.startswith(expected) for line in out.splitlines()), out
    assert out.rstrip().endswith("found.")


NEUTRAL_VIOLATIONS = {
    "extra line": (replace_in("TASK.md", "## Open questions\n", "## Open questions\n\n"),
                   "TASK.md:27: neutral, but not byte-identical to .agents/skills/handoff/neutral/TASK.md"),
    "filled value": (replace_in("HANDOFF.md", "Last updated: none", "Last updated: 2026-10-19"),
                     "HANDOFF.md:3: neutral, but not byte-identical"),
    "CRLF": (lambda repo: (repo / "TASK.md").write_bytes((NEUTRAL / "TASK.md").read_bytes().replace(b"\n", b"\r\n")),
             "TASK.md:1: neutral, but not byte-identical"),
}


@pytest.mark.parametrize("case", list(NEUTRAL_VIOLATIONS))
def test_check_neutral_violation(case: str, repo: Path, run: Run) -> None:
    mutate, expected = NEUTRAL_VIOLATIONS[case]
    mutate(repo)
    code, out = run(repo, "check")
    assert code == 1
    assert any(line.startswith(expected) for line in out.splitlines()), out


def test_check_ignores_neutral_copies_for_an_active_task(active: Path, run: Run) -> None:
    shutil.rmtree(active / state.NEUTRAL_DIR)
    assert run(active, "check")[0] == 0


def test_not_a_repository(tmp_path: Path, run: Run) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert run(empty, "check")[0] == 2


# AC-6


def test_neutral_dir_option(repo: Path, tmp_path: Path, run: Run) -> None:
    moved = tmp_path / "elsewhere"
    shutil.move(str(repo / state.NEUTRAL_DIR), str(moved))
    commit_all(repo, "Move the neutral copies")
    code, out = run(repo, "check")
    assert code == 1 and "neutral copy not found at .agents/skills/handoff/neutral/TASK.md" in out
    assert run(repo, "check", "--neutral-dir", str(moved)) == (0, "No violations found.\n")
    _, out = run(repo, "--neutral-dir", str(moved))
    assert "TASK.md matches the neutral copy" in out


def test_agents_md_commands() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "does not exist yet" not in text
    command = f"uv run --no-project template/{INVOKE.split()[-1]}"
    assert f"{command} --neutral-dir template/.agents/skills/handoff/neutral" in text
    assert f"{command} check --neutral-dir template/.agents/skills/handoff/neutral" in text


# AC-7


@pytest.mark.parametrize("name", ["handoff", "review", "accept"])
def test_skills_run_check_with_fallback(name: str) -> None:
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    assert f"{INVOKE} check" in text
    assert "python3 .agents/skills/resume/scripts/state.py check" in text
    assert "py -3 .agents/skills/resume/scripts/state.py check" in text
    assert "If no Python is available" in text


def test_resume_invocation_matches_spec() -> None:
    text = (SKILLS / "resume" / "SKILL.md").read_text(encoding="utf-8")
    assert f"{INVOKE}\n" in text
    assert "python3 .agents/skills/resume/scripts/state.py" in text
    assert "py -3 .agents/skills/resume/scripts/state.py" in text
