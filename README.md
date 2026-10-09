# newproj

Create and adopt projects whose state lives in the repository, not in an AI chat, so work can move between AI tools (Claude Code, Codex, GitHub Copilot, and others) and between macOS and Windows.

Status: in development (Phase 1). Not ready for use.

## What it does

- `newproj new <name>` creates a project from a Copier template, initializes Git, and creates a private GitHub repository.
- `newproj adopt` adds the same structure to an existing repository without overwriting its files.
- `newproj doctor` checks the machine and the project for problems.

Generated projects carry `AGENTS.md` (project instructions), `TASK.md` (intended work), and `HANDOFF.md` (reported progress), plus a shared agent protocol and skills that any repo-aware AI tool can follow.

## Install

Once a release exists:

```bash
uv tool install git+https://github.com/peejerator/newproj@v<version>
newproj doctor
```

## Development

See `AGENTS.md` for commands and conventions, `docs/ROADMAP.md` for milestones, and `docs/spec.md` for the full specification.
