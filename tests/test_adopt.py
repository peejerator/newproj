"""`newproj adopt` (spec section 20.2), on scratch repositories built in each test."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import pytest

from conftest import ROOT, Env, git, newproj
from newproj import adopt, source

TAG = f"v{version('newproj')}"
NEUTRAL = ROOT / "template" / ".agents" / "skills" / "handoff" / "neutral"
TEMPLATE = ROOT / "template"


def make_repo(env: Env, files: dict[str, bytes | str] | None = None, name: str = "app") -> Path:
    """A committed repository holding `files` (a README by default)."""
    repo = env.work / name
    repo.mkdir()
    git(repo, "init", "--quiet", "-b", "main")
    for path, content in (files if files is not None else {"README.md": "# App\n"}).items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    if files != {}:
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", "Existing project")
    return repo


def run_adopt(env: Env, repo: Path, capfd: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    code = newproj("adopt", str(repo), "--template-path", str(env.template), *args)
    out, err = capfd.readouterr()
    return code, out, err


def row(out: str, path: str) -> str:
    """The table line for `path`, without the path."""
    for line in out.splitlines():
        if line.startswith(path + " "):
            return line[len(path):].strip()
    raise AssertionError(f"no table row for {path}:\n{out}")


def snapshot(repo: Path) -> dict[str, bytes]:
    return {p.relative_to(repo).as_posix(): p.read_bytes() for p in repo.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(repo).parts[:1]}


def assert_nothing_written(repo: Path, before: dict[str, bytes]) -> None:
    assert snapshot(repo) == before
    assert not (repo / ".copier-answers.yml").exists()


# AC-4, AC-6: a clean adoption


def test_clean_adoption(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env)
    head = git(repo, "rev-parse", "HEAD")
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert (repo / "README.md").read_bytes() == b"# App\n"
    assert row(out, "README.md") == "preserved"
    for name in ["AGENTS.md", "CLAUDE.md", "TASK.md", "HANDOFF.md", "docs/DECISIONS.md", ".gitignore",
                 ".gitattributes", ".editorconfig"]:
        assert row(out, name) == "created"
        assert (repo / name).is_file()
    assert (repo / "TASK.md").read_bytes() == (NEUTRAL / "TASK.md").read_bytes()
    assert (repo / "docs" / "AGENT_PROTOCOL.md").read_bytes() == (TEMPLATE / "docs" / "AGENT_PROTOCOL.md").read_bytes()
    assert "nothing requires review" in out
    assert "Run the bootstrap skill before continuing" in out
    # Never stages or commits.
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "diff", "--cached", "--name-only") == ""
    assert "?? AGENTS.md" in git(repo, "status", "--porcelain")


def test_name_defaults_to_folder_and_can_be_overridden(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env)
    assert run_adopt(env, repo, capfd)[0] == 0
    assert "project_name: app\n" in (repo / ".copier-answers.yml").read_text(encoding="utf-8")
    other = make_repo(env, name="other")
    assert run_adopt(env, other, capfd, "--name", "renamed")[0] == 0
    assert "project_name: renamed\n" in (other / ".copier-answers.yml").read_text(encoding="utf-8")


def test_path_defaults_to_current_directory(env: Env, monkeypatch: pytest.MonkeyPatch,
                                            capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env)
    monkeypatch.chdir(repo)
    assert newproj("adopt", "--template-path", str(env.template)) == 0
    assert (repo / "AGENTS.md").is_file()


def test_answers_record_repository_url(env: Env, upstream: Path, capfd: pytest.CaptureFixture[str]) -> None:
    git(upstream, "tag", TAG)
    repo = make_repo(env)
    assert newproj("adopt", str(repo)) == 0
    answers = (repo / ".copier-answers.yml").read_text(encoding="utf-8")
    assert f"_src_path: {source.TEMPLATE_URL}\n" in answers
    assert f"_commit: {TAG}\n" in answers
    assert str(env.tmp / "cache") not in answers


# AC-4: project-owned files


def test_existing_project_files_preserved_and_reviewed(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    files = {
        "README.md": "# App\n",
        "AGENTS.md": "# App agents\n\nOur own rules.\n",
        "CLAUDE.md": "Use the house style.\n",
        "TASK.md": "# Our task list\n",
        "HANDOFF.md": "# Notes\n",
        "docs/DECISIONS.md": "# ADR index\n",
        ".env.example": "TOKEN=\n",
    }
    repo = make_repo(env, files)
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 1
    for name, content in files.items():
        assert (repo / name).read_bytes() == content.encode("utf-8"), name
    assert row(out, "AGENTS.md") == "preserved; bootstrap review required"
    assert "lacks @AGENTS.md, @docs/AGENT_PROTOCOL.md" in row(out, "CLAUDE.md")
    assert "bootstrap review required" in row(out, "CLAUDE.md")
    assert row(out, "TASK.md") == "preserved; not neutral: bootstrap review required"
    assert row(out, "HANDOFF.md") == "preserved; not neutral: bootstrap review required"
    for name in ["README.md", "docs/DECISIONS.md", ".env.example"]:
        assert row(out, name) == "preserved"
    assert "4 items require review" in out
    assert "Run the bootstrap skill before continuing" in out


def test_compatible_project_files_need_no_review(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {
        "CLAUDE.md": "@AGENTS.md\n@docs/AGENT_PROTOCOL.md\n\nMore notes.\n",
        "TASK.md": (NEUTRAL / "TASK.md").read_bytes(),
        "HANDOFF.md": (NEUTRAL / "HANDOFF.md").read_bytes(),
    })
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    for name in ["CLAUDE.md", "TASK.md", "HANDOFF.md"]:
        assert row(out, name) == "preserved"


# AC-5: hygiene files


def test_gitignore_appends_missing_entries(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    original = b"node_modules/\n.env\n# no newline at end"
    repo = make_repo(env, {".gitignore": original})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    data = (repo / ".gitignore").read_bytes()
    assert data.startswith(original)
    block = data[len(original):].decode("utf-8").splitlines()
    assert block == ["", adopt.IGNORE_START, ".env.*", "!.env.example", "context.md", adopt.IGNORE_END]
    assert "appended .env.*, !.env.example, context.md in a marked block" in row(out, ".gitignore")
    assert git(repo, "check-ignore", "--no-index", ".env.local") == ".env.local"
    assert git(repo, "check-ignore", "-q", "--no-index", ".env.example", check=False) == ""


def test_gitignore_with_entries_unchanged(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    original = b"build/\n.env\n.env.*\n!.env.example\ncontext.md\n"
    repo = make_repo(env, {".gitignore": original})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert (repo / ".gitignore").read_bytes() == original
    assert row(out, ".gitignore") == "preserved"


def test_editorconfig_preserved_and_differences_reported(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    original = b"root = true\n\n[*]\nindent_size = 2\n"
    repo = make_repo(env, {".editorconfig": original})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 1
    assert (repo / ".editorconfig").read_bytes() == original
    assert "differs from the template" in row(out, ".editorconfig")
    assert "--- .editorconfig (this repository)" in out and "+charset = utf-8" in out


def test_identical_editorconfig_preserved(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {".editorconfig": (TEMPLATE / ".editorconfig").read_bytes()})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert row(out, ".editorconfig") == "preserved"


def test_gitattributes_without_lf_rule_never_modified(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    original = b"*.png binary\n"
    repo = make_repo(env, {".gitattributes": original})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 1
    assert (repo / ".gitattributes").read_bytes() == original
    assert "no LF rule" in row(out, ".gitattributes")


def test_gitattributes_with_lf_rule_preserved(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    original = b"* text=auto eol=lf\n*.bin binary\n"
    repo = make_repo(env, {".gitattributes": original})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert (repo / ".gitattributes").read_bytes() == original
    assert row(out, ".gitattributes") == "preserved"


def test_renormalization_report(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {"README.md": "# App\n", "notes.txt": b"one\r\ntwo\r\n", "mixed.txt": b"a\r\nb\n"})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 1
    assert not (repo / ".gitattributes").exists()
    assert "not created" in row(out, ".gitattributes")
    listing = out[out.index("so .gitattributes was left out"):]
    assert "notes.txt" in listing and "mixed.txt" in listing and "README.md" not in listing.split("Add it")[0]
    assert "git add --renormalize ." in out
    assert "separate commit" in out
    assert (repo / "notes.txt").read_bytes() == b"one\r\ntwo\r\n"


def test_created_file_ignored_by_project_is_reported(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {".gitignore": ".claude/\n.env\n.env.*\n!.env.example\ncontext.md\n"})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 1
    assert "ignored by .gitignore" in row(out, ".claude/skills/resume/SKILL.md")


# AC-3: preflight failures write nothing


@pytest.mark.parametrize("change", ["modified", "staged", "untracked"])
def test_dirty_tree_refused(change: str, env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env)
    if change == "untracked":
        (repo / "scratch.txt").write_text("new\n", encoding="utf-8")
    else:
        (repo / "README.md").write_text("# Changed\n", encoding="utf-8")
        if change == "staged":
            git(repo, "add", "README.md")
    before = snapshot(repo)
    code, _, err = run_adopt(env, repo, capfd)
    assert code == 2
    assert "working tree is not clean" in err
    assert ("scratch.txt" if change == "untracked" else "README.md") in err
    assert_nothing_written(repo, before)


def test_ignored_files_do_not_block(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {".gitignore": "*.log\n"})
    (repo / "debug.log").write_text("noise\n", encoding="utf-8")
    assert run_adopt(env, repo, capfd)[0] == 0


@pytest.mark.parametrize("folder, flag", [("My_App", None), ("app", "Bad Name")])
def test_invalid_name_refused(folder: str, flag: str | None, env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, name=folder)
    before = snapshot(repo)
    code, _, err = run_adopt(env, repo, capfd, *(["--name", flag] if flag else []))
    assert code == 2
    assert "invalid project name" in err
    assert_nothing_written(repo, before)


def test_differing_template_owned_path_refused(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {"README.md": "# App\n", "docs/AGENT_PROTOCOL.md": "# Our protocol\n",
                           ".agents/skills/handoff/SKILL.md": "Our handoff\n"})
    before = snapshot(repo)
    code, _, err = run_adopt(env, repo, capfd)
    assert code == 2
    assert "template-owned paths exist and differ" in err
    assert "docs/AGENT_PROTOCOL.md" in err and ".agents/skills/handoff/SKILL.md" in err
    assert_nothing_written(repo, before)


def test_identical_template_owned_path_preserved(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    protocol = (TEMPLATE / "docs" / "AGENT_PROTOCOL.md").read_bytes()
    repo = make_repo(env, {"docs/AGENT_PROTOCOL.md": protocol})
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert row(out, "docs/AGENT_PROTOCOL.md") == "preserved; identical to the template"


def test_already_adopted_refused(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {".copier-answers.yml": "_src_path: x\n"})
    code, _, err = run_adopt(env, repo, capfd)
    assert code == 2
    assert ".copier-answers.yml already exists" in err


def test_subdirectory_refused(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {"sub/file.txt": "x\n"})
    code, _, err = run_adopt(env, repo / "sub", capfd)
    assert code == 2
    assert "adopt the repository root" in err


# AC-2: a plain folder


def plain_folder(env: Env) -> Path:
    folder = env.work / "plain"
    folder.mkdir()
    return folder


def test_plain_folder_without_terminal(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    folder = plain_folder(env)
    (folder / "main.py").write_text("print()\n", encoding="utf-8")
    code, _, err = run_adopt(env, folder, capfd)
    assert code == 2
    assert "git init -b main" in err
    assert sorted(p.name for p in folder.iterdir()) == ["main.py"]


@pytest.mark.parametrize("answer", ["n", ""])
def test_plain_folder_declined(answer: str, env: Env, monkeypatch: pytest.MonkeyPatch,
                               capfd: pytest.CaptureFixture[str]) -> None:
    folder = plain_folder(env)
    prompts = []
    monkeypatch.setattr(adopt, "interactive", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or answer)
    code, _, _ = run_adopt(env, folder, capfd)
    assert code == 2
    assert prompts and prompts[0].endswith("Run git init -b main? [y/N] ")
    assert list(folder.iterdir()) == []


def test_plain_folder_initialized_on_yes(env: Env, monkeypatch: pytest.MonkeyPatch,
                                         capfd: pytest.CaptureFixture[str]) -> None:
    folder = plain_folder(env)
    monkeypatch.setattr(adopt, "interactive", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    code, out, _ = run_adopt(env, folder, capfd)
    assert code == 0
    assert git(folder, "symbolic-ref", "--short", "HEAD") == "main"
    assert (folder / "AGENTS.md").is_file()


def test_plain_folder_with_files_needs_a_first_commit(env: Env, monkeypatch: pytest.MonkeyPatch,
                                                      capfd: pytest.CaptureFixture[str]) -> None:
    folder = plain_folder(env)
    (folder / "main.py").write_text("print()\n", encoding="utf-8")
    monkeypatch.setattr(adopt, "interactive", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    code, _, err = run_adopt(env, folder, capfd)
    assert code == 2
    assert "main.py" in err
    assert not (folder / "AGENTS.md").exists()


# AC-6: origin/HEAD


def test_sets_origin_head(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env)
    remote = env.remotes / "app.git"
    git(env.remotes, "init", "--quiet", "--bare", "-b", "main", str(remote))
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "--quiet", "origin", "main")
    assert git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False) == ""
    code, out, _ = run_adopt(env, repo, capfd)
    assert code == 0
    assert git(repo, "symbolic-ref", "refs/remotes/origin/HEAD") == "refs/remotes/origin/main"
    assert "git remote set-head origin --auto" in out
    assert "Default branch: main (step 1" in out


# AC-7: doctor after committing the adoption


def test_doctor_after_committed_adoption(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(env, {"README.md": "# App\n", "src/app.py": "print('hi')\n", ".gitignore": "build/\n"})
    assert not (repo / "AGENTS.md").exists()
    assert run_adopt(env, repo, capfd)[0] == 0
    git(repo, "add", "-A")
    git(repo, "commit", "--quiet", "-m", "Adopt the project template")
    assert newproj("doctor", str(repo)) == 0
    out = capfd.readouterr().out
    assert "  FAIL" not in out
    assert " 0 FAIL" in out
