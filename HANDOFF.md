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
- PASS | uv run pytest | 537 passed, 1 skipped; requested remote cases, adopt/doctor integration, skill content, and pointer frontmatter covered (AC-1 to AC-5, AC-7) | Linux, Python 3.13.5 | reviewer
- FAIL | Push-only remote discovery with a cached remote HEAD | Git lists upstream and can push to it, but configured_remotes returns no remotes; default resolution is unknown and incorrectly says to add a remote (AC-1, AC-2) | Isolated local repositories; upstream has pushurl and fetch configuration but no url | reviewer
- PASS | Snapshot invariants and git diff --check 1631ad2925a99c48ae43c0cbc6f93e9f0c0ecd83...HEAD | state.py copies byte-identical; earlier errata preserved byte for byte; spec, decisions, and new.py unchanged; no whitespace errors (AC-6) | Recorded base to reviewed HEAD | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux; uv cache access required outside sandbox | reviewer
- PASS | CI on Linux and macOS | Both jobs passed tests and the Python 3.9 state checks on the reviewed commit (AC-7) | https://github.com/peejerator/newproj/actions/runs/44884139677 | CI
- NOT RUN | Completed CI on Windows | environment: the Windows job is still running; its final result is unavailable (AC-7) | https://github.com/peejerator/newproj/actions/runs/44884139677 | reviewer
- PASS | CI on Windows | Windows job passed on 0a4e142 (reviewed commit, before the finding 1 fix) (AC-7) | https://github.com/peejerator/newproj/actions/runs/44884139677 | CI

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-11-21
Reviewed at: 0a4e1429a6ac53fff75f2aa95300471fd7d6a495
Contract: a8e8e1c6ed7129776bf72abb6f62215d57e401e2
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: UNSATISFIED | URL-backed remote cases pass, and the template copy is byte-identical. However, configured_remotes omits configured remotes without remote.<name>.url, including working push-only remotes listed by git remote; their cached HEAD is ignored. See finding 1 and the contract discrepancy in finding 2.
- AC-2: UNSATISFIED | Named-remote and no-remote tests pass, but the push-only-remote reproduction prints an add-a-remote fix even though upstream exists and has a usable cached HEAD. This follows from finding 1.
- AC-3: VERIFIED | adopt.set_head uses the selected remote, skips an existing symbolic HEAD, and does nothing without a selected remote; reviewer-executed integration tests cover non-origin and unselected/no-remote cases.
- AC-4: INFERRED | The complete handoff skill and content tests agree with E-027's reported follow-up selection rule and ask when unresolved. This differs from AC-1's rule incorporated by AC-4; direct user confirmation of the amendment is pending (finding 2).
- AC-5: VERIFIED | Complete start-task and accept skills read the target/task branch's configured remote respectively and substitute it into the push/delete block; tests verify commands, origin usage, and identical pointer frontmatter.
- AC-6: INFERRED | E-027 is appended and covers the required sections and skills, with only the requested E-025 sentence superseded. Earlier errata, spec, and decisions are unchanged. Its expanded selection rule awaits resolution of finding 2.
- AC-7: INFERRED | All requested automated cases exist and the local suite passed (537 passed, 1 skipped). Linux and macOS CI passed on the exact reviewed commit; Windows CI is still running.

Findings:
1. [P2] Enumerate all configured remotes, including push-only remotes (`src/newproj/state.py:327-335` and the identical template copy). Reproduced in isolated repositories: create and push develop to upstream, set upstream/HEAD, set remote.upstream.pushurl to its existing URL, then unset remote.upstream.url. Git still lists upstream and successfully pushes to it, and upstream/HEAD points to the existing upstream/develop ref. configured_remotes returns [], so state.py reports unknown at step 4 and advises adding a remote instead of resolving develop at step 1. Doctor and adopt share this discovery path. Enumerate Git's remotes consistently with the skills' git remote check and add regression coverage for a remote without a url key.
2. Open user decision: TASK.md AC-1 requires several remotes without origin to remain unknown; implementation, tests, the handoff skill, and E-027 instead select the sole remote with a remote HEAD. Relevant decisions reports this was approved on 2026-11-21, but the active contract does not contain the amendment. The reviewer asked the user whether to apply the reported follow-up; that question remains open. Do not infer approval from the report or edit the active contract as the reviewer. The remote-discovery failure in finding 1 applies under either rule.
3. Complete Windows CI verification on the reviewed or corrected commit before marking AC-7 VERIFIED.
4. Acceptance criteria were user-confirmed on 2026-11-21, as recorded in TASK.md. This is a fresh reviewer session; the implementer's model is not recorded, so model-family independence is not established.

## Exact next steps

1. The user commits the finding 1 fix and the AC-1 amendment and pushes; confirm CI on Linux, macOS, and Windows (AC-7).
2. Re-review by a different agent (the `review` skill).
3. Acceptance via the `accept` skill.

## Blockers / open questions

## Relevant decisions

- Remote selection rule and printed push commands: `TASK.md`, `## Context`, decisions 2 and 3, and the follow-up decision (AC-1 amended).
- Follow-up user decision (2026-11-21, this session): decision 2's fix for several remotes without `origin` (`git remote set-head <remote> --auto`) could never take effect under the rule as written, so the user chose to extend selection: with several remotes and none named `origin`, select the one remote whose `refs/remotes/<remote>/HEAD` is set, if exactly one has it. Recorded in E-027 item 1. Review finding 2 resolved: the user confirmed the extension and authorized amending `TASK.md` AC-1 to match (2026-11-21).
- E-027 supersedes E-025 resolution item 2's "Remote-backed target resolution remains unchanged".
