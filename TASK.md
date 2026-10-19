# Task

Status: active
Tier: standard
Task ID:
Base commit: 43bdd59e028830242971b5d06988f7ef546e96bf
Target branch: main
Issue:
PR:

## Goal

Milestone M4: build the shared state module. It covers default-branch resolution, the `TASK.md` and `HANDOFF.md` parsers, the recovery signals, the `state.py` report, and a `check` mode that verifies the mechanical rules. The template ships a byte-identical copy that the skills call.

## Context

Relevant spec sections, and only these:
- 4 (default branch);
- 12.3 and 12.8;
- 13.1, 13.4, 13.5 and 13.6;
- 17.2;
- D-002, E-007 and E-012.

The module is standard-library only (D-002). It runs on Python 3.9 and newer, because spec 17.2 falls back to `python3` and macOS ships 3.9. It is read-only: it never modifies a repository, never runs `git remote set-head`, and never writes files.

Out of scope: `newproj doctor` (M5) and the formal-task signals, which arrive with Phase 2 activation.

## Scope

Work happens on `m4-core-library`, and the PR targets `main`. The user makes every commit: stage the work and print commit commands with no AI attribution, joined with `&&`. Files in scope:

- `src/newproj/state.py`
- `template/.agents/skills/resume/scripts/state.py`
- `template/.agents/skills/{resume,handoff,review,accept}/SKILL.md` (only to call `state.py`)
- `tests/test_state.py`
- `.github/workflows/ci.yml` (the Python 3.9 step only)
- `AGENTS.md` (only the `state.py` notes and commands)
- One documented command, or a small script, that copies the module into the template

## Acceptance criteria

- AC-1: `src/newproj/state.py` uses only the standard library and runs on Python 3.9 or newer. `template/.agents/skills/resume/scripts/state.py` is byte-identical to it, a test asserts this, and one documented command performs the copy.
- AC-2: Default-branch resolution follows spec 4 steps 1 to 4 in order, and reports which step resolved it. Step 2 uses `git ls-remote --symref origin HEAD`, with a timeout, when a remote exists. When step 1 failed but step 2 succeeded, the report says that `git remote set-head origin --auto` would help. An unresolvable default branch is reported with that fix, never guessed.
- AC-3: The `TASK.md` and `HANDOFF.md` parsers read by heading.
  - They report missing or renamed headings and header lines (12.3, 13.4).
  - They report an invalid `Status:`, `## Status` or `Outcome:` value.
  - They report a validation entry whose last field is not `implementer`, `reviewer` or `CI` (13.5).
  - They never raise on malformed input.
- AC-4: The default report prints the items in spec 17.2's list, grouped into the three categories of 13.1:
  - **History freshness:** stale relative to history, and local modifications, as separate signals. "Never committed" is reported when it applies.
  - **Metadata consistency:** the recorded branch against the current branch, and dirty paths outside the recorded working area. Whether `Base commit` resolves and is an ancestor of `HEAD` is reported as information. Whether a review is current or historical follows the validity rules in 13.6.
  - **Semantic reconciliation:** stated as not checked.
  In the neutral state it prints `No active task (neutral state)`, the default branch and how it was resolved, `git status --short`, and recent commits. It skips the first two groups. It reports one neutral file without the other as a mismatch.
- AC-5: `state.py check` exits 0 when clean and 1 when it finds a violation, printing each one with its file and line. It checks:
  - the fixed headings and header lines;
  - the status and outcome values, and validation provenance;
  - that an active task's `Base commit:` is non-empty and resolves (E-007);
  - that, when both files are neutral, they are byte-identical to the neutral copies.
- AC-6: Neutral copies are found at `.agents/skills/handoff/neutral/` under the repository root, or at a path given by `--neutral-dir`. This repository's `AGENTS.md` replaces its "state.py does not exist yet" note with the exact commands for running `state.py` and `state.py check` here.
- AC-7: The `handoff`, `review` and `accept` skills run `state.py check` when Python is available, and fall back to their existing manual checks when it isn't. The `resume` skill's invocation matches spec 17.2.
- AC-8: `tests/test_state.py` builds temporary Git repositories, with no network; the remote for step 2 is a local bare repository. It covers:
  - each default-branch step, including a missing `origin/HEAD` and an unknown default branch;
  - the neutral state, and a mismatch between the two neutral files;
  - stale and dirty `HANDOFF.md`, and a never-committed `HANDOFF.md`;
  - a branch mismatch, and dirty paths outside the working area;
  - review validity: current, historical after a code commit, and historical after a `TASK.md` change;
  - each `check` violation, plus a clean pass;
  - that the repository is unchanged after every run.
  `uv run pytest` passes in CI on all three operating systems, and CI also runs `state.py` and `state.py check` under Python 3.9 against this repository.

## Relevant areas

- `src/newproj/state.py`
- `template/.agents/skills/`
- `tests/test_state.py`
- `.github/workflows/ci.yml`
- `AGENTS.md`

## Validation

- `uv run pytest`
- `git diff --check`
- `state.py` and `state.py check` run by hand against this repository and against a scratch project rendered from the template
- CI on all three operating systems, plus the Python 3.9 step

## Do not change

- `docs/spec.md`
- `src/newproj/cli.py` (doctor is M5)
- `copier.yml`
- The protocol, `docs/PROMPTS.md`, and the template's other content
- `TASK.md`
- `## Review` in `HANDOFF.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
