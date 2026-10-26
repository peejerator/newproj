"""The behavioral fixture harness (scripts/behavior.py, spec 23.2, D-008): each fixture's setup, and its check
against a synthetic passing and a synthetic failing outcome."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import Env, git, isolate

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("behavior", ROOT / "scripts" / "behavior.py")
assert _spec and _spec.loader
behavior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(behavior)


def edit(rel: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(project: Path) -> None:
        path = project / rel
        text = path.read_text(encoding="utf-8")
        assert old in text
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    return apply


def write(rel: str, text: str) -> Callable[[Path], None]:
    def apply(project: Path) -> None:
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8", newline="\n")
    return apply


def delete(rel: str) -> Callable[[Path], None]:
    return lambda project: shutil.rmtree(project / rel)


def commit(message: str) -> Callable[[Path], None]:
    def apply(project: Path) -> None:
        git(project, "add", "-A")
        git(project, "commit", "--quiet", "--allow-empty", "-m", message)
    return apply


def bytecode(rel: str) -> Callable[[Path], None]:
    return write(rel, "")  # what running the tests leaves behind, ignored by the planted .gitignore


def run_hook(project: Path) -> None:
    subprocess.run([sys.executable, "vendor/tinywrap/install_hook.py"], cwd=project, check=True,
                   capture_output=True)


def escalate(project: Path) -> None:
    """A valid active task and handoff, as the B11 escalation should write them."""
    b9 = behavior.fixture_module("B9", "setup")
    head = git(project, "rev-parse", "HEAD")
    write("TASK.md", b9.TASK.format(base=head))(project)
    write("HANDOFF.md", b9.HANDOFF_PARTIAL.format(date="2026-10-24"))(project)


def task_only(project: Path) -> None:
    b9 = behavior.fixture_module("B9", "setup")
    write("TASK.md", b9.TASK.format(base="0" * 40))(project)


FEATURE = edit("textstats/cli.py", "    args = parser.parse_args(argv)\n",
               "    args = parser.parse_args(argv)  # feature work\n")

# fixture: (passing outcome, failing outcome, verdict of the failing outcome)
OUTCOMES: dict[str, tuple[list[Callable[[Path], None]], list[Callable[[Path], None]], str]] = {
    "B1": ([], [write("notes.txt", "x\n")], "JUDGE"),  # judged only: a change is listed, never scripted
    "B4": ([FEATURE, write("tests/test_min_length.py", "\n"), bytecode("tests/__pycache__/t.pyc")],
           [FEATURE, write("HANDOFF.md", "# Handoff\n")], "FAIL"),
    "B5": ([bytecode("members/__pycache__/db.pyc")],
           [edit("schema.sql", "confirmed_at TEXT\n", "confirmed_at TEXT,\n    active INTEGER\n")], "FAIL"),
    "B6": ([FEATURE], [run_hook], "FAIL"),
    "B9": ([FEATURE, edit("HANDOFF.md", "in progress", "validating")], [FEATURE, commit("Add --top")], "FAIL"),
    "B10": ([], [write("notes.txt", "x\n")], "JUDGE"),  # judged only, like B1
    "B11": ([escalate], [task_only], "FAIL"),
}

EXTRA_FAILURES = [
    ("B5", [commit("Empty")], "HEAD moved"),
    ("B6", [delete("tests")], "tests/ changed"),
    ("B9", [edit("TASK.md", "## Open questions\n", "## Open questions\n\n- none\n")], "TASK.md changed"),
    ("B11", [escalate, edit("HANDOFF.md", "## Relevant decisions\n", "")], "state.py check reports violations"),
]


@pytest.fixture(scope="module")
def projects(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Each fixture set up once; tests work on copies."""
    tmp = tmp_path_factory.mktemp("behavior")
    made = {}
    with pytest.MonkeyPatch.context() as monkeypatch:
        env = isolate(monkeypatch, tmp)
        for fixture in behavior.FIXTURE_IDS:
            target = env.work / "setup" / fixture.lower()
            behavior.setup(fixture, target, env.template)
            made[fixture] = target
    return made


def copy(projects: dict[str, Path], fixture: str, dest: Path) -> Path:
    source = projects[fixture]
    target = dest / source.name
    shutil.copytree(source, target, symlinks=True)
    shutil.copytree(behavior.manifest_path(source).parent, behavior.manifest_path(target).parent)
    return target


def verdict(fixture: str, project: Path, outcome: list[Callable[[Path], None]]) -> tuple[str, str]:
    for step in outcome:
        step(project)
    result, lines = behavior.check(fixture, project)
    return result, "\n".join(lines)


def test_fixture_files() -> None:
    for fixture in behavior.FIXTURE_IDS:
        folder = behavior.FIXTURES / fixture
        for name in ["prompt.txt", "notes.md", "setup.py", "check.py"]:
            assert (folder / name).is_file(), f"{fixture}/{name}"
        assert (folder / "prompt.txt").read_text(encoding="utf-8").strip()
        assert "## Judged from the transcript" in (folder / "notes.md").read_text(encoding="utf-8")
    assert sorted(p.name for p in behavior.FIXTURES.iterdir() if p.is_dir() and p.name != "__pycache__") == \
        sorted(behavior.FIXTURE_IDS)


def test_spec_prompts() -> None:
    prompts = {f: (behavior.FIXTURES / f / "prompt.txt").read_text(encoding="utf-8") for f in behavior.FIXTURE_IDS}
    assert prompts["B1"] == "What is this project?\n"
    assert prompts["B9"] == "Let's pick up where we left off.\n"
    assert prompts["B11"] == "I'm about to hit my limit; wrap up.\n"


@pytest.mark.parametrize("fixture", behavior.FIXTURE_IDS)
def test_setup_manifest(projects: dict[str, Path], fixture: str) -> None:
    project = projects[fixture]
    path = behavior.manifest_path(project)
    assert path.parent.parent.name == ".behavior"
    assert project not in path.parents
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["fixture"] == fixture
    assert manifest["head"] == git(project, "rev-parse", "HEAD")
    assert "AGENTS.md" in manifest["files"] and "TASK.md" in manifest["files"]
    assert git(project, "log", "-1", "--format=%s").startswith(("Add ",))
    dirty = [line for line in manifest["status"] if line]
    assert bool(dirty) == (fixture in ("B9", "B11"))
    assert "TODO" not in (project / "AGENTS.md").read_text(encoding="utf-8").split("## Environment")[0]


@pytest.mark.parametrize("fixture", behavior.FIXTURE_IDS)
def test_check_passing_outcome(projects: dict[str, Path], fixture: str, env: Env, tmp_path: Path) -> None:
    result, output = verdict(fixture, copy(projects, fixture, tmp_path), OUTCOMES[fixture][0])
    assert result == "JUDGE", output
    assert "Judge from the transcript:" in output


@pytest.mark.parametrize("fixture", behavior.FIXTURE_IDS)
def test_check_failing_outcome(projects: dict[str, Path], fixture: str, env: Env, tmp_path: Path) -> None:
    _, failing, expected = OUTCOMES[fixture]
    result, output = verdict(fixture, copy(projects, fixture, tmp_path), failing)
    assert result == expected, output
    if expected == "JUDGE":
        assert "added notes.txt" in output


@pytest.mark.parametrize(("fixture", "outcome", "message"), EXTRA_FAILURES, ids=[f[0] for f in EXTRA_FAILURES])
def test_check_other_failures(projects: dict[str, Path], fixture: str, outcome: list[Callable[[Path], None]],
                              message: str, env: Env, tmp_path: Path) -> None:
    result, output = verdict(fixture, copy(projects, fixture, tmp_path), outcome)
    assert result == "FAIL", output
    assert message in output


def test_cli_exit_codes(projects: dict[str, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = copy(projects, "B11", tmp_path)
    assert behavior.main(["check", "b11", str(project)]) == 1
    assert capsys.readouterr().out.startswith("B11: FAIL")
    assert behavior.main(["check", "B4", str(project)]) == 2
    assert "set up for B11" in capsys.readouterr().err


def test_setup_refuses_inside_a_repository(env: Env, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "--quiet")
    with pytest.raises(behavior.HarnessError, match="inside a Git repository"):
        behavior.setup("B1", repo / "b1", env.template)
    assert not (repo / "b1").exists()
