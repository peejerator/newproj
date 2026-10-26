# Handoff

Last updated: 2026-10-24 by Claude Code (claude-opus-5-5)
Branch: m7-behavioral-fixtures
Task: standard
Environment: other (Linux)

## Status

in progress

## Completed

- AC-1: seven fixtures in `tests/fixtures/behavior/B<n>/` (`prompt.txt`, `notes.md`, `setup.py`, `check.py`); shared planted package in `shared.py`.
- AC-2: `scripts/behavior.py setup`; manifest at `<dir>/../.behavior/<name>/manifest.json`. Commit signing is off for fixture projects only (`GIT_CONFIG_COUNT`), and setup refuses a directory inside another repository.
- AC-3: `scripts/behavior.py check`; scripted conditions as listed; B1 and B10 JUDGE only. Exit 1 on FAIL, 2 on usage error.
- AC-4: `tests/test_behavior.py`; for JUDGE-only B1 and B10 the failing outcome is asserted to stay JUDGE with the change listed, since AC-3 forbids scripted conditions there.
- AC-7, AC-8 (E-021), AC-9 (D-008), AC-10: done.
- AC-6: section, Copilot and Antigravity rows, fallback, and plain-language form written; Claude Code and Codex cells read `pending B10`.
- AC-5: `docs/research/behavioral-fixtures.md` written with 28 rows. Run 1 recorded for 13 of 14 fixture and tool pairs (2026-10-24 to 2026-10-26, judged by the implementer from the user's transcripts in `~/behavior-runs/transcripts/`, confirmed by the user): FAIL Claude Code B6 (#38), Codex B10 (#39); the rest PASS. Claude Code B10 run 1 pending the user's judgment. Also filed #40 (`start-task` stops in a project with no remote), seen in B10 on both tools. Run 2 not started.
- Review P1 (AC-4, AC-11): `scripts/behavior.py` `run()` now passes an empty stdin pipe instead of `DEVNULL`. On Windows `NUL` is a character device that `isatty()` reports as a terminal, so `newproj new` took the interactive path and Copier failed with "No Windows console found" (the CI log has no "stdin is not a terminal" line, confirming it). Awaiting a Windows CI run.

## Current working area

- `scripts/behavior.py`, `tests/fixtures/behavior/`, `tests/test_behavior.py`, `tests/test_agent_content.py`
- `template/docs/PROMPTS.md`, `template/.agents/skills/start-task/references/interview.md`
- `docs/research/behavioral-fixtures.md`, `docs/ERRATA.md`, `docs/DECISIONS.md`, `AGENTS.md`, `HANDOFF.md`

## Validation

- PASS | uv run pytest | 443 passed, 1 skipped; covers AC-4, AC-7, AC-10, AC-11 locally | Linux, Python 3.13 | implementer
- PASS | dry run: behavior.py setup and check for all seven fixtures | B1 to B10 JUDGE, B11 FAIL (neutral files) on the untouched state, as designed; planted tests pass; B9 `state.py check` clean | Linux | implementer
- PASS | grep for em and en dashes in added prose | none | Linux | implementer
- NOT RUN | CI on Linux, macOS, Windows | environment: not pushed yet | implementer
- NOT RUN | 28 agent sessions (AC-5) | user-run by design (TASK.md Scope) | implementer
- PASS | uv run pytest | 443 passed, 1 skipped; includes all fixture synthetic outcomes and AC-7 content checks | Linux, Python 3.13.5 | reviewer
- PASS | uv run python scripts/behavior.py setup <id> <dir>; uv run python scripts/behavior.py check <id> <dir> | all seven fresh temporary projects; untouched B1, B4, B5, B6, B9, B10 JUDGE and B11 FAIL as expected; planted unittest suites pass; B9 state check clean (AC-1 to AC-3) | Linux, working-tree template | reviewer
- FAIL | Inspect CI run https://github.com/peejerator/newproj/actions/runs/40157888861 | Linux and macOS pass; Windows has 418 passed, 26 setup errors: copier reports No Windows console found (AC-4, AC-11) | PR #37 merge 37b2281486e483cd927631846ca4ec5d690a654b of reviewed HEAD into task base; not a direct HEAD run | reviewer
- PASS | git diff --check 5eae621...HEAD; inspect added prose and protected paths | no whitespace errors or em/en dashes added; protected files and skill names unchanged; DECISIONS and ERRATA append only (AC-8 to AC-11) | committed diff | reviewer
- NOT RUN | 28 interactive agent sessions (AC-5) | skipped: TASK.md reserves these runs for the user; all 28 committed result rows remain pending | reviewer
- PASS | uv run pytest (after P1 fix) | 443 passed, 1 skipped; Windows not verifiable locally | Linux, Python 3.13 | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | Linux | reviewer

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-10-24
Reviewed at: 05672f3ad780ae2047dabe9fcc618cb242e68227
Contract: df70f976e25977a07beda8f7de495fddd9303074
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | All seven fixture directories contain the four required files; complete setup and notes inspected; reviewer setup dry runs confirm the planted states.
- AC-2: VERIFIED | All seven Linux CLI setup dry runs create projects through newproj new, baseline commits and external manifests; pytest verifies manifest hashes, HEAD, status and B9/B11 dirty state. Windows failure is recorded under AC-4.
- AC-3: VERIFIED | Complete runner and fixture checks inspected; reviewer pytest exercises passing/failing scripted conditions, JUDGE-only B1/B10, change reporting and exit codes; fresh CLI checks produce expected verdicts on Linux.
- AC-4: UNSATISFIED | Standard-library harness and synthetic tests exist, but Windows CI fixture setup fails with No Windows console found; 26 errors. Linux/macOS CI pass.
- AC-5: UNSATISFIED | docs/research/behavioral-fixtures.md:21-53 contains 28 pending rows with no recorded environments, judgments, results or failure issues; pass rates remain pending. E-021 is cited.
- AC-6: UNSATISFIED | template/docs/PROMPTS.md:76-81 contains pending B10 for all twelve tested-tool cells. Untested tools, fallback and generic plain-language form exist; observed invocations and override-specific forms are missing.
- AC-7: VERIFIED | Matching mechanism-explanation rule added to Recommendations and the start-task prompt; test_recommendations_explain_mechanisms passes in reviewer pytest.
- AC-8: VERIFIED | E-021 is appended at EOF and permits Codex CLI Phase 1 runs while deferring extension/desktop runs; prior entries unchanged.
- AC-9: VERIFIED | D-008 is appended at EOF and records layout, commands, external manifest, verdicts and user-run interactive sessions; prior entries unchanged.
- AC-10: VERIFIED | AGENTS.md Commands lists both runner commands; content test passes.
- AC-11: UNSATISFIED | Reviewer Linux pytest passes (443 passed, 1 skipped), prose hygiene and protected skill checks pass, but the Windows test suite fails in the added harness tests.

Findings:
- [P1] Make fixture setup work with redirected streams on Windows (scripts/behavior.py:55-57,186-187). The new subprocess wrapper captures stdout/stderr and supplies DEVNULL stdin; the child newproj/Copier call fails with No Windows console found. CI run 40157888861, Windows job 121063073191, reports 26 setup errors before fixtures can run. Make child rendering work without console handles and obtain passing CI on all three operating systems. CI checked PR merge 37b2281486e483cd927631846ca4ec5d690a654b of reviewed HEAD into the recorded base, rather than HEAD directly.
- [P2] Record the 28 user-run sessions before claiming M7 complete (docs/research/behavioral-fixtures.md:21-53). Fill each environment, judged result and note, cite a GitHub issue for each FAIL, and calculate pass rates. These are intentionally user-run sessions, not evidence the reviewer can replace with synthetic checks. The handoff correctly reports in progress.
- [P2] Finish invocation documentation from B10 (template/docs/PROMPTS.md:76-83). Replace pending cells with observed invocations and document each overridden skill's working plain-language form. The categorical claim that a same-named built-in always wins is unsupported: issue #33 reports Claude Code /resume invoking the skill in a prior trial and asks whether precedence is reliable. Describe the observed tool/version behavior instead of assuming precedence from matching names; raise any needed rename as a blocker.
- Acceptance criteria were user-confirmed on 2026-10-24. This review is a separate session and model from the reported implementer, Claude Code (claude-opus-5-5).
- The implementer's NOT RUN CI entry predates the push; the reviewer CI inspection above records the current observed result. No source code or task requirements were changed during review.

## Exact next steps

1. User commits the P1 fix and pushes; confirm CI passes on Linux, macOS, and Windows (AC-4, AC-11).
2. User runs the remaining run-2 sessions (14) per `docs/research/behavioral-fixtures.md` Method and reports each `check` output and judgment; record them in that document and the pass-rate table (AC-5, review P2).
3. For each FAIL, draft issue text; the user files it or authorizes `gh issue create`; cite the number in the row.
4. Fill the Claude Code and Codex cells of the `PROMPTS.md` invocation table from B10, and replace the categorical "a same-named built-in always wins" claim with the observed per-tool, per-version behavior (review P2; issue #33 reports Claude Code `/resume` invoking the skill once). A needed rename is a blocker: record it and ask.
5. Mark complete; independent review (instruction content changed).
6. Not in M7 scope, for a later issue: `newproj new` itself has the same latent bug when stdin is redirected from `NUL` on Windows (`source.render` uses `sys.stdin.isatty()`).

## Blockers / open questions

- None.

## Relevant decisions

- D-002, D-008; ERRATA E-002, E-014, E-018, E-021
