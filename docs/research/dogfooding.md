# Dogfooding and Phase 1 exit

Evidence for roadmap milestone M8: the template in use on two real projects, recovery tests 24.1 to 24.3, the spec 28.1 exit checklist, and the 28.4 retrospective (docs/ERRATA.md, E-022). Entries are summaries: no transcripts, secrets, or private project content.

## Projects

- ohm-manager (adopted): an existing repository, adopted with `newproj adopt` followed by its `bootstrap` skill.
- Project B (new, AI game-playing competition): different AI models compete to beat Pokemon games or individual gyms, streamed live. Created with `newproj new`. It has no final name yet.

## ohm-manager adoption

Pending: the adopt report (collisions and renormalization), the hygiene-file comparison, the `bootstrap` run, and the `newproj doctor` result.

## Project B creation

Created 2026-11-03 on the Linux development machine (E-023) as `pokemon-content`, with `newproj new --template-path` from this branch at 9e09658 (a development render, E-002). Answers: a one-line description, Python, no license.

- `newproj new` committed the render on `main`, created the private GitHub repository through `gh`, pushed, and set `origin/HEAD`; the default branch is `main` and the repository's visibility is PRIVATE.
- `newproj doctor`: 20 PASS, 0 WARN, 0 FAIL, 3 INFO, run after the push.
- A first attempt, run by an agent without a terminal, rendered the files but failed at the initial commit because the user's commit signing key needs a passphrase; with no terminal, it also took the default answers. `newproj` stopped there and reported where the rendered files were, and created no remote. The user removed the directory and reran the command in a terminal. Run `newproj new` from a terminal when commits are signed.

Pending: the first real task done with the template's workflow. macOS and Windows: CI (E-023).

## Recovery tests

Each entry is one passing run on a real standard task, recorded from the project's Git history and task files; every pass criterion of the spec section is checked individually.

### 24.1 Same-machine interrupted-session recovery

Pending.

### 24.2 Cross-machine recovery (ordinary Git)

Pending.

### 24.3 Task-intent preservation (standard task, different provider)

Pending.

## 28.1 exit checklist

| # | Criterion (spec 28.1) | Status | Evidence |
|---|---|---|---|
| 1 | `newproj new` works on macOS and Windows, with Git and GitHub side effects orchestrated by `newproj`, not Copier tasks, and automatic private repository creation | pending | `tests/test_new.py` (`test_new_runs_no_copier_tasks`, `test_new_with_remote`); CI on Linux, macOS, and Windows; real use: Project B creation (pending) |
| 2 | `newproj adopt` preserves project-owned files and reports collisions; bootstrap reconciles an existing repository safely | pending | `tests/test_adopt.py` (`test_existing_project_files_preserved_and_reviewed`, `test_renormalization_report`, `test_dirty_tree_refused`); `tests/test_agent_content.py` (`test_bootstrap_collisions_and_required_files`); real use: ohm-manager adoption (pending) |
| 3 | `newproj doctor` performs its Phase 1 checks on both machines, and a freshly generated project, before and after ordinary lightweight work, is reported healthy | pending | `tests/test_doctor.py` (`test_lightweight_change_keeps_no_fail`); CI on Linux, macOS, and Windows; real use: Project B on macOS and Windows (pending) |
| 4 | The protocol stays within budget and defines workflow tiers (including escalation on interruption), the Definition of Done, information lifetimes, and trust boundaries | met | `template/docs/AGENT_PROTOCOL.md` (114 lines; sections Workflow tiers, Definition of done, During work, Trust boundaries and authority); `tests/test_agent_content.py` (`test_protocol_line_limit`, `test_protocol_headings`) |
| 5 | Lightweight work, including moderately sized features, proceeds without touching `TASK.md` or `HANDOFF.md` | met | Fixture B4, 2/2 on Claude Code CLI and 2/2 on Codex CLI (`docs/research/behavioral-fixtures.md`) |
| 6 | Resume continues automatically when state is coherent and reconciles discrepancies using Git before asking | met | Fixture B9, 2/2 on each tool (`docs/research/behavioral-fixtures.md`); recovery tests 24.1 and 24.3 (pending) |
| 7 | `state.py` reports the three signal groups, with no false history-freshness warning after a normal commit | met | `tests/test_state.py` (`test_active_report_lists_spec_items`: the three groups in order and "No commits since the last handoff" after a normal commit; `test_stale_and_dirty_handoff`) |
| 8 | Phase 1 CI tests pass; fixtures B1, B4, B5, B6, B9, B10, and B11 pass on at least two tools | met | CI passes on Linux, macOS, and Windows. Every fixture passes on Claude Code CLI and Codex CLI; B6 and B10 pass 2/2 on each tool after the M7.1 protocol fixes (issues #38 and #39) (`docs/research/behavioral-fixtures.md`, Pass rates) |
| 9 | Recovery tests 24.1, 24.2 (ordinary Git), and 24.3 (standard task) pass | pending | Recovery tests, above |
| 10 | Formal-risk work is recognized and gated on the user's go-ahead (fixture B5) | met | Fixture B5, 2/2 on each tool (`docs/research/behavioral-fixtures.md`) |
| 11 | Adoption of an existing repository with its own hygiene files changes none of them destructively | pending | `tests/test_adopt.py` (`test_editorconfig_preserved_and_differences_reported`, `test_gitattributes_with_lf_rule_preserved`); real use: ohm-manager adoption (pending) |
| 12 | The template has been used on two real projects, and an interrupted session on one of them was recovered by a different agent | pending | Projects, ohm-manager adoption, Project B creation, and recovery test 24.3 (pending) |

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
