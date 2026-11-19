# Handoff

Last updated: 2026-11-17
Branch: m8-dogfooding-exit
Task: standard

## Status

validating

## Completed

- AC-8: MIT `LICENSE` at the root (holder "2026 Patrick Canady", text from the template's MIT include); `pyproject.toml` has `license = "MIT"` and `license-files = ["LICENSE"]`, so the wheel and sdist carry it. Template default unchanged.
- AC-9: `CHANGELOG.md` with a `v0.1.0` section (undated; the tag date is in Git). `pyproject.toml` already declared `0.1.0`.
- AC-7: ERRATA E-022 appended (28.4 transcript-derived retrospective).
- AC-10: `docs/ROADMAP.md` "Before M8" and "Before tagging v0.1.0" sections removed; Phase 1 marked complete, no Phase 2 milestones.
- AC-6: 28.4 retrospective in `docs/research/dogfooding.md`: aggregate transcript figures for Linux (both eras) and Windows (Agent B of 24.2), one line per ongoing signal from the user's answers, and the closing rule. No transcript content or script committed.
- AC-1, AC-5 started: `docs/research/dogfooding.md` names both projects and has the 28.1 checklist; every bullet (1 to 12) is met.
- `main` merged into this branch after M7.1 (PR #41), so the dogfooded template carries the M7.1 protocol wording. The merge's changes to `template/` are M7.1's, tested and reviewed there, not M8 changes under AC-11.
- AC-3: Project B created as `pokemon-content`, private repository, `newproj doctor` healthy; first real task (game-harness skeleton) accepted 2026-11-09 after a Codex PASS review (`docs/research/dogfooding.md`, Project B creation). 28.1 bullets 1 and 3 marked met (E-023).
- AC-4: 24.1, 24.2, and 24.3 passed in pokemon-content (`docs/research/dogfooding.md`, Recovery tests; 24.2 ran from this machine to Windows 11, E-023; 24.3 resumed Claude Code's interrupted session in Codex CLI). 28.1 bullet 9 marked met.
- AC-2: ohm-manager adopted and bootstrapped; `newproj doctor` 0 FAIL, one WARN for `AGENTS.md` size (`docs/research/dogfooding.md`, ohm-manager adoption). 28.1 bullets 2 and 11 marked met.
- M8 template changes (AC-11), from pokemon-content's first task, ERRATA E-024, each covered by a test:
  - `template/docs/AGENT_PROTOCOL.md`, During work: set `in progress` before the first change; run the `state.py` check after each handoff update (`test_protocol_marks_work_started_and_checks_each_handoff_update`).
  - `template/docs/AGENT_PROTOCOL.md`, Session end and switching, and `template/.agents/skills/handoff/SKILL.md`, Marking the task complete: print the commit command for uncommitted work the next step needs (`test_uncommitted_work_gets_a_printed_commit_command`).
  - `template/.agents/skills/start-task/references/interview.md`: criteria must be checkable in the review environment (`test_interview_requires_criteria_the_reviewer_can_check`).
  - `template/AGENTS.md.jinja`, Conventions: template-managed files are never edited by hand and are excluded from formatters and linters (`tests/test_render.py`, `test_agents_md`).
  - The protocol is 116 lines.

## Current working area

- `docs/research/dogfooding.md`

## Validation

- PASS | uv run pytest | 448 passed, 1 skipped, with the E-024 changes | Linux, working tree | implementer
- PASS | state.py check | no violations, after merging `main` | Linux, working tree | implementer
- PASS | uv build | wheel has `dist-info/licenses/LICENSE` and `License-Expression: MIT`; sdist has `LICENSE` (AC-8) | Linux, working tree | implementer
- PASS | cmp of ERRATA.md's original bytes against the new file's prefix | earlier entries unchanged (AC-7) | working tree | implementer
- PASS | CI at 6f64e8e | run 41402042355, before merging `main`; CI at the merge commit runs on the next push (AC-11) | CI

- PASS | uv run pytest | 448 passed, 1 skipped; AC-11 | Linux, reviewed HEAD | reviewer
- PASS | UV_CACHE_DIR=/tmp/newproj-review-uv uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations | Linux | reviewer
- PASS | gh run view 44212690518 --json jobs,headSha,conclusion | Linux, macOS, Windows jobs successful at c1dab8f965c5e4863672eea8101a6308c1c38c47; AC-3, AC-5, AC-11 | https://github.com/peejerator/newproj/actions/runs/44212690518 | reviewer
- PASS | git diff --exit-code 494fb67 HEAD -- docs/spec.md | unchanged; AC-12 | reviewed HEAD | reviewer
- PASS | Python byte comparisons and added-line privacy scan; full review diff inspection | ERRATA prefix unchanged, state.py copies identical, no private material or personal paths added; path patterns in TASK.md are search instructions; AC-7, AC-11, AC-12 | reviewed HEAD | reviewer
- PASS | Read dogfooding.md against AC-1 to AC-6 and spec 24.1 to 24.3, 28.1, 28.4 with E-022 and E-023 | every required summary, pass criterion, checklist item, signal and aggregate present | reviewed HEAD | reviewer

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-11-18
Reviewed at: c1dab8f965c5e4863672eea8101a6308c1c38c47
Contract: 4e74863aa1aea970bf91711a7873aa9990fe2b58
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | dogfooding.md names ohm-manager and Project B with their roles.
- AC-2: VERIFIED | adoption summary records collision refusal and retry, bootstrap, hygiene preservation, renormalization and healthy doctor results.
- AC-3: VERIFIED | creation summary records new, private remote, healthy Linux doctor and accepted first real task; exact-HEAD three-platform CI confirmed under E-023.
- AC-4: VERIFIED | all three recovery summaries individually check the spec pass criteria; 24.2 uses Linux and Windows and 24.3 uses Claude Code and Codex without prior chat.
- AC-5: VERIFIED | all twelve 28.1 bullets marked met with relevant document, fixture or test evidence; cited tests inspected and suite and CI passed.
- AC-6: VERIFIED | all six ongoing signals, closing judgement, per-machine aggregates, surviving baseline and calculation method recorded under E-022.
- AC-7: VERIFIED | E-022 appends the approved retrospective replacement; base ERRATA bytes remain an exact prefix.
- AC-8: VERIFIED | root MIT LICENSE and pyproject license declaration present; no-license default unchanged and render tests pass.
- AC-9: VERIFIED | v0.1.0 changelog lists CLI, template and six skills; project version is 0.1.0.
- AC-10: VERIFIED | roadmap marks Phase 1 complete, removes prerequisite sections, and contains no Phase 2 milestones.
- AC-11: VERIFIED | all M8 template edits listed in Completed and covered by passing content/render tests; no src changes; state.py copies identical; exact-HEAD CI passed on all three OSes. M7.1 merged changes have their own tests and fixture evidence.
- AC-12: VERIFIED | frozen spec unchanged; complete diff inspected for private material, transcripts and personal paths; none introduced by M8. M7.1 fixture result quotations describe synthetic public fixtures.

Findings:
- No blocking findings or regressions found.
- Criteria user-confirmed 2026-11-02; amended AC-3 and AC-4 user-confirmed 2026-11-03.
- Independent session; this reviewer did not implement M8. Implementer model identity is not recorded, so model-family independence cannot be established.
- AC-2 to AC-4 and AC-6 require committed evidence summaries. Those artifacts were verified at HEAD; historical real-project sessions and transcript aggregates were not rerun or independently recalculated. The single-pass private-transcript authorization was not reused.
- M7.1 changes merged from main are included in the required base-commit diff, identified by Git history and checked; they are not unexplained M8 scope additions.

## Exact next steps

1. The user commits and pushes; CI must pass on Linux, macOS, and Windows at `HEAD` (AC-11).
2. Independent review by a different agent (`review` skill), then `accept`; the accept block ends with the `v0.1.0` tag commands.

## Blockers / open questions

## Relevant decisions

- User decision (2026-11-02): ohm-manager is adopted after its current active task is accepted (done 2026-11-03).
- User decision (2026-11-03): Project B's repository is `pokemon-content`, private.
- User decision (2026-11-02, done 2026-11-03): 28.1 bullet 8 was resolved by fixing #38 and #39 in milestone M7.1 from `main`, merged before M8 resumed.
- User decision (2026-11-03): one Linux development machine; option 2 of the agent's proposal, recorded as ERRATA E-023 and in `AGENTS.md` Environment.
- User decision (2026-11-09): template fixes (a) to (e) from pokemon-content's first task, recorded as ERRATA E-024.
- User decisions and facts: `TASK.md` `## Context`.
