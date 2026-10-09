# Handoff

Last updated: 2026-10-09 by Codex (M1 implementation)
Branch: m1-skeleton
Task: standard

## Status

Implemented and locally verified. Pull request and CI verification pending.

## Completed

- M1 src-layout package, argparse console script, installed-script tests, CI matrix, and uv.lock implemented.
- Version is defined only in pyproject.toml and read from installed package metadata.
- D-005 records the user-approved build-only uv_build dependency.
- Existing AGENTS.md commands remain correct.

## Current working area

- M1 changes ready for commit and pull request to main.

## Validation

- PASS | pyproject.toml and source review | AC-1: src layout, Python >=3.11, console script, Copier as sole runtime dependency, pytest in dev group | static review | Codex
- PASS | uv run newproj --version | AC-2: prints 0.1.0 from installed metadata; single version definition in pyproject.toml | Windows, Python 3.13.5, uv 0.12.24 | Codex
- PASS | uv run newproj --help; uv run pytest | AC-3: new, adopt, doctor listed; each stub prints not implemented and exits 2 | Windows, Python 3.13.5 | Codex
- PASS | uv sync; uv run pytest | AC-4: 10 tests pass, invoking installed console script from outside repository | Windows, Python 3.13.5 | Codex
- PASS | uv sync --locked --python 3.11; uv run pytest | AC-4: 10 tests pass on minimum supported Python | Windows, Python 3.11.17 | Codex
- PASS | .github/workflows/ci.yml review | AC-5 configuration: push and pull_request, all three required OS runners, official setup-uv action, locked sync | static review; hosted execution pending | Codex
- PASS | uv lock --check | AC-6: uv.lock generated and current, ready for commit | Windows, uv 0.12.24 | Codex
- PASS | uv build | source distribution and wheel build successfully | Windows, Python 3.13.5 | Codex
- PASS | git diff --check | no whitespace errors | Windows | Codex

## Review

Outcome: implementation reviewed; hosted CI pending.

- Reviewed source, tests, package configuration, CI workflow, and lockfile.
- No edits to TASK.md, docs/spec.md, copier.yml, template/, or accepted decision entries. D-005 is appended.
- Lockfile uses public PyPI sources and contains no personal paths.
- Cross-platform execution will be verified by GitHub Actions; it is not assumed from local Windows tests.

## Exact next steps

1. Commit and push M1 changes.
2. Open pull request to main.
3. Confirm all three CI jobs pass and record the pull request and results here.

## Blockers / open questions

None.

## Relevant decisions

- D-002
- D-003
- D-005
