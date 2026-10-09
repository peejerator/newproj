# Task

Status: active
Tier: standard
Task ID:
Base commit:
Target branch:
Issue:
PR:

## Goal

Milestone M2: write the agent content that generated projects ship with (the operating protocol, the `resume`, `handoff`, and `bootstrap` skills, their Claude pointer skills, and the Phase 1 prompt adapters), and make this repository follow that protocol itself.

## Context

The protocol and skills determine agent behavior; the CLI is plumbing (D-004). This is the highest-leverage content in Phase 1, so precision matters more than speed.

Relevant spec sections, and only these: 11 (protocol, all subsections), 13.4 to 13.6 (HANDOFF.md contract, validation format, review record), 16 introduction and 16.1 to 16.3 (prompt adapters), 17.1 to 17.4 and 17.7 (skills), D8, D10, D22, D25.

This is the Phase 1 version: no formal lifecycle (`newproj activate`, task branches, recorded reviews of formal tasks) and no `delegate` or `review` skills. Formal-risk work is still recognized and gated on the user's go-ahead (section 11.2, Phase 1 bullet). `state.py` arrives in M4 and the neutral `TASK.md` and `HANDOFF.md` copies in M3, so skills may reference them but must work without them.

M1 review findings that this milestone resolves: the implementer wrote its own `## Review` section, `## Status` held free text, and validation provenance named the tool instead of the role.

All content goes under `template/` as plain files (no `.jinja` suffix), so Copier copies them verbatim.

## Scope

- `template/docs/AGENT_PROTOCOL.md`
- `template/docs/PROMPTS.md`
- `template/.agents/skills/resume/SKILL.md`, `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/bootstrap/SKILL.md`
- `template/.claude/skills/resume/SKILL.md`, `template/.claude/skills/handoff/SKILL.md`, `template/.claude/skills/bootstrap/SKILL.md`
- `tests/test_agent_content.py`
- `AGENTS.md` and `CLAUDE.md` of this repository (AC-7 only)
- `.github/workflows/ci.yml` (AC-8 only)

## Acceptance criteria

- AC-1: `template/docs/AGENT_PROTOCOL.md` exists, is 120 lines or fewer, and contains exactly these second-level headings in this order: `## Session start`, `## Workflow tiers`, `## Reconciliation`, `## Task rules`, `## During work`, `## Definition of done`, `## Trust boundaries and authority`, `## Session end and switching`, `## Durable documents`. Their content implements spec 11.1 to 11.9 as Phase 1 rules: workflow tiers with Phase 1 formal-risk gating, escalation of interrupted lightweight work, and the guaranteed versus best-effort distinction (D22); the Definition of Done; the trust and authority table; machine switches by ordinary Git commit and push. It does not instruct agents to run commands that do not exist in Phase 1.
- AC-2: The protocol states these `HANDOFF.md` invariants: the required headings are fixed (13.4); `## Status` holds exactly one of `none`, `not started`, `in progress`, `blocked`, `validating`, `complete`; validation provenance is exactly one of `implementer`, `reviewer`, `CI` (13.5); and `## Review` is written only by an independent reviewer, never by the agent that implemented the work, with `Outcome:` exactly one of `PASS`, `FAIL`, `INCONCLUSIVE`, `none` (13.6). Detailed formats may live in the `handoff` skill, but these invariants are in the protocol.
- AC-3: The three canonical skills implement spec 17.1, 17.3, and 17.4 for Phase 1. Each `SKILL.md` has YAML frontmatter with exactly two keys, `name` (equal to its directory name) and `description` (stating precisely when to use it), per D8. `resume` gives the `state.py` invocation from 17.2 and the equivalent raw Git commands, and works when `state.py` does not exist yet.
- AC-4: Each Claude pointer skill has frontmatter identical to its canonical skill and a body that instructs the agent to read and follow `.agents/skills/<name>/SKILL.md`, and nothing else (17.7).
- AC-5: `template/docs/PROMPTS.md` contains the resume, handoff, and bootstrap adapters (16.1 to 16.3), written for Phase 1, where files are uploaded by hand rather than bundled. Each adapter points to the rules rather than restating them (D25).
- AC-6: `tests/test_agent_content.py` asserts AC-1's line limit and heading list, AC-3's frontmatter rules, AC-4's identical frontmatter and canonical-path reference, and that no text file under `template/` contains an em dash, an en dash, or a carriage return. `uv run pytest` passes in CI on all three operating systems.
- AC-7: This repository follows its own protocol. The interim rules in `AGENTS.md` ("How to work in this repository") are replaced by an instruction to read and follow `template/docs/AGENT_PROTOCOL.md`, keeping this repository's specific rules (frozen spec, errata, decisions). `CLAUDE.md` contains `@AGENTS.md` and `@template/docs/AGENT_PROTOCOL.md`.
- AC-8: `.github/workflows/ci.yml` uses `actions/checkout@v5` (M1 review finding).

## Relevant areas

- `template/`
- `tests/test_agent_content.py`
- `AGENTS.md`, `CLAUDE.md`
- `.github/workflows/ci.yml`

## Validation

- `uv run pytest`
- Line count of `template/docs/AGENT_PROTOCOL.md`
- A full read-through of the protocol and each skill as an agent seeing them for the first time: every instruction must be actionable with Phase 1 tooling.
- CI passes on all three operating systems.

## Do not change

- `docs/spec.md`
- `copier.yml` and `template/{{_copier_conf.answers_file}}.jinja`
- `src/` (no package code changes in M2)
- `TASK.md`
- `## Review` in `HANDOFF.md` (the reviewer writes it)
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
