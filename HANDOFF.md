# Handoff

Last updated: 2026-11-03
Branch: m8-dogfooding-exit
Task: standard

## Status

in progress

## Completed

- AC-8: MIT `LICENSE` at the root (holder "2026 Patrick Canady", text from the template's MIT include); `pyproject.toml` has `license = "MIT"` and `license-files = ["LICENSE"]`, so the wheel and sdist carry it. Template default unchanged.
- AC-9: `CHANGELOG.md` with a `v0.1.0` section (undated; the tag date is in Git). `pyproject.toml` already declared `0.1.0`.
- AC-7: ERRATA E-022 appended (28.4 transcript-derived retrospective).
- AC-10, partly: `docs/ROADMAP.md` "Before M8" and "Before tagging v0.1.0" sections removed. Marking Phase 1 complete waits until the 28.1 checklist is all met.
- AC-1, AC-5 started: `docs/research/dogfooding.md` names both projects and has the 28.1 checklist; bullets 4 to 8 and 10 cite existing evidence; the rest are pending.
- `main` merged into this branch after M7.1 (PR #41), so the dogfooded template carries the M7.1 protocol wording. The merge's changes to `template/` are M7.1's, tested and reviewed there, not M8 changes under AC-11.
- No M8 change to `src/newproj/` or `template/` yet (AC-11).

## Current working area

- `docs/research/dogfooding.md`

## Validation

- PASS | uv run pytest | 445 passed, 1 skipped, after merging `main` | Linux, working tree | implementer
- PASS | state.py check | no violations, after merging `main` | Linux, working tree | implementer
- PASS | uv build | wheel has `dist-info/licenses/LICENSE` and `License-Expression: MIT`; sdist has `LICENSE` (AC-8) | Linux, working tree | implementer
- PASS | cmp of ERRATA.md's original bytes against the new file's prefix | earlier entries unchanged (AC-7) | working tree | implementer
- PASS | CI at 6f64e8e | run 41402042355, before merging `main`; CI at the merge commit runs on the next push (AC-11) | CI

## Review

Outcome: none

## Exact next steps

1. Set `"cleanupPeriodDays": 365` in Claude Code user settings on macOS and Windows (user; already set on the Linux machine).
2. Answer the open questions below.
3. After ohm-manager's current task is accepted, adopt ohm-manager with `newproj adopt --template-path <this repository>` on this branch, run its `bootstrap` skill, and record the result in `docs/research/dogfooding.md` (AC-2).
4. Create Project B with `newproj new` and check it with `newproj doctor` on macOS and Windows (AC-3).
5. Run recovery tests 24.1, 24.3, and 24.2 on real tasks and record each (AC-4).
6. At the end: the 28.4 transcript pass on each machine (AC-6), then mark Phase 1 complete in `docs/ROADMAP.md` (AC-10).

## Blockers / open questions

## Relevant decisions

- User decision (2026-11-02): ohm-manager is adopted after its current active task is accepted.
- User decision (2026-11-02, done 2026-11-03): 28.1 bullet 8 was resolved by fixing #38 and #39 in milestone M7.1 from `main`, merged before M8 resumed.
- User decisions and facts: `TASK.md` `## Context`.
