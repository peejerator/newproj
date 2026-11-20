# Task

Status: active
Tier: standard
Task ID:
Base commit: 0bc980c01b773a24a00160746a8896d088a3cad2
Target branch: main
Issue: https://github.com/peejerator/newproj/issues/40
PR:

## Goal

Allow start-task to create and resume tasks in local-only projects created with
`newproj new --no-remote`.

## Context

Acceptance criteria confirmed by the user: 2026-11-20

- Agreed task branch: `fix-40-local-start-task`.
- Agreed target branch: `main`.
- User decisions: standard tier; independent review of skill instruction changes;
  local-only command output omits push and pull request commands; update the
  canonical skill, interview guidance, content tests, and append an erratum
  superseding conflicting parts of E-018/E-019; automated tests only, without
  additional behavioral fixture scenarios or manual tool runs.
- Repository evidence: the canonical start-task skill requires a target upstream
  and prints a push command unconditionally. The handoff skill resolves the target
  through `origin/HEAD`, then asks the user if that fails. The existing state report
  also resolves local branches through `init.defaultBranch`, `main`, and `master`.
- User decisions: local-only means no configured remotes. Skip only fetch and
  upstream freshness checks in that case, with a one-line explanation. A remote
  that cannot be reached does not qualify for this exception.
- User decisions: for local-only projects with no user-specified target, use the
  state report's local default resolution: `init.defaultBranch` if that branch
  exists, then existing `main`, then existing `master`. Ask the user if unresolved.
  Align the handoff skill's Writing a task guidance with this rule.

## Scope

- Change start-task guidance and supporting tests and documentation for issue #40.
- Coordinate local-only target resolution guidance with the handoff skill.
- Use automated validation only. No new behavioral fixture scenario or required
  manual runs in Claude Code or Codex.
- The user makes every commit. Do not implement while this task is a draft.

## Acceptance criteria

- AC-1: The canonical start-task skill defines local-only as no configured
  remotes. For both new tasks and resumed drafts, it skips fetch and upstream
  freshness checks in that case and explains the skip in one line.
- AC-2: Local-only final commands include a commit command and omit push and pull
  request commands.
- AC-3: Whenever any remote exists, existing target-upstream and freshness checks
  remain required, including stopping for missing upstream, ahead, behind,
  diverged, or failed-fetch states. Existing clean-tree, branch identity and
  creation, resumed-branch ancestry, confirmation, and staging rules remain in
  force for local-only and remote-backed projects wherever applicable.
- AC-4: Local-only target guidance honors a user-specified target; otherwise it
  uses the state report's local default resolution: an existing branch named by
  `init.defaultBranch`, then existing `main`, then existing `master`, asking the
  user if unresolved. The start-task skill, interview reference, and handoff
  skill's Writing a task guidance agree on these rules.
- AC-5: Automated regression tests cover the approved local-only guidance and
  preserved remote-backed safeguards, and `uv run pytest` passes. No additional
  behavioral fixtures or manual tool runs are required.
- AC-6: A new append-only erratum documents the approved exceptions to E-018/E-019;
  the frozen spec and existing accepted entries remain unchanged.

## Relevant areas

- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`
- `template/.agents/skills/handoff/SKILL.md`
- `tests/test_agent_content.py`
- `tests/test_render.py`
- `docs/ERRATA.md`, E-018 and E-019
- `src/newproj/state.py`, default branch resolution, as reference only

## Validation

- Run automated content and rendering tests appropriate to the final guidance,
  then `uv run pytest`.
- Inspect the diff for unintended instruction changes and verify each final
  acceptance criterion by ID.
- Run the repository's state.py consistency check after activation and handoff.

## Do not change

- `docs/spec.md`.
- Existing accepted entries in `docs/DECISIONS.md` or `docs/ERRATA.md`.
- CLI behavior, dependencies, and default branch resolution code.
- Existing behavioral fixtures or their recorded results.

## Open questions

- None.
