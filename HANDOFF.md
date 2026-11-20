# Handoff

Last updated: 2026-11-20 by Codex
Branch: fix-40-local-start-task
Task: standard
Environment: Linux

## Status

not started

## Completed

- User confirmed AC-1 through AC-6; the contract is active. Implementation has not started.

## Current working area

- `TASK.md`, `HANDOFF.md`
- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`
- `template/.agents/skills/handoff/SKILL.md`
- `tests/test_agent_content.py`, `tests/test_render.py`
- `docs/ERRATA.md`

## Validation

- PASS | git fetch origin; git rev-list --left-right --count 'main...main@{upstream}'; git merge-base --is-ancestor main HEAD | main matches upstream (0 ahead, 0 behind); main is an ancestor of the task branch | Linux | implementer
- PASS | python3 template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux; Python fallback because uv's cache is outside the writable sandbox | implementer
- NOT RUN | uv run pytest | Implementation has not started; automated coverage and suite run remain required by AC-5 | Linux | implementer

## Review

Outcome: none

## Exact next steps

1. User commits and pushes the staged task and handoff.
2. In a fresh implementation session, read the active contract and implement AC-1 through AC-6. Update this handoff to in progress before the first implementation change.
3. Add automated tests and run the validation in TASK.md. No additional behavioral fixture scenarios or manual tool runs are required.
4. Stage the verified implementation and print the user's commit and push commands. Obtain independent review of the committed skill changes before acceptance.

## Blockers / open questions

- None.

## Relevant decisions

- E-018 and E-019: preserve the existing task interview and draft resumption rules except for the confirmed local-only exception; append a superseding erratum.
- E-007 and E-008: the baseline records the updated main commit; acceptance criteria describe the finished result.
