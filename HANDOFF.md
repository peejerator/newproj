# Handoff

Last updated: 2026-11-21
Branch: fix-46-remote-name
Task: standard

## Status

validating

## Completed

- AC-1: `src/newproj/state.py` adds `configured_remotes`, `select_remote`, and `set_head_command`; `resolve_default_branch` runs steps 1 and 2 against the selected remote, returns unknown (step 4, no local fallback) when remotes exist but none is selected, and resolves `origin` repositories as before. Template copy synced (byte-identical).
- AC-2: hints and fixes in `state.py`, `doctor.py`, and `adopt.py` name the selected remote; with no remote the fix is "add a remote and run `git remote set-head <remote> --auto`".
- AC-3: `adopt.set_head` runs `git remote set-head <remote> --auto` for the selected remote only.
- AC-4, AC-5: `handoff` Writing a task uses the selection rule and asks when unresolved; `start-task` prints `git push -u <remote> <branch>` (target branch's configured remote); `accept` prints `git push <remote> --delete <task branch>` (task branch's configured remote). Pointer frontmatter unchanged.
- AC-6: E-027 appended to `docs/ERRATA.md`, including the follow-up decision below.
- AC-7: tests added in `tests/test_state.py`, `tests/test_doctor.py`, `tests/test_adopt.py`, `tests/test_agent_content.py`; existing no-remote assertions now expect `<remote>`.

## Current working area

- `src/newproj/state.py`, `template/.agents/skills/resume/scripts/state.py`, `src/newproj/doctor.py`, `src/newproj/adopt.py`
- `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/start-task/SKILL.md`, `template/.agents/skills/accept/SKILL.md`
- `docs/ERRATA.md`
- `tests/test_state.py`, `tests/test_doctor.py`, `tests/test_adopt.py`, `tests/test_agent_content.py`

## Validation

- PASS | uv run pytest | 537 passed, 1 skipped; covers AC-1 to AC-5 and AC-7 tests, byte-identical state.py copy, pointer frontmatter | Linux | implementer
- PASS | git diff docs/spec.md docs/DECISIONS.md; git diff docs/ERRATA.md | spec and decisions unchanged; ERRATA diff is additions only (AC-6) | Linux | implementer
- NOT RUN | CI on Linux, macOS, and Windows | skipped: runs after the user commits and pushes | | implementer

## Review

Outcome: none

## Exact next steps

1. The user commits the implementation and pushes; confirm CI passes on Linux, macOS, and Windows (AC-7).
2. Independent review by a different agent (the `review` skill), expected because skill content changed.
3. Acceptance via the `accept` skill.

## Blockers / open questions

## Relevant decisions

- Remote selection rule and printed push commands: `TASK.md`, `## Context`, decisions 2 and 3.
- Follow-up user decision (2026-11-21, this session): decision 2's fix for several remotes without `origin` (`git remote set-head <remote> --auto`) could never take effect under the rule as written, so the user chose to extend selection: with several remotes and none named `origin`, select the one remote whose `refs/remotes/<remote>/HEAD` is set, if exactly one has it. Recorded in E-027 item 1.
- E-027 supersedes E-025 resolution item 2's "Remote-backed target resolution remains unchanged".
