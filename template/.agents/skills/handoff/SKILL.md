---
name: handoff
description: Use when ending a session of standard or formal work, before switching tool, agent, or machine, when lightweight work is interrupted with the work unfinished, or when the user asks to update the handoff or to mark the task complete.
---

# Handoff

Bring `HANDOFF.md` up to date so that an agent with no access to this session can continue correctly. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Steps

1. If the work is unfinished and there is no active task (`TASK.md` missing or `Status: none`), escalate to standard: write `TASK.md` first, as described under Writing a task.
2. Reconcile the repository against `TASK.md`: compare it and the current `HANDOFF.md` with `git status --short`, the diff, and recent commits (the `resume` skill lists the signals).
3. Update `HANDOFF.md` in the format below. Record outcomes, not activities.
4. Record validation in the entry format below, referencing acceptance criteria by ID.
5. Move findings that are durable and likely to be reused to `docs/research/` or `docs/specs/`, and cite them in `HANDOFF.md` instead of copying them.
6. Record exact next steps and the relevant decision IDs from `docs/DECISIONS.md`.
7. Record any concern about the task itself under `## Blockers / open questions`. Never edit an active `TASK.md`.
8. Do not commit unless the user asks. If the user is switching machines, offer to commit to a non-default branch and push, because an uncommitted handoff does not travel.

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

## Validation entries

```text
<PASS | FAIL | NOT RUN> | <exact command or check> | <concise result> | <environment and inputs, when relevant> | <provenance>
```

- Provenance is exactly one of `implementer` (run and reported by the implementing agent), `reviewer` (run by an independent reviewer during review), or `CI` (a CI run on the exact commit, cited by run URL or ID). It names the role, never the tool or model.
- Reference acceptance criteria by ID, for example `PASS | uv run pytest tests/test_export.py | 12 passed, covers AC-2 | macOS | implementer`.
- A `NOT RUN` entry always states why, distinguishing an environment limitation (`environment: no Xcode on Windows`) from a choice (`skipped: slow suite, run in CI`). A check the environment cannot run is never recorded as `FAIL`.
- Where results depend on external runtime state, the environment field names it (model version, dataset snapshot ID, schema version), never the private data itself.

## Review record

`## Review` records the latest independent review and is written only by the reviewer, never by the agent that implemented the work. As the implementer, leave it exactly as you found it, except that writing a new task resets it to `Outcome: none`. A reviewer, who must be a different agent or model, writes:

```markdown
Outcome: <PASS | FAIL | INCONCLUSIVE>
Reviewer: <tool/model>, YYYY-MM-DD
Reviewed at: <literal output of git rev-parse HEAD>
Contract: <literal output of git hash-object TASK.md>
Working tree clean at review: <yes | no>
Baseline: <default-branch diff | reduced confidence>
Artifact coverage: <complete | partial (what was missing)>
Validation provenance: <reviewer-executed | CI-confirmed | implementer-reported only | none>

- AC-1: <VERIFIED | INFERRED | UNSATISFIED | NOT CHECKED> | <evidence>

Findings:
- <finding>
```

- `Reviewed at:` and `Contract:` are copied from command output, never typed.
- VERIFIED: supported by the complete relevant code and, for runtime behavior, by `reviewer` or `CI` checks. INFERRED: probably satisfied, but the evidence is indirect or implementer-reported only. UNSATISFIED: demonstrably not met. NOT CHECKED: evidence missing, truncated, or not runnable.
- PASS: every criterion VERIFIED, artifact coverage complete, no blocking findings. FAIL: at least one criterion UNSATISFIED, or a blocking regression found. INCONCLUSIVE: anything else.
- After FAIL or INCONCLUSIVE, the reviewer puts the remaining work in `## Exact next steps` and `## Blockers / open questions` and sets `## Status` to `in progress`. The reviewer does not modify source code or `TASK.md`.
- For a standard task the implementer wrote the criteria, so the reviewer notes that the evidence is weaker.

## Writing a task

Use this when escalating lightweight work, or when the user asks for a standard task. Write `TASK.md` with these lines and headings, spelled exactly:

```markdown
# Task

Status: active
Tier: standard
Task ID:
Base commit:
Target branch:
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

- Take the goal and scope from the user's request. Write acceptance criteria as checkable statements with IDs (`AC-1`, `AC-2`, ...). Leave `Task ID:`, `Base commit:`, and `Target branch:` empty; never write an ID or a commit hash there.
- If the work is formal-risk, follow the protocol's Workflow tiers rule: the user confirms the acceptance criteria before implementation continues.
- Then write `HANDOFF.md` in the format above with `Task: standard`, the current branch, a status, and `Outcome: none` under `## Review`.
- From this point the task is active: do not edit `TASK.md` again.

## Marking the task complete

1. Check the Definition of Done in `docs/AGENT_PROTOCOL.md`, condition by condition. Record each acceptance criterion's evidence under `## Validation` and any exception under `## Blockers / open questions`.
2. Set `## Status` to `complete`, or to `validating` while checks such as CI are still running.
3. Recommend an independent review by a different agent or model. It is required before acceptance for formal-risk work.
4. If the branch contains WIP or `checkpoint(` commits, remind the user to squash them before merging.
5. Acceptance belongs to the user. Only when the user explicitly accepts the task, on the task's branch and before merging, replace `TASK.md` and `HANDOFF.md` with the neutral state and commit both.

## Neutral state

Copy `.agents/skills/handoff/neutral/TASK.md` and `.agents/skills/handoff/neutral/HANDOFF.md` byte for byte. If those files do not exist, write exactly the content below: UTF-8 without a byte-order mark, LF line endings, one blank line between sections, and a single trailing newline.

`TASK.md`:

```markdown
# Task

Status: none
Tier:
Task ID:
Base commit:
Target branch:
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

`HANDOFF.md`:

```markdown
# Handoff

Last updated: none
Branch: none
Task: none

## Status

none

## Completed

## Current working area

## Validation

## Review

Outcome: none

## Exact next steps

## Blockers / open questions

## Relevant decisions
```
