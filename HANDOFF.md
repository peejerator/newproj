# Handoff

Last updated: 2026-11-21 by Codex
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
- AC-6: E-025 appends the approved exceptions to E-018/E-019.

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

## Review

Outcome: FAIL
Reviewer: Claude Code/claude-opus-5-5, 2026-11-20
Reviewed at: de89d87c152bb6f4c578363730dc276dfc857e84
Contract: ce42a00f63cd312915bf9300491de8d7422c47d2
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: CI-confirmed

- AC-1: VERIFIED | start-task SKILL.md step 3 defines local-only as a successful `git remote` with no names, stops on a failed check, and for new tasks and resumed drafts skips only fetch and upstream freshness checks with the one-line explanation; interview.md repeats it; test_start_task_local_only_preflight passes (reviewer, CI).
- AC-2: VERIFIED | Confirm and hand off step 4 prints only `git commit -m "Start <goal>"` for local-only projects and restricts push and further push or PR commands to remote-backed projects; template AGENTS.md.jinja adds no push or PR requirement; test_start_task_final_commands_depend_on_remotes passes.
- AC-3: VERIFIED | Remote-backed paragraph keeps target upstream, fetch, zero ahead/behind counts, and stops for missing upstream, ahead, behind, diverged, and failed fetch; clean-tree, branch identity and creation, ancestry, confirmation, and staging text unchanged or restated; covered by content tests.
- AC-4: VERIFIED | start-task step 3, interview.md, and handoff Writing a task each honor a user-specified target, then existing `init.defaultBranch`, `main`, `master`, then ask; matches `resolve_default_branch` step 3 in src/newproj/state.py; test_local_only_target_resolution_agrees passes for all three.
- AC-5: UNSATISFIED | Amended AC-5 requires an automated non-interactive agent run against local-only new-task and resumed-draft fixtures; none exists at HEAD (no fixture under tests/fixtures/behavior/ for start-task, no runner in scripts/behavior.py). The content-test part holds: seven new content tests and two rendered-equality assertions cover local-only guidance and retained remote safeguards; `uv run pytest` 466 passed, 1 skipped (reviewer); CI run 44685446259 green on Linux, macOS, Windows.
- AC-6: VERIFIED | docs/ERRATA.md diff is append-only (E-025); docs/spec.md, docs/DECISIONS.md, src/, and tests/fixtures/ unchanged from the base.

Findings:
- Acceptance criteria were user-confirmed on 2026-11-20; the user approved amending AC-5 and `## Scope` after the first review (TASK.md `## Context` correction), and this record is against the amended contract.
- Remaining work (AC-5): add a `docs/DECISIONS.md` entry superseding D-008 for the automated run (user decisions in TASK.md `## Context`: `claude -p`, `codex exec`, or both; local only, no CI secret); add local-only new-task and resumed-draft fixtures; add a single command that runs the agent non-interactively and prints PASS or FAIL from scripted checks (skip line, no push or PR command, only TASK.md and HANDOFF.md staged, no commit); add pytest coverage for the fixtures' setup and check; record a real run's result under `## Validation`.
- AC-1 to AC-4 and AC-6 remain verified at de89d87 and need no rework.
- Implemented by Codex; reviewed by a different agent and model family (Claude Opus 5.5) in a new session.
- Non-blocking: remote-backed projects whose only remote is not named `origin` still hit the pre-existing `origin/HEAD` lookup (ask the user) and the `git push -u origin <branch>` template; unchanged by this task and consistent with "remote-backed target resolution remains unchanged".
- Non-blocking: the new tests are phrase-presence content checks, as the user chose (automated tests only, no behavioral fixtures); they guard wording, not agent behavior.

## Exact next steps

1. User commits the staged follow-up with `git commit -m "Automate local-only start-task behavior checks (#40)"` and pushes with `git push`.
2. Run the user-invoked review skill in a fresh independent session on the committed fix. The recorded FAIL describes de89d87 under the amended contract; its remaining AC-5 finding is addressed by this follow-up, pending re-review.
3. Verify fresh macOS and Windows CI before acceptance. Open the PR only at acceptance.

## Blockers / open questions

- None.

## Relevant decisions

- E-025 supersedes conflicting parts of E-018/E-019 for local-only interviews and aligns handoff target resolution.
- E-007 and E-008: the baseline records the updated main commit; acceptance criteria describe the finished result.
- D-009 supersedes D-008 only for the approved local, automated B12/B13 agent run; existing interactive fixtures and recorded results remain unchanged.
