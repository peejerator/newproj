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
- Review FAIL fixes (AC-3, AC-4, AC-5), recorded as DECISIONS D-007:
  - F1: preflight inspects paths without following links (`adopt.kind`, `adopt.blocked`); a symbolic link or junction above a rendered path, a dangling or non-file destination link, and a `.gitignore` link needing entries fail with exit 2 before any write. A link to a file that adopt only reads (for example `CLAUDE.md` to `AGENTS.md`) is preserved.
  - F2: a destination that is a directory or other non-regular entry (for example a `.gitignore/` or `AGENTS.md/` directory) fails preflight with the paths listed.
  - F3: the LF rule check probes four paths (no extension, `.txt`, dotfile, subdirectory with an unknown extension); a narrower rule such as `*.txt text=auto eol=lf` is preserved and reported as "no general LF rule", exit 1.
  - Regression tests added to `tests/test_adopt.py` for each case; symlink tests skip where links cannot be created, and a Windows-only test checks that a junction counts as a link.

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
- PASS | uv run pytest | 400 passed, one expected Copier dirty-template warning; AC-1 to AC-10, AC-12, AC-13 | Linux, Python 3.13.5, Copier 9.18.2, reviewed HEAD | reviewer
- PASS | uv run newproj adopt <scratch> --template-path <fixture-template>, then commit the scratch adoption and uv run newproj doctor <scratch> | adopt exit 0, nothing staged; doctor exit 0, 19 PASS, 1 WARN (hooksPath unset), 0 FAIL; AC-6, AC-7 | synthetic repository and fake gh, Linux | reviewer
- FAIL | scratch adoption path-collision and LF-rule probes | directory links and dangling file links write outside the repository; a .gitignore directory causes partial writes; an AGENTS.md directory remains without the required file; a txt-only LF rule incorrectly passes | synthetic committed fixtures, Linux; F1 to F3 below | reviewer
- PASS | CI tests on Linux, macOS, and Windows | all three jobs passed on the reviewed commit; AC-12 | https://github.com/peejerator/newproj/actions/runs/39708783971 | CI
- PASS | git diff --check 07a8beb...HEAD and complete review diff inspection | no whitespace errors; frozen spec and existing decision/errata entries unchanged; doctor change only extracts an unchanged check into a helper | base-commit diff, reviewed HEAD | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found, including the completed review record | repository root | reviewer
- PASS | uv run pytest after the F1 to F3 fixes | 409 passed, 1 skipped (Windows junction test), one expected Copier dirty-template warning; new regressions for directory links, dangling links, `.gitignore` link, file link preserved, directories in place of `.gitignore` and `AGENTS.md`, narrow and blanket LF rules; AC-3 to AC-5, AC-12 | Linux, Python 3.13.5, Copier 9.18.2, working tree | implementer
- PASS | ruff --select F, git diff --check, state.py check after the fixes | no findings, no whitespace errors, no violations | working tree | implementer
- NOT RUN | CI on Linux, macOS, and Windows for the fixes | requires the user to commit and push; symlink and junction tests are first exercised on macOS and Windows there | working tree | implementer

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-10-21
Reviewed at: 297fd4e5327f6c87db18845b91a681a45bbe2f3c
Contract: 41d16049f23f8e26ddcee34021daea37ceee6f39
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | CLI wiring, default path, name override, and hidden development option inspected; CLI/help and adoption tests pass.
- AC-2: VERIFIED | Plain-folder terminal yes/no and nonterminal refusal tests pass; initialization only follows consent.
- AC-3: VERIFIED | Dirty, staged, untracked, invalid-name, and differing template-owned file tests pass without writes; ignored files and identical template-owned files tested. Additional path-type gaps are blocking findings F1 and F2.
- AC-4: UNSATISFIED | Ordinary project-file preservation, review flags, table, and instructions pass, but an existing AGENTS.md directory is treated as a preserved required file; links can redirect creation outside the repository (F1, F2).
- AC-5: UNSATISFIED | Hygiene preservation, append blocks, and renormalization tests pass, but a txt-only attribute rule suppresses the missing blanket LF-rule report (F3); a .gitignore directory fails after writes (F2).
- AC-6: VERIFIED | Remote HEAD resolution, URL answers for the tagged source, exit statuses, and absence of staging/commits inspected and tested; local development source remains the E-002 exception.
- AC-7: VERIFIED | Reviewer ran CLI adoption on a repository without AGENTS.md, committed only the synthetic result, and ran doctor: 0 FAIL.
- AC-8: VERIFIED | Added protocol/handoff lines retain durable-findings guidance and permit AGENTS.md mappings; template search/content tests pass; protocol is 114 lines.
- AC-9: VERIFIED | Complete bootstrap instructions cover mappings, security assumptions, fixed decisions/ADRs, terminology, missing required files, hygiene reporting, and approval; pointer frontmatter identity tests pass.
- AC-10: VERIFIED | Decisions reference bytes match template/docs/DECISIONS.md; identity test passes.
- AC-11: VERIFIED | E-020 appends amendments to 11.9, 15.3, and 17.4; existing ERRATA entries are unchanged in the complete diff.
- AC-12: VERIFIED | tests/test_adopt.py covers AC-2 through AC-7; content tests cover AC-8 through AC-10; all 400 local tests and exact-commit Linux/macOS/Windows CI jobs pass. Missing regression cases are listed below.
- AC-13: VERIFIED | AGENTS.md Commands documents adopt; content test passes.
- AC-14: VERIFIED | Committed Blockers section records first start-task use on 2026-10-20 to 2026-10-21, two rounds plus confirmation, and the wording friction.

