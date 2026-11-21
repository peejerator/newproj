# Handoff

Last updated: 2026-11-21 by Claude Code
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
- AC-5: B12/B13 fixtures and a local `claude -p` driver now exercise new-task and resumed-draft interviews automatically. Both real runs PASS; pytest passes without launching agents or needing credentials. D-009 records the approved exception to D-008.
- AC-6: E-025 appends the approved exceptions to E-018/E-019. E-026 supersedes E-025 item 4, which still said no behavioral fixtures were required, to match amended AC-5 and D-009.
- Review follow-up (findings at c2a78d7): B13's scripted check now requires the activated criteria to equal the draft's settled AC-1 to AC-3, whitespace normalized; new tests cover rewording, a dropped criterion, a missing section, and rewrapping.

## Current working area

- `HANDOFF.md`
- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`
- `template/.agents/skills/handoff/SKILL.md`
- `tests/test_agent_content.py`, `tests/test_render.py`
- `docs/ERRATA.md`
- `docs/DECISIONS.md`, `scripts/behavior.py`, `scripts/start_task_behavior.py`
- `tests/test_start_task_behavior.py`, `tests/test_behavior.py`
- `tests/fixtures/behavior/B12/`, `tests/fixtures/behavior/B13/`, `tests/fixtures/behavior/start_task.py`
- `AGENTS.md`
- `tests/fixtures/behavior/B13/check.py`

## Validation

- PASS | uv run pytest tests/test_agent_content.py tests/test_render.py | 185 passed; AC-1 through AC-6 content and rendering coverage | Linux; Python 3.13.5 | implementer
- PASS | AC-1 inspection and test_start_task_local_only_preflight | Successful empty remote listing defines local-only; new and resumed paths explain skipping only fetch and target-upstream freshness requirements | Linux | implementer
- PASS | AC-2 inspection and test_start_task_final_commands_depend_on_remotes | Local-only output includes only commit; remote-backed output retains push and applicable PR guidance | Linux | implementer
- PASS | AC-3 instruction diff and remote/branch safeguard content tests | Missing upstream, ahead, behind, divergence, and fetch failure still stop when any remote exists; branch, ancestry, confirmation, and staging rules retained | Linux | implementer
- PASS | AC-4 inspection and test_local_only_target_resolution_agrees | All three documents honor user target, then existing init.defaultBranch, main, master; unresolved targets ask the user | Linux | implementer
- PASS | uv run pytest | AC-5: 514 passed, 1 skipped (Windows junction test on Linux); one expected Copier dirty-template warning. Includes real-Git fixture setup, synthetic passing/failing verdicts, and mocked driver coverage for errors, timeout, unexpected replies, and premature activation | Linux; Python 3.13.5 | implementer
- PASS | uv run python scripts/start_task_behavior.py /tmp/newproj-start-task-20261121-03 | AC-5: B12 PASS, B13 PASS, overall PASS. Skip explained; no push/PR command; only TASK.md and HANDOFF.md changed and staged; no commits including reflogs. Raw events and transcripts under the output directory's .behavior/ | Linux; Claude Code 2.1.330; claude-opus-5-5; synthetic textstats projects | implementer
- PASS | AC-6 byte comparison against 0bc980c and instruction diff inspection | E-025 and D-009 are append-only; frozen spec, active contract, state code, existing behavioral fixtures, and independent review record unchanged in this follow-up | Linux | implementer
- PASS | git diff --check and full diff inspection | No whitespace errors or unintended changes; no dependency or CLI changes | Linux | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | implementer
- NOT RUN | macOS and Windows CI for this follow-up | Requires user commit and push; required before merge. The CI entry below covers only de89d87 | Linux session only | implementer
- PASS | uv run pytest | 466 passed, 1 skipped (Windows junction test on Linux) at de89d87 | Linux; Python 3.13.5 | reviewer
- PASS | state.py check --neutral-dir template/.agents/skills/handoff/neutral and git diff --check 0bc980c HEAD | No violations; no whitespace errors | Linux | reviewer
- PASS | GitHub Actions CI run 44685446259 at de89d87 | Tests passed on ubuntu-latest, macos-latest, windows-latest | Linux, macOS, Windows | CI
- PASS | uv run pytest | 514 passed, 1 skipped (Windows junction test on Linux) at c2a78d7 | Linux; Python 3.13.5 | reviewer
- PASS | state.py check --neutral-dir template/.agents/skills/handoff/neutral and git diff --check 0bc980c HEAD | No violations; no whitespace errors at c2a78d7 | Linux | reviewer
- PASS | uv run python scripts/start_task_behavior.py <scratch dir outside any repository> | AC-5: B12 PASS (3 turns), B13 PASS (2 turns), overall PASS at c2a78d7; transcripts show the skip line and a commit-only command block | Linux; Claude Code 2.1.330; claude-opus-5-5 | reviewer
- PASS | GitHub Actions CI run 44878117963 at c2a78d7 | Tests passed on ubuntu-latest, macos-latest, windows-latest | Linux, macOS, Windows | CI
- PASS | uv run pytest | Review follow-up: 518 passed, 1 skipped (Windows junction test on Linux), including test_resumed_draft_criteria_must_survive and test_resumed_draft_criteria_ignore_rewrapping | Linux; Python 3.13.5 | implementer
- PASS | uv run python scripts/behavior.py check B12/B13 on the reviewer's real c2a78d7 agent run output | Both still PASS under the stricter B13 criteria check; no new agent run | Linux | implementer
- PASS | state.py check --neutral-dir template/.agents/skills/handoff/neutral and git diff --check | No violations; no whitespace errors | Linux | implementer
- NOT RUN | macOS and Windows CI for the review follow-up | Requires user commit and push; required before merge | Linux session only | implementer

## Review

Outcome: PASS
Reviewer: Claude Code/claude-opus-5-5, 2026-11-21
Reviewed at: c2a78d7eafa44a6acd2ab2630d7e1a8e6b408ea1
Contract: ce42a00f63cd312915bf9300491de8d7422c47d2
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | start-task SKILL.md step 3 and interview.md define local-only as a successful `git remote` with no names, stop on a failed check, and for new tasks and resumed drafts skip only fetch and upstream freshness checks with the one-line explanation; unchanged since de89d87; test_start_task_local_only_preflight passes; real B12 and B13 runs printed the skip line (reviewer).
- AC-2: VERIFIED | Confirm and hand off step 4 prints only `git commit -m "Start <goal>"` for local-only projects and restricts push and PR commands to remote-backed ones; test_start_task_final_commands_depend_on_remotes passes; real B12/B13 transcripts contain a commit command and no `git push` or `gh pr` command (reviewer).
- AC-3: VERIFIED | Remote-backed paragraph keeps target upstream, fetch, zero ahead/behind counts, and stops for missing upstream, ahead, behind, diverged, and failed fetch; clean-tree, branch identity and creation, ancestry, confirmation, and staging rules retained; covered by test_start_task_remote_preflight_still_blocks_unsafe_states and test_start_task_preserves_branch_and_contract_safeguards.
- AC-4: VERIFIED | start-task step 3, interview.md, and handoff Writing a task each honor a user-specified target, then existing `init.defaultBranch`, `main`, `master`, then ask; matches `resolve_default_branch` in src/newproj/state.py; test_local_only_target_resolution_agrees passes for all three.
- AC-5: VERIFIED | `scripts/start_task_behavior.py` runs `claude -p` non-interactively against B12 (local-only new task on main) and B13 (settled draft on existing add-min-length branch), then scripted checks in tests/fixtures/behavior/start_task.py require the skip line, no push/PR command, a commit command, only TASK.md and HANDOFF.md changed and staged, no new commits including reflogs, branch, target, activated contract, and state.py validity; no JUDGE items. Reviewer rerun: overall PASS. Pytest covers setup, passing and 14 failing verdicts per fixture, and the driver with a fake agent, without credentials; `uv run pytest` 514 passed, 1 skipped (reviewer); CI run 44878117963 green on Linux, macOS, Windows. D-009 supersedes D-008 only for this run.
- AC-6: VERIFIED | docs/ERRATA.md diff against the base is append-only (E-025); docs/DECISIONS.md diff is append-only (D-009); docs/spec.md, src/, and existing behavioral fixtures (B1 to B11) unchanged from the base.

Findings:
- Acceptance criteria were user-confirmed on 2026-11-20; AC-5 and `## Scope` were amended with user approval after the first review, and this record is against the amended contract (same `Contract:` hash as the first review).
- Implemented by Codex; reviewed by a different agent and model family (Claude Opus 5.5) in a fresh session. The automated AC-5 run drives the same model as this reviewer, which does not affect independence from the implementer.
- Non-blocking, recommended before acceptance: E-025 resolution item 4 still says "No additional behavioral fixture scenarios or manual tool runs are required for this change", which contradicts amended AC-5, D-009, and the new B12/B13 fixtures. E-025 is not yet merged to main; correct it or append a superseding erratum so the durable record matches what shipped.
- Non-blocking: tests/fixtures/behavior/B13/notes.md says the draft's settled criteria must survive, but the scripted check only requires `--min-length` in TASK.md; it does not compare the activated criteria with the draft's AC-1 to AC-3.
- Non-blocking, carried over: remote-backed projects whose only remote is not named `origin` still hit the pre-existing `origin/HEAD` lookup and `git push -u origin <branch>` template; unchanged by this task.

## Exact next steps

1. User commits the staged review record, then the follow-up, and pushes (commands printed in the session).
2. Run the user-invoked review skill in a fresh session with a different agent on the follow-up commit. The recorded PASS covers c2a78d7 only, and the follow-up was written by the reviewing agent's model, so a different agent or model family should review it.
3. Verify fresh macOS and Windows CI before acceptance. Open the PR only at acceptance.

## Blockers / open questions

- Review finding not fixed: remote-backed projects whose only remote is not named `origin` still use the `origin/HEAD` lookup and `git push -u origin <branch>`. Changing it is outside this contract (E-025 item 2: remote-backed target resolution remains unchanged); it needs a separate issue if wanted.

## Relevant decisions

- E-025 supersedes conflicting parts of E-018/E-019 for local-only interviews and aligns handoff target resolution.
- E-007 and E-008: the baseline records the updated main commit; acceptance criteria describe the finished result.
- E-026 supersedes E-025 resolution item 4 only.
- D-009 supersedes D-008 only for the approved local, automated B12/B13 agent run; existing interactive fixtures and recorded results remain unchanged.
