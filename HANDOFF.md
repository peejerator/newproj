# Handoff

Last updated: 2026-11-20 by Codex
Branch: fix-40-local-start-task
Task: standard
Environment: Linux

## Status

complete

## Completed

- AC-1: start-task defines local-only by a successful, empty remote listing; new tasks and resumed drafts explain the limited preflight skip.
- AC-2: local-only final commands contain only the commit; remote-backed output retains push guidance.
- AC-3: remote-backed freshness checks and all applicable branch, ancestry, confirmation, and staging safeguards remain required.
- AC-4: start-task, interview guidance, and handoff honor an explicit target, then existing configured default, main, master, or ask the user.
- AC-5: automated content regression coverage and rendered skill equality checks are added; focused and full suites pass.
- AC-6: E-025 appends the approved exceptions to E-018/E-019.

## Current working area

- `HANDOFF.md`
- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`
- `template/.agents/skills/handoff/SKILL.md`
- `tests/test_agent_content.py`, `tests/test_render.py`
- `docs/ERRATA.md`

## Validation

- PASS | uv run pytest tests/test_agent_content.py tests/test_render.py | 185 passed; AC-1 through AC-6 content and rendering coverage | Linux; Python 3.13.5 | implementer
- PASS | AC-1 inspection and test_start_task_local_only_preflight | Successful empty remote listing defines local-only; new and resumed paths explain skipping only fetch and target-upstream freshness requirements | Linux | implementer
- PASS | AC-2 inspection and test_start_task_final_commands_depend_on_remotes | Local-only output includes only commit; remote-backed output retains push and applicable PR guidance | Linux | implementer
- PASS | AC-3 instruction diff and remote/branch safeguard content tests | Missing upstream, ahead, behind, divergence, and fetch failure still stop when any remote exists; branch, ancestry, confirmation, and staging rules retained | Linux | implementer
- PASS | AC-4 inspection and test_local_only_target_resolution_agrees | All three documents honor user target, then existing init.defaultBranch, main, master; unresolved targets ask the user | Linux | implementer
- PASS | uv run pytest | AC-5: 466 passed, 1 skipped (Windows junction test on Linux); one expected Copier dirty-template warning | Linux; Python 3.13.5 | implementer
- PASS | AC-6 byte comparison against 3630862 and git diff inspection | E-025 appended; earlier errata, frozen spec, accepted decisions, active contract, state code, and behavioral fixtures unchanged | Linux | implementer
- PASS | git diff --check and full diff inspection | No whitespace errors or unintended changes; no dependency or CLI changes | Linux | implementer
- PASS | python3 template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | implementer
- NOT RUN | macOS and Windows CI | Requires user commit and push; required before merge | Linux session only | implementer

## Review

Outcome: none

## Exact next steps

1. User commits the staged implementation with `git commit -m "Support local-only start-task interviews (#40)"` and pushes with `git push`.
2. Run the user-invoked review skill in a different agent on the committed changes; review is expected for these skill instruction changes. Review remains unperformed (Outcome: none).
3. Verify macOS and Windows CI before acceptance. Open the PR only at acceptance, as AGENTS.md requires. No additional behavioral fixture scenarios or manual tool runs are required.

## Blockers / open questions

- None.

## Relevant decisions

- E-025 supersedes conflicting parts of E-018/E-019 for local-only interviews and aligns handoff target resolution.
- E-007 and E-008: the baseline records the updated main commit; acceptance criteria describe the finished result.
