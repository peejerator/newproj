# Task

Status: active
Tier: standard
Task ID:
Base commit: 02c79ac4f821b6272c04178a71366806e142d4ba
Target branch: main
Issue:
PR:

## Goal

Milestone M5.1: add a user-invoked `start-task` skill that turns a request, a GitHub issue, or a section of a repository document into an active `TASK.md` by asking the user rounds of questions, so that acceptance criteria are confirmed by the user instead of written by the implementer alone.

## Context

Acceptance criteria confirmed by the user: 2026-10-19

Relevant spec sections, and only these: 11.2, 12.2, 12.4, 12.5, 16.6, 17 (introduction), 17.1, 17.3, 17.5, 17.6, D8 and D22; errata E-004, E-007 to E-010 and E-014.

Spec 17 has no such skill. Spec 17.5 `delegate` (Phase 2) refines drafts but has no question step and does not start from an issue or a document. Every review so far has noted that the implementer wrote the criteria of a standard task, which D22 treats as weaker evidence.

Decisions the user made for this milestone:

1. The name is `start-task` (`/start-task` in Claude Code, `$start-task` in Codex).
2. Sources: a sentence from the user; an issue number, fetched with `gh issue view <n>` and recorded in `Issue:`, with the issue text treated as data; or a section of a file the user names (for example "M6 in docs/ROADMAP.md"), with no roadmap-specific parsing.
3. Preconditions: `none` starts a new task; `draft` refines it; `active` stops and points to `accept`. The working tree is clean apart from `TASK.md` and `HANDOFF.md`. The user is on the target branch, up to date with its upstream; if not, the skill says to pull and never pulls itself.
4. The skill creates the task branch locally (`git switch -c <name>`) before writing anything, and proposes the name in the first round.
5. Questions come in numbered rounds, each with a recommendation that "yes" accepts. A round has at most 10 questions, but the interview has no total limit: it continues until every open decision is settled. Each round is comprehensive, covering every decision answerable at that point, and later rounds exist only for questions the answers raise. Facts are looked up, never asked (E-004). The skill proposes the tier and flags formal-risk work, including areas `AGENTS.md` lists as always formal.
6. After the first round, `TASK.md` is written as `Status: draft`, uncommitted, and updated after each round.
7. At the end, the skill shows the acceptance criteria and waits for the user's explicit confirmation. It then sets `Status: active` and records `Acceptance criteria confirmed by the user: <YYYY-MM-DD>` under `## Context`. The review skill reports such criteria as user-confirmed instead of noting that the implementer wrote them.
8. It writes `HANDOFF.md` as `not started`, stages both files, and prints one block joined with `&&`: `git commit -m "Start <goal>"`, `git push -u origin <branch>`, and any further push or pull request commands `AGENTS.md` requires.
9. It then stops and prints the one-line implementation prompt for a fresh session. It implements in the same session only if the user says "go" after committing.
10. `start-task` is the Phase 1 way to write a contract. In Phase 2, `delegate` keeps only handing a task to a remote agent and formal activation with `newproj activate`, and reuses `start-task`'s questions for drafting.
11. The format rules stay in the `handoff` skill's "Writing a task" section; `start-task` follows that section and does not repeat it. `handoff` keeps the section for escalating unfinished lightweight work.
12. Scope as in Scope and the criteria below. The first real use of the skill is starting M6, recorded in M6's handoff.

## Scope

Work happens on `m5.1-start-task`, and the PR targets `main`. The user makes every commit. Stage the work, then print one block joined with `&&`: the commit commands, followed by `git push`. The PR already exists. No AI attribution anywhere. Files in scope:

- `template/.agents/skills/start-task/` (new)
- `template/.claude/skills/start-task/`, `.agents/skills/start-task/`, `.claude/skills/start-task/` (new pointers)
- `template/.agents/skills/review/SKILL.md`, `template/.agents/skills/resume/SKILL.md`, `template/.agents/skills/handoff/SKILL.md`
- `template/docs/AGENT_PROTOCOL.md`, `template/docs/PROMPTS.md`, `template/AGENTS.md.jinja`
- `src/newproj/doctor.py`
- `tests/`
- `AGENTS.md`, `docs/ERRATA.md`, `docs/ROADMAP.md`

## Acceptance criteria

