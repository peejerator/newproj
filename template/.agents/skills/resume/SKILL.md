---
name: resume
description: Use when the user asks to continue, to pick up where a previous agent left off, or where the project stands, or when this session follows an interruption or a switch of tool, agent, or machine. Ordinary session starts do not need it.
---

# Resume

Reconstruct the state of the work from the repository, then continue it. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`. Do not ask the user for confirmation on the normal path.

## Steps

1. Collect the repository signals (see Signals).
2. Read `AGENTS.md`.
3. Read `TASK.md`. If it does not exist, treat it as `Status: none`.
4. Read `HANDOFF.md`. If it does not exist, treat it as status `none`.
5. Reconcile intended state (`TASK.md`), reported state (`HANDOFF.md`), and actual state (the signals and the diff), using Interpreting the signals. Repair `HANDOFF.md` where a discrepancy is explainable.
6. Read only the additional context the work needs: documents cited by `TASK.md` or `HANDOFF.md`, and the files in the diff.
7. Act on the first case below that applies.

| Situation | Action |
|---|---|
| `TASK.md` has `Status: draft` | Summarize it and ask the user whether to start it. Do not implement. If the user agrees, rewrite it with `Status: active` and `Tier: standard`; if it is formal-risk, the user must also confirm its acceptance criteria first (protocol, Workflow tiers). Reset `## Review` in `HANDOFF.md` to `Outcome: none`. |
| `## Review` in `HANDOFF.md` has `Outcome: FAIL` or `Outcome: INCONCLUSIVE` | Treat its findings as the next work. Set `## Status` to `in progress`. Leave `## Review` itself unchanged. |
| Unfinished work in the working tree or branch, but no active task | Escalate to standard (protocol, Workflow tiers). If the intent is not evident from the diff, the history, and the user's request, ask the user. Then write `TASK.md` and `HANDOFF.md` as the `handoff` skill describes under Writing a task. Tell the user this recovery is best-effort. |
| State is coherent | State in one or two sentences what you are resuming (goal, status, next step), then continue from `## Exact next steps`. |
| A material ambiguity remains after inspection | Ask the user one specific question. |
| Both files are neutral and the working tree is clean | Report that no task is in progress and continue with the user's request. |

## Signals

### With `state.py`

If `.agents/skills/resume/scripts/state.py` exists, run it from the repository root:

```text
uv run --no-project .agents/skills/resume/scripts/state.py
```

Where `uv` is unavailable, run it with `python3 .agents/skills/resume/scripts/state.py` on macOS and Linux, or `py -3 .agents/skills/resume/scripts/state.py` on Windows. The script is read-only and prints the signals grouped as below. If it does not exist, or no Python is available, use the raw Git commands instead.

### Without `state.py`

Run these from the repository root. They work unchanged in bash, zsh, and PowerShell. Replace `<sha>` with the output of the command that produces it.

| Signal | Command |
|---|---|
| Current branch | `git branch --show-current` |
| Current commit | `git rev-parse HEAD` |
| Working tree and dirty paths | `git status --short` |
| Merge, rebase, or cherry-pick in progress | `git status` (look for "rebase in progress", "unmerged paths", or "cherry-pick") |
| Last commit that changed `HANDOFF.md` | `git log -1 --format=%H -- HANDOFF.md` |
| Commits since then that changed other files | `git log --oneline <sha>..HEAD -- . ":(exclude)HANDOFF.md"` |
| Local modifications to `HANDOFF.md` or `TASK.md` | `git status --short -- HANDOFF.md TASK.md` |
| Recent history | `git log --oneline -10` |
| Files changed since a recorded review | `git diff --name-only <Reviewed at> HEAD` |
| Current hash of `TASK.md`, to compare with a review's `Contract:` | `git hash-object TASK.md` |

## Interpreting the signals

Signals are prompts for reconciliation, not proof that anything is wrong. Keep the three groups separate and never collapse them into a single "fresh" or "stale" verdict.

Neutral state. If `TASK.md` has `Status: none` and the `HANDOFF.md` status is `none`, there is no task state: skip history freshness and metadata consistency. If only one of the two files is neutral, report it, because a task was started or cleared incompletely.

History freshness:

- If commits after the last commit that changed `HANDOFF.md` changed other files, the handoff is stale relative to history.
- Separately, report local modifications to `HANDOFF.md`. A modified `HANDOFF.md` is not proof that it is current; it may be left over from an abandoned session. Both signals can be true at once, and one never cancels the other.
- If `HANDOFF.md` has never been committed, history freshness cannot be computed. Say so and rely on the other signals.

Metadata consistency:

- The `Branch:` line in `HANDOFF.md` against the current branch.
- `## Current working area` against the dirty paths. Dirty paths outside the working area are a signal.
- Local modifications to `TASK.md`: an active task should not change after it is written.

Review currency. A recorded `PASS` is current only while no commit after `Reviewed at:` changes files other than `TASK.md` and `HANDOFF.md`, the working tree has no changes outside `HANDOFF.md`, and `git hash-object TASK.md` still equals `Contract:`. Otherwise the review is historical: a past state passed, not necessarily the current one.

Semantic reconciliation. No command checks whether the handoff's account matches the code. Always compare `## Completed` and `## Validation` in `HANDOFF.md` with the actual diff yourself.
