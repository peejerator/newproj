"""The template source: a cached clone of the template repository, used at the CLI's tag (spec section 20)."""

from __future__ import annotations

import os
import sys
from importlib.metadata import version
from pathlib import Path

import copier

from newproj.tools import run

# docs/DECISIONS.md, D-001.
TEMPLATE_URL = "https://github.com/peejerator/newproj.git"
FETCH_TIMEOUT = 300
ANSWERS = ".copier-answers.yml"


class SourceError(Exception):
    """The template cannot be provided at the required tag."""


def tag() -> str:
    return f"v{version('newproj')}"


def cache_dir() -> Path:
    """The per-user cache directory for newproj."""
    home = Path.home()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        return (Path(base) if base else home / "AppData" / "Local") / "newproj" / "Cache"
    if sys.platform == "darwin":
        return home / "Library" / "Caches" / "newproj"
    base = os.environ.get("XDG_CACHE_HOME")
    return (Path(base) if base else home / ".cache") / "newproj"


def has_tag(clone: Path, name: str) -> bool:
    return run("git", "rev-parse", "--verify", "--quiet", f"refs/tags/{name}^{{commit}}", cwd=clone).ok


def template_clone(name: str) -> Path:
    """A bare clone of the template repository that contains tag `name`.

    Fetches only when the tag is missing, so it works offline once the cache has the tag.
    """
    clone = cache_dir() / "template.git"
    if not (clone / "HEAD").is_file():
        clone.parent.mkdir(parents=True, exist_ok=True)
        result = run("git", "clone", "--quiet", "--bare", TEMPLATE_URL, str(clone), timeout=FETCH_TIMEOUT)
        if not result.ok:
            raise SourceError(
                f"could not clone the template repository {TEMPLATE_URL} into {clone}:\n  {result.err}\n"
                "Check the network connection and the Git credentials (newproj doctor), then try again."
            )
    if has_tag(clone, name):
        return clone
    result = run("git", "fetch", "--quiet", "--tags", "--force", TEMPLATE_URL,
                 "+refs/heads/*:refs/heads/*", cwd=clone, timeout=FETCH_TIMEOUT)
    if has_tag(clone, name):
        return clone
    reason = f"fetching failed:\n  {result.err}" if not result.ok else "the repository has no such tag"
    raise SourceError(
        f"the template tag {name} is not in the cached clone {clone}, and {reason}\n"
        f"newproj {name[1:]} renders the template only at its own tag (spec section 20). "
        f"Install a released version (uv tool install git+{TEMPLATE_URL.removesuffix('.git')}@<tag>), "
        "or try again once the network is available."
    )


def render(name: str, target: Path, template_path: Path | None, quiet: bool = False) -> None:
    """Run `copier copy` at the CLI's tag, or from `template_path`. Runs no Copier tasks (spec 19.3).

    `quiet` hides Copier's list of the files it writes.
    """
    interactive = sys.stdin.isatty()
    if not interactive:
        print("stdin is not a terminal: using the template's default answers.")
    options = dict(data={"project_name": name}, defaults=not interactive, skip_tasks=True, quiet=quiet)
    if template_path is not None:
        # HEAD renders the working tree, uncommitted changes included, even when the
        # directory is a Git repository with release tags (E-002).
        copier.run_copy(str(template_path.resolve()), target, vcs_ref="HEAD", **options)
        return
    name_tag = tag()
    clone = template_clone(name_tag)
    copier.run_copy(str(clone), target, vcs_ref=name_tag, **options)
    # Record the repository URL, not this machine's cache path, so the answers file
    # works on every machine and leaks no local path.
    answers = target / ANSWERS
    lines = answers.read_bytes().decode("utf-8").splitlines(keepends=True)
    lines = [f"_src_path: {TEMPLATE_URL}\n" if line.startswith("_src_path:") else line for line in lines]
    answers.write_bytes("".join(lines).encode("utf-8"))
