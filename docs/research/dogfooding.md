# Dogfooding and Phase 1 exit

Evidence for roadmap milestone M8: the template in use on two real projects, recovery tests 24.1 to 24.3, the spec 28.1 exit checklist, and the 28.4 retrospective (docs/ERRATA.md, E-022). Entries are summaries: no transcripts, secrets, or private project content.

## Projects

- ohm-manager (adopted): an existing repository, adopted with `newproj adopt` followed by its `bootstrap` skill.
- Project B (new, AI game-playing competition): different AI models compete to beat Pokemon games or individual gyms, streamed live. Created with `newproj new`. It has no final name yet.

## ohm-manager adoption

First attempt (2026-11-03, `newproj adopt --template-path` from this branch): the preflight refused and wrote nothing, because five template-owned paths existed and differed from the template: `docs/AGENT_PROTOCOL.md`, the `bootstrap`, `handoff`, and `resume` skills under `.agents/skills/`, and the `bootstrap` pointer under `.claude/skills/`. All five were byte-identical to this repository's M2 template at 41114dc, copied by hand into ohm-manager on 2026-10-09 (the M2 trial, D-004) and never edited there, so removing them loses nothing. Finding: a project carrying an unmodified earlier template version must remove those files by hand before adopting.

After the user removed them (542ea82 in ohm-manager), the second run succeeded (2026-11-03; answers: Python, no license, empty description).

- Adopt report: 23 template-owned files created. Collisions: the existing `AGENTS.md` preserved and marked for `bootstrap` review; `CLAUDE.md`, `README.md`, `TASK.md`, `HANDOFF.md`, and `docs/DECISIONS.md` preserved; the `handoff` and `resume` pointers under `.claude/skills/` preserved as identical to the template. Default branch resolved from `origin/HEAD`. Nothing staged or committed.
- Renormalization: none needed. The adopt report listed no renormalization item, and `git ls-files --eol` shows all 298 tracked files stored with LF, so the new `* text=auto eol=lf` rule changes no file.
- Hygiene files: `.gitignore` was the only one that existed; it was preserved and gained a marked block appending the required `context.md` entry, with no existing line changed (checked with `git diff`). `.editorconfig`, `.gitattributes`, and `.env.example` did not exist and were created.
- The template working tree had an uncommitted documentation change at the time, so Copier rendered a temporary commit and the answers file records its hash (44dd926) rather than a commit on this branch. Only this document differed.

- `bootstrap` (Claude Code, 2026-11-03) found all required files present and created nothing. It reported three collisions and the user approved its proposals for all three: the empty, older-format `docs/DECISIONS.md` replaced by the template's reference copy; `docs/development_state.md` no longer calls itself a handoff; dated operational notes go to `docs/operations-log.md` instead of `HANDOFF.md`, which is not an activity log. At the user's request it also added the rule that the user makes every commit. It proposed no trimming of `AGENTS.md`'s safety rules without the user's direction.
- Committed by the user as one adoption commit (c5d05ac in ohm-manager), with `core.hooksPath` set to `.githooks`.
- `newproj doctor` after the commit: 19 PASS, 1 WARN, 0 FAIL, 3 INFO. The WARN is `AGENTS.md` at 315 lines against a budget of about 150; most of it is ohm-manager's safety rules, left for a later ohm-manager task rather than trimmed during adoption. No FAIL, so the project counts as healthy.

## Project B creation

Created 2026-11-03 on the Linux development machine (E-023) as `pokemon-content`, with `newproj new --template-path` from this branch at 9e09658 (a development render, E-002). Answers: a one-line description, Python, no license.

- `newproj new` committed the render on `main`, created the private GitHub repository through `gh`, pushed, and set `origin/HEAD`; the default branch is `main` and the repository's visibility is PRIVATE.
- `newproj doctor`: 20 PASS, 0 WARN, 0 FAIL, 3 INFO, run after the push.
- A first attempt, run by an agent without a terminal, rendered the files but failed at the initial commit because the user's commit signing key needs a passphrase; with no terminal, it also took the default answers. `newproj` stopped there and reported where the rendered files were, and created no remote. The user removed the directory and reran the command in a terminal. Run `newproj new` from a terminal when commits are signed.

First real task (2026-11-09, accepted ee780a9 in pokemon-content): the game-harness skeleton, a standard task through the full workflow. `start-task` interview (two rounds, criteria AC-1 to AC-11 confirmed) on branch `harness-skeleton`; implementation in Claude Code across three sessions (recovery test 24.1, below); independent review in Codex, first INCONCLUSIVE (AC-2 needed a real ROM run), then PASS after the implementer recorded real-ROM runs and Codex reran them itself; `accept` reset both task files and fast-forwarded `main`. After acceptance, `state.py check` reports no violations and `newproj doctor` reports 20 PASS, 0 WARN, 0 FAIL.

