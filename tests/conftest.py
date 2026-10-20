"""Fixtures for running `newproj new` and `newproj doctor` in process, isolated from the machine.

Each test gets its own Git configuration, home and cache directories, and a fake `gh`
first on PATH. Sockets are blocked, so nothing reaches the network.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from newproj import cli

ROOT = Path(__file__).resolve().parent.parent
FAKE_GH = Path(__file__).resolve().parent / "fake_gh.py"


@dataclass
class Env:
    tmp: Path
    bin: Path
    gitconfig: Path
    remotes: Path
    gh_log: Path
    template: Path
    work: Path
    monkeypatch: pytest.MonkeyPatch

    def gh_mode(self, mode: str) -> None:
        self.monkeypatch.setenv("FAKE_GH_MODE", mode)

    def gh_calls(self) -> list[str]:
        return self.gh_log.read_text(encoding="utf-8").splitlines() if self.gh_log.exists() else []


def write_gitconfig(path: Path, identity: bool = True) -> None:
    # Detached maintenance can remove loose objects during Copier's local clone.
    # Disable both maintenance and older Git's auto-GC in every test subprocess.
    lines = ["[commit]", "\tgpgsign = false", "[tag]", "\tgpgsign = false",
             "[credential]", "\thelper = store", "[init]", "\tdefaultBranch = main",
             "[maintenance]", "\tauto = false", "[gc]", "\tauto = 0"]
    if identity:
        lines += ["[user]", "\tname = Test User", "\temail = test@example.com"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_fake_gh(bin_dir: Path) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        (bin_dir / "gh.cmd").write_text(f'@"{sys.executable}" "{FAKE_GH}" %*\r\n', encoding="utf-8")
    else:
        script = bin_dir / "gh"
        script.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FAKE_GH}" "$@"\n', encoding="utf-8")
        script.chmod(0o755)


def copy_template(dest: Path) -> Path:
    """A plain copy of the working tree's template, so Copier renders it as it is."""
    shutil.copytree(ROOT / "template", dest / "template")
    shutil.copy2(ROOT / "copier.yml", dest / "copier.yml")
    return dest


def isolate(monkeypatch: pytest.MonkeyPatch, tmp: Path) -> Env:
    env = Env(tmp, tmp / "bin", tmp / "gitconfig", tmp / "remotes", tmp / "gh.log",
              tmp / "template-src", tmp / "work", monkeypatch)
    home = tmp / "home"
    for path in (home, env.remotes, env.work):
        path.mkdir(parents=True, exist_ok=True)
    write_gitconfig(env.gitconfig)
    install_fake_gh(env.bin)
    copy_template(env.template)
    for key in [k for k in os.environ if k.startswith("GIT_") or k.startswith("GH_")]:
        monkeypatch.delenv(key)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(env.gitconfig))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("LOCALAPPDATA", str(home / "AppData" / "Local"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(home / ".cache"))
    monkeypatch.setenv("PATH", str(env.bin) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("FAKE_GH_REMOTES", str(env.remotes))
    monkeypatch.setenv("FAKE_GH_LOG", str(env.gh_log))
    monkeypatch.setenv("FAKE_GH_MODE", "ok")
    monkeypatch.chdir(env.work)

    def no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("a test tried to use the network")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    return env


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Env:
    return isolate(monkeypatch, tmp_path)


def newproj(*args: str) -> int:
    return cli.main(list(args))


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


@pytest.fixture(scope="session")
def base_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One project made by `newproj new --no-remote`, copied by each test that needs it."""
    tmp = tmp_path_factory.mktemp("base")
    with pytest.MonkeyPatch.context() as monkeypatch:
        env = isolate(monkeypatch, tmp)
        assert newproj("new", "demo", "--no-remote", "--template-path", str(env.template)) == 0
    return env.work / "demo"


@pytest.fixture
def project(env: Env, base_project: Path) -> Path:
    dest = env.work / "demo"
    shutil.copytree(base_project, dest, symlinks=True)
    return dest
