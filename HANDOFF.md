# Handoff

Last updated: 2026-10-19 by Claude Code (claude-opus-5-5)
Branch: m4-core-library
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: `src/newproj/state.py` (stdlib only, 3.9 syntax); byte-identical template copy; `uv run python scripts/sync_state.py` copies it and is documented in `AGENTS.md`.
- AC-2: default branch resolved by spec 4 steps 1 to 4, reporting the step; `ls-remote` has a 10 s timeout; step 2 and offline step 3 print the `set-head` hint; step 4 is reported as unknown with the fix.
- AC-3: heading-based parsers for both files; report missing, renamed, and duplicate headings and header lines, invalid values, and validation provenance; never raise (fuzzed in tests).
- AC-4: report covers the 17.2 list in the three 13.1 groups; neutral report, neutral-file mismatch, review validity per 13.6.
- AC-5: `state.py check` exits 0 or 1, printing `file:line: message` sorted by file and line.
- AC-6: `--neutral-dir`, default `.agents/skills/handoff/neutral/`; `AGENTS.md` gives the report and check commands for this repository.
- AC-7: `handoff` (step 8), `review` (step 12), and `accept` (step 4) run `state.py check` with a manual fallback; `resume` was already as spec 17.2 and is unchanged.
- AC-8: `tests/test_state.py` (61 tests) against temporary repositories and a local bare remote; every run asserts the repository is unchanged. CI step runs both commands under Python 3.9.

## Current working area

- `src/newproj/state.py`
- `template/.agents/skills/`
- `tests/test_state.py`
- `tests/test_render.py`
- `scripts/sync_state.py`
- `.github/workflows/ci.yml`
- `AGENTS.md`
- `HANDOFF.md`

## Validation

- PASS | `uv run pytest` | 202 passed, covers AC-1 to AC-8 | Linux aarch64, Python 3.13.5, Git 2.47.3 | implementer
- PASS | `git diff --check` | no output | Linux | implementer
- PASS | `uv run --no-project --python 3.9 template/.agents/skills/resume/scripts/state.py [check] --neutral-dir template/.agents/skills/handoff/neutral` | report printed; check: No violations found, exit 0 (AC-1, AC-6) | Linux, Python 3.9.25 | implementer
- PASS | `state.py` and `state.py check` in a scratch project rendered from the template | neutral report and check exit 0; after setting `Status: active` by hand, check exit 1 with 3 violations | Linux, Python 3.9.25 and 3.13.5 | implementer
- NOT RUN | CI on Linux, macOS, and Windows, plus the Python 3.9 step | environment: runs after the user commits and pushes | | implementer

## Review

Outcome: none

## Exact next steps

1. Commit with the printed commands, push `m4-core-library`, and open the PR to `main`.
2. Confirm CI passes on all three operating systems, including the Python 3.9 step; record it here with `CI` provenance and set `## Status` to `complete`.
3. Run the `review` skill in a different agent or model.

## Blockers / open questions

- Scope disclosure: `tests/test_render.py` is not in the task's file list but had to change, because M3's layout test asserted that no `state.py` is rendered, which AC-1 now requires. Only the expected layout and that assertion changed.
- Scope disclosure: `check` also reports unexpected and duplicate headings or header lines, text before the title, and an active task without a Goal or an `AC-` criterion (spec 12.3). These go beyond the AC-5 list, but follow from the cited sections.
- Unverified on macOS and Windows until CI runs: path display relative to the repository root, and the `ls-remote` timeout behavior on a hanging remote (only an unreachable local path is tested).
- The CI step runs `git fetch --unshallow` so `check` can resolve `Base commit` in the shallow checkout.

## Relevant decisions

- D-002
- E-007
- E-012
