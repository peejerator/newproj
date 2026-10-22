"""`newproj new` (spec section 20.1), with a fake gh and local bare repositories as remotes."""

from __future__ import annotations

import os
import shutil
from importlib.metadata import version
from pathlib import Path

import pytest

from conftest import Env, git, newproj, write_gitconfig
from newproj import new, source

TAG = f"v{version('newproj')}"
MESSAGE = f"Initialize from project-template {TAG}"


def new_local(env: Env, *args: str) -> int:
    return newproj("new", "demo", "--template-path", str(env.template), *args)


def assert_committed(project: Path) -> None:
    assert git(project, "log", "--format=%s") == MESSAGE
    assert git(project, "status", "--porcelain", "--untracked-files=all") == ""
    assert git(project, "branch", "--show-current") == "main"
    assert git(project, "config", "core.hooksPath") == ".githooks"


# AC-1: local repository


def test_new_no_remote(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    assert new_local(env, "--no-remote") == 0
    project = env.work / "demo"
    assert_committed(project)
    tracked = set(git(project, "ls-files").splitlines())
    on_disk = {p.relative_to(project).as_posix() for p in project.rglob("*")
               if p.is_file() and ".git" not in p.relative_to(project).parts[:1]}
    assert tracked == on_disk
    assert ".githooks/commit-msg" in tracked
    assert env.gh_calls() == []
    assert MESSAGE in capfd.readouterr().out


def test_new_runs_no_copier_tasks(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    original = source.copier.run_copy

    def spy(*args: object, **kwargs: object) -> object:
        calls.append(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(source.copier, "run_copy", spy)
    assert new_local(env, "--no-remote") == 0
    assert len(calls) == 1 and calls[0]["skip_tasks"] is True
    assert calls[0]["data"] == {"project_name": "demo"}


def test_new_into_empty_directory(env: Env) -> None:
    (env.work / "demo").mkdir()
    assert new_local(env, "--no-remote") == 0
    assert_committed(env.work / "demo")


# AC-1: remote


def test_new_with_remote(env: Env) -> None:
    assert new_local(env) == 0
    project = env.work / "demo"
    assert_committed(project)
    remote = env.remotes / "fake-user" / "demo.git"
    assert git(project, "remote", "get-url", "origin") == str(remote)
    assert git(remote, "rev-parse", "main") == git(project, "rev-parse", "HEAD")
    assert git(project, "symbolic-ref", "refs/remotes/origin/HEAD") == "refs/remotes/origin/main"
    calls = env.gh_calls()
    assert "api user --jq .login" in calls
    assert "repo create fake-user/demo --private --source . --remote origin --push" in calls


def test_new_public_with_owner(env: Env) -> None:
    assert new_local(env, "--public", "--owner", "some-org") == 0
    calls = env.gh_calls()
    assert not any(call.startswith("api user") for call in calls)
    assert "repo create some-org/demo --public --source . --remote origin --push" in calls
    assert (env.remotes / "some-org" / "demo.git").is_dir()


def test_new_remote_failure(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    env.gh_mode("fail-create")
    assert new_local(env) == 1
    project = env.work / "demo"
    assert_committed(project)
    err = capfd.readouterr().err
    assert "is complete and committed" in err
    assert f"cd {project}" in err
    assert "gh repo create fake-user/demo --private --source . --remote origin --push" in err
    assert "git remote set-head origin --auto" in err
    # The project is usable: doctor finds nothing wrong with it.
    assert newproj("doctor", str(project)) == 0
    assert "0 FAIL" in capfd.readouterr().out


def test_new_remote_failure_after_create(env: Env, monkeypatch: pytest.MonkeyPatch,
                                         capfd: pytest.CaptureFixture[str]) -> None:
    # origin exists and is pushed, but setting origin/HEAD fails: only that step remains.
    original = new.run

    def failing_set_head(*args: str, **kwargs: object) -> object:
        if list(args) == new.SET_HEAD:
            return original("git", "remote", "set-head", "origin", "no-such-branch", cwd=kwargs.get("cwd"))
        return original(*args, **kwargs)

    monkeypatch.setattr(new, "run", failing_set_head)
    assert new_local(env) == 1
    err = capfd.readouterr().err
    assert "gh repo create" not in err.split("To finish the remote setup, run:")[1]
    assert "  git remote set-head origin --auto" in err


# AC-1: preflight


def assert_preflight_fails(capfd: pytest.CaptureFixture[str], code: int, *expected: str) -> None:
    assert code == 1
    err = capfd.readouterr().err
    assert "preflight failed" in err
    for text in expected:
        assert text in err


def test_preflight_invalid_name(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    code = newproj("new", "Bad_Name", "--no-remote", "--template-path", str(env.template))
    assert_preflight_fails(capfd, code, "invalid project name")
    assert not (env.work / "Bad_Name").exists()


def test_preflight_target_not_empty(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    (env.work / "demo").mkdir()
    (env.work / "demo" / "file.txt").write_text("x", encoding="utf-8")
    assert_preflight_fails(capfd, new_local(env, "--no-remote"), "not an empty directory")
    assert [p.name for p in (env.work / "demo").iterdir()] == ["file.txt"]


def test_preflight_target_is_file(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    (env.work / "demo").write_text("x", encoding="utf-8")
    assert_preflight_fails(capfd, new_local(env, "--no-remote"), "not an empty directory")


def test_preflight_git_missing(env: Env, monkeypatch: pytest.MonkeyPatch,
                               capfd: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("PATH", str(env.bin))
    assert_preflight_fails(capfd, new_local(env, "--no-remote"), "git is not installed")
    assert not (env.work / "demo").exists()


@pytest.mark.parametrize("key", ["user.name", "user.email"])
def test_preflight_identity_missing(key: str, env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    write_gitconfig(env.gitconfig, identity=False)
    other = "user.email" if key == "user.name" else "user.name"
    git(env.work, "config", "--global", other, "x@example.com" if other == "user.email" else "X")
    assert_preflight_fails(capfd, new_local(env, "--no-remote"), f"Git {key} is not set")
    assert not (env.work / "demo").exists()


def test_preflight_gh_missing(env: Env, monkeypatch: pytest.MonkeyPatch,
                              capfd: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(new, "which", lambda tool: None if tool == "gh" else shutil.which(tool))
    assert_preflight_fails(capfd, new_local(env), "gh is not installed")
    assert not (env.work / "demo").exists()


def test_preflight_gh_unauthenticated(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    env.gh_mode("unauthenticated")
    assert_preflight_fails(capfd, new_local(env), "gh is not authenticated")
    assert not (env.work / "demo").exists()


def test_preflight_owner_unknown(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    env.gh_mode("no-user")
    assert_preflight_fails(capfd, new_local(env), "could not read the GitHub user", "pass --owner")
    assert not (env.work / "demo").exists()


def test_preflight_owner_flag_skips_gh_api(env: Env) -> None:
    env.gh_mode("no-user")
    assert new_local(env, "--owner", "some-org") == 0


def test_preflight_template_path_without_copier_yml(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    code = newproj("new", "demo", "--no-remote", "--template-path", str(env.tmp))
    assert_preflight_fails(capfd, code, "has no copier.yml")


def test_preflight_reports_every_problem(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    write_gitconfig(env.gitconfig, identity=False)
    env.gh_mode("unauthenticated")
    code = newproj("new", "Bad", "--template-path", str(env.template))
    assert_preflight_fails(capfd, code, "invalid project name", "user.name", "user.email", "not authenticated")


# AC-1: template source


def test_template_path_renders_working_tree_of_tagged_repository(env: Env, upstream: Path) -> None:
    git(upstream, "tag", "v0.0.1")
    (upstream / "template" / "development-change.txt").write_text("committed\n", encoding="utf-8")
    git(upstream, "add", "-A")
    git(upstream, "commit", "--quiet", "-m", "Change after the tag")
    (upstream / "template" / "dirty-change.txt").write_text("uncommitted\n", encoding="utf-8")
    assert new_local(env, "--no-remote") == 0
    project = env.work / "demo"
    assert_committed(project)
    assert (project / "development-change.txt").is_file()
    assert (project / "dirty-change.txt").is_file()
    assert "_commit: v0.0.1\n" not in (project / ".copier-answers.yml").read_text(encoding="utf-8")


def test_template_from_cached_clone(env: Env, upstream: Path) -> None:
    git(upstream, "tag", TAG)
    assert newproj("new", "demo", "--no-remote") == 0
    project = env.work / "demo"
    assert_committed(project)
    answers = (project / ".copier-answers.yml").read_text(encoding="utf-8")
    assert f"_commit: {TAG}\n" in answers
    assert f"_src_path: {source.TEMPLATE_URL}\n" in answers
    assert str(env.tmp / "cache") not in answers
    assert (env.tmp / "cache" / "template.git" / "HEAD").is_file()


def test_template_offline_with_cached_tag(env: Env, upstream: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    git(upstream, "tag", TAG)
    assert newproj("new", "first", "--no-remote") == 0
    monkeypatch.setattr(source, "TEMPLATE_URL", str(env.tmp / "unreachable"))
    assert newproj("new", "second", "--no-remote") == 0
    assert_committed(env.work / "second")


def test_template_fetches_missing_tag(env: Env, upstream: Path) -> None:
    git(upstream, "tag", "v0.0.1")
    source.template_clone("v0.0.1")
    assert not source.has_tag(env.tmp / "cache" / "template.git", TAG)
    git(upstream, "tag", TAG)
    assert newproj("new", "demo", "--no-remote") == 0
    assert source.has_tag(env.tmp / "cache" / "template.git", TAG)


def test_template_tag_not_found(env: Env, upstream: Path, capfd: pytest.CaptureFixture[str]) -> None:
    assert newproj("new", "demo", "--no-remote") == 1
    err = capfd.readouterr().err
    assert f"the template tag {TAG} is not in the cached clone" in err
    assert "has no such tag" in err
    assert not (env.work / "demo").exists()


def test_template_unreachable(env: Env, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(source, "TEMPLATE_URL", str(env.tmp / "unreachable"))
    monkeypatch.setattr(source, "cache_dir", lambda: env.tmp / "cache")
    assert newproj("new", "demo", "--no-remote") == 1
    assert "could not clone the template repository" in capfd.readouterr().err
    assert not (env.work / "demo").exists()


@pytest.mark.parametrize("platform, expected", [
    ("darwin", ("Library", "Caches", "newproj")),
    ("linux", (".cache", "newproj")),
    ("win32", ("AppData", "Local", "newproj", "Cache")),
])
def test_cache_dir(platform: str, expected: tuple[str, ...], env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(source.sys, "platform", platform)
    assert source.cache_dir().parts[-len(expected):] == expected
    assert str(source.cache_dir()).startswith(os.environ["HOME"])