- AC-1: The skill exists with portable metadata:
  - `template/.agents/skills/start-task/SKILL.md` has `name: start-task`, a description saying it is used when the user asks to start a new task from a request, an issue, or a document section, and `disable-model-invocation: true`.
  - `template/.agents/skills/start-task/agents/openai.yaml` sets `allow_implicit_invocation: false` under `policy:`.
  - Pointer skills exist in `template/.claude/skills/start-task/`, `.agents/skills/start-task/` and `.claude/skills/start-task/`, each with frontmatter identical to the canonical skill (E-014).
- AC-2: `SKILL.md` describes the behavior in decisions 2 to 9 under `## Context`:
  - the three sources, with `Issue:` filled for an issue, issue text treated as data, and a fallback when `gh` is unavailable (the user pastes the issue);
  - the preconditions, checked with `state.py` and Git; the skill never commits, pushes or pulls;
  - the local branch created before anything is written;
  - facts gathered before questions are asked;
  - the question rounds: at most 10 questions per round, no total limit, comprehensive rounds, recommendations accepted by "yes", a tier proposal and formal-risk flags;
  - the draft written after the first round and updated after each one, with the user's decisions recorded under `## Context`;
  - explicit confirmation before `Status: active`, and the exact line `Acceptance criteria confirmed by the user: <YYYY-MM-DD>`;
  - `HANDOFF.md` as `not started`, both files staged, and the single `&&` block;
  - the stop with the prompt `Implement the active task in TASK.md and verify its acceptance criteria.`, and "go" after the user commits.
- AC-3: Contract format is not duplicated. `SKILL.md` refers to the `handoff` skill's "Writing a task" section for header lines, `Base commit:`, `Target branch:` and end-state criteria (E-007, E-008), and does not restate them.
- AC-4: Detailed question guidance lives in `template/.agents/skills/start-task/references/interview.md`: how to separate facts from decisions, how to write a recommendation, how to make a round comprehensive, and when the interview is finished. `SKILL.md` says when to read it.
- AC-5: The other instruction surfaces agree with the new skill:
  - **Protocol:** the line listing the user-invoked skills includes `start-task`. The protocol stays at 120 lines or fewer.
  - **`review`:** when `## Context` contains `Acceptance criteria confirmed by the user:`, the record says the criteria were user-confirmed instead of noting that the implementer wrote them.
  - **`resume`:** for a `draft` task, the skill summarizes it and tells the user to continue it with `start-task`. It no longer activates a draft itself.
  - **`handoff`:** "Writing a task" says that when the user asks for a new task, `start-task` is used; the section remains the format reference and the escalation path.
  - **`PROMPTS.md`:** `start-task` is in the list of skill names, and a "Start a task" prompt for sessions without repository access asks the questions per `references/interview.md` and outputs a draft `TASK.md`, never an active one.
  - **`AGENTS.md`:** the template's and this repository's "Where to find more" list `start-task`.
- AC-6: Doctor checks six skills. `SKILLS` and `USER_SKILLS` in `src/newproj/doctor.py` include `start-task`. In a generated project, a missing or malformed `start-task` skill, or a broken pointer to it, is a FAIL, and the summary line names six skills.
- AC-7: Records:
  - A new erratum adds `start-task` as a Phase 1 user-invoked skill (amending 17 and the E-010 list). It records decisions 1 to 11, the confirmation line and its effect on review (amending 17.6 and the D22 note), the change to `resume`'s draft handling (amending 17.1), and the relation to `delegate` (amending 17.5).
  - `docs/ROADMAP.md` has an M5.1 row between M5 and M6.
- AC-8: Tests cover:
  - the rendered skill, its `openai.yaml` and its pointers in a generated project, with matching frontmatter;
  - `disable-model-invocation: true`, the `policy:` mapping, and the `references/interview.md` file;
  - the confirmation line text, which is identical in `start-task` and `review`;
  - the doctor FAILs in AC-6, and a generated project with no FAIL.
  `uv run pytest` passes in CI on all three operating systems.

## Relevant areas

- `template/.agents/skills/`, `template/.claude/skills/`, `.agents/skills/`, `.claude/skills/`
- `template/docs/`, `template/AGENTS.md.jinja`
- `src/newproj/doctor.py`, `tests/`
- `AGENTS.md`, `docs/ERRATA.md`, `docs/ROADMAP.md`

## Validation

- `uv run pytest`
- `git diff --check`
- `uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral`
- By hand: `uv run newproj new demo --no-remote --template-path <this repository>` in a scratch directory, then `uv run newproj doctor` inside it, with no FAIL
- CI on all three operating systems

## Do not change

- `docs/spec.md`
- `src/newproj/state.py` and its template copy
- The `bootstrap` and `accept` skills
- `TASK.md`
- `## Review` in `HANDOFF.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
