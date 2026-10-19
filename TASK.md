# Task

Status: active
Tier: standard
Task ID:
Base commit: 051eda11584b2a23b75b06d80ca5f7abb88877ae
Target branch: main
Issue:
PR:

## Goal

Milestone M2.1: apply the accepted findings from the ohm-manager trial to the protocol and skills. Record each change to the frozen spec as an erratum, add the user-invoked `review` and `accept` skills, and make every skill invocable inside this repository.

## Context

The user accepted these decisions on 2026-10-19:
- precedence of instructions;
- the user resolves questions addressed to the user;
- commit order when the user makes every commit;
- short-lived task branches fast-forwarded at acceptance;
- `Base commit` for standard tasks;
- acceptance criteria describe the end state;
- review expected when safety rules or instruction files change;
- user-invoked `bootstrap`, `review` and `accept`;
- a Phase 1 `review` skill;
- an `accept` skill;
- a HANDOFF.md size guideline;
- root pointer skills in this repository.

The evidence is in the `trial-finding` issues on GitHub and in ohm-manager's history. This task changes instruction files, so independent review is expected (decision 8).

Relevant spec sections, and only these: 11 (all), 12.4 to 12.6, 12.8, 13.4 to 13.6, 16 introduction and 16.1 to 16.3, 17.1, 17.3, 17.4, 17.6, 17.7, D8, D22.

Constraints:
- The protocol stays at 120 lines or fewer with its nine headings. Put procedure detail in the skills and keep one-line rules in the protocol. If 120 lines proves impossible, record it under Blockers and ask; do not raise the limit.
- Skills must work without `state.py`, which arrives in M4.
- Copilot's support for `disable-model-invocation` is unverified. The erratum says so instead of claiming it.

## Scope

Work happens on `m2.1-trial-fixes`, and the PR targets `main`. The user makes every commit: stage the work and propose commit commands with no AI attribution. Files in scope:

- `docs/ERRATA.md` (new entries, plus a header rule for the bar a change must meet)
- `docs/ROADMAP.md`
- `template/docs/AGENT_PROTOCOL.md`
- `template/docs/PROMPTS.md`
- `template/.agents/skills/` (`resume`, `handoff`, `bootstrap`, new `review` and `accept`, and the `handoff/neutral/` files)
- `template/.claude/skills/` (pointers)
- Root `.agents/skills/` and `.claude/skills/` (pointers into `template/`)
- `tests/test_agent_content.py`
- `AGENTS.md` (only where these changes require it)

## Acceptance criteria

- AC-1: `docs/ERRATA.md` has one new entry per accepted decision, numbered from E-003. Each entry names the spec sections it changes, the observed failure from the trial, and the resolution. The file's header states that an erratum must cite an observed failure or a contradiction in the spec. E-001 and E-002 are unchanged.
- AC-2: `template/docs/AGENT_PROTOCOL.md` has the same nine headings in the same order and 120 lines or fewer. It states:
  - the precedence order: the user's current instruction, then `AGENTS.md`, then protocol defaults, with the trust and authority table as a floor that `AGENTS.md` may tighten but never loosen;
  - that agents settle facts themselves but never resolve a question addressed to the user;
  - that when the user makes every commit, agents stage and print the commit command, and review covers only committed work;
  - machine switches on a short-lived task branch, fast-forwarded into the default branch at acceptance (when the default branch has moved, merge it into the task branch first, never rebase);
  - that independent review is expected for standard work that moves, rewrites, or removes safety rules or instruction-file content.
- AC-3: The `handoff` skill:
  - records `Base commit` from `git rev-parse HEAD` and `Target branch` for standard tasks;
  - requires acceptance criteria to describe the final state at `HEAD`, with session instructions under `## Scope`;
  - gives a size guideline: `## Completed` lists outcomes by AC ID;
  - points to the `review` skill for the review record and to the `accept` skill for acceptance;
  - no longer embeds the review-record format or the neutral-state text.
- AC-4: `template/.agents/skills/handoff/neutral/TASK.md` and `neutral/HANDOFF.md` are byte-identical to the blocks in spec 12.8: UTF-8 with no BOM, LF line endings, and one trailing newline.
- AC-5: The `resume` skill continues on the normal path, as spec 17.1 says. It stops and reports instead when `## Blockers / open questions` contains a question addressed to the user.
- AC-6: A new `review` skill implements spec 17.6 for standard tasks:
  - it takes the starting commit from `Base commit` (asking for it if absent) and uses `git diff <base>...HEAD`;
  - it reports at most INCONCLUSIVE when the implementation is not committed;
  - it gives every acceptance criterion its own status, judged at `HEAD`, and reruns checks itself;
  - it compares moved content against added lines only;
  - it takes the model name from the user or the tool's interface;
  - it writes `Reviewed at` and `Contract` from command output;
  - it changes only `## Review` and its own `reviewer` validation entries, stages `HANDOFF.md`, and prints the commit command;
  - it contains the review-record format moved out of the handoff skill.
- AC-7: A new `accept` skill:
  - verifies that `Outcome: PASS`, that `Reviewed at` is `HEAD` or that only `HANDOFF.md` changed since, and that `Contract` equals `git hash-object TASK.md`;
  - copies the neutral files byte for byte and stages both;
  - prints a commit command with no attribution, and on a non-default branch also prints `git merge --ff-only` and branch-cleanup commands;
  - never commits, pushes, or merges itself.
- AC-8: `bootstrap`, `review` and `accept` carry `disable-model-invocation: true` and an `agents/openai.yaml` setting `policy: allow_implicit_invocation: false`. `resume` and `handoff` keep exactly `name` and `description`. The erratum amending D8 records which tools were checked and lists any unchecked tool as unverified.
- AC-9: `template/.claude/skills/` has pointers for all five skills, with frontmatter identical to each canonical skill. This repository's root `.agents/skills/` and `.claude/skills/` have pointers for all five that point to `template/.agents/skills/<name>/SKILL.md`, plus root copies of each `agents/openai.yaml`.
- AC-10: `template/docs/PROMPTS.md` adds review and accept adapters for upload-only sessions. They point to the rules rather than restating them.
- AC-11: `docs/ROADMAP.md` lists M2.1 between M2 and M3, moves the neutral copies from M3 to M2.1, and adds a `check` mode for `state.py` to M4.
- AC-12: `tests/test_agent_content.py` covers:
  - AC-2's headings and line limit;
  - the frontmatter rules for both kinds of skill, including the `openai.yaml` files;
  - pointer identity for template and root pointers;
  - AC-4's byte identity against spec 12.8;
  - no em dash, en dash, or carriage return in any file under `template/`, root `.agents/` or root `.claude/`.

  `uv run pytest` passes in CI on all three operating systems.

## Relevant areas

- `docs/ERRATA.md`, `docs/ROADMAP.md`
- `template/docs/`, `template/.agents/skills/`, `template/.claude/skills/`
- Root `.agents/skills/` and `.claude/skills/`
- `tests/test_agent_content.py`

## Validation

- `uv run pytest`
- `git diff --check`
- Line count of `template/docs/AGENT_PROTOCOL.md`
- A read-through of each skill as an agent seeing it for the first time, with Phase 1 tooling only
- CI on all three operating systems

## Do not change

- `docs/spec.md`
- `copier.yml` and `template/{{_copier_conf.answers_file}}.jinja`
- `src/`
- `TASK.md`
- `## Review` in `HANDOFF.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
