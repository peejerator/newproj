# Task

Status: active
Tier: standard
Task ID:
Base commit: 07a8bebfa71b4283689c150452a00421fd8ae035
Target branch: main
Issue: #3, #14, #4, #19, #6, #18
PR:

## Goal

M6 in `docs/ROADMAP.md`: implement `newproj adopt` (spec 20.2), and fix the adoption trial findings on the documentation layout wording (#3, #14), terminology collisions (#4, #19), and bootstrap creating required files (#6, #18).

## Context

Interview decisions (start-task, Round 1, 2026-10-20):

- Task branch `m6-adopt`, target `main`. Tier standard: adopt never overwrites project-owned files, refuses a dirty tree, and never commits. Independent review is expected because the protocol and the `bootstrap` and `handoff` skills change.
- Issues in scope: #3, #14, #4, #19, #6, #18, closed from the PR. Everything else, including #35, is out of scope.
- Terminology: a bootstrap step searches existing instruction files and `docs/` for the protocol terms task, handoff, review, validation, decision, accept/acceptance, and milestone. Each collision is reported with a proposed rename or `AGENTS.md` mapping line, applied only with approval. No glossary file.
- Required files in manual adoption: bootstrap creates each missing required file (`AGENTS.md`, `TASK.md`, `HANDOFF.md`, `docs/DECISIONS.md`) and lists what it created. The canonical `DECISIONS.md` header ships as `bootstrap/references/DECISIONS.md`, byte-identical to `template/docs/DECISIONS.md` (tested). Bootstrap reports, but does not create, missing `.gitattributes` LF rules or `.gitignore` entries, and recommends `newproj adopt` or a manual fix.
- Plain folder: adopt prompts `Run git init -b main? [y/N]` when stdin is a terminal; otherwise it fails and prints the command. No `--init` flag.
- Dirty tree: any `git status --porcelain` output refuses (untracked counts, ignored does not).
- Collisions: existing project-owned files are preserved; `AGENTS.md`, a `CLAUDE.md` without the required imports, and a non-neutral `TASK.md` or `HANDOFF.md` are reported as requiring bootstrap review. An existing template-owned path that differs from the template fails preflight before anything is written; a byte-identical one is reported as preserved.
- Hygiene: `.gitignore` gets missing required entries appended in a marked block; `.editorconfig` is preserved and differences are reported; an existing `.gitattributes` is never modified, and a missing LF rule is reported for review; a missing `.gitattributes` is created unless `git ls-files --eol` shows committed files that would change, in which case it is left out, the files are listed, and `git add --renormalize .` is recommended as a separate commit.
- Inputs and results: template source as for `new` (tagged cached clone, or `--template-path` for development); `.copier-answers.yml` records the repository URL; project name defaults to the folder name with a `--name` override, and an invalid name fails preflight; `git remote set-head origin --auto` runs when `origin/HEAD` is missing, and the default branch is reported. Exit 0 for a clean adoption, 1 for adoption completed with review required, 2 for failure; nothing is written on a preflight failure. Adopt prints the file table and bootstrap instructions and never commits.
- Durable documents (Round 2, 2026-10-21): the protocol's Durable documents rule and the handoff skill's step 5 name "the locations `AGENTS.md` names, or `docs/research/` and `docs/specs/` if it names none"; this amends spec 11.9 and 15.3 and needs a new erratum. Mapped locations must be inside the repository; external stores (wikis, Notion, trackers) are reported by bootstrap as collisions. One mapping line may cover both defaults or name a location for each; the security-assumptions default (`docs/research/security.md`) follows the `docs/research/` mapping. `docs/DECISIONS.md` stays fixed and is not mappable; bootstrap reports an existing ADR directory, and `DECISIONS.md` may carry a pointer to it. Bootstrap detects existing equivalents and proposes the mapping line under `AGENTS.md` "Where to find more", written only with approval. `doctor` does not check the mapping. `template/docs/PROMPTS.md` has no hard-coded `docs/research/` or `docs/specs/` paths (checked 2026-10-21; only the protocol line 114 and handoff step 5 do), so it needs no change.
- Validation: new `tests/test_adopt.py` covering hygiene preservation, the renormalization report, dirty-tree refusal, template-owned collision failure, exit codes, and a no-FAIL `newproj doctor` result for a committed adoption of a repository without `AGENTS.md`; content tests for the new protocol, handoff, and bootstrap wording; `AGENTS.md` Commands lists `newproj adopt`; CI passes on Linux, macOS, and Windows. `HANDOFF.md` records this interview as the first real use of `start-task` (date, rounds, friction).
Acceptance criteria confirmed by the user: 2026-10-21

## Scope

- Implement `newproj adopt` per spec 20.2 and the decisions above.
- Update the protocol, the `handoff` skill, and the `bootstrap` skill for issues #3, #14, #4, #19, #6, and #18, with one new ERRATA entry.
- Work on branch `m6-adopt`. The user makes every commit: stage the work and print the commit commands (AGENTS.md).
- Update `HANDOFF.md` at milestones; when done, recommend an independent review by a different agent.

## Acceptance criteria

- AC-1: `newproj adopt [path]` is implemented (path defaults to the current directory), with a `--name` option and the hidden development `--template-path` option (E-002); `newproj adopt --help` documents it and the CLI no longer reports it as not implemented.
- AC-2: For a folder that is not a Git repository, adopt prompts `Run git init -b main? [y/N]` when stdin is a terminal and initializes only on yes; when stdin is not a terminal it exits 2, prints `git init -b main`, and writes nothing.
- AC-3: Adopt exits 2 and writes nothing when `git status --porcelain` reports anything (untracked files included, ignored files excluded), when the project name (folder name or `--name`) is invalid, or when an existing template-owned path differs from the template; the failure message lists the offending paths. A byte-identical template-owned path is reported as preserved.
- AC-4: Existing project-owned files are preserved byte for byte and missing ones are created. `AGENTS.md`, a `CLAUDE.md` without the required imports, and a `TASK.md` or `HANDOFF.md` that is not neutral are reported as requiring bootstrap review. Adopt prints a table classifying each relevant file as created, preserved, or requiring bootstrap review, followed by bootstrap instructions.
- AC-5: Hygiene files: missing required `.gitignore` entries (spec 18.3) are appended in a marked block and nothing is removed; an existing `.editorconfig` is preserved and its differences from the template are reported; an existing `.gitattributes` is never modified and a missing LF rule is reported for review; a missing `.gitattributes` is created unless `git ls-files --eol` shows committed files whose line endings would change, in which case it is left out, the affected files are listed, and `git add --renormalize .` is recommended as a separate commit.
- AC-6: Adopt runs `git remote set-head origin --auto` when `origin` exists without `origin/HEAD` and reports the resolved default branch; `.copier-answers.yml` records the template repository URL rather than a local path; adopt never commits or stages. Exit status is 0 for a clean adoption, 1 for adoption completed with review required, and 2 for failure.
- AC-7: After adopting a repository that had no `AGENTS.md` and committing the result, `newproj doctor` reports no FAIL.
- AC-8: The protocol's Durable documents rule and the `handoff` skill's findings step direct durable findings to the locations `AGENTS.md` names, or to `docs/research/` and `docs/specs/` if it names none. No other template file hard-codes those paths as the only location. `template/docs/AGENT_PROTOCOL.md` is 120 lines or fewer.
- AC-9: The `bootstrap` skill: (a) detects existing durable-document locations and proposes an in-repository mapping line under `AGENTS.md` "Where to find more" (one line for both defaults or one per kind; the security-assumptions file follows the `docs/research/` mapping), reporting external stores as collisions and keeping `docs/DECISIONS.md` fixed, with any existing ADR directory reported; (b) searches existing instruction files and `docs/` for task, handoff, review, validation, decision, accept/acceptance, and milestone, and reports each collision with a proposed rename or mapping line; (c) creates each missing required file (`AGENTS.md`, `TASK.md`, `HANDOFF.md`, `docs/DECISIONS.md`) and lists what it created, using `bootstrap/references/DECISIONS.md` for `docs/DECISIONS.md`; (d) reports, without creating, a missing `.gitattributes` LF rule or missing required `.gitignore` entries, recommending `newproj adopt` or a manual fix. Every proposal is applied only with the user's approval. The skill's pointer copies keep identical frontmatter.
- AC-10: `template/.agents/skills/bootstrap/references/DECISIONS.md` is byte-identical to `template/docs/DECISIONS.md`, enforced by a test.
- AC-11: `docs/ERRATA.md` has a new appended entry recording the amendments to spec 11.9, 15.3, and 17.4 made by AC-8 and AC-9; existing entries are unchanged.
- AC-12: `tests/test_adopt.py` covers AC-2 through AC-7, including hygiene-file preservation, the renormalization report, dirty-tree refusal, template-owned collision failure, and each exit status; content tests cover AC-8 to AC-10. `uv run pytest` passes, and CI passes on Linux, macOS, and Windows.
- AC-13: `AGENTS.md` Commands lists `newproj adopt`.
- AC-14: `HANDOFF.md` records this task's interview as the first real use of `start-task`: its date, number of rounds, and any friction found.

## Relevant areas

- `src/newproj/cli.py`, new `src/newproj/adopt.py`, `src/newproj/new.py` and `src/newproj/source.py` (shared rendering and template source)
- `copier.yml`, `template/.gitignore` and hygiene templates, `template/.gitattributes`, `template/.editorconfig`
- `template/docs/AGENT_PROTOCOL.md`, `template/.agents/skills/handoff/SKILL.md`, `template/.agents/skills/bootstrap/` (including new `references/DECISIONS.md`), root pointer skills
- `docs/ERRATA.md`, `AGENTS.md`, `README.md` if behavior descriptions change
- `tests/test_adopt.py`, `tests/test_agent_content.py`, `tests/test_render.py`, `tests/conftest.py`
- Spec sections: 11.9, 15.3, 17.4, 18.3, 19.2, 20 intro, 20.2, 20.7

## Validation

- `uv run pytest`
- `uv run newproj adopt` on a scratch repository built from fixtures, followed by `uv run newproj doctor` after committing
- State check: `uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral`
- CI on Linux, macOS, and Windows

## Do not change

- `docs/spec.md`.
- Accepted entries in `docs/DECISIONS.md` and `docs/ERRATA.md`.
- `newproj doctor` checks (no mapping validation), and `newproj new` behavior apart from refactoring shared code.
- Issue #35 (template clone race) and other open issues.

## Open questions
