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
- PASS | CI tests on Linux, macOS, and Windows | all three jobs passed on the reviewed commit; AC-12 | https://github.com/peejerator/newproj/actions/runs/39708783971 | CI
- PASS | uv run pytest after the F1 to F3 fixes | 409 passed, 1 skipped (Windows junction test), one expected Copier dirty-template warning; new regressions for directory links, dangling links, `.gitignore` link, file link preserved, directories in place of `.gitignore` and `AGENTS.md`, narrow and blanket LF rules; AC-3 to AC-5, AC-12 | Linux, Python 3.13.5, Copier 9.18.2, working tree | implementer
- PASS | ruff --select F, git diff --check, state.py check after the fixes | no findings, no whitespace errors, no violations | working tree | implementer
- NOT RUN | CI on Linux, macOS, and Windows for the fixes | requires the user to commit and push; symlink and junction tests are first exercised on macOS and Windows there | working tree | implementer
- PASS | uv run pytest | 409 passed, 1 skipped (Windows junction), one expected Copier warning; AC-1 to AC-10, AC-12, AC-13; previous F1 to F3 CLI regressions pass | Linux, Python 3.13.5, Copier 9.18.2, reviewed HEAD | reviewer
- PASS | uv run python /tmp/newproj_review_m6.py: scratch CLI adoption, commit, doctor | adopt exit 0, nothing staged; committed synthetic adoption gives doctor exit 0, 19 PASS, 1 WARN, 0 FAIL; AC-6, AC-7 | isolated fixtures and fake gh, Linux | reviewer
- FAIL | uv run python /tmp/newproj_review_m6.py: bootstrap step 10 LF probe | txt-only attributes satisfy the prescribed probe.txt check while src/app.py has unspecified text/eol; CLI multi-path check correctly rejects the same rule; AC-9, F4 | synthetic committed repository, Linux | reviewer
- PASS | uv run python /tmp/newproj_review_m6.py: additional preflight probes | AGENTS.md directory and docs regular-file parent rejected without writes; AC-3, AC-4 | synthetic committed repositories, Linux | reviewer
- PASS | git diff --check 07a8bebfa71b4283689c150452a00421fd8ae035...HEAD and complete diff inspection | no whitespace errors; frozen spec and existing decision/errata entries unchanged; doctor change only extracts the same ignore check into a helper | base-commit diff, reviewed HEAD | reviewer
- PASS | gh pr view --json headRefOid,statusCheckRollup | exact reviewed HEAD matches PR 36; Linux and macOS jobs passed; Windows jobs still running | https://github.com/peejerator/newproj/actions/runs/39713993482 and https://github.com/peejerator/newproj/actions/runs/39713986690 | reviewer
- NOT RUN | completed Windows CI verification for reviewed HEAD | environment: exact-commit Windows jobs still in progress; AC-12 remains unverified | PR 36, reviewed HEAD | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found, including the completed review record | repository root | reviewer

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-10-21
Reviewed at: b818487ca2efb3fdbd64d21b752367ba583f89be
Contract: 41d16049f23f8e26ddcee34021daea37ceee6f39
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Complete CLI wiring and help inspected; default current directory, name override, and hidden development option tests pass.
- AC-2: VERIFIED | Terminal yes/no initialization and nonterminal refusal tests pass; no initialization without consent.
- AC-3: VERIFIED | Dirty/staged/untracked, invalid-name, differing template-file, identical-file, link, and non-file preflight tests pass; additional file-parent probe writes nothing.
- AC-4: VERIFIED | Project-file byte preservation, required-file creation, review flags, classification table, and bootstrap instructions inspected and tested; F1 and F2 destination gaps fixed.
- AC-5: VERIFIED | Hygiene preservation, marked ignore append, editorconfig differences, renormalization report, and narrow/general LF-rule tests pass; F3 fixed in the CLI.
- AC-6: VERIFIED | Remote HEAD resolution, default branch report, URL answers for tagged source, exit 0/1/2, and no staging/commits inspected and tested; local development source is the E-002 exception.
- AC-7: VERIFIED | Reviewer ran scratch CLI adoption without AGENTS.md, committed the synthetic result, and ran doctor: exit 0 and 0 FAIL.
- AC-8: VERIFIED | Added protocol/handoff lines preserve durable-findings guidance and allow AGENTS.md mappings; complete template content checks pass; protocol is 114 lines.
- AC-9: UNSATISFIED | Mapping, terminology, required-file creation, approval rules, fixed decisions/ADRs, and pointer frontmatter inspected and tested; bootstrap's single txt LF probe misses a missing general LF rule (F4).
- AC-10: VERIFIED | Decisions reference is byte-identical to template/docs/DECISIONS.md; identity test passes.
- AC-11: VERIFIED | E-020 appends amendments to 11.9, 15.3, and 17.4; complete diff leaves existing ERRATA entries unchanged.
- AC-12: NOT CHECKED | Adoption/content coverage and all 409 local tests pass; exact-commit Linux/macOS CI passed, but Windows jobs remain in progress, so the full CI requirement is not yet verified.
- AC-13: VERIFIED | AGENTS.md Commands documents adopt; content test passes.
- AC-14: VERIFIED | Committed Blockers section records first start-task use on 2026-10-20 to 2026-10-21, two rounds plus confirmation, and the wording friction.

