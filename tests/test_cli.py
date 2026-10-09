"""Exercise the installed console script on every supported platform."""

from importlib.metadata import version
from pathlib import Path
import subprocess
import sysconfig

import pytest


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    scripts = Path(sysconfig.get_path("scripts"))
    executable = scripts / ("newproj.exe" if sysconfig.get_platform().startswith("win") else "newproj")
    return subprocess.run(
        [str(executable), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_version(tmp_path: Path) -> None:
    result = run_cli("--version", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == version("newproj")
    assert result.stderr == ""


def test_help(tmp_path: Path) -> None:
    result = run_cli("--help", cwd=tmp_path)
    assert result.returncode == 0
    assert "{new,adopt,doctor}" in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("command", ["new", "adopt", "doctor"])
def test_subcommand_stub(command: str, tmp_path: Path) -> None:
    result = run_cli(command, cwd=tmp_path)
    assert result.returncode == 2
    assert result.stdout.strip() == f"newproj {command} is not implemented yet."
    assert result.stderr == ""


@pytest.mark.parametrize("command", ["new", "adopt", "doctor"])
def test_subcommand_help(command: str, tmp_path: Path) -> None:
    result = run_cli(command, "--help", cwd=tmp_path)
    assert result.returncode == 0
    assert f"usage: newproj {command}" in result.stdout
    assert "not implemented" not in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("args", [[], ["unknown"]])
def test_command_required(args: list[str], tmp_path: Path) -> None:
    result = run_cli(*args, cwd=tmp_path)
    assert result.returncode == 2
    assert "usage:" in result.stderr
    assert result.stdout == ""
