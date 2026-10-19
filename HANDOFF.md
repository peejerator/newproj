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
- PASS | `uv run pytest` | 202 passed, including 61 state tests covering AC-1 to AC-8 | Linux aarch64, Python 3.13.5 | reviewer
- PASS | `git diff --check` and `git diff --check 43bdd59e028830242971b5d06988f7ef546e96bf...HEAD` | no whitespace errors in the working tree or committed changes | Linux | reviewer
- PASS | `uv run --no-project --python 3.9 template/.agents/skills/resume/scripts/state.py --neutral-dir template/.agents/skills/handoff/neutral` | active report printed all signal groups, base ancestry, and clean format results (AC-1, AC-4, AC-6) | Linux, Python 3.9.25 | reviewer
- PASS | `uv run --no-project --python 3.9 template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral` | no violations, exit 0 (AC-1, AC-5, AC-6); rerun after recording review | Linux, Python 3.9.25 | reviewer
- PASS | Rendered-project report/check smoke check | neutral and active reports/checks exit 0; empty active base exits 1 with file and line; rendered script byte-identical; file snapshots including .git unchanged after all five invocations (AC-1, AC-4, AC-5, AC-6) | scratch Copier render, Linux, Python 3.13.5, isolated Git configuration | reviewer
- PASS | CI tests and Python 3.9 report/check | all three OS jobs and their test and Python 3.9 steps passed at reviewed commit 8d7291ff7b8a84abc2ce0974237f2364d951dc87 (AC-8); https://github.com/peejerator/newproj/actions/runs/39313582759 | ubuntu-latest, macos-latest, windows-latest | CI

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-10-19
Reviewed at: 8d7291ff7b8a84abc2ce0974237f2364d951dc87
Contract: d82e78de091d9f014e7f77793d4e6f47dfa37534
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | standard-library imports inspected; actual Python 3.9 execution; byte identity and copy-command tests pass; rendered copy also compared byte for byte.
- AC-2: VERIFIED | resolver inspected against spec 4; local-bare-remote tests exercise steps 1 and 2, configured/main/master fallback and unknown default; timeout and read-only set-head hints present.
- AC-3: VERIFIED | complete heading parsers inspected; missing/renamed headings and headers, invalid values, validation provenance, fenced headings, and malformed-input tests pass.
- AC-4: VERIFIED | report and recovery code inspected; neutral/mismatch, stale plus dirty, never committed, branch/working-area mismatch, base ancestry, and current/historical review tests pass; reports run independently.
- AC-5: VERIFIED | clean, malformed, invalid-base and neutral-byte checks pass with file/line diagnostics; independently observed exits 0 and 1 in a rendered project.
- AC-6: VERIFIED | default and explicit neutral-directory tests pass; repository commands inspected and executed; rendered project uses its default neutral directory.
- AC-7: VERIFIED | complete skills and their added lines inspected; handoff/review/accept invoke check with Python and manual fallbacks; unchanged resume invocation matches spec 17.2; skill tests pass.
- AC-8: VERIFIED | all 61 state tests pass within the 202-test suite; synthetic repositories, local bare remote and unchanged snapshots inspected; exact-commit CI confirms all three operating systems and Python 3.9 steps.

Findings:
- No blocking defects found. The tests/test_render.py scope adjustment replaces the obsolete assertion that state.py is absent, as required by AC-1.
- The implementer wrote the acceptance criteria for this standard task, so the evidence is weaker than for user-confirmed criteria. This review used a separate session and model family from the recorded Claude implementer.

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