Findings:
- F4 [P2]: Check general LF coverage in bootstrap, too (template/.agents/skills/bootstrap/SKILL.md:50). Step 10 prescribes only `git check-attr text eol -- probe.txt`. In a committed scratch repository with `.gitattributes` containing only `*.txt text=auto eol=lf`, that command gives the expected auto/lf output while `src/app.py` has both attributes unspecified. Manual bootstrap following this recipe misses the missing general LF rule required by AC-9(d); the CLI now detects the same case correctly. Expand the skill's check to representative paths covering more than .txt, preserve its report-only behavior, and guard the recipe with a regression check. Then rerun the content checks and independent review.
- Prior findings F1 to F3 are resolved in the committed CLI fixes: directory links, dangling links, mutable .gitignore links, and non-file destinations fail preflight; a narrow LF rule requires review. Relevant regression tests pass locally.
- Acceptance criteria were user-confirmed on 2026-10-21. This is a fresh Codex/GPT-6 review of work reported as implemented by Claude Code/claude-opus-5-5; the earlier review also used Codex/GPT-6.
- Confirm Windows CI on the reviewed commit before marking AC-12 verified. The older CI entry and implementer NOT RUN entries above describe earlier snapshots; current evidence is in this review's validation entries. Other handoff sections, including Exact next steps, are unchanged under the review skill's write limits.

## Exact next steps

1. The user commits and pushes the F1 to F3 fixes to the open pull request; confirm CI passes on all three operating systems, including the link tests (AC-12).
2. Rerun the `review` skill in a different agent against the committed fixes.

## Blockers / open questions

- For review, choices made beyond the interview decisions (recorded in DECISIONS D-006): adopt also refuses a subdirectory of a repository and a repository that already has `.copier-answers.yml`; the "required `.gitignore` entries" are the four rules spec 18.3 labels required (`.env`, `.env.*`, `!.env.example`, `context.md`), not the OS and editor snippets; `.editorconfig` differences and created files that the project ignores count as review items (exit 1); adopt prints, but does not run, `git config core.hooksPath .githooks`.
- AC-14, first real use of `start-task`: it ran 2026-10-20 to 2026-10-21 with two question rounds plus final confirmation. Friction: Round 1 question 3 proposed the durable-documents wording without explaining how relocated documents are found, so the user asked, and the mechanism and four follow-up decisions moved to Round 2. Preflight and branch creation ran without problems.

## Relevant decisions

- ERRATA E-002, E-007, E-008, E-018, E-019, E-020; DECISIONS D-002, D-006, D-007.
