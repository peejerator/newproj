"""Exercise the installed console script on every supported platform."""

from importlib.metadata import version
from pathlib import Path
import subprocess
import sysconfig
import tomllib

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


def test_adopt_not_implemented(tmp_path: Path) -> None:
    result = run_cli("adopt", cwd=tmp_path)
    assert result.returncode == 2
    assert result.stdout.strip() == "newproj adopt is not implemented yet."
    assert result.stderr == ""


def test_new_requires_name(tmp_path: Path) -> None:
    result = run_cli("new", cwd=tmp_path)
    assert result.returncode == 2
    assert "the following arguments are required: name" in result.stderr


def test_new_help_hides_template_path(tmp_path: Path) -> None:
    result = run_cli("new", "--help", cwd=tmp_path)
    for flag in ["--public", "--no-remote", "--owner"]:
        assert flag in result.stdout
    assert "--template-path" not in result.stdout


def test_no_new_runtime_dependency() -> None:
    pyproject = tomllib.loads((Path(__file__).resolve().parent.parent / "pyproject.toml").read_text("utf-8"))
    assert pyproject["project"]["dependencies"] == ["copier>=9.18.2,<10"]


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
