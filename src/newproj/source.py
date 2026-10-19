"""The template source: a cached clone of the template repository, used at the CLI's tag (spec section 20)."""

from __future__ import annotations

import os
import sys
from importlib.metadata import version
from pathlib import Path

from newproj.tools import run

# docs/DECISIONS.md, D-001.
TEMPLATE_URL = "https://github.com/peejerator/newproj.git"
FETCH_TIMEOUT = 300


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
