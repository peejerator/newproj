# Handoff

Last updated: 2026-10-09 by Claude Code (claude-opus-5-5)
Branch: m2-agent-content
Task: standard
Environment: Windows

## Status

complete

## Completed

- AC-1: `template/docs/AGENT_PROTOCOL.md` (109 lines) with the nine required headings in order, implementing spec 11.1 to 11.9 for Phase 1. No Phase 2 commands are named.
- AC-2: the protocol's During work section states the `HANDOFF.md` heading contract, status values, provenance values, and the reviewer-only `## Review` rule with its outcome values.
- AC-3: `resume`, `handoff`, and `bootstrap` skills under `template/.agents/skills/`. `resume` gives the `state.py` invocation with `python3` and `py -3` fallbacks and a raw Git command table (verified to behave identically in PowerShell and bash).
- AC-4: Claude pointer skills under `template/.claude/skills/` with byte-identical frontmatter and a one-line body naming the canonical path.
- AC-5: `template/docs/PROMPTS.md` with resume, handoff, and bootstrap adapters for hand-uploaded files.
- AC-6: `tests/test_agent_content.py` (21 tests; 31 in the suite).
- AC-7: `AGENTS.md` interim rules replaced by the protocol instruction plus this repository's path mapping; `CLAUDE.md` imports both files.
- AC-8: CI uses `actions/checkout@v5`.
- Branch is based on `main` after the M1 merge; the M2 setup commit was cherry-picked from `m1-skeleton`, where it had been made on top of pre-merge history.

## Current working area

- `template/docs/`
- `template/.agents/skills/`
- `template/.claude/skills/`
- `tests/test_agent_content.py`

## Validation

- PASS | uv run pytest | 31 passed; covers AC-1 line limit and headings, AC-2 invariant strings, AC-3 frontmatter, AC-4 pointer frontmatter and body, AC-5 adapter headings, AC-6 hygiene (no em or en dash, no CR, no Phase 2 commands) on every template file | Windows, Python 3.13 | implementer
- PASS | line count of template/docs/AGENT_PROTOCOL.md | 109 lines, AC-1 | Windows | implementer
- PASS | git ls-files --eol on new files | all LF in the working tree | Windows | implementer
- PASS | git diff --check | no whitespace errors | Windows | implementer
- PASS | uv run copier copy --defaults into a scratch directory | all eight agent files rendered byte-identical to template/ | Windows, Copier from uv.lock | implementer
- PASS | read-through of protocol, skills, and prompts as a first-time agent | every instruction actionable with Phase 1 tooling; one vague rule ("the workflow requires it") made concrete | static review | implementer
- PASS | gh pr checks 2 | AC-6: push run 37950856148 and pull-request run 37951276473 pass on commit 41114dc, https://github.com/peejerator/newproj/actions/runs/37951276473 | GitHub Actions, ubuntu-latest/macos-latest/windows-latest, Python 3.11 | CI

## Review

Outcome: none

## Exact next steps

1. Pull request: https://github.com/peejerator/newproj/pull/2. Implementation commit: 41114dc; later commits change `HANDOFF.md` only.
2. Independent review by a different agent or model, using the record format in `template/.agents/skills/handoff/SKILL.md` (Review record).
3. ROADMAP "done when" for M2 also needs the content copied by hand into one real project and used for a few days; that is the user's step.

## Blockers / open questions

- Interpretation for review: Phase 1 formal-risk work is written as `Tier: standard` with the risk noted under `## Context` (spec 11.2 says it "runs as a standard task"). If `Tier: formal` is preferred, the protocol, `resume`, `handoff`, and `bootstrap` need a one-line change.
- With no `review` skill in Phase 1, the review record format (13.6) lives in the `handoff` skill. When the `review` skill ships (Phase 2), move it there so it has one home (D25).
- The `handoff` skill embeds the neutral `TASK.md` and `HANDOFF.md` content as a fallback until M3 ships `.agents/skills/handoff/neutral/`. M3 should add a test that the embedded copies match those files byte for byte, or drop the fallback.
- Local branch `m1-skeleton` still holds the original setup commit `f2c3203`; it can be deleted once this branch is merged.

## Relevant decisions

- D-002
- D-004