Findings:
- F1 [P1]: Reject or safely contain symlink/junction destinations before any writes (src/newproj/adopt.py:114-120, 174, 259-264). In a clean committed fixture, docs pointing to an empty sibling directory passes preflight and adopt exits 0 after writing AGENT_PROTOCOL.md, DECISIONS.md, and PROMPTS.md outside the repository; Git does not track these created documents. A committed dangling AGENTS.md symlink also passes as absent and creates its external target. The exists/is_dir checks and copy2 follow links. Check destination entries without following links and validate resolved ancestors stay inside the root; include directory-link and dangling-link regressions, with no external writes and no partial adoption.
- F2 [P2]: Preflight destination file types, not only parent types (src/newproj/adopt.py:174-197). A committed .gitignore/keep.txt directory is treated as an appendable .gitignore; adopt copies the answers and agent files before read_bytes raises IsADirectoryError and returns 2. An AGENTS.md/keep.txt directory is reported as preserved/requiring review while the required AGENTS.md file remains absent. Reject unsupported destination types with the offending paths before write(), and test that neither case creates anything.
- F3 [P2]: A single txt probe cannot establish the blanket LF rule (src/newproj/adopt.py:124-131). With only '*.txt text=auto eol=lf' in .gitattributes, adopt exits 0 and reports it preserved without review although 'git check-attr text eol -- src/app.py' reports both attributes unspecified. Preserve the existing file but report that the general rule is missing, returning 1. Add this regression and verify equivalent blanket rules still pass.
- Acceptance criteria were user-confirmed on 2026-10-21. This is a separate Codex/GPT-6 review of work reported as implemented by Claude Code/claude-opus-5-5.
- Rerun the affected checks and independent review after fixes. The implementer NOT RUN entries above describe its earlier snapshot; the reviewer and CI entries record the current evidence.

## Exact next steps

1. The user commits and pushes the F1 to F3 fixes to the open pull request; confirm CI passes on all three operating systems, including the link tests (AC-12).
2. Rerun the `review` skill in a different agent against the committed fixes.

## Blockers / open questions

- For review, choices made beyond the interview decisions (recorded in DECISIONS D-006): adopt also refuses a subdirectory of a repository and a repository that already has `.copier-answers.yml`; the "required `.gitignore` entries" are the four rules spec 18.3 labels required (`.env`, `.env.*`, `!.env.example`, `context.md`), not the OS and editor snippets; `.editorconfig` differences and created files that the project ignores count as review items (exit 1); adopt prints, but does not run, `git config core.hooksPath .githooks`.
- AC-14, first real use of `start-task`: it ran 2026-10-20 to 2026-10-21 with two question rounds plus final confirmation. Friction: Round 1 question 3 proposed the durable-documents wording without explaining how relocated documents are found, so the user asked, and the mechanism and four follow-up decisions moved to Round 2. Preflight and branch creation ran without problems.

## Relevant decisions

- ERRATA E-002, E-007, E-008, E-018, E-019, E-020; DECISIONS D-002, D-006, D-007.
