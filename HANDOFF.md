# Handoff

Last updated: 2026-10-19 by Claude Code (claude-opus-5-5)
Branch: m3-template-content
Task: standard
Environment: other (Linux, Python 3.13, Copier 9.18.2)

## Status

validating

## Completed

- AC-1: template renders the Phase 1 layout (E-011, E-012); `LICENSE` only when chosen; no `delegate`, no `state.py`.
- AC-2: `TASK.md.jinja` and `HANDOFF.md.jinja` are single `{% include %}` lines of the `neutral/` files.
- AC-3: `AGENTS.md.jinja` with the bootstrap skill's seven sections, `TODO` command placeholders, both required rules (52 lines rendered).
- AC-4: `CLAUDE.md` is the two import lines.
- AC-5: `docs/DECISIONS.md` is a title plus an HTML comment giving the format, Status values, and `### Supersedes` rule; no entries.
- AC-6: hygiene files added; `.gitignore` composed from snippets vendored under `template/_includes/gitignore/` (github/gitignore `0e5d690`), each with a source line; environment block last.
- AC-7: MIT and Apache-2.0 texts under `template/_includes/licenses/`; `copyright_holder` question (MIT only, non-empty validator); E-015 appended.
- AC-8: `_skip_if_exists` and conditional `_exclude` unchanged; test derives the list from the spec 8 table.
- AC-9: `tests/test_render.py` renders three ways with sockets blocked.

## Current working area

- `template/` (new files), `copier.yml`, `tests/test_render.py`, `docs/ERRATA.md`

## Validation

- PASS | uv run pytest | 140 passed, covers AC-1 to AC-9 | Linux, Python 3.13, Copier 9.18.2 | implementer
- PASS | git diff --cached --check | no output | Linux | implementer
- PASS | manual `copier copy --defaults --vcs-ref HEAD` and an all-options MIT render into scratch directories | trees inspected, match AC-1 | Linux | implementer
- NOT RUN | CI on Linux, macOS, Windows | environment: needs the work committed and pushed | implementer

## Review

Outcome: none

## Exact next steps

1. User commits the staged work and pushes `m3-template-content`; confirm CI passes on all three operating systems, then set `## Status` to `complete`.
2. Commit before review, then run the `review` skill in a different agent.

## Blockers / open questions

- For the reviewer: two upstream macOS rules contain a CR byte (`Icon[\r]`, `.HFS+ Private Directory Data[\r]`) and were removed so rendered files stay LF only (AC-9); the change is noted in the snippet's header.
- For the reviewer: snippets and licenses live in `template/_includes/`, excluded from rendering by an unconditional `/_includes` entry in `_exclude`; Copier's include loader resolves from the template repository root, so include paths start with `template/`.
- Observation, not in scope: the pre-existing `.copier-answers.yml` template renders a blank line before EOF (`to_nice_yaml` output plus the file's own newline).

## Relevant decisions

- D-002, D-003; ERRATA E-001, E-010 to E-012, E-015
