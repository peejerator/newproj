# Roadmap

Current phase: Phase 1, minimal working system (spec section 2.3). Phase 1 ends with tag `v0.1.0` once every exit criterion in spec section 28.1 is met.

Each milestone is one branch and one pull request. CI must pass on macOS and Windows before merging. The next milestone's `TASK.md` is written after the previous one merges.

## Phase 1 milestones

| # | Milestone | Spec sections | Done when |
|---|---|---|---|
| M1 | Skeleton: `pyproject.toml`, `newproj --version`, pytest, CI matrix | 6, 20, D15 | CI passes on all three operating systems |
| M2 | Agent content: `docs/AGENT_PROTOCOL.md`, `resume`, `handoff`, and `bootstrap` skills, Claude pointer skills, prompts 16.1 to 16.3 | 11, 13, 16.1 to 16.3, 17.1 to 17.4, 17.7 | Protocol is 120 lines or fewer; copied by hand into one real project and used for a few days |
| M3 | Template content: hygiene files, vendored `.gitignore` snippets, neutral `TASK.md` and `HANDOFF.md` copies, `AGENTS.md`, `CLAUDE.md`, `docs/DECISIONS.md`, `LICENSE` choices | 7 to 10, 12.8, 14, 18, 19 | Render tests pass: neutral files byte-identical, LF endings, ownership lists match `copier.yml` |
| M4 | Core library: default-branch resolution, `TASK.md` and `HANDOFF.md` parser, recovery signals, `state.py` | 4, 12.3, 13.1, 13.4, 17.2 | Signal tests pass, including neutral state and missing `origin/HEAD` |
| M5 | `newproj new` and `newproj doctor` (Phase 1 checks) | 20 intro, 20.1, 20.7, 21 | A fresh project is healthy before and after a lightweight change, on both machines |
| M6 | `newproj adopt` | 20.2 | Tests pass for hygiene-file preservation, the renormalization report, and dirty-tree refusal |
| M7 | Behavioral fixtures B1, B4, B5, B6, B9, B10, B11 on Claude Code and Codex, two runs each | 23.2 | Results recorded |
| M8 | Dogfooding and exit | 24.1 to 24.3, 28.1 | Two real projects in use; an interrupted session recovered by the other agent; tag `v0.1.0` |

M2 precedes the template and CLI work on purpose: the protocol and skills determine agent behavior and can be used by hand on a real project before the CLI exists (D-004).

## Before M8

- Record the section 28.4 baseline: for two or three tasks done in the current workflow, note minutes spent and manual interventions.
- Choose the M8 projects: one existing repository to adopt and one new project.

## Before tagging v0.1.0

- Choose this repository's own license. The repository is public, but without a license others may view it and nothing more. Generated projects still default to no license (ERRATA E-001).
