# Task

Status: active
Tier: standard
Task ID:
Base commit: 15a29952a9b77a1ffc21c5f88381f10a8c58273b
Target branch: main
Issue:
PR:

## Goal

Milestone M3: complete the Copier template so that `copier copy` produces a full Phase 1 project. That means the project-owned files, the hygiene files, `TASK.md` and `HANDOFF.md` rendered from the neutral copies, and the license choices, with render tests proving the result.

## Context

Relevant spec sections, and only these: 7, 8, 9, 10, 12.8, 14, 18, 19, plus ERRATA E-001, E-002 and E-010 to E-012.

Carried here from M2.1 (decision 12):
- the attribution rule in the template's `AGENTS.md`;
- `.gitattributes`;
- the canonical `docs/DECISIONS.md` header;
- rendering the neutral files.

The user decided on 2026-10-19 that an MIT license asks for a copyright holder. That adds a Copier question to spec 19.1, so it needs an erratum.

Out of scope:
- `state.py` and the `check` mode (M4);
- the `delegate` skill (Phase 2);
- an automated `copier update` test (M6);
- the undecided documentation-layout, terminology and bootstrap issues.

## Scope

Work happens on `m3-template-content`, and the PR targets `main`. The user makes every commit: stage the work and print commit commands with no AI attribution, joined with `&&`. Files in scope:

- `template/` (new files only, apart from rendering wiring)
- `copier.yml`
- `tests/test_render.py` (new)
- `docs/ERRATA.md` (E-015, and any other recorded deviation)

## Acceptance criteria

- AC-1: `copier copy` of this repository renders the Phase 1 layout of spec 7, adjusted by E-011 and E-012:
  - `AGENTS.md`, `CLAUDE.md`, `TASK.md`, `HANDOFF.md`, `README.md`, `.copier-answers.yml`, `.env.example`, `.gitignore`, `.gitattributes`, `.editorconfig`;
  - `docs/AGENT_PROTOCOL.md`, `docs/PROMPTS.md`, `docs/DECISIONS.md`;
  - the five skills under `.agents/skills/` with their `neutral/` and `agents/` files, and the five pointers under `.claude/skills/`;
  - `LICENSE` only when a license is chosen.
  It renders no `delegate` skill and no `state.py`.
- AC-2: The rendered `TASK.md` and `HANDOFF.md` are byte-identical to `.agents/skills/handoff/neutral/TASK.md` and `neutral/HANDOFF.md`. The neutral text exists in exactly one place in `template/`; the rendered files include it rather than duplicate it.
- AC-3: The rendered `AGENTS.md` has the sections of spec 9.1 to 9.7 and is at most 150 lines. It also:
  - fills in the project name and description from the answers;
  - contains the stable instruction of 9.2 verbatim;
  - has placeholders for build, test, run and lint commands;
  - lists the rules "Never commit secrets or credentials." and "Never add Co-Authored-By trailers, "Generated with" footers, or other AI attribution to commits or pull requests."
- AC-4: The rendered `CLAUDE.md` is exactly the two import lines of spec 10.
- AC-5: The rendered `docs/DECISIONS.md` has a title and a short comment describing the entry format of spec 14. The comment defines the Status values (`Proposed`, `Accepted`, `Superseded`) and says a superseding entry names the one it replaces under `### Supersedes`. It contains no entries.
- AC-6: The hygiene files:
  - `.gitattributes` has `* text=auto eol=lf` plus binary markers for common binary formats;
  - `.editorconfig` follows spec 18.2;
  - `.gitignore` always contains the macOS, Windows, VS Code and environment sections, including the four exact env lines of 18.3, and adds a section for each selected language only;
  - the language snippets are vendored in the template, with their upstream source and commit recorded in a comment, so rendering needs no network;
  - `.env.example` holds a short explanatory comment;
  - `README.md` has the project name and description and points to `AGENTS.md`.
- AC-7: `LICENSE` is absent when the license is `none`. MIT and Apache-2.0 render their standard texts. MIT's copyright line is `Copyright (c) <copyright_holder>`, with no year. `copyright_holder` is a Copier question asked only when the license is MIT, and it must not be empty. E-015 records the new question against spec 19.1.
- AC-8: `copier.yml`'s `_skip_if_exists` list and its update-conditional `_exclude` entries both equal the project-owned files in spec 8 that the template renders, and a test asserts it.
- AC-9: `tests/test_render.py` renders into temporary directories, with no network, three ways: the defaults; all languages with MIT; and Apache-2.0. It asserts AC-1 to AC-8. It also asserts that every rendered text file is UTF-8, uses LF only, ends with a newline, and contains no em dash or en dash. `uv run pytest` passes in CI on all three operating systems.

## Relevant areas

- `template/`, `copier.yml`
- `tests/test_render.py`
- `docs/ERRATA.md`

## Validation

- `uv run pytest`
- `git diff --check`
- A manual `copier copy` into a scratch directory, with the rendered tree inspected
- CI on all three operating systems

## Do not change

- `docs/spec.md`
- `src/`
- The protocol and skills under `template/docs/` and `template/.agents/skills/`, apart from what AC-2 needs
- `TASK.md`
- `## Review` in `HANDOFF.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
