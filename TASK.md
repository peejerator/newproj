# Task

Status: active
Tier: standard
Task ID:
Base commit:
Target branch:
Issue:
PR:

## Goal

Milestone M1: create the Python package skeleton, CLI entry point, test suite, and CI for `newproj`, so later milestones have a working, tested foundation on macOS and Windows.

## Context

The repository currently holds the frozen spec (`docs/spec.md`), planning documents, and a verified `copier.yml`. No code exists yet. See `docs/ROADMAP.md` for where M1 fits. Relevant spec sections: 6 (template repository layout), 20 (CLI introduction), D15.

## Scope

- `pyproject.toml` for a src-layout package named `newproj`.
- `src/newproj/` with a CLI built on `argparse` (D-002).
- `tests/` with pytest.
- `.github/workflows/ci.yml`.
- The Commands section of `AGENTS.md` if the commands differ from those listed.

## Acceptance criteria

- AC-1: `pyproject.toml` defines the `newproj` package (src layout), `requires-python = ">=3.11"`, a `newproj` console script, and a single runtime dependency, `copier>=9.18.2,<10`. Development dependencies (pytest) are in a dependency group, not runtime dependencies.
- AC-2: `newproj --version` prints the package version, which is defined in exactly one place.
- AC-3: `newproj --help` lists the subcommands `new`, `adopt`, and `doctor`. Each subcommand exists, prints that it is not implemented yet, and exits with status 2.
- AC-4: `uv run pytest` passes, with tests covering AC-2 and AC-3 by invoking the installed console script (not only importing functions).
- AC-5: CI runs `uv run pytest` on `ubuntu-latest`, `macos-latest`, and `windows-latest` for every push and pull request (D-003). It uses the official `astral-sh/setup-uv` action.
- AC-6: `uv.lock` is committed.

## Relevant areas

- `pyproject.toml`
- `src/newproj/`
- `tests/`
- `.github/workflows/ci.yml`
- `AGENTS.md` (Commands section only)

## Validation

- `uv sync`
- `uv run pytest`
- `uv run newproj --version`
- `uv run newproj --help`
- CI passes on all three operating systems on the M1 pull request.

## Do not change

- `docs/spec.md`
- `copier.yml` and `template/`
- `TASK.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
