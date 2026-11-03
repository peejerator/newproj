# Task

Status: active
Tier: standard
Task ID:
Base commit: 494fb67f5a79131978366590a573bbafe05558c3
Target branch: main
Issue:
PR:

## Goal

Finish Phase 1 (roadmap M8): use the template on real projects, run recovery tests 24.1, 24.2 (ordinary Git), and 24.3 (standard task), record evidence that every spec 28.1 exit criterion is met, and prepare the repository for the `v0.1.0` tag.

## Context

Spec sections: 24.1, 24.2, 24.3, 24.8, 25, 28.1, 28.4. Roadmap: M8, "Before M8", "Before tagging v0.1.0".

Agreed task branch: `m8-dogfooding-exit`. Target: `main`.

User decisions (Round 1, 2026-11-02):

- The task is roadmap M8, standard tier. No formal-risk work: the tag push is an external action the user runs.
- The adopted project is ohm-manager (already named in `docs/ROADMAP.md` and `docs/ERRATA.md`). The new project is not chosen yet.
- Evidence goes in one document, `docs/research/dogfooding.md`, with a 28.1 exit checklist mapping each bullet to its evidence; `HANDOFF.md` cites it rather than copying it.
- No recording of minutes spent; the user wants as little logging as possible.
- Recovery tests run on real tasks in the real projects: 24.1 (same machine, dirty tree, unplanned stop), 24.3 (resumed by a different provider, Claude Code and Codex; also covers 28.1's recovery by a different agent), 24.2 (between two machines with an ordinary WIP commit and push; amended 2026-11-03, see below). One passing run each, summarized; no transcripts or private project content.
- Small template or CLI fixes found during dogfooding are in scope, each with tests and listed in the handoff. Spec changes need the user's approval and an ERRATA entry; anything larger is a blocker.
- Add an MIT `LICENSE` at the repository root and set `license` in `pyproject.toml`. Generated projects keep their no-license default (E-001).
- Add `CHANGELOG.md` with a `v0.1.0` entry. The tag is not an acceptance criterion; the accept block ends with the tag commands for the user to run on `main`. No GitHub Release.
- At acceptance, `docs/ROADMAP.md` marks Phase 1 complete; Phase 2 planning is a later task.

User decisions (Round 2, 2026-11-02):

- Spec 28.4: no per-task logging. One short retrospective in `dogfooding.md` at the end of M8, a line per 28.4 ongoing signal, written by the agent from the user's brief answers. Recorded as an ERRATA entry; the roadmap's "Before M8" baseline bullet is removed.
- The user has an idea for the new project; it does not block starting. It is created with `newproj new` including its GitHub private repository, and `newproj doctor` reports it healthy (amended 2026-11-03, see below).
- ohm-manager is adopted with `newproj adopt --template-path` pointing at this branch, followed by its `bootstrap` skill. The record notes the adopt report, that no hygiene file was changed destructively, and a healthy `doctor` result. ohm-manager's commits stay in ohm-manager.
- Recovery-run entries are drafted by an agent in this repository from ohm-manager's Git history and task files (read-only data); it asks the user only what it cannot see.
- 28.1 bullets covered by earlier milestones cite existing evidence rather than being re-run.
- Roadmap at exit: Phase 1 complete, "Before M8" and "Before tagging v0.1.0" license items removed, Phase 2 unplanned.
- `CHANGELOG.md`: one short `v0.1.0` section listing what Phase 1 ships.
- Independent review by a different agent before acceptance.

User decisions (Round 3, 2026-11-02):

- The 28.4 retrospective uses aggregate figures derived from local Claude Code and Codex transcripts, in a single pass at the end of M8 on each machine. The user authorized this read of private data for that pass only. Only ohm-manager and new-project sessions are read, plus surviving pre-adoption ohm-manager sessions as the baseline. Only aggregate numbers and one-line judgements are written; no quotes or transcript content; no script is added to the repository. The 28.4 ERRATA entry says the figures come from transcripts instead of manual notes.
- The user sets `"cleanupPeriodDays": 365` in Claude Code's user settings on macOS and Windows so transcripts survive until the retrospective (already set on the Linux machine used for this interview).
- The new project: different AI models compete to beat Pokemon games or individual gyms, streamed on YouTube or Twitch. It has no name yet; this repository refers to it as "Project B (new, AI game-playing competition)".

User decisions (confirmation, 2026-11-02):

- After the 28.4 figures are recorded on a machine, the user removes `cleanupPeriodDays` from that machine's Claude Code user settings, restoring the default (30 days). Claude Code then deletes transcripts older than 30 days, so the removal waits until that machine's figures are in `dogfooding.md`.
- No Codex setting is changed.

User decisions (machine setup, 2026-11-03):

- Development happens on one Linux machine, reached over SSH from macOS and Windows, for the foreseeable future; agents run only there. Option 2 of the agent's proposal is chosen, recorded as `docs/ERRATA.md` E-023.
- Real use of `newproj new` and `newproj doctor` happens on this Linux machine; CI on Linux, macOS, and Windows is the evidence that they work on macOS and Windows.
- Recovery test 24.2 runs once between this Linux machine and one of macOS or Windows (either direction), working directly on that machine rather than over SSH.
- The 28.4 transcript pass runs on this machine only; `cleanupPeriodDays` is not needed on macOS or Windows.

Facts (2026-11-02, this machine): Claude Code keeps transcripts as JSONL under `~/.claude/projects/<path-slug>/`, Codex under `~/.codex/sessions/YYYY/MM/DD/`; both carry per-entry timestamps, and Codex records the working directory. The oldest local transcripts date from 2026-10-19, including 10 ohm-manager Claude Code sessions. Transcripts are per machine. A string search of the Codex CLI 0.166.0 binary found no session-retention or cleanup setting; its only related mechanism is manual archiving into `archived_sessions`, and its `history` settings govern prompt history, not session files. Recheck the installed Codex version before the retrospective.

Acceptance criteria confirmed by the user: 2026-11-02
Amended AC-3 and AC-4 confirmed by the user: 2026-11-03

## Scope

- In scope: adopting ohm-manager, creating Project B, the three recovery tests, the evidence document, the 28.4 retrospective and its ERRATA entry, `LICENSE`, `CHANGELOG.md`, the roadmap update, and small template or CLI fixes found during dogfooding.
- Recovery tests run on real standard tasks in ohm-manager or Project B. The user starts, stops, and switches the agents; Agent A in 24.1 and 24.3 is stopped without a final handoff.
- After each recovery run, the user asks an agent in this repository to record it; that agent reads the other project's Git history and task files as data and asks the user only what it cannot see.
- The transcript read for 28.4 happens once, at the end of M8, on each machine, under the user's authorization recorded in Context. Never read ohm-manager's `.ohm/secrets/`.
- After a machine's figures are recorded, remind the user to remove `cleanupPeriodDays` from that machine's Claude Code user settings.
- Spec problems go to `HANDOFF.md` blockers; an ERRATA entry needs the user's approval. Larger fixes are blockers, not scope.
- Update `HANDOFF.md` after each recovery run and after any fix, not as an activity log.
- The user makes every commit. Pushes before acceptance run CI once; the pull request opens at acceptance (`AGENTS.md`).
- Tagging `v0.1.0` is not part of the reviewed work: the accept block ends, after the merge on `main`, with `git tag -a v0.1.0 -m "v0.1.0" && git push origin v0.1.0` for the user to run. No GitHub Release.
- Not in scope: Phase 2 planning, renaming or publishing Project B, and changes to ohm-manager beyond its adoption and its own real tasks.

## Acceptance criteria

- AC-1: `docs/research/dogfooding.md` exists and names the two real projects: ohm-manager (adopted) and Project B (new, AI game-playing competition).
- AC-2: The document records ohm-manager's adoption with `newproj adopt` followed by its `bootstrap` skill: a summary of the adopt report (collisions and renormalization), that none of ohm-manager's existing hygiene files was changed destructively, and a `newproj doctor` result reporting it healthy.
- AC-3: The document records that Project B was created with `newproj new`, including automatic creation of its private GitHub repository, that `newproj doctor` reported it healthy on the development machine (Linux), with CI passing on Linux, macOS, and Windows as the cross-platform evidence (E-023), and that at least one real task was done in it with the template's workflow.
- AC-4: The document records one passing run each of recovery tests 24.1 (same machine), 24.2 (between the Linux development machine and one of macOS or Windows, ordinary Git, E-023), and 24.3 (standard task, resumed by an agent from a different provider), each on a real task in one of the two projects, with every pass criterion of its spec section checked individually. The 24.3 entry shows an interrupted session on a real project recovered by a different agent.
- AC-5: The document contains a spec 28.1 exit checklist in which every bullet is marked met and cites its evidence (a section of the document, `docs/research/behavioral-fixtures.md`, a test, or a CI run).
- AC-6: The document contains a 28.4 retrospective: one line for each ongoing signal in 28.4, plus aggregate figures per machine derived from local transcripts (session count, active time, user message count, judged count of manual interventions) for template-era sessions and, where transcripts survive, pre-adoption baseline sessions.
- AC-7: `docs/ERRATA.md` has a new appended entry replacing 28.4's manual notes of time and interventions with that single transcript-derived retrospective; earlier entries are unchanged.
- AC-8: The repository root has an MIT `LICENSE`, and `pyproject.toml` declares `license = "MIT"`. Generated projects still default to no license.
- AC-9: `CHANGELOG.md` exists with a `v0.1.0` section listing what Phase 1 ships (`newproj new`, `adopt`, and `doctor`, the Copier template, and the six skills), and `pyproject.toml` declares version `0.1.0`.
- AC-10: `docs/ROADMAP.md` marks Phase 1 complete, no longer lists the "Before M8" items or the "Before tagging v0.1.0" license item, and lists no Phase 2 milestones.
- AC-11: Every change to `src/newproj/` or `template/` made during M8 has a test covering it and is listed in `HANDOFF.md`; `uv run pytest` passes, the `state.py` copies are byte-identical, and CI passes on Linux, macOS, and Windows at `HEAD`.
- AC-12: `docs/spec.md` is unchanged from `Base commit:`, and no committed file contains transcript excerpts, secrets, private project content, or personal paths.

## Relevant areas

- `docs/research/dogfooding.md` (new)
- `docs/ROADMAP.md`
- `LICENSE` (new), `pyproject.toml`, `CHANGELOG.md` (new)
- `docs/ERRATA.md` (append only, if approved)
- `AGENTS.md` (Environment section, E-023)
- `src/newproj/`, `template/`, `tests/` (dogfooding fixes only)

## Validation

- `uv run pytest`
- `uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral`
- CI on Linux, macOS, and Windows at `HEAD`
- `git diff --exit-code <Base commit> HEAD -- docs/spec.md`
- Search the diff for personal paths (`/Users/`, `C:\Users`, `/home/`) and transcript text before committing
- Read `docs/research/dogfooding.md` against AC-1 to AC-6 and spec 24.1 to 24.3 and 28.1

## Do not change

- `docs/spec.md`
- The template's no-license default for generated projects
- ohm-manager's `.ohm/secrets/` (never read)
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions

