# Task

Status: active
Tier: standard
Task ID:
Base commit: 1631ad2925a99c48ae43c0cbc6f93e9f0c0ecd83
Target branch: main
Issue: #46
PR:

## Goal

Stop assuming the remote is named `origin`: `state.py`, `newproj doctor`, `newproj adopt`, and the `handoff`, `start-task`, and `accept` skills resolve which remote to use, so a project whose only remote has another name gets a consistent target branch and push commands that name a remote that exists.

## Context

Agreed task branch: `fix-46-remote-name`. Target branch: `main`.

Acceptance criteria confirmed by the user: 2026-11-21

User decisions (Round 1, 2026-11-21, all recommendations accepted):

1. Resolve the remote rather than documenting `origin` as a requirement.
2. Remote selection for default-branch resolution: `origin` if configured (even alongside other remotes); otherwise the only configured remote; with several remotes and none named `origin`, the default branch is unknown (spec section 4 step 4) and the message names the fix (`git remote set-head <remote> --auto`, or a user-specified target), and the skills ask the user. Steps 1 and 2 use `refs/remotes/<remote>/HEAD` and `git ls-remote --symref <remote> HEAD` for the selected remote. `branch.<target>.remote` is not used for this, because the target is what is being resolved.
3. Printed push commands: `start-task` pushes with `git push -u <remote> <branch>`, where `<remote>` is the target branch's configured remote (`git config branch.<target>.remote`; preflight already requires the target's upstream). `accept` deletes with `git push <remote> --delete <task branch>`, where `<remote>` is the task branch's configured remote. With `origin`, the commands are unchanged.
4. Code scope: `src/newproj/state.py` and its template copy, `doctor` and `adopt` hints naming the selected remote, and `adopt` running `git remote set-head <remote> --auto` for the selected remote. `newproj new` is unchanged (it always creates `origin`).
5. Record the change as a new erratum, E-027, generalizing `origin` to the selected remote in spec sections 4 and 20.2 step 3 and in the skills, superseding only E-025 resolution item 2's "Remote-backed target resolution remains unchanged".
6. Validation is automated: unit, integration, and content tests, the full suite, and CI. No new agent behavioral fixture.
7. Standard tier. Not formal risk. Independent review by a different agent is expected before acceptance, because the task changes skill (instruction-file) content.

Facts from the repository: spec section 4 (default branch) names `origin` in steps 1, 2, and 4; `resolve_default_branch` (`src/newproj/state.py`) reads only `origin` and is used by `doctor` and `adopt`; `adopt.py` runs `set-head` only when `origin` exists (spec 20.2 step 3); `new.py` creates `origin`.

User decision (follow-up, 2026-11-21): under decision 2 as first written, the suggested fix `git remote set-head <remote> --auto` could never take effect, so selection is extended: with several remotes and none named `origin`, select the one remote whose `refs/remotes/<remote>/HEAD` is set, if exactly one has it. AC-1 amended by the user's authorization, 2026-11-21, resolving review finding 2.

## Scope

- Implement the decisions above in `src/newproj/state.py` (then `uv run python scripts/sync_state.py`), `src/newproj/doctor.py`, `src/newproj/adopt.py`, and the canonical skills under `template/.agents/skills/` (`handoff`, `start-task` and its interview reference where relevant, `accept`).
- Append E-027 to `docs/ERRATA.md`. Do not edit `docs/spec.md` or rewrite E-025.
- Add tests in `tests/`.
- Out of scope: `newproj new`, other doctor checks, issue #44, and other remote-related behavior not listed here.
- The user makes every commit: stage the work and print the commit and push commands (AGENTS.md).

## Acceptance criteria

- AC-1: `resolve_default_branch` (in `src/newproj/state.py` and its byte-identical template copy) selects the remote as `origin` if configured, otherwise the only configured remote, otherwise (several remotes, none named `origin`) the one remote whose `refs/remotes/<remote>/HEAD` is set, otherwise none. Steps 1 and 2 use the selected remote's `refs/remotes/<remote>/HEAD` and `git ls-remote --symref <remote> HEAD`. When remotes exist but none is selected, it reports the default branch as unknown (step 4) with a fix naming `git remote set-head <remote> --auto` or a user-specified target, and does not fall back to local branches as if there were no remote. Repositories with an `origin` remote resolve exactly as before.
- AC-2: Hints and fixes printed by `state.py`, `newproj doctor`, and `newproj adopt` name the selected remote rather than `origin`. With no remote configured, the fix tells the user to add a remote and run `git remote set-head <remote> --auto`, without requiring the name `origin`.
- AC-3: `newproj adopt` runs `git remote set-head <remote> --auto` for the selected remote when its `refs/remotes/<remote>/HEAD` is missing, and does not run it when no remote is selected.
- AC-4: The `handoff` skill's Writing a task resolves the remote-backed default target with the same remote selection rule as AC-1 and asks the user when it does not resolve.
- AC-5: The `start-task` skill's remote-backed command block pushes with `git push -u <remote> <branch>`, naming the target branch's configured remote, and the `accept` skill's final block deletes the task branch with `git push <remote> --delete <task branch>`, naming the task branch's configured remote. Neither skill, nor the `handoff` skill, hard-codes `origin` as the only remote; `origin` appears only as part of the selection rule or as an example. Root pointer skills keep frontmatter identical to the canonical skills.
- AC-6: `docs/ERRATA.md` ends with E-027, which records the remote selection rule, its application to spec sections 4 and 20.2 step 3 and the three skills, and supersedes only E-025 resolution item 2's "Remote-backed target resolution remains unchanged". `docs/spec.md` and earlier errata entries are unchanged.
- AC-7: Automated tests cover: a single non-`origin` remote resolving at step 1, at step 2, and offline at step 3; several remotes with none named `origin` (unknown); `origin` plus another remote (`origin` selected); `adopt` running `set-head` for a non-`origin` remote; and the skill text for AC-4 and AC-5. `uv run pytest` passes, and CI passes on Linux, macOS, and Windows.

## Relevant areas

- `src/newproj/state.py`, `template/.agents/skills/resume/scripts/state.py`, `scripts/sync_state.py`
- `src/newproj/doctor.py`, `src/newproj/adopt.py`
- `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/start-task/SKILL.md`, `template/.agents/skills/start-task/references/interview.md`, `template/.agents/skills/accept/SKILL.md`
- `docs/ERRATA.md` (E-025)
- `tests/test_state.py`, `tests/test_adopt.py`, `tests/test_doctor.py`, `tests/test_agent_content.py`
- Spec sections 4 (Default branch, lines around "Default branch, wherever this spec uses the term") and 20.2

## Validation

- `uv run pytest`
- `uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral`
- CI on Linux, macOS, and Windows

## Do not change

- `docs/spec.md`
- Existing entries in `docs/ERRATA.md` and `docs/DECISIONS.md`
- `newproj new` behavior
- Behavior for repositories with an `origin` remote

## Open questions
