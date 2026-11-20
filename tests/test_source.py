"""Rendering from a local repository while Git maintenance runs in it (issue #35)."""

from __future__ import annotations

import subprocess
import threading
import time
from pathlib import Path

import pytest

from conftest import Env, git, newproj
from newproj import source


class GitError(Exception):
    """Stands in for plumbum's ProcessExecutionError, which Copier raises for a failed Git command."""

    def __init__(self, *argv: str) -> None:
        super().__init__("git failed")
        self.argv = list(argv)


def template_repo(env: Env) -> Path:
    """The template as a committed Git repository, with its objects loose."""
    repo = env.template
    git(repo, "init", "--quiet")
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "-m", "Template")
    return repo


def fake_copier(monkeypatch: pytest.MonkeyPatch, failures: list[Exception]) -> list[str]:
    """Replace Copier's copy: raise each of `failures` in turn, then succeed. Record waits and copies."""
    calls = []
    monkeypatch.setattr(source, "wait_for_maintenance", lambda repo: calls.append("wait"))

    def run_copy(*args: object, **kwargs: object) -> None:
        calls.append("copy")
        if failures:
            raise failures.pop(0)

    monkeypatch.setattr(source.copier, "run_copy", run_copy)
    return calls


def test_retries_once_after_a_git_failure(env: Env, monkeypatch: pytest.MonkeyPatch,
                                          capfd: pytest.CaptureFixture[str]) -> None:
    calls = fake_copier(monkeypatch, [GitError("/usr/bin/git", "clone", "--no-checkout")])
    source.render("demo", env.work / "demo", env.template, quiet=True)
    assert calls == ["wait", "copy", "wait", "copy"]
    assert "retrying once" in capfd.readouterr().err


def test_windows_git_failure_is_retried(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = fake_copier(monkeypatch, [GitError("C:\\Program Files\\Git\\cmd\\GIT.EXE", "clone")])
    source.render("demo", env.work / "demo", env.template, quiet=True)
    assert calls.count("copy") == 2


def test_second_git_failure_is_raised(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = fake_copier(monkeypatch, [GitError("git", "clone"), GitError("git", "checkout")])
    with pytest.raises(GitError):
        source.render("demo", env.work / "demo", env.template, quiet=True)
    assert calls.count("copy") == 2


def test_other_failures_are_not_retried(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = fake_copier(monkeypatch, [ValueError("bad answer")])
    with pytest.raises(ValueError):
        source.render("demo", env.work / "demo", env.template, quiet=True)
    assert calls == ["wait", "copy"]


@pytest.mark.parametrize("lock", ["objects/maintenance.lock", "gc.pid"])
def test_waits_for_a_maintenance_lock(env: Env, lock: str) -> None:
    repo = template_repo(env)
    path = repo / ".git" / lock
    path.write_text("", encoding="utf-8")
    timer = threading.Timer(1.0, path.unlink)
    timer.start()
    start = time.monotonic()
    source.wait_for_maintenance(repo, timeout=30)
    timer.join()
    assert time.monotonic() - start >= 0.9
    assert not path.exists()


def test_stale_lock_wait_is_bounded(env: Env) -> None:
    repo = template_repo(env)
    (repo / ".git" / "objects" / "maintenance.lock").write_text("", encoding="utf-8")
    start = time.monotonic()
    source.wait_for_maintenance(repo, timeout=1)
    assert time.monotonic() - start < 10


def test_no_wait_outside_a_repository(env: Env) -> None:
    start = time.monotonic()
    source.wait_for_maintenance(env.template, timeout=30)
    assert time.monotonic() - start < 10


def test_new_waits_for_a_repack_in_progress(env: Env) -> None:
    """A repack holding the maintenance lock deletes loose objects; `newproj new` waits for it."""
    repo = template_repo(env)
    git(repo, "repack", "--quiet")  # Pack the objects but keep the loose copies, for prune-packed to delete.
    loose = [p for p in (repo / ".git" / "objects").glob("??/*")]
    assert loose
    lock = repo / ".git" / "objects" / "maintenance.lock"
    lock.write_text("", encoding="utf-8")

    def maintenance() -> None:
        time.sleep(1.0)
        subprocess.run(["git", "prune-packed"], cwd=repo, check=True)
        lock.unlink()

    thread = threading.Thread(target=maintenance)
    thread.start()
    try:
        assert newproj("new", "demo", "--no-remote", "--template-path", str(repo)) == 0
    finally:
        thread.join()
    assert not any(p.exists() for p in loose)
    assert (env.work / "demo" / "AGENTS.md").is_file()
