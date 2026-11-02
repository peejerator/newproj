# Changelog

All notable changes to `newproj` are recorded here, one section per release (spec section 25).

## v0.1.0

Phase 1, the minimal working system (spec sections 2.3 and 28.1).

- `newproj new <name>`: creates a project from the Copier template, initializes Git, makes the first commit, and creates a private GitHub repository.
- `newproj adopt [path]`: adds the template to an existing repository without overwriting its files, reports collisions and line-ending renormalization, refuses a dirty working tree, and never commits.
- `newproj doctor [path]`: Phase 1 machine and project checks.
- The Copier template: `AGENTS.md`, `CLAUDE.md`, `TASK.md`, `HANDOFF.md`, `docs/AGENT_PROTOCOL.md`, `docs/PROMPTS.md`, `docs/DECISIONS.md`, `README.md`, `.env.example`, hygiene files (`.gitattributes`, `.gitignore`, `.editorconfig`), a `commit-msg` hook that rejects AI attribution, and an optional license.
- Six skills under `.agents/skills/`, with Claude Code pointers under `.claude/skills/`: `resume`, `handoff`, `bootstrap`, `start-task`, `review`, and `accept`.
- `state.py`: a standard-library report of task, working-tree, and history signals, with a `check` mode for the mechanical rules of `TASK.md` and `HANDOFF.md`.
