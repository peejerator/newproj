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
- Follow-up review FAIL fix (AC-9):
  - F4: bootstrap step 10 now probes four paths (`probe probe.txt .probe dir/probe.zzz`), mirroring the CLI, requires `text: auto` or `set` and `eol: lf` for every path, and names `*.txt text=auto eol=lf` as not a general LF rule; still report only. `tests/test_agent_content.py::test_bootstrap_lf_probe_detects_general_rule` extracts the skill's command and runs it against a general rule (passes) and a txt-only rule (detected); it fails against the previous single-probe recipe.

## Current working area

- `src/newproj/adopt.py`, `src/newproj/source.py`, `src/newproj/new.py`, `src/newproj/cli.py`, `src/newproj/doctor.py`
- `template/docs/AGENT_PROTOCOL.md`, `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/bootstrap/` (F4: `SKILL.md` step 10)
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
- PASS | uv run pytest after the F4 fix | 411 passed, 1 skipped (Windows junction), one expected Copier warning; new LF probe regression passes for both rules and fails when run against the previous skill text; AC-9, AC-12 | Linux, Python 3.13.5, Copier 9.18.2, working tree | implementer
- PASS | ruff --select F, git diff --check, state.py check after the F4 fix | no findings, no whitespace errors, no violations | working tree | implementer
- NOT RUN | CI on Linux, macOS, and Windows for the F4 fix, and completed Windows CI for b818487 | requires the user to commit and push; AC-12 | working tree | implementer

- PASS | uv run pytest | 411 passed, 1 skipped (Windows-only junction), one expected Copier warning; AC-1 to AC-10, AC-12, AC-13, including F4's executable LF-recipe regression | Linux, Python 3.13.5, Copier 9.18.2, reviewed HEAD 1e6ca5d | reviewer
- PASS | uv run python /tmp/newproj_m6_review.py | scratch uv run newproj adopt exits 0, preserves existing bytes, stages and commits nothing; committed synthetic adoption gives doctor exit 0, 19 PASS, 1 WARN, 0 FAIL; AC-6, AC-7 | isolated fixtures and fake gh, Linux, reviewed HEAD 1e6ca5d | reviewer
- PASS | GitHub connector: fetch_commit_workflow_runs, fetch_workflow_run_jobs, get_pr_info | PR 36 head equals reviewed HEAD; CI run 39714953910 and all Linux/macOS/Windows jobs succeeded; AC-12 | https://github.com/peejerator/newproj/actions/runs/39714953910, reviewed HEAD 1e6ca5d | reviewer
- PASS | git diff --check 07a8bebfa71b4283689c150452a00421fd8ae035...HEAD and complete diff inspection | no whitespace errors, blocking regressions, or unintended changes; frozen spec and earlier decisions/errata unchanged; moved guidance checked against added lines | base-commit diff, reviewed HEAD 1e6ca5d | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found, including the completed PASS review record | repository root, reviewed HEAD 1e6ca5d | reviewer

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-10-21
Reviewed at: 1e6ca5def98bc686442883d3acf5ad7f6e4f599f
Contract: 41d16049f23f8e26ddcee34021daea37ceee6f39
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Complete CLI wiring and help inspected; current-directory default, --name, and hidden --template-path checks pass.
- AC-2: VERIFIED | Terminal yes/no initialization and nonterminal refusal checks pass, including unchanged plain-folder contents on refusal.
- AC-3: VERIFIED | Dirty/staged/untracked, ignored files, invalid names, differing/identical template paths, links, and non-file destination checks pass; preflight rejects unsafe paths before adoption writes.
- AC-4: VERIFIED | Project-owned bytes, missing-file creation, bootstrap-review flags, classification table, and bootstrap instructions inspected and tested.
- AC-5: VERIFIED | Marked ignore append, hygiene preservation, editorconfig differences, LF coverage, and CRLF/mixed renormalization reporting inspected and tested.
- AC-6: VERIFIED | Remote HEAD resolution, default branch report, tagged-source URL answers, exit statuses, and no staging/commits inspected and tested; scratch CLI adoption independently confirmed no index or HEAD changes. E-002 permits local-path answers for development renders.
- AC-7: VERIFIED | Scratch repository without AGENTS.md adopted through the CLI; after committing the synthetic fixture, doctor exits 0 with 19 PASS, 1 WARN, and 0 FAIL.
- AC-8: VERIFIED | Added protocol/handoff lines retain durable-findings guidance and prefer AGENTS.md mappings; complete template content checks pass; protocol is 114 lines.
- AC-9: VERIFIED | Mapping, terminology, required-file creation, approval rules, fixed decisions/ADRs, hygiene reporting, and pointer frontmatter inspected and tested. Bootstrap's four-path LF recipe rejects the txt-only rule and accepts the general rule in executable regression tests.
- AC-10: VERIFIED | Decisions reference matches template/docs/DECISIONS.md byte for byte; identity check passes.
- AC-11: VERIFIED | E-020 appends the amendments to 11.9, 15.3, and 17.4; complete diff leaves earlier errata unchanged.
- AC-12: VERIFIED | Adoption/content coverage inspected; 411 local tests pass, with one Windows-only junction test skipped on Linux. Exact-commit CI run 39714953910 passes Linux, macOS, and Windows.
- AC-13: VERIFIED | AGENTS.md Commands lists adopt; content check passes.
- AC-14: VERIFIED | Committed handoff records first start-task use on 2026-10-20 to 2026-10-21, two rounds plus confirmation, and the durable-documents wording friction.

Findings:
- No blocking findings. F1 to F4 are resolved at the reviewed commit; link/non-file, CLI LF-rule, and bootstrap LF-recipe regression checks pass.
- Acceptance criteria were user-confirmed on 2026-10-21. This is a fresh Codex/GPT-6 review of work reported as implemented by Claude Code/claude-opus-5-5; earlier independent reviews also used Codex/GPT-6.
- Exact-commit CI confirmed through the GitHub connector: https://github.com/peejerator/newproj/actions/runs/39714953910; PR 36 head matches Reviewed at.
- Earlier validation entries and Exact next steps describe prior snapshots. Other handoff sections are unchanged under the review skill's write limits; this review supersedes the prior FAIL record.

## Exact next steps

1. The user commits and pushes the F4 fix to PR 36; confirm CI passes on Linux, macOS, and Windows, including the link and junction tests (AC-12).
2. Rerun the `review` skill in a different agent against the committed fix.

## Blockers / open questions

- For review, choices made beyond the interview decisions (recorded in DECISIONS D-006): adopt also refuses a subdirectory of a repository and a repository that already has `.copier-answers.yml`; the "required `.gitignore` entries" are the four rules spec 18.3 labels required (`.env`, `.env.*`, `!.env.example`, `context.md`), not the OS and editor snippets; `.editorconfig` differences and created files that the project ignores count as review items (exit 1); adopt prints, but does not run, `git config core.hooksPath .githooks`.
- AC-14, first real use of `start-task`: it ran 2026-10-20 to 2026-10-21 with two question rounds plus final confirmation. Friction: Round 1 question 3 proposed the durable-documents wording without explaining how relocated documents are found, so the user asked, and the mechanism and four follow-up decisions moved to Round 2. Preflight and branch creation ran without problems.

## Relevant decisions

- ERRATA E-002, E-007, E-008, E-018, E-019, E-020; DECISIONS D-002, D-006, D-007.
