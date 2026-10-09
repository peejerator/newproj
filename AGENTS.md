# newproj

`newproj` is a cross-platform Python CLI and Copier template that creates and adopts projects whose state lives in repository files (`AGENTS.md`, `TASK.md`, `HANDOFF.md`) instead of AI chat history, so work can move between AI tools and between macOS and Windows. The design is specified in `docs/spec.md` (revision 10, frozen).

## Agent protocol

At the start of every session, read and follow `template/docs/AGENT_PROTOCOL.md`.

This repository is built with the workflow it implements (spec section 2.5), so it follows the protocol it ships. Paths the protocol and skills name under `.agents/skills/` and `docs/` (`AGENT_PROTOCOL.md`, `PROMPTS.md`) are under `template/` here; `TASK.md`, `HANDOFF.md`, `docs/DECISIONS.md`, and `docs/ERRATA.md` are at the repository root. `state.py` does not exist yet (M4), so use the raw Git commands in `template/.agents/skills/resume/SKILL.md`.

Each milestone in `docs/ROADMAP.md` is a standard task. Read only the spec sections that `TASK.md` cites; never load all of `docs/spec.md`.

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
- `template/docs/AGENT_PROTOCOL.md`: the operating protocol.
- `template/.agents/skills/`: the `resume`, `handoff`, and `bootstrap` procedures.
- `docs/ROADMAP.md`: all Phase 1 milestones.
- `docs/DECISIONS.md`: implementation decisions.
- `docs/ERRATA.md`: changes to the frozen spec.
- `docs/spec.md`: the specification (read cited sections only).
