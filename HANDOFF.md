# Handoff

Last updated: 2026-10-19 by Claude Code/claude-opus-5-5
Branch: m5-new-and-doctor
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: `newproj new` in `src/newproj/new.py` (preflight, render, local commit, remote, recovery commands); template source in `src/newproj/source.py` (bare cached clone, fetch only when the tag is missing).
- AC-2, AC-3, AC-4: `newproj doctor` in `src/newproj/doctor.py`, classifying results from `newproj.state`; `state.review_invalidations` split out of `review_signal` for the two-part review display, template copy synced.
- AC-5: `template/.githooks/commit-msg` (mode 100755); doctor checks `core.hooksPath`, the hook file, and the last 20 commits; erratum E-016.
- AC-6: `accept` prints one `&&` block with the commit first; answers file ends with one newline; `Icon?` rule with comment; root `AGENTS.md` push and PR rule.
- AC-7: erratum E-017. No hidden hook beyond `--template-path`: tests replace `source.TEMPLATE_URL` and `source.cache_dir` in process.
- AC-8: `--help` lists new, adopt, doctor; `adopt` exits 2; dependencies unchanged (test).
- AC-9: `tests/test_new.py`, `tests/test_doctor.py`, `tests/conftest.py`, `tests/fake_gh.py`.

## Current working area

- `src/newproj/`
- `tests/`
- `template/.githooks/`
- `template/.agents/skills/accept/SKILL.md`
- `template/.agents/skills/resume/scripts/state.py`
- `template/_includes/gitignore/macOS.gitignore`
- `template/{{_copier_conf.answers_file}}.jinja`
- `docs/ERRATA.md`
- `AGENTS.md`

## Validation

- PASS | uv run pytest | 324 passed, covers AC-1 to AC-9 | Linux (Raspberry Pi), Python 3.13, Copier 9.18.2, git 2.47.3 | implementer
- PASS | git diff --cached --check | no whitespace errors | Linux | implementer
- PASS | state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | implementer
- PASS | by hand: newproj new demo --no-remote --template-path <repo>, then newproj doctor, before and after a small commit | 0 FAIL, 0 WARN both times; hook rejected a Co-Authored-By line and a "Generated with" footer | Linux, isolated GIT_CONFIG_GLOBAL | implementer
- NOT RUN | CI on Linux, macOS, Windows | environment: needs the push of this branch | implementer

## Review

Outcome: none

## Exact next steps

1. The user commits and pushes, and opens the PR.
2. Check CI on all three operating systems; on a Windows failure, look first at the fake `gh.cmd` launcher in `tests/conftest.py` and the hook under Git for Windows' shell.
3. Record the CI result here with `CI` provenance, set Status to `complete`, then the user runs the `review` skill in a different agent.

## Blockers / open questions

- None blocking. Implementation choices for the reviewer and user to confirm:
  - `new` rewrites `_src_path` in `.copier-answers.yml` from the cache path to the template URL, so the file names no local path and works on every machine (not done for `--template-path`, per E-002).
  - When stdin is not a terminal, `new` uses the template's default answers and says so.
  - Missing `gh` or `uv`, unauthenticated `gh`, and no credential setup are WARN; missing `git` and Git identity are FAIL.
  - Recovery signals are INFO, except a stale `HANDOFF.md`, which is WARN (spec 20.7 examples).
- Unverified here: behavior on macOS and Windows (until CI runs), real `gh` against GitHub, and rendering from the real tagged repository, which has no `v0.1.0` tag yet (only local tagged repositories are tested).

## Relevant decisions

- D-001
- D-002
- E-002
- E-007
- E-011
- E-016
- E-017
