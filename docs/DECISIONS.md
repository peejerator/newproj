# Decisions

Implementation decisions for `newproj`. Append only: accepted entries are never rewritten, only superseded by later entries. Changes to the specification itself go in `docs/ERRATA.md`.

## D-001: Repository name, owner, and visibility

Date: 2026-10-09
Status: Accepted

### Decision

The repository is `peejerator/newproj`, public from the start.

### Rationale

The CLI and template share one repository and one version (spec section 20), so naming the repository after the command keeps the install command self-explanatory: `uv tool install git+https://github.com/peejerator/newproj@v<version>`.

Public visibility means standard GitHub-hosted runners are free, so the full CI matrix costs nothing (D-003). It also means `uv tool install`, Copier, and remote agents can fetch the repository without credentials on either machine. Nothing in the repository is secret, and the rule against committing secrets applies from the first commit.

### Alternatives considered

Private during development, public at the end of Phase 1: hides unfinished work, but GitHub Free private repositories include only 2,000 Actions minutes per month with macOS runners at roughly ten times the Linux rate, and every machine and agent needs Git credentials to fetch the template.

### Supersedes

None

## D-002: One shared state module, and minimal CLI dependencies

Date: 2026-10-09
Status: Accepted

### Decision

1. Task and handoff parsing, default-branch resolution, and recovery signals live in one standard-library-only module in `src/newproj/`. A build step copies it into the template as `.agents/skills/resume/scripts/state.py`, and a CI test asserts the two files are byte-identical.
2. The CLI uses `argparse`. Its only runtime dependency is Copier (`>=9.18.2,<10`), installed with the tool, so Copier is always available to `newproj`.

### Rationale

`state.py` must run inside generated projects without `newproj` installed, so it can use only the standard library, while `newproj doctor` needs identical logic. One source with an identity check prevents the two from drifting. Three subcommands do not need a CLI framework, and every extra dependency is something to pin and keep working on two operating systems.

### Alternatives considered

Two separate implementations (would drift). Typer or Rich (nicer output, more to maintain).

### Supersedes

None

## D-003: Full CI matrix on every push

Date: 2026-10-09
Status: Accepted

### Decision

CI runs the test suite on `ubuntu-latest`, `macos-latest`, and `windows-latest` for every push and every pull request.

### Rationale

The repository is public (D-001), so standard GitHub-hosted runners are free. Running every platform on every push catches macOS and Windows breakage at the commit that caused it rather than at pull-request time.

### Alternatives considered

Linux on every push with macOS and Windows only on pull requests (needed only to save minutes on a private repository). Linux only (does not meet the spec's macOS and Windows requirement).

### Supersedes

None

## D-004: Implementation order

Date: 2026-10-09
Status: Accepted

### Decision

Phase 1 is built in the milestone order in `docs/ROADMAP.md`, with agent content (protocol and skills, M2) immediately after the skeleton and before the template and CLI.

### Rationale

The protocol and skills determine agent behavior; the CLI is plumbing. Written early, they can be copied by hand into a real project and tested weeks before the CLI exists, which is the cheapest feedback available.

### Alternatives considered

CLI first, content last (content tested only at the end, when changes are most expensive).

### Supersedes

None
