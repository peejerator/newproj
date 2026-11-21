# Handoff

Last updated: 2026-11-21
Branch: fix-46-remote-name
Task: standard

## Status

in progress

## Completed

- AC-1: `src/newproj/state.py` adds `configured_remotes`, `select_remote`, and `set_head_command`; `resolve_default_branch` runs steps 1 and 2 against the selected remote, returns unknown (step 4, no local fallback) when remotes exist but none is selected, and resolves `origin` repositories as before. Template copy synced (byte-identical).
- AC-2: hints and fixes in `state.py`, `doctor.py`, and `adopt.py` name the selected remote; with no remote the fix is "add a remote and run `git remote set-head <remote> --auto`".
- AC-3: `adopt.set_head` runs `git remote set-head <remote> --auto` for the selected remote only.
- AC-4, AC-5: `handoff` Writing a task uses the selection rule and asks when unresolved; `start-task` prints `git push -u <remote> <branch>` (target branch's configured remote); `accept` prints `git push <remote> --delete <task branch>` (task branch's configured remote). Pointer frontmatter unchanged.
- AC-6: E-027 appended to `docs/ERRATA.md`, including the follow-up decision below.
- Review finding 1 (push-only remotes): `configured_remotes` now enumerates remotes with `git remote`, so a remote with `pushurl` but no `url` is selected; regression test `test_push_only_remote_step_1`. `git remote` lists names alphabetically, so the several-remotes message lists them in that order.
- AC-7: tests added in `tests/test_state.py`, `tests/test_doctor.py`, `tests/test_adopt.py`, `tests/test_agent_content.py`; existing no-remote assertions now expect `<remote>`.

## Current working area

- `src/newproj/state.py`, `template/.agents/skills/resume/scripts/state.py`, `src/newproj/doctor.py`, `src/newproj/adopt.py`
- `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/start-task/SKILL.md`, `template/.agents/skills/accept/SKILL.md`
- `docs/ERRATA.md`
- `tests/test_state.py`, `tests/test_doctor.py`, `tests/test_adopt.py`, `tests/test_agent_content.py`

## Validation

