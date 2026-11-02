# Handoff

Last updated: 2026-11-01 by Claude Code (claude-opus-5-5)
Branch: m7-behavioral-fixtures
Task: standard
Environment: other (Linux)

## Status

complete

## Completed

- AC-1: seven fixtures in `tests/fixtures/behavior/B<n>/` (`prompt.txt`, `notes.md`, `setup.py`, `check.py`); shared planted package in `shared.py`.
- AC-2: `scripts/behavior.py setup`; manifest at `<dir>/../.behavior/<name>/manifest.json`. Commit signing is off for fixture projects only (`GIT_CONFIG_COUNT`), and setup refuses a directory inside another repository.
- AC-3: `scripts/behavior.py check`; scripted conditions as listed; B1 and B10 JUDGE only. Exit 1 on FAIL, 2 on usage error.
- AC-4: `tests/test_behavior.py`; for JUDGE-only B1 and B10 the failing outcome is asserted to stay JUDGE with the change listed, since AC-3 forbids scripted conditions there.
- AC-7, AC-8 (E-021), AC-9 (D-008), AC-10: done.
- AC-6: invocation table filled from B10 (`/<name>` in Claude Code, `$<name>` in Codex, both runs); the categorical override claim replaced with the observed behavior (Claude Code's built-in `/resume` is listed beside the skill, and `/resume` ran the skill in 2.1.310 and 2.1.316); no rename needed. `test_prompts_invoking_skills` asserts the cells.
- AC-5: all 28 runs recorded with OS, tool version, model, date, result, and note, and pass rates filled; judged by the implementer from the session logs, both runs confirmed by the user. FAIL rows: Claude Code B6 runs 1 and 2 and Codex B6 run 2 (#38), Codex B10 runs 1 and 2 (#39). Also filed #40 (`start-task` stops in a project with no remote), seen in B10 on both tools.
- Review P1 (AC-4, AC-11): `scripts/behavior.py` `run()` now passes an empty stdin pipe instead of `DEVNULL`. On Windows `NUL` is a character device that `isatty()` reports as a terminal, so `newproj new` took the interactive path and Copier failed with "No Windows console found" (the CI log has no "stdin is not a terminal" line, confirming it). CI run 40270175589 passed on Linux, macOS, and Windows.

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
- PASS | uv run pytest (after P1 fix) | 443 passed, 1 skipped; Windows not verifiable locally | Linux, Python 3.13 | implementer
- PASS | CI run https://github.com/peejerator/newproj/actions/runs/40270175589 (commit 399c065) | Linux, macOS, and Windows jobs pass; review P1 fixed (AC-4, AC-11) | GitHub Actions | CI
- PASS | 28 user-run sessions, `behavior.py check` on each | every scripted condition passed; judged results as recorded (AC-5) | Linux; Claude Code 2.1.310 and 2.1.316, Codex CLI 0.164.0 and 0.166.0 | implementer
- PASS | uv run pytest (after AC-6 table) | 443 passed, 1 skipped | Linux, Python 3.13.5 | implementer
- NOT RUN | CI for the AC-5 and AC-6 commit | environment: not pushed yet | implementer

- PASS | uv run pytest | 443 passed, 1 skipped; fixture synthetic outcomes and content checks pass (AC-4, AC-7, AC-10, AC-11) | Linux, Python 3.13.5; reviewed HEAD | reviewer
- PASS | uv run python scripts/behavior.py setup <id> <dir>; uv run python scripts/behavior.py check <id> <dir> | all seven fresh temporary projects; external manifests present; untouched B1/B4/B5/B6/B9/B10 JUDGE, B11 FAIL as expected; planted unittest suites and B9 state check pass (AC-1 to AC-3) | Linux; working-tree template identical to HEAD | reviewer
- PASS | inspect result tables, B10 notes, and GitHub issues 33, 38, 39, 40 | 28 unique rows have environment and judged results; five FAIL rows cite issues; pass rates and invocation table match; PR 37 body is Refs #33 (AC-5, AC-6) | committed artifacts and read-only GitHub queries; interactive sessions not rerun | reviewer
- PASS | git diff --check 5eae621961c09a0cb553396a9b15979fcfde36ce...HEAD; inspect complete diff and protected paths | no whitespace errors or em/en dashes added; DECISIONS and ERRATA append only; protected paths, skill names, pointers and frontmatter unchanged (AC-8 to AC-11) | committed base-to-HEAD diff | reviewer
- PASS | CI run https://github.com/peejerator/newproj/actions/runs/41367376699 | Linux, macOS, Windows tests and Python 3.9 state checks pass (AC-4, AC-11) | exact commit 8af9eeffe56c883d29965a2fad93e9b60503f82b | CI
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | Linux; current review record | reviewer

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-11-01
Reviewed at: 8af9eeffe56c883d29965a2fad93e9b60503f82b
Contract: df70f976e25977a07beda8f7de495fddd9303074
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | All seven directories contain the exact prompt, setup, check and session notes; complete fixture content inspected and planted states confirmed by reviewer dry runs.
- AC-2: VERIFIED | Reviewer CLI setup runs create all seven projects through newproj new with --no-remote and the repository template, make baseline commits and external hash/HEAD/status manifests, and retain B9/B11 dirty changes; pytest checks the manifest fields.
- AC-3: VERIFIED | Complete runner and checks inspected; reviewer pytest exercises every scripted condition, JUDGE-only B1/B10, change reporting and exit codes. Fresh CLI checks produce the expected initial verdicts.
- AC-4: VERIFIED | Harness and fixtures use standard-library code plus newproj; reviewer synthetic-outcome tests pass locally, and CI run 41367376699 passes on Linux, macOS and Windows at the reviewed commit. Empty stdin pipe fixes the earlier Windows setup failure.
- AC-5: VERIFIED | Committed results contain all 28 unique fixture/run/tool combinations, each with OS, version, model, date, judged PASS/FAIL and note. All five FAIL rows cite #38 or #39; pass rates match and E-021 is cited. This verifies the required records; interactive sessions were user-run and were not rerun by the reviewer.
- AC-6: VERIFIED | All six Claude Code and Codex invocation cells match the recorded B10 observations; Copilot and Antigravity are marked not tested. Fallback and plain-language forms are present, with observed Claude Code /resume behavior and Codex /review distinguished; issue #33 supports the latter claim.
- AC-7: VERIFIED | Recommendations and the start-task prompt both require mechanism explanations in the question; the corresponding content test passes in reviewer pytest.
- AC-8: VERIFIED | E-021 is appended at EOF, permits Codex CLI Phase 1 runs and defers extension/desktop runs; earlier errata bytes are unchanged.
- AC-9: VERIFIED | D-008 is appended at EOF and records layout, runner commands, external manifest, verdicts and user-run interactive sessions; earlier decision bytes are unchanged.
- AC-10: VERIFIED | AGENTS.md Commands lists setup and check; its content test passes.
- AC-11: VERIFIED | Reviewer pytest passes with 443 passed and 1 skipped; exact-commit CI passes on all three platforms. Added prose has no em/en dashes; skill names, root pointers and pointer frontmatter are unchanged.

Findings:
- No blocking findings. The earlier Windows setup, pending-results and pending-invocation findings are resolved at the reviewed HEAD.
- M7 requires recorded results rather than universal behavioral success. Recorded B6 and B10 failures remain tracked by #38 and #39 for later work; the local-only start-task limitation is tracked by #40. None requires a skill rename.
- Acceptance criteria were user-confirmed on 2026-10-24. This review is a separate session and model from the reported implementer, Claude Code (claude-opus-5-5).
- Earlier implementer NOT RUN entries predate the completed records and CI; current reviewer and exact-commit CI entries above establish the reviewed state. No source code, task requirements or other handoff sections were changed.

## Exact next steps

1. User commits and pushes; confirm CI passes on all three operating systems.
2. Independent review with the `review` skill in a different agent or model (instruction content changed).
3. Not in M7 scope, for a later issue: `newproj new` itself has the same latent bug when stdin is redirected from `NUL` on Windows (`source.render` uses `sys.stdin.isatty()`).

## Blockers / open questions

- The B10 results observed `$review` running the skill in Codex; the statement in `PROMPTS.md` that Codex's `/review` is its own command comes from issue #33, not from B10.

## Relevant decisions

- D-002, D-008; ERRATA E-002, E-014, E-018, E-021
