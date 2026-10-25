"""Set up and check the behavioral fixtures in tests/fixtures/behavior/ (spec 23.2, docs/DECISIONS.md D-008).

  uv run python scripts/behavior.py setup <id> <dir>
  uv run python scripts/behavior.py check <id> <dir>

`setup` creates a project at <dir> with `newproj new --no-remote --template-path <this repository>`,
plants the fixture's state, makes a baseline commit, and writes a manifest to <dir>/../.behavior/<name>/,
outside the project, so the agent never sees it. `check` compares the project with that manifest and
prints PASS, FAIL, or JUDGE with the items a person judges from the session transcript.

Each fixture directory holds prompt.txt, notes.md, setup.py, and check.py. setup.py defines
`plant(project)`, optionally `dirty(project)` for uncommitted changes made after the baseline commit,
and optionally `COMMIT_MESSAGE`. check.py defines `JUDGE` (a list of judged items) and
`check(result)`, which returns the failed scripted conditions.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

from newproj import state

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "behavior"
FIXTURE_IDS = ["B1", "B4", "B5", "B6", "B9", "B10", "B11"]
STATE_PY = ".agents/skills/resume/scripts/state.py"
NEWPROJ = "import sys; from newproj.cli import main; sys.exit(main(sys.argv[1:]))"


class HarnessError(Exception):
    pass


def git_env() -> dict[str, str]:
    """The caller's environment, with commit signing off: fixture projects are disposable and local."""
    env = dict(os.environ)
    count = int(env.get("GIT_CONFIG_COUNT", "0") or "0")
    for key, value in (("commit.gpgsign", "false"), ("tag.gpgsign", "false")):
        env[f"GIT_CONFIG_KEY_{count}"] = key
        env[f"GIT_CONFIG_VALUE_{count}"] = value
        count += 1
    env["GIT_CONFIG_COUNT"] = str(count)
    return env


def run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, env=git_env(), stdin=subprocess.DEVNULL, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", check=False)
    if check and result.returncode != 0:
        raise HarnessError(f"{' '.join(args[:3])} failed in {cwd}:\n{result.stdout}{result.stderr}".rstrip())
    return result


