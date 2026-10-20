# Handoff

Last updated: 2026-10-19 by Codex
Branch: m5.1-start-task
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: added canonical start-task metadata, invocation policy, three matching pointers, and root policy copy.
- AC-2: documented all three sources, preconditions, branch creation, question rounds, draft updates, confirmation, staging, and stop/go behavior.
- AC-3: contract headers, baseline, target, and end-state criterion rules stay in handoff's Writing a task section.
- AC-4: added and linked the interview reference for facts, decisions, recommendations, comprehensive rounds, and finish conditions.
- AC-5: aligned protocol, review, resume, handoff, prompts, and both AGENTS files; protocol remains 114 lines.
- AC-6: doctor checks six skills, start-task metadata/policy/reference, and its Claude pointer.
- AC-7: appended E-018 covering decisions 1 to 11 and added the M5.1 roadmap row and M6 first-use reminder.
- AC-8: render, pointer, confirmation-marker, policy, doctor failure, and healthy-project tests pass locally; three-OS CI pending.

## Current working area

- `template/.agents/skills/`
- `template/.claude/skills/start-task/`
- `.agents/skills/start-task/`
- `.claude/skills/start-task/`
- `template/docs/`
- `template/AGENTS.md.jinja`
- `src/newproj/doctor.py`
- `tests/`
- `AGENTS.md`
- `docs/ERRATA.md`
- `docs/ROADMAP.md`

## Validation

- PASS | uv run pytest | 363 passed; AC-1, AC-5, AC-6, AC-8 regression coverage; one expected Copier dirty-template warning | Linux, Python 3.13.5, Copier 9.18.2 | implementer
- PASS | uv run pytest tests/test_agent_content.py tests/test_render.py | 160 passed after final skill wording changes; AC-1, AC-3, AC-4, AC-5, AC-8 | Linux | implementer
- PASS | AC-2 manual inspection | every behavior in Context decisions 2 to 9 is present in start-task/SKILL.md | working-tree skill and interview reference | implementer
- PASS | AC-3, AC-4 manual inspection | format is referenced rather than copied; interview guidance covers all four requested topics and is linked before Round 1 | working-tree skill, reference, handoff | implementer
- PASS | AC-5, AC-7 manual inspection | all named instruction surfaces agree; protocol 114 lines; E-018 records decisions 1 to 11; M5.1 sits between M5 and M6 | working-tree diff | implementer
- PASS | git diff --check | no whitespace errors; full diff inspected; TASK.md, spec, state copies, bootstrap, accept, and Review section unchanged | working tree | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | implementer
- PASS | uv run --project <repo> newproj new demo --no-remote --template-path <repo>; uv run --project <repo> newproj doctor | generated demo; doctor: 19 PASS, 1 WARN, 0 FAIL; six skills present (AC-6, AC-8); warning is unauthenticated isolated gh config | scratch directory, synthetic Git identity, Linux | implementer
- FAIL | uv run python <skill-creator>/scripts/quick_validate.py template/.agents/skills/start-task | generic validator rejects disable-model-invocation, which AC-1 and E-010 require; repository metadata, policy, pointer, and render tests pass | supplementary validator compatibility limitation | implementer
- NOT RUN | CI on Linux, macOS, Windows | changes are uncommitted; CI runs after the user's commit and push | environment: no CI run for these changes yet | implementer

## Review

Outcome: none

## Exact next steps

1. User commits the staged implementation and pushes: `git commit -m "Implement M5.1 start-task skill" && git push`. The PR already exists.
2. Check CI on the resulting commit on Linux, macOS, and Windows; AC-8 remains pending until all three pass.
3. User invokes review in a different agent against the committed implementation; instruction-file changes warrant independent review. Leave TASK.md active and Review unchanged until then.

## Blockers / open questions

- No implementation blocker. Three-OS CI and independent review are pending; the generic skill validator's unsupported required metadata is recorded above.

## Relevant decisions

- The user's decisions for this milestone are under `## Context` in `TASK.md`.
- E-018 records the new workflow and its amendments; E-007, E-008, E-010, and E-014 remain applicable.
