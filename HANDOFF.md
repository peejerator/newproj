# Handoff

Last updated: 2026-10-09 by Codex (M1 implementation)
Branch: m1-skeleton
Task: standard

## Status

M1 complete. All acceptance criteria verified. PR #1 is open and ready for review.

## Completed

- M1 src-layout package, argparse console script, installed-script tests, CI matrix, and uv.lock implemented.
- Version is defined only in pyproject.toml and read from installed package metadata.
- D-005 records the user-approved build-only uv_build dependency.
- Existing AGENTS.md commands remain correct.

## Current working area

- Pull request: https://github.com/peejerator/newproj/pull/1
- Implementation commit: ed9e62f. Subsequent handoff updates only record validation.

## Validation

- PASS | pyproject.toml and source review | AC-1: src layout, Python >=3.11, console script, Copier as sole runtime dependency, pytest in dev group | static review | Codex
- PASS | uv run newproj --version | AC-2: prints 0.1.0 from installed metadata; single version definition in pyproject.toml | Windows, Python 3.13.5, uv 0.12.24 | Codex
- PASS | uv run newproj --help; uv run pytest | AC-3: new, adopt, doctor listed; each stub prints not implemented and exits 2 | Windows, Python 3.13.5 | Codex
- PASS | uv sync; uv run pytest | AC-4: 10 tests pass, invoking installed console script from outside repository | Windows, Python 3.13.5 | Codex
- PASS | uv sync --locked --python 3.11; uv run pytest | AC-4: 10 tests pass on minimum supported Python | Windows, Python 3.11.17 | Codex
- PASS | .github/workflows/ci.yml review | AC-5 configuration: push and pull_request, all three required OS runners, official setup-uv action, locked sync | static review; hosted execution also passed | Codex
- PASS | uv lock --check | AC-6: uv.lock committed and current | Windows, uv 0.12.24 | Codex
- PASS | uv build | source distribution and wheel build successfully | Windows, Python 3.13.5 | Codex
- PASS | git diff --check; git diff --cached --check | no whitespace errors or unintended changes | Windows | Codex
- PASS | gh pr checks 1 --repo peejerator/newproj | AC-5: all six push and pull-request matrix checks pass on implementation commit ed9e62f | GitHub Actions, ubuntu-latest/macOS-latest/windows-latest, Python 3.11 | Codex
- PASS | gh run view 37947329865 --repo peejerator/newproj | PR CI run completed successfully on all three operating systems: https://github.com/peejerator/newproj/actions/runs/37947329865 | GitHub Actions | Codex

## Review

Outcome: implementation reviewed; local tests, builds, and hosted CI pass.

- Reviewed source, tests, package configuration, CI workflow, and lockfile.
- No edits to TASK.md, docs/spec.md, copier.yml, template/, or accepted decision entries. D-005 is appended.
- Lockfile uses public PyPI sources and contains no personal paths.
- Cross-platform execution verified by GitHub Actions on all three required runners.
- No known blockers or unverified M1 acceptance criteria.

## Exact next steps

1. Review and merge PR #1 when approved.
2. After merge, write the M2 TASK.md per docs/ROADMAP.md.

## Blockers / open questions

None.

## Relevant decisions

- D-002
- D-003
- D-005