class Project:
    """The fixture project, as setup.py and check.py see it."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, rel: str) -> Path:
        return self.root / rel

    def write(self, rel: str, text: str) -> None:
        path = self.path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def read(self, rel: str) -> str:
        return self.path(rel).read_text(encoding="utf-8")

    def replace(self, rel: str, old: str, new: str) -> None:
        text = self.read(rel)
        if text.count(old) != 1:
            raise HarnessError(f"{rel}: expected exactly one {old!r}")
        self.write(rel, text.replace(old, new))

    def git(self, *args: str) -> str:
        return run(["git", *args], self.root).stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def files(self) -> dict[str, str]:
        """SHA-256 of every tracked and untracked, not ignored, file."""
        listed = self.git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
        hashes = {}
        for rel in sorted(set(filter(None, listed))):
            path = self.path(rel)
            if path.is_file():
                hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        return hashes

    def refs(self) -> dict[str, str]:
        out = self.git("for-each-ref", "--format=%(refname) %(objectname)")
        return dict(line.split(" ", 1) for line in out.splitlines())

    def snapshot(self) -> dict[str, object]:
        return {
            "head": self.git("rev-parse", "HEAD"),
            "branch": self.git("branch", "--show-current"),
            "refs": self.refs(),
            "status": self.git("status", "--porcelain=v1", "--untracked-files=all").splitlines(),
            "files": self.files(),
        }


class Result:
    """The project compared with its manifest, for check.py."""

    def __init__(self, project: Project, manifest: dict) -> None:
        self.project = project
        self.manifest = manifest
        self.now = project.snapshot()
        before, after = manifest["files"], self.now["files"]
        self.added = sorted(set(after) - set(before))
        self.deleted = sorted(set(before) - set(after))
        self.modified = sorted(p for p in set(before) & set(after) if before[p] != after[p])

    def changed(self, prefix: str = "") -> list[str]:
        """Paths added, deleted, or modified since setup, limited to a file or directory prefix."""
        paths = sorted(self.added + self.deleted + self.modified)
        if not prefix:
            return paths
        return [p for p in paths if p == prefix or p.startswith(prefix.rstrip("/") + "/")]

    def head_moved(self) -> bool:
        return self.now["head"] != self.manifest["head"]

    def new_commits(self) -> list[str]:
        """Commits reachable from any ref or HEAD now that were not reachable at setup."""
        known = [f"^{sha}" for sha in sorted(set(self.manifest["refs"].values()) | {self.manifest["head"]})]
        out = self.project.git("rev-list", "--all", "HEAD", *known)
        return out.splitlines()

    def exists(self, rel: str) -> bool:
        return self.project.path(rel).exists()

    def neutral(self, name: str) -> bool:
        """Whether TASK.md or HANDOFF.md is in the neutral state, as state.py reads it."""
        loaded = state.load(self.project.root)
        return loaded.task_neutral if name == "TASK.md" else loaded.handoff_neutral

    def state_check(self) -> tuple[bool, str]:
        result = run([sys.executable, STATE_PY, "check"], self.project.root, check=False)
        return result.returncode == 0, (result.stdout + result.stderr).strip()


def fixture_module(fixture: str, name: str) -> ModuleType:
    path = FIXTURES / fixture / f"{name}.py"
    if str(FIXTURES) not in sys.path:
        sys.path.insert(0, str(FIXTURES))  # for the shared planted content in shared.py
    spec = importlib.util.spec_from_file_location(f"behavior_{fixture}_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest_path(project_dir: Path) -> Path:
    return project_dir.parent / ".behavior" / project_dir.name / "manifest.json"


def inside_git_repository(path: Path) -> bool:
    probe = path
    while not probe.exists():
        probe = probe.parent
    return run(["git", "rev-parse", "--show-toplevel"], probe, check=False).returncode == 0


def setup(fixture: str, project_dir: Path, template_path: Path) -> Path:
    if inside_git_repository(project_dir.parent):
        raise HarnessError(f"{project_dir.parent} is inside a Git repository; choose a directory outside any "
                           "repository, so the agent sees only the fixture project")
    project_dir.parent.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "-c", NEWPROJ, "new", project_dir.name, "--no-remote",
         "--template-path", str(template_path)], project_dir.parent)
    project = Project(project_dir)
    module = fixture_module(fixture, "setup")
    module.plant(project)
    project.commit(getattr(module, "COMMIT_MESSAGE", "Add project files"))
    if hasattr(module, "dirty"):
        module.dirty(project)
    manifest = {"fixture": fixture, "project": str(project_dir),
                "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **project.snapshot()}
    path = manifest_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def check(fixture: str, project_dir: Path) -> tuple[str, list[str]]:
    """The verdict and the lines to print."""
    path = manifest_path(project_dir)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise HarnessError(f"no manifest at {path}; run setup first ({error.strerror})") from None
    if manifest["fixture"] != fixture:
        raise HarnessError(f"{project_dir} was set up for {manifest['fixture']}, not {fixture}")
    result = Result(Project(project_dir), manifest)
    module = fixture_module(fixture, "check")
    failures = module.check(result)
    judged = list(module.JUDGE)
    verdict = "FAIL" if failures else "JUDGE" if judged else "PASS"
    lines = [f"{fixture}: {verdict}"]
    if failures:
        lines += ["Failed conditions:"] + [f"  - {failure}" for failure in failures]
    elif judged:
        lines += ["Scripted conditions passed. Judge from the transcript:"] + [f"  - {item}" for item in judged]
    lines.append("Changes since setup:")
    changes = [f"  added {p}" for p in result.added] + [f"  deleted {p}" for p in result.deleted]
    changes += [f"  modified {p}" for p in result.modified]
    commits = result.new_commits()
    if commits:
        changes.append(f"  {len(commits)} new commit{'s' * (len(commits) != 1)}")
    if result.now["branch"] != manifest["branch"]:
        changes.append(f"  branch {manifest['branch']} -> {result.now['branch']}")
    lines += changes or ["  none"]
    return verdict, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="behavior.py", description="Set up and check behavioral fixtures.")
    parser.add_argument("command", choices=["setup", "check"])
    parser.add_argument("fixture", choices=FIXTURE_IDS, type=str.upper, metavar="id",
                        help=f"fixture ID: {', '.join(FIXTURE_IDS)}")
    parser.add_argument("dir", type=Path, help="the fixture project's directory")
    parser.add_argument("--template-path", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    project_dir = args.dir.resolve()
    try:
        if args.command == "setup":
            path = setup(args.fixture, project_dir, args.template_path.resolve())
            print(f"Set up {args.fixture} at {project_dir}")
            print(f"Manifest: {path}")
            print(f"Prompt: {FIXTURES / args.fixture / 'prompt.txt'}")
            print(f"Notes: {FIXTURES / args.fixture / 'notes.md'}")
            return 0
        verdict, lines = check(args.fixture, project_dir)
    except HarnessError as error:
        print(f"behavior.py: {error}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
