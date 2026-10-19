# Task

Status: active
Tier: standard
Task ID:
Base commit: f9ba0ca3175f80f2af05bf9c2c2f08b4eddc8d2d
Target branch: main
Issue:
PR:

## Goal

Milestone M5: implement `newproj new` and the Phase 1 checks of `newproj doctor`, so that a fresh project is created, committed and reported healthy. The milestone also lands the deferred mechanical checks and the batch 3 fixes from the trial.

## Context

Relevant spec sections, and only these: 19.3, 20 (introduction), 20.1, 20.7, 21, D-002, E-002, E-007 and E-010 to E-012.

Doctor reuses `src/newproj/state.py` for parsing, recovery signals and default-branch resolution; it never reimplements them (D-002).

Phase 2 items stay out:
- formal-task checks;
- `newproj update` checks;
- `adopt` (M6).

Because review moved into Phase 1 (E-011), doctor reports review status in the two-part form of 20.7.

Spec 20.7 tells doctor to WARN when an active standard task has a baseline. E-007 now records `Base commit` for standard tasks, so doctor follows E-007 instead, and the erratum below records that.

Tests must not touch the network or real GitHub: they use a fake `gh` on `PATH` and local bare repositories as remotes.

## Scope

Work happens on `m5-new-and-doctor`, and the PR targets `main`. The user makes every commit. Stage the work, then print one block joined with `&&`: the commit commands, followed by `git push` and, if the branch has no PR yet, `gh pr create`. No AI attribution anywhere. Files in scope:

- `src/newproj/` (new modules plus `cli.py`; `state.py` only if a shared helper is truly needed, and then the template copy is synced)
- `template/` (the `.githooks/` hook, the `.copier-answers.yml` fix, the `Icon?` rule)
- `template/.agents/skills/accept/SKILL.md`
- `copier.yml` (only if the hook folder requires it)
- `tests/`
- `docs/ERRATA.md`
- `AGENTS.md`

## Acceptance criteria

- AC-1: `newproj new <name> [--public] [--no-remote] [--owner <owner>]` follows spec 20.1:
  - **Preflight:** the target path is absent or an empty directory; `git` is present and `user.name` and `user.email` are set. With a remote, `gh` is present and authenticated, and the owner comes from `gh api user` unless `--owner` is given.
  - **Template source:** `copier copy` renders at the CLI's tag `v<version>`, from a cached clone of the template repository in the user cache directory. It fetches when the tag is missing, works offline when the cache has the tag, and stops with an explanation when the tag cannot be found. The hidden `--template-path` (E-002) renders a local directory.
  - **Local repository:** `git init -b main`, `git config core.hooksPath .githooks`, then stage only the generated files and commit `Initialize from project-template v<version>`.
  - **Remote:** `gh repo create <owner>/<name>` with `--private` or `--public`, `--source . --remote origin --push`, then `git remote set-head origin --auto`.
  - **Remote failure:** if any remote step fails, the local project stays complete and committed, the exact recovery commands are printed, and the exit code is non-zero.
  - It runs no Copier tasks (19.3).
- AC-2: `newproj doctor [path]` outside a managed project checks:
  - that `git`, `gh`, `uv` and Copier are available;
  - Git `user.name` and `user.email`;
  - `gh` authentication;
  - that a Git credential setup exists.
- AC-3: Inside a managed project, recognized by `.copier-answers.yml`, doctor runs these Phase 1 checks of 20.7:
  - **Template version:** INFO, read from the answers file. The update check is INFO, "arrives with newproj update".
  - **Project-owned files:** FAIL with restore instructions when a required one is missing; WARN when an optional one is missing.
  - **Protocol and skills:** the protocol, the five canonical skills with their `neutral/` and `agents/openai.yaml` files, and pointers whose frontmatter matches their canonical skill. FAIL on a broken pointer or a malformed skill.
  - **`AGENTS.md`:** the protocol reference line; FAIL, printing the line to add.
  - **`CLAUDE.md` imports:** FAIL, printing the missing line.
  - **Task files:** headings, header lines and status values, through the shared module. The neutral-state rules apply, with WARN and a diff. A tier is required for draft and active tasks. For an active standard task, `Base commit` must be present and resolve (E-007), and `Task ID` must be empty.
  - **Partial neutral state:** WARN when exactly one of the two files is neutral.
  - **Review:** the `## Review` section has an `Outcome:` line, and the review status is shown in the two-part form.
  - **Repository state:** conflict markers, and an in-progress merge or rebase.
  - **Size budgets:** `AGENTS.md` (about 150 lines) and the protocol (120 lines), WARN only.
  - **Ignore rules:** the secret-ignore rules (`.env`, `.env.*`, `!.env.example`), WARN only.
  - **Recovery signals:** from the shared module, only while a task is active.
  - **Default branch:** it resolves, with the INFO hint when it resolved only through the network or a fallback.
- AC-4: Every doctor line is classified PASS, WARN, FAIL or INFO. Doctor exits 1 when any FAIL is present and 0 otherwise.
- AC-5: Mechanical attribution checks:
  - Generated projects ship `.githooks/commit-msg`, which rejects a commit message containing a `Co-Authored-By:` line or a "Generated with" footer.
  - Doctor WARNs when `core.hooksPath` is not `.githooks`.
  - Doctor WARNs on attribution lines in the last 20 commits.
  - A new erratum records the hook and its folder as an addition to spec 7 and 8. The hook folder is template-managed.
- AC-6: Batch 3 fixes:
  - **`accept`:** prints its commands as a single block joined with `&&`, with the acceptance commit on the task branch before any switch or merge.
  - **`.copier-answers.yml`:** the rendered file ends with exactly one newline.
  - **`.gitignore`:** the macOS section has an `Icon?` rule with a comment explaining it.
  - **This repository's `AGENTS.md`:** after commit commands, agents print `git push` and, when the branch has no PR, `gh pr create --base main` with the milestone title, all joined with `&&`.
- AC-7: An erratum records that doctor follows E-007 for standard-task baselines (amending 20.7), and that the review status display applies in Phase 1 (E-011). Any hidden test hook beyond `--template-path` gets its own erratum, as E-002 did.
- AC-8: `newproj --help` lists `new`, `adopt` and `doctor`. `adopt` still exits 2 as not implemented. No new runtime dependency is added.
- AC-9: Tests cover:
  - `new --no-remote` followed by doctor, with no FAIL;
  - a lightweight change committed afterwards, still with no FAIL;
  - `new` with a fake `gh` and a local bare remote, which pushes and leaves `origin/HEAD` set;
  - a failing fake `gh`, which leaves a usable committed project and prints the recovery commands;
  - each preflight failure;
  - every FAIL and WARN check in AC-3 and AC-5, triggered at least once;
  - the hook, which rejects an attribution line and accepts a normal message;
  - that doctor uses the shared module's parsers.
  The tests make no network calls. `uv run pytest` passes in CI on all three operating systems.

## Relevant areas

- `src/newproj/`, `tests/`
- `template/.githooks/`, `template/.agents/skills/accept/`
- `docs/ERRATA.md`, `AGENTS.md`

## Validation

- `uv run pytest`
- `git diff --check`
- By hand: `uv run newproj new demo --no-remote --template-path .` in a scratch directory, then `uv run newproj doctor` inside it, before and after a small commit
- CI on all three operating systems

## Do not change

- `docs/spec.md`
- The protocol, and the skills other than `accept`
- `TASK.md`
- `## Review` in `HANDOFF.md`
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`

## Open questions
