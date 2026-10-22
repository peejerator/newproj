# Handoff

Last updated: 2026-10-21 by Claude Code/claude-opus-5-5
Branch: m6-adopt
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: `newproj adopt [path]` with `--name` and hidden `--template-path` (`src/newproj/adopt.py`); rendering shared with `new` in `source.render`; help documents it.
- AC-2: plain folder prompts `Run git init -b main? [y/N]` on a terminal; otherwise exit 2 with the command and nothing written.
- AC-3: dirty tree (untracked included, ignored excluded), invalid name, and differing template-owned paths exit 2 before writing, listing the paths; identical template-owned paths are reported as preserved.
- AC-4: project-owned files preserved byte for byte; review flags for `AGENTS.md`, `CLAUDE.md` without imports, non-neutral `TASK.md`/`HANDOFF.md`; file table and bootstrap instructions printed.
- AC-5: `.gitignore` marked block, `.editorconfig` diff report, `.gitattributes` never modified, renormalization report with `git add --renormalize .`.
- AC-6: `set-head` when `origin/HEAD` is missing; default branch reported; answers file records the URL; never stages or commits; exit 0/1/2.
- AC-7: adopting a repository without `AGENTS.md`, committing, then `newproj doctor` gives 0 FAIL.
- AC-8: protocol and handoff step 5 name the `AGENTS.md` locations first; protocol is 114 lines.
- AC-9: bootstrap skill steps 3 to 5 and 10 cover mapping, terminology, required files, and hygiene reports; pointers unchanged.
- AC-10: `bootstrap/references/DECISIONS.md` added, byte-identity tested.
- AC-11: ERRATA E-020 appended. Also added DECISIONS D-006 for adopt choices beyond the interview (see blockers).
- AC-12: `tests/test_adopt.py` (31 tests) and content tests added; 400 tests pass locally.
- AC-13: `AGENTS.md` Commands lists `uv run newproj adopt`.
- AC-14: recorded below under Blockers / open questions (start-task first use).

## Current working area

- `src/newproj/adopt.py`, `src/newproj/source.py`, `src/newproj/new.py`, `src/newproj/cli.py`, `src/newproj/doctor.py`
- `template/docs/AGENT_PROTOCOL.md`, `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/bootstrap/`
- `docs/ERRATA.md`, `docs/DECISIONS.md`, `AGENTS.md`, `README.md`
- `tests/test_adopt.py`, `tests/test_agent_content.py`, `tests/test_cli.py`, `tests/test_new.py`, `tests/test_render.py`, `tests/conftest.py`

## Validation

- PASS | uv run pytest | 400 passed; AC-1 to AC-10, AC-12, AC-13; one expected Copier dirty-template warning | Linux, Python 3.13, Git 2.47.3, Copier 9.18.2, working tree | implementer
- PASS | newproj adopt --template-path <repo> on a scratch repository (README, src/app.py), commit, newproj doctor | adopt exit 0, nothing staged; doctor 19 PASS, 1 WARN (core.hooksPath not set, as adopt's next steps say), 0 FAIL; AC-6, AC-7 | scratch directory, Linux | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | implementer
- PASS | git diff --check, ruff --select F, full diff inspection | no whitespace errors, unused names, or unintended changes; spec, TASK.md, accepted entries unchanged | working tree | implementer
- NOT RUN | CI on Linux, macOS, and Windows | requires the user to commit and push; AC-12 pending | working tree | implementer
- NOT RUN | independent review | expected for this task; requires committed work and a different agent | working tree | implementer

## Review

Outcome: none

## Exact next steps

1. The user commits and pushes, and opens the pull request; confirm CI passes on all three operating systems (AC-12).
2. Run the `review` skill in a different agent against the committed work.

## Blockers / open questions

- For review, choices made beyond the interview decisions (recorded in DECISIONS D-006): adopt also refuses a subdirectory of a repository and a repository that already has `.copier-answers.yml`; the "required `.gitignore` entries" are the four rules spec 18.3 labels required (`.env`, `.env.*`, `!.env.example`, `context.md`), not the OS and editor snippets; `.editorconfig` differences and created files that the project ignores count as review items (exit 1); adopt prints, but does not run, `git config core.hooksPath .githooks`.
- AC-14, first real use of `start-task`: it ran 2026-10-20 to 2026-10-21 with two question rounds plus final confirmation. Friction: Round 1 question 3 proposed the durable-documents wording without explaining how relocated documents are found, so the user asked, and the mechanism and four follow-up decisions moved to Round 2. Preflight and branch creation ran without problems.

## Relevant decisions

- ERRATA E-002, E-007, E-008, E-018, E-019, E-020; DECISIONS D-002, D-006.