Findings from the task, each fixed in the template (ERRATA E-024):

- Agent A created nine files without first setting `## Status` to `in progress`, so the next agent found `not started` beside a half-built package. The protocol only asks for handoff updates at meaningful milestones.
- At the end of implementation the agent wrote "commit the work" without printing the command. The project's `AGENTS.md` does not say that the user makes every commit, and the template neither asks nor says.
- The implementer updated `HANDOFF.md` from the `resume` flow without running `state.py check`; its validation entries broke the required format, and the reviewer reported it. The check is required only inside the `handoff` skill.
- An acceptance criterion (AC-2, writes no save files) needed a real ROM to verify; the interview did not ask how the reviewer would check it, which produced the INCONCLUSIVE first review.
- The implementer's first `ruff format` run also reformatted the template-managed `state.py`; the agent reverted it and excluded `.agents/` and `.claude/` from ruff.

macOS and Windows: CI (E-023).

## Recovery tests

Each entry is one passing run on a real standard task, recorded from the project's Git history and task files; every pass criterion of the spec section is checked individually.

### 24.1 Same-machine interrupted-session recovery

Pass, 2026-11-09, pokemon-content, the game-harness skeleton task (Claude Code throughout; sessions started fresh, project memory empty throughout). Recorded from the Claude Code transcripts on this machine (user-authorized) and the task's Git history.

Procedure: the confirmed task was committed (f659938). Agent A implemented part of it and was stopped without recording progress (see the earlier attempt below), so the run used the next session as its Agent A: it reconciled the tree, recorded progress in `HANDOFF.md` (`in progress`, the package as completed, tests, ignore rules, the hook, and docs as remaining), then changed `.gitignore` and created `.githooks/pre-commit`, and was interrupted by the user mid-work with the tree dirty and nothing committed. Agent B, a new session with no prior chat, was asked to resume.

- Identified the active task and its acceptance criteria: yes; it validated and reported against AC-1 to AC-11 by ID.
- Detected that the working tree differed from `HANDOFF.md`: yes; it reported that the handoff listed the `.gitignore` entries and the hook as remaining although both were already in the tree, and corrected the handoff.
- Inspected the working tree: yes (`git diff`, the hook, every source file).
- Distinguished completed from incomplete work: yes; it kept the package, ignore rules, and hook, and wrote the missing tests and documentation.
- Identified what had and had not been validated: yes; nothing had been validated, so it ran every check and recorded the real-ROM tests as NOT RUN.
- Determined the correct next step and continued without the old chat: yes; it finished the task to `validating`, which the review and acceptance above confirm.

Earlier attempt (not counted): the first Agent A was stopped before it recorded any progress, with the handoff still `not started`. The next session, asked to resume, noticed the mismatch, reconstructed progress from the working tree, and recorded it. Recovery worked even without a progress record, but the procedure's step 2 was not met.

### 24.2 Cross-machine recovery (ordinary Git)

Pending.

### 24.3 Task-intent preservation (standard task, different provider)

Pass, 2026-11-10, pokemon-content, the agent-interface task (an agent protocol, the random agent moved onto it, and a replay agent with its CLI subcommand; AC-1 to AC-8). Agent A was Claude Code; Agent B was Codex CLI. Recorded from the Codex transcript on this machine (user-authorized), a snapshot of the working tree taken between the two sessions, and the task's Git history.

Procedure: the confirmed task was committed (d090b86). Agent A, a new session asked only to implement the active task, recorded a golden fixture of the random agent's output, wrote the agent module and the shared runner, and moved both CLI subcommands onto them; it was stopped by the user mid-work, before any test for the new code existed, with nothing committed, the new files untracked, and `HANDOFF.md` still `not started`. Agent B, a new session with no access to the earlier chat, was given only the resume command.

- Correctly identified the original acceptance criteria: yes; it reported and validated against AC-1 to AC-8 by ID, the eight criteria in `TASK.md`.
- Distinguished intended work from completed work: yes; it reported that the handoff said `not started` although the tree held the agent module, runner, CLI changes, and fixture, corrected the handoff to `in progress`, kept Agent A's work, reproduced the untracked golden fixture from the base commit's code before relying on it, then wrote the missing tests and documentation. Its only change to Agent A's code was a one-line fix in the replay error message.
- `TASK.md`'s acceptance criteria unchanged after both sessions: yes; `TASK.md` is identical to d090b86 at the implementation commit (71e6a2a).
- No information from the original chat required: yes; its only prompt was the resume command, and it read only the repository.

