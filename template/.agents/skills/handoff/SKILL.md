---
name: handoff
description: Use when ending a session of standard or formal work, before switching tool, agent, or machine, when lightweight work is interrupted with the work unfinished, or when the user asks to update the handoff or to mark the task complete.
---

# Handoff

Bring `HANDOFF.md` up to date so that an agent with no access to this session can continue correctly. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Steps

1. If the work is unfinished and there is no active task (`TASK.md` missing or `Status: none`), escalate to standard: write `TASK.md` first, as described under Writing a task.
2. Reconcile the repository against `TASK.md`: compare it and the current `HANDOFF.md` with `git status --short`, the diff, and recent commits (the `resume` skill lists the signals).
3. Update `HANDOFF.md` in the format below. Record outcomes, not activities, and keep to the size guideline.
4. Record validation in the entry format below, referencing acceptance criteria by ID.
5. Move findings that are durable and likely to be reused to `docs/research/` or `docs/specs/`, and cite them in `HANDOFF.md` instead of copying them.
6. Record exact next steps and the relevant decision IDs from `docs/DECISIONS.md`.
7. Record any concern about the task itself under `## Blockers / open questions`. Never edit an active `TASK.md`.
8. Check the mechanical rules: run `uv run --no-project .agents/skills/resume/scripts/state.py check` from the repository root, or, where `uv` is unavailable, `python3 .agents/skills/resume/scripts/state.py check` on macOS and Linux or `py -3 .agents/skills/resume/scripts/state.py check` on Windows. It is read-only and prints each violation with its file and line. Fix violations in `HANDOFF.md`. Record a violation in an active `TASK.md` under `## Blockers / open questions` instead of fixing it. If no Python is available, check `HANDOFF.md` against the format and rules below by hand.
9. Do not commit unless the user asks. If the user makes every commit, stage the files and print the commit command instead. If the user is switching machines, offer to commit to a short-lived task branch and push (protocol, Session end and switching), because an uncommitted handoff does not travel.

## `HANDOFF.md` format

```markdown
# Handoff

Last updated: YYYY-MM-DD by <tool/model>
Branch: <current branch>
Task: <standard | none>
Environment: <macOS | Windows | CI | remote agent | other>

## Status

<one status value>

## Completed

- <outcome, citing acceptance criteria by ID where they apply>

## Current working area

- `path/to/file`

## Validation

- <validation entry>

## Review

Outcome: none

## Exact next steps

1. <concrete action another agent can take without this session>

## Blockers / open questions

- <concern, or None.>

## Relevant decisions

- <decision ID>
```

Rules:

- The eight `##` headings are required and spelled exactly as shown. Never rename, merge, or remove them. Sections may be empty, except that `## Review` always contains an `Outcome:` line.
- `Last updated:`, `Branch:`, and `Task:` are required; `Environment:` is optional. `Task:` is `standard` while a task is in progress and `none` otherwise.
- `## Status` holds exactly one of these values and nothing else: `none` (no task), `not started`, `in progress`, `blocked`, `validating` (implementation done, checks such as CI still running), `complete` (the implementer's claim that the Definition of Done holds). Put explanations in the other sections.
- `## Current working area` lists the files and modules expected to change. Dirty paths outside it are a reconciliation signal for the next agent.
- `## Review` is written only by an independent reviewer, in the format in the `review` skill. As the implementer, leave it exactly as you found it, except that writing a new task resets it to `Outcome: none`.

## Size guideline

`HANDOFF.md` is read in full by every resuming agent, so keep it short enough to read in one pass; a few dozen lines is typical.

- `## Completed` lists outcomes by acceptance criterion ID, one line each (`AC-3: handoff skill restructured`), not a narrative of what was done.
- `## Validation` keeps one current entry per check. Replace an entry when the check is rerun; do not append history.
- Long inventories, such as a list of every rewritten line, go in the commit message or a task-scoped file that `HANDOFF.md` cites.

## Validation entries

```text
<PASS | FAIL | NOT RUN> | <exact command or check> | <concise result> | <environment and inputs, when relevant> | <provenance>
```

- Provenance is exactly one of `implementer` (run and reported by the implementing agent), `reviewer` (run by an independent reviewer during review), or `CI` (a CI run on the exact commit, cited by run URL or ID). It names the role, never the tool or model.
- Reference acceptance criteria by ID, for example `PASS | uv run pytest tests/test_export.py | 12 passed, covers AC-2 | macOS | implementer`.
- A `NOT RUN` entry always states why, distinguishing an environment limitation (`environment: no Xcode on Windows`) from a choice (`skipped: slow suite, run in CI`). A check the environment cannot run is never recorded as `FAIL`.
- Where results depend on external runtime state, the environment field names it (model version, dataset snapshot ID, schema version), never the private data itself.


## Writing a task

When the user asks for a new task, use the user-invoked `start-task` skill. This section remains its format reference and the path for escalating unfinished lightweight work. Write `TASK.md` with these lines and headings, spelled exactly:

```markdown
# Task

Status: active
Tier: standard
Task ID:
Base commit: <literal output of git rev-parse HEAD>
Target branch: <the branch the work will merge into>
Issue:
PR:

## Goal

## Context

## Scope

## Acceptance criteria

## Relevant areas

## Validation

## Do not change

## Open questions
```

- During a `start-task` interview, use this format with `Status: draft`; leave `Task ID:`, `Base commit:`, and `Target branch:` empty until activation. The remaining rules describe writing an active standard task, either after confirmation through `start-task` or on escalation.
- `Base commit:` is the pre-implementation code state, copied from the output of `git rev-parse HEAD`, never typed. If implementation commits already exist, use the commit before the first of them and say so under `## Context`. The `review` skill diffs against it.
- `Target branch:` is the default branch unless the user names another. Find it with `git symbolic-ref --short refs/remotes/origin/HEAD` and drop the `origin/` prefix; if that fails, ask the user.
- Leave `Task ID:` empty; only formal activation sets it.
- Take the goal and scope from the user's request.
- Each acceptance criterion has an ID (`AC-1`, `AC-2`, ...) and describes a checkable property of the finished work at `HEAD`, because the reviewer judges every criterion at the reviewed commit. Session instructions (stop points, handoff requirements, who commits, which branch) go under `## Scope`, never under `## Acceptance criteria`.
- If the work is formal-risk, follow the protocol's Workflow tiers rule: the user confirms the acceptance criteria before implementation continues.
- Then write `HANDOFF.md` in the format above with `Task: standard`, the current branch, a status, and `Outcome: none` under `## Review`.
- From this point the task is active: do not edit `TASK.md` again.

## Marking the task complete

1. Check the Definition of Done in `docs/AGENT_PROTOCOL.md`, condition by condition. Record each acceptance criterion's evidence under `## Validation` and any exception under `## Blockers / open questions`.
2. List any claim about system behavior you could not verify under `## Blockers / open questions`, so the reviewer checks it against the code.
3. Set `## Status` to `complete`, or to `validating` while checks such as CI are still running.
4. Recommend an independent review with the `review` skill, run by the user in a different agent or model. It is expected when the work moves, rewrites, or removes safety rules or instruction-file content, and required for formal-risk work. The implementation must be committed before the review starts.
5. If the branch contains WIP or `checkpoint(` commits, remind the user to squash them before merging.
6. Acceptance belongs to the user and follows the `accept` skill, which resets `TASK.md` and `HANDOFF.md` to the neutral state on the task's branch before it is merged.