- PASS | uv run pytest | 538 passed, 1 skipped, after the finding 1 fix; includes push-only remote regression (AC-1, AC-2, AC-7) | Linux | implementer
- PASS | git diff docs/spec.md docs/DECISIONS.md; git diff docs/ERRATA.md | spec and decisions unchanged; ERRATA diff is additions only (AC-6) | Linux | implementer
- NOT RUN | CI on Linux, macOS, and Windows | skipped: runs after the user commits and pushes | | implementer
- PASS | uv run pytest | 538 passed, 1 skipped (Windows-only junction test); required remote cases, push-only regression, integration and skill content covered (AC-1 to AC-5, AC-7) | Linux, Python 3.13.5; 5a9bfe9 | reviewer
- PASS | Push-only remote discovery with a cached remote HEAD | configured_remotes lists upstream after its url is unset; the regression test resolves develop at step 1 without an add-a-remote hint (AC-1, AC-2) | Isolated local repositories; full suite on 5a9bfe9 | reviewer
- PASS | Snapshot invariants and git diff --check 1631ad2925a99c48ae43c0cbc6f93e9f0c0ecd83...HEAD | state.py copies and pointer frontmatter identical; prior errata byte-identical; only E-027 appended; spec, decisions and new.py unchanged; LF and whitespace checks pass (AC-1, AC-5, AC-6) | Recorded base to 5a9bfe9 | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux; uv cache access required outside sandbox | reviewer
- PASS | CI on Linux and macOS | Both jobs passed tests and the Python 3.9 state checks on the reviewed commit (AC-7) | https://github.com/peejerator/newproj/actions/runs/44884139677 | CI
- PASS | CI on Windows | Windows job passed on 0a4e142 (reviewed commit, before the finding 1 fix) (AC-7) | https://github.com/peejerator/newproj/actions/runs/44884139677 | CI
- PASS | adopt.set_head existing-HEAD guard | No set-head execution when upstream already has a symbolic HEAD; guarded run would raise if called (AC-3) | Isolated temporary Git repository on Linux | reviewer
- PASS | CI on Linux, macOS, and Windows | All jobs passed the full suite and Python 3.9 state report/check on 5a9bfe9e80fc10c014633be7b11da4764721b47b (AC-7) | https://github.com/peejerator/newproj/actions/runs/44952823614 | CI

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-11-21
Reviewed at: 5a9bfe9e80fc10c014633be7b11da4764721b47b
Contract: 89a1123efdfb9202e9ab98ce491d5e97c6045e7b
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Complete resolver and identical template copy implement origin, sole remote, sole symbolic remote HEAD, or no selection. Reviewer-executed tests cover steps 1 and 2, offline fallback, ambiguous remotes with zero or two HEADs, a sole HEAD, origin precedence, and push-only remote discovery. Ambiguous remotes return step 4 without local fallback.
- AC-2: VERIFIED | Complete state, doctor and adopt paths name the selected remote in their hints. Reviewer-executed unit and integration tests cover named-remote, unreachable, ambiguous and no-remote fixes; the push-only regression no longer advises adding a remote.
- AC-3: VERIFIED | adopt.set_head selects the same remote and invokes set-head only when its symbolic HEAD is missing. Integration tests verify upstream set-head and no selected/no configured remote; an independent guarded check verifies skipping an existing upstream HEAD.
- AC-4: VERIFIED | The complete handoff skill's added target-resolution text matches amended AC-1, explicitly asks when selection or default resolution fails, and preserves local-only and unreachable-remote safeguards. Content tests pass.
- AC-5: VERIFIED | Complete start-task and accept skills substitute the target branch's and task branch's configured remotes into push and delete commands respectively. Content tests pass; all pointer frontmatter is byte-identical to canonical frontmatter. Remaining origin mentions are selection rules or examples.
- AC-6: VERIFIED | E-027 records the amended selection rule, spec sections 4 and 20.2 step 3, all three skills, and the exact limited E-025 supersession. Byte comparisons confirm earlier errata, spec and decisions unchanged and E-027 is the sole appended entry.
- AC-7: VERIFIED | All required automated cases are present; reviewer-executed full suite passed (538 passed, 1 Windows-only test skipped on Linux). CI run 44952823614 passed Linux, macOS and Windows tests plus Python 3.9 state checks on the exact reviewed commit.

Findings:
- No blocking findings. Previous finding 1 is resolved by git remote discovery and its passing push-only regression. Previous finding 2 is resolved by the committed, user-authorized AC-1 amendment; current code, skills and E-027 agree with it. Windows CI is now complete on the corrected commit.
- Acceptance criteria were user-confirmed on 2026-11-21, as recorded in TASK.md, which also records authorization for the follow-up amendment.
- This is a fresh reviewer session, independent of implementation in this conversation. The implementer's model is not recorded, so model-family independence is not established.

## Exact next steps

1. The user commits the finding 1 fix and the AC-1 amendment and pushes; confirm CI on Linux, macOS, and Windows (AC-7).
2. Re-review by a different agent (the `review` skill).
3. Acceptance via the `accept` skill.

## Blockers / open questions

## Relevant decisions

- Remote selection rule and printed push commands: `TASK.md`, `## Context`, decisions 2 and 3, and the follow-up decision (AC-1 amended).
- Follow-up user decision (2026-11-21, this session): decision 2's fix for several remotes without `origin` (`git remote set-head <remote> --auto`) could never take effect under the rule as written, so the user chose to extend selection: with several remotes and none named `origin`, select the one remote whose `refs/remotes/<remote>/HEAD` is set, if exactly one has it. Recorded in E-027 item 1. Review finding 2 resolved: the user confirmed the extension and authorized amending `TASK.md` AC-1 to match (2026-11-21).
- E-027 supersedes E-025 resolution item 2's "Remote-backed target resolution remains unchanged".