The finished work passes 152 tests (2 real-ROM tests skipped), ruff, and the lockfile check, rerun independently. It then goes to the project's independent review and acceptance.

Earlier attempts (not counted), ohm-manager, a task moving `AGENTS.md` sections into topic documents: twice, Agent A wrote every document in one step and finished before it could be stopped. A mechanical task has no natural midpoint, so the test moved to a task with dependent code and test steps; the ohm-manager task continues as ordinary work.

## 28.1 exit checklist

| # | Criterion (spec 28.1) | Status | Evidence |
|---|---|---|---|
| 1 | `newproj new` works on macOS and Windows, with Git and GitHub side effects orchestrated by `newproj`, not Copier tasks, and automatic private repository creation | met | `tests/test_new.py` (`test_new_runs_no_copier_tasks`, `test_new_with_remote`); CI on Linux, macOS, and Windows; real use on Linux: Project B creation, above (E-023) |
| 2 | `newproj adopt` preserves project-owned files and reports collisions; bootstrap reconciles an existing repository safely | met | `tests/test_adopt.py` (`test_existing_project_files_preserved_and_reviewed`, `test_renormalization_report`, `test_dirty_tree_refused`); `tests/test_agent_content.py` (`test_bootstrap_collisions_and_required_files`); real use: ohm-manager adoption, above |
| 3 | `newproj doctor` performs its Phase 1 checks on both machines, and a freshly generated project, before and after ordinary lightweight work, is reported healthy | met | `tests/test_doctor.py` (`test_lightweight_change_keeps_no_fail`); CI on Linux, macOS, and Windows; real use on Linux: Project B healthy when created and after its first task, above (E-023) |
| 4 | The protocol stays within budget and defines workflow tiers (including escalation on interruption), the Definition of Done, information lifetimes, and trust boundaries | met | `template/docs/AGENT_PROTOCOL.md` (116 lines; sections Workflow tiers, Definition of done, During work, Trust boundaries and authority); `tests/test_agent_content.py` (`test_protocol_line_limit`, `test_protocol_headings`) |
| 5 | Lightweight work, including moderately sized features, proceeds without touching `TASK.md` or `HANDOFF.md` | met | Fixture B4, 2/2 on Claude Code CLI and 2/2 on Codex CLI (`docs/research/behavioral-fixtures.md`) |
| 6 | Resume continues automatically when state is coherent and reconciles discrepancies using Git before asking | met | Fixture B9, 2/2 on each tool (`docs/research/behavioral-fixtures.md`); recovery tests 24.1 and 24.3 (above) |
| 7 | `state.py` reports the three signal groups, with no false history-freshness warning after a normal commit | met | `tests/test_state.py` (`test_active_report_lists_spec_items`: the three groups in order and "No commits since the last handoff" after a normal commit; `test_stale_and_dirty_handoff`) |
| 8 | Phase 1 CI tests pass; fixtures B1, B4, B5, B6, B9, B10, and B11 pass on at least two tools | met | CI passes on Linux, macOS, and Windows. Every fixture passes on Claude Code CLI and Codex CLI; B6 and B10 pass 2/2 on each tool after the M7.1 protocol fixes (issues #38 and #39) (`docs/research/behavioral-fixtures.md`, Pass rates) |
| 9 | Recovery tests 24.1, 24.2 (ordinary Git), and 24.3 (standard task) pass | pending | Recovery tests, above |
| 10 | Formal-risk work is recognized and gated on the user's go-ahead (fixture B5) | met | Fixture B5, 2/2 on each tool (`docs/research/behavioral-fixtures.md`) |
| 11 | Adoption of an existing repository with its own hygiene files changes none of them destructively | met | `tests/test_adopt.py` (`test_editorconfig_preserved_and_differences_reported`, `test_gitattributes_with_lf_rule_preserved`); real use: ohm-manager adoption, above |
| 12 | The template has been used on two real projects, and an interrupted session on one of them was recovered by a different agent | met | Projects, ohm-manager adoption, Project B creation, and recovery test 24.3 (Claude Code to Codex CLI), above |

## 28.4 retrospective

Pending: written at the end of M8 from aggregate transcript figures per machine (E-022) and the user's brief answers.

### Ongoing signals

| Signal (spec 28.4) | Judgement |
|---|---|
| Same-machine and cross-machine switches need no reconstructed prompt | pending |
| Lightweight work carries no file overhead | pending |
| Confirmed acceptance criteria never change silently | pending |
| No PASS rests only on implementer claims | pending |
| A new project is usable after one command | pending |
| Template updates do not create recurring manual reconciliation | pending |

### Aggregate figures

| Machine | Era | Sessions | Active time | User messages | Manual interventions (judged) |
|---|---|---|---|---|---|
| pending | | | | | |
