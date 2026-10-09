# Handoff

Last updated: 2026-10-09 by Codex (M1 implementation)
Branch: m1-skeleton
Task: standard

## Status

complete

## Completed

- M1 src-layout package, argparse console script, installed-script tests, CI matrix, and uv.lock implemented.
- Version is defined only in pyproject.toml and read from installed package metadata.
- D-005 records the user-approved build-only uv_build dependency.
- Existing AGENTS.md commands remain correct.

## Current working area

- Pull request: https://github.com/peejerator/newproj/pull/1
- Implementation commit: ed9e62f. Subsequent handoff updates only record validation.

## Validation

- PASS | pyproject.toml and source review | AC-1: src layout, Python >=3.11, console script, Copier as sole runtime dependency, pytest in dev group | static review | implementer
- PASS | uv run newproj --version | AC-2: prints 0.1.0 from installed metadata; single version definition in pyproject.toml | Windows, Python 3.13.5, uv 0.12.24 | implementer
- PASS | uv run newproj --help; uv run pytest | AC-3: new, adopt, doctor listed; each stub prints not implemented and exits 2 | Windows, Python 3.13.5 | implementer
- PASS | uv sync; uv run pytest | AC-4: 10 tests pass, invoking installed console script from outside repository | Windows, Python 3.13.5 | implementer
- PASS | uv sync --locked --python 3.11; uv run pytest | AC-4: 10 tests pass on minimum supported Python | Windows, Python 3.11.17 | implementer
- PASS | .github/workflows/ci.yml review | AC-5 configuration: push and pull_request, all three required OS runners, official setup-uv action, locked sync | static review; hosted execution also passed | implementer
- PASS | uv lock --check | AC-6: uv.lock committed and current | Windows, uv 0.12.24 | implementer
- PASS | uv build | source distribution and wheel build successfully | Windows, Python 3.13.5 | implementer
- PASS | git diff --check; git diff --cached --check | no whitespace errors or unintended changes | Windows | implementer
- PASS | gh pr checks 1 --repo peejerator/newproj | AC-5: all six push and pull-request matrix checks pass on implementation commit ed9e62f | GitHub Actions, ubuntu-latest/macOS-latest/windows-latest, Python 3.11 | CI
- PASS | gh run view 37947329865 --repo peejerator/newproj | PR CI run completed successfully on all three operating systems: https://github.com/peejerator/newproj/actions/runs/37947329865 | GitHub Actions | CI

## Review

Outcome: PASS
Reviewer: Claude (claude-opus-5-5), 2026-10-09
Reviewed at: f0abbe35a4931cde06215d15c1678ce3216081b9
Contract: 3df01433396ef5c7bb2746b6e8071a60d4152c60
Working tree clean at review: yes
Baseline: default-branch diff
Artifact coverage: complete
Validation provenance: reviewer-executed; CI-confirmed

- AC-1: VERIFIED | pyproject.toml inspected: src layout, Python >=3.11, console script, sole runtime dependency copier>=9.18.2,<10, pytest in dev group
- AC-2: VERIFIED | newproj --version prints 0.1.0 from package metadata; version defined only in pyproject.toml (reviewer run, Linux, Python 3.11)
- AC-3: VERIFIED | help lists new, adopt, doctor; doctor prints stub message and exits 2 (reviewer run)
- AC-4: VERIFIED | uv run pytest: 10 passed via the installed console script (reviewer run, Linux, Python 3.11)
- AC-5: VERIFIED | workflow inspected; run 37947329865 succeeded on ubuntu, macOS, Windows for ed9e62f; later commit changes HANDOFF.md only (CI)
- AC-6: VERIFIED | uv.lock committed; uv lock --check passes; no personal paths (reviewer run)

Findings (non-blocking):
- Implementer-written review replaced; M2 protocol must state that only an independent reviewer writes this section.
- actions/checkout@v4 runs on deprecated Node.js 20; bump to @v5 in the M2 PR.

## Exact next steps

1. Review and merge PR #1 when approved.
2. After merge, write the M2 TASK.md per docs/ROADMAP.md.

## Blockers / open questions

None.

## Relevant decisions

- D-002
- D-003
- D-005
