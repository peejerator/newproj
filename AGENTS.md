# newproj

`newproj` is a cross-platform Python CLI and Copier template that creates and adopts projects whose state lives in repository files (`AGENTS.md`, `TASK.md`, `HANDOFF.md`) instead of AI chat history, so work can move between AI tools and between macOS and Windows. The design is specified in `docs/spec.md` (revision 10, frozen).

## How to work in this repository

This repository is built with the workflow it implements, applied by hand until the tooling exists (spec section 2.5). Until `docs/AGENT_PROTOCOL.md` is generated into this repository, these rules stand in for it:

1. At the start of a session, read this file, then `TASK.md` and `HANDOFF.md`. Check `git status` and recent commits, and reconcile them with `HANDOFF.md` before continuing.
2. `TASK.md` is the contract for the current milestone. Do not edit it. If it looks wrong, incomplete, or impossible, record the concern under `## Blockers / open questions` in `HANDOFF.md` and tell the user.
3. Update `HANDOFF.md` at meaningful milestones and before a session ends with work unfinished. Keep it to what another agent needs to continue; it is not an activity log.
4. Before reporting work as complete: check each acceptance criterion by ID, run the tests, inspect the diff for unintended changes, and separate what you verified from what you assumed. Record checks in `HANDOFF.md` as `PASS | command | result | environment | implementer`.
5. Read only the spec sections that `TASK.md` cites. Do not load all of `docs/spec.md`.

## Spec changes

`docs/spec.md` is frozen. Never edit it. If implementation shows the spec is wrong, ambiguous, or incomplete, record the problem in `HANDOFF.md` blockers and ask the user. Accepted changes are recorded as entries in `docs/ERRATA.md` (append only).

## Commands

- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run the CLI from source: `uv run newproj --help`

(Added by milestone M1; update this section when commands change.)

## Environment

- Development machines: macOS (Apple Silicon) and Windows. Every change must work on both.
- Python is managed by `uv`. Requires Python 3.11 or newer.
- CI runs on GitHub Actions on Linux, macOS, and Windows for every push and pull request (docs/DECISIONS.md, D-003). The repository is public: never commit secrets, private data, or personal paths.
- Copier 9.18.2 is the tested minimum version (docs/ERRATA.md, E-001).

## Conventions

- Source in `src/newproj/` (src layout); tests in `tests/`; the Copier template in `template/` with `copier.yml` at the root.
- Standard library only for anything copied into generated projects (for example `state.py`); `newproj` itself depends only on Copier (D-002).
- One branch and one pull request per milestone (`docs/ROADMAP.md`). CI must pass on macOS and Windows before merging.
- LF line endings everywhere (`.gitattributes`).
- No em dashes or en dashes in prose or generated text.

## Rules

- Never commit secrets or credentials.
- Do not edit `docs/spec.md`.
- Do not rewrite accepted entries in `docs/DECISIONS.md` or `docs/ERRATA.md`; supersede them with new entries.
- Ask before adding a dependency.

## Where to find more

- `TASK.md`: the current milestone.
- `HANDOFF.md`: progress on it.
- `docs/ROADMAP.md`: all Phase 1 milestones.
- `docs/DECISIONS.md`: implementation decisions.
- `docs/ERRATA.md`: changes to the frozen spec.
- `docs/spec.md`: the specification (read cited sections only).
