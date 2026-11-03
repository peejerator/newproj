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
- AC-3 started: Project B created as `pokemon-content`, private repository, `newproj doctor` healthy (`docs/research/dogfooding.md`, Project B creation). Its first real task is pending.
- ohm-manager's 2026-10-29 task: checks rerun at its `HEAD` pass; the user reset its task files to neutral (3bd2b51). It is ready for adoption.
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

1. Apply the `TASK.md` amendment for E-023 (user).
2. Adopt ohm-manager with `newproj adopt --template-path <this repository>` on this branch, run its `bootstrap` skill, and record the result in `docs/research/dogfooding.md` (AC-2).
3. Do a first real standard task in `pokemon-content` with the template's workflow (AC-3); it can host recovery test 24.1 or 24.3.
4. Run recovery tests 24.1 and 24.3 on real tasks here, and 24.2 between this machine and macOS or Windows, working directly on that machine (E-023); record each (AC-4).
5. At the end: the 28.4 transcript pass on this machine (AC-6), then mark Phase 1 complete in `docs/ROADMAP.md` (AC-10).

## Blockers / open questions

## Relevant decisions

- User decision (2026-11-02): ohm-manager is adopted after its current active task is accepted (done 2026-11-03).
- User decision (2026-11-03): Project B's repository is `pokemon-content`, private.
- User decision (2026-11-02, done 2026-11-03): 28.1 bullet 8 was resolved by fixing #38 and #39 in milestone M7.1 from `main`, merged before M8 resumed.
- User decision (2026-11-03): one Linux development machine; option 2 of the agent's proposal, recorded as ERRATA E-023 and in `AGENTS.md` Environment.
- User decisions and facts: `TASK.md` `## Context`.
