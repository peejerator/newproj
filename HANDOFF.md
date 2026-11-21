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

- PASS | uv run pytest tests/test_agent_content.py tests/test_render.py | 185 passed; AC-1 to AC-4 guidance, safeguards, and rendering at eb116c1 | Linux; Python 3.13.5 | reviewer
- PASS | uv run pytest | 518 passed, 1 skipped (Windows junction test on Linux), 1 expected Copier dirty-template warning; AC-5 at eb116c1 | Linux; Python 3.13.5; no agent credentials required | reviewer
- PASS | uv run python scripts/start_task_behavior.py /tmp/newproj-review-eb116c1-20261121 | AC-5: B12 PASS (3 turns), B13 PASS (2 turns), overall PASS; skip explained, commit-only output, only task files staged, no commits; B13 settled criteria preserved | Linux; Claude Code 2.1.330; claude-opus-5-5; synthetic projects; artifacts in output directory .behavior | reviewer
- PASS | git diff --check 0bc980c01b773a24a00160746a8896d088a3cad2 HEAD and complete review diff inspection | No whitespace errors; AC-6 append-only E-025/E-026 and D-009; frozen spec, CLI, dependencies, state code, existing fixtures and recorded results unchanged | Linux; eb116c1 | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux; eb116c1 | reviewer

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-11-21
Reviewed at: eb116c15d2e795c12b400c42dd2a0755ddba1c24
Contract: ce42a00f63cd312915bf9300491de8d7422c47d2
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Canonical start-task preflight and interview reference require a successful empty remote listing, stop on a failed check, and explain skipping only fetch and target-upstream freshness checks for new tasks and resumed drafts. Content tests and real B12/B13 output pass.
- AC-2: VERIFIED | Final-command guidance prints a commit alone for local-only projects and limits push/PR guidance to remote-backed projects. Content/render tests pass; real B12/B13 transcripts contain commit commands with no push or PR command.
- AC-3: VERIFIED | Complete instruction diff preserves target-upstream, fetch and zero ahead/behind requirements whenever any remote exists, with explicit stops for missing upstream, ahead, behind, divergence and fetch failure. Clean-tree, branch identity/creation/reuse, resumed ancestry, explicit confirmation and staging safeguards remain. Safeguard content tests pass; B12/B13 exercise applicable local rules.
- AC-4: VERIFIED | start-task, interview reference and handoff Writing a task agree: honor an explicit target, otherwise existing init.defaultBranch, then existing main, then existing master, then ask. Matches the unchanged state resolver's local fallback; all three content tests and rendering checks pass.
- AC-5: VERIFIED | Reviewer executed the single-command non-interactive driver at HEAD: B12 PASS, B13 PASS, overall PASS. Scripted checks verify explained skip, commit-only output, task-file-only changes and staging, no commits including reflogs, agreed branch/target and valid activated state. B13 also requires the settled draft criteria, normalizing whitespace; negative and rewrapping tests pass. Full pytest: 518 passed, 1 skipped; the suite uses synthetic agent responses and does not launch a credentialed agent. D-009 documents the approved local-only headless exception.
- AC-6: VERIFIED | Complete base diff shows only appended E-025/E-026 in ERRATA and D-009 in DECISIONS. E-025 documents exceptions to E-018/E-019; E-026 supersedes its obsolete testing statement. Frozen spec, existing accepted entries, CLI, dependencies, state code and prior behavioral fixtures/results are unchanged.

Findings:
- No blocking findings. Both actionable findings from the c2a78d7 review are resolved: E-026 supersedes E-025 item 4, and B13 checks the settled criteria with regression coverage.
- Acceptance criteria were user-confirmed on 2026-11-20; the contract records the subsequent user-approved clarification to AC-5 and Scope.
- Fresh reviewer session, with no implementation by this agent. The original work is recorded as implemented by Codex, sharing this reviewer's tool/model family; its exact model is not recorded. The latest follow-up was implemented by Claude Code, a different model family. Earlier independent Claude review provides additional evidence for the original changes.
- Integration gate: CI run 44879974895 on the exact reviewed commit has passed on Linux and macOS; Windows is still running. Verify its success before merge: https://github.com/peejerator/newproj/actions/runs/44879974895.
- Non-blocking, pre-existing and outside this contract: remote-backed projects with no remote named origin still use origin/HEAD lookup and git push -u origin in the existing guidance. E-025 intentionally leaves remote-backed target resolution unchanged.

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
