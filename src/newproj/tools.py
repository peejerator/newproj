"""Running external tools (git, gh, uv) the same way on macOS, Linux, and Windows."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

TIMEOUT = 60


@dataclass
class Result:
    code: int
    out: str
    err: str

    @property
    def ok(self) -> bool:
        return self.code == 0


def which(tool: str) -> str | None:
    """The tool's full path, so Windows can run `.cmd` and `.exe` shims alike."""
    return shutil.which(tool)


def run(tool: str, *args: str, cwd: Path | None = None, timeout: float | None = TIMEOUT,
        capture: bool = True) -> Result:
    """Run a tool; never raises. A missing tool gives code -1.

    With `capture` false the tool shares the terminal, so it can show progress and ask
    for a signing passphrase, and `out` and `err` stay empty.
    """
    path = which(tool)
    if path is None:
        return Result(-1, "", f"{tool} not found on PATH")
    if not capture:
        try:
            return Result(subprocess.run([path, *args], cwd=cwd, timeout=timeout).returncode, "", "")
        except (OSError, subprocess.SubprocessError) as error:
            return Result(-1, "", str(error))
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    try:
        done = subprocess.run(
            [path, *args], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return Result(-1, "", str(error))
    return Result(
        done.returncode,
        done.stdout.decode("utf-8", errors="replace").strip(),
        done.stderr.decode("utf-8", errors="replace").strip(),
    )


def git_config(key: str, cwd: Path | None = None) -> str:
    result = run("git", "config", "--get", key, cwd=cwd)
    return result.out if result.ok else ""
