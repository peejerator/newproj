# Handoff

Last updated: 2026-11-02
Branch: m8-dogfooding-exit
Task: standard

## Status

in progress

## Completed

- AC-8: MIT `LICENSE` at the root (holder "2026 Patrick Canady", text from the template's MIT include); `pyproject.toml` has `license = "MIT"` and `license-files = ["LICENSE"]`, so the wheel and sdist carry it. Template default unchanged.
- AC-9: `CHANGELOG.md` with a `v0.1.0` section (undated; the tag date is in Git). `pyproject.toml` already declared `0.1.0`.
- AC-7: ERRATA E-022 appended (28.4 transcript-derived retrospective).
- AC-10, partly: `docs/ROADMAP.md` "Before M8" and "Before tagging v0.1.0" sections removed. Marking Phase 1 complete waits until the 28.1 checklist is all met.
- AC-1, AC-5 started: `docs/research/dogfooding.md` names both projects and has the 28.1 checklist; bullets 4 to 7 and 10 cite existing evidence; the rest are pending or not met (bullet 8).
- No change to `src/newproj/` or `template/` yet (AC-11).

## Current working area

- `docs/research/dogfooding.md`

## Validation

- PASS | uv run pytest | 443 passed, 1 skipped | Linux, working tree | implementer
- PASS | uv build | wheel has `dist-info/licenses/LICENSE` and `License-Expression: MIT`; sdist has `LICENSE` (AC-8) | Linux, working tree | implementer
- PASS | cmp of ERRATA.md's original bytes against the new file's prefix | earlier entries unchanged (AC-7) | working tree | implementer
- NOT RUN | CI at HEAD | needs the user's commit and push (AC-11) | implementer

## Review

Outcome: none

## Exact next steps

1. Set `"cleanupPeriodDays": 365` in Claude Code user settings on macOS and Windows (user; already set on the Linux machine).
2. Answer the open questions below.
3. Adopt ohm-manager with `newproj adopt --template-path <this repository>` on this branch, run its `bootstrap` skill, and record the result in `docs/research/dogfooding.md` (AC-2).
4. Create Project B with `newproj new` and check it with `newproj doctor` on macOS and Windows (AC-3).
5. Run recovery tests 24.1, 24.3, and 24.2 on real tasks and record each (AC-4).
6. At the end: the 28.4 transcript pass on each machine (AC-6), then mark Phase 1 complete in `docs/ROADMAP.md` (AC-10).

## Blockers / open questions

- 28.1 bullet 8 is not met, so AC-5 cannot pass as written: fixtures must pass on at least two tools, but B6 is 0/2 on Claude Code CLI and 1/2 on Codex CLI (issue #38) and B10 is 0/2 on Codex CLI (issue #39) (`docs/research/behavioral-fixtures.md`, Pass rates). That document says failures are fixed in a later milestone before M8; no milestone did. Fixing #38 and #39 and rerunning the fixtures is larger than a dogfooding fix, so it is outside this task's scope. Needs the user's decision.
- ohm-manager has an active standard task on `main` (clean tree). Running `newproj adopt` there now would mix the adoption into that task's working tree. Needs the user's decision on when and on which branch to adopt.

## Relevant decisions

- User decisions and facts: `TASK.md` `## Context`.
