---
name: bootstrap
description: Use once, when adopting this template into an existing project, to draft or reconcile AGENTS.md, CLAUDE.md, TASK.md, and HANDOFF.md from the project's code, documentation, and Git history. Not for new projects or ordinary sessions.
---

# Bootstrap

Fit the template's agent files to an existing project without losing anything the project already has. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Rules

- Never overwrite existing project-owned content without the user's review. Add to existing files; propose any replacement or deletion and wait for approval.
- Surface collisions explicitly: an existing file, section, or rule that conflicts with what the template expects is listed for the user, never silently resolved.
- Mark every conclusion you could not verify with `(unverified)` so the user can review it.
- Do not commit unless the user asks.

## Steps

1. Inspect the project:
   - code layout and languages;
   - `README` and anything under `docs/`;
   - Git history: `git log --oneline -30` and `git branch -a`;
   - build, test, lint, and CI configuration (for example `pyproject.toml`, `package.json`, `Makefile`, `CMakeLists.txt`, `.github/workflows/`);
   - existing agent instruction files (for example `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`).
2. Identify the project's conventions: style, commit messages, branch use, module boundaries, generated or vendored files, and platform constraints.
3. Draft or reconcile `AGENTS.md`. Keep it under about 150 lines, with these sections:
   - `## Project`: name and a one-paragraph description;
   - `## Agent protocol`: exactly the line ``At the start of every session, read and follow `docs/AGENT_PROTOCOL.md`.``;
   - `## Commands`: build, test, run, and lint or format, taken from the configuration you inspected;
   - `## Environment`: only where the repository makes requirements evident (runtime and toolchain versions, lockfiles, OS requirements, environment variable names but never values, external services and their test doubles, and what each environment can and cannot run);
   - `## Conventions`;
   - `## Project-specific rules`: including any areas that always count as formal tier for this project;
   - `## Where to find more`: `TASK.md`, `HANDOFF.md`, `docs/AGENT_PROTOCOL.md`, `docs/DECISIONS.md`, and any architecture or roadmap documents.

   If `AGENTS.md` already exists, keep its content, add the `## Agent protocol` line if it is missing, and propose the other additions.
4. `CLAUDE.md`: if it exists, add the lines `@AGENTS.md` and `@docs/AGENT_PROTOCOL.md` where they are missing, at the top, keeping the rest. If it does not exist, create it with exactly those two lines.
5. `TASK.md`:
   - If the user has stated current work that is standard, write it as an active task, as the `handoff` skill describes under Writing a task.
   - If the stated work is formal-risk, write it the same way but with `Status: draft`, and ask the user to confirm its acceptance criteria before anyone implements it.
   - Otherwise write the neutral state, as the `handoff` skill describes under Neutral state.
6. `HANDOFF.md`: the neutral state if `TASK.md` is neutral; otherwise the `handoff` skill's format with `## Status` set to `not started` and `Outcome: none` under `## Review`.
7. If the project would benefit, suggest `docs/ARCHITECTURE.md` or `docs/ROADMAP.md`. Do not write them unless the user asks.
8. Report to the user: files created, files changed and how, collisions, and every `(unverified)` item.
