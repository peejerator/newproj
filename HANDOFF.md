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
- AC-5: `docs/research/behavioral-fixtures.md` written with 28 `pending` rows.

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

## Review

Outcome: none

## Exact next steps

1. User commits this work and pushes; confirm CI passes on all three operating systems (AC-4).
2. User runs the 28 sessions per `docs/research/behavioral-fixtures.md` Method and reports each `check` output and judgment; record them in that document and the pass-rate table (AC-5).
3. For each FAIL, draft issue text; the user files it or authorizes `gh issue create`; cite the number in the row.
4. Fill the Claude Code and Codex cells of the `PROMPTS.md` invocation table from B10, and the plain-language note for any overridden skill (AC-6). A needed rename is a blocker: record it and ask.
5. Mark complete; independent review (instruction content changed).

## Blockers / open questions

- None.

## Relevant decisions

- D-002, D-008; ERRATA E-002, E-014, E-018, E-021
