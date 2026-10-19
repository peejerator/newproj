# Handoff

Last updated: 2026-10-19 by Claude Code/claude-opus-5-5
Branch: m2.1-trial-fixes
Task: standard
Environment: Linux (Raspberry Pi), local

## Status

validating

## Completed

- AC-1: E-003 to E-014 in `docs/ERRATA.md`, one per accepted decision, each with sections, observed failure (issue and commit), and resolution; header states the observed-failure bar. E-001 and E-002 unchanged.
- AC-2: protocol adds precedence, user-addressed questions, commit order when the user commits, short-lived task branch with `--ff-only`, review expected for safety and instruction-file changes. 114 lines, nine headings unchanged.
- AC-3: handoff skill sets `Base commit`/`Target branch`, end-state ACs, size guideline, points to `review` and `accept`; review format and neutral text removed.
- AC-4: `template/.agents/skills/handoff/neutral/{TASK,HANDOFF}.md` extracted from spec 12.8.
- AC-5: resume stops and reports on a user-addressed question; otherwise continues.
- AC-6: new `review` skill; AC-7: new `accept` skill.
- AC-8: `disable-model-invocation: true` and `agents/openai.yaml` on bootstrap, review, accept; E-010 records Claude Code and Codex as checked against docs, Copilot and all others unverified.
- AC-9: template Claude pointers and root `.agents/skills/`, `.claude/skills/` pointers for all five skills, plus root `openai.yaml` copies.
- AC-10: review and accept adapters in `template/docs/PROMPTS.md`.
- AC-11: M2.1 row in `docs/ROADMAP.md`, neutral copies moved from M3, `state.py` `check` mode in M4.
- AC-12: `tests/test_agent_content.py` covers all listed cases.

## Current working area

- `docs/ERRATA.md`, `docs/ROADMAP.md`, `AGENTS.md`
- `template/docs/AGENT_PROTOCOL.md`, `template/docs/PROMPTS.md`
- `template/.agents/skills/`, `template/.claude/skills/`
- `.agents/skills/`, `.claude/skills/`
- `tests/test_agent_content.py`

## Validation

- PASS | uv run pytest | 75 passed, covers AC-2, AC-4, AC-8, AC-9, AC-12 | Linux, Python via uv | implementer
- PASS | git diff --cached --check | no whitespace errors | Linux | implementer
- PASS | wc -l template/docs/AGENT_PROTOCOL.md | 114 lines, covers AC-2 | Linux | implementer
- PASS | git diff --cached --name-only on protected paths | spec, copier files, src, TASK.md, DECISIONS.md untouched; ERRATA changes only its header above E-001 | Linux | implementer
- PASS | first-time read-through of all five skills with Phase 1 tooling | no step needs `state.py`; commands avoid shell-specific syntax | Linux | implementer
- NOT RUN | CI on Linux, macOS, Windows | environment: requires the user's commit and push | implementer

## Review

Outcome: none

## Exact next steps

1. The user commits the staged work with the commands proposed in the session, then pushes `m2.1-trial-fixes` and opens the PR to `main`.
2. Confirm CI passes on all three operating systems and record it here with `CI` provenance; set status to `complete`.
3. The user runs the `review` skill in a different agent or model (expected: this task changes instruction files, E-009).
4. After a PASS, the user runs the `accept` skill on this branch before merging.

## Blockers / open questions

- For the user: AC-6 says the reviewer changes only `## Review` and its own validation entries, while spec 17.6 has the reviewer write `## Exact next steps`, `## Blockers / open questions` and reset `## Status`. I followed AC-6 and recorded the deviation in E-011 (remaining work goes under `Findings:`, and `resume` sets `in progress`). Confirm this is intended.
- For the user: `AGENTS.md` now states as a durable rule that the user makes every commit, so the protocol's staged-commit path applies to every session here. Confirm, or say if it should apply to this task only.
- For the user: E-010's checks of `disable-model-invocation` and `allow_implicit_invocation` are against vendor documentation only, not behavior; behavioral confirmation belongs in M7. Copilot is unverified.
- For the user: `accept` stops when the review is not a current PASS, and continues only on the user's explicit override, recorded in the commit message (spec 12.4). AC-7 does not say what happens on failure; confirm this reading.

## Relevant decisions

- D-002, D-003
- ERRATA E-003 to E-014
